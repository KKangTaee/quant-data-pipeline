from __future__ import annotations

from datetime import date
from typing import Any

import pandas as pd

from finance.loaders import load_latest_market_date
from finance.performance import portfolio_performance_summary

from .candidate_registry import load_current_candidate_registry_latest
from .portfolio_selection_v2 import (
    FINAL_SELECTION_DECISION_V2_FILE,
    load_final_selection_decisions_v2,
)


SELECTED_PRACTICAL_PORTFOLIO_ROUTE = "SELECT_FOR_PRACTICAL_PORTFOLIO"

FINAL_SELECTED_PORTFOLIO_STATUS_LABELS = {
    "normal": "정상 관찰",
    "watch": "관찰 필요",
    "rebalance_needed": "리밸런싱 확인 필요",
    "re_review_needed": "재검토 필요",
    "blocked": "운영 대상 차단",
}
FINAL_SELECTED_PORTFOLIO_STATUS_ORDER = [
    "normal",
    "watch",
    "rebalance_needed",
    "re_review_needed",
    "blocked",
]
FINAL_SELECTED_PORTFOLIO_DRIFT_ROUTE_LABELS = {
    "DRIFT_ALIGNED": "목표 비중 근처",
    "DRIFT_WATCH": "비중 관찰 필요",
    "REBALANCE_NEEDED": "리밸런싱 검토 필요",
    "DRIFT_INPUT_INCOMPLETE": "현재 비중 입력 확인 필요",
}
FINAL_SELECTED_PORTFOLIO_VALUE_INPUT_MODE_LABELS = {
    "current_value": "현재 보유 평가금액으로 계산",
    "shares_x_price": "보유 수량과 가격으로 계산",
    "current_weight": "이미 계산한 현재 비중 입력",
}
FINAL_SELECTED_PORTFOLIO_DRIFT_ALERT_ROUTE_LABELS = {
    "NO_ALERT": "운영 경고 없음",
    "WATCH_ALERT": "관찰 경고",
    "REBALANCE_REVIEW_ALERT": "리밸런싱 검토 경고",
    "INPUT_REVIEW_ALERT": "입력 확인 경고",
}
SELECTED_MONITORING_TIMELINE_SCHEMA_VERSION = "selected_monitoring_timeline_v1"
SELECTED_CONTINUITY_CHECK_SCHEMA_VERSION = "selected_continuity_check_v1"
SELECTED_RECHECK_COMPARISON_SCHEMA_VERSION = "selected_recheck_comparison_v1"
SELECTED_MONITORING_TIMELINE_STATUS_LABELS = {
    "CLEAR": "정상",
    "WATCH": "관찰",
    "BREACHED": "재검토",
    "NEEDS_INPUT": "입력 필요",
    "OPTIONAL": "선택",
}
SELECTED_CONTINUITY_ROUTE_LABELS = {
    "CONTINUITY_READY": "사후 점검 준비 완료",
    "CONTINUITY_NEEDS_INPUT": "입력 필요",
    "CONTINUITY_REVIEW": "연결 검토 필요",
    "CONTINUITY_BLOCKED": "연결 차단",
}
SELECTED_RECHECK_COMPARISON_ROUTE_LABELS = {
    "RECHECK_COMPARISON_NOT_RUN": "재검증 필요",
    "RECHECK_COMPARISON_READY": "선정 thesis 유지",
    "RECHECK_COMPARISON_WATCH": "관찰 필요",
    "RECHECK_COMPARISON_BREACHED": "재검토 필요",
    "RECHECK_COMPARISON_ERROR": "재검증 오류",
}
_TIMELINE_STATUS_RANK = {
    "OPTIONAL": 0,
    "CLEAR": 1,
    "WATCH": 2,
    "NEEDS_INPUT": 3,
    "BREACHED": 4,
}


def _optional_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    if pd.isna(numeric):
        return None
    return numeric


def _clean_text(value: Any, default: str = "-") -> str:
    text = str(value or "").strip()
    return text or default


def _is_selected_practical_portfolio(row: dict[str, Any]) -> bool:
    return (
        row.get("selected_practical_portfolio") is True
        or str(row.get("decision_route") or "").strip() == SELECTED_PRACTICAL_PORTFOLIO_ROUTE
    )


def _active_components(row: dict[str, Any]) -> list[dict[str, Any]]:
    active: list[dict[str, Any]] = []
    for component in list(row.get("selected_components") or []):
        component_row = dict(component or {})
        weight = _optional_float(component_row.get("target_weight")) or 0.0
        if weight > 0.0:
            active.append(component_row)
    return active


def _component_identity(component: dict[str, Any], index: int) -> str:
    registry_id = _clean_text(component.get("registry_id"), "")
    if registry_id:
        return registry_id
    title = _clean_text(component.get("title"), "")
    if title:
        return title
    return f"component_{index + 1}"


def _format_date_value(value: Any) -> str | None:
    if value is None:
        return None
    if hasattr(value, "date"):
        return str(value.date())
    text = str(value).strip()
    return text or None


def _date_text(value: Any) -> str | None:
    formatted = _format_date_value(value)
    if not formatted:
        return None
    parsed = pd.to_datetime(formatted, errors="coerce")
    if pd.isna(parsed):
        return formatted
    return parsed.strftime("%Y-%m-%d")


def _baseline_component_rows(row: dict[str, Any]) -> list[dict[str, Any]]:
    raw_decision = dict(row.get("raw_decision") or row)
    risk_snapshot = dict(raw_decision.get("risk_and_validation_snapshot") or {})
    robustness = dict(risk_snapshot.get("robustness_validation") or {})
    return [dict(item or {}) for item in list(robustness.get("component_rows") or [])]


def _baseline_snapshot(row: dict[str, Any]) -> dict[str, Any]:
    raw_decision = dict(row.get("raw_decision") or row)
    paper_snapshot = dict(raw_decision.get("paper_tracking_snapshot") or {})
    baseline = dict(paper_snapshot.get("baseline_snapshot") or {})
    component_rows = _baseline_component_rows(raw_decision)
    starts = [_date_text(item.get("Start")) for item in component_rows if _date_text(item.get("Start"))]
    ends = [_date_text(item.get("End")) for item in component_rows if _date_text(item.get("End"))]
    active_components = _active_components(raw_decision)
    if not starts:
        starts = [
            _date_text(component.get("period_start") or component.get("start"))
            for component in active_components
            if _date_text(component.get("period_start") or component.get("start"))
        ]
    if not ends:
        ends = [
            _date_text(component.get("period_end") or component.get("end"))
            for component in active_components
            if _date_text(component.get("period_end") or component.get("end"))
        ]
    baseline_cagr = _optional_float(baseline.get("weighted_cagr"))
    baseline_mdd = _optional_float(baseline.get("weighted_mdd"))
    if baseline_cagr is None and component_rows:
        cagr_values = [_optional_float(item.get("CAGR")) for item in component_rows]
        cagr_values = [value for value in cagr_values if value is not None]
        baseline_cagr = sum(cagr_values) / len(cagr_values) if cagr_values else None
    if baseline_mdd is None and component_rows:
        mdd_values = [_optional_float(item.get("MDD")) for item in component_rows]
        mdd_values = [value for value in mdd_values if value is not None]
        baseline_mdd = min(mdd_values) if mdd_values else None
    return {
        "baseline_start": min(starts) if starts else None,
        "baseline_end": max(ends) if ends else None,
        "baseline_cagr": baseline_cagr,
        "baseline_mdd": baseline_mdd,
        "component_rows": component_rows,
    }


def _target_weight_total(row: dict[str, Any], active_components: list[dict[str, Any]]) -> float:
    paper_snapshot = dict(row.get("paper_tracking_snapshot") or {})
    baseline = dict(paper_snapshot.get("baseline_snapshot") or {})
    baseline_total = _optional_float(baseline.get("target_weight_total"))
    if baseline_total is not None:
        return round(baseline_total, 4)
    return round(
        sum((_optional_float(component.get("target_weight")) or 0.0) for component in active_components),
        4,
    )


def _component_benchmarks(active_components: list[dict[str, Any]]) -> list[str]:
    benchmarks = {
        _clean_text(component.get("benchmark"), "")
        for component in active_components
        if _clean_text(component.get("benchmark"), "")
    }
    return sorted(benchmarks)


def _evidence_blockers(row: dict[str, Any]) -> list[str]:
    evidence = dict(row.get("decision_evidence_snapshot") or {})
    blockers = [str(blocker) for blocker in list(evidence.get("blockers") or []) if str(blocker)]
    paper_snapshot = dict(row.get("paper_tracking_snapshot") or {})
    blockers.extend(str(blocker) for blocker in list(paper_snapshot.get("blockers") or []) if str(blocker))
    return blockers


def _derive_operation_status(
    row: dict[str, Any],
    *,
    active_components: list[dict[str, Any]],
    target_weight_total: float,
    blockers: list[str],
) -> tuple[str, str]:
    if not _is_selected_practical_portfolio(row):
        return "blocked", "Final Review에서 실전 후보로 선정된 row가 아닙니다."
    if not active_components:
        return "blocked", "선정된 component가 없어 운영 대상으로 볼 수 없습니다."
    if abs(target_weight_total - 100.0) > 0.01:
        return "blocked", f"목표 비중 합계가 100%가 아닙니다. current={target_weight_total:.2f}%"
    if blockers:
        return "re_review_needed", "Final Review evidence 또는 paper observation blocker가 남아 있습니다."

    evidence = dict(row.get("decision_evidence_snapshot") or {})
    risk_snapshot = dict(row.get("risk_and_validation_snapshot") or {})
    robustness = dict(risk_snapshot.get("robustness_validation") or {})
    paper_snapshot = dict(row.get("paper_tracking_snapshot") or {})
    evidence_route = str(evidence.get("route") or "").strip()
    validation_route = str(risk_snapshot.get("validation_route") or "").strip()
    robustness_route = str(robustness.get("robustness_route") or "").strip()
    paper_route = str(paper_snapshot.get("route") or "").strip()
    watch_routes = []
    if evidence_route and evidence_route != "READY_FOR_FINAL_DECISION":
        watch_routes.append(f"evidence={evidence_route}")
    if validation_route and validation_route not in {"READY_FOR_ROBUSTNESS_REVIEW", "READY_FOR_FINAL_REVIEW"}:
        watch_routes.append(f"validation={validation_route}")
    if robustness_route and robustness_route != "READY_FOR_STRESS_SWEEP":
        watch_routes.append(f"robustness={robustness_route}")
    if paper_route and paper_route != "PAPER_OBSERVATION_READY":
        watch_routes.append(f"paper={paper_route}")
    if watch_routes:
        return "watch", " / ".join(watch_routes)
    return "normal", "최종 선정 기록, component, 목표 비중, evidence blocker 기준이 운영 대시보드 첫 범위를 통과했습니다."


def build_final_selected_portfolio_dashboard_row(row: dict[str, Any]) -> dict[str, Any]:
    """Convert one Final Review selected decision into the Phase36 dashboard read model."""
    active_components = _active_components(row)
    target_weight_total = _target_weight_total(row, active_components)
    blockers = _evidence_blockers(row)
    operation_status, status_reason = _derive_operation_status(
        row,
        active_components=active_components,
        target_weight_total=target_weight_total,
        blockers=blockers,
    )
    evidence = dict(row.get("decision_evidence_snapshot") or {})
    risk_snapshot = dict(row.get("risk_and_validation_snapshot") or {})
    robustness = dict(risk_snapshot.get("robustness_validation") or {})
    paper_snapshot = dict(row.get("paper_tracking_snapshot") or {})
    operator_decision = dict(row.get("operator_decision") or {})
    benchmarks = _component_benchmarks(active_components)
    baseline = _baseline_snapshot(row)
    return {
        "decision_id": _clean_text(row.get("decision_id")),
        "updated_at": _clean_text(row.get("updated_at") or row.get("created_at")),
        "decision_route": _clean_text(row.get("decision_route")),
        "source_type": _clean_text(row.get("source_type")),
        "source_id": _clean_text(row.get("source_id")),
        "source_title": _clean_text(row.get("source_title") or row.get("source_id")),
        "operation_status": operation_status,
        "operation_status_label": FINAL_SELECTED_PORTFOLIO_STATUS_LABELS.get(operation_status, operation_status),
        "status_reason": status_reason,
        "component_count": len(active_components),
        "target_weight_total": target_weight_total,
        "benchmarks": benchmarks,
        "benchmark_label": ", ".join(benchmarks) if benchmarks else "-",
        "evidence_route": _clean_text(evidence.get("route")),
        "evidence_score": _optional_float(evidence.get("score")),
        "validation_route": _clean_text(risk_snapshot.get("validation_route")),
        "validation_score": _optional_float(risk_snapshot.get("validation_score")),
        "robustness_route": _clean_text(robustness.get("robustness_route")),
        "robustness_score": _optional_float(robustness.get("robustness_score")),
        "paper_observation_route": _clean_text(paper_snapshot.get("route")),
        "review_cadence": _clean_text(paper_snapshot.get("review_cadence")),
        "review_triggers": list(paper_snapshot.get("review_triggers") or []),
        "blockers": blockers,
        "baseline_start": baseline.get("baseline_start"),
        "baseline_end": baseline.get("baseline_end"),
        "baseline_cagr": baseline.get("baseline_cagr"),
        "baseline_mdd": baseline.get("baseline_mdd"),
        "operator_reason": _clean_text(operator_decision.get("reason")),
        "operator_constraints": _clean_text(operator_decision.get("constraints")),
        "operator_next_action": _clean_text(operator_decision.get("next_action")),
        "live_approval": bool(row.get("live_approval")),
        "order_instruction": bool(row.get("order_instruction")),
        "raw_decision": dict(row),
    }


def build_selected_portfolio_drift_check(
    row: dict[str, Any],
    *,
    current_weights: dict[str, Any],
    drift_threshold_pct: float = 5.0,
    watch_threshold_pct: float = 2.0,
    total_weight_tolerance_pct: float = 1.0,
) -> dict[str, Any]:
    """Compare target weights against operator-provided current weights without creating orders."""
    raw_decision = dict(row.get("raw_decision") or row)
    active_components = _active_components(raw_decision)
    target_weight_total = _target_weight_total(raw_decision, active_components)
    rows: list[dict[str, Any]] = []
    current_weight_total = 0.0
    missing_inputs: list[str] = []
    rebalancing_components: list[str] = []
    watch_components: list[str] = []
    max_abs_drift = 0.0

    for index, component in enumerate(active_components):
        identity = _component_identity(component, index)
        title = _clean_text(component.get("title") or identity)
        target_weight = _optional_float(component.get("target_weight")) or 0.0
        current_weight = _optional_float(current_weights.get(identity))
        if current_weight is None:
            missing_inputs.append(identity)
            current_weight = 0.0
        drift = current_weight - target_weight
        abs_drift = abs(drift)
        max_abs_drift = max(max_abs_drift, abs_drift)
        current_weight_total += current_weight
        if abs_drift >= drift_threshold_pct:
            rebalancing_components.append(identity)
        elif abs_drift >= watch_threshold_pct:
            watch_components.append(identity)
        rows.append(
            {
                "component_id": identity,
                "title": title,
                "target_weight": round(target_weight, 4),
                "current_weight": round(current_weight, 4),
                "drift": round(drift, 4),
                "abs_drift": round(abs_drift, 4),
                "drift_direction": "overweight" if drift > 0 else "underweight" if drift < 0 else "aligned",
                "threshold_breached": abs_drift >= drift_threshold_pct,
                "watch_breached": abs_drift >= watch_threshold_pct,
            }
        )

    total_weight_gap = current_weight_total - target_weight_total
    blockers: list[str] = []
    if not active_components:
        blockers.append("active component 없음")
    if missing_inputs:
        blockers.append("현재 비중 입력 누락")
    if abs(current_weight_total - 100.0) > total_weight_tolerance_pct:
        blockers.append("현재 비중 합계가 100% 근처가 아님")

    if blockers:
        route = "DRIFT_INPUT_INCOMPLETE"
        verdict = "현재 비중 입력을 먼저 확인해야 합니다."
        next_action = "component별 현재 비중을 입력하고 합계가 100% 근처인지 확인합니다."
    elif rebalancing_components:
        route = "REBALANCE_NEEDED"
        verdict = "목표 비중 대비 drift가 커서 리밸런싱 검토가 필요합니다."
        next_action = "주문 지시가 아니라, drift가 큰 component를 검토 목록에 올립니다."
    elif watch_components:
        route = "DRIFT_WATCH"
        verdict = "목표 비중에서 일부 벗어났지만 즉시 리밸런싱 판단 전 관찰이 필요합니다."
        next_action = "다음 점검일에 drift가 커지는지 확인합니다."
    else:
        route = "DRIFT_ALIGNED"
        verdict = "현재 비중이 목표 비중 근처에 있습니다."
        next_action = "정기 점검 주기에 따라 계속 관찰합니다."

    return {
        "route": route,
        "route_label": FINAL_SELECTED_PORTFOLIO_DRIFT_ROUTE_LABELS.get(route, route),
        "verdict": verdict,
        "next_action": next_action,
        "rows": rows,
        "blockers": blockers,
        "rebalancing_components": rebalancing_components,
        "watch_components": watch_components,
        "metrics": {
            "target_weight_total": round(target_weight_total, 4),
            "current_weight_total": round(current_weight_total, 4),
            "total_weight_gap": round(total_weight_gap, 4),
            "max_abs_drift": round(max_abs_drift, 4),
            "drift_threshold_pct": round(float(drift_threshold_pct), 4),
            "watch_threshold_pct": round(float(watch_threshold_pct), 4),
            "total_weight_tolerance_pct": round(float(total_weight_tolerance_pct), 4),
            "active_components": len(active_components),
        },
        "execution_boundary": {
            "live_approval": False,
            "order_instruction": False,
            "auto_rebalance": False,
            "notes": "This drift check is read-only and does not create broker orders.",
        },
    }


def build_selected_portfolio_current_weight_inputs(
    row: dict[str, Any],
    *,
    component_inputs: dict[str, Any],
    cash_value: Any = 0.0,
    input_mode: str = "current_value",
) -> dict[str, Any]:
    """Convert value or holding inputs into component current weights for drift checks."""
    raw_decision = dict(row.get("raw_decision") or row)
    active_components = _active_components(raw_decision)
    rows: list[dict[str, Any]] = []
    current_weights: dict[str, float] = {}
    missing_inputs: list[str] = []
    invalid_inputs: list[str] = []
    component_value_total = 0.0
    normalized_mode = str(input_mode or "current_value").strip() or "current_value"

    component_value_rows: list[tuple[int, dict[str, Any], str, str, float, dict[str, Any]]] = []
    for index, component in enumerate(active_components):
        identity = _component_identity(component, index)
        title = _clean_text(component.get("title") or identity)
        target_weight = _optional_float(component.get("target_weight")) or 0.0
        input_row = dict((component_inputs or {}).get(identity) or {})
        current_value = _optional_float(input_row.get("current_value"))
        shares = _optional_float(input_row.get("shares"))
        price = _optional_float(input_row.get("price"))
        if current_value is None and shares is not None and price is not None:
            current_value = shares * price

        if current_value is None:
            missing_inputs.append(identity)
            current_value = 0.0
        elif current_value < 0.0:
            invalid_inputs.append(identity)
            current_value = 0.0

        component_value_total += current_value
        component_value_rows.append((index, component, identity, title, target_weight, input_row | {"current_value": current_value}))

    normalized_cash_value = _optional_float(cash_value)
    if normalized_cash_value is None:
        normalized_cash_value = 0.0
    elif normalized_cash_value < 0.0:
        invalid_inputs.append("cash_value")
        normalized_cash_value = 0.0

    portfolio_value_total = component_value_total + normalized_cash_value
    for _index, component, identity, title, target_weight, input_row in component_value_rows:
        current_value = _optional_float(input_row.get("current_value")) or 0.0
        current_weight = (current_value / portfolio_value_total * 100.0) if portfolio_value_total > 0.0 else 0.0
        current_weights[identity] = current_weight
        rows.append(
            {
                "component_id": identity,
                "title": title,
                "target_weight": round(target_weight, 4),
                "symbol": _clean_text(input_row.get("symbol"), ""),
                "shares": _optional_float(input_row.get("shares")),
                "price": _optional_float(input_row.get("price")),
                "price_date": _format_date_value(input_row.get("price_date")),
                "price_source": _clean_text(input_row.get("price_source"), ""),
                "current_value": round(current_value, 4),
                "current_weight": round(current_weight, 4),
                "input_mode": normalized_mode,
                "input_mode_label": FINAL_SELECTED_PORTFOLIO_VALUE_INPUT_MODE_LABELS.get(normalized_mode, normalized_mode),
                "input_complete": identity not in missing_inputs and identity not in invalid_inputs,
            }
        )

    blockers: list[str] = []
    if not active_components:
        blockers.append("active component 없음")
    if missing_inputs:
        blockers.append("현재 평가금액 입력 누락")
    if invalid_inputs:
        blockers.append("현재 평가금액 또는 현금 입력값이 음수")
    if portfolio_value_total <= 0.0:
        blockers.append("현재 평가금액 합계가 0보다 커야 함")

    return {
        "input_mode": normalized_mode,
        "input_mode_label": FINAL_SELECTED_PORTFOLIO_VALUE_INPUT_MODE_LABELS.get(normalized_mode, normalized_mode),
        "current_weights": current_weights,
        "rows": rows,
        "blockers": blockers,
        "missing_inputs": missing_inputs,
        "invalid_inputs": invalid_inputs,
        "metrics": {
            "component_value_total": round(component_value_total, 4),
            "cash_value": round(normalized_cash_value, 4),
            "portfolio_value_total": round(portfolio_value_total, 4),
            "current_weight_total": round(sum(current_weights.values()), 4),
            "active_components": len(active_components),
        },
        "execution_boundary": {
            "live_approval": False,
            "order_instruction": False,
            "auto_rebalance": False,
            "notes": "Value and holding inputs only estimate current weights; they do not create broker orders.",
        },
    }


def build_selected_portfolio_drift_alert_preview(
    row: dict[str, Any],
    *,
    drift_check: dict[str, Any],
) -> dict[str, Any]:
    """Translate a drift check into read-only alert and review-trigger guidance."""
    raw_decision = dict(row.get("raw_decision") or row)
    paper_snapshot = dict(raw_decision.get("paper_tracking_snapshot") or {})
    review_triggers = [
        str(trigger).strip()
        for trigger in list(row.get("review_triggers") or paper_snapshot.get("review_triggers") or [])
        if str(trigger).strip()
    ]
    drift_route = str(drift_check.get("route") or "").strip()
    drift_rows = [dict(item or {}) for item in list(drift_check.get("rows") or [])]
    drift_row_by_id = {str(item.get("component_id") or ""): item for item in drift_rows}
    rebalancing_components = [str(item) for item in list(drift_check.get("rebalancing_components") or [])]
    watch_components = [str(item) for item in list(drift_check.get("watch_components") or [])]
    blockers = [str(item) for item in list(drift_check.get("blockers") or []) if str(item)]
    metrics = dict(drift_check.get("metrics") or {})
    alert_rows: list[dict[str, Any]] = []

    if drift_route == "DRIFT_INPUT_INCOMPLETE":
        alert_route = "INPUT_REVIEW_ALERT"
        alert_level = "input_review"
        verdict = "drift 판단 전에 입력값을 먼저 확인해야 합니다."
        next_action = "현재 비중 / 평가금액 / 보유 수량 입력을 보강한 뒤 다시 확인합니다."
        for blocker in blockers:
            alert_rows.append(
                {
                    "area": "Input Review",
                    "trigger": blocker,
                    "status": "CHECK_INPUT",
                    "current": f"current_weight_total={metrics.get('current_weight_total', '-')}",
                    "next_action": next_action,
                }
            )
    elif drift_route == "REBALANCE_NEEDED":
        alert_route = "REBALANCE_REVIEW_ALERT"
        alert_level = "high"
        verdict = "목표 비중 대비 drift가 리밸런싱 검토 기준을 넘었습니다."
        next_action = "주문 생성이 아니라, drift가 큰 component를 운영 검토 목록에 올립니다."
        for component_id in rebalancing_components:
            component_row = dict(drift_row_by_id.get(component_id) or {})
            alert_rows.append(
                {
                    "area": "Rebalance Review",
                    "trigger": component_row.get("title") or component_id,
                    "status": "THRESHOLD_BREACHED",
                    "current": f"drift={component_row.get('drift', '-')}, abs={component_row.get('abs_drift', '-')}",
                    "next_action": "리밸런싱 필요 여부와 해당 component의 최신 근거를 확인합니다.",
                }
            )
    elif drift_route == "DRIFT_WATCH":
        alert_route = "WATCH_ALERT"
        alert_level = "medium"
        verdict = "목표 비중에서 벗어나기 시작했으므로 다음 관찰 주기에 확인합니다."
        next_action = "watch component의 drift가 확대되는지 review cadence에 맞춰 다시 봅니다."
        for component_id in watch_components:
            component_row = dict(drift_row_by_id.get(component_id) or {})
            alert_rows.append(
                {
                    "area": "Watch Review",
                    "trigger": component_row.get("title") or component_id,
                    "status": "WATCH_BREACHED",
                    "current": f"drift={component_row.get('drift', '-')}, abs={component_row.get('abs_drift', '-')}",
                    "next_action": "다음 점검일에 drift 확대 여부를 확인합니다.",
                }
            )
    else:
        alert_route = "NO_ALERT"
        alert_level = "none"
        verdict = "현재 drift 기준으로 별도 운영 경고는 없습니다."
        next_action = "Final Review에 남긴 review cadence와 trigger에 따라 정기 점검합니다."

    for trigger in review_triggers:
        alert_rows.append(
            {
                "area": "Final Review Trigger",
                "trigger": trigger,
                "status": "REFERENCE_TRIGGER" if alert_route == "NO_ALERT" else "CHECK_WITH_ALERT",
                "current": drift_check.get("route_label") or drift_route or "-",
                "next_action": "drift 경고와 함께 이 trigger가 재검토 조건에 해당하는지 확인합니다."
                if alert_route != "NO_ALERT"
                else "정기 점검 시 이 trigger 기준을 다시 확인합니다.",
            }
        )

    return {
        "alert_route": alert_route,
        "alert_route_label": FINAL_SELECTED_PORTFOLIO_DRIFT_ALERT_ROUTE_LABELS.get(alert_route, alert_route),
        "alert_level": alert_level,
        "verdict": verdict,
        "next_action": next_action,
        "rows": alert_rows,
        "review_triggers": review_triggers,
        "metrics": {
            "review_trigger_count": len(review_triggers),
            "alert_row_count": len(alert_rows),
            "drift_route": drift_route,
            "max_abs_drift": metrics.get("max_abs_drift"),
            "current_weight_total": metrics.get("current_weight_total"),
        },
        "execution_boundary": {
            "live_approval": False,
            "order_instruction": False,
            "alert_persistence": False,
            "notes": "This preview is read-only and does not save alert records or create orders.",
        },
    }


def _timeline_status_label(status: str) -> str:
    return SELECTED_MONITORING_TIMELINE_STATUS_LABELS.get(status, status)


def _timeline_overall_status(rows: list[dict[str, Any]]) -> str:
    statuses = [str(row.get("status") or "OPTIONAL") for row in rows]
    if not statuses:
        return "NEEDS_INPUT"
    return max(statuses, key=lambda status: _TIMELINE_STATUS_RANK.get(status, 0))


def _timeline_row(
    *,
    order: int,
    event: str,
    status: str,
    signal: str,
    evidence: str,
    next_action: str,
    source: str,
    timestamp: Any = None,
) -> dict[str, Any]:
    return {
        "order": order,
        "event": event,
        "timestamp": _clean_text(_format_date_value(timestamp), "-"),
        "status": status,
        "status_label": _timeline_status_label(status),
        "signal": _clean_text(signal),
        "evidence": _clean_text(evidence),
        "next_action": _clean_text(next_action),
        "source": _clean_text(source),
    }


def _status_from_operation_status(operation_status: str) -> str:
    if operation_status == "normal":
        return "CLEAR"
    if operation_status in {"watch", "rebalance_needed"}:
        return "WATCH"
    if operation_status in {"re_review_needed", "blocked"}:
        return "BREACHED"
    return "WATCH"


def _status_from_recheck_result(recheck_result: dict[str, Any]) -> tuple[str, str, str, str]:
    if not recheck_result:
        return (
            "NEEDS_INPUT",
            "Performance Recheck not run",
            "최신 기간 재검증 결과가 아직 없습니다.",
            "Performance Recheck를 실행해 선정 thesis가 유지되는지 확인합니다.",
        )
    if recheck_result.get("status") == "error":
        error_text = _clean_text(recheck_result.get("error"), "Performance Recheck failed")
        return (
            "NEEDS_INPUT",
            error_text,
            "성과 유지 여부를 판단하려면 recheck 결과가 필요합니다.",
            "입력 기간과 selected component contract를 확인한 뒤 다시 실행합니다.",
        )
    route = str(recheck_result.get("verdict_route") or "").strip()
    if route == "SELECTION_THESIS_HOLDS":
        status = "CLEAR"
    elif route in {"PERFORMANCE_WEAKENED", "RISK_DRAWDOWN_EXPANDED"}:
        status = "BREACHED"
    elif route == "PARTIAL_RECHECK":
        status = "WATCH"
    else:
        status = "WATCH"
    change = dict(recheck_result.get("change_summary") or {})
    period = dict(recheck_result.get("period") or {})
    signal = (
        f"{route or '-'} / CAGR delta={change.get('cagr_delta_vs_baseline', '-')} / "
        f"MDD delta={change.get('mdd_delta_vs_baseline', '-')}"
    )
    evidence = f"{period.get('start') or '-'} -> {period.get('end') or '-'}"
    return (
        status,
        signal,
        evidence,
        _clean_text(recheck_result.get("verdict"), "Performance Recheck 결과를 Review Signals에서 확인합니다."),
    )


def _status_from_drift_check(drift_check: dict[str, Any]) -> tuple[str, str, str, str]:
    if not drift_check:
        return (
            "OPTIONAL",
            "Actual Allocation not checked",
            "실제 또는 가상 보유금액 입력은 선택 점검입니다.",
            "보유금액 배분까지 관리할 때 Actual Allocation tab에서 입력합니다.",
        )
    route = str(drift_check.get("route") or "").strip()
    if route == "DRIFT_ALIGNED":
        status = "CLEAR"
    elif route == "DRIFT_WATCH":
        status = "WATCH"
    elif route == "REBALANCE_NEEDED":
        status = "BREACHED"
    else:
        status = "NEEDS_INPUT"
    metrics = dict(drift_check.get("metrics") or {})
    signal = (
        f"{drift_check.get('route_label') or route or '-'} / "
        f"max drift={metrics.get('max_abs_drift', '-')} / "
        f"current total={metrics.get('current_weight_total', '-')}"
    )
    return (
        status,
        signal,
        _clean_text(drift_check.get("verdict")),
        _clean_text(drift_check.get("next_action")),
    )


def _status_from_alert_preview(alert_preview: dict[str, Any]) -> tuple[str, str, str, str]:
    if not alert_preview:
        return (
            "OPTIONAL",
            "Alert preview not applied",
            "drift alert preview는 session state에 반영될 때 timeline에 표시됩니다.",
            "Actual Allocation에서 Update Review Signals를 누르면 preview를 반영합니다.",
        )
    route = str(alert_preview.get("alert_route") or "").strip()
    if route == "NO_ALERT":
        status = "CLEAR"
    elif route == "WATCH_ALERT":
        status = "WATCH"
    elif route == "REBALANCE_REVIEW_ALERT":
        status = "BREACHED"
    else:
        status = "NEEDS_INPUT"
    metrics = dict(alert_preview.get("metrics") or {})
    signal = (
        f"{alert_preview.get('alert_route_label') or route or '-'} / "
        f"rows={metrics.get('alert_row_count', 0)} / "
        f"triggers={metrics.get('review_trigger_count', 0)}"
    )
    return (
        status,
        signal,
        _clean_text(alert_preview.get("verdict")),
        _clean_text(alert_preview.get("next_action")),
    )


def build_selected_portfolio_monitoring_timeline(
    row: dict[str, Any],
    *,
    recheck_result: dict[str, Any] | None = None,
    drift_check: dict[str, Any] | None = None,
    alert_preview: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a read-only monitoring timeline for a selected portfolio dashboard row."""

    selected = dict(row or {})
    raw_decision = dict(selected.get("raw_decision") or selected)
    recheck = dict(recheck_result or {})
    drift = dict(drift_check or {})
    alert = dict(alert_preview or {})
    operation_status = str(selected.get("operation_status") or "").strip()
    operation_label = _clean_text(selected.get("operation_status_label") or operation_status)
    rows: list[dict[str, Any]] = [
        _timeline_row(
            order=1,
            event="Final Review selection",
            timestamp=selected.get("updated_at") or raw_decision.get("updated_at") or raw_decision.get("created_at"),
            status=_status_from_operation_status(operation_status),
            signal=operation_label,
            evidence=_clean_text(selected.get("status_reason")),
            next_action=(
                "선정 row를 운영 대상으로 계속 읽습니다."
                if operation_status == "normal"
                else "Why Selected에서 남은 blocker와 watch 이유를 먼저 확인합니다."
            ),
            source="FINAL_PORTFOLIO_SELECTION_DECISIONS_V2",
        )
    ]

    evidence_route = _clean_text(selected.get("evidence_route"))
    validation_route = _clean_text(selected.get("validation_route"))
    robustness_route = _clean_text(selected.get("robustness_route"))
    paper_route = _clean_text(selected.get("paper_observation_route"))
    blockers = [str(blocker) for blocker in list(selected.get("blockers") or []) if str(blocker)]
    evidence_clear = (
        not blockers
        and evidence_route == "READY_FOR_FINAL_DECISION"
        and validation_route in {"READY_FOR_FINAL_REVIEW", "READY_FOR_ROBUSTNESS_REVIEW", "-"}
        and robustness_route in {"READY_FOR_STRESS_SWEEP", "-"}
        and paper_route in {"PAPER_OBSERVATION_READY", "-"}
    )
    rows.append(
        _timeline_row(
            order=2,
            event="Evidence gate snapshot",
            timestamp=selected.get("updated_at") or raw_decision.get("updated_at") or raw_decision.get("created_at"),
            status="CLEAR" if evidence_clear else "WATCH",
            signal=f"evidence={evidence_route} / validation={validation_route} / robustness={robustness_route} / paper={paper_route}",
            evidence="blockers 없음" if not blockers else ", ".join(blockers[:3]),
            next_action=(
                "정기 점검으로 넘어갑니다."
                if evidence_clear
                else "Final Review evidence와 gate policy blocker를 다시 확인합니다."
            ),
            source="Final Review evidence packet",
        )
    )

    recheck_status, recheck_signal, recheck_evidence, recheck_action = _status_from_recheck_result(recheck)
    recheck_period = dict(recheck.get("period") or {})
    rows.append(
        _timeline_row(
            order=3,
            event="Performance Recheck",
            timestamp=recheck_period.get("end"),
            status=recheck_status,
            signal=recheck_signal,
            evidence=recheck_evidence,
            next_action=recheck_action,
            source="session_state.performance_recheck",
        )
    )

    drift_status, drift_signal, drift_evidence, drift_action = _status_from_drift_check(drift)
    rows.append(
        _timeline_row(
            order=4,
            event="Actual Allocation drift",
            timestamp=None,
            status=drift_status,
            signal=drift_signal,
            evidence=drift_evidence,
            next_action=drift_action,
            source="session_state.drift_check",
        )
    )

    alert_status, alert_signal, alert_evidence, alert_action = _status_from_alert_preview(alert)
    rows.append(
        _timeline_row(
            order=5,
            event="Review trigger preview",
            timestamp=None,
            status=alert_status,
            signal=alert_signal,
            evidence=alert_evidence,
            next_action=alert_action,
            source="session_state.alert_preview",
        )
    )

    timeline_status = _timeline_overall_status(rows)
    if timeline_status == "BREACHED":
        conclusion = "재검토가 필요한 monitoring event가 있습니다. BREACHED row의 next action부터 확인합니다."
    elif timeline_status == "NEEDS_INPUT":
        conclusion = "timeline을 완성하려면 Performance Recheck 또는 입력값 확인이 필요합니다."
    elif timeline_status == "WATCH":
        conclusion = "차단은 아니지만 watch event가 있습니다. 다음 점검에서 같은 항목이 악화되는지 봅니다."
    else:
        conclusion = "현재 timeline 기준으로 selected thesis와 운영 점검 상태가 유지됩니다."

    return {
        "schema_version": SELECTED_MONITORING_TIMELINE_SCHEMA_VERSION,
        "timeline_status": timeline_status,
        "timeline_label": _timeline_status_label(timeline_status),
        "conclusion": conclusion,
        "rows": rows,
        "metrics": {
            "row_count": len(rows),
            "breached_count": sum(1 for item in rows if item.get("status") == "BREACHED"),
            "watch_count": sum(1 for item in rows if item.get("status") == "WATCH"),
            "needs_input_count": sum(1 for item in rows if item.get("status") == "NEEDS_INPUT"),
            "optional_count": sum(1 for item in rows if item.get("status") == "OPTIONAL"),
            "performance_recheck_present": bool(recheck),
            "drift_check_present": bool(drift),
            "alert_preview_present": bool(alert),
        },
        "execution_boundary": {
            "write_policy": "read_only_timeline",
            "monitoring_log_auto_write": False,
            "live_approval": False,
            "order_instruction": False,
            "auto_rebalance": False,
            "notes": "Timeline reads current decision and session results; it does not append monitoring logs.",
        },
    }


def _continuity_check_row(
    *,
    check: str,
    status: str,
    ready: bool,
    current: Any,
    evidence: str,
    next_action: str,
    severity: str = "review",
) -> dict[str, Any]:
    return {
        "Check": check,
        "Status": status,
        "Ready": bool(ready),
        "Current": _clean_text(current),
        "Evidence": _clean_text(evidence),
        "Next Action": _clean_text(next_action),
        "Severity": severity,
    }


def build_selected_portfolio_continuity_check(
    row: dict[str, Any],
    *,
    monitoring_timeline: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Check whether a Final Review selected row is usable for dashboard monitoring."""

    selected = dict(row or {})
    raw_decision = dict(selected.get("raw_decision") or selected)
    timeline = dict(monitoring_timeline or build_selected_portfolio_monitoring_timeline(selected))
    evidence = dict(raw_decision.get("decision_evidence_snapshot") or {})
    packet = dict(raw_decision.get("investability_evidence_packet") or {})
    gate_policy = dict(raw_decision.get("gate_policy_snapshot") or packet.get("gate_policy_snapshot") or {})
    paper_snapshot = dict(raw_decision.get("paper_tracking_snapshot") or {})
    active_components = _active_components(raw_decision)
    target_weight_total = _target_weight_total(raw_decision, active_components)
    decision_route = _clean_text(raw_decision.get("decision_route") or selected.get("decision_route"), "")
    selected_flag = (
        raw_decision.get("selected_practical_portfolio") is True
        or selected.get("selected_practical_portfolio") is True
        or decision_route == SELECTED_PRACTICAL_PORTFOLIO_ROUTE
    )
    review_triggers = [
        str(trigger).strip()
        for trigger in list(selected.get("review_triggers") or paper_snapshot.get("review_triggers") or [])
        if str(trigger).strip()
    ]
    timeline_boundary = dict(timeline.get("execution_boundary") or {})
    timeline_metrics = dict(timeline.get("metrics") or {})
    packet_route = _clean_text(packet.get("route"), "")
    evidence_route = _clean_text(evidence.get("route") or selected.get("evidence_route"), "")
    gate_outcome = _clean_text(gate_policy.get("outcome"), "")
    gate_selected = bool(gate_policy.get("select_allowed")) if gate_policy else False
    timeline_read_only = (
        timeline.get("schema_version") == SELECTED_MONITORING_TIMELINE_SCHEMA_VERSION
        and timeline_boundary.get("write_policy") == "read_only_timeline"
        and timeline_boundary.get("monitoring_log_auto_write") is False
    )
    recheck_present = bool(timeline_metrics.get("performance_recheck_present"))

    checks = [
        _continuity_check_row(
            check="Selected Final Review row",
            status="PASS" if selected_flag else "BLOCKED",
            ready=selected_flag,
            current=decision_route or "-",
            evidence="Final Review selected route attached" if selected_flag else "Selected route is missing",
            next_action=(
                "Selected Dashboard can read this row."
                if selected_flag
                else "Record a SELECT_FOR_PRACTICAL_PORTFOLIO decision in Final Review first."
            ),
            severity="block",
        ),
        _continuity_check_row(
            check="Investability evidence handoff",
            status="PASS" if packet_route == "INVESTABILITY_PACKET_READY" or gate_selected else "REVIEW",
            ready=packet_route == "INVESTABILITY_PACKET_READY" or gate_selected,
            current=f"packet={packet_route or '-'} / gate={gate_outcome or '-'} / evidence={evidence_route or '-'}",
            evidence="Investability packet and gate policy are attached" if packet or gate_policy else "Investability packet is missing",
            next_action=(
                "Use the saved packet as the selected monitoring baseline."
                if packet or gate_policy
                else "Open Final Review and rebuild the decision from Practical Validation evidence."
            ),
            severity="review",
        ),
        _continuity_check_row(
            check="Component target contract",
            status="PASS" if active_components and abs(target_weight_total - 100.0) <= 0.01 else "BLOCKED",
            ready=bool(active_components) and abs(target_weight_total - 100.0) <= 0.01,
            current=f"{len(active_components)} components / {target_weight_total:.2f}%",
            evidence="Active selected components are available" if active_components else "No active selected components",
            next_action=(
                "Performance Recheck and allocation monitoring can use this component contract."
                if active_components and abs(target_weight_total - 100.0) <= 0.01
                else "Fix selected components or target weights in the Final Review source."
            ),
            severity="block",
        ),
        _continuity_check_row(
            check="Review cadence and triggers",
            status="PASS" if paper_snapshot.get("review_cadence") and review_triggers else "REVIEW",
            ready=bool(paper_snapshot.get("review_cadence") and review_triggers),
            current=f"cadence={paper_snapshot.get('review_cadence') or '-'} / triggers={len(review_triggers)}",
            evidence="Paper observation trigger seed is attached" if review_triggers else "Review trigger seed is missing",
            next_action=(
                "Use triggers in Review Signals and dossier context."
                if review_triggers
                else "Add review triggers through Final Review paper observation criteria."
            ),
            severity="review",
        ),
        _continuity_check_row(
            check="Monitoring timeline connection",
            status="PASS" if timeline_read_only else "REVIEW",
            ready=timeline_read_only,
            current=f"{timeline.get('schema_version') or '-'} / {timeline.get('timeline_status') or '-'}",
            evidence=f"{timeline_metrics.get('row_count', 0)} timeline rows",
            next_action=(
                "Timeline is connected and remains read-only."
                if timeline_read_only
                else "Rebuild the selected monitoring timeline read model."
            ),
            severity="review",
        ),
        _continuity_check_row(
            check="Performance Recheck input",
            status="PASS" if recheck_present else "NEEDS_INPUT",
            ready=recheck_present,
            current="present" if recheck_present else "not run",
            evidence="Latest recheck is in session state" if recheck_present else "Selected Dashboard needs a Performance Recheck run",
            next_action=(
                "Use Review Signals to compare recheck result with the selected baseline."
                if recheck_present
                else "Run Performance Recheck when evaluating this selected portfolio after selection."
            ),
            severity="input",
        ),
        _continuity_check_row(
            check="Execution and storage boundary",
            status="PASS"
            if timeline_boundary.get("monitoring_log_auto_write") is False
            and timeline_boundary.get("live_approval") is False
            and timeline_boundary.get("order_instruction") is False
            and timeline_boundary.get("auto_rebalance") is False
            else "BLOCKED",
            ready=timeline_boundary.get("monitoring_log_auto_write") is False
            and timeline_boundary.get("live_approval") is False
            and timeline_boundary.get("order_instruction") is False
            and timeline_boundary.get("auto_rebalance") is False,
            current=(
                f"auto_write={timeline_boundary.get('monitoring_log_auto_write')} / "
                f"approval={timeline_boundary.get('live_approval')} / "
                f"order={timeline_boundary.get('order_instruction')} / "
                f"rebalance={timeline_boundary.get('auto_rebalance')}"
            ),
            evidence="No auto-write, approval, order, or rebalance behavior",
            next_action="Keep monitoring updates explicit and read-only.",
            severity="block",
        ),
    ]
    blocked = [check for check in checks if check["Status"] == "BLOCKED"]
    needs_input = [check for check in checks if check["Status"] == "NEEDS_INPUT"]
    review = [check for check in checks if check["Status"] == "REVIEW"]
    if blocked:
        route = "CONTINUITY_BLOCKED"
        next_action = "Resolve blocked continuity checks before treating the row as monitorable."
    elif needs_input:
        route = "CONTINUITY_NEEDS_INPUT"
        next_action = "Run the missing dashboard input checks before relying on monitoring signals."
    elif review:
        route = "CONTINUITY_REVIEW"
        next_action = "Review missing or legacy evidence before continuing monitoring."
    else:
        route = "CONTINUITY_READY"
        next_action = "Selected Dashboard can continue monitoring from this Final Review row."
    return {
        "schema_version": SELECTED_CONTINUITY_CHECK_SCHEMA_VERSION,
        "route": route,
        "route_label": SELECTED_CONTINUITY_ROUTE_LABELS.get(route, route),
        "next_action": next_action,
        "checks": checks,
        "metrics": {
            "check_count": len(checks),
            "blocked_count": len(blocked),
            "needs_input_count": len(needs_input),
            "review_count": len(review),
            "pass_count": sum(1 for check in checks if check["Status"] == "PASS"),
        },
        "execution_boundary": {
            "write_policy": "read_only_continuity_check",
            "monitoring_log_auto_write": False,
            "live_approval": False,
            "order_instruction": False,
            "auto_rebalance": False,
            "notes": "Continuity check reads existing final decision and timeline evidence; it does not persist monitoring state.",
        },
    }


def _comparison_check_row(
    *,
    check: str,
    status: str,
    current: Any,
    evidence: str,
    next_action: str,
    threshold: str = "-",
) -> dict[str, Any]:
    return {
        "Check": check,
        "Status": status,
        "Ready": status == "PASS",
        "Current": _clean_text(current),
        "Threshold": _clean_text(threshold),
        "Evidence": _clean_text(evidence),
        "Next Action": _clean_text(next_action),
    }


def _status_from_comparison_delta(
    value: Any,
    *,
    breach_below: float | None = None,
    watch_below: float | None = None,
) -> str:
    numeric = _optional_float(value)
    if numeric is None:
        return "NEEDS_INPUT"
    if breach_below is not None and numeric < breach_below:
        return "BREACHED"
    if watch_below is not None and numeric < watch_below:
        return "WATCH"
    return "PASS"


def _metric_delta_text(metric_name: str, baseline: Any, latest: Any, delta: Any) -> str:
    return (
        f"{metric_name}: baseline={_clean_text(baseline)}, "
        f"recheck={_clean_text(latest)}, delta={_clean_text(delta)}"
    )


def build_selected_portfolio_recheck_comparison(
    row: dict[str, Any],
    *,
    recheck_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Compare latest Performance Recheck evidence against the selected Final Review baseline without writing logs."""

    selected = dict(row or {})
    raw_decision = dict(selected.get("raw_decision") or selected)
    active_components = _active_components(raw_decision)
    baseline = _baseline_snapshot(raw_decision)
    result = dict(recheck_result or {})

    if not result:
        rows = [
            _comparison_check_row(
                check="Performance Recheck input",
                status="NEEDS_INPUT",
                current="not run",
                threshold="required",
                evidence="No latest Performance Recheck result is attached to this dashboard session.",
                next_action="Run Performance Recheck before treating current Review Signals as complete.",
            ),
            _comparison_check_row(
                check="CAGR vs selected baseline",
                status="NEEDS_INPUT",
                current="-",
                threshold="watch < 0.00 / breach < -0.03",
                evidence="CAGR deterioration cannot be evaluated without a recheck result.",
                next_action="Run Performance Recheck and compare CAGR delta against the selected baseline.",
            ),
            _comparison_check_row(
                check="MDD vs selected baseline",
                status="NEEDS_INPUT",
                current="-",
                threshold="watch < 0.00 / breach < -0.05",
                evidence="Drawdown expansion cannot be evaluated without a recheck result.",
                next_action="Run Performance Recheck and compare MDD delta against the selected baseline.",
            ),
            _comparison_check_row(
                check="Benchmark spread",
                status="NEEDS_INPUT",
                current="-",
                threshold="watch < 0.02 / breach < 0.00",
                evidence="Benchmark spread cannot be evaluated without a recheck result.",
                next_action="Run Performance Recheck and confirm benchmark parity evidence.",
            ),
        ]
        return {
            "schema_version": SELECTED_RECHECK_COMPARISON_SCHEMA_VERSION,
            "route": "RECHECK_COMPARISON_NOT_RUN",
            "route_label": SELECTED_RECHECK_COMPARISON_ROUTE_LABELS["RECHECK_COMPARISON_NOT_RUN"],
            "overall_status": "NEEDS_INPUT",
            "conclusion": "Performance Recheck가 아직 없어 selected thesis 유지 여부를 판단할 수 없습니다.",
            "rows": rows,
            "metrics": {
                "check_count": len(rows),
                "pass_count": 0,
                "watch_count": 0,
                "breached_count": 0,
                "needs_input_count": len(rows),
                "active_component_count": len(active_components),
                "recheck_component_count": 0,
                "blocker_count": 0,
                "recheck_present": False,
            },
            "execution_boundary": {
                "write_policy": "read_only_recheck_comparison",
                "monitoring_log_auto_write": False,
                "live_approval": False,
                "order_instruction": False,
                "auto_rebalance": False,
                "notes": "Recheck comparison reads existing decision and session recheck evidence; it does not save monitoring logs.",
            },
        }

    if result.get("status") == "error":
        error_text = _clean_text(result.get("error"), "Performance Recheck failed")
        rows = [
            _comparison_check_row(
                check="Performance Recheck input",
                status="NEEDS_INPUT",
                current=error_text,
                threshold="successful recheck required",
                evidence="The latest recheck failed before comparison evidence could be built.",
                next_action="Fix the selected component contract or period inputs, then rerun Performance Recheck.",
            )
        ]
        return {
            "schema_version": SELECTED_RECHECK_COMPARISON_SCHEMA_VERSION,
            "route": "RECHECK_COMPARISON_ERROR",
            "route_label": SELECTED_RECHECK_COMPARISON_ROUTE_LABELS["RECHECK_COMPARISON_ERROR"],
            "overall_status": "NEEDS_INPUT",
            "conclusion": "Performance Recheck 오류 때문에 selected thesis 유지 여부를 판단할 수 없습니다.",
            "rows": rows,
            "metrics": {
                "check_count": len(rows),
                "pass_count": 0,
                "watch_count": 0,
                "breached_count": 0,
                "needs_input_count": len(rows),
                "active_component_count": len(active_components),
                "recheck_component_count": 0,
                "blocker_count": len(list(result.get("blockers") or [])),
                "recheck_present": True,
            },
            "execution_boundary": {
                "write_policy": "read_only_recheck_comparison",
                "monitoring_log_auto_write": False,
                "live_approval": False,
                "order_instruction": False,
                "auto_rebalance": False,
                "notes": "Recheck comparison reads existing decision and session recheck evidence; it does not save monitoring logs.",
            },
        }

    change = dict(result.get("change_summary") or {})
    portfolio_summary = dict(result.get("portfolio_summary") or {})
    baseline_summary = dict(result.get("baseline_summary") or {})
    benchmark_summary = dict(result.get("benchmark_summary") or {})
    period = dict(result.get("period") or {})
    component_rows = [dict(item or {}) for item in list(result.get("component_rows") or [])]
    blockers = [str(item) for item in list(result.get("blockers") or []) if str(item)]

    latest_cagr = _optional_float(portfolio_summary.get("cagr"))
    latest_mdd = _optional_float(portfolio_summary.get("mdd"))
    baseline_cagr = _optional_float(baseline_summary.get("cagr"))
    baseline_mdd = _optional_float(baseline_summary.get("mdd"))
    if baseline_cagr is None:
        baseline_cagr = _optional_float(baseline.get("baseline_cagr"))
    if baseline_mdd is None:
        baseline_mdd = _optional_float(baseline.get("baseline_mdd"))
    cagr_delta = _optional_float(change.get("cagr_delta_vs_baseline"))
    mdd_delta = _optional_float(change.get("mdd_delta_vs_baseline"))
    spread = _optional_float(change.get("net_cagr_spread"))
    benchmark_cagr = _optional_float(change.get("benchmark_cagr"))
    if benchmark_cagr is None:
        benchmark_cagr = _optional_float(benchmark_summary.get("cagr"))

    result_status = str(result.get("status") or "").strip()
    input_status = "PASS" if result_status == "ok" else "WATCH" if result_status == "partial" else "NEEDS_INPUT"
    rows = [
        _comparison_check_row(
            check="Performance Recheck input",
            status=input_status,
            current=result_status or "-",
            threshold="ok or partial with explicit blockers",
            evidence=_clean_text(result.get("verdict_route") or result.get("verdict")),
            next_action=(
                "Use metric rows below to decide whether the selected thesis still holds."
                if input_status == "PASS"
                else "Partial recheck must be reviewed before relying on the comparison."
                if input_status == "WATCH"
                else "Rerun Performance Recheck with a valid selected component contract."
            ),
        )
    ]

    cagr_status = _status_from_comparison_delta(cagr_delta, breach_below=-0.03, watch_below=0.0)
    rows.append(
        _comparison_check_row(
            check="CAGR vs selected baseline",
            status=cagr_status,
            current=_metric_delta_text("CAGR", baseline_cagr, latest_cagr, cagr_delta),
            threshold="watch < 0.00 / breach < -0.03",
            evidence="Latest recheck CAGR compared with the Final Review baseline CAGR.",
            next_action=(
                "CAGR deterioration is large; review component contribution and thesis validity."
                if cagr_status == "BREACHED"
                else "CAGR is weaker; keep it on the next review cycle."
                if cagr_status == "WATCH"
                else "CAGR evidence still supports the selected thesis."
                if cagr_status == "PASS"
                else "Recheck result is missing CAGR delta evidence."
            ),
        )
    )

    mdd_status = _status_from_comparison_delta(mdd_delta, breach_below=-0.05, watch_below=0.0)
    rows.append(
        _comparison_check_row(
            check="MDD vs selected baseline",
            status=mdd_status,
            current=_metric_delta_text("MDD", baseline_mdd, latest_mdd, mdd_delta),
            threshold="watch < 0.00 / breach < -0.05",
            evidence="Latest recheck MDD compared with the Final Review baseline MDD.",
            next_action=(
                "Drawdown expanded materially; review risk and weak periods before continuing."
                if mdd_status == "BREACHED"
                else "Drawdown is worse; keep it under review."
                if mdd_status == "WATCH"
                else "Drawdown evidence still supports the selected thesis."
                if mdd_status == "PASS"
                else "Recheck result is missing MDD delta evidence."
            ),
        )
    )

    spread_status = _status_from_comparison_delta(spread, breach_below=0.0, watch_below=0.02)
    rows.append(
        _comparison_check_row(
            check="Benchmark spread",
            status=spread_status,
            current=f"spread={_clean_text(spread)}, benchmark_cagr={_clean_text(benchmark_cagr)}",
            threshold="watch < 0.02 / breach < 0.00",
            evidence="Latest recheck net CAGR spread against the benchmark.",
            next_action=(
                "Benchmark outperformed the selected portfolio; review the selection thesis."
                if spread_status == "BREACHED"
                else "Benchmark edge is thin; verify this again in the next recheck."
                if spread_status == "WATCH"
                else "Benchmark spread remains supportive."
                if spread_status == "PASS"
                else "Recheck result is missing benchmark spread evidence."
            ),
        )
    )

    expected_components = len(active_components)
    actual_components = len(component_rows)
    if expected_components <= 0 or actual_components <= 0:
        coverage_status = "NEEDS_INPUT"
    elif blockers or actual_components < expected_components:
        coverage_status = "WATCH"
    else:
        coverage_status = "PASS"
    rows.append(
        _comparison_check_row(
            check="Component evidence coverage",
            status=coverage_status,
            current=f"{actual_components}/{expected_components} components, blockers={len(blockers)}",
            threshold="all active components should contribute or blockers must be reviewed",
            evidence=", ".join(blockers[:3]) if blockers else "All active components contributed to the recheck comparison.",
            next_action=(
                "Fix component replay blockers before relying on the comparison."
                if coverage_status == "NEEDS_INPUT"
                else "Review partial component coverage and decide whether the comparison is representative."
                if coverage_status == "WATCH"
                else "Component coverage is complete."
            ),
        )
    )

    period_start = _date_text(period.get("start"))
    period_end = _date_text(period.get("end"))
    added_days = _optional_float(period.get("added_days_vs_baseline"))
    if not period_start or not period_end:
        period_status = "NEEDS_INPUT"
    elif added_days is not None and added_days <= 0:
        period_status = "WATCH"
    else:
        period_status = "PASS"
    rows.append(
        _comparison_check_row(
            check="Recheck period coverage",
            status=period_status,
            current=f"{period_start or '-'} -> {period_end or '-'} / added_days={_clean_text(added_days)}",
            threshold="latest period should extend beyond selected baseline when checking ongoing validity",
            evidence=(
                f"baseline={period.get('baseline_start') or baseline.get('baseline_start') or '-'}"
                f" -> {period.get('baseline_end') or baseline.get('baseline_end') or '-'}"
            ),
            next_action=(
                "Select a period that reaches the latest available market data."
                if period_status == "WATCH"
                else "Recheck period is available for comparison."
                if period_status == "PASS"
                else "Rerun Performance Recheck with a valid period."
            ),
        )
    )

    statuses = [str(item.get("Status") or "") for item in rows]
    if "BREACHED" in statuses:
        route = "RECHECK_COMPARISON_BREACHED"
        overall_status = "BREACHED"
        conclusion = "최신 재검증 결과가 기존 선정 근거를 훼손한 항목이 있습니다."
    elif "NEEDS_INPUT" in statuses:
        route = "RECHECK_COMPARISON_WATCH"
        overall_status = "NEEDS_INPUT"
        conclusion = "비교를 완료하려면 누락된 recheck evidence를 보강해야 합니다."
    elif "WATCH" in statuses:
        route = "RECHECK_COMPARISON_WATCH"
        overall_status = "WATCH"
        conclusion = "선정 thesis는 즉시 차단되지는 않지만 watch 항목이 있습니다."
    else:
        route = "RECHECK_COMPARISON_READY"
        overall_status = "CLEAR"
        conclusion = "현재 recheck evidence는 기존 선정 thesis를 계속 지지합니다."

    return {
        "schema_version": SELECTED_RECHECK_COMPARISON_SCHEMA_VERSION,
        "route": route,
        "route_label": SELECTED_RECHECK_COMPARISON_ROUTE_LABELS.get(route, route),
        "overall_status": overall_status,
        "conclusion": conclusion,
        "rows": rows,
        "metrics": {
            "check_count": len(rows),
            "pass_count": sum(1 for item in rows if item.get("Status") == "PASS"),
            "watch_count": sum(1 for item in rows if item.get("Status") == "WATCH"),
            "breached_count": sum(1 for item in rows if item.get("Status") == "BREACHED"),
            "needs_input_count": sum(1 for item in rows if item.get("Status") == "NEEDS_INPUT"),
            "active_component_count": expected_components,
            "recheck_component_count": actual_components,
            "blocker_count": len(blockers),
            "recheck_present": True,
        },
        "evidence": {
            "period": period,
            "portfolio_summary": portfolio_summary,
            "baseline_summary": {
                "cagr": baseline_cagr,
                "mdd": baseline_mdd,
                "start": baseline_summary.get("start") or baseline.get("baseline_start"),
                "end": baseline_summary.get("end") or baseline.get("baseline_end"),
            },
            "benchmark_summary": benchmark_summary,
            "change_summary": {
                "cagr_delta_vs_baseline": cagr_delta,
                "mdd_delta_vs_baseline": mdd_delta,
                "benchmark_cagr": benchmark_cagr,
                "net_cagr_spread": spread,
            },
            "component_rows": component_rows,
            "blockers": blockers,
        },
        "execution_boundary": {
            "write_policy": "read_only_recheck_comparison",
            "monitoring_log_auto_write": False,
            "live_approval": False,
            "order_instruction": False,
            "auto_rebalance": False,
            "notes": "Recheck comparison reads existing decision and session recheck evidence; it does not save monitoring logs.",
        },
    }


def load_selected_portfolio_latest_market_date(
    *,
    end: str | None = None,
    timeframe: str = "1d",
) -> dict[str, Any]:
    """Return the latest available market date for dashboard recheck defaults."""
    try:
        latest = load_latest_market_date(end=end, timeframe=timeframe)
    except Exception as exc:  # pragma: no cover - depends on local MySQL availability
        return {"status": "error", "latest_market_date": None, "error": str(exc)}
    return {
        "status": "ok" if latest is not None else "empty",
        "latest_market_date": _format_date_value(latest),
        "error": None,
    }


def build_selected_portfolio_recheck_defaults(row: dict[str, Any]) -> dict[str, Any]:
    """Extract the originally selected validation period for the dashboard recheck controls."""
    baseline = _baseline_snapshot(row)
    latest_result = load_selected_portfolio_latest_market_date()
    latest_date = latest_result.get("latest_market_date")
    return {
        "baseline_start": baseline.get("baseline_start"),
        "baseline_end": baseline.get("baseline_end"),
        "baseline_cagr": baseline.get("baseline_cagr"),
        "baseline_mdd": baseline.get("baseline_mdd"),
        "latest_market_date": latest_date,
        "latest_market_date_status": latest_result.get("status"),
        "latest_market_date_error": latest_result.get("error"),
        "default_start": baseline.get("baseline_start") or "2016-01-01",
        "default_end": latest_date or baseline.get("baseline_end") or date.today().isoformat(),
    }


def _summary_metrics_from_df(result_df: pd.DataFrame, *, name: str, freq: str = "M") -> dict[str, Any]:
    if result_df.empty:
        return {"name": name}
    summary_df = portfolio_performance_summary(result_df, name=name, freq=freq)
    row = dict(summary_df.iloc[0]) if not summary_df.empty else {}
    start_balance = _optional_float(row.get("Start Balance"))
    end_balance = _optional_float(row.get("End Balance"))
    total_return = (end_balance / start_balance - 1.0) if start_balance and end_balance is not None else None
    return {
        "name": name,
        "start_date": _format_date_value(row.get("Start Date")),
        "end_date": _format_date_value(row.get("End Date")),
        "start_balance": start_balance,
        "end_balance": end_balance,
        "total_return": total_return,
        "cagr": _optional_float(row.get("CAGR")),
        "mdd": _optional_float(row.get("Maximum Drawdown")),
        "sharpe": _optional_float(row.get("Sharpe Ratio")),
        "std": _optional_float(row.get("Standard Deviation")),
    }


def _scale_result_df(result_df: pd.DataFrame, *, initial_capital: float) -> pd.DataFrame:
    scaled = result_df[["Date", "Total Balance", "Total Return"]].copy()
    scaled["Date"] = pd.to_datetime(scaled["Date"], errors="coerce")
    scaled = scaled.dropna(subset=["Date", "Total Balance"]).sort_values("Date").reset_index(drop=True)
    if scaled.empty:
        return scaled
    start_balance = _optional_float(scaled["Total Balance"].iloc[0]) or 0.0
    scale = float(initial_capital) / start_balance if start_balance > 0 else 1.0
    scaled["Total Balance"] = pd.to_numeric(scaled["Total Balance"], errors="coerce") * scale
    scaled["Total Return"] = scaled["Total Balance"].pct_change().fillna(0.0)
    return scaled


def _scale_benchmark_df(benchmark_df: pd.DataFrame, *, initial_capital: float) -> pd.DataFrame:
    if benchmark_df is None or benchmark_df.empty or "Benchmark Total Balance" not in benchmark_df.columns:
        return pd.DataFrame()
    scaled = benchmark_df[["Date", "Benchmark Total Balance", "Benchmark Total Return"]].copy()
    scaled["Date"] = pd.to_datetime(scaled["Date"], errors="coerce")
    scaled = scaled.dropna(subset=["Date", "Benchmark Total Balance"]).sort_values("Date").reset_index(drop=True)
    if scaled.empty:
        return scaled
    start_balance = _optional_float(scaled["Benchmark Total Balance"].iloc[0]) or 0.0
    scale = float(initial_capital) / start_balance if start_balance > 0 else 1.0
    scaled["Benchmark Total Balance"] = pd.to_numeric(scaled["Benchmark Total Balance"], errors="coerce") * scale
    scaled["Benchmark Total Return"] = scaled["Benchmark Total Balance"].pct_change().fillna(0.0)
    return scaled


def _combine_component_result_dfs(
    dfs: list[pd.DataFrame],
    *,
    ratios: list[float],
    initial_capital: float,
) -> pd.DataFrame:
    if not dfs:
        return pd.DataFrame()
    normalized_frames: list[pd.DataFrame] = []
    for index, result_df in enumerate(dfs):
        working = result_df[["Date", "Total Balance"]].copy()
        working["Date"] = pd.to_datetime(working["Date"], errors="coerce")
        working["Total Balance"] = pd.to_numeric(working["Total Balance"], errors="coerce")
        working = working.dropna(subset=["Date", "Total Balance"]).sort_values("Date")
        if working.empty:
            continue
        start_balance = _optional_float(working["Total Balance"].iloc[0]) or 0.0
        if start_balance <= 0.0:
            continue
        working[f"component_{index}"] = working["Total Balance"] / start_balance
        normalized_frames.append(working[["Date", f"component_{index}"]].set_index("Date"))
    if not normalized_frames:
        return pd.DataFrame()

    combined = pd.concat(normalized_frames, axis=1, join="inner").sort_index()
    if combined.empty:
        return pd.DataFrame()
    weights = pd.Series(
        [float(ratio or 0.0) for ratio in ratios[: len(combined.columns)]],
        index=list(combined.columns),
        dtype=float,
    )
    if float(weights.sum()) <= 0.0:
        weights = pd.Series([1.0 / len(combined.columns)] * len(combined.columns), index=list(combined.columns))
    else:
        weights = weights / float(weights.sum())
    weighted_balance = combined.mul(weights, axis=1).sum(axis=1) * float(initial_capital)
    output = pd.DataFrame(
        {
            "Date": weighted_balance.index,
            "Total Balance": weighted_balance.values,
        }
    ).reset_index(drop=True)
    output["Total Return"] = output["Total Balance"].pct_change().fillna(0.0)
    return output


def _period_extremes(result_df: pd.DataFrame, *, top_n: int = 3) -> dict[str, list[dict[str, Any]]]:
    if result_df.empty or "Total Return" not in result_df.columns:
        return {"best": [], "worst": []}
    working = result_df[["Date", "Total Balance", "Total Return"]].copy()
    working["Date"] = pd.to_datetime(working["Date"], errors="coerce")
    working["Total Return"] = pd.to_numeric(working["Total Return"], errors="coerce")
    working = working.dropna(subset=["Date", "Total Return"])
    if working.empty:
        return {"best": [], "worst": []}
    working["Date"] = working["Date"].dt.strftime("%Y-%m-%d")
    records = working.to_dict("records")
    return {
        "best": sorted(records, key=lambda item: float(item.get("Total Return") or 0.0), reverse=True)[:top_n],
        "worst": sorted(records, key=lambda item: float(item.get("Total Return") or 0.0))[:top_n],
    }


def _find_candidate_rows_by_registry_id() -> dict[str, dict[str, Any]]:
    return {
        str(row.get("registry_id") or "").strip(): row
        for row in load_current_candidate_registry_latest()
        if str(row.get("registry_id") or "").strip()
    }


def build_selected_portfolio_performance_recheck(
    row: dict[str, Any],
    *,
    start: str,
    end: str,
    initial_capital: float = 10000.0,
) -> dict[str, Any]:
    """Replay selected components over a user-selected period and compare against the original baseline."""
    start_ts = pd.to_datetime(start, errors="coerce")
    end_ts = pd.to_datetime(end, errors="coerce")
    if pd.isna(start_ts) or pd.isna(end_ts):
        return {"status": "error", "error": "재검증 시작일과 종료일을 확인해야 합니다."}
    if start_ts > end_ts:
        return {"status": "error", "error": "재검증 시작일은 종료일보다 늦을 수 없습니다."}
    capital = float(initial_capital or 0.0)
    if capital <= 0:
        return {"status": "error", "error": "가상 투자금은 0보다 커야 합니다."}

    raw_decision = dict(row.get("raw_decision") or row)
    active_components = _active_components(raw_decision)
    if not active_components:
        return {"status": "error", "error": "재검증할 active component가 없습니다."}

    try:
        from .candidate_library import (
            build_candidate_replay_payload,
            run_candidate_replay_payload,
        )
    except Exception as exc:  # pragma: no cover - defensive import boundary
        return {"status": "error", "error": f"candidate replay helper import failed: {exc}"}

    candidate_by_id = _find_candidate_rows_by_registry_id()
    component_dfs: list[pd.DataFrame] = []
    ratios: list[float] = []
    component_rows: list[dict[str, Any]] = []
    blockers: list[str] = []
    first_benchmark_df = pd.DataFrame()
    first_benchmark_label = "-"

    for index, component in enumerate(active_components):
        identity = _component_identity(component, index)
        title = _clean_text(component.get("title") or identity)
        weight = (_optional_float(component.get("target_weight")) or 0.0) / 100.0
        registry_id = _clean_text(component.get("registry_id"), "")
        current_row = candidate_by_id.get(registry_id)
        if not current_row:
            blockers.append(f"{title}: Candidate Registry row를 찾지 못했습니다. registry_id={registry_id or '-'}")
            continue
        try:
            payload = build_candidate_replay_payload(current_row)
            payload["start"] = start_ts.strftime("%Y-%m-%d")
            payload["end"] = end_ts.strftime("%Y-%m-%d")
            bundle = run_candidate_replay_payload(payload, current_row=current_row)
        except Exception as exc:
            blockers.append(f"{title}: 재검증 실행 실패 - {exc}")
            continue

        result_df = bundle.get("result_df")
        if not isinstance(result_df, pd.DataFrame) or result_df.empty:
            blockers.append(f"{title}: 재검증 결과가 비어 있습니다.")
            continue
        component_dfs.append(result_df)
        ratios.append(weight)

        scaled_component_df = _scale_result_df(result_df, initial_capital=capital)
        component_summary = _summary_metrics_from_df(scaled_component_df, name=title)
        component_return = _optional_float(component_summary.get("total_return"))
        component_rows.append(
            {
                "Component": title,
                "Registry ID": registry_id or "-",
                "Target Weight": round(weight * 100.0, 4),
                "Start": component_summary.get("start_date"),
                "End": component_summary.get("end_date"),
                "Total Return": component_return,
                "Weighted Contribution": component_return * weight if component_return is not None else None,
                "CAGR": component_summary.get("cagr"),
                "MDD": component_summary.get("mdd"),
                "Sharpe": component_summary.get("sharpe"),
            }
        )

        benchmark_df = bundle.get("benchmark_chart_df")
        if first_benchmark_df.empty and isinstance(benchmark_df, pd.DataFrame) and not benchmark_df.empty:
            first_benchmark_df = benchmark_df
            first_benchmark_label = str(payload.get("benchmark_ticker") or component.get("benchmark") or "Benchmark")

    if not component_dfs:
        return {
            "status": "error",
            "error": "재검증 가능한 component 결과가 없습니다.",
            "blockers": blockers,
        }

    portfolio_df = _combine_component_result_dfs(component_dfs, ratios=ratios, initial_capital=capital)
    if portfolio_df.empty:
        return {"status": "error", "error": "포트폴리오 성과 합성 결과가 비어 있습니다.", "blockers": blockers}
    portfolio_summary = _summary_metrics_from_df(portfolio_df, name="Selected Portfolio")
    benchmark_scaled = _scale_benchmark_df(first_benchmark_df, initial_capital=capital)
    benchmark_summary = (
        _summary_metrics_from_df(
            benchmark_scaled.rename(
                columns={
                    "Benchmark Total Balance": "Total Balance",
                    "Benchmark Total Return": "Total Return",
                }
            ),
            name=first_benchmark_label,
        )
        if not benchmark_scaled.empty
        else {}
    )

    baseline = _baseline_snapshot(raw_decision)
    latest_cagr = _optional_float(portfolio_summary.get("cagr"))
    latest_mdd = _optional_float(portfolio_summary.get("mdd"))
    baseline_cagr = _optional_float(baseline.get("baseline_cagr"))
    baseline_mdd = _optional_float(baseline.get("baseline_mdd"))
    cagr_delta = latest_cagr - baseline_cagr if latest_cagr is not None and baseline_cagr is not None else None
    mdd_delta = latest_mdd - baseline_mdd if latest_mdd is not None and baseline_mdd is not None else None
    benchmark_cagr = _optional_float(benchmark_summary.get("cagr"))
    net_cagr_spread = latest_cagr - benchmark_cagr if latest_cagr is not None and benchmark_cagr is not None else None
    if blockers:
        verdict_route = "PARTIAL_RECHECK"
        verdict = "일부 component만 재검증되어 결과 해석에 주의가 필요합니다."
    elif cagr_delta is not None and cagr_delta < -0.03:
        verdict_route = "PERFORMANCE_WEAKENED"
        verdict = "원래 검증 대비 CAGR이 의미 있게 낮아졌습니다. 약화 원인을 확인해야 합니다."
    elif mdd_delta is not None and mdd_delta < -0.05:
        verdict_route = "RISK_DRAWDOWN_EXPANDED"
        verdict = "원래 검증 대비 최대 낙폭이 커졌습니다. 리스크 재검토가 필요합니다."
    else:
        verdict_route = "SELECTION_THESIS_HOLDS"
        verdict = "선택한 재검증 기간에서 기존 선정 근거가 대체로 유지됩니다."

    chart_df = portfolio_df[["Date", "Total Balance"]].rename(columns={"Total Balance": "Selected Portfolio"})
    if not benchmark_scaled.empty:
        chart_df = chart_df.merge(
            benchmark_scaled[["Date", "Benchmark Total Balance"]].rename(
                columns={"Benchmark Total Balance": first_benchmark_label}
            ),
            on="Date",
            how="left",
        )

    return {
        "status": "ok" if not blockers else "partial",
        "verdict_route": verdict_route,
        "verdict": verdict,
        "period": {
            "start": start_ts.strftime("%Y-%m-%d"),
            "end": end_ts.strftime("%Y-%m-%d"),
            "baseline_start": baseline.get("baseline_start"),
            "baseline_end": baseline.get("baseline_end"),
            "added_days_vs_baseline": (
                (end_ts - pd.to_datetime(baseline.get("baseline_end"), errors="coerce")).days
                if baseline.get("baseline_end") and not pd.isna(pd.to_datetime(baseline.get("baseline_end"), errors="coerce"))
                else None
            ),
        },
        "initial_capital": capital,
        "portfolio_summary": portfolio_summary,
        "benchmark_summary": benchmark_summary,
        "benchmark_label": first_benchmark_label,
        "baseline_summary": {
            "cagr": baseline_cagr,
            "mdd": baseline_mdd,
            "start": baseline.get("baseline_start"),
            "end": baseline.get("baseline_end"),
        },
        "change_summary": {
            "cagr_delta_vs_baseline": cagr_delta,
            "mdd_delta_vs_baseline": mdd_delta,
            "benchmark_cagr": benchmark_cagr,
            "net_cagr_spread": net_cagr_spread,
        },
        "component_rows": component_rows,
        "chart_df": chart_df,
        "portfolio_result_df": portfolio_df,
        "period_extremes": _period_extremes(portfolio_df),
        "blockers": blockers,
        "execution_boundary": {
            "write_policy": "read_only_recheck",
            "live_approval": False,
            "order_instruction": False,
            "notes": "Performance recheck replays stored candidate contracts over a selected period and does not save portfolio records.",
        },
    }


def load_latest_selected_portfolio_prices(
    symbols: list[str],
    *,
    end: str | None = None,
    timeframe: str = "1d",
    field: str = "close",
) -> dict[str, Any]:
    """Read latest DB prices for optional dashboard input assistance without mutating portfolio records."""
    cleaned_symbols: list[str] = []
    seen: set[str] = set()
    for symbol in symbols:
        cleaned = str(symbol or "").strip().upper()
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        cleaned_symbols.append(cleaned)

    if not cleaned_symbols:
        return {
            "status": "empty",
            "rows": [],
            "price_by_symbol": {},
            "missing_symbols": [],
            "error": None,
        }

    try:
        from finance.loaders.price import load_latest_prices
    except Exception as exc:  # pragma: no cover - defensive UI boundary
        return {
            "status": "error",
            "rows": [],
            "price_by_symbol": {},
            "missing_symbols": cleaned_symbols,
            "error": f"latest price loader import failed: {exc}",
        }

    try:
        price_df = load_latest_prices(symbols=cleaned_symbols, end=end, timeframe=timeframe, field=field)
    except Exception as exc:  # pragma: no cover - depends on local MySQL availability
        return {
            "status": "error",
            "rows": [],
            "price_by_symbol": {},
            "missing_symbols": cleaned_symbols,
            "error": str(exc),
        }

    rows: list[dict[str, Any]] = []
    price_by_symbol: dict[str, dict[str, Any]] = {}
    for record in price_df.to_dict("records") if not price_df.empty else []:
        symbol = str(record.get("symbol") or "").strip().upper()
        price = _optional_float(record.get("price"))
        if not symbol or price is None:
            continue
        row = {
            "symbol": symbol,
            "latest_date": _format_date_value(record.get("latest_date")),
            "price": round(price, 6),
            "close": _optional_float(record.get("close")),
            "adj_close": _optional_float(record.get("adj_close")),
            "field": field,
            "timeframe": timeframe,
        }
        rows.append(row)
        price_by_symbol[symbol] = row

    missing_symbols = [symbol for symbol in cleaned_symbols if symbol not in price_by_symbol]
    return {
        "status": "ok" if rows else "empty",
        "rows": rows,
        "price_by_symbol": price_by_symbol,
        "missing_symbols": missing_symbols,
        "error": None,
    }


def _build_summary(
    *,
    all_final_decisions: list[dict[str, Any]],
    selected_rows: list[dict[str, Any]],
    dashboard_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    status_counts = {status: 0 for status in FINAL_SELECTED_PORTFOLIO_STATUS_ORDER}
    for row in dashboard_rows:
        status = str(row.get("operation_status") or "blocked")
        if status not in status_counts:
            status_counts[status] = 0
        status_counts[status] += 1
    return {
        "registry_path": str(FINAL_SELECTION_DECISION_V2_FILE),
        "final_decision_count": len(all_final_decisions),
        "selected_decision_count": len(selected_rows),
        "dashboard_row_count": len(dashboard_rows),
        "status_counts": status_counts,
        "component_count": sum(int(row.get("component_count") or 0) for row in dashboard_rows),
        "live_approval_enabled_count": sum(1 for row in selected_rows if bool(row.get("live_approval"))),
        "order_instruction_enabled_count": sum(1 for row in selected_rows if bool(row.get("order_instruction"))),
    }


def load_final_selected_portfolio_dashboard(limit: int | None = 250) -> dict[str, Any]:
    """Load selected dashboard data from Final Review V2 decisions without writing new rows."""
    all_rows = load_final_selection_decisions_v2(limit=limit)
    selected_rows = [row for row in all_rows if _is_selected_practical_portfolio(row)]
    dashboard_rows = [build_final_selected_portfolio_dashboard_row(row) for row in selected_rows]
    return {
        "all_final_decisions": all_rows,
        "selected_final_decisions": selected_rows,
        "dashboard_rows": dashboard_rows,
        "summary": _build_summary(
            all_final_decisions=all_rows,
            selected_rows=selected_rows,
            dashboard_rows=dashboard_rows,
        ),
    }
