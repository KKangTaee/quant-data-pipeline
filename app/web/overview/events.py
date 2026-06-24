from __future__ import annotations

from app.web.overview import legacy_dashboard as _legacy


def render_events_tab() -> None:
    """Render the Events Overview tab through the legacy implementation."""
    _legacy._render_events_tab()
