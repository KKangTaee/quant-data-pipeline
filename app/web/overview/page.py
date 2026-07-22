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
  margin-top: -1rem;
  padding-bottom: 0.45rem;
}
.mr-market-research-page-header {
  display: grid;
  gap: 0.4rem;
  max-width: 48rem;
}
.mr-market-research-page-header__eyebrow {
  color: color-mix(in srgb, var(--text-color) 55%, transparent);
  font-size: 0.72rem;
  font-weight: 750;
  letter-spacing: 0.12em;
}
.mr-market-research-page-header h1 {
  margin: 0;
  padding: 0;
  font-size: clamp(2.45rem, 4.8vw, 3.55rem);
  line-height: 1.05;
  letter-spacing: -0.04em;
}
.mr-market-research-page-header p {
  margin: 0;
  color: color-mix(in srgb, var(--text-color) 58%, transparent);
  font-size: 0.94rem;
  line-height: 1.45;
}
@media (max-width: 480px) {
  .st-key-market_research_page_header {
    margin-top: -0.35rem;
  }
  .mr-market-research-page-header h1 {
    font-size: clamp(2.1rem, 11vw, 2.75rem);
  }
}
</style>
"""


def _market_research_header_html() -> str:
    """Return the compact, accessible Market Research page heading."""
    return (
        '<div class="mr-market-research-page-header">'
        '<span class="mr-market-research-page-header__eyebrow">RESEARCH WORKSPACE</span>'
        "<h1>Market Research</h1>"
        "<p>Today에서 발견한 질문을 시장·지수·종목 근거로 확장합니다.</p>"
        "</div>"
    )


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
        st.markdown(_market_research_header_html(), unsafe_allow_html=True)

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
