from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit.components.v1 as components


_COMPONENT_NAME = "practical_validation_fix_queue"
_FRONTEND_BUILD_DIR = Path(__file__).parent / "frontend" / "build"

_component = (
    components.declare_component(_COMPONENT_NAME, path=str(_FRONTEND_BUILD_DIR))
    if _FRONTEND_BUILD_DIR.exists()
    else None
)


def is_practical_validation_fix_queue_available() -> bool:
    return _component is not None


def render_practical_validation_fix_queue(
    *,
    status_label: str,
    tone: str,
    verdict: str,
    next_action: str,
    can_save_and_move: bool,
    fix_items: list[dict[str, Any]],
    core_groups: list[dict[str, Any]],
    criteria_groups: list[dict[str, Any]],
    key: str | None = None,
) -> dict[str, Any] | None:
    """Render the optional Practical Validation read model surface.

    This component is UI-only. Python keeps ownership of validation execution,
    gate calculation, registry writes, and Final Review handoff.
    """
    if _component is None:
        return None
    value = _component(
        statusLabel=status_label,
        tone=tone,
        verdict=verdict,
        nextAction=next_action,
        canSaveAndMove=can_save_and_move,
        fixItems=fix_items,
        coreGroups=core_groups,
        criteriaGroups=criteria_groups or [],
        key=key,
        default=None,
    )
    return value if isinstance(value, dict) else None
