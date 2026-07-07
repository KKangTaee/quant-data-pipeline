from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit.components.v1 as components


EVENTS_REACT_COMPONENT_NAME = "events_workbench"
EVENTS_REACT_COMPONENT_ROOT = (
    Path(__file__).resolve().parent.parent
    / "streamlit_components"
    / "events_workbench"
)
EVENTS_REACT_BUILD_DIR = EVENTS_REACT_COMPONENT_ROOT / "component_static"

_events_component = None


def events_react_component_available(build_dir: Path | None = None) -> bool:
    target = Path(build_dir) if build_dir is not None else EVENTS_REACT_BUILD_DIR
    return (target / "index.html").exists()


def _declare_events_component():
    global _events_component
    if not events_react_component_available():
        return None
    if _events_component is None:
        _events_component = components.declare_component(
            EVENTS_REACT_COMPONENT_NAME,
            path=str(EVENTS_REACT_BUILD_DIR),
        )
    return _events_component


def render_events_react_workbench(
    payload: dict[str, Any],
    *,
    key: str = "events_workbench",
) -> dict[str, Any] | None:
    component = _declare_events_component()
    if component is None:
        return None
    value = component(payload=payload, key=key, default={"event": None})
    return value if isinstance(value, dict) else None
