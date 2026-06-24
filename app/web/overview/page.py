from __future__ import annotations

from datetime import datetime
from typing import Any, Callable

import streamlit as st

from app.web.overview import legacy_dashboard as _legacy
from app.web.overview.components.layout import render_market_session_banner
from app.web.overview.events import render_events_tab
from app.web.overview.futures_macro import render_futures_macro_tab
from app.web.overview.market_context import render_market_context_tab
from app.web.overview.market_movers import render_market_movers_tab
from app.web.overview.navigation import (
    _render_overview_tab_selector,
    _render_selected_overview_tab,
)
from app.web.overview.sentiment import render_sentiment_tab


def render_overview_dashboard(
    *,
    runtime_marker: str,
    loaded_at: datetime,
    git_sha: str | None,
    latest_result: dict[str, Any] | None = None,
    recent_results: list[dict[str, Any]] | None = None,
    render_runtime_snapshot: Callable[[], None] | None = None,
) -> None:
    """Render the top-level product dashboard for Workspace > Overview."""
    del runtime_marker, loaded_at, git_sha, latest_result, recent_results, render_runtime_snapshot
    st.title("Overview")
    st.caption("저장된 시장 자료를 브리프처럼 읽고, 필요한 세부 근거는 각 탭에서 이어서 확인합니다.")
    render_market_session_banner(_legacy._market_session_banner_model())

    active_tab = _render_overview_tab_selector()
    _render_selected_overview_tab(
        active_tab,
        renderers={
            "Market Context": render_market_context_tab,
            "Market Movers": render_market_movers_tab,
            "Futures Macro": render_futures_macro_tab,
            "Sentiment": render_sentiment_tab,
            "Events": render_events_tab,
        },
    )
