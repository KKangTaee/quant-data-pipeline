from __future__ import annotations

from typing import Any

from .final_selection_decisions import (
    FINAL_SELECTION_DECISION_REGISTRY_FILE,
    load_final_selection_decisions,
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


def _optional_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


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
    if validation_route and validation_route != "READY_FOR_ROBUSTNESS_REVIEW":
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
        "registry_path": str(FINAL_SELECTION_DECISION_REGISTRY_FILE),
        "final_decision_count": len(all_final_decisions),
        "selected_decision_count": len(selected_rows),
        "dashboard_row_count": len(dashboard_rows),
        "status_counts": status_counts,
        "component_count": sum(int(row.get("component_count") or 0) for row in dashboard_rows),
        "live_approval_enabled_count": sum(1 for row in selected_rows if bool(row.get("live_approval"))),
        "order_instruction_enabled_count": sum(1 for row in selected_rows if bool(row.get("order_instruction"))),
    }


def load_final_selected_portfolio_dashboard(limit: int | None = 250) -> dict[str, Any]:
    """Load Phase36 dashboard data from Final Review decisions without writing new registry rows."""
    all_rows = load_final_selection_decisions(limit=limit)
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
