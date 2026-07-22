from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit.components.v1 as components


MARKET_RESEARCH_NAVIGATION_COMPONENT_NAME = "market_research_navigation"
MARKET_RESEARCH_NAVIGATION_COMPONENT_ROOT = (
    Path(__file__).resolve().parent.parent
    / "streamlit_components"
    / "market_research_navigation"
)
MARKET_RESEARCH_NAVIGATION_BUILD_DIR = (
    MARKET_RESEARCH_NAVIGATION_COMPONENT_ROOT / "component_static"
)

_market_research_navigation_component = None


def market_research_navigation_react_component_available(
    build_dir: Path | None = None,
) -> bool:
    target = Path(build_dir) if build_dir is not None else MARKET_RESEARCH_NAVIGATION_BUILD_DIR
    return (target / "index.html").exists()


def _declare_market_research_navigation_component():
    global _market_research_navigation_component
    if not market_research_navigation_react_component_available():
        return None
    if _market_research_navigation_component is None:
        _market_research_navigation_component = components.declare_component(
            MARKET_RESEARCH_NAVIGATION_COMPONENT_NAME,
            path=str(MARKET_RESEARCH_NAVIGATION_BUILD_DIR),
        )
    return _market_research_navigation_component


def render_market_research_navigation(
    payload: dict[str, Any],
    *,
    key: str = "market_research_navigation",
) -> dict[str, Any] | None:
    component = _declare_market_research_navigation_component()
    if component is None:
        return None
    value = component(payload=payload, key=key, default={"event": None})
    return value if isinstance(value, dict) else None


__all__ = [
    "MARKET_RESEARCH_NAVIGATION_BUILD_DIR",
    "market_research_navigation_react_component_available",
    "render_market_research_navigation",
]
