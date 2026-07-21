from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Literal

import pandas as pd


FINANCIAL_FACTOR_GROUPS = {
    "income": ("revenue", "operating_income", "net_income", "diluted_eps"),
    "profitability": ("operating_margin", "net_margin", "roe"),
    "stability": ("current_ratio", "debt_ratio"),
}

_FACTOR_META = {
    "revenue": ("매출", "income", "currency"),
    "operating_income": ("영업이익", "income", "currency"),
    "net_income": ("순이익", "income", "currency"),
    "diluted_eps": ("희석 EPS", "income", "currency_per_share"),
    "operating_margin": ("영업이익률", "profitability", "percent"),
    "net_margin": ("순이익률", "profitability", "percent"),
    "roe": ("ROE", "profitability", "percent"),
    "current_ratio": ("유동비율", "stability", "ratio"),
    "debt_ratio": ("부채비율", "stability", "percent"),
}


def _number(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        number = float(str(value).replace(",", ""))
    except (TypeError, ValueError):
        return None
    if pd.isna(number):
        return None
    return number


def _date_label(value: Any) -> str | None:
    if value in (None, ""):
        return None
    timestamp = pd.to_datetime(value, errors="coerce")
    if pd.isna(timestamp):
        return str(value)
    return pd.Timestamp(timestamp).strftime("%Y-%m-%d")


def _ratio(numerator: Any, denominator: Any, *, percent: bool = False) -> float | None:
    top = _number(numerator)
    bottom = _number(denominator)
    if top is None or bottom is None or bottom <= 0:
        return None
    value = top / bottom
    return value * 100.0 if percent else value


def _factor_value(
    row: Mapping[str, Any],
    *,
    factor: str,
    previous_equity: float | None,
) -> float | None:
    if factor == "revenue":
        return _number(row.get("total_revenue") if "total_revenue" in row else row.get("revenue"))
    if factor == "diluted_eps":
        provenance = dict(row.get("metric_provenance") or {}).get("diluted_eps") or {}
        source_kind = str(provenance.get("source_kind") or "").upper()
        if source_kind and source_kind != "REPORTED":
            return None
        return _number(row.get("diluted_eps"))
    if factor in {"operating_income", "net_income"}:
        return _number(row.get(factor))
    if factor == "operating_margin":
        return _ratio(
            row.get("operating_income"),
            row.get("total_revenue") if "total_revenue" in row else row.get("revenue"),
            percent=True,
        )
    if factor == "net_margin":
        return _ratio(
            row.get("net_income"),
            row.get("total_revenue") if "total_revenue" in row else row.get("revenue"),
            percent=True,
        )
    if factor == "roe":
        ending_equity = _number(row.get("shareholders_equity"))
        if previous_equity is None or ending_equity is None:
            return None
        return _ratio(row.get("net_income"), (previous_equity + ending_equity) / 2.0, percent=True)
    if factor == "current_ratio":
        return _ratio(row.get("current_assets"), row.get("current_liabilities"))
    if factor == "debt_ratio":
        return _ratio(row.get("total_liabilities"), row.get("shareholders_equity"), percent=True)
    raise ValueError(f"Unsupported financial factor: {factor!r}")


def build_financial_factor_series(
    rows: Sequence[Mapping[str, Any]],
    *,
    freq: Literal["annual", "quarterly"],
) -> dict[str, Any]:
    """Build one-axis-at-a-time financial factor series for a reporting frequency."""

    if freq not in {"annual", "quarterly"}:
        raise ValueError(f"Unsupported financial frequency: {freq!r}")
    ordered = sorted(
        (dict(row) for row in rows),
        key=lambda row: _date_label(row.get("period_end")) or "",
    )
    factors: dict[str, dict[str, Any]] = {}
    for factor, (label, group, unit) in _FACTOR_META.items():
        points: list[dict[str, Any]] = []
        exclusions: list[dict[str, Any]] = []
        previous_equity: float | None = None
        for row in ordered:
            value = _factor_value(row, factor=factor, previous_equity=previous_equity)
            period_end = _date_label(row.get("period_end"))
            if value is None:
                exclusions.append(
                    {
                        "period_end": period_end,
                        "reason_code": "MISSING_OR_INVALID_INPUT",
                    }
                )
            else:
                points.append(
                    {
                        "period_end": period_end,
                        "value": value,
                        "available_at": _date_label(
                            row.get("available_at") or row.get("latest_available_at")
                        ),
                        "form_type": row.get("form_type") or row.get("latest_form_type"),
                        "accession_no": row.get("accession_no")
                        or row.get("latest_accession_no"),
                    }
                )
            equity = _number(row.get("shareholders_equity"))
            if equity is not None:
                previous_equity = equity
        factors[factor] = {
            "label": label,
            "group": group,
            "unit": unit,
            "points": points,
            "available_count": len(points),
            "excluded_count": len(exclusions),
            "exclusions": exclusions,
        }
    return {
        "schema_version": "market_mover_financial_factor_series_v1",
        "freq": freq,
        "factor_groups": FINANCIAL_FACTOR_GROUPS,
        "factors": factors,
    }


def _quarter_ordinal(row: Mapping[str, Any]) -> int | None:
    year = _number(row.get("fiscal_year"))
    quarter = _number(row.get("fiscal_quarter"))
    if year is None or quarter is None or int(quarter) not in {1, 2, 3, 4}:
        return None
    return int(year) * 4 + int(quarter) - 1


def _unavailable_valuation(reason_code: str, *, latest_price: float | None) -> dict[str, Any]:
    return {
        "status": "UNAVAILABLE",
        "reason_code": reason_code,
        "latest_price": latest_price,
        "ttm_diluted_eps": None,
        "current_per": None,
        "quarters": [],
    }


def build_current_ttm_valuation(
    quarterly_rows: Sequence[Mapping[str, Any]],
    *,
    latest_price: float | None,
    latest_price_date: str | None,
) -> dict[str, Any]:
    """Calculate current PER only from four consecutive reported diluted-EPS quarters."""

    price = _number(latest_price)
    if price is None or price <= 0:
        return _unavailable_valuation("LATEST_PRICE_UNAVAILABLE", latest_price=price)
    ordered = sorted(
        (dict(row) for row in quarterly_rows if _quarter_ordinal(row) is not None),
        key=lambda row: int(_quarter_ordinal(row) or 0),
    )
    if len(ordered) < 4:
        return _unavailable_valuation("INCOMPLETE_REPORTED_DILUTED_EPS", latest_price=price)
    latest_four = ordered[-4:]
    ordinals = [int(_quarter_ordinal(row) or 0) for row in latest_four]
    if ordinals != list(range(ordinals[0], ordinals[0] + 4)):
        return _unavailable_valuation("NON_CONSECUTIVE_FISCAL_QUARTERS", latest_price=price)

    eps_values: list[float] = []
    evidence: list[dict[str, Any]] = []
    for row in latest_four:
        provenance = dict(row.get("metric_provenance") or {}).get("diluted_eps") or {}
        eps = _number(row.get("diluted_eps"))
        if eps is None or str(provenance.get("source_kind") or "").upper() != "REPORTED":
            return _unavailable_valuation("INCOMPLETE_REPORTED_DILUTED_EPS", latest_price=price)
        eps_values.append(eps)
        evidence.append(
            {
                "fiscal_year": int(_number(row.get("fiscal_year")) or 0),
                "fiscal_quarter": int(_number(row.get("fiscal_quarter")) or 0),
                "period_end": _date_label(row.get("period_end")),
                "diluted_eps": eps,
                "source_kind": "REPORTED",
            }
        )

    ttm_eps = sum(eps_values)
    if ttm_eps <= 0:
        return _unavailable_valuation("NON_POSITIVE_TTM_EPS", latest_price=price)
    return {
        "status": "OK",
        "basis": "latest accepted price / four consecutive reported diluted EPS quarters",
        "latest_price": price,
        "latest_price_date": latest_price_date,
        "ttm_diluted_eps": ttm_eps,
        "current_per": price / ttm_eps,
        "quarters": evidence,
    }
