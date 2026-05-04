from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from app.web.backtest_common import _request_backtest_panel
from app.web.backtest_post_selection_guide_helpers import (
    POST_SELECTION_CAPITAL_MODE_OPTIONS,
    POST_SELECTION_REBALANCE_CADENCE_OPTIONS,
    build_final_investment_decision_summary,
    build_post_selection_component_rows,
    build_post_selection_guide_preview,
    build_post_selection_readiness,
    build_post_selection_source_options,
    build_post_selection_source_review_rows,
    default_post_selection_policy_inputs,
)
from app.web.backtest_ui_components import (
    render_artifact_pipeline,
    render_badge_strip,
    render_readiness_route_panel,
    render_stage_brief,
    render_status_card_grid,
)
from app.web.runtime import load_final_selection_decisions


def _render_source_summary(selected_decision: dict[str, Any]) -> None:
    evidence = dict(selected_decision.get("decision_evidence_snapshot") or {})
    handoff = dict(selected_decision.get("phase35_handoff") or {})
    summary = build_final_investment_decision_summary(selected_decision)
    render_badge_strip(
        [
            {"label": "Decision", "value": selected_decision.get("decision_route") or "-", "tone": "positive"},
            {"label": "투자 가능성", "value": summary["verdict_label"], "tone": summary["tone"]},
            {"label": "Decision ID", "value": selected_decision.get("decision_id") or "-", "tone": "neutral"},
            {"label": "Source", "value": f"{selected_decision.get('source_type')} / {selected_decision.get('source_id')}", "tone": "neutral"},
            {"label": "Evidence", "value": evidence.get("route") or "-", "tone": "positive" if evidence.get("route") == "READY_FOR_FINAL_DECISION" else "warning"},
            {"label": "Phase35", "value": handoff.get("handoff_route") or "-", "tone": "positive"},
        ]
    )
    component_df = build_post_selection_component_rows(selected_decision)
    if component_df.empty:
        st.info("이 final decision에는 운영 대상 component가 없습니다.")
    else:
        st.dataframe(component_df, width="stretch", hide_index=True)


def render_post_selection_guide_workspace() -> None:
    st.markdown("### Post-Selection Guide")
    st.caption(
        "Final Review에서 기록한 최종 판단을 읽어 투자 가능 후보인지, 투자하면 안 되는지, 내용이 부족한지, "
        "재검토가 필요한지 확인합니다. 이 화면은 새 registry를 저장하지 않고 live approval이나 주문도 만들지 않습니다."
    )

    final_decision_rows = load_final_selection_decisions(limit=None)
    source_options = build_post_selection_source_options(final_decision_rows)

    render_status_card_grid(
        [
            {"title": "Final Review Records", "value": len(final_decision_rows), "tone": "positive" if final_decision_rows else "neutral"},
            {"title": "투자 가능 후보", "value": len(source_options), "detail": "SELECT_FOR_PRACTICAL_PORTFOLIO만 대상", "tone": "positive" if source_options else "warning"},
            {"title": "Extra Save", "value": "Not Required", "detail": "Final Review 기록을 다시 저장하지 않습니다.", "tone": "positive"},
            {"title": "Live Approval", "value": "Disabled", "detail": "최종 지침은 승인/주문이 아닙니다.", "tone": "neutral"},
            {"title": "Order", "value": "Disabled", "detail": "브로커 주문을 만들지 않습니다.", "tone": "neutral"},
        ]
    )

    with st.container(border=True):
        st.markdown("#### 최종 투자 지침 흐름")
        render_artifact_pipeline(
            [
                {"title": "최종 선정 기록", "detail": "Final Review selected record", "status": "입력", "tone": "positive"},
                {"title": "투자 가능성", "detail": "가능 / 금지 / 부족 / 재검토", "status": "확인", "tone": "neutral"},
                {"title": "운영 전 기준", "detail": "리밸런싱 / 축소 / 중단 / 재검토", "status": "확인", "tone": "neutral"},
                {"title": "기본 흐름 완료", "detail": "후속 live approval은 별도 경계", "status": "No Extra Save", "tone": "positive"},
            ]
        )

    st.divider()
    st.markdown("#### 1. 최종 판단 결과 확인")
    with st.container(border=True):
        render_stage_brief(
            purpose="Final Review에서 이미 기록한 최종 판단을 다시 읽고, 어떤 결과가 투자 가능 후보인지 구분합니다.",
            result="Final investment decision table",
        )
        source_review_df = build_post_selection_source_review_rows(final_decision_rows)
        if source_review_df.empty:
            st.info("아직 읽을 Final Review 기록이 없습니다.")
        else:
            st.dataframe(source_review_df, width="stretch", hide_index=True)

    if not source_options:
        st.warning("투자 가능 후보로 읽을 최종 선정 기록이 없습니다. Final Review에서 먼저 최종 판단을 기록해야 합니다.")
        return

    labels = [str(option["label"]) for option in source_options]
    selected_label = st.selectbox("최종 지침 확인 대상", options=labels, key="post_selection_source_selected")
    source_option = source_options[labels.index(selected_label)]
    selected_decision = dict(source_option.get("row") or {})

    st.markdown("#### 2. 선정 기록과 component 확인")
    with st.container(border=True):
        _render_source_summary(selected_decision)

    defaults = default_post_selection_policy_inputs(selected_decision)
    st.markdown("#### 3. 운영 전 기준 확인")
    with st.container(border=True):
        render_stage_brief(
            purpose="선정된 후보를 실제 투자 후보로 보기 전에 리밸런싱 / 축소 / 중단 / 재검토 기준이 충분한지 확인합니다.",
            result="Final pre-investment guide",
        )
        st.info("이 화면의 입력값은 확인용 preview입니다. 최종 판단 기록은 Final Review에 이미 남아 있으며, 여기서 별도 저장하지 않습니다.")
        id_cols = st.columns(2, gap="small")
        with id_cols[0]:
            capital_mode = st.selectbox(
                "Capital Mode",
                options=POST_SELECTION_CAPITAL_MODE_OPTIONS,
                index=POST_SELECTION_CAPITAL_MODE_OPTIONS.index(defaults["capital_mode"]),
                key="post_selection_capital_mode",
            )
        with id_cols[1]:
            rebalancing_cadence = st.selectbox(
                "Rebalancing Cadence",
                options=POST_SELECTION_REBALANCE_CADENCE_OPTIONS,
                index=POST_SELECTION_REBALANCE_CADENCE_OPTIONS.index(defaults["rebalancing_cadence"]),
                key="post_selection_rebalancing_cadence",
            )
        capital_boundary_note = st.text_area(
            "자본 / 승인 경계",
            value=str(defaults["capital_boundary_note"]),
            key="post_selection_capital_boundary_note",
        )
        rebalance_trigger = st.text_area(
            "리밸런싱 기준",
            value=str(defaults["rebalance_trigger"]),
            key="post_selection_rebalance_trigger",
        )
        trigger_cols = st.columns(2, gap="small")
        with trigger_cols[0]:
            reduce_trigger = st.text_area(
                "축소 기준",
                value=str(defaults["reduce_trigger"]),
                key="post_selection_reduce_trigger",
            )
            stop_trigger = st.text_area(
                "중단 기준",
                value=str(defaults["stop_trigger"]),
                key="post_selection_stop_trigger",
            )
        with trigger_cols[1]:
            re_review_trigger = st.text_area(
                "재검토 기준",
                value=str(defaults["re_review_trigger"]),
                key="post_selection_re_review_trigger",
                height=150,
            )
            operator_review_note = st.text_area(
                "운영 메모",
                value=str(defaults["operator_review_note"]),
                key="post_selection_operator_review_note",
            )

    readiness = build_post_selection_readiness(
        final_decision_row=selected_decision,
        capital_mode=str(capital_mode),
        capital_boundary_note=capital_boundary_note,
        rebalancing_cadence=str(rebalancing_cadence),
        rebalance_trigger=rebalance_trigger,
        reduce_trigger=reduce_trigger,
        stop_trigger=stop_trigger,
        re_review_trigger=re_review_trigger,
    )
    guide_preview = build_post_selection_guide_preview(
        final_decision_row=selected_decision,
        readiness=readiness,
        capital_mode=str(capital_mode),
        capital_boundary_note=capital_boundary_note,
        rebalancing_cadence=str(rebalancing_cadence),
        rebalance_trigger=rebalance_trigger,
        reduce_trigger=reduce_trigger,
        stop_trigger=stop_trigger,
        re_review_trigger=re_review_trigger,
        operator_review_note=operator_review_note,
    )

    st.markdown("#### 4. 최종 투자 가능성 확인")
    with st.container(border=True):
        render_readiness_route_panel(
            route_label=str(readiness.get("route") or "-"),
            score=float(readiness.get("score") or 0.0),
            blockers_count=len(readiness.get("blockers") or []),
            verdict=str(readiness.get("verdict") or "-"),
            next_action=str(readiness.get("next_action") or "-"),
            route_title="Guide Route",
            score_title="Guide Score",
        )
        if readiness.get("blockers"):
            for blocker in list(readiness.get("blockers") or []):
                st.warning(str(blocker))
        st.dataframe(pd.DataFrame(readiness.get("checks") or []), width="stretch", hide_index=True)
        action_cols = st.columns(2, gap="small")
        with action_cols[0]:
            st.button(
                "추가 저장 없음",
                key="post_selection_no_extra_save",
                disabled=True,
                width="stretch",
                help="Phase35는 Final Review 기록을 읽어 최종 지침을 확인하며 새 registry를 저장하지 않습니다.",
            )
        with action_cols[1]:
            st.button(
                "Live Approval / Order",
                key="post_selection_live_order_disabled",
                disabled=True,
                width="stretch",
                help="Phase35는 최종 투자 지침 확인까지만 다루며 실제 승인/주문은 만들지 않습니다.",
            )
        if st.button("Final Review로 돌아가기", key="post_selection_back_to_final_review", width="stretch"):
            _request_backtest_panel("Final Review")
            st.rerun()
        with st.expander("최종 지침 Preview", expanded=False):
            st.json(guide_preview)
