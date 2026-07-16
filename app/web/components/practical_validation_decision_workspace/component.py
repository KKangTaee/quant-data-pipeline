from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit.components.v1 as components


_COMPONENT_NAME = "practical_validation_decision_workspace"
_FRONTEND_BUILD_DIR = Path(__file__).parent / "frontend" / "build"

_component = (
    components.declare_component(
        _COMPONENT_NAME,
        path=str(_FRONTEND_BUILD_DIR),
    )
    if _FRONTEND_BUILD_DIR.exists()
    else None
)


def is_practical_validation_decision_workspace_available() -> bool:
    return _component is not None


def render_practical_validation_decision_workspace(
    *,
    workspace: dict[str, Any],
    key: str | None = None,
) -> dict[str, Any] | None:
    """Render the Python-owned Level2 projection and return presentation intent."""

    if _component is None:
        return None
    value = _component(
        workspace=workspace,
        key=key,
        default=None,
    )
    return value if isinstance(value, dict) else None
