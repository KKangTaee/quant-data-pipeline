from __future__ import annotations

from app.web.overview import legacy_dashboard as _legacy


def render_market_context_tab() -> None:
    """Render the Market Context Overview tab through the legacy implementation."""
    _legacy._render_overview_market_context_tab()
