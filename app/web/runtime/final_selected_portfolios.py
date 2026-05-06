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
