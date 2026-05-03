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
    PAPER_PORTFOLIO_LEDGER_REVIEW_CADENCE_OPTIONS,
    PAPER_PORTFOLIO_LEDGER_STATUS_OPTIONS,
    PORTFOLIO_PROPOSAL_PAPER_CAGR_DETERIORATION_THRESHOLD,
    PORTFOLIO_PROPOSAL_PAPER_MDD_DETERIORATION_THRESHOLD,
    PORTFOLIO_PROPOSAL_ROLE_DESCRIPTIONS,
    PORTFOLIO_PROPOSAL_ROLE_OPTIONS,
    PORTFOLIO_PROPOSAL_STATUS_OPTIONS,
    PORTFOLIO_PROPOSAL_TYPE_OPTIONS,
    PORTFOLIO_PROPOSAL_WEIGHTING_OPTIONS,
    _build_portfolio_risk_validation_input_for_proposal,
    _build_portfolio_risk_validation_input_for_single_candidate,
    _build_portfolio_risk_validation_result,
    _build_portfolio_risk_validation_summary_rows,
    _build_portfolio_proposal_component_rows,
    _build_portfolio_proposal_direct_readiness_evaluation,
    _build_portfolio_proposal_monitoring_rows,
    _build_portfolio_proposal_paper_tracking_feedback_summary_rows,
    _build_portfolio_proposal_pre_live_feedback_summary_rows,
    _build_portfolio_proposal_readiness_evaluation,
    _build_portfolio_proposal_row,
    _build_portfolio_proposal_rows_for_display,
    _build_paper_portfolio_ledger_component_rows,
    _build_paper_portfolio_ledger_row,
    _build_paper_portfolio_ledger_rows_for_display,
    _build_paper_portfolio_ledger_save_evaluation,
    _paper_ledger_default_benchmark,
    _paper_ledger_parse_trigger_lines,
    _paper_ledger_slug,
    _portfolio_proposal_monitoring_blockers,
    _portfolio_proposal_monitoring_state,
    _portfolio_proposal_open_blockers,
    _portfolio_proposal_paper_tracking_feedback_gaps,
    _portfolio_proposal_paper_tracking_feedback_rows,
    _portfolio_proposal_candidate_data_trust_status,
    _portfolio_proposal_current_candidate_by_registry_id,
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
    PAPER_PORTFOLIO_LEDGER_FILE,
    append_paper_portfolio_ledger_row,
    append_portfolio_proposal,
    load_current_candidate_registry_latest as _load_current_candidate_registry_latest,
    load_paper_portfolio_ledger,
    load_portfolio_proposals,
    load_pre_live_candidate_registry_latest as _load_pre_live_candidate_registry_latest,
)


# Turn a current candidate row into an OK / warning / missing data trust label for proposal components.
def _component_data_trust_status(row: dict[str, Any]) -> str:
    return _portfolio_proposal_candidate_data_trust_status(row)


# Keep Streamlit multiselect state valid after registry rows change or a handoff label disappears.
def _sync_component_selection_state(label_to_row: dict[str, dict[str, Any]]) -> None:
    key = "portfolio_proposal_component_selection"
    current_value = st.session_state.get(key)
    if current_value is None:
        return
    valid_labels = [label for label in list(current_value) if label in label_to_row]
    if valid_labels != list(current_value):
        st.session_state[key] = valid_labels


def _render_paper_ledger_draft_controls(
    validation: dict[str, Any],
    *,
    key_prefix: str,
    source_is_persisted: bool,
    paper_ledger_rows: list[dict[str, Any]],
) -> None:
    st.markdown("##### Paper Tracking Ledger Draft")
    st.caption(
        "Phase 33 영역입니다. Validation Pack을 여는 것만으로는 저장되지 않고, "
        "`Save Paper Tracking Ledger`를 명시적으로 눌러야 append-only ledger에 기록됩니다."
    )
    existing_ledger_ids = {
        str(row.get("ledger_id") or "").strip()
        for row in paper_ledger_rows
        if str(row.get("ledger_id") or "").strip()
    }
    source_id = str(validation.get("source_id") or "").strip()
    source_slug = _paper_ledger_slug(source_id)
    if st.session_state.pop(f"{key_prefix}_reset_ledger_id_after_save", False):
        st.session_state.pop(f"{key_prefix}_ledger_id", None)
    default_ledger_id = f"paper_{source_slug}_{date.today().strftime('%Y%m%d')}_{uuid4().hex[:6]}"
    default_triggers = "\n".join(
        [
            f"CAGR delta <= {PORTFOLIO_PROPOSAL_PAPER_CAGR_DETERIORATION_THRESHOLD}",
            f"MDD delta <= {PORTFOLIO_PROPOSAL_PAPER_MDD_DETERIORATION_THRESHOLD}",
            "Pre-Live status drift from paper_tracking",
            "Benchmark-relative underperformance review",
        ]
    )

    input_cols = st.columns(4, gap="small")
    with input_cols[0]:
        ledger_id = st.text_input("Ledger ID", value=default_ledger_id, key=f"{key_prefix}_ledger_id")
    with input_cols[1]:
        paper_status = st.selectbox(
            "Paper Status",
            options=PAPER_PORTFOLIO_LEDGER_STATUS_OPTIONS,
            index=0,
            key=f"{key_prefix}_paper_status",
        )
    with input_cols[2]:
        tracking_start_date = st.date_input(
            "Tracking Start Date",
            value=date.today(),
            key=f"{key_prefix}_tracking_start_date",
        )
    with input_cols[3]:
        review_cadence = st.selectbox(
            "Review Cadence",
            options=PAPER_PORTFOLIO_LEDGER_REVIEW_CADENCE_OPTIONS,
            index=1,
            key=f"{key_prefix}_review_cadence",
        )
    benchmark_note_cols = st.columns([0.32, 0.68], gap="small")
    with benchmark_note_cols[0]:
        tracking_benchmark = st.text_input(
            "Tracking Benchmark",
            value=_paper_ledger_default_benchmark(validation),
            key=f"{key_prefix}_tracking_benchmark",
        )
    with benchmark_note_cols[1]:
        operator_note = st.text_input(
            "Operator Note",
            value="Phase 32 handoff 이후 실제 돈 없이 paper tracking 조건을 기록한다.",
            key=f"{key_prefix}_operator_note",
        )
    trigger_text = st.text_area(
        "Review Triggers",
        value=default_triggers,
        key=f"{key_prefix}_review_triggers",
        help="한 줄에 하나씩 stop / re-review trigger를 남깁니다.",
    )
    review_triggers = _paper_ledger_parse_trigger_lines(trigger_text)
    evaluation = _build_paper_portfolio_ledger_save_evaluation(
        validation=validation,
        ledger_id=ledger_id,
        source_is_persisted=source_is_persisted,
        tracking_start_date=tracking_start_date,
        tracking_benchmark=tracking_benchmark,
        review_cadence=review_cadence,
        review_triggers=review_triggers,
        existing_ledger_ids=existing_ledger_ids,
    )
    render_readiness_route_panel(
        route_label=str(evaluation.get("route") or "-"),
        score=float(evaluation.get("score") or 0.0),
        blockers_count=len(evaluation.get("blockers") or []),
        verdict=str(evaluation.get("verdict") or "-"),
        next_action=str(evaluation.get("next_action") or "-"),
        route_title="Paper Ledger Route",
        score_title="Ledger Score",
    )
    render_badge_strip(
        [
            {"label": "Source", "value": validation.get("source_type") or "-", "tone": "neutral"},
            {"label": "Persisted", "value": "yes" if source_is_persisted else "no", "tone": "positive" if source_is_persisted else "warning"},
            {"label": "Triggers", "value": len(review_triggers), "tone": "positive" if review_triggers else "warning"},
            {"label": "Live Approval", "value": "Disabled", "tone": "neutral"},
        ]
    )
    if evaluation.get("blockers"):
        for blocker in list(evaluation.get("blockers") or []):
            st.warning(str(blocker))

    paper_row = _build_paper_portfolio_ledger_row(
        validation=validation,
        ledger_id=ledger_id,
        paper_status=paper_status,
        tracking_start_date=tracking_start_date,
        tracking_benchmark=tracking_benchmark,
        review_cadence=review_cadence,
        review_triggers=review_triggers,
        operator_note=operator_note,
    )
    action_cols = st.columns(2, gap="small")
    with action_cols[0]:
        if st.button(
            "Save Paper Tracking Ledger",
            key=f"{key_prefix}_save_paper_ledger",
            disabled=not bool(evaluation.get("can_save")),
            width="stretch",
        ):
            append_paper_portfolio_ledger_row(paper_row)
            st.session_state["paper_portfolio_ledger_save_notice"] = (
                f"Paper Tracking Ledger `{paper_row['ledger_id']}`를 저장했습니다. "
                "이 기록은 live approval이나 주문 지시가 아닙니다."
            )
            st.session_state[f"{key_prefix}_reset_ledger_id_after_save"] = True
            st.rerun()
    with action_cols[1]:
        st.button(
            "Open Final Selection",
            key=f"{key_prefix}_open_final_selection_placeholder",
            disabled=True,
            width="stretch",
            help="Phase 34 Final Selection Decision Pack에서 연결할 예정입니다.",
        )
    with st.expander("Paper Ledger JSON Preview", expanded=False):
        st.json(paper_row)
        st.caption(f"Path: {PAPER_PORTFOLIO_LEDGER_FILE}")


# Render the Phase 31 read-only risk validation pack for a selected candidate or proposal.
def _render_portfolio_risk_validation_pack(
    validation: dict[str, Any],
    *,
    title: str,
    paper_ledger_rows: list[dict[str, Any]] | None = None,
    source_is_persisted: bool = True,
) -> None:
    metrics = dict(validation.get("metrics") or {})
    hard_blockers = list(validation.get("hard_blockers") or [])
    paper_tracking_gaps = list(validation.get("paper_tracking_gaps") or [])
    review_gaps = list(validation.get("review_gaps") or [])
    route = str(validation.get("validation_route") or "-")
    score = float(validation.get("validation_score") or 0.0)
    route_tone = "positive" if route == "READY_FOR_ROBUSTNESS_REVIEW" else "warning"
    if route == "BLOCKED_FOR_LIVE_READINESS":
        route_tone = "danger"

    st.markdown(f"##### {title}")
    render_readiness_route_panel(
        route_label=route,
        score=score,
        blockers_count=len(hard_blockers),
        verdict=str(validation.get("verdict") or "-"),
        next_action=str(validation.get("next_action") or "-"),
        route_title="Validation Route",
        score_title="Risk Score",
    )
    render_badge_strip(
        [
            {"label": "Source", "value": validation.get("source_type") or "-", "tone": "neutral"},
            {"label": "Components", "value": metrics.get("active_components", 0), "tone": "positive"},
            {"label": "Weight Total", "value": f"{metrics.get('weight_total', 0)}%", "tone": "neutral"},
            {"label": "Max Weight", "value": f"{metrics.get('max_weight', 0)}%", "tone": "neutral"},
            {"label": "Next Phase", "value": "Phase 32" if route == "READY_FOR_ROBUSTNESS_REVIEW" else "보강 후 판단", "tone": route_tone},
        ]
    )
    st.progress(max(0.0, min(score / 10.0, 1.0)))

    component_df = pd.DataFrame(validation.get("component_rows") or [])
    if component_df.empty:
        st.info("Validation Pack에 연결된 component가 없습니다.")
    else:
        st.dataframe(component_df, width="stretch", hide_index=True)

    gap_cols = st.columns(3, gap="small")
    with gap_cols[0]:
        st.markdown("###### Hard Blockers")
        if hard_blockers:
            for blocker in hard_blockers:
                st.error(blocker)
        else:
            st.success("hard blocker 없음")
    with gap_cols[1]:
        st.markdown("###### Paper Tracking")
        if paper_tracking_gaps:
            for gap in paper_tracking_gaps:
                st.warning(gap)
        else:
            st.success("paper tracking gap 없음")
    with gap_cols[2]:
        st.markdown("###### Review Gaps")
        if review_gaps:
            for gap in review_gaps:
                st.info(gap)
        else:
            st.success("review gap 없음")

    with st.expander("검증 기준 / 다음 단계 안내", expanded=False):
        st.dataframe(pd.DataFrame(validation.get("checks") or []), width="stretch", hide_index=True)
        st.json(validation.get("handoff_summary") or {})
        st.caption("이 결과는 live approval이나 주문 지시가 아니라 다음 robustness 검증 단계로 넘길 수 있는지 보는 읽기 전용 검증 pack입니다.")

    robustness = dict(validation.get("robustness_validation") or {})
    if robustness:
        st.markdown("##### Robustness / Stress Validation Preview")
        robustness_route = str(robustness.get("robustness_route") or "-")
        robustness_score = float(robustness.get("robustness_score") or 0.0)
        robustness_tone = "positive" if robustness_route == "READY_FOR_STRESS_SWEEP" else "warning"
        if robustness_route == "BLOCKED_FOR_ROBUSTNESS":
            robustness_tone = "danger"
        robustness_blockers = list(robustness.get("blockers") or [])
        input_gaps = list(robustness.get("input_gaps") or [])
        suggested_sweeps = list(robustness.get("suggested_sweeps") or [])
        robustness_metrics = dict(robustness.get("metrics") or {})
        stress_metrics = dict(robustness.get("stress_metrics") or {})
        phase33_handoff = dict(robustness.get("phase33_handoff") or {})
        render_readiness_route_panel(
            route_label=robustness_route,
            score=robustness_score,
            blockers_count=len(robustness_blockers),
            verdict=str(robustness.get("verdict") or "-"),
            next_action=str(robustness.get("next_action") or "-"),
            route_title="Robustness Route",
            score_title="Robustness Score",
        )
        render_badge_strip(
            [
                {"label": "Components", "value": robustness_metrics.get("components", 0), "tone": "neutral"},
                {"label": "Families", "value": robustness_metrics.get("families", 0), "tone": "neutral"},
                {"label": "Benchmarks", "value": robustness_metrics.get("benchmarks", 0), "tone": "neutral"},
                {"label": "Suggested Sweeps", "value": robustness_metrics.get("suggested_sweeps", 0), "tone": robustness_tone},
                {"label": "Stress Rows", "value": stress_metrics.get("rows", 0), "tone": "neutral"},
                {"label": "Stress Ready", "value": stress_metrics.get("ready_rows", 0), "tone": robustness_tone},
            ]
        )
        robustness_df = pd.DataFrame(robustness.get("component_rows") or [])
        if robustness_df.empty:
            st.info("Robustness preview에 연결된 component가 없습니다.")
        else:
            st.dataframe(robustness_df, width="stretch", hide_index=True)
        robustness_cols = st.columns(3, gap="small")
        with robustness_cols[0]:
            st.markdown("###### Robustness Blockers")
            if robustness_blockers:
                for blocker in robustness_blockers:
                    st.error(blocker)
            else:
                st.success("robustness blocker 없음")
        with robustness_cols[1]:
            st.markdown("###### Input Gaps")
            if input_gaps:
                for gap in input_gaps:
                    st.warning(gap)
            else:
                st.success("input gap 없음")
        with robustness_cols[2]:
            st.markdown("###### Suggested Sweeps")
            for sweep in suggested_sweeps[:6]:
                st.info(sweep)
        with st.expander("Robustness 기준 / 다음 실행 안내", expanded=False):
            st.dataframe(pd.DataFrame(robustness.get("checks") or []), width="stretch", hide_index=True)
            st.json(robustness.get("stress_result_contract") or {})
            st.caption("이 preview는 Phase 32의 첫 pass입니다. 기간 분할 / benchmark 변경 / parameter sensitivity를 실제 실행했다는 뜻은 아닙니다.")

        st.markdown("##### Stress / Sensitivity Summary")
        stress_df = pd.DataFrame(robustness.get("stress_summary_rows") or [])
        if stress_df.empty:
            st.info("Stress summary row가 아직 없습니다.")
        else:
            st.dataframe(stress_df, width="stretch", hide_index=True)
            st.caption("`Result Status = NOT_RUN`은 아직 실제 stress runner가 실행되지 않았고, Phase 32가 읽을 결과 계약만 준비됐다는 뜻입니다.")

        if phase33_handoff:
            handoff_blockers = int(dict(phase33_handoff.get("metrics") or {}).get("blocked_stress_rows") or 0)
            render_readiness_route_panel(
                route_label=str(phase33_handoff.get("handoff_route") or "-"),
                score=float(phase33_handoff.get("handoff_score") or 0.0),
                blockers_count=handoff_blockers,
                verdict=str(phase33_handoff.get("verdict") or "-"),
                next_action=str(phase33_handoff.get("next_action") or "-"),
                route_title="Phase 33 Handoff",
                score_title="Handoff Score",
            )
            with st.expander("Phase 33 paper ledger 준비 기준", expanded=False):
                st.dataframe(pd.DataFrame(phase33_handoff.get("requirements") or []), width="stretch", hide_index=True)
                st.caption("이 handoff는 paper ledger 준비 가능성만 말합니다. live approval이나 주문 지시가 아닙니다.")
            key_scope = "persisted" if source_is_persisted else "draft"
            key_source = _paper_ledger_slug(f"{key_scope}_{validation.get('source_type')}_{validation.get('source_id')}")
            _render_paper_ledger_draft_controls(
                validation,
                key_prefix=f"paper_ledger_{key_source}",
                source_is_persisted=source_is_persisted,
                paper_ledger_rows=paper_ledger_rows or [],
            )


def _render_saved_paper_ledger_details(paper_ledger_rows: list[dict[str, Any]]) -> None:
    if not paper_ledger_rows:
        return

    with st.container(border=True):
        st.markdown("#### 저장된 Paper Tracking Ledger 확인")
        st.caption("Phase 33에서 저장한 paper tracking 기록을 다시 읽고 Phase 34 handoff 준비 상태를 확인합니다.")
        st.dataframe(_build_paper_portfolio_ledger_rows_for_display(paper_ledger_rows), width="stretch", hide_index=True)
        labels = [
            f"{row.get('updated_at') or row.get('created_at')} | {row.get('paper_status')} | {row.get('ledger_id')}"
            for row in paper_ledger_rows
        ]
        selected_label = st.selectbox(
            "Review Paper Tracking Ledger",
            options=labels,
            key="paper_portfolio_ledger_selected_record",
        )
        selected_row = paper_ledger_rows[labels.index(selected_label)]
        handoff = dict(selected_row.get("phase34_handoff") or {})
        baseline = dict(selected_row.get("baseline_snapshot") or {})
        render_readiness_route_panel(
            route_label=str(handoff.get("handoff_route") or "-"),
            score=float(handoff.get("handoff_score") or 0.0),
            blockers_count=int(dict(handoff.get("metrics") or {}).get("blockers") or 0),
            verdict=str(handoff.get("verdict") or "-"),
            next_action=str(handoff.get("next_action") or "-"),
            route_title="Phase 34 Handoff",
            score_title="Handoff Score",
        )
        render_badge_strip(
            [
                {"label": "Source", "value": f"{selected_row.get('source_type')} / {selected_row.get('source_id')}", "tone": "neutral"},
                {"label": "Status", "value": selected_row.get("paper_status") or "-", "tone": "positive" if selected_row.get("paper_status") == "active_tracking" else "warning"},
                {"label": "Weight Total", "value": f"{baseline.get('target_weight_total')}%", "tone": "neutral"},
                {"label": "Review Cadence", "value": selected_row.get("review_cadence") or "-", "tone": "neutral"},
            ]
        )
        component_df = _build_paper_portfolio_ledger_component_rows(selected_row)
        if component_df.empty:
            st.info("이 ledger에는 target component가 없습니다.")
        else:
            st.dataframe(component_df, width="stretch", hide_index=True)
        with st.expander("Paper Ledger detail", expanded=False):
            st.markdown("###### Review Triggers")
            for trigger in list(selected_row.get("review_triggers") or []):
                st.info(str(trigger))
            st.json(selected_row)


# Render saved proposal monitoring, feedback, and raw JSON as one support area below the main flow.
def _render_saved_proposal_details(
    proposal_rows: list[dict[str, Any]],
    pre_live_rows: list[dict[str, Any]],
    current_rows: list[dict[str, Any]],
    paper_ledger_rows: list[dict[str, Any]],
) -> None:
    with st.container(border=True):
        st.markdown("#### 4. 저장된 Portfolio Proposal 확인")
        st.caption("저장한 포트폴리오 초안은 여기서 Validation / Monitoring / Feedback 순서로 다시 확인합니다.")
        if not proposal_rows:
            st.info("아직 저장된 Portfolio Proposal이 없습니다.")
            st.caption(f"Path: {PORTFOLIO_PROPOSAL_REGISTRY_FILE}")
            return

        current_by_registry_id = _portfolio_proposal_current_candidate_by_registry_id(current_rows)
        pre_live_by_registry_id = _portfolio_proposal_pre_live_record_by_registry_id(pre_live_rows)
        validation_tab, overview_tab, pre_live_tab, paper_tab, json_tab = st.tabs(
            ["Validation Pack", "Monitoring", "Pre-Live Feedback", "Paper Tracking", "Raw JSON"]
        )
        labels = [_portfolio_proposal_selection_label(row) for row in proposal_rows]

        with validation_tab:
            st.caption("Phase 31 검증 surface입니다. 저장된 proposal이 Phase 32 robustness 검증으로 넘어갈 수 있는지 읽습니다.")
            st.dataframe(
                _build_portfolio_risk_validation_summary_rows(
                    proposal_rows,
                    current_by_registry_id,
                    pre_live_by_registry_id,
                ),
                width="stretch",
                hide_index=True,
            )
            selected_label = st.selectbox(
                "Review Validation Pack",
                options=labels,
                key="portfolio_proposal_validation_selected_record",
            )
            selected_row = proposal_rows[labels.index(selected_label)]
            validation_input = _build_portfolio_risk_validation_input_for_proposal(
                proposal_row=selected_row,
                current_by_registry_id=current_by_registry_id,
                pre_live_by_registry_id=pre_live_by_registry_id,
            )
            validation = _build_portfolio_risk_validation_result(validation_input)
            _render_portfolio_risk_validation_pack(
                validation,
                title="Portfolio Risk / Live Readiness Validation",
                paper_ledger_rows=paper_ledger_rows,
                source_is_persisted=True,
            )

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
        "7단계 Portfolio Proposal 작업 공간입니다. 단일 후보는 추가 저장 없이 Live Readiness 직행 가능 여부를 확인하고, "
        "여러 후보를 묶을 때만 목적 / 역할 / 비중이 있는 포트폴리오 초안을 저장합니다."
    )

    current_rows = _load_current_candidate_registry_latest()
    pre_live_rows = _load_pre_live_candidate_registry_latest()
    proposal_rows = load_portfolio_proposals()
    paper_ledger_rows = load_paper_portfolio_ledger()
    pre_live_status_by_registry_id = _portfolio_proposal_pre_live_status_by_registry_id(pre_live_rows)
    pre_live_record_by_registry_id = _portfolio_proposal_pre_live_record_by_registry_id(pre_live_rows)
    current_by_registry_id = _portfolio_proposal_current_candidate_by_registry_id(current_rows)

    pre_live_notice = st.session_state.get("portfolio_proposal_from_pre_live_notice")
    if pre_live_notice:
        st.info(pre_live_notice)
        st.session_state["portfolio_proposal_from_pre_live_notice"] = None
    save_notice = st.session_state.pop("portfolio_proposal_save_notice", None)
    if save_notice:
        st.success(str(save_notice))
    paper_ledger_notice = st.session_state.pop("paper_portfolio_ledger_save_notice", None)
    if paper_ledger_notice:
        st.success(str(paper_ledger_notice))

    render_status_card_grid(
        [
            {"title": "Current Candidates", "value": len(current_rows), "tone": "positive" if current_rows else "neutral"},
            {"title": "Pre-Live Records", "value": len(pre_live_rows), "tone": "positive" if pre_live_rows else "neutral"},
            {"title": "Saved Proposals", "value": len(proposal_rows), "tone": "positive" if proposal_rows else "neutral"},
            {"title": "Paper Ledgers", "value": len(paper_ledger_rows), "tone": "positive" if paper_ledger_rows else "neutral"},
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
                    "title": "진행 방식",
                    "detail": "단일 후보 직행 평가 또는 다중 후보 구성 초안",
                    "status": "선택 후 분기",
                    "tone": "warning",
                },
                {
                    "title": "Live Readiness 후보",
                    "detail": "다음 단계가 읽을 수 있는 후보 또는 proposal draft",
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
                            "value": "단일 후보 직행/초안 선택" if len(selected_rows) == 1 else "다중 후보 구성 초안",
                            "tone": "neutral",
                        },
                    ]
                )
            else:
                st.info("포트폴리오 제안 후보를 먼저 선택하세요.")

    proposal_mode = "construction_draft"
    if selected_rows:
        if len(selected_rows) == 1:
            mode_labels = {
                "direct_live_readiness": "단일 후보 직행 평가",
                "construction_draft": "포트폴리오 초안 작성",
            }
            proposal_mode = st.segmented_control(
                "진행 방식",
                options=list(mode_labels.keys()),
                default="direct_live_readiness",
                format_func=lambda value: mode_labels.get(str(value), str(value)),
                key="portfolio_proposal_mode",
            ) or "direct_live_readiness"
            if proposal_mode == "direct_live_readiness":
                st.success("단일 후보는 별도 proposal 저장 없이 Live Readiness 직행 가능 여부를 먼저 확인합니다.")
            else:
                st.info("이 후보를 목적 / 역할 / 비중이 있는 proposal draft로 명시 저장합니다.")
        else:
            proposal_mode = "construction_draft"
            st.info("2개 이상 후보를 선택했기 때문에 Portfolio Proposal은 비교가 아니라 역할 / 비중을 정하는 구성 초안으로 진행합니다.")
    else:
        st.info("후보를 선택하면 단일 후보 직행 평가 또는 포트폴리오 초안 작성 경로가 열립니다.")

    if proposal_mode == "direct_live_readiness" and len(selected_rows) == 1:
        selected_row = selected_rows[0]
        registry_id = str(selected_row.get("registry_id") or "")
        result = dict(selected_row.get("result") or {})
        pre_live_status = pre_live_status_by_registry_id.get(registry_id, "not_started")
        data_trust_status = _component_data_trust_status(selected_row)

        st.markdown("#### 2. 단일 후보 기본 구성")
        with st.container(border=True):
            render_stage_brief(
                purpose="이미 Candidate Review에서 후보 검토와 Pre-Live 운영 기록을 마친 단일 후보라면 새 proposal draft를 또 저장하지 않습니다.",
                result="Live Readiness direct candidate",
            )
            render_badge_strip(
                [
                    {"label": "Mode", "value": "Direct Live Readiness", "tone": "positive"},
                    {"label": "Role", "value": "core_anchor", "tone": "neutral"},
                    {"label": "Target Weight", "value": "100%", "tone": "neutral"},
                    {"label": "Capital Scope", "value": "paper_only", "tone": "neutral"},
                ]
            )
            with st.container(border=True):
                st.markdown(f"##### {selected_row.get('title') or registry_id}")
                render_badge_strip(
                    [
                        {"label": "Family", "value": selected_row.get("strategy_family") or "-", "tone": "neutral"},
                        {"label": "Candidate Role", "value": selected_row.get("candidate_role") or "-", "tone": "neutral"},
                        {
                            "label": "Pre-Live",
                            "value": pre_live_status,
                            "tone": "positive" if pre_live_status == "paper_tracking" else "warning",
                        },
                        {
                            "label": "Data Trust",
                            "value": data_trust_status,
                            "tone": "positive" if data_trust_status == "ok" else "warning",
                        },
                    ]
                )
                render_status_card_grid(
                    [
                        {"title": "CAGR", "value": result.get("cagr") or "-", "tone": "neutral"},
                        {"title": "MDD", "value": result.get("mdd") or "-", "tone": "neutral"},
                        {"title": "Promotion", "value": result.get("promotion") or "-", "tone": "positive"},
                        {"title": "Deployment", "value": result.get("deployment") or "-", "tone": "neutral"},
                    ]
                )

        st.markdown("#### 3. Live Readiness 직행 평가")
        with st.container(border=True):
            readiness = _build_portfolio_proposal_direct_readiness_evaluation(
                selected_row=selected_row,
                pre_live_status=pre_live_status,
                data_trust_status=data_trust_status,
            )
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
                    {"label": "Proposal Draft", "value": "저장 불필요", "tone": "positive"},
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
                st.success("이 후보는 proposal draft를 새로 저장하지 않고 이후 Live Readiness 검토로 넘길 수 있는 형태입니다.")
            else:
                st.warning("직행 전 보강 항목: " + ", ".join(str(item) for item in readiness["blocking_reasons"]))

            action_cols = st.columns(2, gap="small")
            with action_cols[0]:
                st.button(
                    "Open Live Readiness",
                    key="open_live_readiness_direct_placeholder",
                    disabled=True,
                    width="stretch",
                    help="Live Readiness 단계는 다음 작업에서 연결할 예정입니다.",
                )
            with action_cols[1]:
                st.caption("여러 후보를 하나의 포트폴리오로 묶을 때만 `포트폴리오 초안 작성` 경로를 사용합니다.")

            with st.expander("판단 기준", expanded=False):
                st.dataframe(pd.DataFrame(readiness["checks"]), width="stretch", hide_index=True)
                st.caption("이 평가는 저장 row를 새로 만들지 않고, 기존 current candidate / Pre-Live record를 다음 단계 입력으로 읽을 수 있는지만 봅니다.")

        st.markdown("#### 4. Portfolio Risk / Validation Pack")
        with st.container(border=True):
            validation_input = _build_portfolio_risk_validation_input_for_single_candidate(
                selected_row=selected_row,
                pre_live_record=pre_live_record_by_registry_id.get(registry_id),
                pre_live_status=pre_live_status,
                data_trust_status=data_trust_status,
            )
            validation = _build_portfolio_risk_validation_result(validation_input)
            _render_portfolio_risk_validation_pack(
                validation,
                title="단일 후보 Portfolio Risk / Live Readiness Validation",
                paper_ledger_rows=paper_ledger_rows,
                source_is_persisted=True,
            )
        _render_saved_paper_ledger_details(paper_ledger_rows)

    elif selected_rows:
        st.markdown("#### 2. 목적 / 역할 / 비중 설계")
        with st.container(border=True):
            render_stage_brief(
                purpose="두 개 이상 후보를 하나의 포트폴리오로 묶거나, 단일 후보라도 역할 / 비중 / 목적을 명시적으로 남기고 싶을 때 사용하는 작성 단계입니다.",
                result="Portfolio construction draft",
            )
            with st.expander("Proposal Role / Target Weight 사용법", expanded=False):
                st.markdown(
                    "- active weight가 있는 proposal에는 최소 1개 `core_anchor`가 필요합니다.\n"
                    "- `return_driver`, `diversifier`, `defensive_sleeve`, `satellite`은 중심 후보를 보완하는 역할입니다.\n"
                    "- `watch_only`는 관찰용 후보입니다. 저장 전에는 보통 weight를 0%로 둡니다.\n"
                    "- `Target Weight %` 합계가 100%가 아니면 proposal 저장 전 blocker가 됩니다."
                )
                st.dataframe(
                    pd.DataFrame(
                        [
                            {"Proposal Role": role, "사용 의미": PORTFOLIO_PROPOSAL_ROLE_DESCRIPTIONS.get(role, "-")}
                            for role in PORTFOLIO_PROPOSAL_ROLE_OPTIONS
                        ]
                    ),
                    width="stretch",
                    hide_index=True,
                )
            if st.session_state.pop("portfolio_proposal_reset_id_after_save", False):
                st.session_state.pop("portfolio_proposal_id", None)
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
                    help="이 묶음이 어떤 성격의 포트폴리오 초안인지 표시합니다.",
                )
            with objective_cols[3]:
                capital_scope = st.selectbox(
                    "Capital Scope",
                    options=["paper_only", "review_only", "small_trial_candidate"],
                    index=0,
                    key="portfolio_proposal_capital_scope",
                    help="이 초안이 실제 투자금이 아니라 어떤 검토 범위에서 읽혀야 하는지 표시합니다.",
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
                    help="여기서는 optimizer가 아니라 초기 검토용 비중 방식을 고릅니다.",
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
                    st.caption("이 카드는 후보 비교표가 아니라, 포트폴리오 안에서 맡길 역할과 초기 비중을 정하는 영역입니다.")
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
                            help="포트폴리오 안에서 후보가 맡는 역할입니다. active proposal에는 최소 1개 core_anchor가 필요합니다.",
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
                existing_proposal_ids={str(row.get("proposal_id") or "").strip() for row in proposal_rows},
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
                    st.error("저장 전 확인 필요")
                    for guidance in list(readiness.get("blocking_guidance") or readiness["blocking_reasons"]):
                        st.warning(str(guidance))

            with st.container(border=True):
                validation_input = _build_portfolio_risk_validation_input_for_proposal(
                    proposal_row=proposal_row,
                    current_by_registry_id=current_by_registry_id,
                    pre_live_by_registry_id=pre_live_record_by_registry_id,
                )
                validation = _build_portfolio_risk_validation_result(validation_input)
                _render_portfolio_risk_validation_pack(
                    validation,
                    title="작성 중 Proposal Portfolio Risk / Live Readiness Validation",
                    paper_ledger_rows=paper_ledger_rows,
                    source_is_persisted=False,
                )

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
                    st.session_state["portfolio_proposal_save_notice"] = (
                        f"Portfolio Proposal `{proposal_row['proposal_id']}`를 저장했습니다. "
                        "live approval은 아닙니다. 저장된 proposal은 아래 `4. 저장된 Portfolio Proposal 확인`에서 확인할 수 있습니다."
                    )
                    st.session_state["portfolio_proposal_reset_id_after_save"] = True
                    st.rerun()
            with action_cols[1]:
                st.button(
                    "Open Live Readiness",
                    key="open_live_readiness_placeholder",
                    disabled=True,
                    width="stretch",
                    help="Live Readiness 단계는 다음 작업에서 연결할 예정입니다.",
                )
            st.caption("`Open Live Readiness`는 다음 단계 개발 전까지 비활성화됩니다. 이 경로에서는 proposal draft 저장까지만 처리합니다.")

            with st.expander("상세 보기", expanded=False):
                criteria_tab, json_tab = st.tabs(["판단 기준", "Portfolio Proposal JSON"])
                with criteria_tab:
                    st.dataframe(pd.DataFrame(readiness["checks"]), width="stretch", hide_index=True)
                    if open_blockers:
                        st.warning("저장 blocker: " + ", ".join(open_blockers))
                with json_tab:
                    st.json(proposal_row)

        _render_saved_proposal_details(proposal_rows, pre_live_rows, current_rows, paper_ledger_rows)
        _render_saved_paper_ledger_details(paper_ledger_rows)
    else:
        st.markdown("#### 2. 진행 방식 선택")
        with st.container(border=True):
            render_stage_brief(
                purpose="Live Readiness로 이어갈 후보를 먼저 고르면, 단일 후보 직행 평가와 다중 후보 구성 초안 중 맞는 경로가 열립니다.",
                result="Candidate selection required",
            )
            st.info("`1. Proposal 후보 확인`에서 current candidate를 1개 이상 선택하세요.")
        _render_saved_paper_ledger_details(paper_ledger_rows)
