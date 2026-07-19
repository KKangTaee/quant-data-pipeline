from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit.components.v1 as components


_COMPONENT_NAME = "backtest_policy_signal_board"
_FRONTEND_STATIC_DIR = Path(__file__).parent / "frontend" / "component_static"

_component = (
    components.declare_component(_COMPONENT_NAME, path=str(_FRONTEND_STATIC_DIR))
    if (_FRONTEND_STATIC_DIR / "index.html").exists()
    else None
)


def is_backtest_policy_signal_board_available() -> bool:
    return _component is not None


def render_backtest_policy_signal_board(
    *,
    tone: str,
    headline: str,
    subhead: str,
    metrics: list[dict[str, Any]],
    first_stage_rows: list[dict[str, Any]],
    key: str | None = None,
) -> None:
    """Render the optional React policy board when its frontend build exists.

    The component is intentionally UI-only. Python service code owns policy
    classification, gate math, source registration, and persistence.
    """
    if _component is None:
        return
    _component(
        tone=tone,
        headline=headline,
        subhead=subhead,
        metrics=metrics,
        firstStageRows=first_stage_rows,
        key=key,
        default=None,
    )
