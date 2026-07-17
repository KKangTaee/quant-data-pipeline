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
    *,
    source_basis: str = "stored continuous futures daily OHLCV",
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
        "source_basis": source_basis,
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


def _daily_direction_text(evaluation: Mapping[str, object]) -> str:
    if evaluation.get("reason_code"):
        return "자료가 부족합니다."
    directions = evaluation.get("directions") or {}
    one_month = str(directions.get("21d") or "UNAVAILABLE")
    three_months = str(directions.get("63d") or "UNAVAILABLE")
    labels = {
        "UP": "상승",
        "DOWN": "하락",
        "NEUTRAL": "중립",
        "UNAVAILABLE": "확인 불가",
    }
    if one_month == three_months:
        return f"최근 1개월과 3개월 모두 {labels[one_month]}했습니다."
    return (
        f"최근 1개월은 {labels[one_month]}, "
        f"3개월은 {labels[three_months]}으로 기간별 흐름이 엇갈립니다."
    )


def _movement_metric(
    metric_id: str,
    label: str,
    evaluation: Mapping[str, object],
    *,
    level_unit: str,
    current_value: object | None = None,
) -> dict[str, object]:
    return {
        "metric_id": metric_id,
        "label": label,
        "as_of_date": evaluation.get("as_of_date"),
        "current_value": (
            evaluation.get("current_value")
            if current_value is None
            else current_value
        ),
        "level_unit": level_unit,
        "change_unit": evaluation.get("unit"),
        "changes": dict(evaluation.get("changes") or {}),
        "directions": dict(evaluation.get("directions") or {}),
        "freshness": evaluation.get("freshness"),
        "reason_code": evaluation.get("reason_code"),
    }


def build_rates_context(
    *,
    evaluations: Mapping[str, Mapping[str, object]],
    economic_state: Mapping[str, object],
) -> dict[str, object]:
    """Build a factual rates-structure context from stored yield observations."""
    dgs2 = evaluations["DGS2"]
    dgs10 = evaluations["DGS10"]
    spread = evaluations["DGS10-DGS2"]
    real_yield = evaluations["DFII10"]
    breakeven = evaluations["T10YIE"]
    current_movement = [
        _movement_metric("DGS2", "미국 2년 국채 수익률", dgs2, level_unit="percent"),
        _movement_metric(
            "DGS10", "미국 10년 국채 수익률", dgs10, level_unit="percent"
        ),
        _movement_metric(
            "DGS10-DGS2",
            "10년-2년 금리차",
            spread,
            level_unit="bp",
            current_value=spread.get("current_level_bp"),
        ),
    ]
    observed_pathways = [
        build_observed_pathway(
            "real_yield",
            "10년 실질금리",
            real_yield,
            interpretation=_daily_direction_text(real_yield),
        ),
        build_observed_pathway(
            "breakeven_inflation",
            "10년 기대인플레이션",
            breakeven,
            interpretation=_daily_direction_text(breakeven),
        ),
    ]
    core_available = all(
        not evaluation.get("reason_code") for evaluation in (dgs2, dgs10, spread)
    )
    component_count = sum(
        not evaluation.get("reason_code") for evaluation in (real_yield, breakeven)
    )
    if core_available and component_count == 2:
        coverage = "SUFFICIENT"
    elif core_available or component_count:
        coverage = "PARTIAL"
    else:
        coverage = "INSUFFICIENT"

    spread_label = {
        "STEEPENING": "10년-2년 금리차는 최근 1개월과 3개월에 걸쳐 확대됐습니다.",
        "FLATTENING": "10년-2년 금리차는 최근 1개월과 3개월에 걸쳐 축소됐습니다.",
        "MIXED": "10년-2년 금리차의 1개월과 3개월 흐름은 엇갈립니다.",
        "UNAVAILABLE": "10년-2년 금리차를 계산할 자료가 부족합니다.",
    }[str(spread.get("structure_status") or "UNAVAILABLE")]
    component_directions = [
        str((evaluation.get("directions") or {}).get("21d") or "UNAVAILABLE")
        for evaluation in (real_yield, breakeven)
    ]
    if component_directions == ["UP", "UP"]:
        component_text = "실질금리와 기대인플레이션은 최근 1개월 모두 상승했습니다."
    elif component_directions == ["DOWN", "DOWN"]:
        component_text = "실질금리와 기대인플레이션은 최근 1개월 모두 하락했습니다."
    elif "UNAVAILABLE" in component_directions:
        component_text = "10년물 구성 경로는 계산 가능한 자료만 표시합니다."
    else:
        component_text = "실질금리와 기대인플레이션의 최근 1개월 방향은 엇갈립니다."
    current_interpretation = [
        f"2년물은 {_daily_direction_text(dgs2)}",
        f"10년물은 {_daily_direction_text(dgs10)}",
        spread_label,
        component_text,
    ]
    limitations = [
        "금리 변화와 경제지표의 동행을 인과관계로 해석하지 않습니다."
    ]
    if coverage != "SUFFICIENT":
        limitations.append("일부 금리 경로의 최신성 또는 이력이 부족합니다.")
    return {
        "asset_group": "rates",
        "coverage": coverage,
        "economic_state": dict(economic_state),
        "current_movement": current_movement,
        "observed_pathways": observed_pathways,
        "current_interpretation": current_interpretation,
        "next_check_conditions": [
            "2년물의 1개월 변화 방향이 다음 관측에서도 이어지는지 확인합니다.",
            "10년-2년 금리차의 확대·축소가 이어지는지 확인합니다.",
            "실질금리와 기대인플레이션의 방향이 함께 움직이는지 확인합니다.",
        ],
        "provenance": [
            "FRED DGS2·DGS10·DFII10·T10YIE 저장 관측치",
            "10년-2년 금리차는 동일 관측일의 DGS10-DGS2 계산값",
        ],
        "limitations": limitations,
        "narrative": " ".join(current_interpretation),
    }


def build_equities_context(
    *,
    evaluations: Mapping[str, Mapping[str, object]],
    economic_state: Mapping[str, object],
    sp500_earnings: Mapping[str, object] | None,
) -> dict[str, object]:
    """Build an S&P 500 context with parallel market and actual-earnings paths."""
    spx = evaluations["^GSPC"]
    spy = evaluations["SPY"]
    if not spx.get("reason_code"):
        price_symbol = "^GSPC"
        price_evaluation = spx
        provenance = ["^GSPC stored S&P 500 index daily OHLCV"]
    elif not spy.get("reason_code"):
        price_symbol = "SPY"
        price_evaluation = spy
        provenance = ["SPY stored S&P 500 ETF fallback daily OHLCV"]
    else:
        price_symbol = "^GSPC"
        price_evaluation = spx
        provenance = ["^GSPC와 SPY 저장 가격이 모두 부족함"]
    price_context = _price_context(
        price_symbol,
        price_evaluation,
        source_basis=(
            "stored S&P 500 index daily OHLCV"
            if price_symbol == "^GSPC"
            else "stored S&P 500 ETF fallback daily OHLCV"
        ),
    )

    observed_pathways = [
        build_observed_pathway(
            "real_yield",
            "10년 실질금리",
            evaluations["DFII10"],
            interpretation=_daily_direction_text(evaluations["DFII10"]),
        ),
        build_observed_pathway(
            "credit_spread",
            "Baa 회사채-10년 국채 스프레드",
            evaluations["BAA10Y"],
            interpretation=_daily_direction_text(evaluations["BAA10Y"]),
        ),
        build_observed_pathway(
            "volatility",
            "VIX",
            evaluations["VIXCLS"],
            interpretation=_daily_direction_text(evaluations["VIXCLS"]),
        ),
    ]

    earnings = dict(sp500_earnings or {})
    earnings_reason = earnings.get("reason_code")
    growth = earnings.get("growth_pct")
    if earnings.get("status") != "READY" or growth is None:
        earnings_reason = earnings_reason or "INSUFFICIENT_EARNINGS_HISTORY"
    latest_release = earnings.get("latest_release_date")
    reference_candidates = [
        evaluation.get("as_of_date")
        for evaluation in evaluations.values()
        if evaluation.get("as_of_date")
    ]
    if not earnings_reason and latest_release and reference_candidates:
        reference = max(_as_date(value) for value in reference_candidates)
        if (reference - _as_date(latest_release)).days > 180:
            earnings_reason = "STALE_EARNINGS"
    earnings_series = {
        "series_id": "SP500_ACTUAL_TTM_EPS",
        "as_of_date": earnings.get("latest_period_end"),
        "release_date": latest_release,
        "current_value": earnings.get("current_ttm_eps"),
        "prior_value": earnings.get("prior_ttm_eps"),
        "unit": "percent",
        "freshness": "UNAVAILABLE" if earnings_reason else "CURRENT",
        "reason_code": earnings_reason,
        "changes": {"yoy_ttm": growth if not earnings_reason else None},
        "directions": {
            "yoy_ttm": (
                "UNAVAILABLE"
                if earnings_reason
                else _direction(float(growth), threshold=0.0)
            )
        },
    }
    earnings_interpretation = (
        "최근 완료 분기 8개로 실제 TTM EPS의 전년 대비 변화를 계산했습니다."
        if not earnings_reason
        else "완료된 실제 EPS 분기 자료가 부족하거나 최신성이 제한됩니다."
    )
    observed_pathways.append(
        build_observed_pathway(
            "actual_earnings",
            "실제 TTM EPS",
            earnings_series,
            interpretation=earnings_interpretation,
        )
    )
    price_available = price_context["status"] != "UNAVAILABLE"
    available_paths = sum(row["status"] == "OBSERVED" for row in observed_pathways)
    if price_available and available_paths == 4:
        coverage = "SUFFICIENT"
    elif price_available and available_paths:
        coverage = "PARTIAL"
    else:
        coverage = "INSUFFICIENT"
    current_interpretation = [
        f"S&P 500 가격은 {_daily_direction_text(price_evaluation)}",
        *[
            f"{row['label']}은 {row['interpretation']}"
            for row in observed_pathways
        ],
    ]
    limitations = [
        "가격·금리·신용·변동성·이익의 동시 변화를 인과관계로 합산하지 않습니다."
    ]
    if earnings_reason:
        limitations.append("실제 EPS 경로는 완료된 8개 분기 기준을 충족하지 못했습니다.")
    return {
        "asset_group": "equities",
        "coverage": coverage,
        "economic_state": dict(economic_state),
        "price_context": price_context,
        "current_movement": [
            _movement_metric(
                price_symbol,
                "S&P 500",
                price_evaluation,
                level_unit="index",
            )
        ],
        "observed_pathways": observed_pathways,
        "current_interpretation": current_interpretation,
        "next_check_conditions": [
            "S&P 500의 1개월·3개월 흐름이 같은 방향으로 이어지는지 확인합니다.",
            "실질금리·신용스프레드·VIX의 측정 방향이 유지되는지 확인합니다.",
            "새 실제 분기 EPS가 발표되면 TTM 전년 대비 변화를 갱신합니다.",
        ],
        "provenance": [
            *provenance,
            "FRED DFII10·BAA10Y·VIXCLS 저장 관측치",
            "S&P official actual as-reported EPS",
        ],
        "limitations": limitations,
        "narrative": " ".join(current_interpretation),
    }


def _weekly_direction_text(evaluation: Mapping[str, object]) -> str:
    if evaluation.get("reason_code"):
        return "주간 자료가 부족하거나 최신성이 제한됩니다."
    changes = evaluation.get("changes") or {}
    four_week = float(changes.get("4w") or 0.0)
    year = float(changes.get("52w") or 0.0)
    return (
        f"최근 4주 {four_week:+.1f}%, 전년 동기 대비 {year:+.1f}% 변했습니다."
    )


def build_commodities_context(
    *,
    evaluations: Mapping[str, Mapping[str, object]],
    economic_state: Mapping[str, object],
    gold_context: Mapping[str, object],
) -> dict[str, object]:
    """Build separate WTI, copper, and reused-gold observation contexts."""
    wti_price = evaluations["CL=F"]
    wti_price_context = _price_context("CL=F", wti_price)
    wti_specs = (
        ("inventory", "미국 원유 재고", "WCESTUS1"),
        ("production", "미국 원유 생산", "WCRFPUS2"),
        ("product_supplied", "미국 석유제품 공급량", "WRPUPUS2"),
    )
    wti_paths = [
        build_observed_pathway(
            pathway_id,
            label,
            evaluations[series_id],
            interpretation=_weekly_direction_text(evaluations[series_id]),
        )
        for pathway_id, label, series_id in wti_specs
    ]
    wti_paths.append(
        build_observed_pathway(
            "dollar",
            "미국 달러지수",
            evaluations["DX-Y.NYB"],
            interpretation=_daily_direction_text(evaluations["DX-Y.NYB"]),
        )
    )
    wti_available_paths = sum(row["status"] == "OBSERVED" for row in wti_paths)
    if wti_price_context["status"] != "UNAVAILABLE" and wti_available_paths == 4:
        wti_coverage = "SUFFICIENT"
    elif wti_price_context["status"] != "UNAVAILABLE" and wti_available_paths:
        wti_coverage = "PARTIAL"
    else:
        wti_coverage = "INSUFFICIENT"
    wti_interpretation = [
        f"WTI 가격은 {_daily_direction_text(wti_price)}",
        *[f"{row['label']}은 {row['interpretation']}" for row in wti_paths],
    ]
    wti = {
        "asset_id": "wti",
        "label": "WTI 원유",
        "coverage": wti_coverage,
        "price_context": wti_price_context,
        "current_movement": [
            _movement_metric("CL=F", "WTI 원유", wti_price, level_unit="USD")
        ],
        "observed_pathways": wti_paths,
        "current_interpretation": wti_interpretation,
        "next_check_conditions": [
            "WTI의 1개월·3개월 가격 흐름이 이어지는지 확인합니다.",
            "EIA 재고·생산·제품 공급량의 최근 4주 변화가 이어지는지 확인합니다.",
            "달러지수의 1개월 변화 방향이 유지되는지 확인합니다.",
        ],
        "provenance": [
            "stored CL=F continuous futures daily OHLCV",
            "EIA WCESTUS1·WCRFPUS2·WRPUPUS2 official weekly XLS",
            "stored DX-Y.NYB continuous futures daily OHLCV",
        ],
        "limitations": [
            "EIA 주간 수급과 WTI 일별 가격은 서로 다른 관측 주기를 유지합니다.",
            "동시에 관찰된 수급·달러 변화를 WTI 가격의 인과관계로 확정하지 않습니다.",
        ],
        "narrative": " ".join(wti_interpretation),
    }

    copper_price = evaluations["HG=F"]
    copper_price_context = _price_context("HG=F", copper_price)
    activity = next(
        (
            row
            for row in economic_state.get("observations") or []
            if row.get("factor") == "activity_score"
        ),
        {},
    )
    activity_reason = (
        None if activity.get("direction") != "UNAVAILABLE" else "MISSING_ACTIVITY"
    )
    activity_series = {
        "series_id": "activity_score",
        "as_of_date": activity.get("source_date"),
        "current_value": activity.get("value"),
        "unit": "score",
        "freshness": "CURRENT" if not activity_reason else "UNAVAILABLE",
        "reason_code": activity_reason,
        "changes": {},
        "directions": {"current": activity.get("direction")},
    }
    copper_paths = [
        build_observed_pathway(
            "dollar",
            "미국 달러지수",
            evaluations["DX-Y.NYB"],
            interpretation=_daily_direction_text(evaluations["DX-Y.NYB"]),
        ),
        build_observed_pathway(
            "us_activity",
            "미국 생산·소비 활동",
            activity_series,
            interpretation=(
                f"현재 측정 방향은 {activity.get('direction')}입니다."
                if not activity_reason
                else "활동지표 자료가 부족합니다."
            ),
        ),
    ]
    copper_available_paths = sum(
        row["status"] == "OBSERVED" for row in copper_paths
    )
    copper_coverage = (
        "PARTIAL"
        if copper_price_context["status"] != "UNAVAILABLE"
        and copper_available_paths
        else "INSUFFICIENT"
    )
    copper_interpretation = [
        f"구리 가격은 {_daily_direction_text(copper_price)}",
        *[f"{row['label']}은 {row['interpretation']}" for row in copper_paths],
    ]
    copper = {
        "asset_id": "copper",
        "label": "구리",
        "coverage": copper_coverage,
        "price_context": copper_price_context,
        "current_movement": [
            _movement_metric("HG=F", "구리", copper_price, level_unit="USD")
        ],
        "observed_pathways": copper_paths,
        "current_interpretation": copper_interpretation,
        "next_check_conditions": [
            "구리의 1개월·3개월 가격 흐름이 이어지는지 확인합니다.",
            "달러지수와 미국 활동지표의 측정 방향을 각각 확인합니다.",
        ],
        "provenance": [
            "stored HG=F continuous futures daily OHLCV",
            "stored DX-Y.NYB continuous futures daily OHLCV",
            "economic-cycle canonical U.S. activity observation",
        ],
        "limitations": [
            "연결된 산업활동 자료는 미국 중심이며 글로벌 구리 수요를 대표하지 않습니다.",
            "가격·달러·활동지표의 동시 변화를 인과관계로 확정하지 않습니다.",
        ],
        "narrative": " ".join(copper_interpretation),
    }

    gold_narrative = str(gold_context.get("narrative") or "")
    gold = {
        "asset_id": "gold",
        "label": "금",
        "coverage": gold_context.get("coverage") or "INSUFFICIENT",
        "price_context": dict(gold_context.get("price_context") or {}),
        "current_movement": [],
        "observed_pathways": [
            dict(row) for row in gold_context.get("pathways") or []
        ],
        "current_interpretation": [gold_narrative] if gold_narrative else [],
        "next_check_conditions": [
            "금 가격과 실질금리·달러 경로의 다음 측정값을 각각 확인합니다."
        ],
        "provenance": ["기존 2차 금 관측 컨텍스트 재사용"],
        "limitations": [
            str(row.get("label") or row.get("reason_code") or "")
            for row in gold_context.get("unmeasured_pathways") or []
        ],
        "narrative": gold_narrative,
    }
    assets = [wti, copper, gold]
    coverage = (
        "INSUFFICIENT"
        if all(row["coverage"] == "INSUFFICIENT" for row in assets)
        else "PARTIAL"
        if any(row["coverage"] != "SUFFICIENT" for row in assets)
        else "SUFFICIENT"
    )
    return {
        "asset_group": "commodities",
        "coverage": coverage,
        "economic_state": dict(economic_state),
        "assets": assets,
        "current_movement": [],
        "observed_pathways": [],
        "current_interpretation": [],
        "next_check_conditions": [],
        "provenance": ["WTI·구리 신규 경로와 기존 금 컨텍스트의 결합"],
        "limitations": [],
        "narrative": "WTI·구리·금은 서로 다른 측정 경로로 구분합니다.",
    }
def build_asset_pathway_contexts(
    *,
    evidence: Sequence[Mapping[str, object]],
    market_rows: Sequence[Mapping[str, object]],
    price_rows: Sequence[Mapping[str, object]],
    reference_date: object,
    sp500_earnings: Mapping[str, object] | None = None,
) -> dict[str, dict[str, object]]:
    """Build deterministic asset contexts from measured market paths."""

    evaluations: dict[str, dict[str, object]] = {}
    for series_id in (
        "DGS2",
        "DGS10",
        "DFII10",
        "T10YIE",
        "VIXCLS",
        "BAA10Y",
    ):
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
    evaluations["DGS10-DGS2"] = evaluate_spread(
        _series_points(
            market_rows,
            id_key="series_id",
            series_id="DGS10",
            date_key="observation_date",
            value_key="value",
        ),
        _series_points(
            market_rows,
            id_key="series_id",
            series_id="DGS2",
            date_key="observation_date",
            value_key="value",
        ),
        reference_date=reference_date,
    )
    for symbol in ("GC=F", "DX-Y.NYB", "CL=F", "HG=F", "^GSPC", "SPY"):
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
    for series_id in ("WCESTUS1", "WCRFPUS2", "WRPUPUS2"):
        evaluations[series_id] = evaluate_weekly_series(
            _series_points(
                market_rows,
                id_key="series_id",
                series_id=series_id,
                date_key="observation_date",
                value_key="value",
            ),
            series_id=series_id,
            reference_date=reference_date,
        )

    economic_state = _economic_state(evidence)
    contexts: dict[str, dict[str, object]] = {
        "rates": build_rates_context(
            evaluations=evaluations,
            economic_state=economic_state,
        ),
        "equities": build_equities_context(
            evaluations=evaluations,
            economic_state=economic_state,
            sp500_earnings=sp500_earnings,
        ),
    }
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
    contexts["commodities"] = build_commodities_context(
        evaluations=evaluations,
        economic_state=economic_state,
        gold_context=contexts["gold"],
    )
    return contexts
