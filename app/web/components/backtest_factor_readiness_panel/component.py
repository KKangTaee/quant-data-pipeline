from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit.components.v1 as components


_COMPONENT_NAME = "backtest_factor_readiness_panel"
_FRONTEND_BUILD_DIR = Path(__file__).parent / "frontend" / "build"

_component = (
    components.declare_component(_COMPONENT_NAME, path=str(_FRONTEND_BUILD_DIR))
    if _FRONTEND_BUILD_DIR.exists()
    else None
)


def is_backtest_factor_readiness_panel_available() -> bool:
    return _component is not None


def render_backtest_factor_readiness_panel(
    *,
    status: str,
    tone: str,
    headline: str,
    summary: str,
    strategy_label: str,
    run_recommended: bool,
    checks: list[dict[str, Any]],
    actions: list[dict[str, Any]],
    key: str | None = None,
) -> dict[str, Any] | None:
    """Render the optional strict factor readiness React panel when its frontend build exists."""
    if _component is None:
        return None
    value = _component(
        status=status,
        tone=tone,
        headline=headline,
        summary=summary,
        strategyLabel=strategy_label,
        runRecommended=run_recommended,
        checks=checks,
        actions=actions,
        key=key,
        default=None,
    )
    return value if isinstance(value, dict) else None
