from __future__ import annotations

from datetime import date
from typing import Any
from uuid import uuid4

import pandas as pd
import streamlit as st

from app.services.backtest_evidence_read_model import (
    SELECT_FOR_PRACTICAL_PORTFOLIO,
    build_final_review_candidate_board,
    build_final_review_decision_cockpit,
    build_final_review_decision_record_guide,
)
from app.services.backtest_final_review_decision_brief import (
    build_final_review_candidate_selector,
    build_final_review_decision_brief,
    validate_accepted_limit_acknowledgements,
)
from app.services.backtest_final_review_refresh import (
    build_final_review_refresh_status,
    run_final_review_observation_refresh,
)
from app.web.backtest_final_review_helpers import (
    FINAL_REVIEW_DECISION_LABELS,
    FINAL_REVIEW_ROUTE_OPTIONS,
    FINAL_REVIEW_ROUTE_DESCRIPTIONS,
    _build_investability_evidence_packet,
    _build_final_review_decision_evidence_pack,
    _build_final_review_decision_row,
    _build_final_review_paper_observation_snapshot,
    _build_final_review_save_evaluation,
    _build_final_review_source_options,
    _build_final_review_validation,
    _is_final_review_eligible_validation_result,
    _latest_practical_validation_rows_by_source,
)
from app.web.backtest_final_review.components import (
    render_fr_action_panel,
    render_fr_command_center,
)
from app.web.components.final_review_investment_report import (
    is_final_review_decision_workspace_available,
    render_final_review_decision_workspace,
)
from app.web.backtest_portfolio_proposal_helpers import _paper_ledger_slug
from app.web.backtest_workflow_routes import (
    BACKTEST_STAGE_PRACTICAL_VALIDATION,
    PRACTICAL_VALIDATION_MODE_SELECTED_SOURCE,
)
from app.web.backtest_ui_components import (
    render_badge_strip,
)
from app.runtime import (
    append_current_final_selection_decision,
    build_selected_dashboard_handoff_review,
    load_current_candidate_registry_latest,
    load_current_final_selection_decisions,
    load_portfolio_proposals,
    load_pre_live_candidate_registry_latest,
    load_practical_validation_results,
)


def _candidate_board_route(summary: dict[str, Any]) -> tuple[str, str, str]:
    if not int(summary.get("total_candidates", 0) or 0):
        return "검토 후보 없음", "Final Review Gate를 통과한 후보가 없습니다.", "warning"
    if int(summary.get("select_ready", 0) or 0) > 0:
        return "모니터링 후보 있음", "저장 가능한 후보를 확인하고 Portfolio Monitoring 추적 후보로 저장합니다.", "positive"
    if int(summary.get("recheck_required", 0) or 0) > 0:
        return "2단계 재검증 필요", "필수 데이터를 보강하고 새 Practical Validation 결과를 저장한 뒤 다시 검토합니다.", "warning"
    if int(summary.get("blocked", 0) or 0) > 0:
        return "차단 원인 확인", "먼저 볼 후보의 blocker를 해소해야 정식 저장이 활성화됩니다.", "danger"
    return "재검토 필요", "review-required 근거를 확인하고 모니터링 후보 가능 상태로 보강합니다.", "warning"


_FINAL_REVIEW_ROUTE_BUTTON_LABELS = {
    SELECT_FOR_PRACTICAL_PORTFOLIO: "모니터링 후보로 선정",
    "HOLD_FOR_MORE_PAPER_TRACKING": "보류로 기록",
    "REJECT_FOR_PRACTICAL_USE": "탈락으로 기록",
    "RE_REVIEW_REQUIRED": "재검토로 기록",
}

_FINAL_REVIEW_ROUTE_TONES = {
    SELECT_FOR_PRACTICAL_PORTFOLIO: "positive",
    "HOLD_FOR_MORE_PAPER_TRACKING": "warning",
    "REJECT_FOR_PRACTICAL_USE": "danger",
    "RE_REVIEW_REQUIRED": "warning",
}


def _build_final_review_decision_action_model(
    *,
    cockpit: dict[str, Any],
    evidence: dict[str, Any],
    investability_packet: dict[str, Any],
    decision_id: str,
    existing_decision_ids: set[str],
    data_enrichment_action: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the display-only route choices used by the React decision intent form."""

    gate_policy_snapshot = dict(investability_packet.get("gate_policy_snapshot") or {})
    suggested_route = str(
        gate_policy_snapshot.get("suggested_decision_route")
        or evidence.get("suggested_decision_route")
        or cockpit.get("suggested_decision_route")
        or SELECT_FOR_PRACTICAL_PORTFOLIO
    )
    route_options = list(FINAL_REVIEW_ROUTE_OPTIONS)
    if suggested_route not in route_options:
        route_options.append(suggested_route)

    recovery_action = dict(data_enrichment_action or {})
    recovery_required = bool(recovery_action.get("available"))
    recovery_next_step = str(
        recovery_action.get("next_step")
        or "Flow 2 재검증 결과를 새로 저장해야 합니다."
    )
    recovery_reason = f"2단계 데이터 보강 후 재검증이 필요합니다. {recovery_next_step}"
    if recovery_required:
        suggested_route = "RE_REVIEW_REQUIRED"
    options: list[dict[str, Any]] = []
    for route in route_options:
        guide = build_final_review_decision_record_guide(
            decision_route=route,
            decision_evidence=evidence,
            investability_packet=investability_packet,
        )
        templates = dict(guide.get("route_templates") or {})
        preview = _build_final_review_save_evaluation(
            evidence=evidence,
            investability_packet=investability_packet,
            decision_id=decision_id,
            decision_route=route,
            operator_reason="preview reason",
            existing_decision_ids=existing_decision_ids,
        )
        disabled_reason = (
            recovery_reason
            if recovery_required
            else " · ".join(str(item) for item in list(preview.get("blockers") or []))
        )
        reason_placeholder = str(templates.get("reason") or "왜 이 판단을 선택했는지 직접 작성합니다.")
        if route == SELECT_FOR_PRACTICAL_PORTFOLIO and not bool(preview.get("can_save")):
            reason_placeholder = "현재 blocker가 남아 있어 Monitoring 후보로 선정할 수 없습니다. 다른 판단을 선택하거나 근거를 보강합니다."
        options.append(
            {
                "route": route,
                "label": FINAL_REVIEW_DECISION_LABELS.get(route, route),
                "description": FINAL_REVIEW_ROUTE_DESCRIPTIONS.get(route, "최종 판단 기록으로 저장합니다."),
                "tone": _FINAL_REVIEW_ROUTE_TONES.get(route, "neutral"),
                "recordable": bool(preview.get("can_save")) and not recovery_required,
                "disabled_reason": disabled_reason,
                "reason_placeholder": reason_placeholder,
                "button_label": _FINAL_REVIEW_ROUTE_BUTTON_LABELS.get(route, "최종 판단 저장"),
            }
        )

    return {
        "title": (
            "2단계 재검증 후 최종 판단을 기록합니다"
            if recovery_required
            else "이 후보를 Monitoring 대상으로 기록할까요?"
        ),
        "detail": (
            recovery_reason
            if recovery_required
            else str(cockpit.get("verdict") or "투자 검토서의 총평과 핵심 해석을 바탕으로 최종 판단을 기록합니다.")
        ),
        "status_label": (
            "2단계 재검증 필요"
            if recovery_required
            else str(cockpit.get("state_label") or "판단 확인")
        ),
        "suggested_route": suggested_route,
        "suggested_label": FINAL_REVIEW_DECISION_LABELS.get(suggested_route, suggested_route),
        "reason_label": "판단 사유",
        "reason_help": "자동 문구가 아닌 사용자의 판단 이유를 남겨야 저장 버튼이 활성화됩니다.",
        "boundary_note": "이 판단은 Portfolio Monitoring 후보 기록이며 실제 투자 승인, 주문 또는 자동 리밸런싱이 아닙니다.",
        "options": options,
    }


def _render_final_review_decision_fallback(
    decision_action: dict[str, Any],
    *,
    key: str,
    accepted_limit_acknowledgements: list[dict[str, str]] | None = None,
    accepted_limits_complete: bool = True,
    requires_re_review_route: bool = False,
) -> dict[str, Any] | None:
    """Keep the same compact action contract if the optional React build is unavailable."""

    options = list(decision_action.get("options") or [])
    if not options:
        return None
    route_values = [str(option.get("route") or "") for option in options]
    suggested_route = str(decision_action.get("suggested_route") or route_values[0])
    selected_route = st.radio(
        "최종 판단",
        options=route_values,
        index=route_values.index(suggested_route) if suggested_route in route_values else 0,
        format_func=lambda route: str(
            next((option.get("label") for option in options if option.get("route") == route), route)
        ),
        horizontal=True,
        key=f"{key}_route",
    )
    selected = next(option for option in options if option.get("route") == selected_route)
    reason = st.text_area(
        "판단 사유",
        placeholder=str(selected.get("reason_placeholder") or "왜 이 판단을 선택했는지 직접 작성합니다."),
        key=f"{key}_reason_{_paper_ledger_slug(selected_route)}",
    )
    can_submit = (
        bool(selected.get("recordable"))
        and bool(str(reason or "").strip())
        and accepted_limits_complete
        and (not requires_re_review_route or selected_route == "RE_REVIEW_REQUIRED")
    )
    if not bool(selected.get("recordable")):
        st.error(str(selected.get("disabled_reason") or "현재 조건에서는 이 판단을 저장할 수 없습니다."))
    if requires_re_review_route and selected_route != "RE_REVIEW_REQUIRED":
        st.error("Level2로 되돌리기를 선택했으므로 최종 판단도 재검토 필요를 선택하세요.")
    if st.button(
        str(selected.get("button_label") or "최종 판단 저장"),
        key=f"{key}_submit",
        disabled=not can_submit,
        width="stretch",
    ):
        return {
            "action": "record_final_decision",
            "intent_id": uuid4().hex,
            "decision_route": selected_route,
            "operator_reason": str(reason or "").strip(),
            "accepted_limit_acknowledgements": list(
                accepted_limit_acknowledgements or []
            ),
        }
    st.caption(str(decision_action.get("boundary_note") or ""))
    return None


def _build_final_review_top_summary() -> dict[str, str]:
    return {
        "title": "Final Review",
        "caption": (
            "Gate 통과 후보 중 모니터링 후보로 저장할 대상을 고릅니다. "
            "선정 후 확인은 Operations > Portfolio Monitoring에서 이어집니다."
        ),
        "destination": "Operations > Portfolio Monitoring",
    }


def _build_final_review_decision_desk_model(
    *,
    candidate_summary: dict[str, Any],
    practical_validation_count: int,
    eligible_count: int,
    hidden_validation_count: int,
    final_decision_count: int,
    dashboard_selected_count: int,
    route_value: str,
    route_detail: str,
    route_tone: str,
) -> dict[str, Any]:
    first_candidate = str(candidate_summary.get("first_review_candidate") or "-")
    first_reason = str(candidate_summary.get("first_review_reason") or "-")
    first_action = str(candidate_summary.get("first_review_action") or "-")
    has_candidate = first_candidate not in {"", "-"}
    has_select_ready = int(candidate_summary.get("select_ready", 0) or 0) > 0
    monitoring_badge = "연결 가능" if route_tone == "positive" else "확인 필요"
    return {
        "eyebrow": "Final Review Decision Desk",
        "title": "후보 현황과 다음 판단",
        "detail": (
            f"Gate 통과 후보 {eligible_count}개를 비교합니다. "
            f"저장된 Practical Validation 기록 {practical_validation_count}개 중 "
            f"{hidden_validation_count}개는 Gate 미통과로 숨겨졌습니다."
        ),
        "route_label": "오늘 먼저 볼 후보",
        "route_value": route_value,
        "route_detail": route_detail,
        "route_tone": route_tone,
        "featured_candidate": {
            "candidate": first_candidate if has_candidate else "검토 후보 없음",
            "reason": first_reason if first_reason != "-" else "먼저 볼 후보가 없습니다.",
            "recommendation": route_detail,
            "next_action": first_action if first_action != "-" else "Practical Validation에서 Gate 통과 후보를 먼저 만듭니다.",
            "badges": [
                {
                    "label": "Gate",
                    "value": "통과" if has_select_ready else "재검증 필요" if has_candidate else "대상 없음",
                },
                {"label": "선택 가능", "value": int(candidate_summary.get("select_ready", 0) or 0)},
                {"label": "Monitoring", "value": monitoring_badge},
            ],
        },
        "kpis": [
            {
                "label": "올라온 후보",
                "value": int(candidate_summary.get("total_candidates", 0) or 0),
                "detail": "Gate 통과 후 비교 대상",
            },
            {
                "label": "선택 가능",
                "value": int(candidate_summary.get("select_ready", 0) or 0),
                "detail": "모니터링 후보 저장 가능",
            },
            {
                "label": "보류 / 재검토",
                "value": int(candidate_summary.get("hold_or_re_review", 0) or 0),
                "detail": "추가 판단 또는 근거 보강",
            },
            {"label": "숨김", "value": hidden_validation_count, "detail": "Gate 미통과 기록"},
            {"label": "저장된 판단", "value": final_decision_count, "detail": "Final Review record"},
            {
                "label": "Monitoring 연결",
                "value": dashboard_selected_count,
                "detail": "Portfolio Monitoring 대상",
            },
        ],
    }


def _build_candidate_contexts(
    source_options: list[dict[str, Any]],
    *,
    current_rows: list[dict[str, Any]],
    pre_live_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    contexts: list[dict[str, Any]] = []
    for option in source_options:
        source = dict(option or {})
        validation = _build_final_review_validation(source, current_rows=current_rows, pre_live_rows=pre_live_rows)
        paper_observation = _build_final_review_paper_observation_snapshot(validation)
        evidence = _build_final_review_decision_evidence_pack(validation, paper_observation)
        investability_packet = _build_investability_evidence_packet(source, validation, paper_observation, evidence)
        cockpit = build_final_review_decision_cockpit(
            source=source,
            validation=validation,
            paper_observation=paper_observation,
            decision_evidence=evidence,
            investability_packet=investability_packet,
        )
        contexts.append(
            {
                "label": str(option.get("label") or option.get("source_id") or "-"),
                "candidate_key": _final_review_candidate_key(
                    {
                        "source": source,
                        "validation": validation,
                    }
                ),
                "source": source,
                "validation": validation,
                "paper_observation": paper_observation,
                "decision_evidence": evidence,
                "investability_packet": investability_packet,
                "cockpit": cockpit,
            }
        )
    return contexts


def _final_review_candidate_key(context: dict[str, Any]) -> str:
    """Build a stable Final Review selector identity without using display labels."""

    source = dict(context.get("source") or {})
    validation = dict(context.get("validation") or {})
    source_type = str(source.get("source_type") or validation.get("source_type") or "unknown").strip()
    validation_id = str(validation.get("validation_id") or "").strip()
    selection_source_id = str(validation.get("selection_source_id") or "").strip()
    source_id = str(source.get("source_id") or "").strip()
    identity = validation_id or selection_source_id or source_id
    return f"{source_type}:{identity or 'missing'}"


def _default_candidate_key(
    candidate_contexts: list[dict[str, Any]],
    board_rows: list[dict[str, Any]],
) -> str:
    if not candidate_contexts:
        return ""
    first_row = dict(board_rows[0] or {}) if board_rows else {}
    first_validation_id = str(first_row.get("Validation ID") or "").strip()
    first_source_id = str(first_row.get("Source ID") or "").strip()
    for context in candidate_contexts:
        validation = dict(context.get("validation") or {})
        source = dict(context.get("source") or {})
        if first_validation_id not in {"", "-"} and first_validation_id == str(validation.get("validation_id") or "").strip():
            return str(context.get("candidate_key") or "")
        context_source_ids = {
            str(validation.get("selection_source_id") or "").strip(),
            str(source.get("source_id") or "").strip(),
        }
        if first_source_id not in {"", "-"} and first_source_id in context_source_ids:
            return str(context.get("candidate_key") or "")
    return str(candidate_contexts[0].get("candidate_key") or "")


def _render_candidate_selection_panel(candidate_contexts: list[dict[str, Any]]) -> dict[str, Any]:
    board = build_final_review_candidate_board(candidate_contexts)
    rows = list(board.get("rows") or [])
    if not candidate_contexts:
        st.info("표시할 Final Review 후보가 없습니다.")
        return {}
    st.markdown("###### 검토 대상")
    candidate_by_key = {
        str(context["candidate_key"]): context
        for context in candidate_contexts
    }
    candidate_keys = list(candidate_by_key)
    default_key = _default_candidate_key(candidate_contexts, rows)
    default_index = candidate_keys.index(default_key) if default_key in candidate_keys else 0
    selected_key = st.selectbox(
        "검토 대상",
        options=candidate_keys,
        index=default_index,
        key="final_review_source_selected",
        format_func=lambda candidate_key: str(candidate_by_key[candidate_key]["label"]),
    )
    selected_context = candidate_by_key[selected_key]
    confirmed_key = str(st.session_state.get("final_review_confirmed_candidate_key") or "")
    if st.button(
        "최종 검토서 확인",
        key="final_review_confirm_candidate",
        type="primary",
        width="stretch",
    ):
        confirmed_key = selected_key
        st.session_state["final_review_confirmed_candidate_key"] = selected_key
    is_confirmed = confirmed_key == selected_key
    if not is_confirmed and confirmed_key:
        st.warning("검토 대상이 변경되었습니다. 다시 확인하세요")
    elif not is_confirmed:
        st.info("검토 대상을 선택한 뒤 `최종 검토서 확인`을 눌러 저장된 evidence를 확인하세요.")
    st.caption(
        "이 버튼은 새 검증을 실행하지 않습니다. 저장된 Practical Validation evidence를 현재 후보 기준으로 읽어 "
        "투자 검토서와 최종 판단 화면을 엽니다."
    )
    source = dict(selected_context["source"])
    render_badge_strip(
        [
            {"label": "Source Type", "value": source.get("source_type") or "-", "tone": "neutral"},
            {"label": "Source ID", "value": source.get("source_id") or "-", "tone": "neutral"},
        ]
    )

    if rows:
        with st.expander("후보 비교 상세", expanded=False):
            st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
    st.caption(
        "후보 비교는 기존 Practical Validation result와 investability packet을 읽는 화면 정렬용 정보입니다. "
        "새 registry row를 만들거나 provider 데이터를 수집하지 않습니다."
    )
    return {
        "context": selected_context,
        "selected_key": selected_key,
        "confirmed_key": confirmed_key,
        "is_confirmed": is_confirmed,
    }


def _render_investment_report_fallback(report: dict[str, Any]) -> None:
    recommendation = dict(report.get("recommendation") or {})
    score = dict(report.get("score") or {})
    summary = dict(report.get("summary") or {})
    scorecard = dict(report.get("scorecard") or {})
    narrative = dict(report.get("report_narrative") or {})
    pattern_guide = dict(report.get("pattern_guide") or {})
    assessment = dict(narrative.get("total_assessment") or {})
    render_fr_action_panel(
        title=str(summary.get("headline") or "Final Review 투자 검토서"),
        detail=str(summary.get("verdict") or "-"),
        route_label="Recommendation",
        route_value=str(recommendation.get("label") or "-"),
        route_detail=str(summary.get("next_action") or "-"),
        route_tone=str(recommendation.get("tone") or "neutral"),
        meta_items=[
            {"label": "투자 매력도", "value": f"{float(score.get('value') or 0.0):.1f}"},
            {"label": "판단 상태", "value": recommendation.get("state_label") or "-"},
        ],
    )
    st.markdown(f"##### {assessment.get('label') or '총평'} · {assessment.get('headline') or '-'}")
    st.write(str(assessment.get("detail") or "-"))
    st.caption(str(narrative.get("boundary_note") or "-"))
    render_badge_strip(
        [
            {
                "label": item.get("label") or "-",
                "value": f"{float(item.get('score') or 0.0):.0f}/100",
                "tone": item.get("tone") or "neutral",
            }
            for item in list(scorecard.get("headline_scores") or [])
        ],
    )
    disposition = dict(report.get("level2_review_disposition") or {})
    unresolved_items = list(report.get("pre_selection_unresolved_items") or [])
    accepted_items = list(report.get("accepted_limits_and_decisions") or [])
    st.markdown("##### 선정 전 미해결 항목")
    if unresolved_items:
        st.dataframe(pd.DataFrame(unresolved_items), width="stretch", hide_index=True)
    else:
        st.success("현재 Final Review 후보의 선정 전 미해결 항목은 0개입니다.")
    st.markdown("##### 인수한 한계와 최종 판단 항목")
    if accepted_items:
        st.dataframe(pd.DataFrame(accepted_items), width="stretch", hide_index=True)
    else:
        st.caption("현재 Final Review에서 종결할 한계 또는 Monitoring 이관 항목이 없습니다.")
    role_sections = list(disposition.get("role_sections") or [])
    st.markdown("##### Final Review 확인 필요")
    st.caption(
        "저장된 Practical Validation evidence를 다시 실행하지 않고, 점수 반영 / 저장 전 확인 / "
        "Monitoring 조건 / blocker로 구분합니다."
    )
    render_badge_strip(
        [
            {
                "label": section.get("label") or "-",
                "value": f"{section.get('action_label') or '-'} · {int(section.get('count', 0) or 0)}",
                "tone": section.get("tone") or "neutral",
            }
            for section in role_sections
        ]
    )
    action_rows = [
        {
            "구분": section.get("label") or "-",
            "처리": section.get("action_label") or "-",
            "항목": item.get("title") or "-",
            "근거": item.get("detail") or "-",
            "다음 행동": item.get("action") or "-",
        }
        for section in role_sections
        for item in list(section.get("items") or [])
    ]
    if action_rows:
        st.dataframe(pd.DataFrame(action_rows), width="stretch", hide_index=True)
    else:
        st.success("Final Review에서 추가로 확인할 Level2 REVIEW 항목이 없습니다.")

    st.markdown("##### Monitoring 방향 가이드")
    pattern_rows = [
        {
            "패턴": card.get("label") or "-",
            "지원 수준": card.get("support_label") or "-",
            "해석": card.get("conclusion") or "-",
            "보강 필요": ", ".join(card.get("missing_signals") or []) or "없음",
        }
        for card in list(pattern_guide.get("cards") or [])
    ]
    if pattern_rows:
        st.dataframe(pd.DataFrame(pattern_rows), width="stretch", hide_index=True)

    report_tabs = st.tabs(["점수 근거", "남은 판단 근거", "다음 실험 아이디어"])
    with report_tabs[0]:
        render_badge_strip(
            [
                {"label": "투자 매력도", "value": f"{float(scorecard.get('overall_score') or 0.0):.0f}/100", "tone": "positive" if float(scorecard.get("overall_score") or 0.0) >= 70 else "warning"},
                {"label": "분류", "value": scorecard.get("classification_label") or "-", "tone": "neutral"},
                {"label": "REVIEW 개수 감점", "value": "없음", "tone": "positive"},
            ]
        )
        st.dataframe(pd.DataFrame(scorecard.get("dimensions") or []), width="stretch", hide_index=True)
    with report_tabs[1]:
        st.dataframe(
            pd.DataFrame(scorecard.get("review_impacts") or []),
            width="stretch",
            hide_index=True,
        )
    with report_tabs[2]:
        st.caption("설정 아이디어만 제공합니다. 점수 개선을 예측하거나 counterfactual backtest를 자동 실행하지 않습니다.")
        experiment_rows = [
            {
                "패턴": card.get("label") or "-",
                "바꿀 것": dict(card.get("experiment_plan") or {}).get("change") or "-",
                "같게 둘 것": dict(card.get("experiment_plan") or {}).get("comparison") or "-",
                "확인할 것": dict(card.get("experiment_plan") or {}).get("learning") or "-",
            }
            for card in sorted(
                [
                    dict(row or {})
                    for row in list(pattern_guide.get("cards") or [])
                    if isinstance(row, dict)
                    and row.get("applicable") is not False
                    and row.get("support") != "not_applicable"
                ],
                key=lambda row: -int(row.get("salience") or 0),
            )[:3]
        ]
        st.dataframe(pd.DataFrame(experiment_rows), width="stretch", hide_index=True)


def _render_investment_report(
    report: dict[str, Any],
    *,
    decision_action: dict[str, Any],
    key: str,
) -> dict[str, Any] | None:
    if is_final_review_investment_report_available():
        return render_final_review_investment_report(
            report=report,
            decision_action=decision_action,
            key=key,
        )
    _render_investment_report_fallback(report)
    return _render_final_review_decision_fallback(decision_action, key=key)


def _render_final_review_decision_brief_fallback(
    decision_brief: dict[str, Any],
    *,
    candidate_selector: dict[str, Any],
    key: str,
) -> dict[str, Any] | None:
    """Render the same compact Decision Brief when the React build is unavailable."""

    options = [dict(row or {}) for row in list(candidate_selector.get("options") or [])]
    active_option = next((row for row in options if row.get("selected")), options[0] if options else {})
    if options:
        source_ids = [str(row.get("source_id") or "") for row in options]
        active_source_id = str(active_option.get("source_id") or source_ids[0])
        selected_source_id = st.selectbox(
            "검토할 후보",
            options=source_ids,
            index=source_ids.index(active_source_id) if active_source_id in source_ids else 0,
            format_func=lambda source_id: str(
                next((row.get("title") for row in options if row.get("source_id") == source_id), source_id)
            ),
            key=f"{key}_candidate",
        )
        if selected_source_id != active_source_id:
            return {
                "action": "select_candidate",
                "intent_id": uuid4().hex,
                "source_id": selected_source_id,
            }

    verdict = dict(decision_brief.get("verdict") or {})
    behavior_board = dict(decision_brief.get("behavior_board") or {})
    strengths = list(decision_brief.get("strengths") or [])
    weaknesses = list(decision_brief.get("weaknesses") or [])
    character_profile = dict(decision_brief.get("character_profile") or {})
    review_pressure = dict(decision_brief.get("review_pressure") or {})
    monitoring_conditions = list(decision_brief.get("monitoring_conditions") or [])
    level2_handoff = dict(decision_brief.get("level2_handoff") or {})
    decision_action = dict(decision_brief.get("decision_action") or {})
    disclosures = dict(decision_brief.get("disclosures") or {})
    observation_freshness = dict(decision_brief.get("observation_freshness") or {})

    st.markdown(f"#### {verdict.get('headline') or '추적 가치 결론 미측정'}")
    st.write(str(verdict.get("thesis") or "비교 가능한 관측값이 없습니다."))
    period = dict(behavior_board.get("period") or {})
    st.caption(
        f"관측 기간 {period.get('start') or '미측정'} → {period.get('end') or '미측정'} · "
        f"frequency {period.get('frequency') or 'unknown'}"
    )
    with st.container(border=True):
        st.caption(
            f"{observation_freshness.get('label') or '관측 최신성'} · "
            f"{observation_freshness.get('summary') or '최신성 상태를 확인할 수 없습니다.'}"
        )
        freshness_columns = st.columns(4)
        freshness_columns[0].metric(
            "현재 차트",
            observation_freshness.get("stored_curve_end") or "미측정",
        )
        freshness_columns[1].metric(
            "최신 완료 시장일",
            observation_freshness.get("latest_completed_market_date") or "미측정",
        )
        freshness_columns[2].metric(
            "DB 공통일",
            observation_freshness.get("db_common_price_date") or "미측정",
        )
        freshness_columns[3].metric(
            "제한 종목",
            ", ".join(observation_freshness.get("limiting_symbols") or []) or "없음",
        )
        if observation_freshness.get("detail"):
            st.caption(str(observation_freshness["detail"]))
        if bool(observation_freshness.get("can_refresh")) and st.button(
            str(observation_freshness.get("button_label") or "최신 데이터로 다시 계산"),
            key=f"{key}_refresh_observation",
            type="primary",
        ):
            return {
                "action": "refresh_observation",
                "intent_id": uuid4().hex,
                "source_id": str(observation_freshness.get("selection_source_id") or ""),
                "validation_id": str(observation_freshness.get("validation_id") or ""),
            }

    series_rows = []
    for series_key in ("cumulative_series", "benchmark_series", "underwater_series"):
        series = dict(behavior_board.get(series_key) or {})
        series_rows.append(
            {
                "근거": series.get("label") or series_key,
                "상태": series.get("status") or "unmeasured",
                "마지막 값": (
                    list(series.get("points") or [])[-1].get("value")
                    if list(series.get("points") or [])
                    else "미측정"
                ),
                "누락 이유": series.get("missing_reason") or "-",
            }
        )
    st.markdown("##### 포트폴리오 행동 근거")
    st.dataframe(pd.DataFrame(series_rows), width="stretch", hide_index=True)
    execution_rows = list(behavior_board.get("execution_observations") or [])
    if execution_rows:
        st.dataframe(pd.DataFrame(execution_rows), width="stretch", hide_index=True)

    st.markdown("##### 실제 강점과 약점")
    finding_rows = [
        {"구분": "강점", **dict(row or {})} for row in strengths
    ] + [
        {"구분": "약점", **dict(row or {})} for row in weaknesses
    ]
    if finding_rows:
        st.dataframe(pd.DataFrame(finding_rows), width="stretch", hide_index=True)
    else:
        st.info("직접 비교 가능한 강점과 약점이 미측정입니다.")

    st.markdown("##### 포트폴리오 실제 성격")
    character_rows = [
        {
            "특성": row.get("label"),
            "관측값": row.get("display_value"),
            "상태": (
                "관측됨"
                if row.get("measurement_status") == "observed"
                else "분석 근거 없음"
            ),
            "의미": row.get("interpretation"),
            "기준일": row.get("as_of") or "-",
        }
        for row in list(character_profile.get("items") or [])
    ]
    st.dataframe(pd.DataFrame(character_rows), width="stretch", hide_index=True)

    st.markdown("##### 관리 기준 대비 압력")
    pressure_rows = [
        {
            "특성": row.get("label"),
            "상태": row.get("status"),
            "관측값": row.get("display_value"),
            "관리 기준": row.get("criterion_display") or "기준 미설정",
            "해석": row.get("summary"),
        }
        for row in list(review_pressure.get("items") or [])
    ]
    st.dataframe(pd.DataFrame(pressure_rows), width="stretch", hide_index=True)

    st.markdown("##### Level2에서 이어받은 판단")
    st.caption(
        "Level2에서 해결할 일은 끝났습니다. 확인된 근거만 최종 route 사유와 "
        "Monitoring 조건에 반영합니다."
    )
    accepted_limit_acknowledgements: list[dict[str, str]] = []
    accepted_limits = list(level2_handoff.get("accepted_limits") or [])
    if level2_handoff.get("state") == "blocked":
        st.warning(
            "Level2 차단 항목이 남아 있어 아직 Final Review 판단으로 "
            "승격되지 않았습니다."
        )
    else:
        handoff_groups = (
            (
                "final_decision",
                "최종 판단 입력",
                "계좌·운용 목적처럼 이 화면에서 route 사유로 결정할 내용입니다.",
                list(level2_handoff.get("final_decisions") or []),
            ),
            (
                "accepted_limit",
                "인수한 검증 한계 · 처리 선택",
                "근거를 확인한 뒤 계속 인수할지, Level2 검증으로 되돌릴지 항목별로 결정합니다.",
                accepted_limits,
            ),
            (
                "monitoring_transfer",
                "Monitoring 이관 조건",
                "관측값·조건·주기·재검토 행동이 모두 확인된 항목만 전달됩니다.",
                list(level2_handoff.get("monitoring_conditions") or []),
            ),
        )
        for handoff_kind, title, detail, rows in handoff_groups:
            if not rows:
                continue
            st.markdown(f"###### {title} · {len(rows)}")
            st.caption(detail)
            for row in rows:
                item = dict(row or {})
                with st.container(border=True):
                    st.markdown(
                        f"**{item.get('title') or item.get('root_issue_id') or '인계 항목'}**"
                    )
                    if item.get("observation") or item.get("observed"):
                        st.write(str(item.get("observation") or item.get("observed")))
                    if item.get("decision_guidance"):
                        st.caption(str(item["decision_guidance"]))
                    if item.get("threshold"):
                        st.caption(
                            f"변화 조건 {item.get('threshold')} · "
                            f"확인 주기 {item.get('cadence') or '-'}"
                        )
                    if item.get("re_review_action"):
                        st.caption(f"다시 할 판단: {item['re_review_action']}")
                    if handoff_kind == "accepted_limit":
                        root_issue_id = str(item.get("root_issue_id") or "").strip()
                        decision = st.radio(
                            "처리 방향",
                            options=("accepted", "return_to_level2"),
                            index=None,
                            format_func=lambda value: (
                                "한계를 인수하고 계속"
                                if value == "accepted"
                                else "Level2로 되돌리기"
                            ),
                            horizontal=True,
                            key=f"{key}_accepted_limit_{_paper_ledger_slug(root_issue_id)}",
                        )
                        if decision:
                            accepted_limit_acknowledgements.append(
                                {
                                    "root_issue_id": root_issue_id,
                                    "decision": str(decision),
                                }
                            )

    st.markdown("##### Monitoring 변화 조건")
    if monitoring_conditions:
        st.dataframe(pd.DataFrame(monitoring_conditions), width="stretch", hide_index=True)
    else:
        st.info("구조화된 Monitoring 변화 조건이 미측정입니다.")

    accepted_limits_complete = len(accepted_limit_acknowledgements) == len(
        accepted_limits
    )
    requires_re_review_route = any(
        row.get("decision") == "return_to_level2"
        for row in accepted_limit_acknowledgements
    )
    if requires_re_review_route:
        decision_action = {**decision_action, "suggested_route": "RE_REVIEW_REQUIRED"}
    decision_intent = _render_final_review_decision_fallback(
        decision_action,
        key=key,
        accepted_limit_acknowledgements=accepted_limit_acknowledgements,
        accepted_limits_complete=accepted_limits_complete,
        requires_re_review_route=requires_re_review_route,
    )
    with st.expander("Evidence confidence / accepted limits / provenance", expanded=False):
        st.json(disclosures)
    return decision_intent


def _render_final_review_decision_workspace(
    decision_brief: dict[str, Any],
    *,
    candidate_selector: dict[str, Any],
    key: str,
) -> dict[str, Any] | None:
    if is_final_review_decision_workspace_available():
        return render_final_review_decision_workspace(
            decision_brief=decision_brief,
            candidate_selector=candidate_selector,
            key=key,
        )
    return _render_final_review_decision_brief_fallback(
        decision_brief,
        candidate_selector=candidate_selector,
        key=key,
    )


def _consume_final_review_candidate_intent(
    intent: dict[str, Any] | None,
    *,
    source_options: list[dict[str, Any]],
) -> None:
    """Validate a presentation-only candidate switch and rerun without writing."""

    payload = dict(intent or {})
    if payload.get("action") != "select_candidate":
        return
    intent_id = str(payload.get("intent_id") or "").strip()
    source_id = str(payload.get("source_id") or "").strip()
    allowed_source_ids = {
        str(row.get("source_id") or "").strip()
        for row in source_options
        if bool(row.get("eligible")) and str(row.get("source_id") or "").strip()
    }
    consumed_key = "final_review_consumed_candidate_intent"
    if not intent_id or st.session_state.get(consumed_key) == intent_id:
        return
    if source_id not in allowed_source_ids:
        st.error("현재 Final Review 후보 목록에 없는 요청입니다. 후보를 다시 선택하세요.")
        return
    st.session_state[consumed_key] = intent_id
    st.session_state["final_review_active_decision_brief_source_id"] = source_id
    st.rerun()


def _consume_final_review_decision_intent(
    intent: dict[str, Any] | None,
    *,
    source: dict[str, Any],
    validation: dict[str, Any],
    paper_observation: dict[str, Any],
    evidence: dict[str, Any],
    investability_packet: dict[str, Any],
    decision_brief: dict[str, Any],
    decision_id: str,
    decision_id_key: str,
    existing_decision_ids: set[str],
    observation_freshness: dict[str, Any] | None = None,
) -> None:
    """Validate one component intent and append the authoritative Python decision row once."""

    payload = dict(intent or {})
    if payload.get("action") != "record_final_decision":
        return
    intent_id = str(payload.get("intent_id") or "").strip()
    source_slug = _paper_ledger_slug(source.get("source_id"))
    consumed_key = f"final_review_consumed_decision_intent_{source_slug}"
    if not intent_id or st.session_state.get(consumed_key) == intent_id:
        return
    st.session_state[consumed_key] = intent_id

    decision_route = str(payload.get("decision_route") or "").strip()
    operator_reason = str(payload.get("operator_reason") or "").strip()
    accepted_limit_acknowledgements, acknowledgement_error = (
        validate_accepted_limit_acknowledgements(
            level2_handoff=dict(decision_brief.get("level2_handoff") or {}),
            acknowledgements=payload.get("accepted_limit_acknowledgements"),
            decision_route=decision_route,
        )
    )
    if acknowledgement_error:
        st.error(acknowledgement_error)
        return
    guide = build_final_review_decision_record_guide(
        decision_route=decision_route,
        decision_evidence=evidence,
        investability_packet=investability_packet,
    )
    route_templates = dict(guide.get("route_templates") or {})
    save_evaluation = _build_final_review_save_evaluation(
        evidence=evidence,
        investability_packet=investability_packet,
        decision_id=decision_id,
        decision_route=decision_route,
        operator_reason=operator_reason,
        existing_decision_ids=existing_decision_ids,
        observation_freshness=observation_freshness,
    )
    if not bool(save_evaluation.get("can_save")):
        st.error(str(save_evaluation.get("verdict") or "판단 기록을 저장할 수 없습니다."))
        for blocker in list(save_evaluation.get("blockers") or []):
            st.caption(f"- {blocker}")
        return

    final_row = _build_final_review_decision_row(
        source=source,
        validation=validation,
        paper_observation=paper_observation,
        evidence=evidence,
        investability_packet=investability_packet,
        decision_brief=decision_brief,
        decision_id=decision_id,
        decision_route=decision_route,
        operator_reason=operator_reason,
        operator_constraints=str(route_templates.get("constraints") or ""),
        operator_next_action=str(route_templates.get("next_action") or ""),
        accepted_limit_acknowledgements=accepted_limit_acknowledgements,
    )
    append_current_final_selection_decision(final_row)
    decision_label = FINAL_REVIEW_DECISION_LABELS.get(decision_route, decision_route)
    next_location = (
        "Operations > Portfolio Monitoring에서 추적 조건을 이어서 확인하세요."
        if final_row.get("monitoring_candidate")
        else "판단 기록은 보존되며 Portfolio Monitoring 후보로는 연결되지 않습니다."
    )
    st.session_state["final_review_decision_notice"] = (
        f"{decision_label} 판단을 기록했습니다. {next_location} "
        "이 기록은 실제 투자 승인이나 주문 지시가 아닙니다."
    )
    st.session_state.pop(decision_id_key, None)
    st.rerun()


def _refresh_result_state_key(selection_source_id: Any) -> str:
    return (
        "final_review_observation_refresh_result_"
        f"{_paper_ledger_slug(selection_source_id)}"
    )


def _consume_final_review_observation_refresh_intent(
    intent: dict[str, Any] | None,
    *,
    source: dict[str, Any],
    validation: dict[str, Any],
    observation_freshness: dict[str, Any],
) -> None:
    """Validate one refresh intent and run the Python-owned append workflow once."""

    payload = dict(intent or {})
    if payload.get("action") != "refresh_observation":
        return
    intent_id = str(payload.get("intent_id") or "").strip()
    selection_source_id = str(validation.get("selection_source_id") or "").strip()
    validation_id = str(validation.get("validation_id") or "").strip()
    requested_source_id = str(payload.get("source_id") or "").strip()
    requested_validation_id = str(payload.get("validation_id") or "").strip()
    consumed_key = (
        "final_review_consumed_observation_refresh_"
        f"{_paper_ledger_slug(selection_source_id)}"
    )
    if not intent_id or st.session_state.get(consumed_key) == intent_id:
        return
    if requested_source_id != selection_source_id or requested_validation_id != validation_id:
        st.error("현재 검토 중인 후보와 최신화 요청의 identity가 다릅니다. 화면을 다시 확인하세요.")
        return
    if (
        str(observation_freshness.get("selection_source_id") or selection_source_id)
        != selection_source_id
        or str(observation_freshness.get("validation_id") or validation_id)
        != validation_id
    ):
        st.error("현재 표시된 최신성 상태가 다른 검증 결과에 속합니다. 화면을 새로 확인하세요.")
        return
    if not bool(observation_freshness.get("can_refresh")):
        st.error("현재 후보에는 자동으로 실행할 최신 관측 갱신이 없습니다.")
        return

    st.session_state[consumed_key] = intent_id
    with st.spinner("최신 가격을 확인하고 같은 전략을 다시 계산하는 중입니다..."):
        result = run_final_review_observation_refresh(
            source=dict(validation.get("selection_source_snapshot") or source),
            validation=validation,
        )
    st.session_state[_refresh_result_state_key(selection_source_id)] = dict(result)
    status = str(result.get("status") or "")
    message = str(result.get("message") or "최신 관측 갱신을 확인했습니다.")
    st.session_state["final_review_observation_refresh_notice"] = {
        "status": status,
        "message": message,
    }
    new_validation_id = str(result.get("new_validation_id") or "").strip()
    if bool(result.get("validation_saved")) and new_validation_id:
        st.session_state["final_review_active_decision_brief_source_id"] = (
            f"practical_validation_result:{new_validation_id}"
        )
    st.rerun()


def _consume_final_review_data_enrichment_intent(
    intent: dict[str, Any] | None,
    *,
    validation: dict[str, Any],
) -> None:
    """Route one readable-report intent to the owning Level2 Python action surface."""

    payload = dict(intent or {})
    if payload.get("action") != "open_practical_validation_data_enrichment":
        return
    intent_id = str(payload.get("intent_id") or "").strip()
    validation_id = str(validation.get("validation_id") or "").strip()
    consumed_key = f"final_review_consumed_data_enrichment_{_paper_ledger_slug(validation_id)}"
    if not intent_id or st.session_state.get(consumed_key) == intent_id:
        return
    requested_validation_id = str(payload.get("validation_id") or "").strip()
    if requested_validation_id and requested_validation_id != validation_id:
        st.error("현재 확인한 검토서와 데이터 보강 요청의 validation이 다릅니다. 검토서를 다시 확인하세요.")
        return
    source_snapshot = dict(validation.get("selection_source_snapshot") or {})
    selection_source_id = str(source_snapshot.get("selection_source_id") or validation.get("selection_source_id") or "").strip()
    requested_source_id = str(payload.get("selection_source_id") or "").strip()
    if not source_snapshot or (requested_source_id and requested_source_id != selection_source_id):
        st.error("같은 후보를 2단계로 전달할 selection source가 없습니다. Practical Validation에서 후보를 다시 선택하세요.")
        return

    st.session_state[consumed_key] = intent_id
    st.session_state.backtest_practical_validation_source = source_snapshot
    st.session_state.backtest_practical_validation_mode = PRACTICAL_VALIDATION_MODE_SELECTED_SOURCE
    st.session_state.backtest_practical_validation_data_enrichment_handoff = {
        "selection_source": source_snapshot,
        "validation_result": dict(validation),
    }
    st.session_state.backtest_practical_validation_notice = (
        "Final Review에서 확인한 같은 후보의 데이터 보강으로 이동했습니다. "
        "수집 가능한 자료만 보강한 뒤 Flow 2 재검증을 실행하세요."
    )
    st.session_state.pop("practical_validation_source_selected", None)
    st.session_state.backtest_requested_panel = BACKTEST_STAGE_PRACTICAL_VALIDATION
    st.rerun()


def render_final_review_workspace() -> None:
    st.markdown("### Final Review")
    st.caption("이 포트폴리오를 실제 투자 검토 대상으로 계속 추적할 가치가 있는가?")

    current_rows = load_current_candidate_registry_latest()
    proposal_rows = load_portfolio_proposals()
    pre_live_rows = load_pre_live_candidate_registry_latest()
    practical_validation_rows = load_practical_validation_results()
    latest_practical_validation_rows = _latest_practical_validation_rows_by_source(
        practical_validation_rows
    )
    eligible_practical_validation_rows = [
        row
        for row in latest_practical_validation_rows
        if _is_final_review_eligible_validation_result(dict(row or {}))
    ]
    final_decision_rows = load_current_final_selection_decisions()
    session_practical_source = st.session_state.pop("final_review_practical_validation_source", None)
    final_practical_notice = st.session_state.pop("final_review_practical_validation_notice", None)

    final_notice = st.session_state.pop("final_review_decision_notice", None)
    refresh_notice = st.session_state.pop("final_review_observation_refresh_notice", None)
    if final_practical_notice:
        st.success(str(final_practical_notice))
    if final_notice:
        st.success(str(final_notice))
    if isinstance(refresh_notice, dict):
        refresh_status = str(refresh_notice.get("status") or "")
        refresh_message = str(refresh_notice.get("message") or "")
        if refresh_status == "refreshed":
            st.success(refresh_message)
        elif refresh_status in {"partial_refresh", "up_to_date"}:
            st.warning(refresh_message)
        else:
            st.error(refresh_message)

    source_options = _build_final_review_source_options(
        current_rows,
        proposal_rows,
        practical_validation_rows=eligible_practical_validation_rows,
        session_practical_source=session_practical_source if isinstance(session_practical_source, dict) else None,
        include_legacy_sources=False,
    )
    if not source_options:
        st.info("Final Review Gate를 통과한 Practical Validation 후보가 없습니다.")
        st.caption("Practical Validation에서 미해결 근거를 종결하고 새 결과를 저장한 뒤 다시 확인하세요.")
        return

    candidate_contexts = _build_candidate_contexts(
        source_options,
        current_rows=current_rows,
        pre_live_rows=pre_live_rows,
    )
    selector_candidates = [
        {
            "source_id": str(context.get("candidate_key") or ""),
            "validation_id": str(dict(context.get("validation") or {}).get("validation_id") or ""),
            "title": str(
                dict(context.get("source") or {}).get("source_title")
                or context.get("label")
                or context.get("candidate_key")
                or "후보"
            ),
            "source_type": str(dict(context.get("source") or {}).get("source_type") or ""),
            "eligible": True,
        }
        for context in candidate_contexts
    ]
    allowed_source_ids = [str(row.get("source_id") or "") for row in selector_candidates]
    active_source_id = str(
        st.session_state.get("final_review_active_decision_brief_source_id")
        or allowed_source_ids[0]
    )
    if active_source_id not in allowed_source_ids:
        active_source_id = allowed_source_ids[0]
    st.session_state["final_review_active_decision_brief_source_id"] = active_source_id
    candidate_selector = build_final_review_candidate_selector(
        selector_candidates,
        active_source_id=active_source_id,
    )
    selected_context = next(
        context
        for context in candidate_contexts
        if str(context.get("candidate_key") or "") == active_source_id
    )
    source = dict(selected_context.get("source") or {})
    validation = dict(selected_context.get("validation") or {})
    paper_observation = dict(selected_context.get("paper_observation") or {})
    evidence = dict(selected_context.get("decision_evidence") or {})
    investability_packet = dict(selected_context.get("investability_packet") or {})
    existing_decision_ids = {
        str(row.get("decision_id") or "").strip()
        for row in final_decision_rows
        if str(row.get("decision_id") or "").strip()
    }
    source_slug = _paper_ledger_slug(source.get("source_id"))
    decision_id_key = f"final_review_decision_id_v2_{source_slug}"
    if not str(st.session_state.get(decision_id_key) or "").strip():
        st.session_state[decision_id_key] = f"final_{source_slug}_{date.today().strftime('%Y%m%d')}_{uuid4().hex[:6]}"
    decision_id = str(st.session_state[decision_id_key])
    observation_freshness = build_final_review_refresh_status(
        source=source,
        validation=validation,
    )
    selection_source_id = str(validation.get("selection_source_id") or "").strip()
    last_refresh_result = st.session_state.get(
        _refresh_result_state_key(selection_source_id)
    )
    if isinstance(last_refresh_result, dict):
        observation_freshness["last_result"] = dict(last_refresh_result)
    decision_brief = build_final_review_decision_brief(
        source=source,
        validation=validation,
        paper_observation=paper_observation,
        decision_evidence=evidence,
        investability_packet=investability_packet,
        decision_id=decision_id,
        existing_decision_ids=existing_decision_ids,
        observation_freshness=observation_freshness,
    )
    workspace_intent = _render_final_review_decision_workspace(
        decision_brief,
        candidate_selector=candidate_selector,
        key=f"final_review_decision_workspace_{validation.get('validation_id') or source.get('source_id') or 'current'}",
    )
    _consume_final_review_candidate_intent(
        workspace_intent,
        source_options=list(candidate_selector.get("options") or []),
    )
    _consume_final_review_observation_refresh_intent(
        workspace_intent,
        source=source,
        validation=validation,
        observation_freshness=observation_freshness,
    )
    _consume_final_review_decision_intent(
        workspace_intent,
        source=source,
        validation=validation,
        paper_observation=paper_observation,
        evidence=evidence,
        investability_packet=investability_packet,
        decision_brief=decision_brief,
        decision_id=decision_id,
        decision_id_key=decision_id_key,
        existing_decision_ids=existing_decision_ids,
        observation_freshness=observation_freshness,
    )
