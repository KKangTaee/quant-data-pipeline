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
        "location": "Flow 2 · 실전 재검증 실행",
        "action": "`전략 재검증 실행` 버튼을 누른 뒤 Recheck가 PASS 또는 REVIEW이고 Coverage가 PASS인지 확인합니다.",
    },
    "Latest Runtime Replay": {
        "location": "Flow 2 · 실전 재검증 실행",
        "action": "`전략 재검증 실행` 버튼을 누른 뒤 Recheck가 PASS 또는 REVIEW이고 Coverage가 PASS인지 확인합니다.",
    },
    "validation_efficacy": {
        "location": "Flow4 > 실전성 > 검증 강도 / 강건성 상세",
        "action": "검증 강도 / 강건성 상세에서 walk-forward / OOS / regime / PIT / survivorship 근거 중 부족한 항목을 보강합니다.",
    },
    "Validation Efficacy": {
        "location": "Flow4 > 실전성 > 검증 강도 / 강건성 상세",
        "action": "검증 강도 / 강건성 상세에서 walk-forward / OOS / regime / PIT / survivorship 근거 중 부족한 항목을 보강합니다.",
    },
    "data_coverage": {
        "location": "Flow4 > 데이터 > 데이터 품질 / 편향 통제 상세",
        "action": "데이터 품질 / 편향 통제 상세에서 가격 window, provider freshness, lifecycle / survivorship 부족 항목을 확인하고 provider gap은 Provider / Data 보강 액션에서 수집합니다.",
    },
    "Data Coverage": {
        "location": "Flow4 > 데이터 > 데이터 품질 / 편향 통제 상세",
        "action": "데이터 품질 / 편향 통제 상세에서 가격 window, provider freshness, lifecycle / survivorship 부족 항목을 확인하고 provider gap은 Provider / Data 보강 액션에서 수집합니다.",
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
                    "kicker": "검증 결론",
                    "title": "이동 보류 항목 없음",
                    "status": "PASS",
                    "detail": "Final Review 이동을 즉시 막는 검증 카테고리가 없습니다.",
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
        eyebrow="검증 결론",
        title=f"이동 보류 항목 {len(blocking_modules)}개",
        detail="Flow 3에서는 결론만 요약합니다. 상세 원인과 보강 기준은 Flow 4에서 확인합니다.",
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
                "status": group.get("display_status") or group.get("status") or "-",
                "purpose": group.get("purpose") or f"{len(cards)} criteria",
                "passedCriteria": list(group.get("passed_criteria") or []),
                "remainingIssues": list(group.get("remaining_issues") or []),
                "reviewCriteria": [],
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


def _conclusion_group_detail(group: dict[str, Any]) -> tuple[str, str, str]:
    remaining = [str(item) for item in list(group.get("remaining_issues") or []) if str(item).strip()]
    review = [str(item) for item in list(group.get("review_criteria") or []) if str(item).strip()]
    passed = [str(item) for item in list(group.get("passed_criteria") or []) if str(item).strip()]
    if remaining:
        return "실패", " / ".join(remaining), "danger"
    if passed:
        return "통과", " / ".join(passed), "positive"
    if review or int(group.get("final_review_reference_count") or 0):
        return "통과", str(group.get("decision_summary") or "Practical Validation에서 보강할 항목은 없습니다."), "positive"
    return "확인 필요", str(group.get("decision_summary") or "-"), str(group.get("tone") or "neutral")


def _render_validation_conclusion_summary(
    *,
    gate_summary: dict[str, Any],
    summary: dict[str, Any],
    criteria_groups: list[dict[str, Any]],
) -> None:
    cards: list[dict[str, Any]] = []
    for group in criteria_groups:
        label, detail, tone = _conclusion_group_detail(dict(group or {}))
        cards.append(
            {
                "kicker": label,
                "title": group.get("display_label") or group.get("label") or group.get("group_id") or "-",
                "status": group.get("status") or "-",
                "detail": detail,
                "tone": tone,
            }
        )
    if not cards:
        cards = [
            {
                "kicker": "검증 결론",
                "title": "검증 카테고리 없음",
                "status": "-",
                "detail": "workspace read model에 표시할 카테고리별 검증 요약이 없습니다.",
                "tone": "neutral",
            }
        ]
    render_pv_section_header(
        eyebrow="검증 결론",
        title=str(summary.get("overall_outcome_headline") or "Practical Validation 검증 결론"),
        detail="카테고리별 통과 / 실패만 요약합니다. 자세한 원인과 보강 기준은 Flow 4에서 확인합니다.",
        tone=str(summary.get("overall_outcome_tone") or ("positive" if gate_summary.get("can_save_and_move") else "danger")),
    )
    render_pv_card_grid(cards, min_width=250)


def render_practical_validation_workspace_overview(validation_result: dict[str, Any]) -> None:
    workspace = dict(validation_result.get("practical_validation_workspace") or {})
    summary = dict(workspace.get("summary") or {})
    gate_summary = dict(workspace.get("gate_summary") or validation_result.get("final_review_gate") or {})
    fix_queue = list(workspace.get("fix_queue") or gate_summary.get("blocking_modules") or [])
    core_groups = list(workspace.get("core_evidence_groups") or [])
    conditional_groups = list(workspace.get("conditional_evidence_groups") or [])
    downstream_groups = list(workspace.get("downstream_reference_groups") or [])
    criteria_groups = list(workspace.get("criteria_detail_groups") or [])
    repair_count = int(summary.get("criteria_repair_count") or 0)
    not_practical_count = int(summary.get("criteria_not_practical_count") or 0)
    practical_validation_ready = repair_count == 0 and not_practical_count == 0
    practical_status_label = str(summary.get("overall_outcome_label") or validation_status_label(gate_summary.get("route")))
    practical_tone = str(summary.get("overall_outcome_tone") or ("positive" if practical_validation_ready else "danger"))
    practical_verdict = str(summary.get("overall_outcome_headline") or "Practical Validation 검증 결론")
    practical_next_action = str(summary.get("overall_outcome_detail") or "")

    if is_practical_validation_fix_queue_available():
        render_practical_validation_fix_queue(
            status_label=practical_status_label,
            tone=practical_tone,
            verdict=practical_verdict,
            next_action=practical_next_action,
            can_save_and_move=practical_validation_ready,
            fix_items=_react_fix_queue_items(fix_queue),
            core_groups=_react_core_group_items(core_groups),
            criteria_groups=_react_criteria_group_items(criteria_groups),
            key="practical_validation_fix_queue_overview",
        )
    else:
        _render_validation_conclusion_summary(
            gate_summary=gate_summary,
            summary=summary,
            criteria_groups=criteria_groups,
        )
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
