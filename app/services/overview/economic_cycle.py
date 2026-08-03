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


def _transition_monitor(
    snapshot: Mapping[str, object],
    history_rows: Sequence[Mapping[str, object]] = (),
) -> dict[str, object] | None:
    raw = _json_value(snapshot.get("transition_monitor_json"), {})
    if not isinstance(raw, Mapping) or not raw:
        return None
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
    return output


def _cycle_map(
    history_rows: Sequence[Mapping[str, object]],
    current_snapshot: Mapping[str, object],
) -> dict[str, object]:
    """Build a short actual-coordinate trail; never infer points from probabilities."""

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
    transition_monitor = _transition_monitor(resolved_snapshot, history_rows)
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
    data_freshness = build_economic_cycle_freshness(
        intramonth,
        today=freshness_date,
    )

    market_reference = pd.Timestamp(
        price_reference_date or as_of_date or date.today()
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
        "cycle_map": cycle_map,
        "evidence": evidence,
        "market_implications": market_implications,
        "sources": _sources(resolved_snapshot, evidence),
        "limitations": limitations,
    }
