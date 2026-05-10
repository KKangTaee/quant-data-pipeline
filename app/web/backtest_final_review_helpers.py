from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd

from app.web.backtest_portfolio_proposal_helpers import (
    FINAL_SELECTION_DECISION_ROUTE_OPTIONS,
    _build_final_selection_decision_phase35_handoff,
    _build_portfolio_risk_validation_input_for_proposal,
    _build_portfolio_risk_validation_input_for_single_candidate,
    _build_portfolio_risk_validation_result,
    _paper_ledger_baseline_snapshot,
    _paper_ledger_slug,
    _paper_ledger_target_components,
    _portfolio_proposal_candidate_data_trust_status,
    _portfolio_proposal_current_candidate_by_registry_id,
    _portfolio_proposal_optional_float,
    _portfolio_proposal_pre_live_record_by_registry_id,
    _portfolio_proposal_pre_live_status_by_registry_id,
)
from app.web.runtime import FINAL_SELECTION_DECISION_V2_SCHEMA_VERSION


FINAL_REVIEW_ROUTE_OPTIONS = FINAL_SELECTION_DECISION_ROUTE_OPTIONS
FINAL_REVIEW_ROUTE_DESCRIPTIONS = {
    "SELECT_FOR_PRACTICAL_PORTFOLIO": "실전 후보로 선정합니다. 승인/주문은 아니며 Final Review에서 최종 판단이 완료됩니다.",
    "HOLD_FOR_MORE_PAPER_TRACKING": "근거는 남기되 실제 선정 전 더 관찰합니다.",
    "REJECT_FOR_PRACTICAL_USE": "현재 근거로는 실전 후보에서 제외합니다.",
    "RE_REVIEW_REQUIRED": "구성, 비중, 검증 근거, 데이터 상태를 다시 검토합니다.",
}
FINAL_REVIEW_DECISION_LABELS = {
    "SELECT_FOR_PRACTICAL_PORTFOLIO": "투자 가능 후보",
    "HOLD_FOR_MORE_PAPER_TRACKING": "내용 부족 / 관찰 필요",
    "REJECT_FOR_PRACTICAL_USE": "투자하면 안 됨",
    "RE_REVIEW_REQUIRED": "재검토 필요",
}
FINAL_REVIEW_STATUS_DISPLAY = {
    "SELECT_FOR_PRACTICAL_PORTFOLIO": {
        "route": "FINAL_REVIEW_DECISION_COMPLETE",
        "verdict": "최종 판단 완료: 실전 후보로 선정됨",
        "next_action": "이 기록은 투자 후보 선정 판단입니다. 실제 투자 금액, 리밸런싱, 주문 승인 여부는 별도 운영 / 승인 단계에서 사용자가 결정합니다.",
    },
    "HOLD_FOR_MORE_PAPER_TRACKING": {
        "route": "FINAL_REVIEW_HOLD_FOR_MORE_OBSERVATION",
        "verdict": "최종 판단 보류: 내용 부족 / 추가 관찰 필요",
        "next_action": "추가 paper observation이나 근거 보강 후 Final Review에서 다시 판단합니다.",
    },
    "REJECT_FOR_PRACTICAL_USE": {
        "route": "FINAL_REVIEW_REJECTED",
        "verdict": "최종 판단 완료: 실전 후보에서 제외됨",
        "next_action": "필요하면 후보 탐색, Compare, Portfolio Proposal 단계로 되돌아갑니다.",
    },
    "RE_REVIEW_REQUIRED": {
        "route": "FINAL_REVIEW_REVIEW_REQUIRED",
        "verdict": "최종 판단 재검토 필요: 구성 / 비중 / 검증 근거를 다시 확인",
        "next_action": "구성, 비중, validation, robustness, paper observation 근거를 보강한 뒤 Final Review에서 다시 판단합니다.",
    },
}


def _build_final_review_status_display(row: dict[str, Any]) -> dict[str, str]:
    """Translate saved final-decision rows into the current Final Review end-state copy."""
    decision_route = str(row.get("decision_route") or "").strip()
    status = dict(FINAL_REVIEW_STATUS_DISPLAY.get(decision_route) or {})
    if status:
        return status
    legacy_handoff = dict(row.get("phase35_handoff") or {})
    return {
        "route": str(legacy_handoff.get("handoff_route") or "FINAL_REVIEW_STATUS_UNKNOWN"),
        "verdict": "최종 판단 상태 확인 필요",
        "next_action": "decision route와 evidence를 확인한 뒤 Final Review에서 다시 판단합니다.",
    }


def _final_review_current_label(row: dict[str, Any]) -> str:
    registry_id = str(row.get("registry_id") or "").strip()
    title = str(row.get("title") or registry_id or "-")
    family = str(row.get("strategy_family") or "-")
    return f"단일 후보 | {family} | {title} | id={registry_id}"


def _final_review_proposal_label(row: dict[str, Any]) -> str:
    proposal_id = str(row.get("proposal_id") or "").strip()
    objective = dict(row.get("objective") or {})
    primary_goal = str(objective.get("primary_goal") or "-")
    return f"포트폴리오 초안 | {primary_goal} | id={proposal_id}"


def _final_review_practical_validation_label(row: dict[str, Any]) -> str:
    validation_id = str(row.get("validation_id") or "").strip()
    source_title = str(row.get("source_title") or row.get("selection_source_id") or "-")
    route = str(row.get("validation_route") or "-")
    return f"Clean V2 검증 결과 | {route} | {source_title} | id={validation_id}"


def _build_final_review_source_options(
    current_rows: list[dict[str, Any]],
    proposal_rows: list[dict[str, Any]],
    practical_validation_rows: list[dict[str, Any]] | None = None,
    session_practical_source: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Build selectable final-review sources from V2 validation, current candidates, and saved proposals."""
    options: list[dict[str, Any]] = []
    session_practical_source = dict(session_practical_source or {})
    session_validation = dict(session_practical_source.get("validation_result") or {})
    if session_validation:
        options.append(
            {
                "label": "현재 Practical Validation source | "
                + _final_review_practical_validation_label(session_validation),
                "source_type": "practical_validation_result",
                "source_id": session_validation.get("validation_id") or session_validation.get("selection_source_id"),
                "source_title": session_validation.get("source_title") or session_validation.get("selection_source_id"),
                "row": session_validation,
            }
        )
    seen_validation_ids = {
        str(session_validation.get("validation_id") or "").strip()
    } if session_validation else set()
    for row in list(practical_validation_rows or []):
        validation_id = str(row.get("validation_id") or "").strip()
        if validation_id and validation_id in seen_validation_ids:
            continue
        if not validation_id:
            continue
        options.append(
            {
                "label": _final_review_practical_validation_label(row),
                "source_type": "practical_validation_result",
                "source_id": validation_id,
                "source_title": row.get("source_title") or row.get("selection_source_id") or validation_id,
                "row": dict(row),
            }
        )
    for row in current_rows:
        registry_id = str(row.get("registry_id") or "").strip()
        if not registry_id:
            continue
        options.append(
            {
                "label": _final_review_current_label(row),
                "source_type": "single_candidate",
                "source_id": registry_id,
                "source_title": row.get("title") or registry_id,
                "row": dict(row),
            }
        )
    for row in proposal_rows:
        proposal_id = str(row.get("proposal_id") or "").strip()
        if not proposal_id:
            continue
        options.append(
            {
                "label": _final_review_proposal_label(row),
                "source_type": "portfolio_proposal",
                "source_id": proposal_id,
                "source_title": proposal_id,
                "row": dict(row),
            }
        )
    return options


def _build_final_review_validation(
    source: dict[str, Any],
    *,
    current_rows: list[dict[str, Any]],
    pre_live_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    """Read a selected current candidate or proposal through the shared validation contract."""
    source_type = str(source.get("source_type") or "")
    source_row = dict(source.get("row") or {})
    if source_type == "practical_validation_result":
        validation = dict(source_row)
        validation.setdefault("source_type", "practical_validation_result")
        validation.setdefault("validation_route", source_row.get("validation_route") or "NEEDS_REVIEW")
        validation.setdefault("validation_score", source_row.get("validation_score") or 0.0)
        validation.setdefault("hard_blockers", list(source_row.get("hard_blockers") or []))
        validation.setdefault("paper_tracking_gaps", list(source_row.get("paper_tracking_gaps") or []))
        validation.setdefault("review_gaps", list(source_row.get("review_gaps") or []))
        validation.setdefault("component_rows", list(source_row.get("component_rows") or []))
        return validation
    pre_live_by_registry_id = _portfolio_proposal_pre_live_record_by_registry_id(pre_live_rows)
    if source_type == "single_candidate":
        registry_id = str(source_row.get("registry_id") or "").strip()
        pre_live_statuses = _portfolio_proposal_pre_live_status_by_registry_id(pre_live_rows)
        validation_input = _build_portfolio_risk_validation_input_for_single_candidate(
            selected_row=source_row,
            pre_live_record=pre_live_by_registry_id.get(registry_id),
            pre_live_status=pre_live_statuses.get(registry_id, "not_started"),
            data_trust_status=_portfolio_proposal_candidate_data_trust_status(source_row),
        )
    else:
        validation_input = _build_portfolio_risk_validation_input_for_proposal(
            proposal_row=source_row,
            current_by_registry_id=_portfolio_proposal_current_candidate_by_registry_id(current_rows),
            pre_live_by_registry_id=pre_live_by_registry_id,
        )
    return _build_portfolio_risk_validation_result(validation_input)


def _build_final_review_paper_observation_snapshot(validation: dict[str, Any]) -> dict[str, Any]:
    """Convert validation output into paper-observation criteria without saving a separate ledger."""
    existing = dict(validation.get("paper_observation") or {})
    if existing:
        existing.setdefault("mode", "inline_paper_observation")
        existing.setdefault("route", "PAPER_OBSERVATION_READY")
        existing.setdefault("checks", [])
        existing.setdefault("blockers", [])
        return existing
    baseline = _paper_ledger_baseline_snapshot(validation)
    components = _paper_ledger_target_components(validation)
    active_components = [
        component
        for component in components
        if (_portfolio_proposal_optional_float(component.get("target_weight")) or 0.0) > 0.0
    ]
    benchmarks = sorted(
        {
            str(component.get("benchmark") or "").strip()
            for component in active_components
            if str(component.get("benchmark") or "").strip() not in {"", "-"}
        }
    )
    default_triggers = [
        "CAGR deterioration review",
        "MDD deterioration review",
        "Pre-Live status drift review",
        "Benchmark-relative underperformance review",
    ]
    target_weight_total = float(baseline.get("target_weight_total") or 0.0)
    checks = [
        {
            "Criteria": "Active components",
            "Ready": bool(active_components),
            "Current": str(len(active_components)),
            "Meaning": "최종 판단에 들어갈 active component가 있는지 봅니다.",
        },
        {
            "Criteria": "Target weight total",
            "Ready": bool(active_components) and abs(target_weight_total - 100.0) <= 0.01,
            "Current": f"{target_weight_total:.1f}%",
            "Meaning": "실전 후보 검토 기준 비중이 100%인지 봅니다.",
        },
        {
            "Criteria": "Observation benchmark",
            "Ready": bool(benchmarks),
            "Current": ", ".join(benchmarks) or "-",
            "Meaning": "관찰 성과를 무엇과 비교할지 봅니다.",
        },
        {
            "Criteria": "Review triggers",
            "Ready": True,
            "Current": str(len(default_triggers)),
            "Meaning": "최종 판단 이후에도 다시 볼 조건을 남깁니다.",
        },
    ]
    blockers = [str(row["Criteria"]) for row in checks if not row["Ready"]]
    route = "PAPER_OBSERVATION_READY" if not blockers else "PAPER_OBSERVATION_NEEDS_INPUT"
    return {
        "mode": "inline_paper_observation",
        "route": route,
        "blockers": blockers,
        "baseline_snapshot": baseline,
        "target_components": components,
        "active_components": active_components,
        "tracking_benchmark": benchmarks[0] if benchmarks else None,
        "review_cadence": "monthly_or_rebalance_review",
        "review_triggers": default_triggers,
        "checks": checks,
        "notes": "Paper observation criteria are kept inside the final review record; no separate paper ledger save is required.",
    }


def _build_final_review_decision_evidence_pack(
    validation: dict[str, Any],
    paper_observation: dict[str, Any],
) -> dict[str, Any]:
    """Summarize validation, robustness, and paper observation into one final-review route."""
    robustness = dict(validation.get("robustness_validation") or {})
    validation_route = str(validation.get("validation_route") or "")
    robustness_route = str(robustness.get("robustness_route") or "")
    paper_route = str(paper_observation.get("route") or "")
    validation_ready_routes = {"READY_FOR_ROBUSTNESS_REVIEW", "READY_FOR_FINAL_REVIEW"}
    validation_blocked = validation_route in {"BLOCKED_FOR_LIVE_READINESS", "BLOCKED"}
    robustness_blocked = robustness_route == "BLOCKED_FOR_ROBUSTNESS"
    paper_blocked = bool(paper_observation.get("blockers"))
    checks = [
        {
            "Criteria": "Portfolio validation",
            "Ready": not validation_blocked,
            "Current": validation_route or "-",
            "Meaning": "구성 / 비중 / 후보 상태가 최종 검토 전에 차단 상태인지 봅니다.",
            "Score": 2.4,
        },
        {
            "Criteria": "Robustness preview",
            "Ready": not robustness_blocked,
            "Current": robustness_route or "-",
            "Meaning": "기간 / 설정 / benchmark / 성과 snapshot blocker가 있는지 봅니다.",
            "Score": 2.2,
        },
        {
            "Criteria": "Paper observation criteria",
            "Ready": not paper_blocked,
            "Current": paper_route or "-",
            "Meaning": "별도 ledger 저장 없이 최종 판단 기록에 남길 관찰 기준이 충분한지 봅니다.",
            "Score": 2.0,
        },
        {
            "Criteria": "Execution boundary",
            "Ready": True,
            "Current": "live approval disabled / order instruction disabled",
            "Meaning": "최종 검토 기록이 주문이나 자동매매가 아님을 고정합니다.",
            "Score": 0.8,
        },
    ]
    blockers = [str(row["Criteria"]) for row in checks if not row["Ready"]]
    score = round(sum(float(row["Score"]) for row in checks if row["Ready"]), 1)
    if blockers:
        route = "FINAL_DECISION_BLOCKED"
        verdict = "최종 판단 전 보강 필요: validation / robustness / paper observation blocker가 남아 있음"
        next_action = "blocker를 해결하거나 보류 / 거절 / 재검토 판단으로 기록합니다."
        suggested_decision_route = "RE_REVIEW_REQUIRED"
    elif validation_route not in validation_ready_routes or robustness_route != "READY_FOR_STRESS_SWEEP":
        route = "FINAL_DECISION_NEEDS_REVIEW"
        verdict = "최종 선정 전 추가 검토 필요: hard blocker는 없지만 검증 보강 항목이 남아 있음"
        next_action = "더 관찰하거나 보강 후 선정 판단을 다시 봅니다."
        suggested_decision_route = "HOLD_FOR_MORE_PAPER_TRACKING"
    else:
        route = "READY_FOR_FINAL_DECISION"
        verdict = "최종 검토 가능: 검증 근거와 관찰 기준이 하나의 판단 기록으로 묶임"
        next_action = "최종 판단과 사유를 기록하면 Final Review에서 실전 후보 판단이 완료됩니다."
        suggested_decision_route = "SELECT_FOR_PRACTICAL_PORTFOLIO"
    return {
        "route": route,
        "score": min(score, 10.0),
        "verdict": verdict,
        "next_action": next_action,
        "suggested_decision_route": suggested_decision_route,
        "checks": checks,
        "blockers": blockers,
        "metrics": {
            "validation_route": validation_route,
            "validation_score": validation.get("validation_score"),
            "robustness_route": robustness_route,
            "robustness_score": robustness.get("robustness_score"),
            "paper_observation_route": paper_route,
            "active_components": len(paper_observation.get("active_components") or []),
            "target_weight_total": dict(paper_observation.get("baseline_snapshot") or {}).get("target_weight_total"),
        },
    }


def _build_final_review_save_evaluation(
    *,
    evidence: dict[str, Any],
    decision_id: str,
    decision_route: str,
    operator_reason: str,
    existing_decision_ids: set[str],
) -> dict[str, Any]:
    """Check whether the final review can be recorded as one durable decision row."""
    decision_id_clean = str(decision_id or "").strip()
    decision_route_clean = str(decision_route or "").strip()
    checks = [
        {
            "Criteria": "Decision identity",
            "Ready": bool(decision_id_clean) and decision_id_clean not in existing_decision_ids,
            "Current": decision_id_clean or "-",
            "Meaning": "중복되지 않는 최종 검토 기록 id가 필요합니다.",
        },
        {
            "Criteria": "Decision route",
            "Ready": decision_route_clean in FINAL_REVIEW_ROUTE_OPTIONS,
            "Current": decision_route_clean or "-",
            "Meaning": "선정 / 보류 / 거절 / 재검토 중 하나를 고릅니다.",
        },
        {
            "Criteria": "Operator reason",
            "Ready": bool(str(operator_reason or "").strip()),
            "Current": "attached" if str(operator_reason or "").strip() else "-",
            "Meaning": "왜 이 판단을 했는지 남깁니다.",
        },
        {
            "Criteria": "Select readiness",
            "Ready": decision_route_clean != "SELECT_FOR_PRACTICAL_PORTFOLIO"
            or evidence.get("route") == "READY_FOR_FINAL_DECISION",
            "Current": evidence.get("route") or "-",
            "Meaning": "실전 후보 선정은 blocker가 없을 때만 저장합니다.",
        },
    ]
    blockers = [str(row["Criteria"]) for row in checks if not row["Ready"]]
    if not blockers:
        route = "FINAL_REVIEW_RECORD_READY"
        verdict = "최종 검토 결과 기록 가능"
        next_action = "`최종 검토 결과 기록`을 눌러 판단과 근거를 남깁니다."
    else:
        route = "FINAL_REVIEW_RECORD_BLOCKED"
        verdict = "최종 검토 결과 기록 전 확인 필요"
        next_action = "decision id, 판단 route, 판단 사유, 선정 readiness를 확인합니다."
    return {
        "route": route,
        "score": round((len(checks) - len(blockers)) / len(checks) * 10.0, 1),
        "verdict": verdict,
        "next_action": next_action,
        "checks": checks,
        "blockers": blockers,
        "can_save": not blockers,
    }


def _build_final_review_decision_row(
    *,
    source: dict[str, Any],
    validation: dict[str, Any],
    paper_observation: dict[str, Any],
    evidence: dict[str, Any],
    decision_id: str,
    decision_route: str,
    operator_reason: str,
    operator_constraints: str,
    operator_next_action: str,
) -> dict[str, Any]:
    """Create one final review record that includes validation, observation, and decision evidence."""
    now = datetime.now().isoformat(timespec="seconds")
    source_id = str(source.get("source_id") or "").strip()
    row = {
        "schema_version": FINAL_SELECTION_DECISION_V2_SCHEMA_VERSION,
        "decision_id": str(decision_id or "").strip(),
        "created_at": now,
        "updated_at": now,
        "decision_status": "recorded",
        "decision_route": str(decision_route or "").strip(),
        "selected_practical_portfolio": decision_route == "SELECT_FOR_PRACTICAL_PORTFOLIO",
        "source_paper_ledger_id": None,
        "source_observation_id": f"paper_observation_{_paper_ledger_slug(source_id)}",
        "source_type": source.get("source_type"),
        "source_id": source_id,
        "source_title": source.get("source_title") or source_id,
        "selection_source_id": validation.get("selection_source_id"),
        "validation_id": validation.get("validation_id"),
        "selected_components": list(paper_observation.get("active_components") or []),
        "decision_evidence_snapshot": evidence,
        "risk_and_validation_snapshot": {
            "validation_route": validation.get("validation_route"),
            "validation_score": validation.get("validation_score"),
            "validation_checks": list(validation.get("checks") or []),
            "validation_profile": dict(validation.get("validation_profile") or {}),
            "diagnostic_summary": dict(validation.get("diagnostic_summary") or {}),
            "diagnostic_display_rows": list(validation.get("diagnostic_display_rows") or []),
            "diagnostic_results": list(validation.get("diagnostic_results") or []),
            "profile_score_rows": list(validation.get("profile_score_rows") or []),
            "curve_evidence": dict(validation.get("curve_evidence") or {}),
            "rolling_validation": dict(validation.get("rolling_validation") or {}),
            "not_run_domains": list(validation.get("not_run_domains") or []),
            "not_run_critical_domains": list(validation.get("not_run_critical_domains") or []),
            "intent_mismatch_warnings": list(validation.get("intent_mismatch_warnings") or []),
            "robustness_validation": dict(validation.get("robustness_validation") or {}),
        },
        "paper_tracking_snapshot": paper_observation,
        "operator_decision": {
            "reason": str(operator_reason or "").strip(),
            "constraints": str(operator_constraints or "").strip(),
            "next_action": str(operator_next_action or "").strip(),
        },
        "live_approval": False,
        "order_instruction": False,
        "notes": (
            "Created from Backtest > Final Review. This record combines validation, robustness, "
            "paper observation criteria, and operator judgment. It is not live approval or an order instruction."
        ),
    }
    row["phase35_handoff"] = _build_final_selection_decision_phase35_handoff(row)
    return row


def _build_final_review_decision_rows_for_display(rows: list[dict[str, Any]]) -> pd.DataFrame:
    """Flatten final decision records for the Final Review saved-record table."""
    display_rows: list[dict[str, Any]] = []
    for row in rows:
        evidence = dict(row.get("decision_evidence_snapshot") or {})
        status_display = _build_final_review_status_display(row)
        display_rows.append(
            {
                "Updated At": row.get("updated_at") or row.get("created_at"),
                "Decision ID": row.get("decision_id"),
                "Decision Route": row.get("decision_route"),
                "투자 가능성": FINAL_REVIEW_DECISION_LABELS.get(str(row.get("decision_route") or ""), "재검토 필요"),
                "Source": f"{row.get('source_type')} / {row.get('source_id')}",
                "Observation": row.get("source_observation_id") or row.get("source_paper_ledger_id") or "-",
                "Components": len(row.get("selected_components") or []),
                "Evidence Route": evidence.get("route"),
                "Evidence Score": evidence.get("score"),
                "Final Status": status_display.get("route"),
                "Live Approval": "Disabled",
            }
        )
    return pd.DataFrame(display_rows)
