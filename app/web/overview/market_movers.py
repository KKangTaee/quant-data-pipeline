from __future__ import annotations

from app.web.overview.market_movers_helpers import (
    is_market_movers_auto_refresh_enabled,
    normalize_market_movers_refresh_mode,
    render_market_movers_auto_refresh_panel,
    render_market_movers_context_captions,
    render_market_movers_controls,
    render_market_movers_header,
    render_market_movers_snapshot,
)


def render_market_movers_tab(*, show_header: bool = True) -> None:
    """Render the Market Movers Overview tab."""
    if show_header:
        render_market_movers_header()
    controls = render_market_movers_controls()
    render_market_movers_context_captions(controls)
    normalize_market_movers_refresh_mode(controls)

    if is_market_movers_auto_refresh_enabled(controls):
        render_market_movers_auto_refresh_panel(controls)
    else:
        render_market_movers_snapshot(controls)
