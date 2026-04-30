from __future__ import annotations

from datetime import date, timedelta
from typing import Any
from uuid import uuid4

import pandas as pd
import streamlit as st

from app.web.backtest_candidate_review_helpers import (
    _build_current_candidate_registry_rows_for_display,
    _current_candidate_registry_selection_label,
)
from app.web.backtest_portfolio_proposal_helpers import (
    PORTFOLIO_PROPOSAL_PAPER_CAGR_DETERIORATION_THRESHOLD,
    PORTFOLIO_PROPOSAL_PAPER_MDD_DETERIORATION_THRESHOLD,
    PORTFOLIO_PROPOSAL_ROLE_OPTIONS,
    PORTFOLIO_PROPOSAL_STATUS_OPTIONS,
    PORTFOLIO_PROPOSAL_TYPE_OPTIONS,
    PORTFOLIO_PROPOSAL_WEIGHTING_OPTIONS,
    _build_portfolio_proposal_component_rows,
    _build_portfolio_proposal_monitoring_rows,
    _build_portfolio_proposal_paper_tracking_feedback_summary_rows,
    _build_portfolio_proposal_pre_live_feedback_summary_rows,
    _build_portfolio_proposal_readiness_evaluation,
    _build_portfolio_proposal_row,
    _build_portfolio_proposal_rows_for_display,
    _portfolio_proposal_monitoring_blockers,
    _portfolio_proposal_monitoring_state,
    _portfolio_proposal_open_blockers,
    _portfolio_proposal_paper_tracking_feedback_gaps,
    _portfolio_proposal_paper_tracking_feedback_rows,
    _portfolio_proposal_pre_live_feedback_gaps,
    _portfolio_proposal_pre_live_feedback_rows,
    _portfolio_proposal_pre_live_record_by_registry_id,
    _portfolio_proposal_pre_live_status_by_registry_id,
    _portfolio_proposal_review_gaps,
    _portfolio_proposal_selection_label,
    _portfolio_proposal_weight_total,
)
from app.web.backtest_ui_components import (
    render_artifact_pipeline,
    render_badge_strip,
    render_readiness_route_panel,
    render_stage_brief,
    render_status_card_grid,
)
from app.web.runtime import (
    CURRENT_CANDIDATE_REGISTRY_FILE,
    PORTFOLIO_PROPOSAL_REGISTRY_FILE,
    append_portfolio_proposal,
    load_current_candidate_registry_latest as _load_current_candidate_registry_latest,
    load_portfolio_proposals,
    load_pre_live_candidate_registry_latest as _load_pre_live_candidate_registry_latest,
)


# Turn a current candidate row into an OK / warning / missing data trust label for proposal components.
def _component_data_trust_status(row: dict[str, Any]) -> str:
    review_context = dict(row.get("review_context") or {})
    data_trust = dict(review_context.get("data_trust_snapshot") or {})
    if not data_trust:
        return "not_attached"
    warning_count = data_trust.get("warning_count")
    excluded_tickers = list(data_trust.get("excluded_tickers") or [])
    malformed_count = int(data_trust.get("malformed_price_row_count") or 0)
    if malformed_count > 0:
        return "warning"
    try:
        if int(warning_count or 0) > 0:
            return "warning"
    except (TypeError, ValueError):
        return "warning"
    if excluded_tickers:
        return "warning"
    return "ok"


# Keep Streamlit multiselect state valid after registry rows change or a handoff label disappears.
def _sync_component_selection_state(label_to_row: dict[str, dict[str, Any]]) -> None:
    key = "portfolio_proposal_component_selection"
    current_value = st.session_state.get(key)
    if current_value is None:
        return
    valid_labels = [label for label in list(current_value) if label in label_to_row]
    if valid_labels != list(current_value):
        st.session_state[key] = valid_labels


# Render saved proposal monitoring, feedback, and raw JSON as one support area below the main flow.
def _render_saved_proposal_details(proposal_rows: list[dict[str, Any]], pre_live_rows: list[dict[str, Any]]) -> None:
    with st.expander("보조 도구: Saved Proposals / Feedback", expanded=False):
        if not proposal_rows:
            st.info("아직 저장된 Portfolio Proposal이 없습니다.")
            st.caption(f"Path: {PORTFOLIO_PROPOSAL_REGISTRY_FILE}")
            return

        overview_tab, pre_live_tab, paper_tab, json_tab = st.tabs(
            ["Monitoring", "Pre-Live Feedback", "Paper Tracking", "Raw JSON"]
        )
        labels = [_portfolio_proposal_selection_label(row) for row in proposal_rows]

        with overview_tab:
            st.caption("저장된 proposal draft를 blocker / review gap / 후보 구성 관점에서 다시 읽습니다.")
            st.dataframe(_build_portfolio_proposal_monitoring_rows(proposal_rows), width="stretch", hide_index=True)
            selected_label = st.selectbox(
                "Review Portfolio Proposal",
                options=labels,
                key="portfolio_proposal_monitoring_selected_record",
            )
            selected_row = proposal_rows[labels.index(selected_label)]
            objective = dict(selected_row.get("objective") or {})
            construction = dict(selected_row.get("construction") or {})
            operator_decision = dict(selected_row.get("operator_decision") or {})
            blockers = _portfolio_proposal_monitoring_blockers(selected_row)
            review_gaps = _portfolio_proposal_review_gaps(selected_row)
            component_rows = _build_portfolio_proposal_component_rows(selected_row)

            render_status_card_grid(
                [
                    {
                        "title": "Monitoring State",
                        "value": _portfolio_proposal_monitoring_state(selected_row),
                        "tone": "positive" if not blockers and not review_gaps else "warning",
                    },
                    {"title": "Components", "value": len(selected_row.get("candidate_refs") or []), "tone": "neutral"},
                    {"title": "Target Weight", "value": f"{_portfolio_proposal_weight_total(selected_row)}%", "tone": "neutral"},
                    {"title": "Live Approval", "value": "Disabled", "tone": "neutral"},
                ]
            )
            render_badge_strip(
                [
                    {"label": "Primary", "value": objective.get("primary_goal") or "-", "tone": "neutral"},
                    {"label": "Capital", "value": objective.get("capital_scope") or "-", "tone": "neutral"},
                    {"label": "Weighting", "value": construction.get("weighting_method") or "-", "tone": "neutral"},
                ]
            )
            if component_rows.empty:
                st.info("이 proposal에는 component candidate가 없습니다.")
            else:
                st.dataframe(component_rows, width="stretch", hide_index=True)
            detail_cols = st.columns(2, gap="small")
            with detail_cols[0]:
                st.markdown("##### Blockers")
                if blockers:
                    for blocker in blockers:
                        st.warning(blocker)
                else:
                    st.success("현재 저장된 proposal blocker는 없습니다.")
            with detail_cols[1]:
                st.markdown("##### Review Gaps")
                if review_gaps:
                    for gap in review_gaps:
                        st.info(gap)
                else:
                    st.success("현재 저장된 review gap은 없습니다.")
            st.markdown("##### Operator Decision")
            st.write(
                {
                    "decision": operator_decision.get("decision"),
                    "reason": operator_decision.get("reason"),
                    "next_action": operator_decision.get("next_action"),
                    "review_date": operator_decision.get("review_date"),
                }
            )

        with pre_live_tab:
            st.caption("proposal 저장 당시 snapshot과 현재 Pre-Live registry 상태를 비교하는 읽기 전용 영역입니다.")
            pre_live_by_registry_id = _portfolio_proposal_pre_live_record_by_registry_id(pre_live_rows)
            st.dataframe(
                _build_portfolio_proposal_pre_live_feedback_summary_rows(proposal_rows, pre_live_by_registry_id),
                width="stretch",
                hide_index=True,
            )
            selected_label = st.selectbox(
                "Review Pre-Live Feedback",
                options=labels,
                key="portfolio_proposal_pre_live_feedback_selected_record",
            )
            selected_row = proposal_rows[labels.index(selected_label)]
            feedback_df = _portfolio_proposal_pre_live_feedback_rows(selected_row, pre_live_by_registry_id)
            feedback_gaps = _portfolio_proposal_pre_live_feedback_gaps(selected_row, pre_live_by_registry_id)
            if feedback_df.empty:
                st.info("이 proposal에는 Pre-Live feedback을 연결할 component candidate가 없습니다.")
            else:
                render_status_card_grid(
                    [
                        {"title": "Components", "value": len(feedback_df), "tone": "neutral"},
                        {
                            "title": "Linked Pre-Live",
                            "value": int((feedback_df["Current Pre-Live"] != "not_started").sum()),
                            "tone": "positive",
                        },
                        {
                            "title": "Paper Tracking",
                            "value": int((feedback_df["Current Pre-Live"] == "paper_tracking").sum()),
                            "tone": "positive",
                        },
                        {
                            "title": "Feedback Gaps",
                            "value": len(feedback_gaps),
                            "tone": "positive" if not feedback_gaps else "warning",
                        },
                    ]
                )
                st.dataframe(feedback_df, width="stretch", hide_index=True)
                if feedback_gaps:
                    for gap in feedback_gaps:
                        st.warning(gap)
                else:
                    st.success("현재 Pre-Live feedback gap은 없습니다.")

        with paper_tab:
            st.caption(
                "proposal evidence snapshot과 현재 Pre-Live result snapshot의 CAGR / MDD를 비교합니다. "
                "실제 paper PnL 시계열 계산은 아직 아닙니다."
            )
            pre_live_by_registry_id = _portfolio_proposal_pre_live_record_by_registry_id(pre_live_rows)
            st.dataframe(
                _build_portfolio_proposal_paper_tracking_feedback_summary_rows(proposal_rows, pre_live_by_registry_id),
                width="stretch",
                hide_index=True,
            )
            selected_label = st.selectbox(
                "Review Paper Tracking Feedback",
                options=labels,
                key="portfolio_proposal_paper_tracking_feedback_selected_record",
            )
            selected_row = proposal_rows[labels.index(selected_label)]
            feedback_df = _portfolio_proposal_paper_tracking_feedback_rows(selected_row, pre_live_by_registry_id)
            feedback_gaps = _portfolio_proposal_paper_tracking_feedback_gaps(selected_row, pre_live_by_registry_id)
            if feedback_df.empty:
                st.info("이 proposal에는 paper tracking feedback을 연결할 component candidate가 없습니다.")
            else:
                render_status_card_grid(
                    [
                        {"title": "Components", "value": len(feedback_df), "tone": "neutral"},
                        {
                            "title": "Paper Tracking",
                            "value": int((feedback_df["Current Pre-Live"] == "paper_tracking").sum()),
                            "tone": "positive",
                        },
                        {
                            "title": "Worsened",
                            "value": int((feedback_df["Performance Signal"] == "worsened").sum()),
                            "tone": "warning",
                        },
                        {
                            "title": "Stable / Better",
                            "value": int((feedback_df["Performance Signal"] == "stable_or_better").sum()),
                            "tone": "positive",
                        },
                    ]
                )
                st.caption(
                    "Delta는 current Pre-Live result snapshot에서 proposal 저장 당시 evidence snapshot을 뺀 값입니다. "
                    f"CAGR `{PORTFOLIO_PROPOSAL_PAPER_CAGR_DETERIORATION_THRESHOLD}` 이하 또는 "
                    f"MDD `{PORTFOLIO_PROPOSAL_PAPER_MDD_DETERIORATION_THRESHOLD}` 이하로 악화되면 `worsened`입니다."
                )
                st.dataframe(feedback_df, width="stretch", hide_index=True)
                if feedback_gaps:
                    for gap in feedback_gaps:
                        st.warning(gap)
                else:
                    st.success("현재 paper tracking performance feedback gap은 없습니다.")

        with json_tab:
            st.dataframe(_build_portfolio_proposal_rows_for_display(proposal_rows), width="stretch", hide_index=True)
            selected_label = st.selectbox("Inspect Portfolio Proposal", options=labels, key="portfolio_proposal_selected_record")
            selected_row = proposal_rows[labels.index(selected_label)]
            st.json(selected_row)


# Render the Portfolio Proposal workspace as one construction draft flow toward Live Readiness.
def render_portfolio_proposal_workspace() -> None:
    st.markdown("### Portfolio Proposal")
    st.caption(
        "7단계 Portfolio Proposal 작업 공간입니다. Candidate Review를 통과한 후보를 목적 / 역할 / 비중이 있는 "
        "포트폴리오 초안으로 바꿔 이후 Live Readiness가 읽을 수 있게 만듭니다."
    )

    current_rows = _load_current_candidate_registry_latest()
    pre_live_rows = _load_pre_live_candidate_registry_latest()
    proposal_rows = load_portfolio_proposals()
    pre_live_status_by_registry_id = _portfolio_proposal_pre_live_status_by_registry_id(pre_live_rows)

    pre_live_notice = st.session_state.get("portfolio_proposal_from_pre_live_notice")
    if pre_live_notice:
        st.info(pre_live_notice)
        st.session_state["portfolio_proposal_from_pre_live_notice"] = None

    render_status_card_grid(
        [
            {"title": "Current Candidates", "value": len(current_rows), "tone": "positive" if current_rows else "neutral"},
            {"title": "Pre-Live Records", "value": len(pre_live_rows), "tone": "positive" if pre_live_rows else "neutral"},
            {"title": "Saved Proposals", "value": len(proposal_rows), "tone": "positive" if proposal_rows else "neutral"},
            {"title": "Live Approval", "value": "Disabled", "detail": "이 화면은 승인/주문이 아닙니다.", "tone": "neutral"},
        ]
    )

    with st.container(border=True):
        st.markdown("#### Portfolio Proposal 산출물 흐름")
        render_artifact_pipeline(
            [
                {
                    "title": "후보 묶음",
                    "detail": "Candidate Review를 통과한 후보 선택",
                    "status": f"{len(current_rows)}개 후보",
                    "tone": "positive" if current_rows else "neutral",
                },
                {
                    "title": "구성 초안",
                    "detail": "목적, 역할, 비중, capital scope 결정",
                    "status": "현재 화면에서 작성",
                    "tone": "warning",
                },
                {
                    "title": "Live Readiness 후보",
                    "detail": "다음 단계가 읽을 수 있는 proposal draft",
                    "status": "3번에서 판정",
                    "tone": "neutral",
                },
            ]
        )

    st.divider()
    st.markdown("#### 1. Proposal 후보 확인")
    with st.container(border=True):
        render_stage_brief(
            purpose="후보 전략을 바로 실전 검토로 보내지 않고, 포트폴리오에 들어갈 구성 후보로 먼저 묶습니다.",
            result="Proposal component 후보",
        )
        if not current_rows:
            st.info("Portfolio Proposal을 만들 current candidate가 없습니다.")
            st.caption(f"먼저 Candidate Review에서 `{CURRENT_CANDIDATE_REGISTRY_FILE}`에 후보를 남겨야 합니다.")
            selected_rows: list[dict[str, Any]] = []
        else:
            with st.expander("Current Candidate 목록 보기", expanded=False):
                st.dataframe(_build_current_candidate_registry_rows_for_display(current_rows), width="stretch", hide_index=True)
            label_to_row = {_current_candidate_registry_selection_label(row): row for row in current_rows}
            _sync_component_selection_state(label_to_row)
            selected_labels = st.multiselect(
                "Proposal Components",
                options=list(label_to_row.keys()),
                max_selections=6,
                key="portfolio_proposal_component_selection",
                help="포트폴리오 제안에 포함할 후보를 고릅니다. Candidate Review에서 넘어온 후보는 자동 선택됩니다.",
            )
            selected_rows = [label_to_row[label] for label in selected_labels]
            if selected_rows:
                render_badge_strip(
                    [
                        {"label": "Selected", "value": len(selected_rows), "tone": "positive"},
                        {
                            "label": "Mode",
                            "value": "단일 후보 proposal" if len(selected_rows) == 1 else "다중 후보 proposal",
                            "tone": "neutral",
                        },
                    ]
                )
            else:
                st.info("포트폴리오 제안 후보를 먼저 선택하세요.")

    st.markdown("#### 2. 목적 / 역할 / 비중 설계")
    with st.container(border=True):
        render_stage_brief(
            purpose="Live Readiness가 후보를 포트폴리오 형태로 읽을 수 있게 목적과 비중을 정합니다.",
            result="Portfolio construction draft",
        )
        default_proposal_id = f"proposal_{date.today().strftime('%Y%m%d')}_{uuid4().hex[:6]}"
        default_status = "live_readiness_candidate" if selected_rows else "draft"
        objective_cols = st.columns(4, gap="small")
        with objective_cols[0]:
            proposal_id = st.text_input("Proposal ID", value=default_proposal_id, key="portfolio_proposal_id")
        with objective_cols[1]:
            proposal_status = st.selectbox(
                "Status",
                options=PORTFOLIO_PROPOSAL_STATUS_OPTIONS,
                index=PORTFOLIO_PROPOSAL_STATUS_OPTIONS.index(default_status),
                key="portfolio_proposal_status",
                help="Proposal draft 상태입니다. live approval 상태가 아닙니다.",
            )
        with objective_cols[2]:
            proposal_type = st.selectbox(
                "Type",
                options=PORTFOLIO_PROPOSAL_TYPE_OPTIONS,
                index=0,
                key="portfolio_proposal_type",
            )
        with objective_cols[3]:
            capital_scope = st.selectbox(
                "Capital Scope",
                options=["paper_only", "review_only", "small_trial_candidate"],
                index=0,
                key="portfolio_proposal_capital_scope",
            )
        goal_cols = st.columns(3, gap="small")
        with goal_cols[0]:
            primary_goal = st.text_input("Primary Goal", value="balanced_growth", key="portfolio_proposal_primary_goal")
        with goal_cols[1]:
            secondary_goal = st.text_input("Secondary Goal", value="drawdown_control", key="portfolio_proposal_secondary_goal")
        with goal_cols[2]:
            target_holding_style = st.text_input(
                "Review Cadence",
                value="monthly_or_quarterly_review",
                key="portfolio_proposal_holding_style",
            )
        construction_cols = st.columns(2, gap="small")
        with construction_cols[0]:
            weighting_method = st.selectbox(
                "Weighting Method",
                options=PORTFOLIO_PROPOSAL_WEIGHTING_OPTIONS,
                index=1,
                key="portfolio_proposal_weighting_method",
            )
        with construction_cols[1]:
            benchmark_policy = st.text_input(
                "Benchmark Policy",
                value="compare_or_saved_portfolio_context_required",
                key="portfolio_proposal_benchmark_policy",
            )

        component_inputs: dict[str, dict[str, Any]] = {}
        equal_weight = round(100.0 / len(selected_rows), 4) if selected_rows else 0.0
        for idx, row in enumerate(selected_rows):
            registry_id = str(row.get("registry_id") or f"candidate_{idx}")
            result = dict(row.get("result") or {})
            pre_live_status = pre_live_status_by_registry_id.get(registry_id, "not_started")
            role_index = 0 if len(selected_rows) == 1 else min(idx, len(PORTFOLIO_PROPOSAL_ROLE_OPTIONS) - 1)
            with st.container(border=True):
                st.markdown(f"##### {row.get('title') or registry_id}")
                render_badge_strip(
                    [
                        {"label": "Family", "value": row.get("strategy_family") or "-", "tone": "neutral"},
                        {"label": "Candidate Role", "value": row.get("candidate_role") or "-", "tone": "neutral"},
                        {
                            "label": "Pre-Live",
                            "value": pre_live_status,
                            "tone": "positive" if pre_live_status == "paper_tracking" else "warning",
                        },
                        {
                            "label": "Data Trust",
                            "value": _component_data_trust_status(row),
                            "tone": "positive" if _component_data_trust_status(row) == "ok" else "warning",
                        },
                    ]
                )
                render_status_card_grid(
                    [
                        {"title": "CAGR", "value": result.get("cagr") or "-", "tone": "neutral"},
                        {"title": "MDD", "value": result.get("mdd") or "-", "tone": "neutral"},
                        {"title": "Promotion", "value": result.get("promotion") or "-", "tone": "positive"},
                        {"title": "Shortlist", "value": result.get("shortlist") or "-", "tone": "warning"},
                    ]
                )
                input_cols = st.columns([0.25, 0.18, 0.57], gap="small")
                with input_cols[0]:
                    proposal_role = st.selectbox(
                        "Proposal Role",
                        options=PORTFOLIO_PROPOSAL_ROLE_OPTIONS,
                        index=role_index,
                        key=f"portfolio_proposal_role_{registry_id}",
                    )
                with input_cols[1]:
                    target_weight = st.number_input(
                        "Target Weight %",
                        min_value=0.0,
                        max_value=100.0,
                        value=equal_weight if weighting_method == "equal_weight" else 0.0,
                        step=1.0,
                        key=f"portfolio_proposal_weight_{registry_id}_{weighting_method}",
                    )
                with input_cols[2]:
                    weight_reason = st.text_input(
                        "Weight Reason",
                        value="Live Readiness 검토용 초기 비중",
                        key=f"portfolio_proposal_weight_reason_{registry_id}",
                    )
                component_inputs[registry_id] = {
                    "proposal_role": proposal_role,
                    "target_weight": float(target_weight),
                    "weight_reason": weight_reason,
                    "data_trust_status": _component_data_trust_status(row),
                    "pre_live_status": pre_live_status,
                    "open_candidate_blockers": [],
                }

        total_weight = round(sum(float(value.get("target_weight") or 0.0) for value in component_inputs.values()), 4)
        render_badge_strip(
            [
                {
                    "label": "Target Weight Total",
                    "value": f"{total_weight}%",
                    "tone": "positive" if selected_rows and abs(total_weight - 100.0) <= 0.01 else "warning",
                },
                {"label": "Components", "value": len(selected_rows), "tone": "positive" if selected_rows else "warning"},
                {"label": "Weighting", "value": weighting_method, "tone": "neutral"},
            ]
        )

    st.markdown("#### 3. Proposal 저장 및 다음 단계 판단")
    with st.container(border=True):
        readiness_slot = st.empty()
        st.markdown("##### 검토 메모 / 다음 행동 입력")
        operator_decision = st.selectbox(
            "Operator Decision",
            options=["ready_for_live_readiness_review", "draft_for_review", "needs_more_evidence", "hold"],
            index=0,
            key="portfolio_proposal_operator_decision",
            help="이 값은 proposal 검토 상태이며 live approval이 아닙니다.",
        )
        operator_reason = st.text_area(
            "Operator Reason",
            value="후보 묶음의 목적, 역할, 비중을 Live Readiness에서 검토할 수 있도록 proposal draft를 남긴다.",
            key="portfolio_proposal_operator_reason",
        )
        next_action = st.text_area(
            "Next Action",
            value="Live Readiness 단계에서 component data trust, Real-Money status, Pre-Live status, 비중 근거를 같이 점검한다.",
            key="portfolio_proposal_next_action",
        )
        use_review_date = st.checkbox("Review Date 지정", value=True, key="portfolio_proposal_use_review_date")
        review_date_value: date | None = None
        if use_review_date:
            review_date_value = st.date_input(
                "Review Date",
                value=date.today() + timedelta(days=30),
                key="portfolio_proposal_review_date",
            )

        open_blockers = _portfolio_proposal_open_blockers(
            selected_rows=selected_rows,
            component_inputs=component_inputs,
            proposal_id=proposal_id,
            total_weight=total_weight,
        )
        readiness = _build_portfolio_proposal_readiness_evaluation(
            selected_rows=selected_rows,
            component_inputs=component_inputs,
            proposal_id=proposal_id,
            total_weight=total_weight,
            operator_reason=operator_reason,
            next_action=next_action,
            review_date_value=review_date_value,
            open_blockers=open_blockers,
        )
        proposal_row = _build_portfolio_proposal_row(
            proposal_id=proposal_id,
            proposal_status=proposal_status,
            proposal_type=proposal_type,
            primary_goal=primary_goal,
            secondary_goal=secondary_goal,
            target_holding_style=target_holding_style,
            capital_scope=capital_scope,
            weighting_method=weighting_method,
            benchmark_policy=benchmark_policy,
            selected_rows=selected_rows,
            component_inputs=component_inputs,
            open_blockers=open_blockers,
            operator_decision=operator_decision,
            operator_reason=operator_reason,
            next_action=next_action,
            review_date_value=review_date_value,
        )

        with readiness_slot.container(border=True):
            st.markdown("##### Live Readiness 진입 평가")
            render_readiness_route_panel(
                route_label=str(readiness["route_label"]),
                score=float(readiness["score"]),
                blockers_count=len(readiness["blocking_reasons"]),
                verdict=str(readiness["verdict"]),
                next_action=str(readiness["next_action"]),
                route_title="Next Route",
                score_title="Readiness",
            )
            render_badge_strip(
                [
                    {
                        "label": "Save Draft",
                        "value": "가능" if readiness["can_save_proposal"] else "확인 필요",
                        "tone": "positive" if readiness["can_save_proposal"] else "danger",
                    },
                    {
                        "label": "Live Readiness",
                        "value": "후보 가능" if readiness["can_move_to_live_readiness"] else "보강 필요",
                        "tone": "positive" if readiness["can_move_to_live_readiness"] else "warning",
                    },
                    {
                        "label": "Blockers",
                        "value": len(readiness["blocking_reasons"]),
                        "tone": "positive" if not readiness["blocking_reasons"] else "warning",
                    },
                ]
            )
            st.progress(max(0.0, min(float(readiness["score"]) / 10.0, 1.0)))
            if readiness["can_move_to_live_readiness"]:
                st.success("이 proposal은 저장 후 Live Readiness 후보로 넘길 수 있는 형태입니다.")
            elif readiness["can_save_proposal"]:
                st.info("proposal draft 저장은 가능하지만, Live Readiness 전 보강 항목이 남아 있습니다.")
            else:
                st.error("저장 전 확인 필요: " + ", ".join(str(item) for item in readiness["blocking_reasons"]))

        st.markdown("##### 저장 및 다음 단계")
        action_cols = st.columns(2, gap="small")
        with action_cols[0]:
            if st.button(
                "Save Portfolio Proposal Draft",
                key="save_portfolio_proposal_draft",
                disabled=not bool(readiness["can_save_proposal"]),
                width="stretch",
            ):
                append_portfolio_proposal(proposal_row)
                st.success(f"Portfolio Proposal `{proposal_row['proposal_id']}`를 저장했습니다. live approval은 아닙니다.")
                st.rerun()
        with action_cols[1]:
            st.button(
                "Open Live Readiness",
                key="open_live_readiness_placeholder",
                disabled=True,
                width="stretch",
                help="Live Readiness 단계는 다음 작업에서 연결할 예정입니다.",
            )
        st.caption("`Open Live Readiness`는 다음 단계 개발 전까지 비활성화됩니다. 이 화면에서는 proposal draft 저장까지만 처리합니다.")

        with st.expander("상세 보기", expanded=False):
            criteria_tab, json_tab = st.tabs(["판단 기준", "Portfolio Proposal JSON"])
            with criteria_tab:
                st.dataframe(pd.DataFrame(readiness["checks"]), width="stretch", hide_index=True)
                if open_blockers:
                    st.warning("저장 blocker: " + ", ".join(open_blockers))
            with json_tab:
                st.json(proposal_row)

    st.divider()
    _render_saved_proposal_details(proposal_rows, pre_live_rows)
