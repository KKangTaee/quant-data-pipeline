from __future__ import annotations

from typing import Any

import streamlit as st

from app.web.backtest_practical_validation.components import (
    render_pv_card_grid,
    render_pv_section_header,
)
from app.web.backtest_practical_validation.status_display import (
    validation_status_label,
    validation_status_tone,
)
from app.web.components.practical_validation_fix_queue import (
    is_practical_validation_fix_queue_available,
    render_practical_validation_fix_queue,
)


GATE_FIX_GUIDANCE = {
    "latest_replay": {
        "location": "3. 최신 데이터 기준 전략 재검증",
        "action": "`전략 재검증 실행` 버튼을 누른 뒤 Recheck가 PASS 또는 REVIEW이고 Coverage가 PASS인지 확인합니다.",
    },
    "Latest Runtime Replay": {
        "location": "3. 최신 데이터 기준 전략 재검증",
        "action": "`전략 재검증 실행` 버튼을 누른 뒤 Recheck가 PASS 또는 REVIEW이고 Coverage가 PASS인지 확인합니다.",
    },
    "validation_efficacy": {
        "location": "Validation Efficacy Audit",
        "action": "Validation Efficacy Audit 상세에서 walk-forward / OOS / regime / PIT / survivorship 근거 중 부족한 항목을 보강합니다.",
    },
    "Validation Efficacy": {
        "location": "Validation Efficacy Audit",
        "action": "Validation Efficacy Audit 상세에서 walk-forward / OOS / regime / PIT / survivorship 근거 중 부족한 항목을 보강합니다.",
    },
    "data_coverage": {
        "location": "Data Coverage Audit / Provider Data Gaps",
        "action": "가격 window, provider freshness, lifecycle / survivorship 근거 중 부족한 항목을 확인하고 provider gap 수집 또는 데이터 보강을 진행합니다.",
    },
    "Data Coverage": {
        "location": "Data Coverage Audit / Provider Data Gaps",
        "action": "가격 window, provider freshness, lifecycle / survivorship 근거 중 부족한 항목을 확인하고 provider gap 수집 또는 데이터 보강을 진행합니다.",
    },
}


def _gate_module_display_rows(modules: list[dict[str, Any]]) -> list[dict[str, Any]]:
    display_rows: list[dict[str, Any]] = []
    for row in modules:
        module_id = str(row.get("module_id") or "").strip()
        label = str(row.get("label") or module_id or "-").strip()
        guidance = dict(GATE_FIX_GUIDANCE.get(module_id) or GATE_FIX_GUIDANCE.get(label) or {})
        fix_location = row.get("resolution_surface") or guidance.get("location") or "-"
        fix_action = (
            row.get("resolution_action")
            or guidance.get("action")
            or row.get("next_action")
            or "-"
        )
        display_rows.append(
            {
                "Module": label,
                "Status": row.get("status") or "-",
                "Status Label": row.get("status_label") or validation_status_label(row.get("status") or "-"),
                "Display Label": row.get("display_label") or label,
                "Issue Title": row.get("issue_title") or row.get("display_label") or label,
                "Current Problem": row.get("current_problem") or row.get("gate_reason") or "-",
                "Completion Criteria": row.get("completion_criteria") or row.get("resolution_action") or fix_action,
                "Impact Summary": row.get("impact_summary") or row.get("gate_effect") or "-",
                "Checked Evidence": row.get("checked_evidence") or row.get("reason") or "-",
                "Missing Evidence": row.get("missing_evidence") or row.get("gate_reason") or "-",
                "Action Label": row.get("action_label") or fix_action,
                "Why It Matters": row.get("why_it_matters") or row.get("gate_effect") or "-",
                "Technical Label": row.get("technical_label") or f"{label} · {row.get('status') or '-'}",
                "Fix Location": fix_location,
                "Fix Action": fix_action,
                "Gate Effect": row.get("gate_effect") or "-",
                "Gate Reason": row.get("gate_reason") or "-",
            }
        )
    return display_rows


def gate_module_display_rows(modules: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return _gate_module_display_rows(modules)


def _render_fix_queue(blocking_modules: list[dict[str, Any]]) -> None:
    if not blocking_modules:
        render_pv_card_grid(
            [
                {
                    "kicker": "Fix Queue",
                    "title": "필수 보강 항목 없음",
                    "status": "Ready",
                    "detail": "Final Review로 이동하기 전에 즉시 막는 필수 검증 blocker가 없습니다.",
                    "tone": "positive",
                }
            ],
            min_width=240,
        )
        return
    cards: list[dict[str, Any]] = []
    for module in blocking_modules:
        display_row = _gate_module_display_rows([module])[0]
        cards.append(
            {
                "kicker": display_row.get("Status") or "BLOCKING",
                "title": display_row.get("Module") or "-",
                "status": display_row.get("Fix Location") or "-",
                "detail": display_row.get("Fix Action") or "-",
                "meta": display_row.get("Gate Reason") or "",
                "tone": validation_status_tone(display_row.get("Status")),
            }
        )
    render_pv_section_header(
        eyebrow="Fix Queue",
        title=f"Final Review 이동 전 해결할 항목 {len(blocking_modules)}개",
        detail="각 카드의 Fix Location에서 보강한 뒤 Gate가 다시 계산됩니다.",
        tone="danger",
    )
    render_pv_card_grid(cards, min_width=260)


def render_fix_queue(blocking_modules: list[dict[str, Any]]) -> None:
    _render_fix_queue(blocking_modules)


def _workspace_group_tone(modules: list[dict[str, Any]]) -> str:
    statuses = {str(module.get("status") or "").upper() for module in modules}
    if statuses & {"BLOCKED", "NEEDS_INPUT", "NOT_RUN"}:
        return "danger"
    if "REVIEW" in statuses:
        return "warning"
    return "positive"


def _workspace_group_status(modules: list[dict[str, Any]]) -> str:
    counts: dict[str, int] = {}
    for module in modules:
        status = validation_status_label(module.get("status") or "NOT_RUN")
        counts[status] = counts.get(status, 0) + 1
    if not counts:
        return "-"
    return " / ".join(f"{status} {count}" for status, count in sorted(counts.items()))


def _workspace_group_cards(groups: list[dict[str, Any]], *, kicker: str) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    for group in groups:
        modules = [dict(module or {}) for module in list(group.get("modules") or [])]
        cards.append(
            {
                "kicker": kicker,
                "title": group.get("label") or group.get("group_id") or "-",
                "status": _workspace_group_status(modules),
                "detail": group.get("purpose") or f"{len(modules)} module(s)",
                "tone": _workspace_group_tone(modules),
            }
        )
    return cards


def _react_fix_queue_items(fix_queue: list[dict[str, Any]]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for row in _gate_module_display_rows(fix_queue):
        items.append(
            {
                "label": row.get("Module") or "-",
                "status": row.get("Status") or "-",
                "statusLabel": row.get("Status Label") or row.get("Status") or "-",
                "displayLabel": row.get("Display Label") or row.get("Module") or "-",
                "issueTitle": row.get("Issue Title") or row.get("Display Label") or row.get("Module") or "-",
                "currentProblem": row.get("Current Problem") or "-",
                "completionCriteria": row.get("Completion Criteria") or "-",
                "impactSummary": row.get("Impact Summary") or "",
                "checkedEvidence": row.get("Checked Evidence") or "-",
                "missingEvidence": row.get("Missing Evidence") or "-",
                "actionLabel": row.get("Action Label") or row.get("Fix Action") or "-",
                "whyItMatters": row.get("Why It Matters") or "",
                "technicalLabel": row.get("Technical Label") or "",
                "fixLocation": row.get("Fix Location") or "-",
                "fixAction": row.get("Fix Action") or "-",
                "gateReason": row.get("Gate Reason") or "",
                "tone": validation_status_tone(row.get("Status")),
            }
        )
    return items


def _react_core_group_items(core_groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for group in core_groups:
        modules = [dict(module or {}) for module in list(group.get("modules") or [])]
        items.append(
            {
                "label": group.get("label") or group.get("group_id") or "-",
                "status": _workspace_group_status(modules),
                "purpose": group.get("purpose") or f"{len(modules)} module(s)",
                "tone": _workspace_group_tone(modules),
                "modules": [
                    str(module.get("label") or module.get("module_id") or "-")
                    for module in modules
                    if module
                ],
            }
        )
    return items


def _react_criteria_group_items(criteria_groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for group in criteria_groups:
        cards = [dict(card or {}) for card in list(group.get("criteria_cards") or [])]
        items.append(
            {
                "label": group.get("label") or group.get("group_id") or "-",
                "displayLabel": group.get("display_label") or group.get("label") or group.get("group_id") or "-",
                "status": group.get("status") or "-",
                "purpose": group.get("purpose") or f"{len(cards)} criteria",
                "passedCriteria": list(group.get("passed_criteria") or []),
                "remainingIssues": list(group.get("remaining_issues") or []),
                "reviewCriteria": list(group.get("review_criteria") or []),
                "decisionSummary": group.get("decision_summary") or "-",
                "tone": group.get("tone") or "neutral",
                "criteriaCards": [
                    {
                        "label": card.get("label") or "-",
                        "displayLabel": card.get("display_label") or card.get("label") or "-",
                        "status": card.get("status") or "-",
                        "statusLabel": card.get("status_label") or card.get("status") or "-",
                        "technicalLabel": card.get("technical_label") or "",
                        "tone": card.get("tone") or "neutral",
                        "explanation": card.get("explanation") or "-",
                        "evidence": card.get("evidence") or "-",
                        "issueTitle": card.get("issue_title") or card.get("display_label") or card.get("label") or "-",
                        "currentProblem": card.get("current_problem") or "-",
                        "completionCriteria": card.get("completion_criteria") or "-",
                        "fixLocation": card.get("fix_location") or card.get("resolution_surface") or "-",
                        "impactSummary": card.get("impact_summary") or "",
                        "checkedEvidence": card.get("checked_evidence") or "-",
                        "missingEvidence": card.get("missing_evidence") or "-",
                        "actionLabel": card.get("action_label") or "-",
                        "whyItMatters": card.get("why_it_matters") or "",
                        "resolutionSurface": card.get("resolution_surface") or "-",
                    }
                    for card in cards
                    if card
                ],
            }
        )
    return items


def render_practical_validation_workspace_overview(validation_result: dict[str, Any]) -> None:
    workspace = dict(validation_result.get("practical_validation_workspace") or {})
    gate_summary = dict(workspace.get("gate_summary") or validation_result.get("final_review_gate") or {})
    fix_queue = list(workspace.get("fix_queue") or gate_summary.get("blocking_modules") or [])
    core_groups = list(workspace.get("core_evidence_groups") or [])
    conditional_groups = list(workspace.get("conditional_evidence_groups") or [])
    downstream_groups = list(workspace.get("downstream_reference_groups") or [])
    criteria_groups = list(workspace.get("criteria_detail_groups") or [])
    readiness_status = validation_status_label(gate_summary.get("route"))

    if is_practical_validation_fix_queue_available():
        render_practical_validation_fix_queue(
            status_label=readiness_status,
            tone="positive" if gate_summary.get("can_save_and_move") else "danger",
            verdict=str(gate_summary.get("verdict") or "2차 검증 결론"),
            next_action=str(gate_summary.get("next_action") or ""),
            can_save_and_move=bool(gate_summary.get("can_save_and_move")),
            fix_items=_react_fix_queue_items(fix_queue),
            core_groups=_react_core_group_items(core_groups),
            criteria_groups=_react_criteria_group_items(criteria_groups),
            review_count=int(gate_summary.get("review_count") or 0),
            key="practical_validation_fix_queue_overview",
        )
    else:
        _render_fix_queue(fix_queue)
        if core_groups:
            render_pv_section_header(
                eyebrow="Core Evidence",
                title="2차 검증 핵심 근거",
                detail="Final Review로 넘기기 전에 먼저 확인할 source, validation, readiness preview 근거입니다.",
                tone="neutral",
            )
            render_pv_card_grid(_workspace_group_cards(core_groups, kicker="Core"), min_width=250)
    if conditional_groups or downstream_groups:
        with st.expander("조건부 근거와 후속 참고", expanded=False):
            if conditional_groups:
                render_pv_card_grid(
                    _workspace_group_cards(conditional_groups, kicker="Conditional"),
                    min_width=250,
                )
            if downstream_groups:
                render_pv_card_grid(
                    _workspace_group_cards(downstream_groups, kicker="Reference"),
                    min_width=250,
                )
