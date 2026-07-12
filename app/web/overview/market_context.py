from __future__ import annotations

from app.web.overview.market_context_helpers import (
    render_market_context_header,
    render_market_context_valuation,
)


def render_market_context_tab() -> None:
    """Render the Market Context Overview tab."""
    render_market_context_header()
    render_market_context_valuation()
