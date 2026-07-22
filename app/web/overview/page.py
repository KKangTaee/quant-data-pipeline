from __future__ import annotations

from datetime import datetime
from typing import Any, Callable

import streamlit as st

from app.web.overview.events import render_events_tab
from app.web.overview.futures_macro import render_futures_macro_tab
from app.web.overview.market_context_helpers import (
    render_economic_cycle,
    render_market_context_valuation,
)
from app.web.overview.market_movers import render_market_movers_tab
from app.web.overview.navigation import (
    _render_market_research_selector,
    _render_selected_market_research_view,
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
    """Render the Market Research workspace."""
    del runtime_marker, loaded_at, git_sha, latest_result, recent_results, render_runtime_snapshot
    st.caption("MARKET RESEARCH")
    st.title("Market Research")
    st.caption("Today에서 확인한 시장 판단을 환경·가치평가·종목 근거로 확장합니다.")

    active_view = _render_market_research_selector()
    _render_selected_market_research_view(
        active_view,
        renderers={
            "economic-cycle": render_economic_cycle,
            "futures-macro": lambda: render_futures_macro_tab(show_header=False),
            "sentiment": lambda: render_sentiment_tab(show_header=False),
            "events": lambda: render_events_tab(show_header=False),
            "sp500": lambda: render_market_context_valuation(
                default_instrument="sp500",
                show_instrument_selector=False,
            ),
            "market-movers": lambda: render_market_movers_tab(show_header=False),
            "us-stock": lambda: render_market_context_valuation(
                default_instrument="us_stock",
                show_instrument_selector=False,
            ),
        },
    )
