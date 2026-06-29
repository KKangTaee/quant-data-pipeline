from __future__ import annotations

from app.web.overview.components.market_context import render_macro_context_cockpit
from app.web.overview.market_context_helpers import (
    load_market_context_cockpit_model,
    render_market_context_header,
    render_market_context_refresh_bar,
    render_market_context_refresh_reflection,
)


def render_market_context_tab() -> None:
    """Render the Market Context Overview tab."""
    render_market_context_header()
    render_market_context_refresh_reflection()
    cockpit_model = load_market_context_cockpit_model()
    render_macro_context_cockpit(cockpit_model, include_reading_flow=False)
    render_market_context_refresh_bar(cockpit_model)
