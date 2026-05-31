from __future__ import annotations

import re
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
SELECTED_ALLOCATION_DRIFT_BOUNDARY_SCHEMA_VERSION = "selected_allocation_drift_evidence_boundary_v1"
SELECTED_MONITORING_TIMELINE_SCHEMA_VERSION = "selected_monitoring_timeline_v1"
SELECTED_CONTINUITY_CHECK_SCHEMA_VERSION = "selected_continuity_check_v1"
SELECTED_RECHECK_COMPARISON_SCHEMA_VERSION = "selected_recheck_comparison_v1"
SELECTED_RECHECK_READINESS_SCHEMA_VERSION = "selected_recheck_readiness_v1"
SELECTED_RECHECK_SYMBOL_FRESHNESS_SCHEMA_VERSION = "selected_recheck_symbol_freshness_v1"
SELECTED_RECHECK_OPERATIONS_PREFLIGHT_SCHEMA_VERSION = "selected_recheck_operations_preflight_v1"
SELECTED_PROVIDER_EVIDENCE_SCHEMA_VERSION = "selected_provider_evidence_v1"
SELECTED_PROVIDER_STALENESS_CONTRACT_SCHEMA_VERSION = "selected_provider_evidence_staleness_contract_v1"
SELECTED_REVIEW_SIGNAL_POLICY_SCHEMA_VERSION = "selected_review_signal_policy_v1"
SELECTED_DECISION_SOURCE_CONSISTENCY_SCHEMA_VERSION = "selected_decision_source_consistency_v1"
SELECTED_DASHBOARD_HANDOFF_SCHEMA_VERSION = "selected_dashboard_handoff_v1"
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
SELECTED_RECHECK_READINESS_ROUTE_LABELS = {
    "RECHECK_READINESS_READY": "재검증 준비 완료",
    "RECHECK_READINESS_REVIEW": "재검증 전 확인 필요",
    "RECHECK_READINESS_NEEDS_DATA": "DB 데이터 확인 필요",
    "RECHECK_READINESS_BLOCKED": "재검증 차단",
}
SELECTED_RECHECK_SYMBOL_FRESHNESS_ROUTE_LABELS = {
    "SYMBOL_FRESHNESS_READY": "가격 최신성 준비 완료",
    "SYMBOL_FRESHNESS_WATCH": "가격 최신성 관찰 필요",
    "SYMBOL_FRESHNESS_STALE": "가격 데이터 stale",
    "SYMBOL_FRESHNESS_MISSING": "가격 데이터 누락",
    "SYMBOL_FRESHNESS_NEEDS_DATA": "가격 DB 확인 필요",
    "SYMBOL_FRESHNESS_BLOCKED": "symbol 확인 차단",
}
SELECTED_RECHECK_OPERATIONS_PREFLIGHT_ROUTE_LABELS = {
    "RECHECK_PREFLIGHT_READY": "재검증 preflight 준비 완료",
    "RECHECK_PREFLIGHT_REVIEW": "재검증 preflight 확인 필요",
    "RECHECK_PREFLIGHT_NEEDS_DATA": "재검증 preflight 데이터 확인 필요",
    "RECHECK_PREFLIGHT_BLOCKED": "재검증 preflight 차단",
}
SELECTED_PROVIDER_EVIDENCE_ROUTE_LABELS = {
    "SELECTED_PROVIDER_READY": "Provider 근거 준비 완료",
    "SELECTED_PROVIDER_REVIEW": "Provider 근거 검토 필요",
    "SELECTED_PROVIDER_NEEDS_DATA": "Provider DB 확인 필요",
    "SELECTED_PROVIDER_BLOCKED": "Provider 근거 차단",
}
SELECTED_REVIEW_SIGNAL_POLICY_ROUTE_LABELS = {
    "REVIEW_SIGNAL_CLEAR": "운영 신호 정상",
    "REVIEW_SIGNAL_WATCH": "운영 신호 관찰",
    "REVIEW_SIGNAL_NEEDS_INPUT": "운영 신호 입력 필요",
    "REVIEW_SIGNAL_BREACHED": "운영 신호 재검토",
}
SELECTED_ALLOCATION_DRIFT_BOUNDARY_ROUTE_LABELS = {
    "ALLOCATION_DRIFT_BOUNDARY_OPTIONAL": "비중 근거 선택 점검",
    "ALLOCATION_DRIFT_BOUNDARY_READY": "비중 근거 정상",
    "ALLOCATION_DRIFT_BOUNDARY_WATCH": "비중 근거 관찰",
    "ALLOCATION_DRIFT_BOUNDARY_NEEDS_INPUT": "비중 근거 입력 필요",
    "ALLOCATION_DRIFT_BOUNDARY_BREACHED": "비중 근거 재검토",
    "ALLOCATION_DRIFT_BOUNDARY_BLOCKED": "비중 근거 경계 위반",
}
SELECTED_DASHBOARD_HANDOFF_ROUTE_LABELS = {
    "HANDOFF_NO_FINAL_DECISION": "최종 판단 없음",
    "HANDOFF_NO_SELECTED_DECISION": "선정 row 없음",
    "HANDOFF_BLOCKED": "Dashboard 연결 차단",
    "HANDOFF_READY": "Dashboard 연결 가능",
}
_SELECTED_PROVIDER_REQUIRED_AREAS = {"ETF Operability", "ETF Holdings", "ETF Exposure"}
_SELECTED_PROVIDER_STATUS_RANK = {
    "PASS": 0,
    "REVIEW": 1,
    "NEEDS_INPUT": 2,
    "BLOCKED": 3,
}
_TIMELINE_STATUS_RANK = {
    "OPTIONAL": 0,
    "CLEAR": 1,
    "WATCH": 2,
    "NEEDS_INPUT": 3,
    "BREACHED": 4,
}
_ALLOCATION_DRIFT_DISABLED_FIELDS = (
    "db_write",
    "registry_write",
    "monitoring_log_auto_write",
    "input_persistence",
    "alert_persistence",
    "account_connection",
    "broker_sync",
    "live_approval",
    "order_instruction",
    "auto_rebalance",
)


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


def _selected_allocation_read_only_boundary(*, write_policy: str, notes: str) -> dict[str, Any]:
    return {
        "write_policy": write_policy,
        "db_write": False,
        "registry_write": False,
        "monitoring_log_auto_write": False,
        "input_persistence": False,
        "alert_persistence": False,
        "account_connection": False,
        "broker_sync": False,
        "live_approval": False,
        "order_instruction": False,
        "auto_rebalance": False,
        "notes": notes,
    }


def _selected_decision_source_contract(
    row: dict[str, Any],
    *,
    surface: str,
    session_sources: list[str] | None = None,
) -> dict[str, Any]:
    raw_decision = dict(row.get("raw_decision") or row or {})
    decision_id = _clean_text(raw_decision.get("decision_id") or row.get("decision_id"), "")
    source_type = _clean_text(raw_decision.get("source_type") or row.get("source_type"), "")
    source_id = _clean_text(raw_decision.get("source_id") or row.get("source_id"), "")
    selected_flag = (
        raw_decision.get("selected_practical_portfolio") is True
        or row.get("selected_practical_portfolio") is True
        or _clean_text(raw_decision.get("decision_route") or row.get("decision_route"), "") == SELECTED_PRACTICAL_PORTFOLIO_ROUTE
    )
    normalized_session_sources = [
        str(source).strip()
        for source in list(session_sources or [])
        if str(source or "").strip()
    ]
    return {
        "schema_version": SELECTED_DECISION_SOURCE_CONSISTENCY_SCHEMA_VERSION,
        "surface": _clean_text(surface, "selected_dashboard"),
        "decision_id": decision_id,
        "decision_route": _clean_text(raw_decision.get("decision_route") or row.get("decision_route"), ""),
        "selected_practical_portfolio": selected_flag,
        "source_type": source_type,
        "source_id": source_id,
        "source_title": _clean_text(raw_decision.get("source_title") or row.get("source_title"), ""),
        "selection_source_id": _clean_text(raw_decision.get("selection_source_id") or row.get("selection_source_id"), ""),
        "validation_id": _clean_text(raw_decision.get("validation_id") or row.get("validation_id"), ""),
        "source_identity": f"{source_type}:{source_id}" if source_type or source_id else "",
        "durable_source": "FINAL_PORTFOLIO_SELECTION_DECISIONS_V2",
        "registry_file": getattr(FINAL_SELECTION_DECISION_V2_FILE, "name", str(FINAL_SELECTION_DECISION_V2_FILE)),
        "session_evidence_sources": normalized_session_sources,
        "evidence_scope": "final_decision_v2_plus_session_state",
        "execution_boundary": {
            "write_policy": "read_only_selected_decision_source_contract",
            "db_write": False,
            "registry_write": False,
            "monitoring_log_auto_write": False,
            "report_auto_write": False,
            "live_approval": False,
            "order_instruction": False,
            "auto_rebalance": False,
            "notes": "Selected Dashboard read models share the Final Decision V2 row and optional session-state evidence only.",
        },
    }


def _selected_decision_source_matches_contract(row: dict[str, Any], contract: dict[str, Any]) -> bool:
    if not contract:
        return False
    expected = _selected_decision_source_contract(row, surface=str(contract.get("surface") or "selected_dashboard"))
    fields = ("decision_id", "decision_route", "source_type", "source_id", "selection_source_id", "validation_id")
    return all(_clean_text(expected.get(field), "") == _clean_text(contract.get(field), "") for field in fields)


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


def _final_decision_source_row(row: dict[str, Any]) -> dict[str, Any]:
    return dict(row.get("raw_decision") or row or {})


def _handoff_check_row(
    *,
    check: str,
    status: str,
    ready: bool,
    current: Any,
    evidence: str,
    next_action: str,
) -> dict[str, Any]:
    return {
        "Check": check,
        "Status": status,
        "Ready": ready,
        "Current": _clean_text(current),
        "Evidence": _clean_text(evidence),
        "Next Action": _clean_text(next_action),
    }


def _selected_dashboard_handoff_action(row: dict[str, Any]) -> str:
    status = str(row.get("operation_status") or "")
    if status == "blocked":
        return "Final Review source row의 selected component / target weight / blocker를 보강합니다."
    if status in {"watch", "rebalance_needed", "re_review_needed"}:
        return "Selected Dashboard에서 recheck, provider evidence, timeline을 먼저 확인합니다."
    return "Operations > Selected Portfolio Dashboard에서 사후 점검을 이어갑니다."


def _selected_dashboard_handoff_rows(dashboard_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, row in enumerate(dashboard_rows):
        review_triggers = [
            str(trigger).strip()
            for trigger in list(row.get("review_triggers") or [])
            if str(trigger).strip()
        ]
        rows.append(
            {
                "Updated At": row.get("updated_at"),
                "Decision ID": row.get("decision_id"),
                "Portfolio": row.get("source_title"),
                "Dashboard Status": row.get("operation_status_label"),
                "Status Reason": row.get("status_reason"),
                "Components": row.get("component_count"),
                "Target Weight": f"{(_optional_float(row.get('target_weight_total')) or 0.0):.1f}%",
                "Benchmark": row.get("benchmark_label"),
                "Evidence Route": row.get("evidence_route"),
                "Review Cadence": row.get("review_cadence"),
                "Review Triggers": ", ".join(review_triggers) if review_triggers else "-",
                "Handoff Destination": "Operations > Selected Portfolio Dashboard",
                "Handoff Action": _selected_dashboard_handoff_action(row),
                "Live Approval": "Disabled",
                "Order": "Disabled",
                "_row_index": index,
                "_operation_status": row.get("operation_status"),
            }
        )
    return rows


def build_selected_dashboard_handoff_review(final_decision_rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize which Final Review decisions can flow into Selected Dashboard."""
    final_rows = [_final_decision_source_row(dict(row or {})) for row in list(final_decision_rows or [])]
    selected_rows = [row for row in final_rows if _is_selected_practical_portfolio(row)]
    dashboard_rows = [build_final_selected_portfolio_dashboard_row(row) for row in selected_rows]
    dashboard_rows = sorted(
        dashboard_rows,
        key=lambda row: str(row.get("updated_at") or row.get("decision_id") or ""),
        reverse=True,
    )
    status_counts = {status: 0 for status in FINAL_SELECTED_PORTFOLIO_STATUS_ORDER}
    for row in dashboard_rows:
        status = str(row.get("operation_status") or "blocked")
        if status not in status_counts:
            status_counts[status] = 0
        status_counts[status] += 1

    blocked_count = int(status_counts.get("blocked", 0))
    dashboard_row_count = len(dashboard_rows)
    monitorable_count = max(dashboard_row_count - blocked_count, 0)
    latest_selected = dashboard_rows[0] if dashboard_rows else {}

    if not final_rows:
        route = "HANDOFF_NO_FINAL_DECISION"
        next_action = "Final Review에서 최종 후보 선정 저장을 먼저 진행합니다."
        verdict = "Selected Dashboard로 넘길 최종 선정 row가 아직 없습니다."
    elif not selected_rows:
        route = "HANDOFF_NO_SELECTED_DECISION"
        next_action = "Final Review에서 SELECT_FOR_PRACTICAL_PORTFOLIO 선정 row를 저장해야 합니다."
        verdict = "저장된 Final Review row는 있지만 선정된 dashboard 대상 row가 없습니다."
    elif monitorable_count == 0:
        route = "HANDOFF_BLOCKED"
        next_action = "선정 row의 component, target weight, Final Review blocker를 보강합니다."
        verdict = "선정 row가 모두 dashboard 운영 대상으로 보기 전에 막혀 있습니다."
    else:
        route = "HANDOFF_READY"
        next_action = "Operations > Selected Portfolio Dashboard에서 recheck / readiness / provider / timeline을 이어서 확인합니다."
        verdict = "선정 row가 Selected Dashboard read-only 점검 대상으로 연결됩니다."

    checklist = [
        _handoff_check_row(
            check="Final Review decision record",
            status="PASS" if final_rows else "NEEDS_INPUT",
            ready=bool(final_rows),
            current=len(final_rows),
            evidence="Final Decision V2 rows are available" if final_rows else "No saved final decision rows",
            next_action="Use saved decisions as the handoff source." if final_rows else "Record a final review decision first.",
        ),
        _handoff_check_row(
            check="Selected route record",
            status="PASS" if selected_rows else "NEEDS_INPUT",
            ready=bool(selected_rows),
            current=len(selected_rows),
            evidence="SELECT_FOR_PRACTICAL_PORTFOLIO rows are available" if selected_rows else "No selected decision route",
            next_action=(
                "Build dashboard rows from selected decisions."
                if selected_rows
                else "Save a SELECT_FOR_PRACTICAL_PORTFOLIO decision when the candidate is actually selected."
            ),
        ),
        _handoff_check_row(
            check="Dashboard row build",
            status="PASS" if dashboard_rows else "NEEDS_INPUT",
            ready=bool(dashboard_rows),
            current=dashboard_row_count,
            evidence="Selected rows were converted to dashboard read models" if dashboard_rows else "No dashboard rows can be built yet",
            next_action="Show rows in Selected Dashboard." if dashboard_rows else "Resolve selected route availability first.",
        ),
        _handoff_check_row(
            check="Monitorable row",
            status="PASS" if monitorable_count else "BLOCKED" if selected_rows else "NEEDS_INPUT",
            ready=bool(monitorable_count),
            current=f"{monitorable_count} monitorable / {blocked_count} blocked",
            evidence="At least one selected row is not blocked" if monitorable_count else "No selected dashboard row is monitorable yet",
            next_action=(
                "Continue in Operations > Selected Portfolio Dashboard."
                if monitorable_count
                else "Fix selected component, target weight, or blocker evidence before treating the row as monitorable."
            ),
        ),
        _handoff_check_row(
            check="Execution boundary",
            status="PASS",
            ready=True,
            current="approval=False / order=False / auto_rebalance=False",
            evidence="Handoff review is read-only and does not persist monitoring state",
            next_action="Keep approval, order, and rebalance decisions outside this dashboard handoff.",
        ),
    ]

    return {
        "schema_version": SELECTED_DASHBOARD_HANDOFF_SCHEMA_VERSION,
        "route": route,
        "route_label": SELECTED_DASHBOARD_HANDOFF_ROUTE_LABELS.get(route, route),
        "verdict": verdict,
        "next_action": next_action,
        "destination": "Operations > Selected Portfolio Dashboard",
        "summary": {
            "registry_path": str(FINAL_SELECTION_DECISION_V2_FILE),
            "final_decision_count": len(final_rows),
            "selected_decision_count": len(selected_rows),
            "dashboard_row_count": dashboard_row_count,
            "monitorable_count": monitorable_count,
            "blocked_count": blocked_count,
            "status_counts": status_counts,
            "latest_selected_decision_id": latest_selected.get("decision_id") or "-",
            "latest_selected_title": latest_selected.get("source_title") or "-",
            "latest_selected_updated_at": latest_selected.get("updated_at") or "-",
            "live_approval": False,
            "order_instruction": False,
            "auto_rebalance": False,
            "monitoring_log_auto_write": False,
        },
        "rows": _selected_dashboard_handoff_rows(dashboard_rows),
        "checklist": checklist,
        "execution_boundary": {
            "write_policy": "read_only_selected_dashboard_handoff",
            "db_write": False,
            "registry_write": False,
            "report_auto_write": False,
            "monitoring_log_auto_write": False,
            "live_approval": False,
            "order_instruction": False,
            "auto_rebalance": False,
            "notes": "The handoff review reads Final Decision V2 rows and does not create dashboard state or trading actions.",
        },
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
        next_action = "주문 지시가 아니라, drift가 큰 component를 수동 운영 검토 대상으로 봅니다."
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
        "execution_boundary": _selected_allocation_read_only_boundary(
            write_policy="read_only_drift_check",
            notes="This drift check is read-only and does not write monitoring logs, broker orders, or rebalance actions.",
        ),
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
        "execution_boundary": _selected_allocation_read_only_boundary(
            write_policy="read_only_current_weight_inputs",
            notes="Value and holding inputs only estimate current weights in memory; they do not persist inputs or create broker orders.",
        ),
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
        next_action = "주문 생성이 아니라, drift가 큰 component를 수동 운영 검토 대상으로 봅니다."
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
        "execution_boundary": _selected_allocation_read_only_boundary(
            write_policy="read_only_drift_alert_preview",
            notes="This preview is read-only and does not save alert records, monitoring logs, or create orders.",
        ),
    }


def _allocation_boundary_row(
    *,
    check: str,
    status: str,
    current: Any,
    evidence: str,
    next_action: str,
    source: str,
    ready: bool | None = None,
) -> dict[str, Any]:
    if ready is None:
        ready = status == "PASS"
    return {
        "Check": check,
        "Status": status,
        "Ready": bool(ready),
        "Current": _clean_text(current),
        "Evidence": _clean_text(evidence),
        "Next Action": _clean_text(next_action),
        "Source": _clean_text(source),
    }


def _allocation_boundary_status_from_drift_route(route: str) -> str:
    if not route:
        return "OPTIONAL"
    if route == "DRIFT_ALIGNED":
        return "PASS"
    if route == "DRIFT_WATCH":
        return "WATCH"
    if route == "REBALANCE_NEEDED":
        return "BREACHED"
    return "NEEDS_INPUT"


def _allocation_boundary_status_from_alert_route(route: str) -> str:
    if not route:
        return "OPTIONAL"
    if route == "NO_ALERT":
        return "PASS"
    if route == "WATCH_ALERT":
        return "WATCH"
    if route == "REBALANCE_REVIEW_ALERT":
        return "BREACHED"
    return "NEEDS_INPUT"


def _boundary_flags_current(boundary: dict[str, Any], fields: tuple[str, ...]) -> str:
    return " / ".join(f"{field}={boundary.get(field)}" for field in fields)


def build_selected_portfolio_allocation_drift_boundary(
    row: dict[str, Any],
    *,
    weight_inputs: dict[str, Any] | None = None,
    drift_check: dict[str, Any] | None = None,
    alert_preview: dict[str, Any] | None = None,
    input_mode: str | None = None,
) -> dict[str, Any]:
    """Describe the read-only evidence boundary for optional actual allocation checks."""

    selected = dict(row or {})
    weight_input_contract = dict(weight_inputs or {})
    drift = dict(drift_check or {})
    alert = dict(alert_preview or {})
    normalized_input_mode = str(input_mode or weight_input_contract.get("input_mode") or "current_weight").strip()
    input_mode_label = FINAL_SELECTED_PORTFOLIO_VALUE_INPUT_MODE_LABELS.get(
        normalized_input_mode,
        normalized_input_mode or "manual current weight",
    )
    weight_metrics = dict(weight_input_contract.get("metrics") or {})
    drift_metrics = dict(drift.get("metrics") or {})
    alert_metrics = dict(alert.get("metrics") or {})
    weight_blockers = [str(item) for item in list(weight_input_contract.get("blockers") or []) if str(item)]
    drift_route = str(drift.get("route") or "").strip()
    alert_route = str(alert.get("alert_route") or "").strip()
    execution_boundary = _selected_allocation_read_only_boundary(
        write_policy="read_only_allocation_drift_evidence_boundary",
        notes=(
            "Allocation drift evidence uses manual/session inputs and optional DB price read assistance only; "
            "it does not persist inputs, alerts, monitoring logs, account links, broker sync, orders, or rebalance actions."
        ),
    )

    boundary_sources: list[tuple[str, dict[str, Any]]] = [
        ("boundary", execution_boundary),
    ]
    if weight_input_contract:
        boundary_sources.append(("current_weight_inputs", dict(weight_input_contract.get("execution_boundary") or {})))
    if drift:
        boundary_sources.append(("drift_check", dict(drift.get("execution_boundary") or {})))
    if alert:
        boundary_sources.append(("alert_preview", dict(alert.get("execution_boundary") or {})))

    boundary_violations = [
        f"{source}.{field}={source_boundary.get(field)}"
        for source, source_boundary in boundary_sources
        for field in _ALLOCATION_DRIFT_DISABLED_FIELDS
        if source_boundary.get(field) is not False
    ]

    input_status = "NEEDS_INPUT" if weight_blockers else "PASS"
    if not drift and not weight_input_contract:
        input_status = "OPTIONAL"
    drift_status = _allocation_boundary_status_from_drift_route(drift_route)
    alert_status = _allocation_boundary_status_from_alert_route(alert_route)
    storage_fields = ("db_write", "registry_write", "monitoring_log_auto_write", "input_persistence", "alert_persistence")
    execution_fields = ("account_connection", "broker_sync", "live_approval", "order_instruction", "auto_rebalance")
    rows = [
        _allocation_boundary_row(
            check="Current weight input source",
            status=input_status,
            ready=input_status in {"PASS", "OPTIONAL"},
            current=(
                f"{input_mode_label} / current_weight_total={weight_metrics.get('current_weight_total', '-')}"
                if weight_input_contract
                else f"{input_mode_label} / session input only"
            ),
            evidence=(
                "manual value or holding inputs are converted to weights in memory"
                if weight_input_contract
                else "manual current weight values are used only for this session check"
            ),
            next_action=(
                "입력 blocker를 해결한 뒤 drift check를 다시 계산합니다."
                if weight_blockers
                else "원시 보유값을 저장하지 않고 필요할 때 다시 입력합니다."
            ),
            source="streamlit.session_state.manual_input",
        ),
        _allocation_boundary_row(
            check="Drift evidence",
            status=drift_status,
            ready=drift_status in {"PASS", "OPTIONAL"},
            current=(
                f"{drift.get('route_label') or drift_route or '-'} / max_abs_drift={drift_metrics.get('max_abs_drift', '-')}"
            ),
            evidence=drift.get("verdict") or "Actual Allocation drift check has not been applied.",
            next_action=drift.get("next_action") or "보유 배분까지 점검할 때만 Actual Allocation check를 실행합니다.",
            source=drift.get("schema_version") or "build_selected_portfolio_drift_check",
        ),
        _allocation_boundary_row(
            check="Alert preview evidence",
            status=alert_status,
            ready=alert_status in {"PASS", "OPTIONAL"},
            current=(
                f"{alert.get('alert_route_label') or alert_route or '-'} / rows={alert_metrics.get('alert_row_count', 0)}"
            ),
            evidence=alert.get("verdict") or "Drift alert preview has not been applied.",
            next_action=alert.get("next_action") or "필요할 때만 현재 session의 Review Signals에 반영합니다.",
            source=alert.get("schema_version") or "build_selected_portfolio_drift_alert_preview",
        ),
        _allocation_boundary_row(
            check="Storage boundary",
            status="BLOCKED" if boundary_violations else "PASS",
            current=_boundary_flags_current(execution_boundary, storage_fields),
            evidence=(
                "No DB, registry, monitoring log, input, or alert persistence"
                if not boundary_violations
                else "; ".join(boundary_violations[:5])
            ),
            next_action=(
                "저장 경계 위반을 제거하기 전에는 allocation evidence를 신뢰하지 않습니다."
                if boundary_violations
                else "결과는 화면/session 신호로만 읽고 원시 입력은 다시 입력합니다."
            ),
            source="allocation_drift_evidence_boundary",
        ),
        _allocation_boundary_row(
            check="Execution boundary",
            status="BLOCKED" if boundary_violations else "PASS",
            current=_boundary_flags_current(execution_boundary, execution_fields),
            evidence=(
                "No account connection, broker sync, live approval, order, or auto rebalance"
                if not boundary_violations
                else "; ".join(boundary_violations[:5])
            ),
            next_action=(
                "주문/계좌/자동 리밸런싱 경계 위반을 제거합니다."
                if boundary_violations
                else "주문 판단은 이 화면 밖의 별도 수동 절차로만 다룹니다."
            ),
            source="allocation_drift_evidence_boundary",
        ),
    ]

    statuses = [str(item.get("Status") or "OPTIONAL") for item in rows]
    if "BLOCKED" in statuses:
        route = "ALLOCATION_DRIFT_BOUNDARY_BLOCKED"
        conclusion = "Actual Allocation evidence boundary에 저장 또는 실행 경계 위반이 있습니다."
    elif "BREACHED" in statuses:
        route = "ALLOCATION_DRIFT_BOUNDARY_BREACHED"
        conclusion = "비중 drift가 재검토 기준을 넘었지만, 이 결과는 주문이 아니라 수동 검토 신호입니다."
    elif "NEEDS_INPUT" in statuses:
        route = "ALLOCATION_DRIFT_BOUNDARY_NEEDS_INPUT"
        conclusion = "비중 근거를 읽으려면 현재 배분 입력을 먼저 보강해야 합니다."
    elif "WATCH" in statuses:
        route = "ALLOCATION_DRIFT_BOUNDARY_WATCH"
        conclusion = "비중 drift가 관찰 기준을 넘었고, 다음 점검에서 확대 여부를 확인합니다."
    elif drift or alert:
        route = "ALLOCATION_DRIFT_BOUNDARY_READY"
        conclusion = "현재 Actual Allocation evidence는 읽기 전용 session 신호로만 정상 연결되어 있습니다."
    else:
        route = "ALLOCATION_DRIFT_BOUNDARY_OPTIONAL"
        conclusion = "Actual Allocation은 선택 점검이며 실행하지 않아도 selected monitoring source를 저장하지 않습니다."

    return {
        "schema_version": SELECTED_ALLOCATION_DRIFT_BOUNDARY_SCHEMA_VERSION,
        "decision_id": selected.get("decision_id"),
        "route": route,
        "route_label": SELECTED_ALLOCATION_DRIFT_BOUNDARY_ROUTE_LABELS.get(route, route),
        "conclusion": conclusion,
        "rows": rows,
        "metrics": {
            "row_count": len(rows),
            "pass_count": sum(1 for item in rows if item.get("Status") == "PASS"),
            "watch_count": sum(1 for item in rows if item.get("Status") == "WATCH"),
            "breached_count": sum(1 for item in rows if item.get("Status") == "BREACHED"),
            "needs_input_count": sum(1 for item in rows if item.get("Status") == "NEEDS_INPUT"),
            "optional_count": sum(1 for item in rows if item.get("Status") == "OPTIONAL"),
            "boundary_violation_count": len(boundary_violations),
            "drift_route": drift_route or None,
            "alert_route": alert_route or None,
            "input_mode": normalized_input_mode,
            "raw_input_persisted": False,
        },
        "execution_boundary": execution_boundary,
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
            "Actual Allocation에서 Reflect Session Signal을 누르면 preview를 session에만 반영합니다.",
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
    session_sources: list[str] = []
    if recheck:
        session_sources.append("session_state.performance_recheck")
    if drift:
        session_sources.append("session_state.drift_check")
    if alert:
        session_sources.append("session_state.alert_preview")
    source_contract = _selected_decision_source_contract(
        selected,
        surface="monitoring_timeline",
        session_sources=session_sources,
    )
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
            "source_contract_present": True,
        },
        "source_contract": source_contract,
        "execution_boundary": {
            "write_policy": "read_only_timeline",
            "db_write": False,
            "registry_write": False,
            "report_auto_write": False,
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
    timeline_source_contract = dict(timeline.get("source_contract") or {})
    source_contract = _selected_decision_source_contract(
        selected,
        surface="continuity_check",
        session_sources=list(timeline_source_contract.get("session_evidence_sources") or []),
    )
    source_contract_matches = _selected_decision_source_matches_contract(selected, timeline_source_contract)
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
            check="Decision source consistency",
            status="PASS" if source_contract_matches else "BLOCKED",
            ready=source_contract_matches,
            current=(
                f"decision={timeline_source_contract.get('decision_id') or '-'} / "
                f"source={timeline_source_contract.get('source_type') or '-'}:{timeline_source_contract.get('source_id') or '-'}"
            ),
            evidence=(
                "Timeline, Continuity, and Dossier can use the same Final Decision V2 source"
                if source_contract_matches
                else "Timeline source contract is missing or does not match the selected decision row"
            ),
            next_action=(
                "Use this selected decision row as the source for continuity, timeline, review signals, and dossier."
                if source_contract_matches
                else "Rebuild the monitoring timeline from the currently selected dashboard row before relying on continuity."
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
            "source_contract_consistent": source_contract_matches,
        },
        "source_contract": source_contract,
        "execution_boundary": {
            "write_policy": "read_only_continuity_check",
            "db_write": False,
            "registry_write": False,
            "report_auto_write": False,
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


def _review_signal_status_label(status: str) -> str:
    return SELECTED_MONITORING_TIMELINE_STATUS_LABELS.get(status, status)


def _review_signal_overall_status(rows: list[dict[str, Any]]) -> str:
    statuses = [str(row.get("Status") or "OPTIONAL") for row in rows]
    if not statuses:
        return "NEEDS_INPUT"
    return max(statuses, key=lambda status: _TIMELINE_STATUS_RANK.get(status, 0))


def _review_signal_route(status: str) -> str:
    if status == "BREACHED":
        return "REVIEW_SIGNAL_BREACHED"
    if status == "NEEDS_INPUT":
        return "REVIEW_SIGNAL_NEEDS_INPUT"
    if status == "WATCH":
        return "REVIEW_SIGNAL_WATCH"
    return "REVIEW_SIGNAL_CLEAR"


def _review_signal_row(
    *,
    trigger: str,
    status: str,
    current_signal: Any,
    why_it_matters: str,
    suggested_action: str,
    policy_owner: str,
    source: str,
) -> dict[str, Any]:
    return {
        "Trigger": _clean_text(trigger),
        "Status": status,
        "Status Label": _review_signal_status_label(status),
        "Current Signal": _clean_text(current_signal),
        "Why It Matters": _clean_text(why_it_matters),
        "Suggested Action": _clean_text(suggested_action),
        "Policy Owner": _clean_text(policy_owner),
        "Source": _clean_text(source),
    }


def _review_signal_status_from_comparison_status(status: Any) -> str:
    normalized = str(status or "").strip().upper()
    if normalized == "PASS":
        return "CLEAR"
    if normalized == "WATCH":
        return "WATCH"
    if normalized == "BREACHED":
        return "BREACHED"
    if normalized == "NEEDS_INPUT":
        return "NEEDS_INPUT"
    return "NEEDS_INPUT"


def _review_signal_status_from_preflight_route(route: str) -> str:
    if route == "RECHECK_PREFLIGHT_READY":
        return "CLEAR"
    if route == "RECHECK_PREFLIGHT_REVIEW":
        return "WATCH"
    if route == "RECHECK_PREFLIGHT_NEEDS_DATA":
        return "NEEDS_INPUT"
    if route == "RECHECK_PREFLIGHT_BLOCKED":
        return "BREACHED"
    return "NEEDS_INPUT"


def _review_signal_status_from_provider_route(route: str) -> str:
    if route == "SELECTED_PROVIDER_READY":
        return "CLEAR"
    if route == "SELECTED_PROVIDER_REVIEW":
        return "WATCH"
    if route == "SELECTED_PROVIDER_NEEDS_DATA":
        return "NEEDS_INPUT"
    if route == "SELECTED_PROVIDER_BLOCKED":
        return "BREACHED"
    return "NEEDS_INPUT"


def build_selected_portfolio_review_signal_policy(
    row: dict[str, Any],
    *,
    recheck_result: dict[str, Any] | None = None,
    recheck_comparison: dict[str, Any] | None = None,
    recheck_preflight: dict[str, Any] | None = None,
    provider_evidence: dict[str, Any] | None = None,
    drift_check: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Translate selected monitoring read models into one read-only Review Signals policy board."""

    selected = dict(row or {})
    comparison = dict(
        recheck_comparison
        or build_selected_portfolio_recheck_comparison(selected, recheck_result=recheck_result)
    )
    preflight = dict(recheck_preflight or {})
    provider = dict(provider_evidence or {})
    drift = dict(drift_check or {})
    session_sources: list[str] = []
    if recheck_result:
        session_sources.append("session_state.performance_recheck")
    if drift:
        session_sources.append("session_state.drift_check")
    source_contract = _selected_decision_source_contract(
        selected,
        surface="review_signal_policy",
        session_sources=session_sources,
    )
    blockers = [str(blocker) for blocker in list(selected.get("blockers") or []) if str(blocker)]
    evidence_route = _clean_text(selected.get("evidence_route"), "-")
    evidence_status = "CLEAR" if not blockers and evidence_route == "READY_FOR_FINAL_DECISION" else "WATCH"
    rows: list[dict[str, Any]] = [
        _review_signal_row(
            trigger="Final Review evidence",
            status=evidence_status,
            current_signal=evidence_route,
            why_it_matters="선정 당시 검증 근거가 아직 운영 대상 조건을 만족하는지 확인합니다.",
            suggested_action=(
                "남은 blocker가 없으므로 성과와 보유 상태를 계속 점검합니다."
                if evidence_status == "CLEAR"
                else "Why Selected tab에서 남은 blocker와 검증 근거를 다시 확인합니다."
            ),
            policy_owner="Final Review evidence packet",
            source="FINAL_PORTFOLIO_SELECTION_DECISIONS_V2",
        )
    ]

    preflight_route = str(preflight.get("route") or "").strip()
    preflight_metrics = dict(preflight.get("metrics") or {})
    preflight_status = _review_signal_status_from_preflight_route(preflight_route)
    rows.append(
        _review_signal_row(
            trigger="Recheck operations preflight",
            status=preflight_status,
            current_signal=preflight.get("route_label") or preflight_route or "not evaluated",
            why_it_matters="Performance Recheck가 최신 운영 근거로 쓰일 수 있는지 실행 전 조건을 확인합니다.",
            suggested_action=(
                "Performance Recheck 결과를 comparison policy에 연결합니다."
                if preflight_status == "CLEAR"
                else "Preflight row의 replay contract, DB latest date, symbol freshness gap을 먼저 확인합니다."
            ),
            policy_owner="Recheck Operations Preflight",
            source=preflight.get("schema_version") or SELECTED_RECHECK_OPERATIONS_PREFLIGHT_SCHEMA_VERSION,
        )
    )

    provider_route = str(provider.get("route") or "").strip()
    provider_metrics = dict(provider.get("metrics") or {})
    provider_status = _review_signal_status_from_provider_route(provider_route)
    rows.append(
        _review_signal_row(
            trigger="Provider evidence freshness / coverage",
            status=provider_status,
            current_signal=provider.get("route_label") or provider_route or "not evaluated",
            why_it_matters="Provider holdings / exposure / operability evidence가 stale하거나 partial이면 선정 thesis 유지 근거가 약합니다.",
            suggested_action=(
                "Provider evidence가 현재 selected monitoring 기준을 통과했습니다."
                if provider_status == "CLEAR"
                else "Provider Evidence row에서 stale / partial / missing required area를 확인합니다."
            ),
            policy_owner="Selected Provider Evidence",
            source=provider.get("schema_version") or SELECTED_PROVIDER_EVIDENCE_SCHEMA_VERSION,
        )
    )

    comparison_rows = [dict(item or {}) for item in list(comparison.get("rows") or [])]
    for comparison_row in comparison_rows:
        rows.append(
            _review_signal_row(
                trigger=_clean_text(comparison_row.get("Check")),
                status=_review_signal_status_from_comparison_status(comparison_row.get("Status")),
                current_signal=comparison_row.get("Current"),
                why_it_matters=comparison_row.get("Evidence"),
                suggested_action=comparison_row.get("Next Action"),
                policy_owner="Recheck Comparison",
                source=comparison.get("schema_version") or SELECTED_RECHECK_COMPARISON_SCHEMA_VERSION,
            )
        )

    drift_status, drift_signal, drift_evidence, drift_action = _status_from_drift_check(drift)
    rows.append(
        _review_signal_row(
            trigger="Actual allocation drift",
            status=drift_status,
            current_signal=drift_signal,
            why_it_matters="전략 성과가 아니라 실제 또는 가정 보유금액 배분이 target allocation에서 벗어났는지 봅니다.",
            suggested_action=drift_action,
            policy_owner="Allocation Drift Check",
            source="session_state.drift_check",
        )
    )

    overall_status = _review_signal_overall_status(rows)
    route = _review_signal_route(overall_status)
    if overall_status == "BREACHED":
        conclusion = "재검토가 필요한 monitoring signal이 있습니다. BREACHED row의 Suggested Action부터 확인합니다."
    elif overall_status == "NEEDS_INPUT":
        conclusion = "Performance Recheck, preflight, provider evidence 중 입력 또는 데이터 보강이 필요한 항목이 있습니다."
    elif overall_status == "WATCH":
        conclusion = "큰 차단은 없지만 watch signal이 있습니다. 다음 점검에서 같은 항목이 악화되는지 확인합니다."
    else:
        conclusion = "현재 Review Signals 기준으로 선정 thesis와 운영 점검 상태가 유지됩니다."

    return {
        "schema_version": SELECTED_REVIEW_SIGNAL_POLICY_SCHEMA_VERSION,
        "route": route,
        "route_label": SELECTED_REVIEW_SIGNAL_POLICY_ROUTE_LABELS.get(route, route),
        "overall_status": overall_status,
        "overall_label": _review_signal_status_label(overall_status),
        "conclusion": conclusion,
        "rows": rows,
        "recheck_comparison": comparison,
        "metrics": {
            "row_count": len(rows),
            "clear_count": sum(1 for item in rows if item.get("Status") == "CLEAR"),
            "watch_count": sum(1 for item in rows if item.get("Status") == "WATCH"),
            "breached_count": sum(1 for item in rows if item.get("Status") == "BREACHED"),
            "needs_input_count": sum(1 for item in rows if item.get("Status") == "NEEDS_INPUT"),
            "optional_count": sum(1 for item in rows if item.get("Status") == "OPTIONAL"),
            "stored_trigger_count": len(list(selected.get("review_triggers") or [])),
            "preflight_route": preflight_route or None,
            "provider_route": provider_route or None,
            "comparison_route": comparison.get("route"),
            "comparison_overall_status": comparison.get("overall_status"),
            "recheck_present": bool(dict(comparison.get("metrics") or {}).get("recheck_present")),
            "preflight_missing_symbol_count": preflight_metrics.get("missing_symbol_count", 0),
            "preflight_stale_symbol_count": preflight_metrics.get("stale_symbol_count", 0),
            "provider_stale_count": provider_metrics.get("stale_count", 0),
            "provider_partial_coverage_count": provider_metrics.get("partial_coverage_count", 0),
            "provider_needs_input_count": provider_metrics.get("needs_input_count", 0),
            "source_contract_present": True,
        },
        "source_contract": source_contract,
        "execution_boundary": {
            "write_policy": "read_only_review_signal_policy",
            "db_write": False,
            "registry_write": False,
            "report_auto_write": False,
            "monitoring_log_auto_write": False,
            "alert_persistence": False,
            "live_approval": False,
            "order_instruction": False,
            "auto_rebalance": False,
            "notes": "Review signal policy reads existing selected decision, preflight, provider, comparison, and optional session drift evidence; it does not save monitoring records.",
        },
    }


def _readiness_check_row(
    *,
    check: str,
    status: str,
    current: Any,
    evidence: str,
    next_action: str,
) -> dict[str, Any]:
    return {
        "Check": check,
        "Status": status,
        "Ready": status == "PASS",
        "Current": _clean_text(current),
        "Evidence": _clean_text(evidence),
        "Next Action": _clean_text(next_action),
    }


def _safe_date_compare(left: Any, right: Any) -> int | None:
    left_ts = pd.to_datetime(left, errors="coerce")
    right_ts = pd.to_datetime(right, errors="coerce")
    if pd.isna(left_ts) or pd.isna(right_ts):
        return None
    if left_ts < right_ts:
        return -1
    if left_ts > right_ts:
        return 1
    return 0


def _merge_non_empty(target: dict[str, Any], source: dict[str, Any]) -> None:
    for key, value in source.items():
        if value is None or value == "" or value == []:
            continue
        target[key] = value


def _component_embedded_candidate_row(component: dict[str, Any], identity: str) -> dict[str, Any]:
    replay_contract = dict(component.get("replay_contract") or {})
    settings_snapshot = dict(replay_contract.get("settings_snapshot") or {})
    nested_contract = dict(replay_contract.get("contract") or {})
    component_contract = dict(component.get("contract") or {})
    contract: dict[str, Any] = {}
    _merge_non_empty(contract, settings_snapshot)
    _merge_non_empty(contract, nested_contract)
    _merge_non_empty(contract, component_contract)

    tickers = _provider_symbol_candidates_from_value(contract.get("tickers"))
    if not tickers:
        tickers = _provider_symbol_candidates_from_value(component.get("universe"))
    if not tickers:
        tickers = _provider_symbol_candidates_from_value(settings_snapshot.get("tickers"))
    if tickers:
        contract["tickers"] = tickers

    benchmark = (
        contract.get("benchmark_ticker")
        or settings_snapshot.get("benchmark_ticker")
        or component.get("benchmark")
    )
    if benchmark:
        contract["benchmark_ticker"] = benchmark

    period = dict(component.get("period") or {})
    if component.get("period_start") and not period.get("start"):
        period["start"] = component.get("period_start")
    if component.get("period_end") and not period.get("end"):
        period["end"] = component.get("period_end")
    if contract.get("start") and not period.get("start"):
        period["start"] = contract.get("start")
    if contract.get("end") and not period.get("end"):
        period["end"] = contract.get("end")

    execution_context = dict(component.get("execution_context") or {})
    if period.get("start") and not execution_context.get("start"):
        execution_context["start"] = period.get("start")
    if period.get("end") and not execution_context.get("end"):
        execution_context["end"] = period.get("end")
    if contract.get("timeframe") and not execution_context.get("timeframe"):
        execution_context["timeframe"] = contract.get("timeframe")

    strategy_key = component.get("strategy_key") or contract.get("strategy_key") or settings_snapshot.get("strategy_key")
    strategy_family = strategy_key or component.get("strategy_family")
    compare_prefill = dict(component.get("compare_prefill") or {})
    if strategy_key:
        compare_prefill["strategy_key"] = strategy_key

    if not contract and not tickers:
        return {}

    return {
        "registry_id": component.get("registry_id") or identity,
        "title": component.get("title") or component.get("strategy_name") or identity,
        "strategy_family": strategy_family,
        "strategy_name": component.get("strategy_name") or component.get("title") or identity,
        "contract": contract,
        "execution_context": execution_context,
        "period": period,
        "compare_prefill": compare_prefill,
    }


def _resolve_selected_recheck_contracts(
    row: dict[str, Any],
    *,
    candidate_rows_by_id: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    raw_decision = dict(row.get("raw_decision") or row)
    active_components = _active_components(raw_decision)
    if candidate_rows_by_id is None:
        try:
            candidate_rows = _find_candidate_rows_by_registry_id()
            candidate_load_error = ""
        except Exception as exc:  # pragma: no cover - registry read errors depend on local workspace state
            candidate_rows = {}
            candidate_load_error = str(exc)
    else:
        candidate_rows = dict(candidate_rows_by_id)
        candidate_load_error = ""

    try:
        from .candidate_library import build_candidate_replay_payload

        replay_builder_error = ""
    except Exception as exc:  # pragma: no cover - defensive import boundary
        build_candidate_replay_payload = None  # type: ignore[assignment]
        replay_builder_error = str(exc)

    contracts: list[dict[str, Any]] = []
    missing_contracts: list[str] = []
    invalid_contracts: list[str] = []
    embedded_contract_count = 0
    candidate_registry_fallback_count = 0

    for index, component in enumerate(active_components):
        component_row = dict(component or {})
        identity = _component_identity(component_row, index)
        title = _clean_text(component_row.get("title") or identity)
        registry_id = _clean_text(component_row.get("registry_id"), "")
        current_row = dict(candidate_rows.get(registry_id) or {}) if registry_id else {}
        embedded_row = _component_embedded_candidate_row(component_row, identity)
        payload: dict[str, Any] | None = None
        resolved_row: dict[str, Any] = {}
        source = "unresolved"
        evidence_parts: list[str] = []

        if build_candidate_replay_payload is None:
            evidence_parts.append("replay helper import 실패")
        else:
            if embedded_row:
                try:
                    payload = build_candidate_replay_payload(embedded_row)
                    resolved_row = embedded_row
                    source = "final_decision_embedded_contract"
                    embedded_contract_count += 1
                    evidence_parts.append("Final Review selected component embedded contract is replayable.")
                except Exception as exc:
                    evidence_parts.append(f"embedded_contract_error={exc}")
            if payload is None and current_row:
                try:
                    payload = build_candidate_replay_payload(current_row)
                    resolved_row = current_row
                    source = "candidate_registry_fallback"
                    candidate_registry_fallback_count += 1
                    evidence_parts.append("Current Candidate Registry fallback contract is replayable.")
                except Exception as exc:
                    evidence_parts.append(f"candidate_registry_error={exc}")

        if payload is None:
            if not registry_id and not embedded_row:
                missing_contracts.append(f"{identity}: registry_id 및 embedded replay contract 없음")
            elif registry_id and not current_row and not embedded_row:
                missing_contracts.append(f"{identity}: current candidate row 및 embedded replay contract 없음")
            else:
                invalid_contracts.append(f"{identity}: {'; '.join(evidence_parts) or 'replay contract invalid'}")
            contracts.append(
                {
                    "component": component_row,
                    "identity": identity,
                    "title": title,
                    "registry_id": registry_id,
                    "source": source,
                    "status": "BLOCKED",
                    "payload": {},
                    "candidate_row": resolved_row,
                    "evidence": "; ".join(evidence_parts) or "No replayable selected component contract was resolved.",
                }
            )
            continue

        contracts.append(
            {
                "component": component_row,
                "identity": identity,
                "title": title,
                "registry_id": registry_id,
                "source": source,
                "status": "PASS",
                "payload": payload,
                "candidate_row": resolved_row,
                "evidence": "; ".join(evidence_parts) or "Replay contract is available.",
            }
        )

    return {
        "contracts": contracts,
        "active_component_count": len(active_components),
        "valid_contract_count": sum(1 for item in contracts if item.get("status") == "PASS"),
        "embedded_contract_count": embedded_contract_count,
        "candidate_registry_fallback_count": candidate_registry_fallback_count,
        "missing_contracts": missing_contracts,
        "invalid_contracts": invalid_contracts,
        "candidate_load_error": candidate_load_error,
        "replay_builder_error": replay_builder_error,
    }


def build_selected_portfolio_recheck_readiness(
    row: dict[str, Any],
    *,
    latest_market_result: dict[str, Any] | None = None,
    candidate_rows_by_id: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build a read-only preflight view for Selected Dashboard Performance Recheck inputs."""

    selected = dict(row or {})
    raw_decision = dict(selected.get("raw_decision") or selected)
    active_components = _active_components(raw_decision)
    target_weight_total = _target_weight_total(raw_decision, active_components)
    baseline = _baseline_snapshot(raw_decision)
    decision_route = _clean_text(raw_decision.get("decision_route") or selected.get("decision_route"), "")
    selected_flag = (
        raw_decision.get("selected_practical_portfolio") is True
        or selected.get("selected_practical_portfolio") is True
        or decision_route == SELECTED_PRACTICAL_PORTFOLIO_ROUTE
    )
    rows: list[dict[str, Any]] = []

    component_contract_ready = selected_flag and bool(active_components) and abs(target_weight_total - 100.0) <= 0.01
    rows.append(
        _readiness_check_row(
            check="Selected component contract",
            status="PASS" if component_contract_ready else "BLOCKED",
            current=f"selected={selected_flag} / components={len(active_components)} / target={target_weight_total:.2f}%",
            evidence=(
                "Selected route, active components, and target weight contract are available."
                if component_contract_ready
                else "Selected route, active components, or target weight contract is incomplete."
            ),
            next_action=(
                "Use this component contract for Performance Recheck."
                if component_contract_ready
                else "Fix the Final Review selected row before running Performance Recheck."
            ),
        )
    )

    contract_evidence = _resolve_selected_recheck_contracts(row, candidate_rows_by_id=candidate_rows_by_id)
    valid_contracts = int(contract_evidence.get("valid_contract_count") or 0)
    missing_contracts = [str(item) for item in list(contract_evidence.get("missing_contracts") or [])]
    invalid_contracts = [str(item) for item in list(contract_evidence.get("invalid_contracts") or [])]
    candidate_load_error = str(contract_evidence.get("candidate_load_error") or "")
    replay_builder_error = str(contract_evidence.get("replay_builder_error") or "")
    embedded_contract_count = int(contract_evidence.get("embedded_contract_count") or 0)
    candidate_registry_fallback_count = int(contract_evidence.get("candidate_registry_fallback_count") or 0)
    replay_symbols: set[str] = set()
    replay_benchmarks: set[str] = set()
    replay_periods: list[str] = []

    for contract_row in list(contract_evidence.get("contracts") or []):
        if contract_row.get("status") != "PASS":
            continue
        payload = dict(contract_row.get("payload") or {})
        component = dict(contract_row.get("component") or {})
        replay_symbols.update(str(symbol).strip().upper() for symbol in list(payload.get("tickers") or []) if str(symbol).strip())
        benchmark = str(payload.get("benchmark_ticker") or component.get("benchmark") or "").strip().upper()
        if benchmark:
            replay_benchmarks.add(benchmark)
        replay_periods.append(f"{payload.get('start') or '-'} -> {payload.get('end') or '-'}")

    expected_contracts = len(active_components)
    if replay_builder_error:
        replay_status = "NEEDS_INPUT"
    elif candidate_load_error and valid_contracts < expected_contracts:
        replay_status = "NEEDS_INPUT"
    elif expected_contracts <= 0:
        replay_status = "BLOCKED"
    elif valid_contracts == expected_contracts:
        replay_status = "PASS"
    elif valid_contracts > 0:
        replay_status = "REVIEW"
    else:
        replay_status = "BLOCKED"
    replay_evidence_parts = []
    if embedded_contract_count:
        replay_evidence_parts.append(f"embedded_contracts={embedded_contract_count}")
    if candidate_registry_fallback_count:
        replay_evidence_parts.append(f"candidate_registry_fallbacks={candidate_registry_fallback_count}")
    if replay_symbols:
        replay_evidence_parts.append(f"symbols={len(replay_symbols)}")
    if replay_benchmarks:
        replay_evidence_parts.append("benchmarks=" + ", ".join(sorted(replay_benchmarks)))
    if missing_contracts:
        replay_evidence_parts.append("missing=" + "; ".join(missing_contracts[:3]))
    if invalid_contracts:
        replay_evidence_parts.append("invalid=" + "; ".join(invalid_contracts[:3]))
    if candidate_load_error:
        replay_evidence_parts.append(f"candidate_load_error={candidate_load_error}")
    if replay_builder_error:
        replay_evidence_parts.append(f"replay_builder_error={replay_builder_error}")
    rows.append(
        _readiness_check_row(
            check="Selected replay contract",
            status=replay_status,
            current=f"{valid_contracts}/{expected_contracts} contracts",
            evidence=" / ".join(replay_evidence_parts) if replay_evidence_parts else "Selected replay contracts are available.",
            next_action=(
                "Performance Recheck can rebuild selected component payloads."
                if replay_status == "PASS"
                else "Review partial replay contract coverage before relying on recheck output."
                if replay_status == "REVIEW"
                else "Fix Final Review embedded contracts, Candidate Registry fallback, or selected component registry ids."
                if replay_status == "BLOCKED"
                else "Resolve candidate registry or replay helper availability before running recheck."
            ),
        )
    )

    latest_result = dict(latest_market_result) if latest_market_result is not None else load_selected_portfolio_latest_market_date()
    latest_status = _clean_text(latest_result.get("status"), "")
    latest_market_date = _date_text(latest_result.get("latest_market_date"))
    baseline_start = _date_text(baseline.get("baseline_start"))
    baseline_end = _date_text(baseline.get("baseline_end"))
    latest_vs_baseline = _safe_date_compare(latest_market_date, baseline_end)
    if latest_status == "error" or latest_result.get("error"):
        latest_row_status = "NEEDS_INPUT"
    elif not latest_market_date:
        latest_row_status = "NEEDS_INPUT"
    elif not baseline_end:
        latest_row_status = "REVIEW"
    elif latest_vs_baseline is not None and latest_vs_baseline > 0:
        latest_row_status = "PASS"
    else:
        latest_row_status = "REVIEW"
    rows.append(
        _readiness_check_row(
            check="DB latest market date",
            status=latest_row_status,
            current=f"latest={latest_market_date or '-'} / baseline_end={baseline_end or '-'}",
            evidence=(
                str(latest_result.get("error"))
                if latest_result.get("error")
                else "Latest DB market date extends beyond the selected baseline."
                if latest_row_status == "PASS"
                else "Latest DB market date is unavailable or does not extend beyond the selected baseline."
            ),
            next_action=(
                "Use DB latest market date as the default recheck end date."
                if latest_row_status == "PASS"
                else "Refresh OHLCV data or check DB connectivity before treating recheck as latest evidence."
                if latest_row_status == "NEEDS_INPUT"
                else "Confirm whether the selected baseline already includes the latest DB market date."
            ),
        )
    )

    default_start = baseline_start or "2016-01-01"
    default_end = latest_market_date or baseline_end or date.today().isoformat()
    start_vs_end = _safe_date_compare(default_start, default_end)
    if start_vs_end is None:
        period_status = "NEEDS_INPUT"
    elif start_vs_end > 0:
        period_status = "BLOCKED"
    elif latest_row_status == "NEEDS_INPUT":
        period_status = "NEEDS_INPUT"
    elif latest_row_status == "REVIEW":
        period_status = "REVIEW"
    else:
        period_status = "PASS"
    rows.append(
        _readiness_check_row(
            check="Default recheck period",
            status=period_status,
            current=f"{default_start} -> {default_end}",
            evidence=(
                f"baseline={baseline_start or '-'} -> {baseline_end or '-'}"
                + (f" / replay_periods={'; '.join(replay_periods[:3])}" if replay_periods else "")
            ),
            next_action=(
                "Default period can be used, or the user can choose a different recheck range."
                if period_status == "PASS"
                else "Adjust start/end dates or refresh DB latest market data before recheck."
            ),
        )
    )

    rows.append(
        _readiness_check_row(
            check="Execution and storage boundary",
            status="PASS",
            current="read_only / no auto write / no order",
            evidence="Readiness only inspects existing selected row, registry contract, and DB latest date.",
            next_action="Run Performance Recheck manually when ready; no monitoring log or order is created.",
        )
    )

    blocked = [item for item in rows if item.get("Status") == "BLOCKED"]
    needs_input = [item for item in rows if item.get("Status") == "NEEDS_INPUT"]
    review = [item for item in rows if item.get("Status") == "REVIEW"]
    if blocked:
        route = "RECHECK_READINESS_BLOCKED"
        conclusion = "Performance Recheck 실행 전 차단 항목을 먼저 해결해야 합니다."
    elif needs_input:
        route = "RECHECK_READINESS_NEEDS_DATA"
        conclusion = "Performance Recheck를 최신 DB 근거로 보려면 데이터 / helper 입력을 확인해야 합니다."
    elif review:
        route = "RECHECK_READINESS_REVIEW"
        conclusion = "실행은 가능하지만 최신성 또는 일부 근거를 확인해야 합니다."
    else:
        route = "RECHECK_READINESS_READY"
        conclusion = "Performance Recheck를 실행할 기본 데이터와 contract가 준비되어 있습니다."

    return {
        "schema_version": SELECTED_RECHECK_READINESS_SCHEMA_VERSION,
        "route": route,
        "route_label": SELECTED_RECHECK_READINESS_ROUTE_LABELS.get(route, route),
        "conclusion": conclusion,
        "rows": rows,
        "metrics": {
            "check_count": len(rows),
            "pass_count": sum(1 for item in rows if item.get("Status") == "PASS"),
            "review_count": len(review),
            "needs_input_count": len(needs_input),
            "blocked_count": len(blocked),
            "active_component_count": len(active_components),
            "replay_contract_count": valid_contracts,
            "embedded_replay_contract_count": embedded_contract_count,
            "candidate_registry_fallback_count": candidate_registry_fallback_count,
            "missing_replay_contract_count": len(missing_contracts),
            "invalid_replay_contract_count": len(invalid_contracts),
            "symbol_count": len(replay_symbols),
            "benchmark_count": len(replay_benchmarks),
            "latest_market_date": latest_market_date,
            "baseline_end": baseline_end,
        },
        "execution_boundary": {
            "write_policy": "read_only_recheck_readiness",
            "db_write": False,
            "registry_write": False,
            "monitoring_log_auto_write": False,
            "live_approval": False,
            "order_instruction": False,
            "auto_rebalance": False,
            "notes": "Readiness checks existing DB and registry evidence only; it does not ingest data or save monitoring records.",
        },
    }


def _selected_recheck_symbols_from_contracts(
    row: dict[str, Any],
    *,
    candidate_rows_by_id: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    contract_evidence = _resolve_selected_recheck_contracts(row, candidate_rows_by_id=candidate_rows_by_id)
    symbol_roles: dict[str, set[str]] = {}
    symbol_components: dict[str, set[str]] = {}
    for contract_row in list(contract_evidence.get("contracts") or []):
        if contract_row.get("status") != "PASS":
            continue
        payload = dict(contract_row.get("payload") or {})
        component = dict(contract_row.get("component") or {})
        title = _clean_text(contract_row.get("title") or component.get("title") or contract_row.get("identity"))
        for symbol in list(payload.get("tickers") or []):
            cleaned = str(symbol or "").strip().upper()
            if not cleaned:
                continue
            symbol_roles.setdefault(cleaned, set()).add("portfolio")
            symbol_components.setdefault(cleaned, set()).add(title)
        benchmark = str(payload.get("benchmark_ticker") or component.get("benchmark") or "").strip().upper()
        if benchmark:
            symbol_roles.setdefault(benchmark, set()).add("benchmark")
            symbol_components.setdefault(benchmark, set()).add(title)

    return {
        "symbols": sorted(symbol_roles),
        "symbol_roles": {symbol: sorted(roles) for symbol, roles in symbol_roles.items()},
        "symbol_components": {symbol: sorted(components) for symbol, components in symbol_components.items()},
        "active_component_count": contract_evidence.get("active_component_count", 0),
        "valid_contract_count": contract_evidence.get("valid_contract_count", 0),
        "embedded_contract_count": contract_evidence.get("embedded_contract_count", 0),
        "candidate_registry_fallback_count": contract_evidence.get("candidate_registry_fallback_count", 0),
        "missing_contracts": list(contract_evidence.get("missing_contracts") or []),
        "invalid_contracts": list(contract_evidence.get("invalid_contracts") or []),
        "candidate_load_error": contract_evidence.get("candidate_load_error", ""),
        "replay_builder_error": contract_evidence.get("replay_builder_error", ""),
    }


def _symbol_freshness_status(days_lag: int | None, row_count: int | None) -> str:
    if row_count is None or row_count <= 0 or days_lag is None:
        return "MISSING"
    if days_lag <= 2:
        return "PASS"
    if days_lag <= 5:
        return "WATCH"
    return "STALE"


def build_selected_portfolio_recheck_symbol_freshness(
    row: dict[str, Any],
    *,
    latest_market_result: dict[str, Any] | None = None,
    candidate_rows_by_id: dict[str, dict[str, Any]] | None = None,
    freshness_df: pd.DataFrame | None = None,
    timeframe: str = "1d",
) -> dict[str, Any]:
    """Check selected recheck ticker price freshness without ingesting data or writing monitoring records."""

    latest_result = dict(latest_market_result) if latest_market_result is not None else load_selected_portfolio_latest_market_date()
    latest_market_date = _date_text(latest_result.get("latest_market_date"))
    contract_evidence = _selected_recheck_symbols_from_contracts(row, candidate_rows_by_id=candidate_rows_by_id)
    symbols = [str(symbol) for symbol in list(contract_evidence.get("symbols") or []) if str(symbol)]
    symbol_roles = dict(contract_evidence.get("symbol_roles") or {})
    symbol_components = dict(contract_evidence.get("symbol_components") or {})
    blocker_messages = [
        str(item)
        for item in (
            list(contract_evidence.get("missing_contracts") or [])
            + list(contract_evidence.get("invalid_contracts") or [])
        )
        if str(item)
    ]
    if contract_evidence.get("candidate_load_error"):
        blocker_messages.append(str(contract_evidence.get("candidate_load_error")))
    if contract_evidence.get("replay_builder_error"):
        blocker_messages.append(str(contract_evidence.get("replay_builder_error")))

    if not symbols:
        route = "SYMBOL_FRESHNESS_BLOCKED"
        rows = [
            {
                "Symbol": "-",
                "Role": "-",
                "Components": "-",
                "Status": "BLOCKED",
                "Latest Date": "-",
                "Market Date": latest_market_date or "-",
                "Days Lag": None,
                "Row Count": None,
                "Evidence": "; ".join(blocker_messages[:3]) if blocker_messages else "No replay symbols were resolved.",
                "Next Action": "Fix selected component replay contracts before checking DB price freshness.",
            }
        ]
        return {
            "schema_version": SELECTED_RECHECK_SYMBOL_FRESHNESS_SCHEMA_VERSION,
            "route": route,
            "route_label": SELECTED_RECHECK_SYMBOL_FRESHNESS_ROUTE_LABELS[route],
            "conclusion": "symbol freshness를 확인할 replay symbol이 없습니다.",
            "rows": rows,
            "metrics": {
                "symbol_count": 0,
                "pass_count": 0,
                "watch_count": 0,
                "stale_count": 0,
                "missing_count": 0,
                "blocked_count": 1,
                "latest_market_date": latest_market_date,
                "timeframe": timeframe,
            },
            "execution_boundary": {
                "write_policy": "read_only_symbol_freshness",
                "db_write": False,
                "registry_write": False,
                "monitoring_log_auto_write": False,
                "live_approval": False,
                "order_instruction": False,
                "auto_rebalance": False,
                "notes": "Symbol freshness reads DB price metadata only; it does not ingest data or save monitoring records.",
            },
        }

    if latest_result.get("status") == "error" or latest_result.get("error") or not latest_market_date:
        route = "SYMBOL_FRESHNESS_NEEDS_DATA"
        rows = [
            {
                "Symbol": symbol,
                "Role": ", ".join(symbol_roles.get(symbol) or []),
                "Components": ", ".join(symbol_components.get(symbol) or []),
                "Status": "NEEDS_INPUT",
                "Latest Date": "-",
                "Market Date": latest_market_date or "-",
                "Days Lag": None,
                "Row Count": None,
                "Evidence": str(latest_result.get("error") or "DB latest market date is unavailable."),
                "Next Action": "Check DB connectivity or refresh OHLCV data before using latest recheck evidence.",
            }
            for symbol in symbols
        ]
        return {
            "schema_version": SELECTED_RECHECK_SYMBOL_FRESHNESS_SCHEMA_VERSION,
            "route": route,
            "route_label": SELECTED_RECHECK_SYMBOL_FRESHNESS_ROUTE_LABELS[route],
            "conclusion": "DB 최신 시장일을 확인할 수 없어 symbol freshness를 판단할 수 없습니다.",
            "rows": rows,
            "metrics": {
                "symbol_count": len(symbols),
                "pass_count": 0,
                "watch_count": 0,
                "stale_count": 0,
                "missing_count": 0,
                "blocked_count": 0,
                "needs_input_count": len(symbols),
                "latest_market_date": latest_market_date,
                "timeframe": timeframe,
            },
            "execution_boundary": {
                "write_policy": "read_only_symbol_freshness",
                "db_write": False,
                "registry_write": False,
                "monitoring_log_auto_write": False,
                "live_approval": False,
                "order_instruction": False,
                "auto_rebalance": False,
                "notes": "Symbol freshness reads DB price metadata only; it does not ingest data or save monitoring records.",
            },
        }

    try:
        if freshness_df is None:
            from finance.loaders.price import load_price_freshness_summary

            freshness = load_price_freshness_summary(symbols=symbols, end=latest_market_date, timeframe=timeframe)
        else:
            freshness = freshness_df.copy()
        loader_error = ""
    except Exception as exc:  # pragma: no cover - depends on local MySQL availability
        freshness = pd.DataFrame()
        loader_error = str(exc)

    if loader_error:
        route = "SYMBOL_FRESHNESS_NEEDS_DATA"
        rows = [
            {
                "Symbol": symbol,
                "Role": ", ".join(symbol_roles.get(symbol) or []),
                "Components": ", ".join(symbol_components.get(symbol) or []),
                "Status": "NEEDS_INPUT",
                "Latest Date": "-",
                "Market Date": latest_market_date,
                "Days Lag": None,
                "Row Count": None,
                "Evidence": loader_error,
                "Next Action": "Check price loader / DB connectivity, then refresh this view.",
            }
            for symbol in symbols
        ]
    else:
        freshness_by_symbol: dict[str, dict[str, Any]] = {}
        if isinstance(freshness, pd.DataFrame) and not freshness.empty:
            for record in freshness.to_dict("records"):
                symbol = str(record.get("symbol") or "").strip().upper()
                if symbol:
                    freshness_by_symbol[symbol] = dict(record)

        rows = []
        market_ts = pd.to_datetime(latest_market_date, errors="coerce")
        for symbol in symbols:
            record = freshness_by_symbol.get(symbol, {})
            latest_date = _date_text(record.get("latest_date"))
            row_count_float = _optional_float(record.get("row_count"))
            row_count = int(row_count_float) if row_count_float is not None else None
            symbol_ts = pd.to_datetime(latest_date, errors="coerce")
            days_lag: int | None = None
            if not pd.isna(market_ts) and not pd.isna(symbol_ts):
                days_lag = int((market_ts - symbol_ts).days)
            status = _symbol_freshness_status(days_lag, row_count)
            rows.append(
                {
                    "Symbol": symbol,
                    "Role": ", ".join(symbol_roles.get(symbol) or []),
                    "Components": ", ".join(symbol_components.get(symbol) or []),
                    "Status": status,
                    "Latest Date": latest_date or "-",
                    "Market Date": latest_market_date,
                    "Days Lag": days_lag,
                    "Row Count": row_count,
                    "Evidence": (
                        "Symbol price history is recent enough for recheck preflight."
                        if status == "PASS"
                        else "Symbol is slightly behind latest DB market date."
                        if status == "WATCH"
                        else "Symbol price history is stale versus latest DB market date."
                        if status == "STALE"
                        else "Symbol price history is missing."
                    ),
                    "Next Action": (
                        "Use this symbol in Performance Recheck."
                        if status == "PASS"
                        else "Review whether this lag is expected before relying on latest recheck output."
                        if status == "WATCH"
                        else "Refresh OHLCV data for this symbol before treating recheck as latest evidence."
                    ),
                }
            )

    pass_count = sum(1 for item in rows if item.get("Status") == "PASS")
    watch_count = sum(1 for item in rows if item.get("Status") == "WATCH")
    stale_count = sum(1 for item in rows if item.get("Status") == "STALE")
    missing_count = sum(1 for item in rows if item.get("Status") == "MISSING")
    needs_input_count = sum(1 for item in rows if item.get("Status") == "NEEDS_INPUT")
    if missing_count:
        route = "SYMBOL_FRESHNESS_MISSING"
        conclusion = "일부 symbol의 가격 이력이 DB에서 누락되어 recheck 신뢰도가 낮습니다."
    elif stale_count:
        route = "SYMBOL_FRESHNESS_STALE"
        conclusion = "일부 symbol 가격이 최신 DB 시장일보다 오래되어 recheck 전 데이터 보강이 필요합니다."
    elif needs_input_count:
        route = "SYMBOL_FRESHNESS_NEEDS_DATA"
        conclusion = "가격 DB freshness를 확인하지 못했습니다."
    elif watch_count:
        route = "SYMBOL_FRESHNESS_WATCH"
        conclusion = "일부 symbol이 최신 DB 시장일보다 약간 뒤처져 있습니다."
    else:
        route = "SYMBOL_FRESHNESS_READY"
        conclusion = "선정 포트폴리오 recheck symbol의 가격 최신성이 준비되어 있습니다."

    return {
        "schema_version": SELECTED_RECHECK_SYMBOL_FRESHNESS_SCHEMA_VERSION,
        "route": route,
        "route_label": SELECTED_RECHECK_SYMBOL_FRESHNESS_ROUTE_LABELS.get(route, route),
        "conclusion": conclusion,
        "rows": rows,
        "metrics": {
            "symbol_count": len(symbols),
            "pass_count": pass_count,
            "watch_count": watch_count,
            "stale_count": stale_count,
            "missing_count": missing_count,
            "needs_input_count": needs_input_count,
            "blocked_count": 0,
            "portfolio_symbol_count": sum(1 for symbol in symbols if "portfolio" in set(symbol_roles.get(symbol) or [])),
            "benchmark_symbol_count": sum(1 for symbol in symbols if "benchmark" in set(symbol_roles.get(symbol) or [])),
            "latest_market_date": latest_market_date,
            "timeframe": timeframe,
        },
        "execution_boundary": {
            "write_policy": "read_only_symbol_freshness",
            "db_write": False,
            "registry_write": False,
            "monitoring_log_auto_write": False,
            "live_approval": False,
            "order_instruction": False,
            "auto_rebalance": False,
            "notes": "Symbol freshness reads DB price metadata only; it does not ingest data or save monitoring records.",
        },
    }


def _preflight_status_from_readiness(route: str) -> str:
    if route == "RECHECK_READINESS_READY":
        return "PASS"
    if route == "RECHECK_READINESS_REVIEW":
        return "REVIEW"
    if route == "RECHECK_READINESS_NEEDS_DATA":
        return "NEEDS_INPUT"
    if route == "RECHECK_READINESS_BLOCKED":
        return "BLOCKED"
    return "NEEDS_INPUT"


def _preflight_status_from_freshness(route: str) -> str:
    if route == "SYMBOL_FRESHNESS_READY":
        return "PASS"
    if route in {"SYMBOL_FRESHNESS_WATCH", "SYMBOL_FRESHNESS_STALE"}:
        return "REVIEW"
    if route in {"SYMBOL_FRESHNESS_MISSING", "SYMBOL_FRESHNESS_NEEDS_DATA"}:
        return "NEEDS_INPUT"
    if route == "SYMBOL_FRESHNESS_BLOCKED":
        return "BLOCKED"
    return "NEEDS_INPUT"


def _preflight_row(
    *,
    area: str,
    status: str,
    current: Any,
    evidence: str,
    next_action: str,
) -> dict[str, Any]:
    return {
        "Area": area,
        "Status": status,
        "Ready": status == "PASS",
        "Current": _clean_text(current),
        "Evidence": _clean_text(evidence),
        "Next Action": _clean_text(next_action),
    }


def build_selected_portfolio_recheck_operations_preflight(
    row: dict[str, Any],
    *,
    latest_market_result: dict[str, Any] | None = None,
    candidate_rows_by_id: dict[str, dict[str, Any]] | None = None,
    freshness_df: pd.DataFrame | None = None,
    timeframe: str = "1d",
) -> dict[str, Any]:
    """Combine recheck contract readiness and price freshness into one read-only operations gate."""

    readiness = build_selected_portfolio_recheck_readiness(
        row,
        latest_market_result=latest_market_result,
        candidate_rows_by_id=candidate_rows_by_id,
    )
    symbol_freshness = build_selected_portfolio_recheck_symbol_freshness(
        row,
        latest_market_result=latest_market_result,
        candidate_rows_by_id=candidate_rows_by_id,
        freshness_df=freshness_df,
        timeframe=timeframe,
    )
    readiness_route = str(readiness.get("route") or "")
    freshness_route = str(symbol_freshness.get("route") or "")
    readiness_metrics = dict(readiness.get("metrics") or {})
    freshness_metrics = dict(symbol_freshness.get("metrics") or {})

    rows = [
        _preflight_row(
            area="Recheck Readiness",
            status=_preflight_status_from_readiness(readiness_route),
            current=readiness.get("route_label") or readiness_route,
            evidence=str(readiness.get("conclusion") or "-"),
            next_action=(
                "Use the resolved replay contracts and DB latest market date for Performance Recheck."
                if readiness_route == "RECHECK_READINESS_READY"
                else "Resolve readiness review / data / blocker rows before treating the next recheck as latest evidence."
            ),
        ),
        _preflight_row(
            area="Symbol Freshness",
            status=_preflight_status_from_freshness(freshness_route),
            current=(
                f"symbols={freshness_metrics.get('symbol_count', 0)} / "
                f"missing={freshness_metrics.get('missing_count', 0)} / "
                f"stale={freshness_metrics.get('stale_count', 0)} / "
                f"watch={freshness_metrics.get('watch_count', 0)}"
            ),
            evidence=str(symbol_freshness.get("conclusion") or "-"),
            next_action=(
                "Use these symbols for Performance Recheck."
                if freshness_route == "SYMBOL_FRESHNESS_READY"
                else "Refresh or verify DB price metadata before treating recheck output as current."
            ),
        ),
        _preflight_row(
            area="Execution Boundary",
            status="PASS",
            current="read_only / writes disabled / no order",
            evidence="Preflight reads selected row, Candidate Registry fallback, and DB price metadata only.",
            next_action="Run Performance Recheck manually when ready; no monitoring log, approval, order, or rebalance is created.",
        ),
    ]

    if readiness_route == "RECHECK_READINESS_BLOCKED" or freshness_route == "SYMBOL_FRESHNESS_BLOCKED":
        route = "RECHECK_PREFLIGHT_BLOCKED"
        conclusion = "Performance Recheck 실행 전 차단 항목을 먼저 해결해야 합니다."
    elif readiness_route == "RECHECK_READINESS_NEEDS_DATA" or freshness_route in {
        "SYMBOL_FRESHNESS_MISSING",
        "SYMBOL_FRESHNESS_NEEDS_DATA",
    }:
        route = "RECHECK_PREFLIGHT_NEEDS_DATA"
        conclusion = "Performance Recheck를 최신 evidence로 보려면 DB 데이터 또는 replay 입력을 보강해야 합니다."
    elif readiness_route == "RECHECK_READINESS_REVIEW" or freshness_route in {
        "SYMBOL_FRESHNESS_WATCH",
        "SYMBOL_FRESHNESS_STALE",
    }:
        route = "RECHECK_PREFLIGHT_REVIEW"
        conclusion = "Performance Recheck 실행은 가능하지만 최신성 또는 일부 근거를 확인해야 합니다."
    else:
        route = "RECHECK_PREFLIGHT_READY"
        conclusion = "Performance Recheck 실행 전 readiness와 symbol freshness가 준비되어 있습니다."

    return {
        "schema_version": SELECTED_RECHECK_OPERATIONS_PREFLIGHT_SCHEMA_VERSION,
        "route": route,
        "route_label": SELECTED_RECHECK_OPERATIONS_PREFLIGHT_ROUTE_LABELS.get(route, route),
        "conclusion": conclusion,
        "rows": rows,
        "readiness": readiness,
        "symbol_freshness": symbol_freshness,
        "metrics": {
            "readiness_route": readiness_route,
            "freshness_route": freshness_route,
            "active_component_count": readiness_metrics.get("active_component_count", 0),
            "replay_contract_count": readiness_metrics.get("replay_contract_count", 0),
            "embedded_replay_contract_count": readiness_metrics.get("embedded_replay_contract_count", 0),
            "candidate_registry_fallback_count": readiness_metrics.get("candidate_registry_fallback_count", 0),
            "symbol_count": freshness_metrics.get("symbol_count", readiness_metrics.get("symbol_count", 0)),
            "portfolio_symbol_count": freshness_metrics.get("portfolio_symbol_count", 0),
            "benchmark_symbol_count": freshness_metrics.get("benchmark_symbol_count", 0),
            "missing_symbol_count": freshness_metrics.get("missing_count", 0),
            "stale_symbol_count": freshness_metrics.get("stale_count", 0),
            "watch_symbol_count": freshness_metrics.get("watch_count", 0),
            "readiness_blocked_count": readiness_metrics.get("blocked_count", 0),
            "readiness_needs_input_count": readiness_metrics.get("needs_input_count", 0),
            "freshness_needs_input_count": freshness_metrics.get("needs_input_count", 0),
            "freshness_blocked_count": freshness_metrics.get("blocked_count", 0),
            "latest_market_date": readiness_metrics.get("latest_market_date")
            or freshness_metrics.get("latest_market_date"),
            "timeframe": freshness_metrics.get("timeframe", timeframe),
        },
        "execution_boundary": {
            "write_policy": "read_only_recheck_operations_preflight",
            "db_write": False,
            "registry_write": False,
            "monitoring_log_auto_write": False,
            "live_approval": False,
            "order_instruction": False,
            "auto_rebalance": False,
            "notes": "Operations preflight combines existing readiness and DB price freshness read models; it does not ingest data or save monitoring records.",
        },
    }


def _provider_symbol_candidates_from_value(value: Any) -> list[str]:
    if isinstance(value, str):
        raw_values = re.split(r"[,/\s]+", value)
    elif isinstance(value, (list, tuple, set)):
        raw_values = list(value)
    else:
        raw_values = [value]
    symbols: list[str] = []
    for raw in raw_values:
        text = str(raw or "").strip().upper()
        if not text or text in {"-", "N/A", "NONE"}:
            continue
        if re.fullmatch(r"[A-Z0-9][A-Z0-9.\-]{0,14}", text):
            symbols.append(text)
    return list(dict.fromkeys(symbols))


def _fallback_provider_symbols_from_component(component: dict[str, Any]) -> list[str]:
    contract = dict(component.get("contract") or {})
    replay_contract = dict(component.get("replay_contract") or {})
    settings = dict(replay_contract.get("settings_snapshot") or {})
    raw_values = [
        contract.get("tickers"),
        settings.get("tickers"),
        component.get("universe"),
        component.get("holding_symbol"),
        component.get("asset_symbol"),
        component.get("symbol"),
        component.get("ticker"),
    ]
    symbols: list[str] = []
    for value in raw_values:
        symbols.extend(_provider_symbol_candidates_from_value(value))
    return list(dict.fromkeys(symbols))


def _selected_provider_symbol_weights(
    row: dict[str, Any],
    *,
    candidate_rows_by_id: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Resolve selected portfolio ETF weights for provider evidence without writing user state."""

    contract_evidence = _resolve_selected_recheck_contracts(row, candidate_rows_by_id=candidate_rows_by_id)
    symbol_weights: dict[str, float] = {}
    component_rows: list[dict[str, Any]] = []
    fallback_contracts: list[str] = []

    for contract_row in list(contract_evidence.get("contracts") or []):
        component = dict(contract_row.get("component") or {})
        identity = _clean_text(contract_row.get("identity") or component.get("registry_id") or component.get("title"))
        title = _clean_text(contract_row.get("title") or component.get("title") or identity)
        registry_id = _clean_text(contract_row.get("registry_id") or component.get("registry_id"), "")
        component_weight = _optional_float(component.get("target_weight")) or 0.0
        source = _clean_text(contract_row.get("source"), "unresolved")
        evidence = _clean_text(contract_row.get("evidence"), "Selected replay contract provided portfolio tickers.")
        status = "PASS" if contract_row.get("status") == "PASS" else "BLOCKED"
        tickers: list[str] = []

        if contract_row.get("status") == "PASS":
            payload = dict(contract_row.get("payload") or {})
            tickers = _provider_symbol_candidates_from_value(payload.get("tickers"))

        if not tickers:
            tickers = _fallback_provider_symbols_from_component(component)
            if tickers:
                source = "selected_component_fallback"
                status = "REVIEW"
                evidence = "Replay contract was incomplete; selected component ticker fields were used as fallback."
                fallback_contracts.append(identity)
            else:
                source = "unresolved"
                status = "BLOCKED"
                evidence = "No provider ticker symbols could be resolved for this selected component."

        for ticker in tickers:
            symbol_weights[ticker] = symbol_weights.get(ticker, 0.0) + (component_weight / len(tickers))

        component_rows.append(
            {
                "Component": title,
                "Registry ID": registry_id or "-",
                "Target Weight": round(component_weight, 4),
                "Symbols": ", ".join(tickers) if tickers else "-",
                "Source": source,
                "Status": status,
                "Evidence": evidence,
            }
        )

    return {
        "symbol_weights": {symbol: round(weight, 4) for symbol, weight in sorted(symbol_weights.items()) if weight > 0.0},
        "component_rows": component_rows,
        "active_component_count": contract_evidence.get("active_component_count", 0),
        "valid_contract_count": contract_evidence.get("valid_contract_count", 0),
        "embedded_contract_count": contract_evidence.get("embedded_contract_count", 0),
        "candidate_registry_fallback_count": contract_evidence.get("candidate_registry_fallback_count", 0),
        "fallback_contract_count": len(fallback_contracts),
        "missing_contracts": list(contract_evidence.get("missing_contracts") or []),
        "invalid_contracts": list(contract_evidence.get("invalid_contracts") or []),
        "candidate_load_error": contract_evidence.get("candidate_load_error", ""),
        "replay_builder_error": contract_evidence.get("replay_builder_error", ""),
    }


def _selected_provider_status(value: Any) -> str:
    normalized = str(value or "").strip().upper()
    if normalized in {"PASS", "READY", "CLEAR"}:
        return "PASS"
    if normalized in {"REVIEW", "WATCH", "PARTIAL"}:
        return "REVIEW"
    if normalized in {"BLOCKED", "BREACHED", "ERROR"}:
        return "BLOCKED"
    return "NEEDS_INPUT"


def _provider_status_max(*statuses: str) -> str:
    normalized = [status for status in statuses if status in _SELECTED_PROVIDER_STATUS_RANK]
    if not normalized:
        return "NEEDS_INPUT"
    return max(normalized, key=lambda status: _SELECTED_PROVIDER_STATUS_RANK[status])


def _provider_area_is_required(area: str) -> bool:
    return area in _SELECTED_PROVIDER_REQUIRED_AREAS


def _provider_freshness_status(area: str, freshness: Any) -> tuple[str, str]:
    normalized = str(freshness or "").strip().lower()
    if normalized in {"fresh", "current", "ready", "pass"}:
        return "PASS", ""
    if normalized in {"stale", "watch", "aging", "old", "review"}:
        return "REVIEW", f"freshness={normalized}"
    if normalized in {"error", "blocked"}:
        return "BLOCKED", f"freshness={normalized}"
    if _provider_area_is_required(area):
        return "NEEDS_INPUT", f"freshness={normalized or 'missing'}"
    return "REVIEW", f"freshness={normalized or 'missing'}"


def _provider_coverage_status(
    area: str,
    *,
    coverage: Any,
    coverage_weight: float | None,
) -> tuple[str, str]:
    normalized = str(coverage or "").strip().lower()
    if coverage_weight is not None and coverage_weight <= 0.0:
        if _provider_area_is_required(area):
            return "NEEDS_INPUT", f"coverage_weight={coverage_weight:.1f}%"
        return "REVIEW", f"coverage_weight={coverage_weight:.1f}%"
    if normalized in {"actual", "official", "provider_backed", "full"}:
        if coverage_weight is not None and coverage_weight < 80.0:
            return "REVIEW", f"coverage_weight={coverage_weight:.1f}%"
        return "PASS", ""
    if normalized in {"partial", "bridge", "proxy", "mixed"}:
        return "REVIEW", f"coverage={normalized}"
    if normalized in {"error", "blocked"}:
        return "BLOCKED", f"coverage={normalized}"
    if normalized in {"missing", "not_run", "not run", "-", ""}:
        if _provider_area_is_required(area):
            return "NEEDS_INPUT", f"coverage={normalized or 'missing'}"
        return "REVIEW", f"coverage={normalized or 'missing'}"
    return "REVIEW", f"coverage={normalized}"


def _provider_evidence_next_action(status: str, *, area: str) -> str:
    if status == "PASS":
        return "Use this provider evidence as a current selected portfolio check."
    if status == "REVIEW":
        return f"Review partial or stale {area} coverage before relying on this selected portfolio."
    if status == "BLOCKED":
        return f"Resolve blocked {area} evidence before treating provider evidence as usable."
    return f"Refresh or collect {area} provider data through the ingestion -> DB path, then re-open this view."


def _provider_evidence_row_from_display(row: dict[str, Any]) -> dict[str, Any]:
    area = _clean_text(row.get("Area"))
    diagnostic_status = _selected_provider_status(row.get("Diagnostic Status"))
    coverage_weight = _optional_float(row.get("Coverage Weight"))
    coverage_status, coverage_reason = _provider_coverage_status(
        area,
        coverage=row.get("Coverage"),
        coverage_weight=coverage_weight,
    )
    freshness_status, freshness_reason = _provider_freshness_status(area, row.get("Freshness"))
    status = _provider_status_max(diagnostic_status, coverage_status, freshness_status)
    policy_reasons = [
        reason
        for reason in [
            f"diagnostic={_clean_text(row.get('Diagnostic Status'))}" if diagnostic_status != "PASS" else "",
            coverage_reason,
            freshness_reason,
        ]
        if reason
    ]
    return {
        "Area": area,
        "Status": status,
        "Diagnostic Status": _clean_text(row.get("Diagnostic Status")),
        "Coverage": _clean_text(row.get("Coverage")),
        "Coverage Weight": coverage_weight,
        "Freshness": _clean_text(row.get("Freshness")),
        "As Of Range": _clean_text(row.get("As Of Range")),
        "Source Mix": _clean_text(row.get("Source Mix")),
        "Summary": _clean_text(row.get("Summary")),
        "Policy Reason": "; ".join(policy_reasons) if policy_reasons else "fresh actual provider evidence",
        "Next Action": _provider_evidence_next_action(status, area=area),
    }


def _missing_selected_provider_area_rows(existing_areas: set[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for area in sorted(_SELECTED_PROVIDER_REQUIRED_AREAS - existing_areas):
        rows.append(
            {
                "Area": area,
                "Status": "NEEDS_INPUT",
                "Diagnostic Status": "NOT_RUN",
                "Coverage": "missing",
                "Coverage Weight": 0.0,
                "Freshness": "missing",
                "As Of Range": "-",
                "Source Mix": "-",
                "Summary": "Required selected provider evidence area is missing from provider context.",
                "Policy Reason": "required_provider_area_missing",
                "Next Action": _provider_evidence_next_action("NEEDS_INPUT", area=area),
            }
        )
    return rows


def _provider_look_through_policy_row(board: dict[str, Any]) -> dict[str, Any]:
    if not board:
        return {
            "Area": "Look-through Coverage",
            "Status": "NEEDS_INPUT",
            "Diagnostic Status": "NOT_RUN",
            "Coverage": "missing",
            "Coverage Weight": 0.0,
            "Freshness": "-",
            "As Of Range": "-",
            "Source Mix": "-",
            "Summary": "Look-through board is unavailable for selected provider evidence.",
            "Policy Reason": "look_through_board_missing",
            "Next Action": _provider_evidence_next_action("NEEDS_INPUT", area="Look-through Coverage"),
        }

    holdings_coverage = _optional_float(board.get("holdings_coverage_weight"))
    exposure_coverage = _optional_float(board.get("exposure_coverage_weight"))
    unknown_exposure = _optional_float(board.get("unknown_exposure_weight"))
    top_holding = _optional_float(board.get("top_holding_weight"))
    board_status = _selected_provider_status(board.get("status"))
    policy_reasons: list[str] = []
    coverage_values = [value for value in [holdings_coverage, exposure_coverage] if value is not None]
    min_coverage = min(coverage_values) if coverage_values else None
    coverage_status = "PASS"
    if holdings_coverage is None or exposure_coverage is None:
        coverage_status = "NEEDS_INPUT"
        policy_reasons.append("look_through_coverage_missing")
    elif holdings_coverage <= 0.0 or exposure_coverage <= 0.0:
        coverage_status = "NEEDS_INPUT"
        policy_reasons.append(
            f"holdings={holdings_coverage:.1f}% / exposure={exposure_coverage:.1f}%"
        )
    elif holdings_coverage < 80.0 or exposure_coverage < 80.0:
        coverage_status = "REVIEW"
        policy_reasons.append(
            f"holdings={holdings_coverage:.1f}% / exposure={exposure_coverage:.1f}%"
        )
    if unknown_exposure is not None and unknown_exposure > 20.0:
        coverage_status = _provider_status_max(coverage_status, "REVIEW")
        policy_reasons.append(f"unknown_exposure={unknown_exposure:.1f}%")
    if top_holding is not None and top_holding > 25.0:
        coverage_status = _provider_status_max(coverage_status, "REVIEW")
        policy_reasons.append(f"top_holding={top_holding:.1f}%")
    status = _provider_status_max(board_status, coverage_status)
    if board_status != "PASS":
        policy_reasons.append(f"board_status={board.get('status') or '-'}")

    return {
        "Area": "Look-through Coverage",
        "Status": status,
        "Diagnostic Status": _clean_text(board.get("status")),
        "Coverage": "selected_look_through",
        "Coverage Weight": min_coverage,
        "Freshness": "-",
        "As Of Range": "-",
        "Source Mix": "provider_holdings / provider_exposure",
        "Summary": _clean_text(board.get("summary") or "Selected look-through coverage policy check."),
        "Policy Reason": "; ".join(policy_reasons) if policy_reasons else "holdings and exposure coverage are sufficient",
        "Next Action": _provider_evidence_next_action(status, area="Look-through Coverage"),
    }


def _selected_provider_staleness_contract(
    *,
    route: str,
    rows: list[dict[str, Any]],
    contract_evidence: dict[str, Any],
    max_provider_staleness_days: int,
) -> dict[str, Any]:
    stale_count = sum(1 for row in rows if str(row.get("Freshness") or "").strip().lower() == "stale")
    missing_freshness_count = sum(
        1
        for row in rows
        if str(row.get("Freshness") or "").strip().lower() in {"missing", "not_run", "not run"}
    )
    partial_coverage_count = sum(
        1
        for row in rows
        if str(row.get("Coverage") or "").strip().lower() in {"partial", "bridge", "proxy", "mixed"}
    )
    missing_coverage_count = sum(
        1
        for row in rows
        if str(row.get("Coverage") or "").strip().lower() in {"missing", "not_run", "not run", "error"}
        or (_optional_float(row.get("Coverage Weight")) is not None and (_optional_float(row.get("Coverage Weight")) or 0.0) <= 0.0)
    )
    required_area_status = {
        row.get("Area"): row.get("Status")
        for row in rows
        if str(row.get("Area") or "") in _SELECTED_PROVIDER_REQUIRED_AREAS
    }
    return {
        "schema_version": SELECTED_PROVIDER_STALENESS_CONTRACT_SCHEMA_VERSION,
        "route": route,
        "required_areas": sorted(_SELECTED_PROVIDER_REQUIRED_AREAS),
        "required_area_status": required_area_status,
        "stale_count": stale_count,
        "missing_freshness_count": missing_freshness_count,
        "partial_coverage_count": partial_coverage_count,
        "missing_coverage_count": missing_coverage_count,
        "fallback_contract_count": int(contract_evidence.get("fallback_contract_count") or 0),
        "embedded_contract_count": int(contract_evidence.get("embedded_contract_count") or 0),
        "candidate_registry_fallback_count": int(contract_evidence.get("candidate_registry_fallback_count") or 0),
        "max_provider_staleness_days": max_provider_staleness_days,
        "execution_boundary": {
            "db_write": False,
            "registry_write": False,
            "provider_collection": False,
            "monitoring_log_auto_write": False,
            "live_approval": False,
            "order_instruction": False,
            "auto_rebalance": False,
        },
    }


def build_selected_portfolio_provider_evidence(
    row: dict[str, Any],
    *,
    provider_context: dict[str, Any] | None = None,
    candidate_rows_by_id: dict[str, dict[str, Any]] | None = None,
    as_of_date: str | None = None,
    max_provider_staleness_days: int = 45,
) -> dict[str, Any]:
    """Read selected ETF provider evidence from existing DB snapshots without collecting or persisting data."""

    contract_evidence = _selected_provider_symbol_weights(row, candidate_rows_by_id=candidate_rows_by_id)
    symbol_weights = dict(contract_evidence.get("symbol_weights") or {})
    contract_component_rows = [dict(item or {}) for item in list(contract_evidence.get("component_rows") or [])]
    contract_blockers = [
        str(item)
        for item in (
            list(contract_evidence.get("missing_contracts") or [])
            + list(contract_evidence.get("invalid_contracts") or [])
        )
        if str(item)
    ]
    if contract_evidence.get("candidate_load_error"):
        contract_blockers.append(str(contract_evidence.get("candidate_load_error")))
    if contract_evidence.get("replay_builder_error"):
        contract_blockers.append(str(contract_evidence.get("replay_builder_error")))

    if not symbol_weights:
        rows = [
            {
                "Area": "Selected Symbol Contract",
                "Status": "BLOCKED",
                "Diagnostic Status": "BLOCKED",
                "Coverage": "not_run",
                "Coverage Weight": 0.0,
                "Freshness": "-",
                "As Of Range": "-",
                "Source Mix": "-",
                "Summary": "; ".join(contract_blockers[:3]) if contract_blockers else "No selected provider symbols were resolved.",
                "Policy Reason": "selected_provider_symbol_contract_blocked",
                "Next Action": "Fix selected component replay contracts before checking provider evidence.",
            }
        ]
        staleness_contract = _selected_provider_staleness_contract(
            route="SELECTED_PROVIDER_BLOCKED",
            rows=rows,
            contract_evidence=contract_evidence,
            max_provider_staleness_days=max_provider_staleness_days,
        )
        return {
            "schema_version": SELECTED_PROVIDER_EVIDENCE_SCHEMA_VERSION,
            "route": "SELECTED_PROVIDER_BLOCKED",
            "route_label": SELECTED_PROVIDER_EVIDENCE_ROUTE_LABELS["SELECTED_PROVIDER_BLOCKED"],
            "conclusion": "provider evidence를 확인할 selected portfolio symbol이 없습니다.",
            "rows": rows,
            "symbol_weights": symbol_weights,
            "component_rows": contract_component_rows,
            "provider_context": {},
            "look_through_board": {},
            "staleness_contract": staleness_contract,
            "metrics": {
                "area_count": len(rows),
                "pass_count": 0,
                "review_count": 0,
                "needs_input_count": 0,
                "blocked_count": 1,
                "stale_count": staleness_contract.get("stale_count", 0),
                "missing_freshness_count": staleness_contract.get("missing_freshness_count", 0),
                "partial_coverage_count": staleness_contract.get("partial_coverage_count", 0),
                "missing_coverage_count": staleness_contract.get("missing_coverage_count", 0),
                "provider_symbol_count": 0,
                "total_symbol_weight": 0.0,
                "active_component_count": contract_evidence.get("active_component_count", 0),
                "valid_contract_count": contract_evidence.get("valid_contract_count", 0),
                "embedded_contract_count": contract_evidence.get("embedded_contract_count", 0),
                "candidate_registry_fallback_count": contract_evidence.get("candidate_registry_fallback_count", 0),
                "fallback_contract_count": contract_evidence.get("fallback_contract_count", 0),
                "max_provider_staleness_days": max_provider_staleness_days,
            },
            "execution_boundary": {
                "write_policy": "read_only_selected_provider_evidence",
                "db_read": False,
                "db_write": False,
                "registry_write": False,
                "provider_collection": False,
                "monitoring_log_auto_write": False,
                "live_approval": False,
                "order_instruction": False,
                "auto_rebalance": False,
                "notes": "Provider evidence failed before DB reads because no selected provider symbols were resolved.",
            },
        }

    context_error = ""
    if provider_context is None:
        try:
            from app.services.backtest_practical_validation_provider_context import build_provider_context

            context = build_provider_context(
                symbol_weights,
                as_of_date=as_of_date or date.today().isoformat(),
                max_provider_staleness_days=max_provider_staleness_days,
            )
        except Exception as exc:  # pragma: no cover - depends on local DB/provider availability
            context = {}
            context_error = str(exc)
    else:
        context = dict(provider_context)

    contract_status = "PASS"
    if any(row.get("Status") == "BLOCKED" for row in contract_component_rows):
        contract_status = "BLOCKED"
    elif (
        contract_blockers
        or int(contract_evidence.get("fallback_contract_count") or 0) > 0
        or int(contract_evidence.get("valid_contract_count") or 0) < int(contract_evidence.get("active_component_count") or 0)
    ):
        contract_status = "REVIEW"

    rows: list[dict[str, Any]] = [
        {
            "Area": "Selected Symbol Contract",
            "Status": contract_status,
            "Diagnostic Status": contract_status,
            "Coverage": "selected_contract",
            "Coverage Weight": round(sum(float(value or 0.0) for value in symbol_weights.values()), 4),
            "Freshness": "-",
            "As Of Range": "-",
            "Source Mix": "candidate_replay_contract"
            if contract_status == "PASS"
            else "candidate_replay_contract / selected_component_fallback",
            "Summary": (
                f"{len(symbol_weights)} provider symbols resolved from selected component contract."
                if contract_status == "PASS"
                else "; ".join(contract_blockers[:3])
                if contract_blockers
                else "Some selected provider symbols used component fallback fields."
            ),
            "Next Action": _provider_evidence_next_action(contract_status, area="Selected Symbol Contract"),
        }
    ]

    if context_error:
        rows.append(
            {
                "Area": "Provider Context",
                "Status": "NEEDS_INPUT",
                "Diagnostic Status": "NEEDS_INPUT",
                "Coverage": "error",
                "Coverage Weight": 0.0,
                "Freshness": "-",
                "As Of Range": "-",
                "Source Mix": "-",
                "Summary": context_error,
                "Policy Reason": "provider_context_error",
                "Next Action": "Check provider loader / DB connectivity, then refresh this view.",
            }
        )
    else:
        provider_rows = [
            _provider_evidence_row_from_display(dict(item or {}))
            for item in list(context.get("display_rows") or [])
        ]
        existing_areas = {str(item.get("Area") or "") for item in provider_rows}
        rows.extend(provider_rows)
        rows.extend(_missing_selected_provider_area_rows(existing_areas))

    board = dict(context.get("look_through_board") or {})
    rows.append(_provider_look_through_policy_row(board))

    pass_count = sum(1 for item in rows if item.get("Status") == "PASS")
    review_count = sum(1 for item in rows if item.get("Status") == "REVIEW")
    needs_input_count = sum(1 for item in rows if item.get("Status") == "NEEDS_INPUT")
    blocked_count = sum(1 for item in rows if item.get("Status") == "BLOCKED")
    if blocked_count:
        route = "SELECTED_PROVIDER_BLOCKED"
        conclusion = "selected provider evidence에 차단 항목이 있어 먼저 contract 또는 provider 근거를 보강해야 합니다."
    elif needs_input_count:
        route = "SELECTED_PROVIDER_NEEDS_DATA"
        conclusion = "provider DB 근거가 부족하거나 읽히지 않아 selected portfolio의 provider evidence를 완료할 수 없습니다."
    elif review_count:
        route = "SELECTED_PROVIDER_REVIEW"
        conclusion = "provider evidence는 읽혔지만 coverage, stale, fallback 등 검토 항목이 남아 있습니다."
    else:
        route = "SELECTED_PROVIDER_READY"
        conclusion = "selected portfolio의 provider / holdings / exposure 근거가 현재 읽기 기준을 통과했습니다."

    staleness_contract = _selected_provider_staleness_contract(
        route=route,
        rows=rows,
        contract_evidence=contract_evidence,
        max_provider_staleness_days=max_provider_staleness_days,
    )
    return {
        "schema_version": SELECTED_PROVIDER_EVIDENCE_SCHEMA_VERSION,
        "route": route,
        "route_label": SELECTED_PROVIDER_EVIDENCE_ROUTE_LABELS.get(route, route),
        "conclusion": conclusion,
        "rows": rows,
        "symbol_weights": symbol_weights,
        "component_rows": contract_component_rows,
        "provider_context": context,
        "look_through_board": board,
        "staleness_contract": staleness_contract,
        "metrics": {
            "area_count": len(rows),
            "pass_count": pass_count,
            "review_count": review_count,
            "needs_input_count": needs_input_count,
            "blocked_count": blocked_count,
            "stale_count": staleness_contract.get("stale_count", 0),
            "missing_freshness_count": staleness_contract.get("missing_freshness_count", 0),
            "partial_coverage_count": staleness_contract.get("partial_coverage_count", 0),
            "missing_coverage_count": staleness_contract.get("missing_coverage_count", 0),
            "provider_symbol_count": len(symbol_weights),
            "total_symbol_weight": round(sum(float(value or 0.0) for value in symbol_weights.values()), 4),
            "active_component_count": contract_evidence.get("active_component_count", 0),
            "valid_contract_count": contract_evidence.get("valid_contract_count", 0),
            "embedded_contract_count": contract_evidence.get("embedded_contract_count", 0),
            "candidate_registry_fallback_count": contract_evidence.get("candidate_registry_fallback_count", 0),
            "fallback_contract_count": contract_evidence.get("fallback_contract_count", 0),
            "max_provider_staleness_days": max_provider_staleness_days,
            "look_through_status": board.get("status"),
            "holdings_coverage_weight": board.get("holdings_coverage_weight"),
            "exposure_coverage_weight": board.get("exposure_coverage_weight"),
            "unknown_exposure_weight": board.get("unknown_exposure_weight"),
            "top_holding_weight": board.get("top_holding_weight"),
        },
        "execution_boundary": {
            "write_policy": "read_only_selected_provider_evidence",
            "db_read": provider_context is None,
            "db_write": False,
            "registry_write": False,
            "provider_collection": False,
            "monitoring_log_auto_write": False,
            "live_approval": False,
            "order_instruction": False,
            "auto_rebalance": False,
            "notes": "Provider evidence reads selected component contracts and existing provider DB snapshots only; it does not collect data or save monitoring records.",
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
        from .candidate_library import run_candidate_replay_payload
    except Exception as exc:  # pragma: no cover - defensive import boundary
        return {"status": "error", "error": f"candidate replay helper import failed: {exc}"}

    contract_evidence = _resolve_selected_recheck_contracts(raw_decision)
    component_dfs: list[pd.DataFrame] = []
    ratios: list[float] = []
    component_rows: list[dict[str, Any]] = []
    blockers: list[str] = []
    first_benchmark_df = pd.DataFrame()
    first_benchmark_label = "-"

    if (
        contract_evidence.get("candidate_load_error")
        and int(contract_evidence.get("valid_contract_count") or 0) < int(contract_evidence.get("active_component_count") or 0)
    ):
        blockers.append(str(contract_evidence.get("candidate_load_error")))
    if contract_evidence.get("replay_builder_error"):
        blockers.append(str(contract_evidence.get("replay_builder_error")))

    for contract_row in list(contract_evidence.get("contracts") or []):
        component = dict(contract_row.get("component") or {})
        title = _clean_text(contract_row.get("title") or component.get("title") or contract_row.get("identity"))
        weight = (_optional_float(component.get("target_weight")) or 0.0) / 100.0
        registry_id = _clean_text(contract_row.get("registry_id") or component.get("registry_id"), "")
        if contract_row.get("status") != "PASS":
            blockers.append(f"{title}: replay contract 확인 실패 - {contract_row.get('evidence') or '-'}")
            continue
        try:
            payload = dict(contract_row.get("payload") or {})
            payload["start"] = start_ts.strftime("%Y-%m-%d")
            payload["end"] = end_ts.strftime("%Y-%m-%d")
            current_row = dict(contract_row.get("candidate_row") or {})
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
