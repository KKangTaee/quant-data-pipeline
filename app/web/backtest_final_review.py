from __future__ import annotations

from datetime import date
from typing import Any
from uuid import uuid4

import pandas as pd
import streamlit as st

from app.services.backtest_evidence_read_model import (
    build_decision_dossier,
    build_final_review_candidate_board,
    build_final_review_decision_cockpit,
)
from app.web.backtest_final_review_helpers import (
    FINAL_REVIEW_DECISION_LABELS,
    FINAL_REVIEW_ROUTE_DESCRIPTIONS,
    FINAL_REVIEW_ROUTE_OPTIONS,
    _build_investability_evidence_packet,
    _build_final_review_decision_evidence_pack,
    _build_final_review_decision_row,
    _build_final_review_decision_rows_for_display,
    _build_final_review_paper_observation_snapshot,
    _build_final_review_save_evaluation,
    _build_final_review_source_options,
    _build_final_review_status_display,
    _build_final_review_validation,
    _is_final_review_eligible_validation_result,
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
from app.runtime import (
    FINAL_SELECTION_DECISION_V2_FILE,
    append_final_selection_decision_v2,
    load_current_candidate_registry_latest,
    load_final_selection_decisions_v2,
    load_portfolio_proposals,
    load_pre_live_candidate_registry_latest,
    load_practical_validation_results,
)


def _status_tone(status: Any) -> str:
    status_text = str(status or "").upper()
    if status_text in {"PASS", "READY"}:
        return "positive"
    if status_text == "BLOCKED":
        return "danger"
    if status_text in {"REVIEW", "NEEDS_INPUT"}:
        return "warning"
    return "neutral"


def _provider_look_through_board(validation: dict[str, Any]) -> dict[str, Any]:
    board = dict(validation.get("provider_look_through_board") or {})
    if board:
        return board
    provider_context = dict(validation.get("provider_coverage") or {})
    return dict(provider_context.get("look_through_board") or {})


def _render_provider_look_through_summary(validation: dict[str, Any]) -> None:
    board = _provider_look_through_board(validation)
    if not board:
        return

    st.markdown("###### Look-through Exposure Board")
    render_badge_strip(
        [
            {"label": "Board", "value": board.get("status") or "-", "tone": _status_tone(board.get("status"))},
            {"label": "Holdings", "value": f"{board.get('holdings_coverage_weight', 0)}%", "tone": _status_tone(board.get("holdings_status"))},
            {"label": "Exposure", "value": f"{board.get('exposure_coverage_weight', 0)}%", "tone": _status_tone(board.get("exposure_status"))},
            {"label": "Top Holding", "value": f"{board.get('top_holding_weight', 0)}%", "tone": "warning" if (board.get("top_holding_weight") or 0) > 25 else "neutral"},
            {"label": "Dominant", "value": f"{board.get('dominant_asset_bucket') or '-'} {board.get('dominant_asset_weight', 0)}%", "tone": "neutral"},
            {"label": "Unknown", "value": f"{board.get('unknown_exposure_weight', 0)}%", "tone": "warning" if (board.get("unknown_exposure_weight") or 0) else "neutral"},
        ]
    )
    st.caption(str(board.get("summary") or "-"))
    summary_rows = list(board.get("summary_rows") or [])
    if summary_rows:
        st.dataframe(pd.DataFrame(summary_rows), width="stretch", hide_index=True)
    with st.expander("Look-through detail", expanded=False):
        detail_tabs = st.tabs(["Asset Buckets", "Top Holdings", "Fund Coverage"])
        with detail_tabs[0]:
            rows = list(board.get("asset_bucket_rows") or [])
            if rows:
                st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
            else:
                st.info("표시할 asset bucket row가 없습니다.")
        with detail_tabs[1]:
            rows = list(board.get("top_holding_rows") or [])
            if rows:
                st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
            else:
                st.info("표시할 top holdings row가 없습니다.")
        with detail_tabs[2]:
            rows = list(board.get("fund_coverage_rows") or [])
            if rows:
                st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
            else:
                st.info("표시할 ETF별 coverage row가 없습니다.")


def _robustness_lab_board(validation: dict[str, Any]) -> dict[str, Any]:
    robustness = dict(validation.get("robustness_validation") or {})
    return dict(robustness.get("robustness_lab_board") or validation.get("robustness_lab_board") or {})


def _render_robustness_lab_summary(board: dict[str, Any]) -> None:
    metrics = dict(board.get("metrics") or {})
    st.markdown("###### Robustness Lab")
    render_badge_strip(
        [
            {"label": "Board", "value": board.get("status") or "-", "tone": _status_tone(board.get("status"))},
            {
                "label": "Stress",
                "value": f"{metrics.get('computed_stress_windows', 0)}/{metrics.get('covered_stress_windows', 0)}",
                "tone": _status_tone(metrics.get("stress_status")),
            },
            {
                "label": "Sensitivity",
                "value": metrics.get("computed_sensitivity_checks", 0),
                "tone": _status_tone(metrics.get("sensitivity_status")),
            },
            {
                "label": "Follow-up",
                "value": metrics.get("runtime_followup_count", 0),
                "tone": "warning" if metrics.get("runtime_followup_count") else "neutral",
            },
            {"label": "Rolling", "value": metrics.get("rolling_window_count") or "-", "tone": _status_tone(metrics.get("rolling_status"))},
            {"label": "Trials", "value": metrics.get("local_trial_count", 0), "tone": _status_tone(metrics.get("overfit_status"))},
        ]
    )
    st.caption(str(board.get("summary") or "-"))
    summary_rows = list(board.get("summary_rows") or [])
    if summary_rows:
        st.dataframe(pd.DataFrame(summary_rows), width="stretch", hide_index=True)
    with st.expander("Robustness Lab detail", expanded=False):
        stress_tab, sensitivity_tab, follow_up_tab = st.tabs(["Stress", "Sensitivity", "Follow-up"])
        with stress_tab:
            stress_rows = list(board.get("stress_rows") or [])
            if stress_rows:
                st.dataframe(pd.DataFrame(stress_rows), width="stretch", hide_index=True)
            else:
                st.info("표시할 stress detail row가 없습니다.")
        with sensitivity_tab:
            sensitivity_rows = list(board.get("sensitivity_rows") or [])
            if sensitivity_rows:
                st.dataframe(pd.DataFrame(sensitivity_rows), width="stretch", hide_index=True)
            else:
                st.info("표시할 sensitivity detail row가 없습니다.")
        with follow_up_tab:
            follow_up_rows = list(board.get("follow_up_rows") or [])
            if follow_up_rows:
                st.dataframe(pd.DataFrame(follow_up_rows), width="stretch", hide_index=True)
            else:
                st.success("즉시 follow-up으로 남은 robustness row가 없습니다.")
    limitations = list(board.get("limitations") or [])
    if limitations:
        st.caption("Limitations: " + " / ".join(str(item) for item in limitations))


def _render_validation_efficacy_summary(validation: dict[str, Any]) -> None:
    audit = dict(validation.get("validation_efficacy_audit") or {})
    rows = list(validation.get("validation_efficacy_display_rows") or audit.get("rows") or [])
    if not rows:
        return
    metrics = dict(audit.get("metrics") or {})
    st.markdown("###### Validation Efficacy")
    render_badge_strip(
        [
            {
                "label": "Route",
                "value": audit.get("route_label") or audit.get("route") or "-",
                "tone": _status_tone(audit.get("overall_status")),
            },
            {"label": "PASS", "value": metrics.get("pass", 0), "tone": "positive"},
            {"label": "REVIEW", "value": metrics.get("review", 0), "tone": "warning"},
            {"label": "NEEDS_INPUT", "value": metrics.get("needs_input", 0), "tone": "warning"},
            {"label": "BLOCKED", "value": metrics.get("blocked", 0), "tone": "danger"},
        ]
    )
    with st.expander("Validation efficacy rows", expanded=False):
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
        if audit.get("next_action"):
            st.caption(str(audit.get("next_action")))


def _render_backtest_realism_summary(validation: dict[str, Any]) -> None:
    audit = dict(validation.get("backtest_realism_audit") or {})
    rows = list(validation.get("backtest_realism_display_rows") or audit.get("rows") or [])
    if not rows:
        return
    metrics = dict(audit.get("metrics") or {})
    st.markdown("###### Backtest Realism")
    render_badge_strip(
        [
            {
                "label": "Route",
                "value": audit.get("route_label") or audit.get("route") or "-",
                "tone": _status_tone(audit.get("overall_status")),
            },
            {"label": "PASS", "value": metrics.get("pass", 0), "tone": "positive"},
            {"label": "REVIEW", "value": metrics.get("review", 0), "tone": "warning"},
            {"label": "NEEDS_INPUT", "value": metrics.get("needs_input", 0), "tone": "warning"},
            {"label": "BLOCKED", "value": metrics.get("blocked", 0), "tone": "danger"},
        ]
    )
    with st.expander("Backtest realism rows", expanded=False):
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
        if audit.get("next_action"):
            st.caption(str(audit.get("next_action")))


def _render_data_coverage_summary(validation: dict[str, Any]) -> None:
    audit = dict(validation.get("data_coverage_audit") or {})
    rows = list(validation.get("data_coverage_display_rows") or audit.get("rows") or [])
    if not rows:
        return
    metrics = dict(audit.get("metrics") or {})
    st.markdown("###### Data Coverage")
    render_badge_strip(
        [
            {
                "label": "Route",
                "value": audit.get("route_label") or audit.get("route") or "-",
                "tone": _status_tone(audit.get("overall_status")),
            },
            {"label": "PASS", "value": metrics.get("pass", 0), "tone": "positive"},
            {"label": "REVIEW", "value": metrics.get("review", 0), "tone": "warning"},
            {"label": "NEEDS_INPUT", "value": metrics.get("needs_input", 0), "tone": "warning"},
            {"label": "Symbols", "value": metrics.get("symbol_count", 0), "tone": "neutral"},
        ]
    )
    with st.expander("Data coverage rows", expanded=False):
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
        if audit.get("next_action"):
            st.caption(str(audit.get("next_action")))


def _render_construction_risk_summary(validation: dict[str, Any]) -> None:
    audit = dict(validation.get("construction_risk_audit") or {})
    rows = list(validation.get("construction_risk_display_rows") or audit.get("rows") or [])
    if not rows:
        return
    metrics = dict(audit.get("metrics") or {})
    st.markdown("###### Construction Risk")
    render_badge_strip(
        [
            {
                "label": "Route",
                "value": audit.get("route_label") or audit.get("route") or "-",
                "tone": _status_tone(audit.get("overall_status")),
            },
            {"label": "Source", "value": audit.get("source_strength") or "-", "tone": "neutral"},
            {"label": "PASS", "value": metrics.get("pass", 0), "tone": "positive"},
            {"label": "REVIEW", "value": metrics.get("review", 0), "tone": "warning"},
            {"label": "NEEDS_INPUT", "value": metrics.get("needs_input", 0), "tone": "warning"},
            {"label": "BLOCKED", "value": metrics.get("blocked", 0), "tone": "danger"},
        ]
    )
    with st.expander("Construction risk rows", expanded=False):
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
        if audit.get("next_action"):
            st.caption(str(audit.get("next_action")))


def _render_risk_contribution_summary(validation: dict[str, Any]) -> None:
    audit = dict(validation.get("risk_contribution_audit") or {})
    rows = list(validation.get("risk_contribution_display_rows") or audit.get("rows") or [])
    if not rows:
        return
    metrics = dict(audit.get("metrics") or {})
    st.markdown("###### Risk Contribution")
    render_badge_strip(
        [
            {
                "label": "Route",
                "value": audit.get("route_label") or audit.get("route") or "-",
                "tone": _status_tone(audit.get("overall_status")),
            },
            {"label": "Source", "value": audit.get("source_strength") or "-", "tone": "neutral"},
            {"label": "PASS", "value": metrics.get("pass", 0), "tone": "positive"},
            {"label": "REVIEW", "value": metrics.get("review", 0), "tone": "warning"},
            {"label": "NEEDS_INPUT", "value": metrics.get("needs_input", 0), "tone": "warning"},
            {"label": "BLOCKED", "value": metrics.get("blocked", 0), "tone": "danger"},
        ]
    )
    with st.expander("Risk contribution rows", expanded=False):
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
        component_rows = list(audit.get("component_rows") or [])
        if component_rows:
            st.markdown("Component proxy rows")
            st.dataframe(pd.DataFrame(component_rows), width="stretch", hide_index=True)
        if audit.get("next_action"):
            st.caption(str(audit.get("next_action")))


def _render_component_role_weight_summary(validation: dict[str, Any]) -> None:
    audit = dict(validation.get("component_role_weight_audit") or {})
    rows = list(validation.get("component_role_weight_display_rows") or audit.get("rows") or [])
    if not rows:
        return
    metrics = dict(audit.get("metrics") or {})
    st.markdown("###### Component Role / Weight")
    render_badge_strip(
        [
            {
                "label": "Route",
                "value": audit.get("route_label") or audit.get("route") or "-",
                "tone": _status_tone(audit.get("overall_status")),
            },
            {"label": "Source", "value": audit.get("source_strength") or "-", "tone": "neutral"},
            {"label": "PASS", "value": metrics.get("pass", 0), "tone": "positive"},
            {"label": "REVIEW", "value": metrics.get("review", 0), "tone": "warning"},
            {"label": "NEEDS_INPUT", "value": metrics.get("needs_input", 0), "tone": "warning"},
            {"label": "BLOCKED", "value": metrics.get("blocked", 0), "tone": "danger"},
        ]
    )
    with st.expander("Component role / weight rows", expanded=False):
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
        component_rows = list(audit.get("component_rows") or [])
        if component_rows:
            st.markdown("Component role source rows")
            st.dataframe(pd.DataFrame(component_rows), width="stretch", hide_index=True)
        if audit.get("next_action"):
            st.caption(str(audit.get("next_action")))


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
    _render_validation_efficacy_summary(validation)
    _render_data_coverage_summary(validation)
    _render_construction_risk_summary(validation)
    _render_risk_contribution_summary(validation)
    _render_component_role_weight_summary(validation)
    _render_backtest_realism_summary(validation)
    diagnostic_rows = list(validation.get("diagnostic_display_rows") or [])
    if diagnostic_rows:
        st.markdown("###### Practical Diagnostics")
        profile = dict(validation.get("validation_profile") or {})
        status_counts = dict(dict(validation.get("diagnostic_summary") or {}).get("status_counts") or {})
        render_badge_strip(
            [
                {"label": "Profile", "value": profile.get("profile_label") or "-", "tone": "neutral"},
                {"label": "PASS", "value": status_counts.get("PASS", 0), "tone": "positive"},
                {"label": "REVIEW", "value": status_counts.get("REVIEW", 0), "tone": "warning"},
                {"label": "BLOCKED", "value": status_counts.get("BLOCKED", 0), "tone": "danger"},
                {"label": "NOT_RUN", "value": status_counts.get("NOT_RUN", 0), "tone": "neutral"},
            ]
        )
        st.dataframe(pd.DataFrame(diagnostic_rows), width="stretch", hide_index=True)
        provider_rows = list(validation.get("provider_coverage_display_rows") or [])
        if provider_rows:
            st.markdown("###### Provider Coverage")
            st.dataframe(pd.DataFrame(provider_rows), width="stretch", hide_index=True)
            _render_provider_look_through_summary(validation)
        not_run_critical = list(validation.get("not_run_critical_domains") or [])
        if not_run_critical:
            st.caption("NOT_RUN 항목은 선택을 자동 차단하지 않지만, 최종 판단 사유에서 확인해야 합니다.")
            st.dataframe(pd.DataFrame(not_run_critical), width="stretch", hide_index=True)
        profile_score_rows = list(validation.get("profile_score_rows") or [])
        if profile_score_rows:
            with st.expander("Profile-aware score breakdown", expanded=False):
                st.dataframe(pd.DataFrame(profile_score_rows), width="stretch", hide_index=True)
        curve_evidence = dict(validation.get("curve_evidence") or {})
        if curve_evidence:
            with st.expander("Curve / Replay evidence", expanded=False):
                render_badge_strip(
                    [
                        {"label": "Portfolio Curve", "value": curve_evidence.get("portfolio_curve_source") or "-", "tone": "neutral"},
                        {"label": "Rows", "value": curve_evidence.get("portfolio_curve_rows", 0), "tone": "neutral"},
                        {"label": "Benchmark", "value": curve_evidence.get("benchmark_ticker") or "-", "tone": "neutral"},
                        {"label": "Benchmark Rows", "value": curve_evidence.get("benchmark_curve_rows", 0), "tone": "neutral"},
                    ]
                )
                component_curve_rows = list(curve_evidence.get("component_curve_rows") or [])
                if component_curve_rows:
                    st.dataframe(pd.DataFrame(component_curve_rows), width="stretch", hide_index=True)
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
    board = _robustness_lab_board(validation)
    if board:
        _render_robustness_lab_summary(board)
        return

    stress_interpretation = dict(robustness.get("stress_interpretation") or validation.get("stress_interpretation") or {})
    sensitivity_interpretation = dict(
        robustness.get("sensitivity_interpretation") or validation.get("sensitivity_interpretation") or {}
    )
    if stress_interpretation or sensitivity_interpretation:
        st.markdown("###### Stress / Sensitivity Interpretation")
        interpretation_tabs = st.tabs(["Stress", "Sensitivity"])
        with interpretation_tabs[0]:
            render_badge_strip(
                [
                    {"label": "Status", "value": stress_interpretation.get("status") or "-", "tone": _status_tone(stress_interpretation.get("status"))},
                    {"label": "Computed", "value": f"{stress_interpretation.get('computed_count', 0)}/{stress_interpretation.get('covered_count', 0)}", "tone": "neutral"},
                    {"label": "Uncomputed", "value": stress_interpretation.get("uncomputed_count", 0), "tone": "warning" if stress_interpretation.get("uncomputed_count") else "neutral"},
                ]
            )
            st.caption(str(stress_interpretation.get("summary") or "-"))
            stress_rows = list(stress_interpretation.get("rows") or [])
            if stress_rows:
                st.dataframe(pd.DataFrame(stress_rows), width="stretch", hide_index=True)
        with interpretation_tabs[1]:
            render_badge_strip(
                [
                    {"label": "Status", "value": sensitivity_interpretation.get("status") or "-", "tone": _status_tone(sensitivity_interpretation.get("status"))},
                    {"label": "Computed", "value": sensitivity_interpretation.get("computed_count", 0), "tone": "neutral"},
                    {"label": "Review", "value": sensitivity_interpretation.get("review_count", 0), "tone": "warning" if sensitivity_interpretation.get("review_count") else "neutral"},
                    {"label": "Runtime Follow-up", "value": sensitivity_interpretation.get("runtime_followup_count", 0), "tone": "warning" if sensitivity_interpretation.get("runtime_followup_count") else "neutral"},
                ]
            )
            st.caption(str(sensitivity_interpretation.get("summary") or "-"))
            sensitivity_rows = list(sensitivity_interpretation.get("rows") or [])
            if sensitivity_rows:
                st.dataframe(pd.DataFrame(sensitivity_rows), width="stretch", hide_index=True)
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


def _render_investability_packet(packet: dict[str, Any]) -> None:
    summary = dict(packet.get("summary") or {})
    source_chain = dict(packet.get("source_chain") or {})
    gate_policy = dict(packet.get("gate_policy_snapshot") or {})
    policy_blocker_count = len(gate_policy.get("blockers") or []) + len(gate_policy.get("review_required") or [])
    route = str(packet.get("route") or "-")
    render_readiness_route_panel(
        route_label=route,
        score=float(packet.get("score") or 0.0),
        blockers_count=policy_blocker_count or len(packet.get("critical_gaps") or []),
        verdict=str(packet.get("verdict") or "-"),
        next_action=str(packet.get("next_action") or "-"),
        route_title="Investability Packet",
        score_title="Packet Score",
    )
    render_badge_strip(
        [
            {"label": "Source", "value": source_chain.get("selection_source_id") or source_chain.get("source_id") or "-", "tone": "neutral"},
            {"label": "Validation", "value": source_chain.get("validation_id") or "-", "tone": "neutral"},
            {"label": "PASS", "value": summary.get("pass", 0), "tone": "positive"},
            {"label": "REVIEW", "value": summary.get("review", 0), "tone": "warning"},
            {"label": "BLOCKED", "value": summary.get("blocked", 0), "tone": "danger"},
            {"label": "NOT_RUN", "value": summary.get("not_run", 0), "tone": "neutral"},
            {"label": "Gate", "value": gate_policy.get("outcome") or "-", "tone": "positive" if gate_policy.get("select_allowed") else "warning"},
            {"label": "Live Approval", "value": "Disabled", "tone": "neutral"},
        ]
    )
    st.caption("이 packet은 새 저장소가 아니라 Final Review에서 기존 validation evidence를 읽는 compact 판단 근거입니다.")
    st.dataframe(pd.DataFrame(packet.get("checks") or []), width="stretch", hide_index=True)
    policy_rows = list(gate_policy.get("policy_rows") or [])
    if policy_rows:
        st.markdown("###### Validation Gate Policy")
        st.caption("profile-aware gate matrix입니다. `Selected Route = Blocked`이면 선정 대신 보류 / 재검토로 기록합니다.")
        st.dataframe(pd.DataFrame(policy_rows), width="stretch", hide_index=True)
        if gate_policy.get("blockers"):
            for blocker in list(gate_policy.get("blockers") or []):
                st.error(str(blocker))
        if gate_policy.get("review_required"):
            for item in list(gate_policy.get("review_required") or []):
                st.warning(str(item))
    critical_gaps = list(packet.get("critical_gaps") or [])
    if critical_gaps:
        st.markdown("###### Critical Gaps")
        st.dataframe(pd.DataFrame(critical_gaps), width="stretch", hide_index=True)
    else:
        if gate_policy.get("blockers") or gate_policy.get("review_required"):
            st.info("packet critical gap은 없지만 gate policy상 선정 전 보강 항목이 있습니다.")
        else:
            st.success("critical gap 없음")
    with st.expander("Assumptions & Limits", expanded=False):
        st.dataframe(pd.DataFrame(packet.get("assumptions_and_limits") or []), width="stretch", hide_index=True)


def _cockpit_tone(state: Any) -> str:
    state_text = str(state or "").upper()
    if state_text == "SELECT_READY":
        return "positive"
    if state_text == "SELECT_BLOCKED":
        return "danger"
    return "warning"


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
                "source": source,
                "validation": validation,
                "paper_observation": paper_observation,
                "decision_evidence": evidence,
                "investability_packet": investability_packet,
                "cockpit": cockpit,
            }
        )
    return contexts


def _render_candidate_board(candidate_contexts: list[dict[str, Any]]) -> None:
    board = build_final_review_candidate_board(candidate_contexts)
    rows = list(board.get("rows") or [])
    if not rows:
        st.info("표시할 Final Review 후보가 없습니다.")
        return
    summary = dict(board.get("summary") or {})
    render_status_card_grid(
        [
            {
                "title": "Review Queue",
                "value": summary.get("total_candidates", 0),
                "detail": "Final Review Gate 통과 후보",
                "tone": "positive" if summary.get("total_candidates") else "neutral",
            },
            {
                "title": "Select Ready",
                "value": summary.get("select_ready", 0),
                "detail": "선정 기록 가능 후보",
                "tone": "positive" if summary.get("select_ready") else "neutral",
            },
            {
                "title": "Hold / Re-review",
                "value": summary.get("hold_or_re_review", 0),
                "detail": "보류 / 재검토 판단 필요",
                "tone": "warning" if summary.get("hold_or_re_review") else "neutral",
            },
            {
                "title": "Blocked",
                "value": summary.get("blocked", 0),
                "detail": "선정 전 차단 원인 있음",
                "tone": "danger" if summary.get("blocked") else "neutral",
            },
        ]
    )
    st.info(
        f"먼저 볼 후보: {summary.get('first_review_candidate') or '-'} / "
        f"{summary.get('first_review_action') or '-'}"
    )
    st.caption(str(summary.get("first_review_reason") or "-"))
    queue_rows = list(board.get("review_queue_rows") or [])
    if queue_rows:
        st.markdown("###### Review Queue")
        st.dataframe(pd.DataFrame(queue_rows), width="stretch", hide_index=True)
    with st.expander("Candidate Board detail", expanded=True):
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
    st.caption(
        "Candidate Board는 기존 Practical Validation result와 investability packet을 읽는 비교표입니다. "
        "Review Priority는 화면 정렬용 우선순위이며, 새 registry row를 만들거나 provider 데이터를 수집하지 않습니다."
    )


def _render_policy_row_list(rows: list[dict[str, Any]], *, empty_message: str, status: str) -> None:
    if not rows:
        st.success(empty_message)
        return
    for row in rows[:4]:
        label = str(row.get("Criteria") or row.get("Group") or "-")
        evidence = str(row.get("Required Action") or row.get("Current") or row.get("Evidence") or "-")
        if len(evidence) > 180:
            evidence = evidence[:177].rstrip() + "..."
        if status == "error":
            st.error(f"{label}: {evidence}")
        elif status == "warning":
            st.warning(f"{label}: {evidence}")
        else:
            st.info(f"{label}: {evidence}")
    if len(rows) > 4:
        st.caption(f"외 {len(rows) - 4}개 항목은 Gate Policy 상세에서 확인합니다.")


def _render_decision_cockpit(cockpit: dict[str, Any]) -> None:
    metrics = dict(cockpit.get("metrics") or {})
    handoff = dict(cockpit.get("monitoring_handoff") or {})
    source_chain = dict(cockpit.get("source_chain") or {})
    render_readiness_route_panel(
        route_label=str(cockpit.get("state_label") or "-"),
        score=float(cockpit.get("packet_score") or 0.0),
        blockers_count=int(metrics.get("policy_blockers", 0) or 0) + int(metrics.get("policy_review_required", 0) or 0),
        verdict=str(cockpit.get("verdict") or "-"),
        next_action=str(cockpit.get("next_action") or "-"),
        route_title="Decision Cockpit",
        score_title="Packet Score",
    )
    render_badge_strip(
        [
            {"label": "State", "value": cockpit.get("state_label") or "-", "tone": _cockpit_tone(cockpit.get("state"))},
            {"label": "Suggested", "value": cockpit.get("suggested_decision_label") or "-", "tone": _cockpit_tone(cockpit.get("state"))},
            {"label": "Gate", "value": cockpit.get("gate_outcome") or "-", "tone": "positive" if cockpit.get("select_allowed") else "warning"},
            {"label": "Blockers", "value": metrics.get("policy_blockers", 0), "tone": "danger" if metrics.get("policy_blockers") else "neutral"},
            {"label": "Review", "value": metrics.get("policy_review_required", 0), "tone": "warning" if metrics.get("policy_review_required") else "neutral"},
            {"label": "NOT_RUN", "value": metrics.get("not_run", 0), "tone": "warning" if metrics.get("not_run") else "neutral"},
            {"label": "Validation", "value": source_chain.get("validation_id") or "-", "tone": "neutral"},
            {"label": "Live Approval", "value": "Disabled", "tone": "neutral"},
        ]
    )
    cockpit_cols = st.columns(3, gap="small")
    with cockpit_cols[0]:
        st.markdown("###### Must Fix")
        _render_policy_row_list(
            list(cockpit.get("must_fix_rows") or []),
            empty_message="선정 차단 blocker 없음",
            status="error",
        )
    with cockpit_cols[1]:
        st.markdown("###### Must Review")
        _render_policy_row_list(
            list(cockpit.get("must_review_rows") or []),
            empty_message="선정 전 review-required 없음",
            status="warning",
        )
    with cockpit_cols[2]:
        st.markdown("###### Monitoring Seed")
        st.write(
            {
                "cadence": handoff.get("review_cadence") or "-",
                "benchmark": handoff.get("tracking_benchmark") or "-",
                "triggers": len(handoff.get("review_triggers") or []),
                "components": handoff.get("active_components", 0),
                "weight_total": handoff.get("target_weight_total"),
            }
        )
    if cockpit.get("watch_rows"):
        with st.expander("Watch-only policy rows", expanded=False):
            st.dataframe(pd.DataFrame(cockpit.get("watch_rows") or []), width="stretch", hide_index=True)


def _render_evidence_appendix(
    *,
    validation: dict[str, Any],
    paper_observation: dict[str, Any],
    investability_packet: dict[str, Any],
) -> None:
    render_stage_brief(
        purpose="이전 단계에서 이미 저장된 validation evidence를 필요할 때만 확인하는 부록입니다.",
        result="Read-only evidence appendix",
    )
    st.caption(
        "Evidence Appendix는 Practical Validation을 다시 실행하지 않습니다. "
        "현재 선택 후보의 저장된 validation result와 Final Review read model을 그대로 읽습니다."
    )
    appendix_tabs = st.tabs(
        [
            "Guide",
            "Practical Validation",
            "Robustness / Stress",
            "Paper Observation",
            "Investability Packet",
        ]
    )
    with appendix_tabs[0]:
        st.info(
            "최종 판단에 필요한 요약은 위 Decision Cockpit과 Final Decision Record에 있습니다. "
            "이 부록은 왜 그런 판단이 나왔는지 원본 근거를 추적할 때 확인합니다."
        )
        render_badge_strip(
            [
                {"label": "Validation Re-run", "value": "Disabled", "tone": "neutral"},
                {"label": "Provider Fetch", "value": "Disabled", "tone": "neutral"},
                {"label": "Registry Write", "value": "Disabled", "tone": "neutral"},
                {"label": "Live Approval", "value": "Disabled", "tone": "neutral"},
            ]
        )
    with appendix_tabs[1]:
        _render_validation_summary(validation)
    with appendix_tabs[2]:
        _render_robustness_summary(validation)
    with appendix_tabs[3]:
        render_stage_brief(
            purpose="별도 Paper Ledger를 또 저장하지 않고, 최종 검토 기록 안에 관찰 기준을 함께 남깁니다.",
            result="Inline paper observation criteria",
        )
        _render_paper_observation_summary(paper_observation)
    with appendix_tabs[4]:
        render_stage_brief(
            purpose="새 저장 기능을 늘리지 않고, 기존 검증 결과를 최종 판단용 compact packet으로 읽습니다.",
            result="Decision support packet",
        )
        _render_investability_packet(investability_packet)


def _render_decision_dossier_export(row: dict[str, Any], *, key_prefix: str) -> None:
    dossier = build_decision_dossier(row)
    decision = dict(dossier.get("decision") or {})
    metrics = dict(dossier.get("metrics") or {})
    boundary = dict(dossier.get("execution_boundary") or {})
    st.markdown("###### Decision Dossier")
    st.caption(
        "저장된 Final Review row를 사람이 읽는 markdown dossier로 묶습니다. "
        "이 export는 report 파일을 자동 저장하지 않습니다."
    )
    render_badge_strip(
        [
            {"label": "Schema", "value": dossier.get("schema_version"), "tone": "neutral"},
            {"label": "Decision", "value": decision.get("decision_label"), "tone": "neutral"},
            {"label": "Evidence", "value": metrics.get("evidence_check_count", 0), "tone": "neutral"},
            {
                "label": "Needs Review",
                "value": metrics.get("not_ready_evidence_check_count", 0),
                "tone": "warning" if metrics.get("not_ready_evidence_check_count") else "neutral",
            },
            {"label": "Auto Write", "value": "Disabled", "tone": "neutral"},
        ]
    )
    action_cols = st.columns([0.36, 0.64], gap="small")
    with action_cols[0]:
        st.download_button(
            "Markdown 다운로드",
            data=str(dossier.get("markdown") or ""),
            file_name=str(dossier.get("filename") or "decision_dossier.md"),
            mime="text/markdown",
            key=f"{key_prefix}_download",
            width="stretch",
        )
    with action_cols[1]:
        st.caption(
            f"Write policy: {boundary.get('write_policy') or '-'} / "
            f"report auto write: {boundary.get('report_auto_write')}"
        )
    with st.expander("Dossier preview", expanded=False):
        st.markdown(str(dossier.get("markdown") or "-"))


def _render_saved_final_review_decisions(final_decision_rows: list[dict[str, Any]]) -> None:
    if not final_decision_rows:
        st.info("아직 기록된 최종 검토 결과가 없습니다.")
        st.caption(f"Path: {FINAL_SELECTION_DECISION_V2_FILE}")
        return

    st.dataframe(_build_final_review_decision_rows_for_display(final_decision_rows), width="stretch", hide_index=True)
    labels = [
        f"{row.get('updated_at') or row.get('created_at')} | {row.get('decision_route')} | {row.get('decision_id')}"
        for row in final_decision_rows
    ]
    selected_label = st.selectbox("기록 확인", options=labels, key="final_review_saved_decision_selected")
    selected_row = final_decision_rows[labels.index(selected_label)]
    evidence = dict(selected_row.get("decision_evidence_snapshot") or {})
    status_display = _build_final_review_status_display(selected_row)
    render_readiness_route_panel(
        route_label=str(status_display.get("route") or "-"),
        score=float(evidence.get("score") or 0.0),
        blockers_count=len(evidence.get("blockers") or []),
        verdict=str(status_display.get("verdict") or "-"),
        next_action=str(status_display.get("next_action") or "-"),
        route_title="Final Review Status",
        score_title="Evidence Score",
    )
    decision_label = FINAL_REVIEW_DECISION_LABELS.get(str(selected_row.get("decision_route") or ""), "재검토 필요")
    render_badge_strip(
        [
            {"label": "Decision", "value": selected_row.get("decision_route") or "-", "tone": "positive" if selected_row.get("decision_route") == "SELECT_FOR_PRACTICAL_PORTFOLIO" else "warning"},
            {"label": "판단 라벨", "value": decision_label, "tone": "positive" if selected_row.get("decision_route") == "SELECT_FOR_PRACTICAL_PORTFOLIO" else "warning"},
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
    _render_decision_dossier_export(
        selected_row,
        key_prefix=f"final_review_dossier_{selected_row.get('decision_id') or 'saved'}",
    )
    packet = dict(selected_row.get("investability_evidence_packet") or {})
    if packet:
        with st.expander("Investability Evidence Packet", expanded=False):
            _render_investability_packet(packet)
    with st.expander("최종 검토 결과 JSON", expanded=False):
        st.json(selected_row)


def render_final_review_workspace() -> None:
    st.markdown("### Final Review")
    st.caption(
        "최종 실전 후보로 선정할지 판단하는 공간입니다. Candidate Board와 Decision Cockpit으로 판단 상태를 먼저 보고, "
        "최종 판단을 기록한 뒤 필요한 경우에만 이전 validation evidence 부록을 확인합니다. 검토 대상은 Practical Validation Gate를 통과한 후보만 표시합니다."
    )

    current_rows = load_current_candidate_registry_latest()
    proposal_rows = load_portfolio_proposals()
    pre_live_rows = load_pre_live_candidate_registry_latest()
    practical_validation_rows = load_practical_validation_results()
    eligible_practical_validation_rows = [
        row
        for row in practical_validation_rows
        if _is_final_review_eligible_validation_result(dict(row or {}))
    ]
    final_decision_rows = load_final_selection_decisions_v2()
    session_practical_source = st.session_state.pop("final_review_practical_validation_source", None)
    final_practical_notice = st.session_state.pop("final_review_practical_validation_notice", None)

    final_notice = st.session_state.pop("final_review_decision_notice", None)
    if final_practical_notice:
        st.success(str(final_practical_notice))
    if final_notice:
        st.success(str(final_notice))

    render_status_card_grid(
        [
            {
                "title": "Saved PV Records",
                "value": len(practical_validation_rows),
                "detail": "기록용 저장 포함",
                "tone": "positive" if practical_validation_rows else "neutral",
            },
            {
                "title": "Final Review Eligible",
                "value": f"{len(eligible_practical_validation_rows)} / {len(practical_validation_rows)}",
                "detail": "통과 / 전체 Practical Validation",
                "tone": "positive" if eligible_practical_validation_rows else "neutral",
            },
            {"title": "Final Review Records", "value": len(final_decision_rows), "tone": "positive" if final_decision_rows else "neutral"},
            {"title": "Paper Ledger Save", "value": "Not Required", "detail": "관찰 기준은 최종 검토 기록 안에 포함합니다.", "tone": "neutral"},
            {"title": "Live Approval", "value": "Disabled", "detail": "이 화면은 승인/주문이 아닙니다.", "tone": "neutral"},
        ]
    )
    hidden_validation_count = len(practical_validation_rows) - len(eligible_practical_validation_rows)
    if hidden_validation_count > 0:
        st.caption(
            f"Practical Validation 저장 기록 {hidden_validation_count}개는 Final Review Gate를 통과하지 않아 검토 대상 목록에서 숨겼습니다."
        )

    with st.container(border=True):
        st.markdown("#### 최종 검토 흐름")
        render_artifact_pipeline(
            [
                {"title": "검토 대상", "detail": "Practical Validation Gate 통과 후보", "status": "선택", "tone": "neutral"},
                {"title": "판정 요약", "detail": "Decision Cockpit", "status": "자동 계산", "tone": "neutral"},
                {"title": "최종 판단", "detail": "선정 / 보류 / 거절 / 재검토", "status": "명시 기록", "tone": "warning"},
                {"title": "근거 부록", "detail": "이전 검증 결과 read-only 확인", "status": "Appendix", "tone": "neutral"},
            ]
        )

    source_options = _build_final_review_source_options(
        current_rows,
        proposal_rows,
        practical_validation_rows=eligible_practical_validation_rows,
        session_practical_source=session_practical_source if isinstance(session_practical_source, dict) else None,
        include_legacy_sources=False,
    )
    if not source_options:
        st.info("Final Review Gate를 통과한 Practical Validation 후보가 없습니다.")
        st.caption("검증 결과만 저장한 blocked / needs input / not run 후보는 기록으로 남지만, Final Review 검토 대상에는 표시되지 않습니다.")
        st.markdown("#### 기록된 최종 검토 결과 확인")
        with st.container(border=True):
            _render_saved_final_review_decisions(final_decision_rows)
        return

    candidate_contexts = _build_candidate_contexts(
        source_options,
        current_rows=current_rows,
        pre_live_rows=pre_live_rows,
    )

    st.divider()
    st.markdown("#### 1. Candidate Board / 최종 검토 대상 선택")
    with st.container(border=True):
        render_stage_brief(
            purpose="Final Review Gate를 통과한 후보를 먼저 비교하고, 오늘 판단할 source를 고릅니다.",
            result="Candidate board + selected source",
        )
        _render_candidate_board(candidate_contexts)
        labels = [str(context["label"]) for context in candidate_contexts]
        selected_label = st.selectbox("검토 대상", options=labels, key="final_review_source_selected")
        selected_context = candidate_contexts[labels.index(selected_label)]
        source = dict(selected_context["source"])
        render_badge_strip(
            [
                {"label": "Source Type", "value": source.get("source_type") or "-", "tone": "neutral"},
                {"label": "Source ID", "value": source.get("source_id") or "-", "tone": "neutral"},
            ]
        )

    validation = dict(selected_context["validation"])
    paper_observation = dict(selected_context["paper_observation"])
    evidence = dict(selected_context["decision_evidence"])
    investability_packet = dict(selected_context["investability_packet"])
    cockpit = dict(selected_context["cockpit"])

    st.markdown("#### 2. Decision Cockpit")
    with st.container(border=True):
        render_stage_brief(
            purpose="상세 표를 보기 전에, 선정 차단 / 보류 필요 / 선정 가능 여부와 monitoring seed를 먼저 확인합니다.",
            result="Decision state",
        )
        _render_decision_cockpit(cockpit)

    st.markdown("#### 3. 최종 판단 기록")
    with st.container(border=True):
        render_stage_brief(
            purpose="Decision Cockpit을 보고 오늘의 최종 select / hold / reject / re-review 판단을 한 번만 명시적으로 기록합니다.",
            result="Final decision record",
        )
        render_readiness_route_panel(
            route_label=str(evidence.get("route") or "-"),
            score=float(evidence.get("score") or 0.0),
            blockers_count=len(evidence.get("blockers") or []),
            verdict=str(evidence.get("verdict") or "-"),
            next_action=str(evidence.get("next_action") or "-"),
            route_title="Final Review Route",
            score_title="Evidence Score",
        )
        st.caption("상세 validation table은 아래 Evidence Appendix에서 확인합니다. 이 구간은 최종 판단 기록이 주 action입니다.")
        if evidence.get("blockers"):
            for blocker in list(evidence.get("blockers") or []):
                st.warning(str(blocker))
        with st.expander("Final route check detail", expanded=False):
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

        st.info(
            "여기가 실제 최종 판단 구간입니다. 앞 단계의 운영 상태 / proposal 메모는 준비 기록이고, "
            "실전 후보 선정 / 보류 / 거절 / 재검토는 여기에서 한 번만 명시적으로 기록합니다."
        )

        input_cols = st.columns([0.56, 0.44], gap="small")
        with input_cols[0]:
            decision_route = st.selectbox(
                "최종 판단",
                options=FINAL_REVIEW_ROUTE_OPTIONS,
                index=suggested_index,
                key="final_review_decision_route",
                help="이 값이 Final Review의 최종 판단으로 저장됩니다.",
            )
        with input_cols[1]:
            st.text_input("Source", value=str(source.get("source_id") or "-"), disabled=True, key="final_review_source_display")
        st.caption(FINAL_REVIEW_ROUTE_DESCRIPTIONS.get(str(decision_route), "-"))
        operator_reason = st.text_area(
            "판단 사유",
            value="검증 근거와 관찰 기준을 함께 보고 최종 실전 후보 여부를 판단한다.",
            key="final_review_operator_reason",
        )
        with st.expander("고급: 저장 ID / 운영 전 조건 / 다음 행동 확인", expanded=False):
            decision_id = st.text_input("Decision ID", value=default_decision_id, key="final_review_decision_id")
            operator_constraints = st.text_area(
                "운영 전 조건",
                value="실제 투자 전 투입 금액, 리밸런싱, 중단 / 재검토 기준은 사용자가 별도로 확인한다.",
                key="final_review_operator_constraints",
            )
            operator_next_action = st.text_area(
                "다음 행동",
                value="선정이면 최종 판단 완료로 보고, 보류 / 재검토면 추가 관찰 또는 구성 근거를 보강한다.",
                key="final_review_operator_next_action",
            )
        save_evaluation = _build_final_review_save_evaluation(
            evidence=evidence,
            investability_packet=investability_packet,
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
            investability_packet=investability_packet,
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
                append_final_selection_decision_v2(final_row)
                st.session_state["final_review_decision_notice"] = (
                    f"최종 검토 결과 `{final_row['decision_id']}`를 기록했습니다. "
                    "이 기록은 live approval이나 주문 지시가 아닙니다."
                )
                st.session_state["final_review_reset_decision_id_after_save"] = True
                st.rerun()
        with action_cols[1]:
            st.button(
                "Live Approval / Order",
                key="final_review_live_order_disabled",
                disabled=True,
                width="stretch",
                help="Final Review는 최종 검토 기록까지 담당하며 실제 승인/주문은 만들지 않습니다.",
            )
        with st.expander("최종 검토 결과 Preview", expanded=False):
            st.json(final_row)
            st.caption(f"Path: {FINAL_SELECTION_DECISION_V2_FILE}")

    st.markdown("#### 4. Evidence Appendix / 이전 검증 결과 부록")
    with st.container(border=True):
        _render_evidence_appendix(
            validation=validation,
            paper_observation=paper_observation,
            investability_packet=investability_packet,
        )

    st.markdown("#### 5. 기록된 최종 검토 결과 확인")
    with st.container(border=True):
        _render_saved_final_review_decisions(final_decision_rows)
