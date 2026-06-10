from __future__ import annotations

from datetime import date
from typing import Any
from uuid import uuid4

import pandas as pd
import streamlit as st

from app.services.backtest_evidence_read_model import (
    SELECT_FOR_PRACTICAL_PORTFOLIO,
    build_decision_dossier,
    build_final_review_candidate_board,
    build_final_review_decision_cockpit,
    build_final_review_decision_record_guide,
    build_saved_final_review_decision_review,
)
from app.services.backtest_practical_validation import build_market_sentiment_context_overlay
from app.web.backtest_final_review_helpers import (
    FINAL_REVIEW_DECISION_LABELS,
    FINAL_REVIEW_ROUTE_DESCRIPTIONS,
    _build_investability_evidence_packet,
    _build_final_review_decision_evidence_pack,
    _build_final_review_decision_row,
    _build_final_review_decision_rows_for_display,
    _build_final_review_paper_observation_snapshot,
    _build_final_review_save_evaluation,
    _build_final_review_selected_component_rows,
    _build_final_review_source_options,
    _build_final_review_status_display,
    _build_final_review_validation,
    _final_review_slug,
    _is_final_review_eligible_validation_result,
)
from app.web.backtest_final_review_components import (
    render_fr_action_panel,
    render_fr_command_center,
    render_fr_flow,
    render_fr_lane_grid,
    render_fr_section_header,
)
from app.web.backtest_ui_components import (
    render_badge_strip,
    render_readiness_route_panel,
    render_stage_brief,
    render_status_card_grid,
)
from app.web.final_selected_portfolio_dashboard_helpers import (
    build_selected_dashboard_handoff_checklist_table,
    build_selected_dashboard_handoff_table,
)
from app.web.reference_contextual_help import render_reference_contextual_help
from app.runtime import (
    FINAL_SELECTION_DECISION_FILE,
    append_current_final_selection_decision,
    build_selected_dashboard_handoff_review,
    load_current_final_selection_decisions,
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


def _handoff_tone(route: Any) -> str:
    route_text = str(route or "")
    if route_text == "HANDOFF_READY":
        return "positive"
    if route_text in {"HANDOFF_NO_FINAL_DECISION", "HANDOFF_NO_SELECTED_DECISION"}:
        return "warning"
    if route_text == "HANDOFF_BLOCKED":
        return "danger"
    return "neutral"


def _short_text(value: Any, limit: int = 140) -> str:
    text = str(value or "").strip()
    if not text:
        return "-"
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 3)].rstrip() + "..."


def _candidate_board_tone(summary: dict[str, Any]) -> str:
    if int(summary.get("select_ready", 0) or 0) > 0:
        return "positive"
    if int(summary.get("blocked", 0) or 0) > 0:
        return "danger"
    if int(summary.get("hold_or_re_review", 0) or 0) > 0:
        return "warning"
    return "neutral"


def _candidate_board_route(summary: dict[str, Any]) -> tuple[str, str, str]:
    if not int(summary.get("total_candidates", 0) or 0):
        return "검토 후보 없음", "Final Review Gate를 통과한 후보가 없습니다.", "warning"
    if int(summary.get("select_ready", 0) or 0) > 0:
        return "모니터링 후보 있음", "저장 가능한 후보를 확인하고 Portfolio Monitoring 후보로 저장합니다.", "positive"
    if int(summary.get("blocked", 0) or 0) > 0:
        return "차단 원인 확인", "먼저 볼 후보의 blocker를 해소해야 정식 저장이 활성화됩니다.", "danger"
    return "재검토 필요", "review-required 근거를 확인하고 모니터링 후보 가능 상태로 보강합니다.", "warning"


def _policy_rows_preview(rows: list[dict[str, Any]], *, empty_message: str) -> str:
    if not rows:
        return empty_message
    previews: list[str] = []
    for row in rows[:2]:
        label = str(row.get("Criteria") or row.get("Group") or row.get("Module") or "-")
        action = str(row.get("Required Action") or row.get("Fix Action") or row.get("Current") or row.get("Evidence") or "-")
        previews.append(f"{label}: {_short_text(action, 86)}")
    if len(rows) > 2:
        previews.append(f"외 {len(rows) - 2}개")
    return " / ".join(previews)


def _format_sentiment_score(value: Any) -> str:
    try:
        return f"{float(value):.1f}"
    except (TypeError, ValueError):
        return "-"


def _format_sentiment_pct(value: Any) -> str:
    try:
        return f"{float(value):.1f}%"
    except (TypeError, ValueError):
        return "-"


def _format_sentiment_pp(value: Any) -> str:
    try:
        return f"{float(value):+.1f} pp"
    except (TypeError, ValueError):
        return "-"


def _render_market_sentiment_context_overlay() -> None:
    overlay = build_market_sentiment_context_overlay(surface="Final Review")
    risk_context = dict(overlay.get("risk_context") or {})
    metrics = dict(overlay.get("metrics") or {})
    boundary = dict(overlay.get("boundary") or {})
    tone = str(risk_context.get("tone") or "neutral")
    render_fr_section_header(
        eyebrow="Market Context",
        title="시장 심리 Context Overlay",
        detail=(
            "CNN Fear & Greed / AAII sentiment를 Final Review 판단의 배경으로만 보여줍니다. "
            "Candidate Board priority, selected-route gate, 저장 가능 여부는 기존 evidence owner가 계속 결정합니다."
        ),
        tone=tone,
    )
    with st.container(border=True):
        render_fr_action_panel(
            title=f"{risk_context.get('state_label') or 'Neutral'} · {risk_context.get('source_phase_label') or '-'}",
            detail=f"{overlay.get('headline') or ''} {overlay.get('summary') or ''}".strip(),
            route_label="Boundary",
            route_value="Context only",
            route_detail=str(boundary.get("message") or ""),
            route_tone=tone,
            meta_items=[
                {"label": "Gate Effect", "value": boundary.get("gate_effect") or "none"},
                {"label": "Trade Signal", "value": "Disabled"},
                {"label": "Registry Write", "value": "No"},
                {"label": "Live Approval", "value": "Disabled"},
            ],
        )
        render_fr_lane_grid(
            [
                {
                    "kicker": "CNN Fear & Greed",
                    "title": _format_sentiment_score(metrics.get("cnn_fear_greed")),
                    "status": metrics.get("cnn_rating") or overlay.get("status") or "-",
                    "detail": "0~100 headline sentiment score",
                    "tone": tone,
                },
                {
                    "kicker": "AAII Bearish",
                    "title": _format_sentiment_pct(metrics.get("aaii_bearish")),
                    "status": "weekly survey",
                    "detail": "높을수록 개인투자자 비관이 강합니다.",
                    "tone": "warning" if (metrics.get("aaii_bearish") or 0) and float(metrics.get("aaii_bearish") or 0) >= 35 else "neutral",
                },
                {
                    "kicker": "AAII Bull-Bear Spread",
                    "title": _format_sentiment_pp(metrics.get("aaii_bull_bear_spread")),
                    "status": "bullish - bearish",
                    "detail": "양수는 낙관 우위, 음수는 비관 우위입니다.",
                    "tone": "positive" if (metrics.get("aaii_bull_bear_spread") or 0) and float(metrics.get("aaii_bull_bear_spread") or 0) > 0 else "warning",
                },
                {
                    "kicker": "Data Confidence",
                    "title": dict(overlay.get("data_confidence") or {}).get("status") or overlay.get("status") or "-",
                    "status": f"missing {metrics.get('missing_count') or 0} / stale {metrics.get('stale_count') or 0}",
                    "detail": dict(overlay.get("data_confidence") or {}).get("detail") or "Stored DB rows",
                    "tone": dict(overlay.get("data_confidence") or {}).get("tone") or "neutral",
                },
            ],
            min_width=190,
        )
        render_badge_strip(
            [
                {"label": "PASS / BLOCKER", "value": "No effect", "tone": "neutral"},
                {"label": "Saved Setup", "value": "No write", "tone": "neutral"},
                {"label": "Order / Rebalance", "value": "Disabled", "tone": "neutral"},
                {"label": "Surface", "value": overlay.get("surface") or "Final Review", "tone": "neutral"},
            ]
        )
        warnings = list(overlay.get("warnings") or [])
        if warnings:
            st.warning(" / ".join(str(item) for item in warnings))
        evidence_rows = list(overlay.get("evidence_rows") or [])
        if evidence_rows:
            with st.expander("CNN / AAII context evidence", expanded=False):
                st.dataframe(pd.DataFrame(evidence_rows), width="stretch", hide_index=True)
        if overlay.get("next_action"):
            st.caption(str(overlay["next_action"]))


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


def _provenance_display_rows(summary: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for raw_row in list(dict(summary or {}).get("rows") or []):
        row = dict(raw_row or {})
        effect = dict(row.get("decision_effect") or {})
        rows.append(
            {
                "Area": row.get("evidence_area"),
                "Source": row.get("source_name"),
                "Source Type": row.get("source_type"),
                "Source Date": row.get("source_date"),
                "Collected": row.get("collected_at"),
                "Snapshot Kind": row.get("snapshot_kind"),
                "Coverage": row.get("coverage_status"),
                "Freshness": row.get("freshness_status"),
                "Staleness Days": row.get("staleness_days"),
                "PIT Safe": row.get("is_point_in_time_safe"),
                "Proxy": row.get("proxy_status"),
                "Decision": effect.get("status"),
                "Treat As Pass": effect.get("treat_as_pass"),
                "PIT Risk": row.get("pit_risk"),
                "Look-ahead Risk": row.get("lookahead_risk"),
                "Survivorship Risk": row.get("survivorship_risk"),
            }
        )
    return rows


def _render_investability_packet(packet: dict[str, Any]) -> None:
    summary = dict(packet.get("summary") or {})
    source_chain = dict(packet.get("source_chain") or {})
    gate_policy = dict(packet.get("gate_policy_snapshot") or {})
    robustness_run_set = dict(packet.get("robustness_run_set") or {})
    data_provenance = dict(packet.get("data_provenance_summary") or {})
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
    if robustness_run_set:
        st.markdown("###### Robustness Experiment Run-Set")
        run_set_effect = dict(robustness_run_set.get("decision_effect") or {})
        render_badge_strip(
            [
                {"label": "Run-set", "value": robustness_run_set.get("robustness_run_set_id") or "-", "tone": "neutral"},
                {"label": "Status", "value": robustness_run_set.get("overall_status") or "-", "tone": _status_tone(robustness_run_set.get("overall_status"))},
                {"label": "Strategy", "value": robustness_run_set.get("strategy_key") or "-", "tone": "neutral"},
                {"label": "Experiments", "value": len(robustness_run_set.get("experiment_types") or []), "tone": "neutral"},
                {
                    "label": "Final Review",
                    "value": run_set_effect.get("final_review") or "-",
                    "tone": _status_tone(run_set_effect.get("final_review")),
                },
            ]
        )
        st.caption(
            "Run-set은 Robustness Lab을 대체하지 않는 provenance/grouping layer입니다. "
            "`NOT_RUN` / `REVIEW` / `BLOCKED` evidence는 pass로 승격하지 않습니다."
        )
        run_set_rows = list(robustness_run_set.get("not_run_review_blocked_evidence") or [])
        if run_set_rows:
            with st.expander("Run-set non-pass evidence", expanded=False):
                st.dataframe(pd.DataFrame(run_set_rows), width="stretch", hide_index=True)
    provenance_rows = _provenance_display_rows(data_provenance)
    if provenance_rows:
        st.markdown("###### Data Provenance / PIT Contract")
        provenance_metrics = dict(data_provenance.get("metrics") or {})
        render_badge_strip(
            [
                {
                    "label": "Route",
                    "value": data_provenance.get("route_label") or data_provenance.get("route") or "-",
                    "tone": _status_tone(data_provenance.get("overall_status")),
                },
                {
                    "label": "Current",
                    "value": provenance_metrics.get("current_snapshot_rows", 0),
                    "tone": "warning" if provenance_metrics.get("current_snapshot_rows") else "neutral",
                },
                {
                    "label": "Proxy",
                    "value": provenance_metrics.get("proxy_rows", 0),
                    "tone": "warning" if provenance_metrics.get("proxy_rows") else "neutral",
                },
                {
                    "label": "Stale",
                    "value": provenance_metrics.get("stale_or_unknown_rows", 0),
                    "tone": "warning" if provenance_metrics.get("stale_or_unknown_rows") else "neutral",
                },
                {
                    "label": "PIT Safe",
                    "value": provenance_metrics.get("pit_safe_rows", 0),
                    "tone": "positive" if provenance_metrics.get("pit_safe_rows") else "neutral",
                },
            ]
        )
        st.caption(
            "current snapshot / stale / proxy / non-PIT-safe evidence는 `Treat As Pass=False`로 남겨 최종 판단에서 숨기지 않습니다."
        )
        with st.expander("Provenance row detail", expanded=False):
            st.dataframe(pd.DataFrame(provenance_rows), width="stretch", hide_index=True)
    st.dataframe(pd.DataFrame(packet.get("checks") or []), width="stretch", hide_index=True)
    policy_rows = list(gate_policy.get("policy_rows") or [])
    if policy_rows:
        st.markdown("###### Validation Gate Policy")
        st.caption("profile-aware gate matrix입니다. `Selected Route = Blocked`이면 정식 선정 저장은 비활성화됩니다.")
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
    route_value, route_detail, route_tone = _candidate_board_route(summary)
    render_fr_lane_grid(
        [
            {
                "kicker": "Next Review",
                "title": _short_text(summary.get("first_review_candidate") or "검토 후보 없음", 96),
                "status": route_value,
                "detail": _short_text(summary.get("first_review_reason") or route_detail, 150),
                "meta": _short_text(summary.get("first_review_action") or "-", 100),
                "tone": route_tone,
            },
            {
                "title": "Select Ready",
                "status": summary.get("select_ready", 0),
                "detail": "선정 기록 가능 후보",
                "tone": "positive" if summary.get("select_ready") else "neutral",
            },
            {
                "title": "Hold / Re-review",
                "status": summary.get("hold_or_re_review", 0),
                "detail": "보류 / 재검토 판단 필요",
                "tone": "warning" if summary.get("hold_or_re_review") else "neutral",
            },
            {
                "title": "Blocked",
                "status": summary.get("blocked", 0),
                "detail": "선정 전 차단 원인 있음",
                "tone": "danger" if summary.get("blocked") else "neutral",
            },
        ],
        min_width=210,
    )
    queue_rows = list(board.get("review_queue_rows") or [])
    if queue_rows:
        st.markdown("###### Review Queue")
        st.dataframe(pd.DataFrame(queue_rows), width="stretch", hide_index=True)
    with st.expander("Candidate Board detail", expanded=False):
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
    st.caption(
        "Candidate Board는 기존 Practical Validation result와 investability packet을 읽는 비교표입니다. "
        "Review Priority는 화면 정렬용 우선순위이며, 새 registry row를 만들거나 provider 데이터를 수집하지 않습니다."
    )


def _render_decision_cockpit(cockpit: dict[str, Any]) -> None:
    metrics = dict(cockpit.get("metrics") or {})
    handoff = dict(cockpit.get("monitoring_handoff") or {})
    source_chain = dict(cockpit.get("source_chain") or {})
    must_fix_rows = list(cockpit.get("must_fix_rows") or [])
    must_review_rows = list(cockpit.get("must_review_rows") or [])
    watch_rows = list(cockpit.get("watch_rows") or [])
    cockpit_tone = _cockpit_tone(cockpit.get("state"))
    render_fr_action_panel(
        title="Decision Cockpit",
        detail=str(cockpit.get("verdict") or "-"),
        route_label="Suggested Decision",
        route_value=str(cockpit.get("suggested_decision_label") or "-"),
        route_detail=str(cockpit.get("next_action") or "-"),
        route_tone=cockpit_tone,
        meta_items=[
            {"label": "State", "value": cockpit.get("state_label") or "-"},
            {"label": "Gate", "value": cockpit.get("gate_outcome") or "-"},
            {"label": "Packet Score", "value": f"{float(cockpit.get('packet_score') or 0.0):.1f}"},
            {"label": "Validation", "value": source_chain.get("validation_id") or "-"},
            {"label": "Live Approval", "value": "Disabled"},
        ],
    )
    render_fr_lane_grid(
        [
            {
                "kicker": "Gate Policy",
                "title": "Must Fix",
                "status": len(must_fix_rows),
                "detail": _policy_rows_preview(must_fix_rows, empty_message="선정 차단 blocker 없음"),
                "tone": "danger" if must_fix_rows else "positive",
            },
            {
                "kicker": "Gate Policy",
                "title": "Must Review",
                "status": len(must_review_rows),
                "detail": _policy_rows_preview(must_review_rows, empty_message="선정 전 review-required 없음"),
                "tone": "warning" if must_review_rows else "positive",
            },
            {
                "kicker": "Monitoring Seed",
                "title": str(handoff.get("review_cadence") or "관찰 기준 미지정"),
                "status": f"{handoff.get('active_components', 0)} components",
                "detail": (
                    f"Benchmark {handoff.get('tracking_benchmark') or '-'} / "
                    f"Triggers {len(handoff.get('review_triggers') or [])} / "
                    f"Weight {handoff.get('target_weight_total') or '-'}"
                ),
                "tone": "info",
            },
            {
                "kicker": "Watch Only",
                "title": "Policy Watch",
                "status": len(watch_rows),
                "detail": _policy_rows_preview(watch_rows, empty_message="관찰 전용 policy row 없음"),
                "tone": "warning" if watch_rows else "neutral",
            },
        ],
        min_width=220,
    )
    with st.expander("Decision Cockpit detail", expanded=False):
        render_badge_strip(
            [
                {"label": "State", "value": cockpit.get("state_label") or "-", "tone": cockpit_tone},
                {"label": "Suggested", "value": cockpit.get("suggested_decision_label") or "-", "tone": cockpit_tone},
                {"label": "Gate", "value": cockpit.get("gate_outcome") or "-", "tone": "positive" if cockpit.get("select_allowed") else "warning"},
                {"label": "Blockers", "value": metrics.get("policy_blockers", 0), "tone": "danger" if metrics.get("policy_blockers") else "neutral"},
                {"label": "Review", "value": metrics.get("policy_review_required", 0), "tone": "warning" if metrics.get("policy_review_required") else "neutral"},
                {"label": "NOT_RUN", "value": metrics.get("not_run", 0), "tone": "warning" if metrics.get("not_run") else "neutral"},
            ]
        )
        detail_tabs = st.tabs(["Must Fix", "Must Review", "Monitoring Seed", "Watch-only"])
        with detail_tabs[0]:
            if must_fix_rows:
                st.dataframe(pd.DataFrame(must_fix_rows), width="stretch", hide_index=True)
            else:
                st.success("선정 차단 blocker 없음")
        with detail_tabs[1]:
            if must_review_rows:
                st.dataframe(pd.DataFrame(must_review_rows), width="stretch", hide_index=True)
            else:
                st.success("선정 전 review-required 없음")
        with detail_tabs[2]:
            st.dataframe(
                pd.DataFrame(
                    [
                        {"Field": "Cadence", "Value": str(handoff.get("review_cadence") or "-")},
                        {"Field": "Benchmark", "Value": str(handoff.get("tracking_benchmark") or "-")},
                        {"Field": "Triggers", "Value": str(len(handoff.get("review_triggers") or []))},
                        {"Field": "Components", "Value": str(handoff.get("active_components", 0))},
                        {"Field": "Weight Total", "Value": str(handoff.get("target_weight_total") or "-")},
                    ]
                ),
                width="stretch",
                hide_index=True,
            )
        with detail_tabs[3]:
            if watch_rows:
                st.dataframe(pd.DataFrame(watch_rows), width="stretch", hide_index=True)
            else:
                st.info("관찰 전용 policy row가 없습니다.")


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
            "모니터링 후보 선정에 필요한 요약은 위 Decision Cockpit과 Final Decision Action에 있습니다. "
            "이 부록은 왜 그런 후보 가능 / 차단 판단이 나왔는지 원본 근거를 추적할 때 확인합니다."
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


def _render_selected_dashboard_handoff(final_decision_rows: list[dict[str, Any]]) -> None:
    handoff = build_selected_dashboard_handoff_review(final_decision_rows)
    summary = dict(handoff.get("summary") or {})
    route = str(handoff.get("route") or "")
    st.markdown("##### Portfolio Monitoring Handoff")
    render_badge_strip(
        [
            {"label": "Handoff", "value": handoff.get("route_label") or route, "tone": _handoff_tone(route)},
            {
                "label": "Selected Rows",
                "value": summary.get("selected_decision_count", 0),
                "tone": "positive" if summary.get("selected_decision_count") else "warning",
            },
            {
                "label": "Dashboard Rows",
                "value": summary.get("dashboard_row_count", 0),
                "tone": "positive" if summary.get("dashboard_row_count") else "neutral",
            },
            {
                "label": "Monitorable",
                "value": summary.get("monitorable_count", 0),
                "tone": "positive" if summary.get("monitorable_count") else "warning",
            },
            {
                "label": "Blocked",
                "value": summary.get("blocked_count", 0),
                "tone": "danger" if summary.get("blocked_count") else "neutral",
            },
            {"label": "Approval / Order", "value": "Disabled", "tone": "neutral"},
        ]
    )
    message = f"{handoff.get('verdict') or '-'} 다음 단계: {handoff.get('next_action') or '-'}"
    if route == "HANDOFF_READY":
        st.success(message)
    elif route == "HANDOFF_BLOCKED":
        st.error(message)
    else:
        st.warning(message)
    handoff_df = build_selected_dashboard_handoff_table(handoff)
    if not handoff_df.empty:
        st.dataframe(handoff_df, width="stretch", hide_index=True)
    else:
        st.caption("Portfolio Monitoring으로 넘길 모니터링 후보 row가 아직 없습니다.")
    with st.expander("Handoff checklist / storage boundary", expanded=False):
        checklist_df = build_selected_dashboard_handoff_checklist_table(handoff)
        if not checklist_df.empty:
            st.dataframe(checklist_df, width="stretch", hide_index=True)
        boundary = dict(handoff.get("execution_boundary") or {})
        st.caption(
            f"Destination: {handoff.get('destination') or '-'} / "
            f"write policy: {boundary.get('write_policy') or '-'} / "
            f"monitoring auto-write: {boundary.get('monitoring_log_auto_write')} / "
            f"auto rebalance: {boundary.get('auto_rebalance')}"
        )


def _render_saved_final_review_decisions(final_decision_rows: list[dict[str, Any]]) -> None:
    if not final_decision_rows:
        st.info("아직 저장된 모니터링 후보 선정 결과가 없습니다.")
        st.caption(f"Path: {FINAL_SELECTION_DECISION_FILE}")
        _render_selected_dashboard_handoff(final_decision_rows)
        return

    review = build_saved_final_review_decision_review(final_decision_rows)
    summary = dict(review.get("summary") or {})
    render_stage_brief(
        purpose="저장된 모니터링 후보 선정 기록을 다시 읽고, 어떤 후보가 Portfolio Monitoring으로 이어지는지 확인합니다.",
        result="Saved decision ledger",
    )
    render_status_card_grid(
        [
            {"title": "Saved Decisions", "value": summary.get("total_records", 0), "tone": "positive"},
            {"title": "Selected", "value": summary.get("selected", 0), "detail": "Dashboard eligible", "tone": "positive" if summary.get("selected") else "neutral"},
            {"title": "Hold", "value": summary.get("hold", 0), "tone": "warning" if summary.get("hold") else "neutral"},
            {"title": "Reject", "value": summary.get("reject", 0), "tone": "warning" if summary.get("reject") else "neutral"},
            {"title": "Re-review", "value": summary.get("re_review", 0), "tone": "warning" if summary.get("re_review") else "neutral"},
            {"title": "Live Approval", "value": "Disabled", "detail": "review only", "tone": "neutral"},
        ]
    )
    _render_selected_dashboard_handoff(final_decision_rows)
    st.info(
        "최근 판단: "
        f"{summary.get('latest_updated_at') or '-'} / "
        f"{summary.get('latest_decision') or '-'} / "
        f"id={summary.get('latest_decision_id') or '-'}"
    )
    filter_options = list(review.get("filter_options") or ["All"])
    selected_filter = st.selectbox(
        "판단 상태 필터",
        options=filter_options,
        key="final_review_saved_decision_route_filter",
    )
    review_rows = list(review.get("rows") or [])
    if selected_filter != "All":
        review_rows = [row for row in review_rows if row.get("Route Family") == selected_filter]
    st.caption(f"표시 중인 기록: {len(review_rows)} / {summary.get('total_records', 0)}")
    if not review_rows:
        st.warning("선택한 필터에 해당하는 최종 검토 기록이 없습니다.")
        return

    table_rows = [
        {key: value for key, value in row.items() if not str(key).startswith("_")}
        for row in review_rows
    ]
    st.dataframe(pd.DataFrame(table_rows), width="stretch", hide_index=True)
    labels = [
        f"{row.get('Updated At')} | {row.get('Decision')} | {row.get('Decision ID')}"
        for row in review_rows
    ]
    selected_label = st.selectbox(
        "기록 확인",
        options=labels,
        key=f"final_review_saved_decision_selected_{selected_filter}",
    )
    selected_review_row = review_rows[labels.index(selected_label)]
    selected_row = dict(final_decision_rows[int(selected_review_row.get("_row_index", 0))] or {})
    evidence = dict(selected_row.get("decision_evidence_snapshot") or {})
    status_display = _build_final_review_status_display(selected_row)
    decision_label = FINAL_REVIEW_DECISION_LABELS.get(str(selected_row.get("decision_route") or ""), "재검토 필요")
    detail_tabs = st.tabs(["Summary", "Dossier", "Evidence Packet", "Raw JSON"])
    with detail_tabs[0]:
        render_readiness_route_panel(
            route_label=str(status_display.get("route") or "-"),
            score=float(evidence.get("score") or 0.0),
            blockers_count=len(evidence.get("blockers") or []),
            verdict=str(status_display.get("verdict") or "-"),
            next_action=str(status_display.get("next_action") or "-"),
            route_title="Final Review Status",
            score_title="Evidence Score",
        )
        render_badge_strip(
            [
                {
                    "label": "Decision",
                    "value": selected_row.get("decision_route") or "-",
                    "tone": "positive" if selected_row.get("decision_route") == "SELECT_FOR_PRACTICAL_PORTFOLIO" else "warning",
                },
                {
                    "label": "판단 라벨",
                    "value": decision_label,
                    "tone": "positive" if selected_row.get("decision_route") == "SELECT_FOR_PRACTICAL_PORTFOLIO" else "warning",
                },
                {"label": "Source", "value": f"{selected_row.get('source_type')} / {selected_row.get('source_id')}", "tone": "neutral"},
                {"label": "Observation", "value": selected_row.get("source_observation_id") or selected_row.get("source_paper_ledger_id") or "-", "tone": "neutral"},
                {"label": "Dashboard", "value": "Eligible" if selected_row.get("decision_route") == "SELECT_FOR_PRACTICAL_PORTFOLIO" else "Not selected", "tone": "positive" if selected_row.get("decision_route") == "SELECT_FOR_PRACTICAL_PORTFOLIO" else "neutral"},
                {"label": "Order", "value": "Disabled", "tone": "neutral"},
            ]
        )
        operator = dict(selected_row.get("operator_decision") or {})
        st.markdown("###### Operator Decision")
        st.dataframe(
            pd.DataFrame(
                [
                    {"Field": "Reason", "Value": operator.get("reason") or "-"},
                    {"Field": "Constraints", "Value": operator.get("constraints") or "-"},
                    {"Field": "Next Action", "Value": operator.get("next_action") or "-"},
                ]
            ),
            width="stretch",
            hide_index=True,
        )
        component_df = _build_final_review_selected_component_rows(selected_row)
        if component_df.empty:
            st.info("이 기록에는 selected component가 없습니다.")
        else:
            st.markdown("###### Components")
            st.dataframe(component_df, width="stretch", hide_index=True)
    with detail_tabs[1]:
        _render_decision_dossier_export(
            selected_row,
            key_prefix=f"final_review_dossier_{selected_row.get('decision_id') or 'saved'}",
        )
    with detail_tabs[2]:
        packet = dict(selected_row.get("investability_evidence_packet") or {})
        if packet:
            _render_investability_packet(packet)
        else:
            st.info("이 기록에는 investability evidence packet snapshot이 없습니다.")
    with detail_tabs[3]:
        st.json(selected_row)


def render_final_review_workspace() -> None:
    st.markdown("### Final Review")
    st.caption(
        "Portfolio Monitoring에서 추적할 모니터링 후보로 선정할지 판단하는 공간입니다. Candidate Board와 Decision Cockpit으로 판단 상태를 먼저 보고, "
        "selected-route gate까지 통과한 후보만 정식 저장합니다. 필요한 경우에만 이전 validation evidence 부록을 확인합니다. 검토 대상은 Practical Validation Gate를 통과한 후보만 표시합니다."
    )
    render_reference_contextual_help("final_review")

    practical_validation_rows = load_practical_validation_results()
    eligible_practical_validation_rows = [
        row
        for row in practical_validation_rows
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
        [],
        [],
        practical_validation_rows=eligible_practical_validation_rows,
        session_practical_source=session_practical_source if isinstance(session_practical_source, dict) else None,
        include_legacy_sources=False,
    )
    candidate_contexts = (
        _build_candidate_contexts(
            source_options,
            current_rows=[],
            pre_live_rows=[],
        )
        if source_options
        else []
    )
    candidate_board = build_final_review_candidate_board(candidate_contexts) if candidate_contexts else {}
    candidate_summary = dict(candidate_board.get("summary") or {})
    route_value, route_detail, route_tone = _candidate_board_route(candidate_summary)
    dashboard_handoff = build_selected_dashboard_handoff_review(final_decision_rows)
    dashboard_summary = dict(dashboard_handoff.get("summary") or {})
    hidden_validation_count = len(practical_validation_rows) - len(eligible_practical_validation_rows)
    render_fr_command_center(
        eyebrow="Final Review Decision Desk",
        title="모니터링 후보 선별",
        detail=(
            "Practical Validation Gate를 통과한 후보만 비교하고, Decision Cockpit에서 차단 / 보류 / 모니터링 후보 가능 상태를 확인한 뒤 "
            "가능 후보만 정식 저장합니다."
        ),
        route_label="오늘의 판단 상태",
        route_value=route_value,
        route_detail=route_detail,
        route_tone=route_tone,
        kpis=[
            {
                "label": "Saved PV",
                "value": len(practical_validation_rows),
                "detail": "기록용 저장 포함",
            },
            {
                "label": "Eligible",
                "value": f"{len(eligible_practical_validation_rows)} / {len(practical_validation_rows)}",
                "detail": "Final Review Gate 통과",
            },
            {"label": "Hidden", "value": hidden_validation_count, "detail": "Gate 미통과 기록"},
            {
                "label": "Review Queue",
                "value": candidate_summary.get("total_candidates", 0),
                "detail": "오늘 비교할 후보",
            },
            {"label": "Final Records", "value": len(final_decision_rows), "detail": "저장된 모니터링 후보 기록"},
            {
                "label": "Monitoring Selected",
                "value": dashboard_summary.get("selected_decision_count", 0),
                "detail": "Portfolio Monitoring 후보",
            },
        ],
    )
    render_fr_flow(
        [
            {
                "title": "후보 선택",
                "detail": "Gate 통과 후보를 Candidate Board에서 비교합니다.",
                "tone": "info",
            },
            {
                "title": "상태 판단",
                "detail": "Decision Cockpit에서 선정 차단 / 보류 / 모니터링 후보 가능 상태를 확인합니다.",
                "tone": "neutral",
            },
            {
                "title": "모니터링 후보 저장",
                "detail": "selected-route gate가 통과된 후보만 정식 저장합니다.",
                "tone": "warning",
            },
            {
                "title": "근거 확인",
                "detail": "필요할 때만 이전 validation evidence를 read-only 부록으로 확인합니다.",
                "tone": "neutral",
            },
            {
                "title": "대시보드 연결",
                "detail": "선정 기록만 Portfolio Monitoring 후보로 전달됩니다.",
                "tone": "positive",
            },
        ]
    )
    _render_market_sentiment_context_overlay()
    if hidden_validation_count > 0:
        st.caption(
            f"Practical Validation 저장 기록 {hidden_validation_count}개는 Final Review Gate를 통과하지 않아 검토 대상 목록에서 숨겼습니다."
        )

    if not source_options:
        st.info("Final Review Gate를 통과한 Practical Validation 후보가 없습니다.")
        st.caption("검증 결과만 저장한 blocked / needs input / not run 후보는 기록으로 남지만, Final Review 검토 대상에는 표시되지 않습니다.")
        render_fr_section_header(
            eyebrow="Saved Decisions",
            title="Decision History / Dashboard Handoff",
            detail="새로 판단할 후보가 없을 때도 기존 최종 판단과 Dashboard handoff 상태는 확인할 수 있습니다.",
            tone=_handoff_tone(dashboard_handoff.get("route")),
        )
        with st.container(border=True):
            _render_saved_final_review_decisions(final_decision_rows)
        return

    st.divider()
    render_fr_section_header(
        eyebrow="Step 1",
        title="Candidate Board",
        detail="Final Review Gate를 통과한 후보를 먼저 비교하고, 오늘 판단할 source를 고릅니다.",
        tone=_candidate_board_tone(candidate_summary),
    )
    with st.container(border=True):
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

    render_fr_section_header(
        eyebrow="Step 2",
        title="Decision Cockpit",
        detail="상세 표를 보기 전에 선정 차단, 보류 필요, 모니터링 후보 가능 여부와 monitoring seed를 먼저 확인합니다.",
        tone=_cockpit_tone(cockpit.get("state")),
    )
    with st.container(border=True):
        _render_decision_cockpit(cockpit)

    render_fr_section_header(
        eyebrow="Step 3",
        title="Final Decision Action",
        detail="Decision Cockpit을 보고 모니터링 후보 선정 저장 가능 여부를 확인합니다.",
        tone="warning",
    )
    with st.container(border=True):
        render_fr_action_panel(
            title="Final Decision Action",
            detail=(
                "이 구간이 Portfolio Monitoring 후보 저장입니다. 운영 상태와 proposal 메모는 준비 기록이고, "
                "보류 / 거절 / 재검토는 저장하지 않는 상태 안내로만 표시합니다."
            ),
            route_label="Evidence Route",
            route_value=str(evidence.get("route") or "-"),
            route_detail=str(evidence.get("next_action") or "-"),
            route_tone="danger" if evidence.get("blockers") else "positive",
            meta_items=[
                {"label": "Evidence Score", "value": f"{float(evidence.get('score') or 0.0):.1f}"},
                {"label": "Blockers", "value": len(evidence.get("blockers") or [])},
                {"label": "Source", "value": source.get("source_id") or "-"},
                {"label": "Live Approval", "value": "Disabled"},
            ],
        )
        st.caption("상세 validation table은 아래 Evidence Appendix에서 확인합니다. 이 구간은 모니터링 후보 선정 저장이 주 action입니다.")
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
        source_slug = _final_review_slug(source.get("source_id"))
        source_display_key = f"final_review_source_display_v1_{source_slug}"
        decision_id_key = f"final_review_decision_id_v1_{source_slug}"
        if st.session_state.pop("final_review_reset_decision_id_after_save", False):
            reset_source_slug = str(st.session_state.pop("final_review_reset_decision_id_source_slug", "") or source_slug)
            st.session_state.pop(f"final_review_decision_id_v1_{reset_source_slug}", None)
            st.session_state.pop("final_review_decision_id", None)
        default_decision_id = f"final_{source_slug}_{date.today().strftime('%Y%m%d')}_{uuid4().hex[:6]}"
        gate_policy_snapshot = dict(investability_packet.get("gate_policy_snapshot") or {})
        suggested_route = str(
            gate_policy_snapshot.get("suggested_decision_route")
            or evidence.get("suggested_decision_route")
            or cockpit.get("suggested_decision_route")
            or SELECT_FOR_PRACTICAL_PORTFOLIO
        )
        decision_route = SELECT_FOR_PRACTICAL_PORTFOLIO
        official_route_label = FINAL_REVIEW_DECISION_LABELS.get(decision_route, decision_route)
        suggested_route_label = FINAL_REVIEW_DECISION_LABELS.get(suggested_route, suggested_route or "-")
        official_route_display_key = f"final_review_official_route_display_v1_{source_slug}"
        operator_reason_key = f"final_review_selection_reason_v2_{source_slug}"
        operator_constraints_key = f"final_review_selection_constraints_v2_{source_slug}"
        operator_next_action_key = f"final_review_selection_next_action_v2_{source_slug}"

        input_cols = st.columns([0.56, 0.44], gap="small")
        with input_cols[0]:
            st.text_input(
                "정식 저장",
                value=official_route_label,
                disabled=True,
                key=official_route_display_key,
                help="Final Review의 정식 저장은 selected-route gate를 통과한 모니터링 후보 선정만 허용합니다.",
            )
        with input_cols[1]:
            st.text_input("Source", value=str(source.get("source_id") or "-"), disabled=True, key=source_display_key)
        st.caption(
            "정식 저장은 모니터링 후보 선정만 남깁니다. "
            f"현재 권장 상태는 `{suggested_route_label}`이며, 보류 / 거절 / 재검토는 저장하지 않는 상태 안내입니다. "
            f"{FINAL_REVIEW_ROUTE_DESCRIPTIONS.get(decision_route, '')}"
        )
        decision_record_guide = build_final_review_decision_record_guide(
            decision_route=decision_route,
            decision_evidence=evidence,
            investability_packet=investability_packet,
        )
        official_save_ready = bool(decision_record_guide.get("recordable_route"))
        selected_gate = dict(decision_record_guide.get("selected_route_gate") or {})
        render_badge_strip(
            [
                {
                    "label": "Suggested",
                    "value": decision_record_guide.get("suggested_decision_label") or "-",
                    "tone": "neutral",
                },
                {
                    "label": "Official Save",
                    "value": decision_record_guide.get("decision_label") or "-",
                    "tone": "positive" if official_save_ready else "warning",
                },
                {
                    "label": "Selected Gate",
                    "value": "Ready" if selected_gate.get("Ready") else "Blocked",
                    "tone": "positive" if selected_gate.get("Ready") else "danger",
                },
                {
                    "label": "Record Type",
                    "value": decision_record_guide.get("route_state_label") or "-",
                    "tone": "positive" if official_save_ready else "warning",
                },
                {"label": "Live Approval", "value": "Disabled", "tone": "neutral"},
            ]
        )
        notice = str(decision_record_guide.get("notice") or "")
        if decision_record_guide.get("notice_level") == "warning":
            st.warning(notice)
        elif decision_record_guide.get("notice_level") == "success":
            st.success(notice)
        else:
            st.info(notice)
        with st.expander("Decision Record Checklist", expanded=True):
            st.dataframe(pd.DataFrame(decision_record_guide.get("checklist_rows") or []), width="stretch", hide_index=True)
            st.caption("이 checklist는 기존 evidence를 다시 검증하지 않고, 최종 기록 전에 route 의미와 저장 경계를 보여주는 안내입니다.")
        route_templates = dict(decision_record_guide.get("route_templates") or {})
        if not official_save_ready:
            route_templates = {
                "reason": (
                    f"현재 권장 상태는 {suggested_route_label}이며, selected-route blocker가 남아 "
                    "모니터링 후보 선정 저장을 하지 않는다."
                ),
                "constraints": "Must Fix / Must Review 항목을 해소한 뒤에만 Portfolio Monitoring 후보로 선정할 수 있다.",
                "next_action": "Practical Validation 또는 해당 evidence 보강 위치로 돌아가 blocker를 해소한 뒤 Final Review에서 다시 확인한다.",
            }
        if not str(st.session_state.get(operator_reason_key) or "").strip():
            st.session_state[operator_reason_key] = str(route_templates.get("reason") or "")
        if not str(st.session_state.get(operator_constraints_key) or "").strip():
            st.session_state[operator_constraints_key] = str(route_templates.get("constraints") or "")
        if not str(st.session_state.get(operator_next_action_key) or "").strip():
            st.session_state[operator_next_action_key] = str(route_templates.get("next_action") or "")
        with st.expander("선정 저장 문안 / 미통과 시 다음 행동", expanded=False):
            st.markdown(f"**선정 사유**: {route_templates.get('reason') or '-'}")
            st.markdown(f"**운영 전 조건**: {route_templates.get('constraints') or '-'}")
            st.markdown(f"**다음 행동**: {route_templates.get('next_action') or '-'}")
        operator_reason = st.text_area(
            "선정 사유",
            key=operator_reason_key,
            placeholder=str(route_templates.get("reason") or ""),
        )
        with st.expander("고급: 저장 ID / 운영 전 조건 / 다음 행동 확인", expanded=False):
            decision_id = st.text_input("Decision ID", value=default_decision_id, key=decision_id_key)
            operator_constraints = st.text_area(
                "운영 전 조건",
                key=operator_constraints_key,
                placeholder=str(route_templates.get("constraints") or ""),
            )
            operator_next_action = st.text_area(
                "다음 행동",
                key=operator_next_action_key,
                placeholder=str(route_templates.get("next_action") or ""),
            )
        save_evaluation = _build_final_review_save_evaluation(
            evidence=evidence,
            investability_packet=investability_packet,
            decision_id=decision_id,
            decision_route=decision_route,
            operator_reason=operator_reason,
            existing_decision_ids=existing_decision_ids,
        )
        render_fr_action_panel(
            title="Selection Save Readiness",
            detail=str(save_evaluation.get("verdict") or "-"),
            route_label="Official Save",
            route_value=str(save_evaluation.get("route") or "-"),
            route_detail=str(save_evaluation.get("next_action") or "-"),
            route_tone="positive" if save_evaluation.get("can_save") else "danger",
            meta_items=[
                {"label": "Record Score", "value": f"{float(save_evaluation.get('score') or 0.0):.1f}"},
                {"label": "Blockers", "value": len(save_evaluation.get("blockers") or [])},
                {"label": "Decision ID", "value": decision_id},
                {"label": "Storage", "value": "Monitoring Candidate"},
            ],
        )
        final_row = _build_final_review_decision_row(
            source=source,
            validation=validation,
            paper_observation=paper_observation,
            evidence=evidence,
            investability_packet=investability_packet,
            decision_id=decision_id,
            decision_route=decision_route,
            operator_reason=operator_reason,
            operator_constraints=operator_constraints,
            operator_next_action=operator_next_action,
        )
        action_cols = st.columns(2, gap="small")
        with action_cols[0]:
            if st.button(
                "모니터링 후보로 선정",
                key="final_review_record_decision",
                disabled=not bool(save_evaluation.get("can_save")),
                width="stretch",
            ):
                append_current_final_selection_decision(final_row)
                st.session_state["final_review_decision_notice"] = (
                    f"모니터링 후보 선정 `{final_row['decision_id']}`를 기록했습니다. "
                    "이 기록은 live approval이나 주문 지시가 아닙니다."
                )
                st.session_state["final_review_reset_decision_id_after_save"] = True
                st.session_state["final_review_reset_decision_id_source_slug"] = source_slug
                st.rerun()
        with action_cols[1]:
            st.button(
                "Live Approval / Order",
                key="final_review_live_order_disabled",
                disabled=True,
                width="stretch",
                help="Final Review는 모니터링 후보 선정 저장까지 담당하며 실제 승인/주문은 만들지 않습니다.",
            )
        with st.expander("모니터링 후보 선정 Preview", expanded=False):
            st.json(final_row)
            st.caption(f"Path: {FINAL_SELECTION_DECISION_FILE}")

    render_fr_section_header(
        eyebrow="Step 4",
        title="Evidence Appendix",
        detail="모니터링 후보 선정에 필요한 요약은 위에서 끝내고, 원본 검증 근거는 필요한 경우에만 read-only로 확인합니다.",
        tone="neutral",
    )
    with st.container(border=True):
        _render_evidence_appendix(
            validation=validation,
            paper_observation=paper_observation,
            investability_packet=investability_packet,
        )

    render_fr_section_header(
        eyebrow="Step 5",
        title="Decision History / Dashboard Handoff",
        detail="저장된 모니터링 후보 선정 기록과 Portfolio Monitoring으로 이어질 후보 상태를 확인합니다.",
        tone=_handoff_tone(dashboard_handoff.get("route")),
    )
    with st.container(border=True):
        _render_saved_final_review_decisions(final_decision_rows)
