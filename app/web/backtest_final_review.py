from __future__ import annotations

from datetime import date
from typing import Any
from uuid import uuid4

import pandas as pd
import streamlit as st

from app.web.backtest_final_review_helpers import (
    FINAL_REVIEW_ROUTE_DESCRIPTIONS,
    FINAL_REVIEW_ROUTE_OPTIONS,
    _build_final_review_decision_evidence_pack,
    _build_final_review_decision_row,
    _build_final_review_decision_rows_for_display,
    _build_final_review_paper_observation_snapshot,
    _build_final_review_save_evaluation,
    _build_final_review_source_options,
    _build_final_review_validation,
)
from app.web.backtest_portfolio_proposal_helpers import (
    _build_final_selection_decision_component_rows,
    _paper_ledger_slug,
)
from app.web.backtest_ui_components import (
    render_artifact_pipeline,
    render_badge_strip,
    render_readiness_route_panel,
    render_stage_brief,
    render_status_card_grid,
)
from app.web.runtime import (
    FINAL_SELECTION_DECISION_REGISTRY_FILE,
    append_final_selection_decision,
    load_current_candidate_registry_latest,
    load_final_selection_decisions,
    load_portfolio_proposals,
    load_pre_live_candidate_registry_latest,
)


def _render_validation_summary(validation: dict[str, Any]) -> None:
    metrics = dict(validation.get("metrics") or {})
    route = str(validation.get("validation_route") or "-")
    render_readiness_route_panel(
        route_label=route,
        score=float(validation.get("validation_score") or 0.0),
        blockers_count=len(validation.get("hard_blockers") or []),
        verdict=str(validation.get("verdict") or "-"),
        next_action=str(validation.get("next_action") or "-"),
        route_title="Portfolio Validation",
        score_title="Validation Score",
    )
    render_badge_strip(
        [
            {"label": "Source", "value": validation.get("source_type") or "-", "tone": "neutral"},
            {"label": "Components", "value": metrics.get("active_components", 0), "tone": "neutral"},
            {"label": "Weight Total", "value": f"{metrics.get('weight_total', 0)}%", "tone": "neutral"},
            {"label": "Max Weight", "value": f"{metrics.get('max_weight', 0)}%", "tone": "neutral"},
        ]
    )
    component_df = pd.DataFrame(validation.get("component_rows") or [])
    if component_df.empty:
        st.info("최종 검토에 연결된 component가 없습니다.")
    else:
        st.dataframe(component_df, width="stretch", hide_index=True)
    gap_cols = st.columns(3, gap="small")
    with gap_cols[0]:
        st.markdown("###### Hard Blockers")
        if validation.get("hard_blockers"):
            for blocker in list(validation.get("hard_blockers") or []):
                st.error(str(blocker))
        else:
            st.success("hard blocker 없음")
    with gap_cols[1]:
        st.markdown("###### Paper / Observation Gaps")
        if validation.get("paper_tracking_gaps"):
            for gap in list(validation.get("paper_tracking_gaps") or []):
                st.warning(str(gap))
        else:
            st.success("관찰 gap 없음")
    with gap_cols[2]:
        st.markdown("###### Review Gaps")
        if validation.get("review_gaps"):
            for gap in list(validation.get("review_gaps") or []):
                st.info(str(gap))
        else:
            st.success("review gap 없음")


def _render_robustness_summary(validation: dict[str, Any]) -> None:
    robustness = dict(validation.get("robustness_validation") or {})
    if not robustness:
        st.info("Robustness / Stress preview가 없습니다.")
        return
    route = str(robustness.get("robustness_route") or "-")
    render_readiness_route_panel(
        route_label=route,
        score=float(robustness.get("robustness_score") or 0.0),
        blockers_count=len(robustness.get("blockers") or []),
        verdict=str(robustness.get("verdict") or "-"),
        next_action=str(robustness.get("next_action") or "-"),
        route_title="Robustness Preview",
        score_title="Robustness Score",
    )
    stress_df = pd.DataFrame(robustness.get("stress_summary_rows") or [])
    if stress_df.empty:
        st.info("Stress / Sensitivity summary가 없습니다.")
    else:
        st.dataframe(stress_df, width="stretch", hide_index=True)
        st.caption("`Result Status = NOT_RUN`은 stress runner 실행 결과가 아니라, 최종 검토 전에 확인할 검증 질문입니다.")


def _render_paper_observation_summary(paper_observation: dict[str, Any]) -> None:
    baseline = dict(paper_observation.get("baseline_snapshot") or {})
    render_badge_strip(
        [
            {"label": "Mode", "value": "Inline Observation", "tone": "neutral"},
            {"label": "Route", "value": paper_observation.get("route") or "-", "tone": "positive" if paper_observation.get("route") == "PAPER_OBSERVATION_READY" else "warning"},
            {"label": "Components", "value": baseline.get("active_component_count", 0), "tone": "neutral"},
            {"label": "Weight Total", "value": f"{baseline.get('target_weight_total', 0)}%", "tone": "neutral"},
            {"label": "Benchmark", "value": paper_observation.get("tracking_benchmark") or "-", "tone": "neutral"},
        ]
    )
    st.dataframe(pd.DataFrame(paper_observation.get("checks") or []), width="stretch", hide_index=True)
    trigger_cols = st.columns(2, gap="small")
    with trigger_cols[0]:
        st.markdown("###### 관찰 기준")
        st.write(
            {
                "review_cadence": paper_observation.get("review_cadence"),
                "tracking_benchmark": paper_observation.get("tracking_benchmark"),
            }
        )
    with trigger_cols[1]:
        st.markdown("###### 재검토 trigger")
        for trigger in list(paper_observation.get("review_triggers") or []):
            st.info(str(trigger))


def _render_saved_final_review_decisions(final_decision_rows: list[dict[str, Any]]) -> None:
    if not final_decision_rows:
        st.info("아직 기록된 최종 검토 결과가 없습니다.")
        st.caption(f"Path: {FINAL_SELECTION_DECISION_REGISTRY_FILE}")
        return

    st.dataframe(_build_final_review_decision_rows_for_display(final_decision_rows), width="stretch", hide_index=True)
    labels = [
        f"{row.get('updated_at') or row.get('created_at')} | {row.get('decision_route')} | {row.get('decision_id')}"
        for row in final_decision_rows
    ]
    selected_label = st.selectbox("기록 확인", options=labels, key="final_review_saved_decision_selected")
    selected_row = final_decision_rows[labels.index(selected_label)]
    evidence = dict(selected_row.get("decision_evidence_snapshot") or {})
    handoff = dict(selected_row.get("phase35_handoff") or {})
    render_readiness_route_panel(
        route_label=str(handoff.get("handoff_route") or "-"),
        score=float(evidence.get("score") or 0.0),
        blockers_count=len(evidence.get("blockers") or []),
        verdict=str(handoff.get("verdict") or "-"),
        next_action=str(handoff.get("next_action") or "-"),
        route_title="Phase 35 Handoff",
        score_title="Evidence Score",
    )
    render_badge_strip(
        [
            {"label": "Decision", "value": selected_row.get("decision_route") or "-", "tone": "positive" if selected_row.get("decision_route") == "SELECT_FOR_PRACTICAL_PORTFOLIO" else "warning"},
            {"label": "Source", "value": f"{selected_row.get('source_type')} / {selected_row.get('source_id')}", "tone": "neutral"},
            {"label": "Observation", "value": selected_row.get("source_observation_id") or selected_row.get("source_paper_ledger_id") or "-", "tone": "neutral"},
            {"label": "Live Approval", "value": "Disabled", "tone": "neutral"},
            {"label": "Order", "value": "Disabled", "tone": "neutral"},
        ]
    )
    component_df = _build_final_selection_decision_component_rows(selected_row)
    if component_df.empty:
        st.info("이 기록에는 selected component가 없습니다.")
    else:
        st.dataframe(component_df, width="stretch", hide_index=True)
    with st.expander("최종 검토 결과 JSON", expanded=False):
        st.json(selected_row)


def render_final_review_workspace() -> None:
    st.markdown("### Final Review")
    st.caption(
        "최종 실전 후보로 선정할지 판단하는 공간입니다. Proposal 작성과 분리해서 Validation, Robustness, "
        "Paper Observation 기준, 최종 판단을 한 화면에서 확인합니다."
    )

    current_rows = load_current_candidate_registry_latest()
    proposal_rows = load_portfolio_proposals()
    pre_live_rows = load_pre_live_candidate_registry_latest()
    final_decision_rows = load_final_selection_decisions()

    final_notice = st.session_state.pop("final_review_decision_notice", None)
    if final_notice:
        st.success(str(final_notice))

    render_status_card_grid(
        [
            {"title": "Current Candidates", "value": len(current_rows), "tone": "positive" if current_rows else "neutral"},
            {"title": "Saved Proposals", "value": len(proposal_rows), "tone": "positive" if proposal_rows else "neutral"},
            {"title": "Final Review Records", "value": len(final_decision_rows), "tone": "positive" if final_decision_rows else "neutral"},
            {"title": "Paper Ledger Save", "value": "Not Required", "detail": "관찰 기준은 최종 검토 기록 안에 포함합니다.", "tone": "neutral"},
            {"title": "Live Approval", "value": "Disabled", "detail": "이 화면은 승인/주문이 아닙니다.", "tone": "neutral"},
        ]
    )

    with st.container(border=True):
        st.markdown("#### 최종 검토 흐름")
        render_artifact_pipeline(
            [
                {"title": "검토 대상", "detail": "단일 후보 또는 저장된 proposal", "status": "선택", "tone": "neutral"},
                {"title": "검증 근거", "detail": "Validation / Robustness / Stress", "status": "자동 계산", "tone": "neutral"},
                {"title": "관찰 기준", "detail": "별도 ledger 저장 없이 최종 기록에 포함", "status": "Inline", "tone": "positive"},
                {"title": "최종 판단", "detail": "선정 / 보류 / 거절 / 재검토", "status": "명시 기록", "tone": "warning"},
            ]
        )

    source_options = _build_final_review_source_options(current_rows, proposal_rows)
    if not source_options:
        st.info("최종 검토할 current candidate 또는 saved proposal이 없습니다.")
        return

    st.divider()
    st.markdown("#### 1. 최종 검토 대상 선택")
    with st.container(border=True):
        render_stage_brief(
            purpose="Proposal 작성 탭에서 만든 포트폴리오 초안 또는 단일 후보를 최종 검토 대상으로 고릅니다.",
            result="Final review source",
        )
        labels = [str(option["label"]) for option in source_options]
        selected_label = st.selectbox("검토 대상", options=labels, key="final_review_source_selected")
        source = source_options[labels.index(selected_label)]
        render_badge_strip(
            [
                {"label": "Source Type", "value": source.get("source_type") or "-", "tone": "neutral"},
                {"label": "Source ID", "value": source.get("source_id") or "-", "tone": "neutral"},
            ]
        )

    validation = _build_final_review_validation(source, current_rows=current_rows, pre_live_rows=pre_live_rows)
    paper_observation = _build_final_review_paper_observation_snapshot(validation)
    evidence = _build_final_review_decision_evidence_pack(validation, paper_observation)

    st.markdown("#### 2. 검증 근거 확인")
    with st.container(border=True):
        _render_validation_summary(validation)

    st.markdown("#### 3. Robustness / Stress 질문 확인")
    with st.container(border=True):
        _render_robustness_summary(validation)

    st.markdown("#### 4. Paper Observation 기준 확인")
    with st.container(border=True):
        render_stage_brief(
            purpose="별도 Paper Ledger를 또 저장하지 않고, 최종 검토 기록 안에 관찰 기준을 함께 남깁니다.",
            result="Inline paper observation criteria",
        )
        _render_paper_observation_summary(paper_observation)

    st.markdown("#### 5. 최종 판단 및 테스트 검증")
    with st.container(border=True):
        render_readiness_route_panel(
            route_label=str(evidence.get("route") or "-"),
            score=float(evidence.get("score") or 0.0),
            blockers_count=len(evidence.get("blockers") or []),
            verdict=str(evidence.get("verdict") or "-"),
            next_action=str(evidence.get("next_action") or "-"),
            route_title="Final Review Route",
            score_title="Evidence Score",
        )
        if evidence.get("blockers"):
            for blocker in list(evidence.get("blockers") or []):
                st.warning(str(blocker))
        st.dataframe(pd.DataFrame(evidence.get("checks") or []), width="stretch", hide_index=True)

        existing_decision_ids = {
            str(row.get("decision_id") or "").strip()
            for row in final_decision_rows
            if str(row.get("decision_id") or "").strip()
        }
        if st.session_state.pop("final_review_reset_decision_id_after_save", False):
            st.session_state.pop("final_review_decision_id", None)
        source_slug = _paper_ledger_slug(source.get("source_id"))
        default_decision_id = f"final_{source_slug}_{date.today().strftime('%Y%m%d')}_{uuid4().hex[:6]}"
        suggested_route = str(evidence.get("suggested_decision_route") or FINAL_REVIEW_ROUTE_OPTIONS[0])
        suggested_index = FINAL_REVIEW_ROUTE_OPTIONS.index(suggested_route) if suggested_route in FINAL_REVIEW_ROUTE_OPTIONS else 0

        input_cols = st.columns([0.36, 0.34, 0.30], gap="small")
        with input_cols[0]:
            decision_id = st.text_input("Decision ID", value=default_decision_id, key="final_review_decision_id")
        with input_cols[1]:
            decision_route = st.selectbox(
                "최종 판단",
                options=FINAL_REVIEW_ROUTE_OPTIONS,
                index=suggested_index,
                key="final_review_decision_route",
            )
        with input_cols[2]:
            st.text_input("Source", value=str(source.get("source_id") or "-"), disabled=True, key="final_review_source_display")
        st.caption(FINAL_REVIEW_ROUTE_DESCRIPTIONS.get(str(decision_route), "-"))
        operator_reason = st.text_area(
            "판단 사유",
            value="검증 근거와 관찰 기준을 함께 보고 최종 실전 후보 여부를 판단한다.",
            key="final_review_operator_reason",
        )
        operator_constraints = st.text_area(
            "운영 제약",
            value="실제 투자 전 Phase 35에서 투입 금액, 리밸런싱, 중단 / 재검토 기준을 별도로 확정한다.",
            key="final_review_operator_constraints",
        )
        operator_next_action = st.text_area(
            "다음 행동",
            value="선정이면 Phase 35 운영 가이드로 넘기고, 보류 / 재검토면 추가 관찰 또는 구성 근거를 보강한다.",
            key="final_review_operator_next_action",
        )
        save_evaluation = _build_final_review_save_evaluation(
            evidence=evidence,
            decision_id=decision_id,
            decision_route=str(decision_route),
            operator_reason=operator_reason,
            existing_decision_ids=existing_decision_ids,
        )
        render_readiness_route_panel(
            route_label=str(save_evaluation.get("route") or "-"),
            score=float(save_evaluation.get("score") or 0.0),
            blockers_count=len(save_evaluation.get("blockers") or []),
            verdict=str(save_evaluation.get("verdict") or "-"),
            next_action=str(save_evaluation.get("next_action") or "-"),
            route_title="Record Route",
            score_title="Record Score",
        )
        final_row = _build_final_review_decision_row(
            source=source,
            validation=validation,
            paper_observation=paper_observation,
            evidence=evidence,
            decision_id=decision_id,
            decision_route=str(decision_route),
            operator_reason=operator_reason,
            operator_constraints=operator_constraints,
            operator_next_action=operator_next_action,
        )
        action_cols = st.columns(2, gap="small")
        with action_cols[0]:
            if st.button(
                "최종 검토 결과 기록",
                key="final_review_record_decision",
                disabled=not bool(save_evaluation.get("can_save")),
                width="stretch",
            ):
                append_final_selection_decision(final_row)
                st.session_state["final_review_decision_notice"] = (
                    f"최종 검토 결과 `{final_row['decision_id']}`를 기록했습니다. "
                    "이 기록은 live approval이나 주문 지시가 아닙니다."
                )
                st.session_state["final_review_reset_decision_id_after_save"] = True
                st.rerun()
        with action_cols[1]:
            st.button(
                "Phase 35 운영 가이드 열기",
                key="final_review_open_phase35_placeholder",
                disabled=True,
                width="stretch",
                help="Phase 35에서 최종 선정 후보의 운영 가이드를 연결할 예정입니다.",
            )
        with st.expander("최종 검토 결과 Preview", expanded=False):
            st.json(final_row)
            st.caption(f"Path: {FINAL_SELECTION_DECISION_REGISTRY_FILE}")

    st.markdown("#### 6. 기록된 최종 검토 결과 확인")
    with st.container(border=True):
        _render_saved_final_review_decisions(final_decision_rows)
