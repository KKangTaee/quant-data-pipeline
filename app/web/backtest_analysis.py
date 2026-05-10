from __future__ import annotations

import streamlit as st

from app.web.backtest_compare import render_compare_portfolio_workspace
from app.web.backtest_single_strategy import render_single_strategy_workspace
from app.web.backtest_workflow_routes import (
    BACKTEST_ANALYSIS_MODE_COMPARE,
    BACKTEST_ANALYSIS_MODE_OPTIONS,
    BACKTEST_ANALYSIS_MODE_SINGLE,
)


def render_backtest_analysis_workspace() -> None:
    st.markdown("### Backtest Analysis")
    st.caption(
        "Single Strategy 실행, Compare, 저장된 비중 조합 replay를 통해 후보를 만들고 "
        "Practical Validation으로 보낼 source를 선택합니다."
    )
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
