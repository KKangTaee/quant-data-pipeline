from __future__ import annotations

from datetime import date
from typing import Any
from uuid import uuid4

import pandas as pd
import streamlit as st

from app.web.backtest_post_selection_guide_helpers import (
    POST_SELECTION_CAPITAL_MODE_OPTIONS,
    POST_SELECTION_REBALANCE_CADENCE_OPTIONS,
    build_post_selection_component_rows,
    build_post_selection_guide_rows_for_display,
    build_post_selection_operating_guide_row,
    build_post_selection_readiness,
    build_post_selection_source_options,
    build_post_selection_source_review_rows,
    default_post_selection_policy_inputs,
)
from app.web.backtest_portfolio_proposal_helpers import _paper_ledger_slug
from app.web.backtest_ui_components import (
    render_artifact_pipeline,
    render_badge_strip,
    render_readiness_route_panel,
    render_stage_brief,
    render_status_card_grid,
)
from app.web.runtime import (
    POST_SELECTION_OPERATING_GUIDE_FILE,
    append_post_selection_operating_guide,
    load_final_selection_decisions,
    load_post_selection_operating_guides,
)


def _render_source_summary(selected_decision: dict[str, Any]) -> None:
    evidence = dict(selected_decision.get("decision_evidence_snapshot") or {})
    handoff = dict(selected_decision.get("phase35_handoff") or {})
    render_badge_strip(
        [
            {"label": "Decision", "value": selected_decision.get("decision_route") or "-", "tone": "positive"},
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


def _render_saved_operating_guides(saved_guides: list[dict[str, Any]]) -> None:
    if not saved_guides:
        st.info("아직 기록된 Post-Selection Operating Guide가 없습니다.")
        st.caption(f"Path: {POST_SELECTION_OPERATING_GUIDE_FILE}")
        return

    st.dataframe(build_post_selection_guide_rows_for_display(saved_guides), width="stretch", hide_index=True)
    labels = [
        f"{row.get('updated_at') or row.get('created_at')} | {row.get('source_title') or row.get('source_id')} | id={row.get('guide_id')}"
        for row in saved_guides
    ]
    selected_label = st.selectbox("운영 가이드 확인", options=labels, key="post_selection_saved_guide_selected")
    selected_row = saved_guides[labels.index(selected_label)]
    readiness = dict(selected_row.get("guide_readiness_snapshot") or {})
    handoff = dict(selected_row.get("post_selection_handoff") or {})
    render_readiness_route_panel(
        route_label=str(handoff.get("handoff_route") or "-"),
        score=float(readiness.get("score") or 0.0),
        blockers_count=len(readiness.get("blockers") or []),
        verdict=str(handoff.get("verdict") or "-"),
        next_action=str(handoff.get("next_action") or "-"),
        route_title="Guide Handoff",
        score_title="Guide Score",
    )
    render_badge_strip(
        [
            {"label": "Source Decision", "value": selected_row.get("source_decision_id") or "-", "tone": "neutral"},
            {"label": "Weight Total", "value": f"{selected_row.get('target_weight_total')}%", "tone": "neutral"},
            {"label": "Live Approval", "value": "Disabled", "tone": "neutral"},
            {"label": "Order", "value": "Disabled", "tone": "neutral"},
        ]
    )
    component_df = build_post_selection_component_rows(selected_row)
    if not component_df.empty:
        st.dataframe(component_df, width="stretch", hide_index=True)
    policy = dict(selected_row.get("operating_policy") or {})
    st.markdown("###### 운영 기준")
    st.write(
        {
            "capital_mode": policy.get("capital_mode"),
            "rebalancing_cadence": policy.get("rebalancing_cadence"),
            "rebalance_trigger": policy.get("rebalance_trigger"),
            "reduce_trigger": policy.get("reduce_trigger"),
            "stop_trigger": policy.get("stop_trigger"),
            "re_review_trigger": policy.get("re_review_trigger"),
        }
    )
    with st.expander("운영 가이드 JSON", expanded=False):
        st.json(selected_row)


def render_post_selection_guide_workspace() -> None:
    st.markdown("### Post-Selection Guide")
    st.caption(
        "Final Review에서 최종 선정한 후보를 실제 운영 전 리밸런싱 / 축소 / 중단 / 재검토 기준으로 정리합니다. "
        "이 화면도 live approval이나 주문 지시가 아닙니다."
    )

    final_decision_rows = load_final_selection_decisions(limit=None)
    saved_guides = load_post_selection_operating_guides(limit=None)
    source_options = build_post_selection_source_options(final_decision_rows)

    guide_notice = st.session_state.pop("post_selection_guide_notice", None)
    if guide_notice:
        st.success(str(guide_notice))

    render_status_card_grid(
        [
            {"title": "Final Review Records", "value": len(final_decision_rows), "tone": "positive" if final_decision_rows else "neutral"},
            {"title": "Guide Eligible", "value": len(source_options), "detail": "SELECT_FOR_PRACTICAL_PORTFOLIO만 대상", "tone": "positive" if source_options else "warning"},
            {"title": "Saved Guides", "value": len(saved_guides), "tone": "positive" if saved_guides else "neutral"},
            {"title": "Live Approval", "value": "Disabled", "detail": "가이드는 승인/주문이 아닙니다.", "tone": "neutral"},
            {"title": "Order", "value": "Disabled", "detail": "브로커 주문을 만들지 않습니다.", "tone": "neutral"},
        ]
    )

    with st.container(border=True):
        st.markdown("#### 운영 가이드 흐름")
        render_artifact_pipeline(
            [
                {"title": "최종 선정 기록", "detail": "Final Review selected record", "status": "입력", "tone": "positive"},
                {"title": "운영 기준", "detail": "리밸런싱 / 축소 / 중단 / 재검토", "status": "작성", "tone": "neutral"},
                {"title": "운영 가이드 기록", "detail": "원본 decision을 덮어쓰지 않음", "status": "Append-only", "tone": "warning"},
                {"title": "기본 흐름 완료", "detail": "후속 live approval은 별도 경계", "status": "Guide", "tone": "neutral"},
            ]
        )

    st.divider()
    st.markdown("#### 1. Phase35 입력 대상 확인")
    with st.container(border=True):
        render_stage_brief(
            purpose="Final Review에서 `SELECT_FOR_PRACTICAL_PORTFOLIO`로 기록된 대상만 운영 가이드 입력으로 읽습니다.",
            result="Selected final review record",
        )
        source_review_df = build_post_selection_source_review_rows(final_decision_rows)
        if source_review_df.empty:
            st.info("아직 읽을 Final Review 기록이 없습니다.")
        else:
            st.dataframe(source_review_df, width="stretch", hide_index=True)

    if not source_options:
        st.warning("운영 가이드로 넘길 수 있는 최종 선정 기록이 없습니다. Final Review에서 먼저 선정 판단을 기록해야 합니다.")
        return

    labels = [str(option["label"]) for option in source_options]
    selected_label = st.selectbox("운영 가이드 대상", options=labels, key="post_selection_source_selected")
    source_option = source_options[labels.index(selected_label)]
    selected_decision = dict(source_option.get("row") or {})

    st.markdown("#### 2. 선정 기록과 component 확인")
    with st.container(border=True):
        _render_source_summary(selected_decision)

    defaults = default_post_selection_policy_inputs(selected_decision)
    existing_guide_ids = {
        str(row.get("guide_id") or "").strip()
        for row in saved_guides
        if str(row.get("guide_id") or "").strip()
    }
    if st.session_state.pop("post_selection_reset_guide_id_after_save", False):
        st.session_state.pop("post_selection_guide_id", None)
    decision_slug = _paper_ledger_slug(selected_decision.get("decision_id"))
    default_guide_id = f"guide_{decision_slug}_{date.today().strftime('%Y%m%d')}_{uuid4().hex[:6]}"

    st.markdown("#### 3. 운영 기준 작성")
    with st.container(border=True):
        render_stage_brief(
            purpose="선정된 후보를 어떻게 운용할지 사람의 기준으로 고정합니다.",
            result="Post-selection operating policy",
        )
        id_cols = st.columns([0.42, 0.30, 0.28], gap="small")
        with id_cols[0]:
            guide_id = st.text_input("Guide ID", value=default_guide_id, key="post_selection_guide_id")
        with id_cols[1]:
            capital_mode = st.selectbox(
                "Capital Mode",
                options=POST_SELECTION_CAPITAL_MODE_OPTIONS,
                index=POST_SELECTION_CAPITAL_MODE_OPTIONS.index(defaults["capital_mode"]),
                key="post_selection_capital_mode",
            )
        with id_cols[2]:
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
        guide_id=guide_id,
        existing_guide_ids=existing_guide_ids,
        capital_mode=str(capital_mode),
        capital_boundary_note=capital_boundary_note,
        rebalancing_cadence=str(rebalancing_cadence),
        rebalance_trigger=rebalance_trigger,
        reduce_trigger=reduce_trigger,
        stop_trigger=stop_trigger,
        re_review_trigger=re_review_trigger,
    )
    guide_row = build_post_selection_operating_guide_row(
        final_decision_row=selected_decision,
        guide_id=guide_id,
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

    st.markdown("#### 4. 운영 가이드 기록 준비")
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
            if st.button(
                "운영 가이드 기록",
                key="post_selection_record_guide",
                disabled=not bool(readiness.get("can_save")),
                width="stretch",
            ):
                append_post_selection_operating_guide(guide_row)
                st.session_state["post_selection_guide_notice"] = (
                    f"Post-Selection Operating Guide `{guide_row['guide_id']}`를 기록했습니다. "
                    "이 기록은 live approval이나 주문 지시가 아닙니다."
                )
                st.session_state["post_selection_reset_guide_id_after_save"] = True
                st.rerun()
        with action_cols[1]:
            st.button(
                "Live Approval / Order",
                key="post_selection_live_order_disabled",
                disabled=True,
                width="stretch",
                help="Phase35는 운영 가이드까지만 만들며 실제 승인/주문은 만들지 않습니다.",
            )
        with st.expander("운영 가이드 Preview", expanded=False):
            st.json(guide_row)
            st.caption(f"Path: {POST_SELECTION_OPERATING_GUIDE_FILE}")

    st.markdown("#### 5. 기록된 운영 가이드 확인")
    with st.container(border=True):
        _render_saved_operating_guides(saved_guides)
