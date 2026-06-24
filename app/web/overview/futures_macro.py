from __future__ import annotations

from app.web.overview import legacy_dashboard as _legacy


def render_futures_macro_tab() -> None:
    """Render the Futures Macro Overview tab through the legacy implementation."""
    _legacy._render_futures_macro_tab()
