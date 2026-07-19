from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit.components.v1 as components

ECONOMIC_CYCLE_COMPONENT_NAME = "economic_cycle_workbench"
ECONOMIC_CYCLE_ROOT = (
    Path(__file__).resolve().parent.parent
    / "streamlit_components"
    / "economic_cycle_workbench"
)
ECONOMIC_CYCLE_BUILD_DIR = ECONOMIC_CYCLE_ROOT / "component_static"

_economic_cycle_component = None


def economic_cycle_component_available(build_dir: Path | None = None) -> bool:
    target = Path(build_dir) if build_dir is not None else ECONOMIC_CYCLE_BUILD_DIR
    return (target / "index.html").exists()


def _declare_economic_cycle_component():
    global _economic_cycle_component
    if not economic_cycle_component_available():
        return None
    if _economic_cycle_component is None:
        _economic_cycle_component = components.declare_component(
            ECONOMIC_CYCLE_COMPONENT_NAME,
            path=str(ECONOMIC_CYCLE_BUILD_DIR),
        )
    return _economic_cycle_component


def render_economic_cycle_component(
    payload: dict[str, Any],
    *,
    key: str = "economic_cycle_workbench",
) -> None:
    component = _declare_economic_cycle_component()
    if component is not None:
        component(payload=payload, key=key, default=None)
