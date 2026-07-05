from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit.components.v1 as components


_COMPONENT_NAME = "backtest_price_refresh_action"
_FRONTEND_BUILD_DIR = Path(__file__).parent / "frontend" / "build"

_component = (
    components.declare_component(_COMPONENT_NAME, path=str(_FRONTEND_BUILD_DIR))
    if _FRONTEND_BUILD_DIR.exists()
    else None
)


def is_backtest_price_refresh_action_available() -> bool:
    return _component is not None


def render_backtest_price_refresh_action(
    *,
    status_label: str,
    tone: str,
    summary: str,
    detail: str,
    metric_items: list[dict[str, Any]],
    action_text: str,
    button_label: str,
    action_note: str,
    disabled: bool,
    key: str | None = None,
) -> dict[str, Any] | None:
    """Render the optional React price-refresh card when its frontend build exists.

    The component is UI-only. Python owns the OHLCV ingestion call, rerun, and
    session feedback so the browser component never mutates application state
    directly.
    """
    if _component is None:
        return None
    value = _component(
        statusLabel=status_label,
        tone=tone,
        summary=summary,
        detail=detail,
        metricItems=metric_items,
        actionText=action_text,
        buttonLabel=button_label,
        actionNote=action_note,
        disabled=disabled,
        key=key,
        default=None,
    )
    return value if isinstance(value, dict) else None
