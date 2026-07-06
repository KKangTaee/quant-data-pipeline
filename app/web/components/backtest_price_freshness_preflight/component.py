from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit.components.v1 as components


_COMPONENT_NAME = "backtest_price_freshness_preflight"
_FRONTEND_BUILD_DIR = Path(__file__).parent / "frontend" / "build"

_component = (
    components.declare_component(_COMPONENT_NAME, path=str(_FRONTEND_BUILD_DIR))
    if _FRONTEND_BUILD_DIR.exists()
    else None
)


def is_backtest_price_freshness_preflight_available() -> bool:
    return _component is not None


def render_backtest_price_freshness_preflight(
    *,
    status_label: str,
    tone: str,
    headline: str,
    summary: str,
    detail: str,
    metric_items: list[dict[str, Any]],
    issue_rows: list[dict[str, Any]],
    next_action: str,
    footnote: str,
    key: str | None = None,
) -> None:
    """Render the optional React preflight card when its frontend build exists."""
    if _component is None:
        return
    _component(
        statusLabel=status_label,
        tone=tone,
        headline=headline,
        summary=summary,
        detail=detail,
        metricItems=metric_items,
        issueRows=issue_rows,
        nextAction=next_action,
        footnote=footnote,
        key=key,
        default=None,
    )
