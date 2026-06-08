from __future__ import annotations

import streamlit as st

from app.web.reference_contextual_help import render_reference_contextual_help
from app.web.backtest_compare import render_compare_portfolio_workspace
from app.web.backtest_single_strategy import render_single_strategy_workspace
from app.web.backtest_workflow_routes import (
    BACKTEST_ANALYSIS_MODE_COMPARE,
    BACKTEST_ANALYSIS_MODE_OPTIONS,
    BACKTEST_ANALYSIS_MODE_SINGLE,
    BACKTEST_LEGACY_ANALYSIS_MODE_COMPARE,
)


def render_backtest_analysis_workspace() -> None:
    st.markdown("### Backtest Analysis")
    st.caption(
        "Single Strategy 또는 Portfolio Mix Builder로 1차 후보를 만들고, "
        "통과한 후보만 Practical Validation source로 보냅니다."
    )
    render_reference_contextual_help("backtest_analysis")
    current_mode = st.session_state.get("backtest_analysis_mode")
    if current_mode == BACKTEST_LEGACY_ANALYSIS_MODE_COMPARE:
        st.session_state.backtest_analysis_mode = BACKTEST_ANALYSIS_MODE_COMPARE
    elif current_mode not in BACKTEST_ANALYSIS_MODE_OPTIONS:
        st.session_state.backtest_analysis_mode = BACKTEST_ANALYSIS_MODE_SINGLE
    mode = st.radio(
        "Analysis Mode",
        options=BACKTEST_ANALYSIS_MODE_OPTIONS,
        horizontal=True,
        key="backtest_analysis_mode",
        label_visibility="collapsed",
    )
    if mode == BACKTEST_ANALYSIS_MODE_COMPARE:
        render_compare_portfolio_workspace()
    else:
        if mode != BACKTEST_ANALYSIS_MODE_SINGLE:
            st.session_state.backtest_analysis_mode = BACKTEST_ANALYSIS_MODE_SINGLE
        render_single_strategy_workspace()
