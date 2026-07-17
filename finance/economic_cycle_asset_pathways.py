"""Pure time-series evaluation for economic-cycle asset pathways."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import date
from math import isclose
from statistics import median
from typing import Literal

import pandas as pd


HORIZONS = (5, 21, 63)
MIN_HISTORICAL_CHANGES = 252
MAX_STALENESS_BUSINESS_DAYS = 5
ChangeMode = Literal["PERCENT_RETURN", "BASIS_POINT"]

PATHWAY_STATUS_LABELS = {
    "SUPPORTS_RISE": "상승 요인",
    "SUPPORTS_FALL": "하락 요인",
    "MIXED": "방향 혼재",
    "NEUTRAL": "중립",
    "UNAVAILABLE": "자료 부족",
}

PATHWAY_SPECS: dict[str, tuple[dict[str, object], ...]] = {
    "gold": (
        {
            "pathway_id": "real_yield",
            "label": "실질금리 경로",
            "members": (("DFII10", "DOWN"),),
            "core": True,
        },
        {
            "pathway_id": "dollar",
            "label": "달러 경로",
            "members": (("DX-Y.NYB", "DOWN"),),
            "core": True,
        },
        {
            "pathway_id": "short_rate",
            "label": "단기금리 경로",
            "members": (("DGS2", "DOWN"),),
            "core": False,
        },
        {
            "pathway_id": "risk_aversion",
            "label": "위험회피 경로",
            "members": (("VIXCLS", "UP"), ("BAA10Y", "UP")),
            "core": False,
        },
    ),
    "dollar": (
        {
            "pathway_id": "us_nominal_yield",
            "label": "미국 명목금리 경로",
            "members": (("DGS2", "UP"), ("DGS10", "UP")),
            "core": True,
        },
        {
            "pathway_id": "us_real_yield",
            "label": "미국 실질금리 경로",
            "members": (("DFII10", "UP"),),
            "core": True,
        },
        {
            "pathway_id": "risk_aversion",
            "label": "위험회피 경로",
            "members": (("VIXCLS", "UP"), ("BAA10Y", "UP")),
            "core": False,
        },
    ),
}

COMMON_UNMEASURED_PATHWAYS = (
    {
        "pathway_id": "official_flows",
        "label": "공식기관·ETF 수급",
        "reason_code": "SOURCE_NOT_APPROVED",
    },
    {
        "pathway_id": "external_events",
        "label": "뉴스·지정학적 사건",
        "reason_code": "OUT_OF_MEASURED_SCOPE",
    },
)

ECONOMIC_FACTOR_LABELS = {
    "activity_score": "생산·소비 활동",
    "labor_income_score": "고용·소득",
    "financial_leading_score": "금융·선행 여건",
    "inflation_policy_score": "물가·정책 압력",
}


def _as_date(value: object) -> date:
    return pd.Timestamp(value).date()


def _change(current: float, previous: float, mode: ChangeMode) -> float:
    if mode == "BASIS_POINT":
        return (current - previous) * 100.0
    if previous <= 0:
        raise ValueError("PERCENT_RETURN requires a positive lagged value")
    return (current / previous - 1.0) * 100.0


def _direction(value: float, *, threshold: float) -> str:
    magnitude = abs(value)
    if value == 0 or (
        magnitude < threshold
        and not isclose(magnitude, threshold, rel_tol=1e-9, abs_tol=1e-12)
    ):
        return "NEUTRAL"
    return "UP" if value > 0 else "DOWN"


def _unavailable(
    series_id: str,
    reason_code: str,
    *,
    as_of_date: date | None = None,
) -> dict[str, object]:
    return {
        "series_id": series_id,
        "as_of_date": as_of_date.isoformat() if as_of_date else None,
        "current_value": None,
        "unit": None,
        "freshness": "UNAVAILABLE",
        "reason_code": reason_code,
        "changes": {"5d": None, "21d": None, "63d": None},
        "thresholds": {"21d": None, "63d": None},
        "directions": {"21d": "UNAVAILABLE", "63d": "UNAVAILABLE"},
    }


def evaluate_series(
    points: Sequence[Mapping[str, object]],
    *,
    series_id: str,
    reference_date: object,
    change_mode: ChangeMode,
) -> dict[str, object]:
    """Evaluate current 5/21/63-day changes against prior five-year medians."""

    reference = _as_date(reference_date)
    by_date: dict[date, float] = {}
    for row in points:
        try:
            row_date = _as_date(row["date"])
            value = float(row["value"])
        except (KeyError, TypeError, ValueError):
            continue
        if row_date <= reference and (change_mode == "BASIS_POINT" or value > 0):
            by_date[row_date] = value

    ordered = sorted(by_date.items())
    if not ordered:
        return _unavailable(series_id, "MISSING_SERIES")

    latest_date = ordered[-1][0]
    business_age = len(
        pd.bdate_range(latest_date, reference, inclusive="right")
    )
    if business_age > MAX_STALENESS_BUSINESS_DAYS:
        return _unavailable(series_id, "STALE_SERIES", as_of_date=latest_date)
    if len(ordered) - 63 < MIN_HISTORICAL_CHANGES:
        return _unavailable(
            series_id,
            "INSUFFICIENT_HISTORY",
            as_of_date=latest_date,
        )

    values = [value for _, value in ordered]
    changes = {
        f"{horizon}d": _change(values[-1], values[-1 - horizon], change_mode)
        for horizon in HORIZONS
    }
    five_year_start = pd.Timestamp(reference) - pd.DateOffset(years=5)
    thresholds: dict[str, float] = {}
    for horizon in (21, 63):
        history = [
            abs(_change(values[index], values[index - horizon], change_mode))
            for index in range(horizon, len(values) - 1)
            if pd.Timestamp(ordered[index][0]) >= five_year_start
        ]
        if len(history) < MIN_HISTORICAL_CHANGES:
            return _unavailable(
                series_id,
                "INSUFFICIENT_HISTORY",
                as_of_date=latest_date,
            )
        thresholds[f"{horizon}d"] = median(history)

    unit = "bp" if change_mode == "BASIS_POINT" else "percent"
    return {
        "series_id": series_id,
        "as_of_date": latest_date.isoformat(),
        "current_value": values[-1],
        "unit": unit,
        "freshness": "CURRENT",
        "reason_code": None,
        "changes": changes,
        "thresholds": thresholds,
        "directions": {
            key: _direction(changes[key], threshold=thresholds[key])
            for key in ("21d", "63d")
        },
    }


def evaluate_spread(
    long_points: Sequence[Mapping[str, object]],
    short_points: Sequence[Mapping[str, object]],
    *,
    reference_date: object,
    series_id: str = "DGS10-DGS2",
) -> dict[str, object]:
    """Evaluate an aligned long-minus-short yield spread without interpolation."""
    reference = _as_date(reference_date)

    def values_by_date(
        points: Sequence[Mapping[str, object]],
    ) -> dict[date, float]:
        normalized: dict[date, float] = {}
        for row in points:
            try:
                row_date = _as_date(row["date"])
                value = float(row["value"])
            except (KeyError, TypeError, ValueError):
                continue
            if row_date <= reference:
                normalized[row_date] = value
        return normalized

    long_by_date = values_by_date(long_points)
    short_by_date = values_by_date(short_points)
    common_dates = sorted(set(long_by_date) & set(short_by_date))
    aligned = [
        {
            "date": row_date,
            "value": long_by_date[row_date] - short_by_date[row_date],
        }
        for row_date in common_dates
    ]
    result = evaluate_series(
        aligned,
        series_id=series_id,
        reference_date=reference,
        change_mode="BASIS_POINT",
    )
    if result.get("reason_code"):
        result["current_level_bp"] = None
        result["structure_status"] = "UNAVAILABLE"
        return result
    current_value = result.get("current_value")
    result["current_level_bp"] = (
        float(current_value) * 100.0 if current_value is not None else None
    )
    directions = result.get("directions") or {}
    if directions.get("21d") == directions.get("63d") == "UP":
        result["structure_status"] = "STEEPENING"
    elif directions.get("21d") == directions.get("63d") == "DOWN":
        result["structure_status"] = "FLATTENING"
    else:
        result["structure_status"] = "MIXED"
    return result


def evaluate_weekly_series(
    points: Sequence[Mapping[str, object]],
    *,
    series_id: str,
    reference_date: object,
) -> dict[str, object]:
    """Evaluate official weekly observations at 4-week and year-over-year horizons."""
    reference = _as_date(reference_date)
    by_date: dict[date, float] = {}
    for row in points:
        try:
            row_date = _as_date(row["date"])
            value = float(row["value"])
        except (KeyError, TypeError, ValueError):
            continue
        if row_date <= reference and value > 0:
            by_date[row_date] = value
    ordered = sorted(by_date.items())

    def unavailable(reason_code: str) -> dict[str, object]:
        latest = ordered[-1][0] if ordered else None
        return {
            "series_id": series_id,
            "as_of_date": latest.isoformat() if latest else None,
            "current_value": None,
            "unit": None,
            "freshness": "UNAVAILABLE",
            "reason_code": reason_code,
            "changes": {"4w": None, "52w": None},
            "directions": {"4w": "UNAVAILABLE", "52w": "UNAVAILABLE"},
        }

    if not ordered:
        return unavailable("MISSING_SERIES")
    latest_date = ordered[-1][0]
    if (reference - latest_date).days > 14:
        return unavailable("STALE_SERIES")
    if len(ordered) < 53:
        return unavailable("INSUFFICIENT_HISTORY")
    values = [value for _, value in ordered]
    changes = {
        "4w": _change(values[-1], values[-5], "PERCENT_RETURN"),
        "52w": _change(values[-1], values[-53], "PERCENT_RETURN"),
    }
    return {
        "series_id": series_id,
        "as_of_date": latest_date.isoformat(),
        "current_value": values[-1],
        "unit": "percent",
        "freshness": "CURRENT",
        "reason_code": None,
        "changes": changes,
        "directions": {
            key: _direction(value, threshold=0.0)
            for key, value in changes.items()
        },
    }


def build_observed_pathway(
    pathway_id: str,
    label: str,
    series: Mapping[str, object],
    *,
    interpretation: str,
) -> dict[str, object]:
    """Shape one measured series and its factual interpretation for the UI."""
    return {
        "pathway_id": pathway_id,
        "label": label,
        "status": (
            "UNAVAILABLE" if series.get("reason_code") else "OBSERVED"
        ),
        "series": dict(series),
        "interpretation": interpretation,
    }


def _series_points(
    rows: Sequence[Mapping[str, object]],
    *,
    id_key: str,
    series_id: str,
    date_key: str,
    value_key: str,
) -> list[dict[str, object]]:
    points: list[dict[str, object]] = []
    for row in rows:
        if str(row.get(id_key) or "").upper() != series_id.upper():
            continue
        points.append({"date": row.get(date_key), "value": row.get(value_key)})
    return points


def _series_status(evaluation: Mapping[str, object], rise_when: str) -> str:
    if evaluation.get("reason_code"):
        return "UNAVAILABLE"
    directions = evaluation.get("directions") or {}
    statuses: list[str] = []
    for horizon in ("21d", "63d"):
        direction = str(directions.get(horizon) or "UNAVAILABLE")
        if direction == "UNAVAILABLE":
            return "UNAVAILABLE"
        if direction == "NEUTRAL":
            statuses.append("NEUTRAL")
        elif direction == rise_when:
            statuses.append("SUPPORTS_RISE")
        else:
            statuses.append("SUPPORTS_FALL")
    if len(set(statuses)) == 1:
        return statuses[0]
    if "NEUTRAL" in statuses:
        return "NEUTRAL"
    return "MIXED"


def _combined_status(statuses: Sequence[str]) -> str:
    if not statuses or "UNAVAILABLE" in statuses:
        return "UNAVAILABLE"
    if len(set(statuses)) == 1:
        return statuses[0]
    if "MIXED" in statuses:
        return "MIXED"
    if "NEUTRAL" in statuses:
        return "NEUTRAL"
    return "MIXED"


def _economic_state(
    evidence: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    observations: list[dict[str, object]] = []
    for factor, label in ECONOMIC_FACTOR_LABELS.items():
        row = next(
            (item for item in evidence if str(item.get("factor") or "") == factor),
            None,
        )
        if row is None:
            direction = "UNAVAILABLE"
            value = None
        else:
            try:
                value = float(row.get("value"))
            except (TypeError, ValueError):
                value = None
            if value is None:
                direction = "UNAVAILABLE"
            elif value > 0.15:
                direction = "STRENGTHENING"
            elif value < -0.15:
                direction = "WEAKENING"
            else:
                direction = "NEUTRAL"
        observations.append(
            {
                "factor": factor,
                "label": label,
                "direction": direction,
                "value": value,
                "source_date": (row or {}).get("source_date"),
            }
        )

    grouped: dict[str, list[str]] = {
        "STRENGTHENING": [],
        "WEAKENING": [],
        "NEUTRAL": [],
        "UNAVAILABLE": [],
    }
    for row in observations:
        grouped[str(row["direction"])].append(str(row["label"]))
    clauses: list[str] = []
    if grouped["WEAKENING"]:
        clauses.append(f"{', '.join(grouped['WEAKENING'])}은 약화")
    if grouped["STRENGTHENING"]:
        clauses.append(f"{', '.join(grouped['STRENGTHENING'])}은 강화")
    if grouped["NEUTRAL"]:
        clauses.append(f"{', '.join(grouped['NEUTRAL'])}은 중립")
    if grouped["UNAVAILABLE"]:
        clauses.append(f"{', '.join(grouped['UNAVAILABLE'])}은 자료 부족")
    summary = ", ".join(clauses) + " 상태입니다." if clauses else "경제 근거가 없습니다."
    return {"summary": summary, "observations": observations}


def _price_context(
    symbol: str,
    evaluation: Mapping[str, object],
) -> dict[str, object]:
    status = _series_status(evaluation, "UP")
    price_status = {
        "SUPPORTS_RISE": "RISING",
        "SUPPORTS_FALL": "FALLING",
        "MIXED": "MIXED",
        "NEUTRAL": "NEUTRAL",
        "UNAVAILABLE": "UNAVAILABLE",
    }[status]
    changes = evaluation.get("changes") or {}
    return {
        "symbol": symbol,
        "as_of_date": evaluation.get("as_of_date"),
        "status": price_status,
        "reason_code": evaluation.get("reason_code"),
        "returns": {
            "one_week": changes.get("5d"),
            "one_month": changes.get("21d"),
            "three_months": changes.get("63d"),
        },
        "freshness": evaluation.get("freshness"),
        "source_basis": "stored continuous futures daily OHLCV",
    }


def _pathway_narrative(
    *,
    asset_group: str,
    economic_state: Mapping[str, object],
    pathways: Sequence[Mapping[str, object]],
    price_context: Mapping[str, object],
) -> str:
    rising = [str(row["label"]) for row in pathways if row["status"] == "SUPPORTS_RISE"]
    falling = [str(row["label"]) for row in pathways if row["status"] == "SUPPORTS_FALL"]
    mixed = [str(row["label"]) for row in pathways if row["status"] in {"MIXED", "NEUTRAL"}]
    unavailable = [str(row["label"]) for row in pathways if row["status"] == "UNAVAILABLE"]
    clauses = [str(economic_state.get("summary") or "")]
    if rising:
        clauses.append(f"측정된 {', '.join(rising)}는 상승 요인으로 나타납니다.")
    if falling:
        clauses.append(f"측정된 {', '.join(falling)}는 하락 요인으로 나타납니다.")
    if mixed:
        clauses.append(f"{', '.join(mixed)}는 방향이 뚜렷하지 않습니다.")
    if unavailable:
        clauses.append(f"{', '.join(unavailable)}는 자료가 부족합니다.")
    price_label = {
        "RISING": "상승",
        "FALLING": "하락",
        "MIXED": "기간별 혼재",
        "NEUTRAL": "중립",
        "UNAVAILABLE": "확인 불가",
    }.get(str(price_context.get("status")), "확인 불가")
    subject = "달러지수" if asset_group == "dollar" else "금 가격"
    clauses.append(f"실제 {subject}의 1개월·3개월 방향은 {price_label}입니다.")
    if asset_group == "dollar":
        clauses.append("해외 상대금리가 아직 없어 달러의 국가 간 금리 차이는 판정하지 않습니다.")
    clauses.append("이 결과는 측정된 경로를 나눈 설명이며 가격 원인을 확정하지 않습니다.")
    return " ".join(clause for clause in clauses if clause)


def build_asset_pathway_contexts(
    *,
    evidence: Sequence[Mapping[str, object]],
    market_rows: Sequence[Mapping[str, object]],
    price_rows: Sequence[Mapping[str, object]],
    reference_date: object,
) -> dict[str, dict[str, object]]:
    """Build deterministic gold and dollar contexts from measured market paths."""

    evaluations: dict[str, dict[str, object]] = {}
    for series_id in ("DGS2", "DGS10", "DFII10", "VIXCLS", "BAA10Y"):
        mode: ChangeMode = "PERCENT_RETURN" if series_id == "VIXCLS" else "BASIS_POINT"
        evaluations[series_id] = evaluate_series(
            _series_points(
                market_rows,
                id_key="series_id",
                series_id=series_id,
                date_key="observation_date",
                value_key="value",
            ),
            series_id=series_id,
            reference_date=reference_date,
            change_mode=mode,
        )
    for symbol in ("GC=F", "DX-Y.NYB"):
        evaluations[symbol] = evaluate_series(
            _series_points(
                price_rows,
                id_key="provider_symbol",
                series_id=symbol,
                date_key="candle_time_utc",
                value_key="close",
            ),
            series_id=symbol,
            reference_date=reference_date,
            change_mode="PERCENT_RETURN",
        )

    economic_state = _economic_state(evidence)
    contexts: dict[str, dict[str, object]] = {}
    for asset_group, specs in PATHWAY_SPECS.items():
        pathways: list[dict[str, object]] = []
        for spec in specs:
            member_rows: list[dict[str, object]] = []
            member_statuses: list[str] = []
            for series_id, rise_when in spec["members"]:
                evaluation = evaluations[str(series_id)]
                status = _series_status(evaluation, str(rise_when))
                member_statuses.append(status)
                member_rows.append(
                    {
                        "series_id": series_id,
                        "status": status,
                        "evaluation": evaluation,
                    }
                )
            status = _combined_status(member_statuses)
            pathways.append(
                {
                    "pathway_id": spec["pathway_id"],
                    "label": spec["label"],
                    "status": status,
                    "status_label": PATHWAY_STATUS_LABELS[status],
                    "reason_code": (
                        "PATHWAY_SERIES_UNAVAILABLE"
                        if status == "UNAVAILABLE"
                        else None
                    ),
                    "core": bool(spec["core"]),
                    "series": member_rows,
                }
            )

        price_symbol = "GC=F" if asset_group == "gold" else "DX-Y.NYB"
        price_context = _price_context(price_symbol, evaluations[price_symbol])
        valid_core = sum(
            row["core"] and row["status"] != "UNAVAILABLE" for row in pathways
        )
        price_available = price_context["status"] != "UNAVAILABLE"
        if asset_group == "gold" and price_available and valid_core == 2:
            coverage = "SUFFICIENT"
        elif price_available and valid_core >= 1:
            coverage = "PARTIAL"
        else:
            coverage = "INSUFFICIENT"

        unmeasured = [dict(row) for row in COMMON_UNMEASURED_PATHWAYS]
        if asset_group == "dollar":
            unmeasured.insert(
                0,
                {
                    "pathway_id": "relative_rates",
                    "label": "해외 상대금리",
                    "reason_code": "RELATIVE_RATE_NOT_COLLECTED",
                },
            )
        contexts[asset_group] = {
            "asset_group": asset_group,
            "coverage": coverage,
            "economic_state": economic_state,
            "pathways": pathways,
            "price_context": price_context,
            "unmeasured_pathways": unmeasured,
        }
        contexts[asset_group]["narrative"] = _pathway_narrative(
            asset_group=asset_group,
            economic_state=economic_state,
            pathways=pathways,
            price_context=price_context,
        )
    return contexts
