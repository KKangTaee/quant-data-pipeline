from __future__ import annotations

from typing import Any, Callable

import streamlit as st

MARKET_RESEARCH_FAMILY_OPTIONS = (
    "market-environment",
    "index-valuation",
    "stock-research",
)
MARKET_RESEARCH_FAMILY_LABELS = {
    "market-environment": "시장 환경",
    "index-valuation": "지수 가치평가",
    "stock-research": "종목 리서치",
}
MARKET_RESEARCH_VIEW_OPTIONS = (
    "economic-cycle",
    "futures-macro",
    "sentiment",
    "events",
    "sp500",
    "market-movers",
    "us-stock",
)
MARKET_RESEARCH_VIEW_LABELS = {
    "economic-cycle": "경제 사이클",
    "futures-macro": "선물 매크로",
    "sentiment": "심리",
    "events": "일정",
    "sp500": "S&P 500",
    "market-movers": "변동 종목",
    "us-stock": "개별 종목",
}
MARKET_RESEARCH_VIEW_FAMILY = {
    "economic-cycle": "market-environment",
    "futures-macro": "market-environment",
    "sentiment": "market-environment",
    "events": "market-environment",
    "sp500": "index-valuation",
    "market-movers": "stock-research",
    "us-stock": "stock-research",
}
MARKET_RESEARCH_LEGACY_SLUGS = {
    "market-movers": "market-movers",
    "futures-macro": "futures-macro",
    "sentiment": "sentiment",
    "events": "events",
}
MARKET_RESEARCH_LEGACY_LABELS = {
    "market context": "economic-cycle",
    "market movers": "market-movers",
    "futures macro": "futures-macro",
    "sentiment": "sentiment",
    "events": "events",
}

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


def normalize_market_research_view(
    value: object,
    legacy_market_context_mode: object = None,
) -> str:
    """Return the canonical Market Research view for current and legacy inputs."""
    slug = str(value or "").strip().lower()
    if slug in MARKET_RESEARCH_VIEW_OPTIONS:
        return slug
    if slug == "market-context":
        legacy_mode = str(legacy_market_context_mode or "").strip().lower()
        return {
            "economic_cycle": "economic-cycle",
            "sp500": "sp500",
            "us_stock": "us-stock",
        }.get(legacy_mode, "economic-cycle")
    return MARKET_RESEARCH_LEGACY_SLUGS.get(
        slug,
        MARKET_RESEARCH_LEGACY_LABELS.get(slug, "economic-cycle"),
    )


def market_research_family_for_view(view: object) -> str:
    return MARKET_RESEARCH_VIEW_FAMILY[normalize_market_research_view(view)]


def market_research_views_for_family(family: object) -> tuple[str, ...]:
    normalized = str(family or "").strip()
    if normalized not in MARKET_RESEARCH_FAMILY_OPTIONS:
        normalized = MARKET_RESEARCH_FAMILY_OPTIONS[0]
    return tuple(
        view
        for view in MARKET_RESEARCH_VIEW_OPTIONS
        if MARKET_RESEARCH_VIEW_FAMILY[view] == normalized
    )


def market_research_default_view_for_family(family: object) -> str:
    return market_research_views_for_family(family)[0]


def resolve_market_research_seed_view(
    *,
    query_slug: object,
    applied_query_slug: object,
    widget_view: object,
    session_view: object,
    legacy_market_context_mode: object,
) -> str:
    """Resolve URL, widget, and session state without letting stale widgets win."""
    raw_query = str(query_slug or "").strip().lower()
    raw_applied = str(applied_query_slug or "").strip().lower()
    if raw_query and raw_query != raw_applied:
        return normalize_market_research_view(raw_query, legacy_market_context_mode)
    if str(widget_view or "").strip().lower() in MARKET_RESEARCH_VIEW_OPTIONS:
        return normalize_market_research_view(widget_view)
    if str(session_view or "").strip().lower() in MARKET_RESEARCH_VIEW_OPTIONS:
        return normalize_market_research_view(session_view)
    if raw_query:
        return normalize_market_research_view(raw_query, legacy_market_context_mode)
    return MARKET_RESEARCH_VIEW_OPTIONS[0]


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
    "MARKET_RESEARCH_FAMILY_LABELS",
    "MARKET_RESEARCH_FAMILY_OPTIONS",
    "MARKET_RESEARCH_LEGACY_LABELS",
    "MARKET_RESEARCH_LEGACY_SLUGS",
    "MARKET_RESEARCH_VIEW_FAMILY",
    "MARKET_RESEARCH_VIEW_LABELS",
    "MARKET_RESEARCH_VIEW_OPTIONS",
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
    "market_research_default_view_for_family",
    "market_research_family_for_view",
    "market_research_views_for_family",
    "normalize_market_research_view",
    "resolve_market_research_seed_view",
]
