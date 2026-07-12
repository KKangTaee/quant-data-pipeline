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
    build_final_review_investment_report,
    build_final_review_decision_record_guide,
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
    is_final_review_investment_report_available,
    render_final_review_investment_report,
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
        format_func=lambda route: FINAL_REVIEW_DECISION_LABELS.get(route, route),
        horizontal=True,
        key=f"{key}_route",
    )
    selected = next(option for option in options if option.get("route") == selected_route)
    reason = st.text_area(
        "판단 사유",
        placeholder=str(selected.get("reason_placeholder") or "왜 이 판단을 선택했는지 직접 작성합니다."),
        key=f"{key}_reason_{_paper_ledger_slug(selected_route)}",
    )
    can_submit = bool(selected.get("recordable")) and bool(str(reason or "").strip())
    if not bool(selected.get("recordable")):
        st.error(str(selected.get("disabled_reason") or "현재 조건에서는 이 판단을 저장할 수 없습니다."))
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


def _consume_final_review_decision_intent(
    intent: dict[str, Any] | None,
    *,
    source: dict[str, Any],
    validation: dict[str, Any],
    paper_observation: dict[str, Any],
    evidence: dict[str, Any],
    investability_packet: dict[str, Any],
    decision_id: str,
    decision_id_key: str,
    existing_decision_ids: set[str],
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
        decision_id=decision_id,
        decision_route=decision_route,
        operator_reason=operator_reason,
        operator_constraints=str(route_templates.get("constraints") or ""),
        operator_next_action=str(route_templates.get("next_action") or ""),
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
    top_summary = _build_final_review_top_summary()
    st.markdown(f"### {top_summary['title']}")
    st.caption(top_summary["caption"])

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
    if final_practical_notice:
        st.success(str(final_practical_notice))
    if final_notice:
        st.success(str(final_notice))

    source_options = _build_final_review_source_options(
        current_rows,
        proposal_rows,
        practical_validation_rows=eligible_practical_validation_rows,
        session_practical_source=session_practical_source if isinstance(session_practical_source, dict) else None,
        include_legacy_sources=False,
    )
    candidate_contexts = (
        _build_candidate_contexts(
            source_options,
            current_rows=current_rows,
            pre_live_rows=pre_live_rows,
        )
        if source_options
        else []
    )
    candidate_board = build_final_review_candidate_board(candidate_contexts) if candidate_contexts else {}
    candidate_summary = dict(candidate_board.get("summary") or {})
    route_value, route_detail, route_tone = _candidate_board_route(candidate_summary)
    dashboard_handoff = build_selected_dashboard_handoff_review(final_decision_rows)
    dashboard_summary = dict(dashboard_handoff.get("summary") or {})
    hidden_validation_count = len(latest_practical_validation_rows) - len(eligible_practical_validation_rows)
    decision_desk = _build_final_review_decision_desk_model(
        candidate_summary=candidate_summary,
        practical_validation_count=len(practical_validation_rows),
        eligible_count=len(eligible_practical_validation_rows),
        hidden_validation_count=hidden_validation_count,
        final_decision_count=len(final_decision_rows),
        dashboard_selected_count=int(dashboard_summary.get("selected_decision_count", 0) or 0),
        route_value=route_value,
        route_detail=route_detail,
        route_tone=route_tone,
    )
    render_fr_command_center(
        eyebrow=str(decision_desk["eyebrow"]),
        title=str(decision_desk["title"]),
        detail=str(decision_desk["detail"]),
        route_label=str(decision_desk["route_label"]),
        route_value=str(decision_desk["route_value"]),
        route_detail=str(decision_desk["route_detail"]),
        route_tone=str(decision_desk["route_tone"]),
        kpis=list(decision_desk["kpis"]),
        featured_candidate=dict(decision_desk["featured_candidate"]),
    )
    if hidden_validation_count > 0:
        st.caption(
            f"Practical Validation 저장 기록 {hidden_validation_count}개는 Final Review Gate를 통과하지 않아 검토 대상 목록에서 숨겼습니다."
        )

    if not source_options:
        st.info("Final Review Gate를 통과한 Practical Validation 후보가 없습니다.")
        st.caption("검증 결과만 저장한 blocked / needs input / not run 후보는 기록으로 남지만, Final Review 검토 대상에는 표시되지 않습니다.")
        st.caption("기존에 선정한 Monitoring 후보와 운영 상태는 Operations > Portfolio Monitoring에서 확인합니다.")
        return

    with st.container(border=True):
        candidate_selection = _render_candidate_selection_panel(candidate_contexts)
    if not bool(candidate_selection.get("is_confirmed")):
        return
    selected_context = dict(candidate_selection["context"])
    source = dict(selected_context["source"])

    validation = dict(selected_context["validation"])
    paper_observation = dict(selected_context["paper_observation"])
    evidence = dict(selected_context["decision_evidence"])
    investability_packet = dict(selected_context["investability_packet"])
    cockpit = dict(selected_context["cockpit"])
    investment_report = build_final_review_investment_report(
        source=source,
        validation=validation,
        paper_observation=paper_observation,
        decision_evidence=evidence,
        investability_packet=investability_packet,
    )

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
    decision_action = _build_final_review_decision_action_model(
        cockpit=cockpit,
        evidence=evidence,
        investability_packet=investability_packet,
        decision_id=decision_id,
        existing_decision_ids=existing_decision_ids,
        data_enrichment_action=dict(
            dict(investment_report.get("level2_review_disposition") or {}).get("data_enrichment_action")
            or {}
        ),
    )
    decision_intent = _render_investment_report(
        investment_report,
        decision_action=decision_action,
        key=f"final_review_investment_report_{validation.get('validation_id') or source.get('source_id') or 'current'}",
    )
    _consume_final_review_data_enrichment_intent(
        decision_intent,
        validation=validation,
    )
    _consume_final_review_decision_intent(
        decision_intent,
        source=source,
        validation=validation,
        paper_observation=paper_observation,
        evidence=evidence,
        investability_packet=investability_packet,
        decision_id=decision_id,
        decision_id_key=decision_id_key,
        existing_decision_ids=existing_decision_ids,
    )
