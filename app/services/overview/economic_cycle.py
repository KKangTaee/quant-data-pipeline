"""Compact DB-only read model for the Overview economic-cycle surface."""

from __future__ import annotations

import json
import math
from collections.abc import Callable, Mapping, Sequence
from datetime import date, datetime
from typing import Any

import pandas as pd

from app.services.overview.economic_cycle_freshness import (
    build_economic_cycle_freshness,
)
from app.services.overview.economic_cycle_asset_freshness import (
    build_asset_pathway_freshness,
)
from finance.economic_cycle_interpretation import (
    build_market_implications,
    evidence_direction,
    evidence_group,
    translate_reason_code,
)
from finance.loaders.economic_cycle import load_cycle_history, load_cycle_snapshot
from finance.loaders.economic_cycle_assets import (
    load_economic_cycle_asset_prices,
    load_economic_cycle_market_series,
)
from finance.loaders.sp500_valuation import load_sp500_actual_eps_history

SCHEMA_VERSION = "economic_cycle_v3"
OBSERVED_PHASES = ("recovery", "expansion", "slowdown", "contraction")
PHASE_LABELS = {
    "recovery": "회복",
    "expansion": "확장",
    "slowdown": "둔화",
    "contraction": "위축",
    "recession": "침체",
}
PHASE_HEADLINE_SUMMARIES = {
    "recovery": "실물경제 수준은 낮지만 최근 3개월 흐름이 개선된 상태입니다.",
    "expansion": "실물경제 수준이 높고 최근 3개월 흐름도 개선된 상태입니다.",
    "slowdown": "실물경제 수준은 높지만 최근 3개월 흐름이 약화된 상태입니다.",
    "contraction": "실물경제 수준이 낮고 최근 3개월 흐름도 약화된 상태입니다.",
}
INTRAMONTH_FACTORS = (
    "activity_score",
    "labor_income_score",
    "financial_leading_score",
    "inflation_policy_score",
)
CONFIDENCE_LABELS = {
    "HIGH": "높음",
    "MEDIUM": "보통",
    "LIMITED": "제한",
}
REVISION_SENSITIVITY_LABELS = {
    "STABLE": "안정",
    "SENSITIVE": "수정 민감",
    "UNAVAILABLE": "비교 불가",
}
RECENT_CHANGE_LABELS = {1: "최근 1개월", 3: "최근 3개월", 6: "최근 6개월"}
RECENT_CHANGE_STATUS_LABELS = {
    "STRENGTHENING": "강화",
    "WEAKENING": "약화",
    "MIXED": "혼조",
    "UNAVAILABLE": "판단 제한",
}
TRANSITION_STATUS_LABELS = {
    "MAINTAIN": "현재 국면 유지",
    "WATCH": "전환 조건 관찰",
    "CONFIRMED": "전환 확인",
}
CONDITION_LABELS = {
    "persistence": "지속성",
    "diffusion": "확산도",
    "corroboration": "활동·고용 동반 확인",
}
CONTEXT_LABELS = {
    "TOWARD_TARGET": "다음 국면 방향을 지지",
    "SUPPORT_CURRENT": "현재 국면을 지지",
    "MIXED": "혼조",
}
ANCHOR_SOURCE_LABELS = {
    "INITIALIZED": "초기 기준",
    "CONFIRMED": "조건 확인",
    "LEGACY_OBSERVED": "조회 이력 내 최초 관측",
    "UNKNOWN": "기준일 기록 없음",
}
TRANSITION_FORECAST_CONTRACT_VERSION = "transition_forecast_v1"
PRESSURE_LEVEL_LABELS = {
    "LOW": "낮음",
    "NORMAL": "보통",
    "ELEVATED": "높아지는 중",
    "HIGH": "높음",
}
PRESSURE_LEVEL_SUMMARIES = {
    "LOW": "가까운 발표 안의 전환 가능성이 낮아 현재 국면 유지 가능성을 우선 봅니다.",
    "NORMAL": "전환 징후가 평소 범위에 있어 현재 국면과 전환 가능성을 함께 봅니다.",
    "ELEVATED": "가까운 발표 안의 전환 가능성이 높아지는 구간이라 조건 변화를 주의 깊게 봅니다.",
    "HIGH": "가까운 발표 안의 전환 가능성이 높은 구간이지만 정확한 전환 시점을 뜻하지는 않습니다.",
}
TRANSITION_DRIVER_LABELS = {
    "level": "실물경제 수준",
    "momentum": "실물경제 모멘텀",
    "phase_duration": "현재 국면 지속기간",
    "positive_breadth": "개선 지표 확산도",
    "phase_context": "현재 국면의 과거 전환 패턴",
    "FEDFUNDS_delta_3m": "정책금리 변화",
    "PCEPILFE_gap_2pct": "근원물가의 2% 괴리",
    "yield_curve_delta_3m": "10년-2년 금리차 변화",
    "BAA10Y_delta_3m": "회사채 신용스프레드 변화",
    "PERMIT_change_6m_pct": "주택허가 6개월 변화",
}
PRESSURE_EFFECT_LABELS = {
    "RAISES_PRESSURE": "전환압력을 높이는 중",
    "LOWERS_PRESSURE": "전환압력을 낮추는 중",
    "NEUTRAL": "전환압력 영향 중립",
}


def _json_value(value: object, fallback: object) -> object:
    if value is None:
        return fallback
    if isinstance(value, (dict, list, tuple)):
        return value
    try:
        return json.loads(str(value))
    except (TypeError, ValueError, json.JSONDecodeError):
        return fallback


def _empty_model(
    *,
    status: str,
    reason_code: str,
    as_of_date: object = None,
    freshness_date: str | date | datetime | None = None,
) -> dict[str, object]:
    reason = translate_reason_code(reason_code)
    economic_as_of_date = str(as_of_date or "") or None
    market_implications = build_market_implications((), [])
    for item in market_implications:
        item["economic_as_of_date"] = economic_as_of_date
    return {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "as_of_date": str(as_of_date or "") or None,
        "model_version": None,
        "intramonth_change": None,
        "data_freshness": build_economic_cycle_freshness(
            None,
            today=freshness_date,
            read_error=status == "ERROR",
        ),
        "headline": {
            "phase": None,
            "phase_label": "판단 제한",
            "summary": reason,
            "reason_code": reason_code,
        },
        "observed_state": {
            "phase": None,
            "phase_label": None,
            "confidence": "LIMITED",
            "confidence_label": CONFIDENCE_LABELS["LIMITED"],
            "revision_sensitivity": "UNAVAILABLE",
            "revision_sensitivity_label": REVISION_SENSITIVITY_LABELS[
                "UNAVAILABLE"
            ],
            "data_status": "UNAVAILABLE",
        },
        "recent_changes": [],
        "transition_monitor": None,
        "transition_forecast": None,
        "cycle_map": {"phase_order": list(OBSERVED_PHASES), "points": []},
        "evidence": [],
        "market_implications": market_implications,
        "sources": [],
        "limitations": [reason, "NBER 공식 판정이나 투자 지시가 아닙니다."],
    }


def _evidence(snapshot: Mapping[str, object]) -> list[dict[str, object]]:
    raw_rows = _json_value(snapshot.get("top_evidence_json"), [])
    rows = [dict(item) for item in raw_rows if isinstance(item, Mapping)]
    normalized = []
    for item in rows:
        factor = str(item.get("factor") or item.get("series_id") or "unknown")
        normalized.append(
            {
                "factor": factor,
                "series_id": str(item.get("series_id") or "") or None,
                "group": evidence_group(factor),
                "direction": evidence_direction(item.get("value")),
                "value": (
                    float(item["value"])
                    if isinstance(item.get("value"), (int, float))
                    else None
                ),
                "source_date": str(
                    item.get("source_date")
                    or snapshot.get("data_cutoff_date")
                    or snapshot.get("as_of_date")
                    or ""
                )[:10]
                or None,
                "source_basis": "FRED/ALFRED point-in-time",
            }
        )
    normalized.sort(key=lambda item: 0 if item["group"] == "real_economy" else 1)
    return normalized[:10]


def _factor_values(snapshot: Mapping[str, object]) -> dict[str, float]:
    raw_rows = _json_value(snapshot.get("top_evidence_json"), [])
    values: dict[str, float] = {}
    for raw in raw_rows if isinstance(raw_rows, (list, tuple)) else []:
        if not isinstance(raw, Mapping):
            continue
        factor = str(raw.get("factor") or "")
        if factor not in INTRAMONTH_FACTORS:
            continue
        try:
            value = float(raw.get("value"))
        except (TypeError, ValueError):
            continue
        if math.isfinite(value):
            values[factor] = value
    return values


def _compact_source_coverage(value: object) -> dict[str, object]:
    raw = _json_value(value, {})
    if not isinstance(raw, Mapping):
        return {"requested_series": None, "available_series": None, "series": []}
    series = []
    raw_series = raw.get("series")
    if isinstance(raw_series, (list, tuple)):
        for item in raw_series[:25]:
            if not isinstance(item, Mapping):
                continue
            series.append(
                {
                    "series_id": str(item.get("series_id") or "") or None,
                    "status": str(item.get("status") or "") or None,
                    "latest_observation_date": str(
                        item.get("latest_observation_date") or ""
                    )[:10]
                    or None,
                    "staleness_days": item.get("staleness_days"),
                }
            )
    return {
        "requested_series": raw.get("requested_series"),
        "available_series": raw.get("available_series"),
        "series": series,
    }


def _finite_number(value: object) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if math.isfinite(parsed) else None


def _transition_forecast(
    snapshot: Mapping[str, object],
    *,
    observed_state: Mapping[str, object],
) -> dict[str, object] | None:
    """Decode only the explicit unrestricted production forecast contract."""

    raw = _json_value(snapshot.get("transition_monitor_json"), {})
    if (
        not isinstance(raw, Mapping)
        or raw.get("contract_version") != TRANSITION_FORECAST_CONTRACT_VERSION
    ):
        return None
    current_phase = str(raw.get("current_phase") or "")
    if current_phase not in OBSERVED_PHASES or current_phase != observed_state.get("phase"):
        return None

    pressure_raw = raw.get("pressure")
    destination_raw = raw.get("destination")
    if not isinstance(pressure_raw, Mapping) or not isinstance(destination_raw, Mapping):
        return None
    probability = _finite_number(pressure_raw.get("probability"))
    percentile = _finite_number(pressure_raw.get("historical_percentile"))
    if (
        probability is None
        or percentile is None
        or not 0.0 <= probability <= 1.0
        or not 0.0 <= percentile <= 1.0
    ):
        return None
    pressure_level = str(pressure_raw.get("level") or "NORMAL").upper()
    if pressure_level not in PRESSURE_LEVEL_LABELS:
        pressure_level = "NORMAL"

    raw_probabilities = destination_raw.get("probabilities")
    if not isinstance(raw_probabilities, Mapping):
        return None
    probabilities = {
        phase: _finite_number(raw_probabilities.get(phase))
        for phase in OBSERVED_PHASES
    }
    if (
        any(value is None or not 0.0 <= value <= 1.0 for value in probabilities.values())
        or abs(sum(float(value) for value in probabilities.values()) - 1.0) > 1e-6
        or float(probabilities[current_phase] or 0.0) > 1e-9
    ):
        return None
    primary_phase = str(destination_raw.get("primary_phase") or "")
    alternatives = sorted(
        (
            {
                "phase": phase,
                "phase_label": PHASE_LABELS[phase],
                "probability": float(probabilities[phase] or 0.0),
            }
            for phase in OBSERVED_PHASES
            if phase != current_phase
        ),
        key=lambda item: float(item["probability"]),
        reverse=True,
    )
    if primary_phase != alternatives[0]["phase"]:
        primary_phase = str(alternatives[0]["phase"])

    drivers: list[dict[str, object]] = []
    raw_drivers = raw.get("drivers")
    if isinstance(raw_drivers, (list, tuple)):
        for item in raw_drivers:
            if not isinstance(item, Mapping):
                continue
            driver_id = str(item.get("driver_id") or "")
            if driver_id not in TRANSITION_DRIVER_LABELS:
                continue
            current_effect = str(item.get("current_effect") or "NEUTRAL").upper()
            higher_effect = str(item.get("higher_value_effect") or "NEUTRAL").upper()
            drivers.append(
                {
                    **dict(item),
                    "driver_id": driver_id,
                    "label": TRANSITION_DRIVER_LABELS[driver_id],
                    "current_effect": current_effect,
                    "current_effect_label": PRESSURE_EFFECT_LABELS.get(
                        current_effect, PRESSURE_EFFECT_LABELS["NEUTRAL"]
                    ),
                    "higher_value_effect": higher_effect,
                    "higher_value_effect_label": PRESSURE_EFFECT_LABELS.get(
                        higher_effect, PRESSURE_EFFECT_LABELS["NEUTRAL"]
                    ),
                }
            )
    drivers.sort(key=lambda item: abs(float(item.get("contribution") or 0.0)), reverse=True)
    return {
        "contract_version": TRANSITION_FORECAST_CONTRACT_VERSION,
        "status": "READY",
        "current_phase": current_phase,
        "current_phase_label": PHASE_LABELS[current_phase],
        "pressure": {
            **dict(pressure_raw),
            "probability": probability,
            "historical_percentile": percentile,
            "level": pressure_level,
            "level_label": PRESSURE_LEVEL_LABELS[pressure_level],
            "summary": PRESSURE_LEVEL_SUMMARIES[pressure_level],
        },
        "destination": {
            **dict(destination_raw),
            "probabilities": {
                phase: float(value or 0.0) for phase, value in probabilities.items()
            },
            "primary_phase": primary_phase,
            "primary_phase_label": PHASE_LABELS[primary_phase],
            "alternatives": alternatives,
        },
        "drivers": drivers,
        "boundary": (
            "전환압력은 다음 3개 usable release 안에 공식 국면이 바뀔 가능성이고, "
            "다음 국면 분포는 전환이 발생한다는 조건 아래의 비교입니다."
        ),
    }


def _observed_state(snapshot: Mapping[str, object]) -> dict[str, object]:
    """Decode persisted observed state without falling back to model probabilities."""

    raw = _json_value(snapshot.get("observed_state_json"), {})
    if not isinstance(raw, Mapping):
        raw = {}
    phase = str(raw.get("phase") or "")
    data_status = str(raw.get("data_status") or "UNAVAILABLE").upper()
    confidence = str(raw.get("confidence") or "LIMITED").upper()
    revision = str(raw.get("revision_sensitivity") or "UNAVAILABLE").upper()
    if phase not in OBSERVED_PHASES:
        phase = None
        data_status = "UNAVAILABLE"
        confidence = "LIMITED"
    output = dict(raw)
    output.update(
        {
            "phase": phase,
            "phase_label": PHASE_LABELS.get(phase),
            "confidence": confidence,
            "confidence_label": CONFIDENCE_LABELS.get(confidence, "제한"),
            "revision_sensitivity": revision,
            "revision_sensitivity_label": REVISION_SENSITIVITY_LABELS.get(
                revision, "비교 불가"
            ),
            "data_status": data_status,
        }
    )
    return output


def _recent_changes(snapshot: Mapping[str, object]) -> list[dict[str, object]]:
    raw = _json_value(snapshot.get("recent_changes_json"), [])
    rows: list[dict[str, object]] = []
    if not isinstance(raw, (list, tuple)):
        return rows
    for item in raw:
        if not isinstance(item, Mapping):
            continue
        try:
            horizon = int(item.get("horizon_months") or 0)
        except (TypeError, ValueError):
            continue
        if horizon not in RECENT_CHANGE_LABELS:
            continue
        status = str(item.get("status") or "UNAVAILABLE").upper()
        normalized = dict(item)
        normalized.update(
            {
                "horizon_months": horizon,
                "label": RECENT_CHANGE_LABELS[horizon],
                "status": status,
                "status_label": RECENT_CHANGE_STATUS_LABELS.get(
                    status, "판단 제한"
                ),
            }
        )
        rows.append(normalized)
    return sorted(rows, key=lambda item: int(item["horizon_months"]))


def _next_observed_phase(phase: object) -> str | None:
    normalized = str(phase or "")
    if normalized not in OBSERVED_PHASES:
        return None
    index = OBSERVED_PHASES.index(normalized)
    return OBSERVED_PHASES[(index + 1) % len(OBSERVED_PHASES)]


def _previous_observed_state(
    history_rows: Sequence[Mapping[str, object]],
    *,
    current_date: object,
) -> dict[str, object] | None:
    cutoff = str(current_date or "")[:10]
    candidates: list[tuple[str, Mapping[str, object]]] = []
    for row in history_rows:
        row_date = str(row.get("as_of_date") or "")[:10]
        if row_date and (not cutoff or row_date < cutoff):
            candidates.append((row_date, row))
    if not candidates:
        return None
    return _observed_state(max(candidates, key=lambda item: item[0])[1])


def _score_label(value: object) -> str:
    parsed = _finite_number(value)
    return "-" if parsed is None else f"{parsed:+.2f}"


def _current_transition_conditions(
    *,
    observed_state: Mapping[str, object],
    previous_state: Mapping[str, object] | None,
    target_phase: str,
) -> list[dict[str, object]]:
    uses_momentum = target_phase in {"recovery", "slowdown"}
    positive = target_phase in {"recovery", "expansion"}
    axis = "momentum" if uses_momentum else "level"
    activity_axis = "activity_momentum" if uses_momentum else "activity_level"
    labor_axis = "labor_income_momentum" if uses_momentum else "labor_income_level"
    breadth_axis = "momentum_breadth" if uses_momentum else "level_breadth"
    breadth_available_axis = (
        "momentum_breadth_available" if uses_momentum else "level_breadth_available"
    )

    current_axis = _finite_number(observed_state.get(axis))
    previous_axis = (
        _finite_number(previous_state.get(axis)) if previous_state is not None else None
    )
    persistence_available = current_axis is not None and previous_axis is not None
    persistence_met = bool(
        persistence_available
        and ((current_axis >= 0 and previous_axis >= 0) if positive else (current_axis < 0 and previous_axis < 0))
    )
    persistence_status = (
        "UNAVAILABLE" if not persistence_available else "MET" if persistence_met else "UNMET"
    )

    breadth = _finite_number(observed_state.get(breadth_axis))
    available_pairs_value = observed_state.get(breadth_available_axis)
    if available_pairs_value is None:
        available_pairs_value = observed_state.get("available_series")
    try:
        available_pairs = int(available_pairs_value or 0)
    except (TypeError, ValueError):
        available_pairs = 0
    diffusion_available = breadth is not None and available_pairs >= 6
    diffusion_met = bool(
        diffusion_available
        and (breadth >= 0.60 if positive else breadth <= 0.40)
    )
    diffusion_status = (
        "UNAVAILABLE" if not diffusion_available else "MET" if diffusion_met else "UNMET"
    )
    supportive_ratio = None if breadth is None else breadth if positive else 1.0 - breadth
    supportive_count = (
        None
        if supportive_ratio is None or available_pairs <= 0
        else int(round(supportive_ratio * available_pairs))
    )
    required_count = math.ceil(available_pairs * 0.60) if available_pairs > 0 else None

    activity = _finite_number(observed_state.get(activity_axis))
    labor = _finite_number(observed_state.get(labor_axis))
    corroboration_available = activity is not None and labor is not None
    corroboration_met = bool(
        corroboration_available
        and ((activity >= 0 and labor >= 0) if positive else (activity < 0 and labor < 0))
    )
    corroboration_status = (
        "UNAVAILABLE"
        if not corroboration_available
        else "MET"
        if corroboration_met
        else "UNMET"
    )

    return [
        {
            "condition_id": "persistence",
            "label": CONDITION_LABELS["persistence"],
            "status": persistence_status,
            "value_label": f"현재 {_score_label(current_axis)} / 이전 {_score_label(previous_axis)}",
            "threshold_label": "2회 연속 0 이상" if positive else "2회 연속 0 미만",
        },
        {
            "condition_id": "diffusion",
            "label": CONDITION_LABELS["diffusion"],
            "status": diffusion_status,
            "value_label": (
                "자료 부족"
                if supportive_count is None or supportive_ratio is None
                else f"{supportive_count}/{available_pairs}개 · {supportive_ratio:.0%}"
            ),
            "threshold_label": (
                "비교 가능한 지표 6개 이상"
                if available_pairs < 6
                else f"{required_count}/{available_pairs}개 이상 · 60% 이상"
            ),
        },
        {
            "condition_id": "corroboration",
            "label": CONDITION_LABELS["corroboration"],
            "status": corroboration_status,
            "value_label": f"활동 {_score_label(activity)} / 고용·소득 {_score_label(labor)}",
            "threshold_label": "두 항목 모두 0 이상" if positive else "두 항목 모두 0 미만",
        },
    ]


def _current_transition_guidance(
    *,
    observed_state: Mapping[str, object],
    history_rows: Sequence[Mapping[str, object]],
) -> dict[str, object] | None:
    observed_phase = str(observed_state.get("phase") or "")
    from_phase = observed_phase
    target_phase = _next_observed_phase(from_phase)
    if from_phase not in OBSERVED_PHASES or target_phase not in OBSERVED_PHASES:
        return None
    previous_state = _previous_observed_state(
        history_rows,
        current_date=observed_state.get("as_of_date"),
    )
    conditions = _current_transition_conditions(
        observed_state=observed_state,
        previous_state=previous_state,
        target_phase=target_phase,
    )
    conditions_met = sum(item["status"] == "MET" for item in conditions)
    conditions_available = sum(item["status"] != "UNAVAILABLE" for item in conditions)
    if conditions_met == len(conditions):
        status = "CONFIRMED"
        status_label = f"{PHASE_LABELS[target_phase]} 전환 조건 충족"
    else:
        status = "WATCH"
        status_label = (
            f"{PHASE_LABELS[target_phase]} 전환 미확인"
            if conditions_available
            else f"{PHASE_LABELS[target_phase]} 전환 판단 제한"
        )
    return {
        "from_phase": from_phase,
        "from_phase_label": PHASE_LABELS[from_phase],
        "target_phase": target_phase,
        "target_phase_label": PHASE_LABELS[target_phase],
        "status": status,
        "status_label": status_label,
        "conditions_met": conditions_met,
        "conditions_total": len(conditions),
        "conditions": conditions,
    }


def _transition_monitor(
    snapshot: Mapping[str, object],
    history_rows: Sequence[Mapping[str, object]] = (),
    *,
    observed_state: Mapping[str, object] | None = None,
) -> dict[str, object] | None:
    raw = _json_value(snapshot.get("transition_monitor_json"), {})
    if not isinstance(raw, Mapping) or not raw:
        return None
    if raw.get("contract_version") == TRANSITION_FORECAST_CONTRACT_VERSION:
        phase = str(raw.get("current_phase") or "")
        return {
            "contract_version": TRANSITION_FORECAST_CONTRACT_VERSION,
            "observed_phase": phase if phase in OBSERVED_PHASES else None,
            "observed_phase_label": PHASE_LABELS.get(phase),
            "status": "MAINTAIN",
            "status_label": "현재 공식 국면 확인",
            "conditions_met": 0,
            "conditions_total": 0,
            "conditions": [],
            "context": [],
            "current_transition": None,
        }
    output = dict(raw)
    status = str(raw.get("status") or "MAINTAIN").upper()
    output["status"] = status
    output["status_label"] = TRANSITION_STATUS_LABELS.get(status, "전환 조건 관찰")
    for field in ("observed_phase", "anchor_phase", "target_phase"):
        phase = str(raw.get(field) or "")
        output[field] = phase if phase in OBSERVED_PHASES else None
        output[f"{field}_label"] = PHASE_LABELS.get(phase)
    anchor_phase = output.get("anchor_phase")
    anchor_started_at = str(raw.get("anchor_started_at") or "")[:10] or None
    anchor_confirmed_at = str(raw.get("anchor_confirmed_at") or "")[:10] or None
    anchor_source = str(raw.get("anchor_source") or "").upper()
    confirmed_candidates: list[str] = []
    first_seen_candidates: list[str] = []
    if anchor_phase and (
        not anchor_started_at or anchor_source not in {"INITIALIZED", "CONFIRMED"}
    ):
        for row in history_rows:
            record = _json_value(row.get("transition_monitor_json"), {})
            if not isinstance(record, Mapping):
                continue
            row_date = str(row.get("as_of_date") or "")[:10]
            if not row_date:
                continue
            if str(record.get("anchor_phase") or "") == anchor_phase:
                first_seen_candidates.append(row_date)
            if (
                str(record.get("status") or "").upper() == "CONFIRMED"
                and str(record.get("target_phase") or "") == anchor_phase
            ):
                confirmed_candidates.append(
                    str(record.get("confirmed_at") or row_date)[:10]
                )
        if confirmed_candidates:
            anchor_confirmed_at = max(confirmed_candidates)
            anchor_started_at = anchor_confirmed_at
            anchor_source = "CONFIRMED"
        elif first_seen_candidates:
            anchor_started_at = min(first_seen_candidates)
            anchor_confirmed_at = None
            anchor_source = "LEGACY_OBSERVED"
        else:
            anchor_source = "UNKNOWN"
    elif anchor_source not in ANCHOR_SOURCE_LABELS:
        anchor_source = "UNKNOWN"
    output.update(
        {
            "anchor_started_at": anchor_started_at,
            "anchor_source": anchor_source,
            "anchor_source_label": ANCHOR_SOURCE_LABELS[anchor_source],
            "anchor_confirmed_at": anchor_confirmed_at,
        }
    )
    conditions: list[dict[str, object]] = []
    raw_conditions = raw.get("conditions")
    if isinstance(raw_conditions, (list, tuple)):
        for item in raw_conditions:
            if not isinstance(item, Mapping):
                continue
            condition = dict(item)
            condition_id = str(item.get("condition_id") or "")
            condition["label"] = CONDITION_LABELS.get(condition_id, condition_id)
            condition["status"] = str(item.get("status") or "UNMET").upper()
            conditions.append(condition)
    output["conditions"] = conditions
    context: list[dict[str, object]] = []
    raw_context = raw.get("context")
    if isinstance(raw_context, (list, tuple)):
        for item in raw_context:
            if not isinstance(item, Mapping):
                continue
            record = dict(item)
            relation = str(item.get("relation") or "MIXED").upper()
            record["relation"] = relation
            record["relation_label"] = CONTEXT_LABELS.get(relation, "혼조")
            context.append(record)
    output["context"] = context
    normalized_observed_state = observed_state or _observed_state(snapshot)
    output["current_transition"] = _current_transition_guidance(
        observed_state=normalized_observed_state,
        history_rows=history_rows,
    )
    return output


def _cycle_map(
    history_rows: Sequence[Mapping[str, object]],
    current_snapshot: Mapping[str, object],
) -> dict[str, object]:
    """Build a short actual-coordinate trail; never infer points from probabilities."""

    monitor = _json_value(current_snapshot.get("transition_monitor_json"), {})
    if (
        isinstance(monitor, Mapping)
        and monitor.get("contract_version") == TRANSITION_FORECAST_CONTRACT_VERSION
        and isinstance(monitor.get("recent_phase_history"), (list, tuple))
    ):
        confirmed_points: list[dict[str, object]] = []
        for item in monitor["recent_phase_history"]:
            if not isinstance(item, Mapping):
                continue
            phase = str(item.get("phase") or "")
            level = _finite_number(item.get("level"))
            momentum = _finite_number(item.get("momentum"))
            point_date = str(item.get("date") or "")[:10]
            if (
                phase not in OBSERVED_PHASES
                or level is None
                or momentum is None
                or not point_date
            ):
                continue
            confirmed_points.append(
                {
                    **dict(item),
                    "date": point_date,
                    "level": level,
                    "momentum": momentum,
                    "phase": phase,
                    "phase_label": PHASE_LABELS[phase],
                    "nber_recession": bool(item.get("nber_recession")),
                }
            )
        if confirmed_points:
            return {
                "phase_order": list(OBSERVED_PHASES),
                "points": confirmed_points[-12:],
            }

    def replay_rank(snapshot: Mapping[str, object]) -> tuple[str, int, str]:
        try:
            row_id = int(snapshot.get("id") or -1)
        except (TypeError, ValueError):
            row_id = -1
        return (
            str(snapshot.get("updated_at") or snapshot.get("created_at") or ""),
            row_id,
            str(snapshot.get("model_version") or ""),
        )

    def point_from(snapshot: Mapping[str, object]) -> tuple[str, dict[str, object]] | None:
        state = _observed_state(snapshot)
        level = _finite_number(state.get("level"))
        momentum = _finite_number(state.get("momentum"))
        phase = state.get("phase")
        point_date = str(
            state.get("as_of_date") or snapshot.get("as_of_date") or ""
        )[:10]
        if not point_date or level is None or momentum is None or phase not in OBSERVED_PHASES:
            return None
        return point_date, {
            "date": point_date,
            "level": level,
            "momentum": momentum,
            "phase": phase,
            "phase_label": PHASE_LABELS[str(phase)],
            "nber_recession": bool(snapshot.get("nber_recession")),
            "confidence": state.get("confidence"),
            "revision_sensitivity": state.get("revision_sensitivity"),
        }

    by_date: dict[str, dict[str, object]] = {}
    selected_rank: dict[str, tuple[str, int, str]] = {}
    for snapshot in history_rows:
        resolved = point_from(snapshot)
        if resolved is None:
            continue
        point_date, point = resolved
        rank = replay_rank(snapshot)
        if point_date not in selected_rank or rank > selected_rank[point_date]:
            by_date[point_date] = point
            selected_rank[point_date] = rank

    # The canonical current snapshot always owns its date, even if a replay row was
    # regenerated later with a different model version.
    current = point_from(current_snapshot)
    if current is not None:
        point_date, point = current
        by_date[point_date] = point
    points = sorted(by_date.values(), key=lambda item: str(item["date"]))[-12:]
    return {"phase_order": list(OBSERVED_PHASES), "points": points}


def _intramonth_change(
    monthly: Mapping[str, object],
    intramonth: Mapping[str, object] | None,
) -> dict[str, object] | None:
    """Compare a provisional row with its exact monthly baseline only."""

    if not intramonth:
        return None
    try:
        monthly_date = pd.Timestamp(monthly.get("as_of_date")).date()
        baseline_date = pd.Timestamp(intramonth.get("baseline_as_of_date")).date()
        intramonth_date = pd.Timestamp(intramonth.get("as_of_date")).date()
    except (TypeError, ValueError):
        return None
    if baseline_date != monthly_date or intramonth_date <= monthly_date:
        return None
    if str(intramonth.get("model_version") or "") != str(
        monthly.get("model_version") or ""
    ):
        return None

    monthly_state = _observed_state(monthly)
    provisional_state = _observed_state(intramonth)
    baseline_raw = _finite_number(monthly_state.get("raw_level"))
    current_raw = _finite_number(provisional_state.get("raw_level"))
    available_value = _finite_number(provisional_state.get("available_series"))
    available = int(available_value) if available_value is not None else 0
    if available < 6 or provisional_state.get("data_status") == "UNAVAILABLE":
        visible_state: dict[str, object] | None = None
    else:
        visible_state = provisional_state

    baseline_factors = _factor_values(monthly)
    current_factors = _factor_values(intramonth)
    factor_deltas = [
        {
            "factor": factor,
            "baseline": baseline_factors[factor],
            "current": current_factors[factor],
            "delta": current_factors[factor] - baseline_factors[factor],
        }
        for factor in INTRAMONTH_FACTORS
        if factor in baseline_factors and factor in current_factors
    ]
    return {
        "baseline_as_of_date": baseline_date.isoformat(),
        "as_of_date": intramonth_date.isoformat(),
        "provisional": True,
        "label": "월말 이후 잠정 변화",
        "model_version": str(intramonth.get("model_version") or "") or None,
        "raw_level_delta": (
            current_raw - baseline_raw
            if current_raw is not None and baseline_raw is not None
            else None
        ),
        "observed_state": visible_state,
        "recent_changes": _recent_changes(intramonth),
        "factor_deltas": factor_deltas,
        "source_collected_at": str(intramonth.get("source_collected_at") or "")
        or None,
        "source_coverage": _compact_source_coverage(
            intramonth.get("source_coverage_json")
        ),
    }


def _sources(
    snapshot: Mapping[str, object], evidence: Sequence[Mapping[str, object]]
) -> list[dict[str, object]]:
    dates = list(
        dict.fromkeys(
            str(item.get("source_date") or "")
            for item in evidence
            if item.get("source_date")
        )
    )
    if not dates:
        dates = [
            str(snapshot.get("data_cutoff_date") or snapshot.get("as_of_date") or "")[
                :10
            ]
        ]
    return [
        {
            "name": "FRED/ALFRED 빈티지",
            "source_date": source_date,
            "basis": "forecast-origin eligible observations",
        }
        for source_date in dates
        if source_date
    ]


def build_economic_cycle_read_model(
    *,
    as_of_date: str | date | None = None,
    snapshot_loader: Callable[..., Mapping[str, object] | None] | None = None,
    intramonth_loader: Callable[..., Mapping[str, object] | None] | None = None,
    history_loader: Callable[..., Sequence[Mapping[str, object]]] | None = None,
    market_series_loader: Callable[..., Sequence[Mapping[str, object]]] | None = None,
    asset_price_loader: Callable[..., Sequence[Mapping[str, object]]] | None = None,
    sp500_earnings_loader: Callable[..., Mapping[str, object]] | None = None,
    price_reference_date: str | date | None = None,
    freshness_date: str | date | datetime | None = None,
) -> dict[str, object]:
    """Adapt persisted compact rows; never fetch, fit, write, or mutate UI state."""

    load_snapshot = snapshot_loader or load_cycle_snapshot
    load_history = history_loader or load_cycle_history
    try:
        snapshot = load_snapshot(as_of_date=as_of_date)
    except Exception:
        return _empty_model(
            status="ERROR",
            reason_code="READ_ERROR",
            as_of_date=as_of_date,
            freshness_date=freshness_date,
        )
    if not snapshot:
        return _empty_model(
            status="LIMITED",
            reason_code="NOT_MATERIALIZED",
            as_of_date=as_of_date,
            freshness_date=freshness_date,
        )

    resolved_snapshot = dict(snapshot)
    snapshot_date = str(resolved_snapshot.get("as_of_date") or as_of_date or "")[:10]
    try:
        end = pd.Timestamp(snapshot_date).date()
        start = (pd.Timestamp(end) - pd.DateOffset(months=11)).date()
        history_rows = load_history(start_date=start, end_date=end)
    except Exception:
        return _empty_model(
            status="ERROR",
            reason_code="READ_ERROR",
            as_of_date=snapshot_date,
            freshness_date=freshness_date,
        )

    observed_state = _observed_state(resolved_snapshot)
    recent_changes = _recent_changes(resolved_snapshot)
    transition_monitor = _transition_monitor(
        resolved_snapshot,
        history_rows,
        observed_state=observed_state,
    )
    transition_forecast = _transition_forecast(
        resolved_snapshot,
        observed_state=observed_state,
    )
    cycle_map = _cycle_map(history_rows, resolved_snapshot)
    evidence = _evidence(resolved_snapshot)
    load_intramonth = (
        intramonth_loader
        if intramonth_loader is not None
        else load_cycle_snapshot
        if snapshot_loader is None
        else None
    )
    intramonth_row: Mapping[str, object] | None = None
    if load_intramonth is not None:
        try:
            intramonth_row = load_intramonth(
                as_of_date=as_of_date,
                run_kind="intramonth_nowcast",
            )
        except Exception:
            intramonth_row = None
    intramonth = _intramonth_change(resolved_snapshot, intramonth_row)
    cycle_freshness = build_economic_cycle_freshness(
        intramonth,
        today=freshness_date,
    )

    market_reference = pd.Timestamp(
        price_reference_date or as_of_date or freshness_date or date.today()
    ).date()
    market_start = (
        pd.Timestamp(market_reference) - pd.DateOffset(years=5, months=4)
    ).date()
    load_market_series = market_series_loader or load_economic_cycle_market_series
    try:
        market_rows = list(
            load_market_series(start_date=market_start, end_date=market_reference)
        )
    except Exception:
        market_rows = []

    load_asset_prices = asset_price_loader or load_economic_cycle_asset_prices
    try:
        asset_price_rows = list(
            load_asset_prices(lookback_rows=1500, end_date=market_reference)
        )
    except Exception:
        asset_price_rows = []
    asset_freshness = build_asset_pathway_freshness(
        market_rows,
        asset_price_rows,
        reference_date=market_reference,
    )
    required_scopes = []
    if cycle_freshness.get("refresh_required"):
        required_scopes.append("cycle_snapshot")
    if asset_freshness.get("refresh_required"):
        required_scopes.append("asset_pathways")
    scope_statuses = {
        str(cycle_freshness.get("status") or "ERROR"),
        str(asset_freshness.get("status") or "ERROR"),
    }
    overall_status = (
        "ERROR"
        if "ERROR" in scope_statuses
        else "MISSING"
        if "MISSING" in scope_statuses
        else "REFRESH_AVAILABLE"
        if "REFRESH_AVAILABLE" in scope_statuses
        else "READY"
    )
    if required_scopes:
        combined_message = "필요한 경기·자산 자료만 최신 기준으로 확인할 수 있습니다."
    else:
        combined_message = "경기 국면과 자산별 확인 포인트가 최신 상태입니다."
    data_freshness = {
        **cycle_freshness,
        "status": overall_status,
        "overall_status": overall_status,
        "cycle_snapshot": cycle_freshness,
        "asset_pathways": asset_freshness,
        "refresh_required_scopes": required_scopes,
        "refresh_required": bool(required_scopes),
        "message": combined_message,
    }
    if required_scopes:
        data_freshness["action"] = dict(
            cycle_freshness.get("action")
            or {
                "id": "refresh_economic_cycle_data",
                "label": "최신 발표 확인·재계산",
                "enabled": True,
            }
        )
    load_sp500_earnings = sp500_earnings_loader or load_sp500_actual_eps_history
    try:
        sp500_earnings = dict(load_sp500_earnings(end_date=market_reference))
    except Exception:
        sp500_earnings = {
            "status": "UNAVAILABLE",
            "reason_code": "EARNINGS_READ_ERROR",
        }
    market_implications = build_market_implications(
        (),
        evidence,
        asset_price_rows,
        market_rows=market_rows,
        sp500_earnings=sp500_earnings,
        economic_as_of_date=snapshot_date or None,
        price_reference_date=market_reference,
    )
    for item in market_implications:
        item["economic_as_of_date"] = snapshot_date or None
    current_phase = observed_state.get("phase")
    status = str(resolved_snapshot.get("status") or "LIMITED").upper()
    if observed_state.get("data_status") != "READY" or not current_phase:
        status = "LIMITED"
    limitations = [
        "이 결과는 데이터 기반 국면 추정이며 NBER의 공식 경기판정이 아닙니다.",
        "시장 맥락은 조건부 해석이며 수익률 예측이나 매매 지시가 아닙니다.",
    ]
    warnings = _json_value(resolved_snapshot.get("warnings_json"), [])
    limitations.extend(str(item) for item in warnings if item)
    headline_reason = None if current_phase else "OBSERVED_STATE_MISSING"
    headline_summary = PHASE_HEADLINE_SUMMARIES.get(
        str(current_phase),
        "관측 국면을 계산할 실물지표가 충분하지 않습니다.",
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "READY" if status == "READY" else "LIMITED",
        "as_of_date": snapshot_date or None,
        "model_version": str(resolved_snapshot.get("model_version") or "") or None,
        "intramonth_change": intramonth,
        "data_freshness": data_freshness,
        "headline": {
            "phase": current_phase,
            "phase_label": PHASE_LABELS.get(str(current_phase), "판단 제한"),
            "summary": headline_summary,
            "reason_code": headline_reason,
        },
        "observed_state": observed_state,
        "recent_changes": recent_changes,
        "transition_monitor": transition_monitor,
        "transition_forecast": transition_forecast,
        "cycle_map": cycle_map,
        "evidence": evidence,
        "market_implications": market_implications,
        "sources": _sources(resolved_snapshot, evidence),
        "limitations": limitations,
    }
