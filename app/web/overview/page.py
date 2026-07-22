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


def _market_research_page_css() -> str:
    """Return page-header styles scoped to the Market Research shell."""
    return """
<style>
.st-key-market_research_page_header {
  padding-top: 0.1rem;
  padding-bottom: 0.35rem;
}
.st-key-market_research_page_header [data-testid="stCaptionContainer"] {
  margin-bottom: 0.15rem;
}
.st-key-market_research_page_header h1 {
  margin: 0;
  padding: 0;
  font-size: clamp(2.45rem, 4.8vw, 3.55rem);
  line-height: 1.05;
  letter-spacing: -0.04em;
}
@media (max-width: 480px) {
  .st-key-market_research_page_header h1 {
    font-size: clamp(2.1rem, 11vw, 2.75rem);
  }
}
</style>
"""


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
    st.markdown(_market_research_page_css(), unsafe_allow_html=True)
    with st.container(key="market_research_page_header"):
        st.caption("RESEARCH WORKSPACE")
        st.title("Market Research")
        st.caption("Today에서 발견한 질문을 시장·지수·종목 근거로 확장합니다.")

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
