from __future__ import annotations

from typing import Any, Literal
from uuid import uuid4

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
        "action": "데이터 품질 / 편향 통제 상세에서 가격 window, 운용사 / 공식 외부 데이터 freshness, lifecycle / survivorship 부족 항목을 확인하고 수집 가능한 gap은 Flow4 데이터 보강 / 수집 실행에서 처리합니다.",
    },
    "Data Coverage": {
        "location": "Flow4 > 데이터 > 데이터 품질 / 편향 통제 상세",
        "action": "데이터 품질 / 편향 통제 상세에서 가격 window, 운용사 / 공식 외부 데이터 freshness, lifecycle / survivorship 부족 항목을 확인하고 수집 가능한 gap은 Flow4 데이터 보강 / 수집 실행에서 처리합니다.",
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
        detail="카테고리별 결론과 Final Review 이동 가능 여부를 확인합니다. 상세 원인과 보강 기준은 Flow 4에서 확인합니다.",
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
        if group.get("visible_in_practical_validation") is False:
            continue
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
    if int(group.get("pv_practical_caution_count") or 0):
        return "주의", str(group.get("decision_summary") or "2단계 실용성 주의 항목이 있습니다."), "warning"
    if int(group.get("pv_data_caution_count") or 0):
        return "주의", str(group.get("decision_summary") or "데이터 주의 항목이 있습니다."), "warning"
    if int(group.get("final_review_reference_count") or 0):
        return "참고", str(group.get("decision_summary") or "최종 판단 참고 항목입니다."), "neutral"
    if int(group.get("monitoring_followup_count") or 0):
        return "추적", str(group.get("decision_summary") or "Monitoring 추적 항목입니다."), "neutral"
    if passed:
        return "통과", " / ".join(passed), "positive"
    if group.get("visible_in_practical_validation") is False:
        return "확인 필요", str(group.get("decision_summary") or "-"), "warning"
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
        detail=(
            "카테고리별 통과 / 실패와 Final Review 이동 가능 여부를 확인합니다. "
            "상세 원인과 보강 기준은 Flow 4에서 확인합니다."
        ),
        tone=str(summary.get("overall_outcome_tone") or ("positive" if gate_summary.get("can_save_and_move") else "danger")),
    )
    render_pv_card_grid(cards, min_width=250)
    final_review_limit_count = max(int(summary.get("final_review_limit_count") or 0), 0)
    if final_review_limit_count:
        st.caption(
            f"Final Review 판단에 반영할 한계 {final_review_limit_count}건 · "
            "즉시 해결하거나 개발해야 할 차단 항목은 위 Gate에서 별도로 확인합니다."
        )


def _render_next_stage_action_fallback(next_stage_action: dict[str, Any]) -> dict[str, Any] | None:
    primary = dict(next_stage_action.get("primary_action") or {})
    secondary = dict(next_stage_action.get("secondary_action") or {})
    primary_enabled = bool(primary.get("enabled"))
    secondary_enabled = bool(secondary.get("enabled", True))
    action_cols = st.columns(2, gap="small")
    with action_cols[0]:
        if st.button(
            str(primary.get("label") or "저장하고 Final Review로 이동"),
            key="practical_validation_flow3_save_and_move",
            width="stretch",
            disabled=not primary_enabled,
        ):
            return {"action": "save_and_move", "source": "practical_validation_fix_queue_fallback"}
    with action_cols[1]:
        if st.button(
            str(secondary.get("label") or "검증 결과 저장(기록용)"),
            key="practical_validation_flow3_save_audit_only",
            width="stretch",
            disabled=not secondary_enabled,
        ):
            return {"action": "save_audit_only", "source": "practical_validation_fix_queue_fallback"}
    detail = secondary.get("detail") or next_stage_action.get("boundary_note")
    boundary_note = str(next_stage_action.get("boundary_note") or "")
    if detail:
        st.caption(str(detail))
    if boundary_note and str(detail or "") != boundary_note:
        st.caption(boundary_note)
    return None


def render_practical_validation_workspace_overview(validation_result: dict[str, Any], *, source: dict[str, Any] | None = None) -> dict[str, Any] | None:
    workspace = dict(validation_result.get("practical_validation_workspace") or {})
    summary = dict(workspace.get("summary") or {})
    gate_summary = dict(workspace.get("gate_summary") or validation_result.get("final_review_gate") or {})
    fix_queue = list(workspace.get("fix_queue") or gate_summary.get("blocking_modules") or [])
    core_groups = list(workspace.get("core_evidence_groups") or [])
    criteria_groups = list(workspace.get("visible_criteria_detail_groups") or workspace.get("criteria_detail_groups") or [])
    next_stage_action = dict(workspace.get("next_stage_action") or {})
    primary_action = dict(next_stage_action.get("primary_action") or {})
    practical_validation_ready = bool(primary_action.get("enabled", gate_summary.get("can_save_and_move")))
    practical_status_label = str(summary.get("overall_outcome_label") or validation_status_label(gate_summary.get("route")))
    practical_tone = str(summary.get("overall_outcome_tone") or ("positive" if practical_validation_ready else "danger"))
    practical_verdict = str(summary.get("overall_outcome_headline") or "Practical Validation 검증 결론")
    practical_next_action = str(summary.get("overall_outcome_detail") or "")

    if is_practical_validation_fix_queue_available():
        return render_practical_validation_fix_queue(
            status_label=practical_status_label,
            tone=practical_tone,
            verdict=practical_verdict,
            next_action=practical_next_action,
            can_save_and_move=practical_validation_ready,
            final_review_limit_count=int(summary.get("final_review_limit_count") or 0),
            fix_items=_react_fix_queue_items(fix_queue),
            core_groups=_react_core_group_items(core_groups),
            criteria_groups=_react_criteria_group_items(criteria_groups),
            next_stage_action=next_stage_action,
            key="practical_validation_fix_queue_overview",
        )
    _render_validation_conclusion_summary(
        gate_summary=gate_summary,
        summary=summary,
        criteria_groups=criteria_groups,
    )
    return _render_next_stage_action_fallback(next_stage_action)


def _workspace_intent(
    action: str,
    *,
    workspace: dict[str, Any],
    **extra: Any,
) -> dict[str, Any]:
    return {
        "action": action,
        "intent_id": f"{action}-{uuid4()}",
        "selection_source_id": str(workspace.get("selection_source_id") or ""),
        "validation_result_id": str(workspace.get("validation_result_id") or ""),
        **extra,
    }


def _render_workspace_issue_lane(
    *,
    title: str,
    issues: list[dict[str, Any]],
    workspace: dict[str, Any],
    action_enabled: bool,
    detail: str = "",
) -> dict[str, Any] | None:
    if not issues:
        return None
    st.markdown(f"##### {title}")
    if detail:
        st.caption(detail)
    for issue in issues:
        root_issue_id = str(issue.get("root_issue_id") or "issue")
        with st.container(border=True):
            st.markdown(f"**{issue.get('title') or root_issue_id}**")
            observed = str(issue.get("observed") or "").strip()
            if observed:
                st.caption(observed)
            completion = str(issue.get("completion_criteria") or "").strip()
            if completion:
                st.caption(completion)
            action_id = str(issue.get("action_id") or "").strip()
            if action_enabled and issue.get("actionable_now") and action_id:
                if st.button(
                    str(issue.get("action_label") or "지금 해결"),
                    key=f"pv2-fallback-resolution-{root_issue_id}",
                    width="stretch",
                ):
                    return _workspace_intent(
                        "run_resolution_action",
                        workspace=workspace,
                        root_issue_id=root_issue_id,
                        action_id=action_id,
                    )
    return None


def _render_practical_validation_context_surface_fallback(
    workspace: dict[str, Any],
) -> dict[str, Any] | None:
    """Render only candidate and policy selection outside the replay fragment."""

    header = dict(workspace.get("header") or {})
    candidate = dict(workspace.get("candidate") or {})
    selector = dict(workspace.get("candidate_selector") or {})
    profile = dict(workspace.get("profile") or {})
    source_options = [
        dict(row)
        for row in list(selector.get("options") or [])
        if isinstance(row, dict)
    ]
    profile_options = [
        dict(row)
        for row in list(profile.get("options") or [])
        if isinstance(row, dict)
    ]
    selected_profile = next(
        (row for row in profile_options if bool(row.get("selected"))),
        {},
    )

    st.markdown(
        f"### {header.get('question') or '이 후보는 Final Review에서 실제 투자 판단을 할 만큼 검증되었는가?'}"
    )
    st.caption(str(header.get("detail") or ""))
    st.markdown("#### 1. 후보와 검증 기준")
    summary_columns = st.columns((3, 1))
    with summary_columns[0]:
        st.caption("검증 대상")
        st.markdown(f"**{candidate.get('title') or '-'}**")
        st.caption(
            f"{candidate.get('source_type_label') or '-'} · "
            f"{candidate.get('as_of') or '-'}"
        )
    with summary_columns[1]:
        st.caption("판정 기준")
        st.markdown(f"**{selected_profile.get('label') or '미선택'}**")

    with st.expander("1A. 후보 변경", expanded=False):
        if source_options:
            for option in source_options:
                option_id = str(option.get("selection_source_id") or "")
                if bool(option.get("selected")):
                    with st.container(border=True):
                        st.markdown(
                            f"**✓ {option.get('title') or option_id or '후보'}**"
                        )
                        st.caption(
                            str(option.get("source_type_label") or "검증 후보")
                        )
                    continue
                if st.button(
                    str(option.get("title") or option_id or "후보"),
                    key=f"pv2-fallback-source-{option_id}",
                    width="stretch",
                    disabled=not bool(option.get("eligible", True)),
                ):
                    return _workspace_intent(
                        "select_source",
                        workspace=workspace,
                        selection_source_id=option_id,
                    )
        else:
            st.info("Backtest Analysis에서 검증할 후보를 먼저 보내세요.")

    st.markdown("##### 1B. 어떤 관점으로 검증할까요?")
    st.caption(
        "포트폴리오 설계가 아니라 손실 허용도와 운용 목적에 맞는 판정 기준입니다."
    )
    for option in profile_options:
        profile_id = str(option.get("profile_id") or "")
        if bool(option.get("selected")):
            with st.container(border=True):
                st.markdown(
                    f"**✓ {option.get('label') or profile_id}**"
                )
                st.caption(str(option.get("description") or "현재 판정 기준"))
            continue
        if st.button(
            str(option.get("label") or profile_id),
            key=f"pv2-fallback-profile-{profile_id}",
            width="stretch",
        ):
            return _workspace_intent(
                "select_profile_preset",
                workspace=workspace,
                profile_id=profile_id,
            )
    questions = [
        dict(row)
        for row in list(profile.get("questions") or [])
        if isinstance(row, dict)
    ]
    with st.expander(
        "판정 기준 세부 조정",
        expanded=str(profile.get("profile_id") or "") == "custom",
    ):
        thresholds = dict(profile.get("threshold_summary") or {})
        st.caption(
            f"Rolling {int(thresholds.get('rolling_window_months') or 0)}개월 · "
            f"MDD 검토선 {float(thresholds.get('mdd_review_line') or 0.0):g}% · "
            f"편도 거래비용 {int(thresholds.get('one_way_cost_bps') or 0)} bps"
        )
        for question in questions:
            question_id = str(question.get("question_id") or "")
            options = [
                dict(row)
                for row in list(question.get("options") or [])
                if isinstance(row, dict)
            ]
            option_values = [str(row.get("value") or "") for row in options]
            labels = {
                str(row.get("value") or ""): str(row.get("label") or "")
                for row in options
            }
            current = str(question.get("value") or "")
            selected = st.selectbox(
                str(question.get("label") or question_id),
                options=option_values,
                format_func=lambda value, labels=labels: labels.get(value, value),
                index=option_values.index(current) if current in option_values else 0,
                key=f"pv2-fallback-profile-answer-{question_id}",
            )
            if selected != current:
                return _workspace_intent(
                    "update_profile_answer",
                    workspace=workspace,
                    question_id=question_id,
                    answer=selected,
                )
    return None


def render_practical_validation_decision_workspace_fallback(
    workspace: dict[str, Any],
    *,
    surface: Literal["context", "decision"] = "decision",
) -> dict[str, Any] | None:
    """Render one Python fallback surface from the shared read model."""

    if surface == "context":
        return _render_practical_validation_context_surface_fallback(workspace)

    replay = dict(workspace.get("replay") or {})
    verdict = dict(workspace.get("verdict") or {})
    summary = dict(workspace.get("summary") or {})
    resolution_lanes = dict(workspace.get("resolution_lanes") or {})
    actions = dict(workspace.get("actions") or {})

    st.markdown("#### 2. 최신 데이터 기준 재검증")
    mode_options = [
        dict(row)
        for row in list(replay.get("mode_options") or [])
        if isinstance(row, dict)
    ]
    mode_values = [str(row.get("value") or "") for row in mode_options]
    mode_labels = {
        str(row.get("value") or ""): str(row.get("label") or "")
        for row in mode_options
    }
    current_mode = str(replay.get("mode") or "")
    selected_mode = st.radio(
        "재검증 범위",
        options=mode_values,
        format_func=lambda value: mode_labels.get(value, value),
        index=mode_values.index(current_mode) if current_mode in mode_values else 0,
        horizontal=True,
        key="pv2-fallback-recheck-mode",
    )
    if selected_mode != current_mode:
        return _workspace_intent(
            "select_recheck_mode",
            workspace=workspace,
            recheck_mode=selected_mode,
        )
    st.caption(
        f"현재 상태: {replay.get('status') or 'NOT_RUN'} · "
        f"{replay.get('replay_id') or '아직 실행하지 않음'}"
    )
    replay_action = dict(actions.get("run_replay") or {})
    if st.button(
        str(replay_action.get("label") or "최신 데이터 기준 재검증"),
        key="pv2-fallback-run-replay",
        width="stretch",
        disabled=not bool(replay_action.get("enabled")),
    ):
        return _workspace_intent("run_replay", workspace=workspace)

    st.markdown(f"### {verdict.get('headline') or '-'}")
    st.caption(str(verdict.get("detail") or ""))
    metric_labels = (
        ("verified_count", "검증됨"),
        ("measured_caution_count", "측정 주의"),
        ("validated_caution_count", "Level2 주의"),
        ("resolve_now_count", "지금 해결"),
        ("engineering_blocker_count", "개발 차단"),
        ("accepted_limit_count", "인수할 한계"),
        ("final_decision_count", "최종 판단"),
        ("monitoring_transfer_count", "Monitoring"),
    )
    metric_columns = st.columns(len(metric_labels), gap="small")
    for column, (key, label) in zip(metric_columns, metric_labels):
        column.metric(label, int(summary.get(key) or 0))

    st.markdown("#### 3. 결과 해석과 해결 구분")
    verified = [
        dict(row)
        for row in list(workspace.get("verified_findings") or [])[:8]
        if isinstance(row, dict)
    ]
    if verified:
        st.markdown("##### 검증된 내용")
        for item in verified:
            with st.container(border=True):
                st.markdown(
                    f"**{item.get('display_title') or '검증 통과'}** "
                    f"· {item.get('status_label') or '확인 완료'}"
                )
                st.caption(str(item.get("what_was_checked") or ""))
                st.write(str(item.get("result_summary") or ""))
                st.caption(str(item.get("meaning") or ""))

    intent = _render_workspace_issue_lane(
        title="주의해서 볼 결과",
        issues=[
            dict(row)
            for row in list(workspace.get("measured_cautions") or [])
            if isinstance(row, dict)
        ],
        workspace=workspace,
        action_enabled=False,
    )
    if intent:
        return intent
    intent = _render_workspace_issue_lane(
        title="지금 해야 할 일",
        issues=[
            dict(row)
            for row in list(resolution_lanes.get("resolve_now") or [])
            if isinstance(row, dict)
        ],
        workspace=workspace,
        action_enabled=True,
    )
    if intent:
        return intent
    intent = _render_workspace_issue_lane(
        title="개발 후 재검토",
        issues=[
            dict(row)
            for row in list(resolution_lanes.get("engineering_required") or [])
            if isinstance(row, dict)
        ],
        workspace=workspace,
        action_enabled=False,
    )
    if intent:
        return intent
    handoff_summary = dict(workspace.get("handoff_summary") or {})
    handoff_items = [
        dict(row)
        for row in list(handoff_summary.get("items") or [])
        if isinstance(row, dict)
    ]
    if handoff_items:
        st.markdown(
            f"##### {handoff_summary.get('title') or 'Final Review 인계 준비'}"
        )
        st.caption(str(handoff_summary.get("detail") or ""))
        for item in handoff_items:
            with st.container(border=True):
                st.caption(str(item.get("handoff_label") or "Final Review 인계"))
                st.markdown(f"**{item.get('title') or item.get('root_issue_id')}**")
                st.write(str(item.get("summary") or ""))
                st.caption(str(item.get("next_stage_action") or ""))

    with st.expander("상세 검증 근거", expanded=False):
        groups = [
            dict(row)
            for row in list(workspace.get("category_disclosures") or [])
            if isinstance(row, dict)
        ]
        if groups:
            group_labels = {
                str(group.get("category_id") or index): (
                    f"{group.get('title') or '검증 범주'} · "
                    f"{dict(group.get('summary') or {}).get('total_count') or 0}개"
                )
                for index, group in enumerate(groups)
            }
            selected_group_id = st.selectbox(
                "상세 검증 범주",
                options=list(group_labels),
                format_func=lambda value: group_labels[value],
                key="pv2-fallback-evidence-category",
            )
            group = next(
                row
                for row in groups
                if str(row.get("category_id") or groups.index(row))
                == selected_group_id
            )
            st.markdown(
                f"**{group.get('title') or '검증 범주'}** · "
                f"{group.get('outcome') or '근거 없음'}"
            )
            st.caption(str(group.get("question") or ""))
            for explanation in [
                dict(item)
                for item in list(group.get("explanations") or [])
                if isinstance(item, dict)
            ]:
                with st.container(border=True):
                    st.markdown(
                        f"**{explanation.get('display_title') or '검증 항목'}** "
                        f"· {explanation.get('status_label') or '확인 필요'}"
                    )
                    st.caption(
                        f"무엇을 확인했나 · "
                        f"{explanation.get('what_was_checked') or '-'}"
                    )
                    st.write(
                        f"확인 결과 · "
                        f"{explanation.get('result_summary') or '-'}"
                    )
                    st.write(
                        f"이 결과의 의미 · "
                        f"{explanation.get('meaning') or '-'}"
                    )
                    st.info(
                        f"다음 조치 · "
                        f"{explanation.get('next_action') or '-'}"
                    )
                    with st.expander("기술 원문", expanded=False):
                        st.json(
                            dict(explanation.get("technical_trace") or {}),
                            expanded=False,
                        )

    st.markdown("#### 4. 저장하고 Final Review로 이동")
    save_only = dict(actions.get("save_audit_only") or {})
    save_and_move = dict(actions.get("save_and_move") or {})
    left, right = st.columns(2, gap="small")
    with left:
        if st.button(
            str(save_only.get("label") or "검증 결과 저장"),
            key="pv2-fallback-save-audit",
            width="stretch",
            disabled=not bool(save_only.get("enabled")),
        ):
            return _workspace_intent("save_audit_only", workspace=workspace)
    with right:
        if st.button(
            str(save_and_move.get("label") or "저장하고 Final Review로 이동"),
            key="pv2-fallback-save-move",
            width="stretch",
            disabled=not bool(save_and_move.get("enabled")),
        ):
            return _workspace_intent("save_and_move", workspace=workspace)
    st.caption("이동은 최종 승인, broker order, account sync, auto rebalance가 아닙니다.")
    return None
