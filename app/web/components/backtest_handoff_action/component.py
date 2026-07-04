from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit.components.v1 as components


_COMPONENT_NAME = "backtest_handoff_action"
_FRONTEND_BUILD_DIR = Path(__file__).parent / "frontend" / "build"

_component = (
    components.declare_component(_COMPONENT_NAME, path=str(_FRONTEND_BUILD_DIR))
    if _FRONTEND_BUILD_DIR.exists()
    else None
)


def render_backtest_handoff_action(
    *,
    status_label: str,
    tone: str,
    button_label: str,
    disabled: bool,
    review_count: int,
    blocker_count: int,
    boundary_text: str,
    key: str | None = None,
) -> dict[str, Any] | None:
    """Render the optional React action card when its frontend build exists.

    The component is intentionally UI-only. Python remains responsible for
    source registration, registry writes, reruns, and backtest/runtime calls.
    """
    if _component is None:
        return None
    value = _component(
        statusLabel=status_label,
        tone=tone,
        buttonLabel=button_label,
        disabled=disabled,
        reviewCount=review_count,
        blockerCount=blocker_count,
        boundaryText=boundary_text,
        key=key,
        default=None,
    )
    return value if isinstance(value, dict) else None
