from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

import pandas as pd

from finance.data.us_stock_turnaround import (
    TURNAROUND_CONCEPT_FAMILIES,
    TURNAROUND_INSTANT_CONCEPT_FAMILIES,
    build_turnaround_quarterly_series,
)
from finance.loaders.us_stock_valuation import QueryFn, _query, load_us_stock_identity


InputLoader = Callable[..., dict[str, Any]]
_DURATION_UNITS = ("USD", "USD/share", "USD/shares", "shares")
_INSTANT_UNITS = ("USD", "shares")


def _concepts(families: Mapping[str, tuple[str, ...]]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(concept for values in families.values() for concept in values))


def _statement_rows(
    *,
    symbol: str,
    start_year: int,
    end_year: int,
    as_of_date: str,
    period_type: str,
    concepts: tuple[str, ...],
    units: tuple[str, ...],
    query_fn: QueryFn | None,
) -> list[dict[str, Any]]:
    concept_placeholders = ", ".join(["%s"] * len(concepts))
    unit_placeholders = ", ".join(["%s"] * len(units))
    period_filter = (
        "AND period_type IN ('Q', 'FY')"
        if period_type == "duration"
        else "AND period_type IN ('Q', 'FY', 'I')"
    )
    return _query(
        "finance_fundamental",
        f"""
        SELECT symbol, concept, unit, source_period_type, period_type,
               fiscal_year, fiscal_quarter, period_start, period_end,
               value, available_at, report_date, form_type, accession_no, source
        FROM nyse_financial_statement_values
        WHERE symbol = %s
          AND fiscal_year BETWEEN %s AND %s
          AND available_at <= %s
          AND source_period_type = '{period_type}'
          {period_filter}
          AND concept IN ({concept_placeholders})
          AND unit IN ({unit_placeholders})
        ORDER BY fiscal_year ASC, fiscal_quarter ASC, period_end ASC,
                 available_at ASC, accession_no ASC
        """,
        (symbol, start_year, end_year, as_of_date, *concepts, *units),
        query_fn=query_fn,
    )


def _coverage(
    *,
    profile: Mapping[str, Any],
    price_rows: list[dict[str, Any]],
    series: Mapping[str, Any],
    as_of: pd.Timestamp,
    price_start: str,
) -> dict[str, Any]:
    latest_price = price_rows[-1] if price_rows else None
    latest_price_date = pd.to_datetime((latest_price or {}).get("date"), errors="coerce")
    profile_date = pd.to_datetime(profile.get("last_collected_at"), errors="coerce")
    price_missing = pd.isna(latest_price_date) or (
        pd.Timestamp(as_of).normalize() - pd.Timestamp(latest_price_date).normalize()
    ).days > 7
    profile_stale = (
        not profile
        or not profile.get("market_cap")
        or pd.isna(profile_date)
        or pd.isna(latest_price_date)
        or abs(
            (
                pd.Timestamp(profile_date).normalize()
                - pd.Timestamp(latest_price_date).normalize()
            ).days
        )
        > 7
    )
    timeline = [dict(row) for row in series.get("timeline") or []]
    available = [row for row in timeline if row.get("status") == "AVAILABLE"]
    latest = available[-1] if available else {}
    missing_concepts = [
        metric
        for metric in ("revenue", "operating_income", "ocf", "diluted_eps")
        if not any(row.get(metric) is not None for row in available)
    ]
    statement_core_missing = (
        len(available) < 8
        or latest.get("ttm_revenue") is None
        or latest.get("ttm_ocf") is None
    )
    latest_text = (
        pd.Timestamp(latest_price_date).strftime("%Y-%m-%d")
        if not pd.isna(latest_price_date)
        else None
    )
    return {
        "profile_stale": bool(profile_stale),
        "price_missing": bool(price_missing),
        "price_missing_range": {
            "start": latest_text or price_start,
            "end": as_of.strftime("%Y-%m-%d"),
        }
        if price_missing
        else None,
        "statement_core_missing": bool(statement_core_missing),
        "available_quarters": len(available),
        "missing_concepts": missing_concepts,
    }


def load_us_stock_turnaround_inputs(
    symbol: str,
    *,
    as_of_date: str | None = None,
    visible_quarters: int = 20,
    query_fn: QueryFn | None = None,
) -> dict[str, Any]:
    """Read one selected stock's bounded profile, price, and filing evidence."""
    normalized = str(symbol or "").strip().upper()
    as_of = pd.Timestamp(as_of_date or pd.Timestamp.now().strftime("%Y-%m-%d")).normalize()
    resolved_visible = min(20, max(8, int(visible_quarters)))
    end_year = int(as_of.year)
    start_year = end_year - 6
    price_start = f"{start_year:04d}-01-01"
    end_text = as_of.strftime("%Y-%m-%d")
    identity = load_us_stock_identity(normalized, query_fn=query_fn)
    window = {
        "statement_start": price_start,
        "price_start": price_start,
        "as_of_date": end_text,
        "start_fiscal_year": start_year,
        "end_fiscal_year": end_year,
        "fiscal_years": 7,
        "visible_quarters": resolved_visible,
    }
    if identity is None:
        return {
            "identity": None,
            "profile": {},
            "latest_price": None,
            "price_rows": [],
            "statement_rows": [],
            "window": window,
            "coverage": {"identity_missing": True},
        }

    profiles = _query(
        "finance_meta",
        """
        SELECT symbol, long_name, quote_type, exchange, sector, industry, country,
               market_cap, status, last_collected_at
        FROM nyse_asset_profile
        WHERE symbol = %s
          AND kind = 'stock'
          AND status = 'active'
        ORDER BY last_collected_at DESC
        LIMIT 1
        """,
        (normalized,),
        query_fn=query_fn,
    )
    profile = dict(profiles[0]) if profiles else {}
    profile["currency"] = "USD"
    price_rows = _query(
        "finance_price",
        """
        SELECT symbol, `date`, close, adj_close, stock_splits
        FROM nyse_price_history
        WHERE symbol = %s
          AND timeframe = '1d'
          AND `date` BETWEEN %s AND %s
        ORDER BY `date` ASC
        """,
        (normalized, price_start, end_text),
        query_fn=query_fn,
    )
    duration_rows = _statement_rows(
        symbol=normalized,
        start_year=start_year,
        end_year=end_year,
        as_of_date=end_text,
        period_type="duration",
        concepts=_concepts(TURNAROUND_CONCEPT_FAMILIES),
        units=_DURATION_UNITS,
        query_fn=query_fn,
    )
    instant_rows = _statement_rows(
        symbol=normalized,
        start_year=start_year,
        end_year=end_year,
        as_of_date=end_text,
        period_type="instant",
        concepts=_concepts(TURNAROUND_INSTANT_CONCEPT_FAMILIES),
        units=_INSTANT_UNITS,
        query_fn=query_fn,
    )
    statements = [*duration_rows, *instant_rows]
    series = build_turnaround_quarterly_series(
        statements,
        price_rows,
        as_of_date=end_text,
    )
    latest_price = dict(price_rows[-1]) if price_rows else None
    if latest_price is not None:
        latest_price["currency"] = "USD"
    return {
        "identity": identity,
        "profile": profile,
        "latest_price": latest_price,
        "price_rows": price_rows,
        "statement_rows": statements,
        "series": series,
        "window": window,
        "coverage": _coverage(
            profile=profile,
            price_rows=price_rows,
            series=series,
            as_of=as_of,
            price_start=price_start,
        ),
    }


def build_us_stock_turnaround_collection_plan(
    symbol: str,
    *,
    as_of_date: str | None = None,
    loaded_inputs: Mapping[str, Any] | None = None,
    input_loader: InputLoader = load_us_stock_turnaround_inputs,
) -> dict[str, Any]:
    """Map only repairable selected-stock raw gaps to explicit collection scopes."""
    normalized = str(symbol or "").strip().upper()
    inputs = dict(loaded_inputs or input_loader(normalized, as_of_date=as_of_date))
    identity = inputs.get("identity")
    base = {
        "symbol": normalized,
        "identity": identity,
        "scopes": [],
        "missing_ranges": {},
        "missing_concepts": [],
    }
    if not isinstance(identity, Mapping) or str(identity.get("symbol") or "").strip().upper() != normalized:
        return {
            **base,
            "status": "ERROR",
            "reason_code": "IDENTITY_MISMATCH",
            "reason": "선택 ticker와 current SEC identity가 일치하지 않습니다.",
        }
    if str(identity.get("instrument_type") or "common_stock") != "common_stock" or str(
        identity.get("adr_unit_status") or "not_adr"
    ) == "unverified":
        return {
            **base,
            "status": "NOT_APPLICABLE",
            "reason_code": "INSTRUMENT_UNSUPPORTED",
            "reason": "검증된 미국 보통주 단위에만 전환 분석을 제공합니다.",
        }
    coverage = dict(inputs.get("coverage") or {})
    scopes: list[str] = []
    ranges: dict[str, Any] = {}
    if coverage.get("profile_stale"):
        scopes.append("asset_profile")
    if coverage.get("price_missing"):
        scopes.append("prices")
        ranges["prices"] = coverage.get("price_missing_range") or {
            "start": dict(inputs.get("window") or {}).get("price_start"),
            "end": dict(inputs.get("window") or {}).get("as_of_date"),
        }
    if coverage.get("statement_core_missing"):
        scopes.append("sec_statements")
        ranges["sec_statements"] = {
            "start": dict(inputs.get("window") or {}).get("statement_start"),
            "end": dict(inputs.get("window") or {}).get("as_of_date"),
        }
    if not scopes:
        return {**base, "status": "READY", "reason_code": None, "reason": None}
    if not str(identity.get("cik") or "").strip():
        return {
            **base,
            "status": "BLOCKED",
            "reason_code": "CIK_MISSING",
            "reason": "현재 분석은 유지하지만 SEC CIK를 확인하기 전에는 원자료를 수집할 수 없습니다.",
        }
    return {
        **base,
        "status": "COLLECTABLE",
        "reason_code": "RAW_DATA_GAP",
        "reason": "저장된 profile, 가격 또는 SEC 전환 분석 근거를 보강할 수 있습니다.",
        "scopes": scopes,
        "missing_ranges": ranges,
        "missing_concepts": list(coverage.get("missing_concepts") or []),
    }
