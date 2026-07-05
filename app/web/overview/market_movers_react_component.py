from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit.components.v1 as components


MARKET_MOVERS_REACT_COMPONENT_NAME = "market_movers_workbench"
MARKET_MOVERS_REACT_COMPONENT_ROOT = (
    Path(__file__).resolve().parent.parent
    / "streamlit_components"
    / "market_movers_workbench"
)
MARKET_MOVERS_REACT_BUILD_DIR = MARKET_MOVERS_REACT_COMPONENT_ROOT / "component_static"

_market_movers_component = None


def market_movers_react_component_available(build_dir: Path | None = None) -> bool:
    target = Path(build_dir) if build_dir is not None else MARKET_MOVERS_REACT_BUILD_DIR
    return (target / "index.html").exists()


def _declare_market_movers_component():
    global _market_movers_component
    if not market_movers_react_component_available():
        return None
    if _market_movers_component is None:
        _market_movers_component = components.declare_component(
            MARKET_MOVERS_REACT_COMPONENT_NAME,
            path=str(MARKET_MOVERS_REACT_BUILD_DIR),
        )
    return _market_movers_component


def _render_market_movers_react_component(
    payload: dict[str, Any],
    *,
    key: str,
) -> dict[str, Any] | None:
    component = _declare_market_movers_component()
    if component is None:
        return None
    value = component(payload=payload, key=key, default={"event": None})
    return value if isinstance(value, dict) else None


def render_market_movers_react_workbench(
    payload: dict[str, Any],
    *,
    key: str = "market_movers_workbench",
) -> dict[str, Any] | None:
    return _render_market_movers_react_component(payload, key=key)


def render_market_mover_investigation_pane_react(
    payload: dict[str, Any],
    *,
    key: str = "market_mover_investigation_pane",
) -> dict[str, Any] | None:
    return _render_market_movers_react_component(payload, key=key)


def render_market_movers_sector_breadth_react(
    payload: dict[str, Any],
    *,
    key: str = "market_movers_sector_breadth",
) -> dict[str, Any] | None:
    return _render_market_movers_react_component(payload, key=key)
