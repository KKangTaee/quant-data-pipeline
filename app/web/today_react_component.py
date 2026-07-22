from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit.components.v1 as components


TODAY_REACT_COMPONENT_NAME = "today_workbench"
TODAY_REACT_COMPONENT_ROOT = (
    Path(__file__).resolve().parent / "streamlit_components" / "today_workbench"
)
TODAY_REACT_BUILD_DIR = TODAY_REACT_COMPONENT_ROOT / "component_static"

_today_component = None


def today_react_component_available(build_dir: Path | None = None) -> bool:
    """Return whether the deployable Today React bundle is present."""

    target = Path(build_dir) if build_dir is not None else TODAY_REACT_BUILD_DIR
    return (target / "index.html").exists()


def _declare_today_component():
    global _today_component
    if not today_react_component_available():
        return None
    if _today_component is None:
        _today_component = components.declare_component(
            TODAY_REACT_COMPONENT_NAME,
            path=str(TODAY_REACT_BUILD_DIR),
        )
    return _today_component


def render_today_workbench(
    payload: dict[str, Any],
    *,
    key: str = "today_workbench",
) -> dict[str, Any] | None:
    """Render Today and return its small navigation-event envelope."""

    component = _declare_today_component()
    if component is None:
        return None
    value = component(
        payload=payload,
        key=key,
        default={"event": None},
    )
    return value if isinstance(value, dict) else None


__all__ = [
    "TODAY_REACT_BUILD_DIR",
    "render_today_workbench",
    "today_react_component_available",
]
