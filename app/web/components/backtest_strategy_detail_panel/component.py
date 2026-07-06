from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit.components.v1 as components


_COMPONENT_NAME = "backtest_strategy_detail_panel"
_FRONTEND_BUILD_DIR = Path(__file__).parent / "frontend" / "build"
_FRONTEND_INDEX_PATH = _FRONTEND_BUILD_DIR / "index.html"

_component = (
    components.declare_component(_COMPONENT_NAME, path=str(_FRONTEND_BUILD_DIR))
    if _FRONTEND_INDEX_PATH.exists()
    else None
)


def is_backtest_strategy_detail_panel_available() -> bool:
    return _component is not None


def render_backtest_strategy_detail_panel(
    *,
    detail_model: dict[str, Any],
    key: str | None = None,
) -> None:
    """Render the optional React strategy detail panel when its frontend build exists."""
    if _component is None:
        return
    _component(
        detailModel=detail_model,
        key=key,
        default=None,
    )
