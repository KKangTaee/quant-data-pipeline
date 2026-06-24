from __future__ import annotations

from app.web.overview import legacy_dashboard as _legacy


def render_sentiment_tab() -> None:
    """Render the Sentiment Overview tab through the legacy implementation."""
    _legacy._render_market_sentiment_tab()
