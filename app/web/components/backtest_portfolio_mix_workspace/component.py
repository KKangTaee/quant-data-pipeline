from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

import streamlit.components.v1 as components


_COMPONENT_NAME = "backtest_portfolio_mix_workspace"
_FRONTEND_STATIC_DIR = Path(__file__).parent / "frontend" / "component_static"

_component = (
    components.declare_component(
        _COMPONENT_NAME,
        path=str(_FRONTEND_STATIC_DIR),
    )
    if (_FRONTEND_STATIC_DIR / "index.html").exists()
    else None
)


def is_backtest_portfolio_mix_workspace_available() -> bool:
    return _component is not None


def render_backtest_portfolio_mix_workspace_component(
    *,
    workspace: dict[str, Any],
    key: str,
    on_change: Callable[[], None] | None = None,
) -> dict[str, Any] | None:
    """Render the Python-owned Mix read model and return presentation intent."""

    if _component is None:
        return None
    value = _component(
        workspace=workspace,
        key=key,
        default=None,
        on_change=on_change,
    )
    return value if isinstance(value, dict) else None


__all__ = [
    "is_backtest_portfolio_mix_workspace_available",
    "render_backtest_portfolio_mix_workspace_component",
]
