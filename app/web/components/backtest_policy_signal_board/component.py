from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit.components.v1 as components


_COMPONENT_NAME = "backtest_policy_signal_board"
_FRONTEND_BUILD_DIR = Path(__file__).parent / "frontend" / "build"

_component = (
    components.declare_component(_COMPONENT_NAME, path=str(_FRONTEND_BUILD_DIR))
    if _FRONTEND_BUILD_DIR.exists()
    else None
)


def is_backtest_policy_signal_board_available() -> bool:
    return _component is not None


def render_backtest_policy_signal_board(
    *,
    tone: str,
    score: str,
    headline: str,
    subhead: str,
    metrics: list[dict[str, Any]],
    first_stage_rows: list[dict[str, Any]],
    second_stage_groups: list[dict[str, Any]],
    handoff_note: str,
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
        score=score,
        headline=headline,
        subhead=subhead,
        metrics=metrics,
        firstStageRows=first_stage_rows,
        secondStageGroups=second_stage_groups,
        handoffNote=handoff_note,
        key=key,
        default=None,
    )
