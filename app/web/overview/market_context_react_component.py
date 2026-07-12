from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit.components.v1 as components


MARKET_CONTEXT_VALUATION_COMPONENT_NAME = "market_context_valuation"
MARKET_CONTEXT_VALUATION_ROOT = (
    Path(__file__).resolve().parent.parent
    / "streamlit_components"
    / "market_context_valuation"
)
MARKET_CONTEXT_VALUATION_BUILD_DIR = MARKET_CONTEXT_VALUATION_ROOT / "component_static"

_market_context_valuation_component = None


def market_context_valuation_component_available(
    build_dir: Path | None = None,
) -> bool:
    target = Path(build_dir) if build_dir is not None else MARKET_CONTEXT_VALUATION_BUILD_DIR
    return (target / "index.html").exists()


def _declare_market_context_valuation_component():
    global _market_context_valuation_component
    if not market_context_valuation_component_available():
        return None
    if _market_context_valuation_component is None:
        _market_context_valuation_component = components.declare_component(
            MARKET_CONTEXT_VALUATION_COMPONENT_NAME,
            path=str(MARKET_CONTEXT_VALUATION_BUILD_DIR),
        )
    return _market_context_valuation_component


def render_market_context_valuation_component(
    payload: dict[str, Any],
    *,
    key: str = "market_context_valuation",
) -> dict[str, Any] | None:
    component = _declare_market_context_valuation_component()
    if component is None:
        return None
    value = component(payload=payload, key=key, default={"event": None})
    return value if isinstance(value, dict) else None
