from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit.components.v1 as components


SENTIMENT_REACT_COMPONENT_NAME = "sentiment_workbench"
SENTIMENT_REACT_COMPONENT_ROOT = (
    Path(__file__).resolve().parent.parent
    / "streamlit_components"
    / "sentiment_workbench"
)
SENTIMENT_REACT_BUILD_DIR = SENTIMENT_REACT_COMPONENT_ROOT / "component_static"

_sentiment_component = None


def sentiment_react_component_available(build_dir: Path | None = None) -> bool:
    target = Path(build_dir) if build_dir is not None else SENTIMENT_REACT_BUILD_DIR
    return (target / "index.html").exists()


def _declare_sentiment_component():
    global _sentiment_component
    if not sentiment_react_component_available():
        return None
    if _sentiment_component is None:
        _sentiment_component = components.declare_component(
            SENTIMENT_REACT_COMPONENT_NAME,
            path=str(SENTIMENT_REACT_BUILD_DIR),
        )
    return _sentiment_component


def render_sentiment_react_workbench(
    payload: dict[str, Any],
    *,
    key: str = "sentiment_workbench",
) -> dict[str, Any] | None:
    component = _declare_sentiment_component()
    if component is None:
        return None
    value = component(payload=payload, key=key, default={"event": None})
    return value if isinstance(value, dict) else None
