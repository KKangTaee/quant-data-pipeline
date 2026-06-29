from __future__ import annotations

from typing import Any, Callable

import streamlit as st

OVERVIEW_DEEP_TAB_KEY = "overview_active_deep_tab"
OVERVIEW_DEEP_TAB_WIDGET_KEY = "overview_active_deep_tab_widget"
OVERVIEW_DEEP_TAB_QUERY_PARAM = "overview_tab"
OVERVIEW_DEEP_TAB_OPTIONS = (
    "Market Context",
    "Market Movers",
    "Futures Macro",
    "Sentiment",
    "Events",
)
OVERVIEW_DEEP_TAB_DISPLAY = {
    "Market Context": ("시장 맥락", "Market Context"),
    "Market Movers": ("변동 종목", "Market Movers"),
    "Futures Macro": ("선물 매크로", "Futures Macro"),
    "Sentiment": ("심리", "Sentiment"),
    "Events": ("일정", "Events"),
}
OVERVIEW_DEEP_TAB_SLUGS = {
    "Market Context": "market-context",
    "Market Movers": "market-movers",
    "Futures Macro": "futures-macro",
    "Sentiment": "sentiment",
    "Events": "events",
}


def _overview_active_tab_label(value: str | None) -> str:
    label = str(value or "").strip()
    if label in OVERVIEW_DEEP_TAB_OPTIONS:
        return label
    return OVERVIEW_DEEP_TAB_OPTIONS[0]


def _overview_tab_label_from_slug(value: Any) -> str | None:
    normalized = str(value or "").strip().lower()
    if not normalized:
        return None
    for label, slug in OVERVIEW_DEEP_TAB_SLUGS.items():
        if normalized == slug:
            return label
    return None


def _overview_query_tab_label() -> str | None:
    query_params = getattr(st, "query_params", None)
    if query_params is None:
        return None
    try:
        raw_value = query_params.get(OVERVIEW_DEEP_TAB_QUERY_PARAM)
    except Exception:
        return None
    if isinstance(raw_value, list):
        raw_value = raw_value[-1] if raw_value else None
    return _overview_tab_label_from_slug(raw_value)


def _overview_tab_display_label(label: str) -> str:
    active_label = _overview_active_tab_label(label)
    primary, secondary = OVERVIEW_DEEP_TAB_DISPLAY[active_label]
    return f"{primary} · {secondary}"


def _overview_tab_seed_label(
    *,
    query_label: str | None,
    widget_value: str | None,
    session_value: str | None,
) -> str:
    if widget_value in OVERVIEW_DEEP_TAB_OPTIONS:
        return _overview_active_tab_label(widget_value)
    if query_label in OVERVIEW_DEEP_TAB_OPTIONS:
        return _overview_active_tab_label(query_label)
    return _overview_active_tab_label(session_value)


def _overview_tab_nav_css() -> str:
    return (
        """
<style>
/* ov-primary-nav: scoped override for the Overview st.pills selector. */
.st-key-overview_active_deep_tab_widget [data-testid="stButtonGroup"] {
  margin: 0.42rem 0 1.08rem 0;
  padding: 0;
  border-bottom: 1px solid rgba(100, 116, 139, 0.24);
}
.st-key-overview_active_deep_tab_widget div[data-baseweb="button-group"] {
  gap: 1.45rem;
  align-items: flex-end;
}
.st-key-overview_active_deep_tab_widget [data-testid="stBaseButton-pills"],
.st-key-overview_active_deep_tab_widget [data-testid="stBaseButton-pillsActive"] {
  min-height: 2.15rem;
  padding: 0 0 0.62rem 0;
  border: 0 !important;
  border-bottom: 2px solid transparent !important;
  border-radius: 0;
  background: transparent !important;
  color: rgba(100, 116, 139, 0.95);
  color: color-mix(in srgb, var(--text-color) 70%, transparent);
  box-shadow: none !important;
  font-weight: 650;
  letter-spacing: 0;
}
.st-key-overview_active_deep_tab_widget [data-testid="stBaseButton-pillsActive"] {
  border-bottom-color: #ff4b4b !important;
  background: transparent !important;
  color: #ff4b4b !important;
  box-shadow: none !important;
}
.st-key-overview_active_deep_tab_widget [data-testid="stBaseButton-pills"]:hover {
  color: #ff4b4b;
  background: transparent !important;
}
@media (max-width: 760px) {
  .st-key-overview_active_deep_tab_widget [data-testid="stBaseButton-pills"],
  .st-key-overview_active_deep_tab_widget [data-testid="stBaseButton-pillsActive"] {
    min-height: 2.1rem;
    padding-bottom: 0.55rem;
  }
}
</style>
"""
    )


def _render_overview_tab_selector() -> str:
    current = _overview_tab_seed_label(
        query_label=_overview_query_tab_label(),
        widget_value=st.session_state.get(OVERVIEW_DEEP_TAB_WIDGET_KEY),
        session_value=st.session_state.get(OVERVIEW_DEEP_TAB_KEY),
    )

    st.markdown(_overview_tab_nav_css(), unsafe_allow_html=True)
    selected = st.pills(
        "Overview 영역",
        OVERVIEW_DEEP_TAB_OPTIONS,
        selection_mode="single",
        default=current,
        required=True,
        format_func=_overview_tab_display_label,
        key=OVERVIEW_DEEP_TAB_WIDGET_KEY,
        label_visibility="collapsed",
        width="stretch",
    )
    selected_label = _overview_active_tab_label(str(selected or current))
    st.session_state[OVERVIEW_DEEP_TAB_KEY] = selected_label
    return selected_label


def _render_selected_overview_tab(
    selected_label: str | None,
    *,
    renderers: dict[str, Callable[[], None]],
) -> None:
    active_label = _overview_active_tab_label(selected_label)
    renderer = renderers.get(active_label) or renderers.get(OVERVIEW_DEEP_TAB_OPTIONS[0])
    if callable(renderer):
        renderer()


__all__ = [
    "OVERVIEW_DEEP_TAB_DISPLAY",
    "OVERVIEW_DEEP_TAB_KEY",
    "OVERVIEW_DEEP_TAB_OPTIONS",
    "OVERVIEW_DEEP_TAB_QUERY_PARAM",
    "OVERVIEW_DEEP_TAB_SLUGS",
    "OVERVIEW_DEEP_TAB_WIDGET_KEY",
    "_overview_active_tab_label",
    "_overview_query_tab_label",
    "_overview_tab_display_label",
    "_overview_tab_label_from_slug",
    "_overview_tab_nav_css",
    "_overview_tab_seed_label",
    "_render_overview_tab_selector",
    "_render_selected_overview_tab",
]

