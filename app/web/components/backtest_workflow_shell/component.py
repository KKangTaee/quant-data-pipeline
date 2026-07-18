from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

import streamlit.components.v1 as components


_COMPONENT_NAME = "backtest_workflow_shell"
_FRONTEND_BUILD_DIR = Path(__file__).parent / "frontend" / "build"

_component = (
    components.declare_component(
        _COMPONENT_NAME,
        path=str(_FRONTEND_BUILD_DIR),
    )
    if _FRONTEND_BUILD_DIR.exists()
    else None
)


def is_backtest_workflow_shell_available() -> bool:
    return _component is not None


def render_backtest_workflow_shell_component(
    *,
    shell: dict[str, Any],
    key: str,
    on_change: Callable[[], None] | None = None,
) -> dict[str, Any] | None:
    """Render the Python-owned page shell and return a stage-selection intent."""

    if _component is None:
        return None
    value = _component(
        shell=shell,
        key=key,
        default=None,
        on_change=on_change,
    )
    return value if isinstance(value, dict) else None


__all__ = [
    "is_backtest_workflow_shell_available",
    "render_backtest_workflow_shell_component",
]
