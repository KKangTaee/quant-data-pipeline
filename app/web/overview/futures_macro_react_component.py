from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit.components.v1 as components


FUTURES_MACRO_REACT_COMPONENT_NAME = "futures_macro_workbench"
FUTURES_MACRO_REACT_COMPONENT_ROOT = (
    Path(__file__).resolve().parent.parent
    / "streamlit_components"
    / "futures_macro_workbench"
)
FUTURES_MACRO_REACT_BUILD_DIR = FUTURES_MACRO_REACT_COMPONENT_ROOT / "component_static"

_futures_macro_component = None


def futures_macro_react_component_available(build_dir: Path | None = None) -> bool:
    target = Path(build_dir) if build_dir is not None else FUTURES_MACRO_REACT_BUILD_DIR
    return (target / "index.html").exists()


def _declare_futures_macro_component():
    global _futures_macro_component
    if not futures_macro_react_component_available():
        return None
    if _futures_macro_component is None:
        _futures_macro_component = components.declare_component(
            FUTURES_MACRO_REACT_COMPONENT_NAME,
            path=str(FUTURES_MACRO_REACT_BUILD_DIR),
        )
    return _futures_macro_component


def render_futures_macro_react_workbench(
    payload: dict[str, Any],
    *,
    key: str = "futures_macro_workbench",
) -> dict[str, Any] | None:
    component = _declare_futures_macro_component()
    if component is None:
        return None
    value = component(payload=payload, key=key, default={"event": None})
    return value if isinstance(value, dict) else None
