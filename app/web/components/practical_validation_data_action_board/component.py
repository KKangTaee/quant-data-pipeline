from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit.components.v1 as components


_COMPONENT_NAME = "practical_validation_data_action_board"
_FRONTEND_STATIC_DIR = Path(__file__).parent / "frontend" / "component_static"

_component = (
    components.declare_component(_COMPONENT_NAME, path=str(_FRONTEND_STATIC_DIR))
    if (_FRONTEND_STATIC_DIR / "index.html").exists()
    else None
)


def is_practical_validation_data_action_board_available() -> bool:
    return _component is not None


def render_practical_validation_data_action_board(
    *,
    board: dict[str, Any],
    key: str | None = None,
) -> dict[str, Any] | None:
    """Render the optional data-action board.

    This component is UI-only. Python keeps ownership of collection planning,
    ingestion job execution, replay, gate calculation, and persistence.
    """
    if _component is None:
        return None
    value = _component(
        board=board,
        key=key,
        default=None,
    )
    return value if isinstance(value, dict) else None
