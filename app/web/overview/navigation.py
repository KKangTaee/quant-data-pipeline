from __future__ import annotations

from html import escape
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
MARKET_RESEARCH_FAMILY_DESCRIPTIONS = {
    "market-environment": "경제·매크로·심리·일정",
    "index-valuation": "대표지수 멀티플과 실적",
    "stock-research": "변동 종목과 개별 기업",
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
MARKET_RESEARCH_VIEW_KEY = "market_research_active_view"
MARKET_RESEARCH_FAMILY_WIDGET_KEY = "market_research_family_widget"
MARKET_RESEARCH_VIEW_WIDGET_KEY = "market_research_view_widget"
MARKET_RESEARCH_APPLIED_QUERY_KEY = "market_research_applied_query"
MARKET_RESEARCH_LOCAL_NAV_KEY = "market_research_local_navigation"

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


def market_research_local_navigation_context(
    family: object,
) -> tuple[str, tuple[str, ...]]:
    """Return the visible family label and canonical child views."""
    normalized = str(family or "").strip()
    if normalized not in MARKET_RESEARCH_FAMILY_OPTIONS:
        normalized = MARKET_RESEARCH_FAMILY_OPTIONS[0]
    return (
        MARKET_RESEARCH_FAMILY_LABELS[normalized],
        market_research_views_for_family(normalized),
    )


def market_research_default_view_for_family(family: object) -> str:
    return market_research_views_for_family(family)[0]


def build_market_research_navigation_payload(active_view: object) -> dict[str, object]:
    """Build the presentation-only React navigation payload."""
    canonical = normalize_market_research_view(active_view)
    families = []
    for family in MARKET_RESEARCH_FAMILY_OPTIONS:
        families.append(
            {
                "id": family,
                "label": MARKET_RESEARCH_FAMILY_LABELS[family],
                "description": MARKET_RESEARCH_FAMILY_DESCRIPTIONS[family],
                "views": [
                    {"id": view, "label": MARKET_RESEARCH_VIEW_LABELS[view]}
                    for view in market_research_views_for_family(family)
                ],
            }
        )
    return {
        "schema_version": "market_research_navigation_v1",
        "eyebrow": "RESEARCH WORKSPACE",
        "title": "Market Research",
        "description": "Today에서 발견한 질문을 시장·지수·종목 근거로 확장합니다.",
        "active_family": market_research_family_for_view(canonical),
        "active_view": canonical,
        "families": families,
    }


def resolve_market_research_navigation_event(
    current_view: object,
    component_value: object,
) -> str:
    """Accept only a canonical React navigation selection event."""
    canonical = normalize_market_research_view(current_view)
    if not isinstance(component_value, dict):
        return canonical
    event = component_value.get("event")
    if not isinstance(event, dict) or event.get("id") != "select_view":
        return canonical
    candidate = str(event.get("view") or "").strip().lower()
    return candidate if candidate in MARKET_RESEARCH_VIEW_OPTIONS else canonical


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


def _market_research_query_slug() -> str | None:
    query_params = getattr(st, "query_params", None)
    if query_params is None:
        return None
    try:
        raw = query_params.get(OVERVIEW_DEEP_TAB_QUERY_PARAM)
    except Exception:
        return None
    if isinstance(raw, list):
        raw = raw[-1] if raw else None
    value = str(raw or "").strip().lower()
    return value or None


def _store_market_research_view(view: str) -> str:
    canonical = normalize_market_research_view(view)
    st.session_state[MARKET_RESEARCH_VIEW_KEY] = canonical
    st.session_state[MARKET_RESEARCH_APPLIED_QUERY_KEY] = canonical
    try:
        st.query_params[OVERVIEW_DEEP_TAB_QUERY_PARAM] = canonical
    except Exception:
        pass
    return canonical


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


def _market_research_navigation_css() -> str:
    return """
<style>
.st-key-market_research_family_widget div[data-baseweb="button-group"] {
  display: flex;
  width: fit-content;
  max-width: 100%;
  gap: 0.25rem;
  padding: 0;
  border-bottom: 1px solid color-mix(in srgb, var(--text-color) 14%, transparent);
}
.st-key-market_research_family_widget button {
  width: auto !important;
  min-height: 2.35rem;
  padding: 0.4rem 0.75rem !important;
  border: 0 !important;
  border-bottom: 2px solid transparent !important;
  border-radius: 0 !important;
  background: transparent !important;
  color: color-mix(in srgb, var(--text-color) 66%, transparent) !important;
  box-shadow: none !important;
}
.st-key-market_research_family_widget button:hover {
  color: var(--text-color) !important;
  background: color-mix(in srgb, #7c96ad 7%, transparent) !important;
}
.st-key-market_research_family_widget [data-testid="stBaseButton-segmented_controlActive"] {
  color: var(--text-color) !important;
  font-weight: 700 !important;
  border-bottom-color: #647b8f !important;
  background: transparent !important;
}
.st-key-market_research_local_navigation {
  margin: 0.15rem 0 0.7rem;
  padding: 0.8rem 0.95rem;
  border: 1px solid color-mix(in srgb, #7c96ad 26%, transparent) !important;
  border-radius: 0.85rem;
  background: color-mix(in srgb, #dce7ef 34%, var(--background-color));
}
.mr-market-research-local-label {
  display: grid;
  flex: 0 0 9.4rem;
  min-width: 9.4rem;
  gap: 0.12rem;
  line-height: 1.25;
}
.mr-market-research-local-label span {
  color: color-mix(in srgb, var(--text-color) 52%, transparent);
  font-size: 0.69rem;
  font-weight: 650;
  letter-spacing: 0.04em;
}
.mr-market-research-local-label strong {
  color: var(--text-color);
  font-size: 0.9rem;
  font-weight: 720;
}
.st-key-market_research_view_widget div[data-baseweb="button-group"] {
  display: flex;
  width: fit-content;
  max-width: 100%;
  flex-wrap: wrap;
  gap: 0.35rem;
}
.st-key-market_research_view_widget [data-testid="stBaseButton-pills"],
.st-key-market_research_view_widget [data-testid="stBaseButton-pillsActive"] {
  width: auto;
  min-height: 2.2rem;
  padding: 0.35rem 0.7rem;
  border-radius: 999px;
  box-shadow: none !important;
}
.st-key-market_research_view_widget [data-testid="stBaseButton-pills"] {
  border: 1px solid transparent !important;
  background: transparent !important;
  color: color-mix(in srgb, var(--text-color) 70%, transparent) !important;
}
.st-key-market_research_view_widget [data-testid="stBaseButton-pillsActive"] {
  border: 1px solid color-mix(in srgb, #647b8f 34%, transparent) !important;
  background: color-mix(in srgb, #b9ccda 30%, var(--background-color)) !important;
  color: var(--text-color) !important;
  font-weight: 700 !important;
}
@media (max-width: 760px) {
  .st-key-market_research_local_navigation [data-testid="stHorizontalBlock"] {
    flex-wrap: wrap;
  }
}
@media (max-width: 480px) {
  .st-key-market_research_family_widget div[data-baseweb="button-group"] {
    display: grid;
    width: 100%;
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
  .st-key-market_research_family_widget button {
    width: 100% !important;
    padding-inline: 0.3rem !important;
    white-space: normal;
  }
  .st-key-market_research_view_widget div[data-baseweb="button-group"] {
    display: grid;
    width: 100%;
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .st-key-market_research_view_widget [data-testid="stBaseButton-pills"],
  .st-key-market_research_view_widget [data-testid="stBaseButton-pillsActive"] {
    width: 100%;
  }
  .st-key-market_research_view_widget button:only-child {
    grid-column: 1 / -1;
  }
}
</style>
"""


def _render_market_research_selector() -> str:
    query_slug = _market_research_query_slug()
    applied_query = st.session_state.get(MARKET_RESEARCH_APPLIED_QUERY_KEY)
    query_changed = bool(query_slug and query_slug != applied_query)
    if query_changed:
        st.session_state.pop(MARKET_RESEARCH_FAMILY_WIDGET_KEY, None)
        st.session_state.pop(MARKET_RESEARCH_VIEW_WIDGET_KEY, None)

    current_view = resolve_market_research_seed_view(
        query_slug=query_slug,
        applied_query_slug=applied_query,
        widget_view=st.session_state.get(MARKET_RESEARCH_VIEW_WIDGET_KEY),
        session_view=st.session_state.get(MARKET_RESEARCH_VIEW_KEY),
        legacy_market_context_mode=st.session_state.get("overview_market_context_mode"),
    )
    current_family = market_research_family_for_view(current_view)
    st.markdown(_market_research_navigation_css(), unsafe_allow_html=True)

    family_options: dict[str, object] = {}
    if MARKET_RESEARCH_FAMILY_WIDGET_KEY not in st.session_state:
        family_options["default"] = current_family
    selected_family = st.segmented_control(
        "리서치 목적",
        options=list(MARKET_RESEARCH_FAMILY_OPTIONS),
        format_func=lambda value: MARKET_RESEARCH_FAMILY_LABELS[str(value)],
        key=MARKET_RESEARCH_FAMILY_WIDGET_KEY,
        label_visibility="collapsed",
        width="content",
        **family_options,
    ) or current_family

    family_label, family_views = market_research_local_navigation_context(
        selected_family
    )
    selected_view = (
        current_view
        if current_view in family_views
        else market_research_default_view_for_family(selected_family)
    )
    if st.session_state.get(MARKET_RESEARCH_VIEW_WIDGET_KEY) not in family_views:
        st.session_state.pop(MARKET_RESEARCH_VIEW_WIDGET_KEY, None)
    view_options: dict[str, object] = {}
    if MARKET_RESEARCH_VIEW_WIDGET_KEY not in st.session_state:
        view_options["default"] = selected_view

    with st.container(
        key=MARKET_RESEARCH_LOCAL_NAV_KEY,
        border=True,
        horizontal=True,
        horizontal_alignment="left",
        vertical_alignment="center",
        gap="small",
    ):
        st.markdown(
            '<div class="mr-market-research-local-label">'
            "<span>선택한 리서치</span>"
            f"<strong>{escape(family_label)}</strong>"
            "</div>",
            unsafe_allow_html=True,
        )
        selected_view = st.pills(
            "세부 리서치",
            options=list(family_views),
            format_func=lambda value: MARKET_RESEARCH_VIEW_LABELS[str(value)],
            selection_mode="single",
            required=True,
            key=MARKET_RESEARCH_VIEW_WIDGET_KEY,
            label_visibility="collapsed",
            width="content",
            **view_options,
        ) or selected_view

    return _store_market_research_view(str(selected_view))


def _render_selected_market_research_view(
    selected_view: object,
    *,
    renderers: dict[str, Callable[[], None]],
) -> str:
    canonical = normalize_market_research_view(selected_view)
    renderer = renderers.get(canonical) or renderers.get("economic-cycle")
    if callable(renderer):
        renderer()
    return canonical


def _render_overview_tab_selector() -> str:
    """Retain the old helper name for external callers during migration."""
    return _render_market_research_selector()


def _render_selected_overview_tab(
    selected_label: object,
    *,
    renderers: dict[str, Callable[[], None]],
) -> str:
    """Normalize legacy English renderer keys before canonical dispatch."""
    canonical_renderers = {
        normalize_market_research_view(key): renderer
        for key, renderer in renderers.items()
    }
    return _render_selected_market_research_view(
        selected_label,
        renderers=canonical_renderers,
    )


__all__ = [
    "MARKET_RESEARCH_FAMILY_DESCRIPTIONS",
    "MARKET_RESEARCH_FAMILY_LABELS",
    "MARKET_RESEARCH_FAMILY_OPTIONS",
    "MARKET_RESEARCH_LEGACY_LABELS",
    "MARKET_RESEARCH_LEGACY_SLUGS",
    "MARKET_RESEARCH_LOCAL_NAV_KEY",
    "MARKET_RESEARCH_APPLIED_QUERY_KEY",
    "MARKET_RESEARCH_FAMILY_WIDGET_KEY",
    "MARKET_RESEARCH_VIEW_FAMILY",
    "MARKET_RESEARCH_VIEW_LABELS",
    "MARKET_RESEARCH_VIEW_OPTIONS",
    "MARKET_RESEARCH_VIEW_KEY",
    "MARKET_RESEARCH_VIEW_WIDGET_KEY",
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
    "_market_research_navigation_css",
    "_market_research_query_slug",
    "_render_market_research_selector",
    "_render_overview_tab_selector",
    "_render_selected_market_research_view",
    "_render_selected_overview_tab",
    "_store_market_research_view",
    "build_market_research_navigation_payload",
    "market_research_default_view_for_family",
    "market_research_family_for_view",
    "market_research_local_navigation_context",
    "market_research_views_for_family",
    "normalize_market_research_view",
    "resolve_market_research_seed_view",
    "resolve_market_research_navigation_event",
]
