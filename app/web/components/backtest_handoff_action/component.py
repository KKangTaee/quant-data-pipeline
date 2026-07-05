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


def is_backtest_handoff_action_available() -> bool:
    return _component is not None


def render_backtest_handoff_action(
    *,
    status_label: str,
    tone: str,
    summary: str,
    reason_title: str,
    reasons: list[str],
    entry_cards: list[dict[str, Any]],
    action_text: str,
    button_label: str,
    disabled: bool,
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
        summary=summary,
        reasonTitle=reason_title,
        reasons=reasons,
        entryCards=entry_cards,
        actionText=action_text,
        buttonLabel=button_label,
        disabled=disabled,
        boundaryText=boundary_text,
        key=key,
        default=None,
    )
    return value if isinstance(value, dict) else None
