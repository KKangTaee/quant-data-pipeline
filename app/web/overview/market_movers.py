from __future__ import annotations

from app.web.overview import legacy_dashboard as _legacy


def render_market_movers_tab() -> None:
    """Render the Market Movers Overview tab through the legacy implementation."""
    _legacy._render_market_movers_tab()
