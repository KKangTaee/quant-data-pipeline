from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Literal

import streamlit.components.v1 as components


_COMPONENT_NAME = "backtest_analysis_decision_workspace"
_FRONTEND_BUILD_DIR = Path(__file__).parent / "frontend" / "build"

_component = (
    components.declare_component(
        _COMPONENT_NAME,
        path=str(_FRONTEND_BUILD_DIR),
    )
    if _FRONTEND_BUILD_DIR.exists()
    else None
)


def is_backtest_analysis_decision_workspace_available() -> bool:
    return _component is not None


def render_backtest_analysis_decision_workspace(
    *,
    workspace: dict[str, Any],
    surface: Literal["context", "decision"],
    key: str,
    on_change: Callable[[], None] | None = None,
) -> dict[str, Any] | None:
    """Render the Python-owned Level1 projection and return presentation intent."""

    if _component is None:
        return None
    value = _component(
        workspace=workspace,
        surface=surface,
        key=key,
        default=None,
        on_change=on_change,
    )
    return value if isinstance(value, dict) else None
