from __future__ import annotations

from typing import Any, Callable

import streamlit as st

from app.web.overview.market_context_helpers import (
    render_economic_cycle,
    render_market_context_header,
    render_market_context_valuation,
)

MARKET_CONTEXT_MODE_KEY = "overview_market_context_mode"
DEFAULT_MARKET_CONTEXT_MODE = "economic_cycle"
MARKET_CONTEXT_MODE_OPTIONS = (
    ("economic_cycle", "경제 사이클"),
    ("sp500", "S&P 500"),
    ("us_stock", "미국 개별주식"),
)
MARKET_CONTEXT_MODE_LABELS = dict(MARKET_CONTEXT_MODE_OPTIONS)


def normalize_market_context_mode(value: object) -> str:
    normalized = str(value or "").strip()
    return (
        normalized
        if normalized in MARKET_CONTEXT_MODE_LABELS
        else DEFAULT_MARKET_CONTEXT_MODE
    )


def render_market_context_mode_selector(*, state: Any = None) -> str:
    resolved_state = state if state is not None else st.session_state
    raw_value = resolved_state.get(MARKET_CONTEXT_MODE_KEY)
    current = normalize_market_context_mode(raw_value)
    if raw_value not in MARKET_CONTEXT_MODE_LABELS and MARKET_CONTEXT_MODE_KEY in resolved_state:
        del resolved_state[MARKET_CONTEXT_MODE_KEY]
    widget_options: dict[str, object] = {}
    if MARKET_CONTEXT_MODE_KEY not in resolved_state:
        widget_options["default"] = current
    selected = st.segmented_control(
        "시장 맥락 보기",
        options=[item[0] for item in MARKET_CONTEXT_MODE_OPTIONS],
        format_func=lambda value: MARKET_CONTEXT_MODE_LABELS[str(value)],
        key=MARKET_CONTEXT_MODE_KEY,
        label_visibility="collapsed",
        **widget_options,
    )
    return normalize_market_context_mode(selected or current)


def render_market_context_content(
    mode: object,
    *,
    cycle_renderer: Callable[[], None] = render_economic_cycle,
    valuation_renderer: Callable[..., None] = render_market_context_valuation,
) -> str:
    normalized = normalize_market_context_mode(mode)
    if normalized == "economic_cycle":
        cycle_renderer()
    else:
        valuation_renderer(
            default_instrument=normalized,
            show_instrument_selector=False,
        )
    return normalized


def render_market_context_tab() -> None:
    """Render the Market Context Overview tab."""
    render_market_context_header()
    mode = render_market_context_mode_selector()
    render_market_context_content(mode)
