# Market Research IA Redesign V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 기존 `/overview`를 Today의 반복 요약이 아닌 `시장 환경 | 지수 가치평가 | 종목 리서치` 목적형 Market Research workspace로 전환하고 변동 종목에서 동일 symbol의 개별주식 분석까지 연결한다.

**Architecture:** `app/web/overview/navigation.py`가 canonical view, family mapping, legacy slug, query/widget/session precedence를 pure contract와 Streamlit selector로 소유한다. `page.py`는 canonical view 하나만 lazy dispatch하며 기존 module renderer와 DB-backed service는 유지한다. Market Movers의 React event는 Python에서 현재 선택 symbol을 재검증한 뒤 기존 U.S. Stock session state와 `overview_tab=us-stock`만 변경한다.

**Tech Stack:** Python 3.12, Streamlit multipage/navigation API, React 18, TypeScript 5.7, Vite 6, Node test runner, pytest/unittest mocks, existing Streamlit component bundles.

## Global Constraints

- canonical page path는 `/overview`를 유지한다.
- visible primary labels는 정확히 `시장 환경`, `지수 가치평가`, `종목 리서치`를 사용한다.
- canonical views는 정확히 `economic-cycle`, `futures-macro`, `sentiment`, `events`, `sp500`, `market-movers`, `us-stock`이다.
- legacy `overview_tab=market-context|market-movers|futures-macro|sentiment|events`를 계속 수용한다.
- Today의 `market-context` CTA는 `economic-cycle`, `market-movers` CTA는 `market-movers`로 열려야 한다.
- Market Research render 중 provider fetch, registry write, monitoring log write를 추가하지 않는다.
- module 계산, loader, DB schema, ingestion cadence를 변경하지 않는다.
- page-global Overview help, full market-session banner, freshness/source-count summary, run/job/row diagnostic panel을 만들지 않는다.
- 420px primary selector는 3 equal columns, secondary selector는 2-column wrap이며 horizontal scroll에 의존하지 않는다.
- generated Browser screenshot와 local run-history/registry artifact를 commit하지 않는다.

---

## File Responsibility Map

| File | Responsibility |
| --- | --- |
| `app/web/overview/navigation.py` | canonical view/family/legacy/query state와 2-level selector |
| `app/web/overview/page.py` | Market Research page shell과 canonical view lazy dispatch |
| `app/web/overview/market_context.py` | retained legacy Market Context compatibility adapter |
| `app/web/overview/market_movers.py` | Market Movers header optional rendering |
| `app/web/overview/futures_macro.py` | Futures Macro header optional rendering |
| `app/web/overview/sentiment.py` | Sentiment header optional rendering |
| `app/web/overview/events.py` | Events header optional rendering |
| `app/web/overview/market_movers_helpers.py` | allow-listed `open_us_stock_research` event validation/state handoff |
| `app/web/streamlit_components/market_movers_workbench/src/marketResearchHandoff.ts` | normalized React handoff event builder |
| `app/web/streamlit_components/market_movers_workbench/src/MarketMoversWorkbench.tsx` | selected symbol의 `개별 종목 분석` CTA |
| `tests/test_market_research_navigation.py` | focused pure/navigation/page/header/handoff contracts |
| `tests/test_service_contracts.py` | old five-tab structural assertions를 new IA contract로 migration |

---

### Task 1: Canonical Market Research View Contract

**Files:**
- Create: `tests/test_market_research_navigation.py`
- Modify: `app/web/overview/navigation.py`
- Modify: `tests/test_service_contracts.py` methods beginning with `test_overview_navigation_surface_owns_selector_entrypoints`, `test_overview_dashboard_defaults_unknown_deep_tab_to_market_context`, `test_overview_dashboard_pill_nav_slug_contract`

**Interfaces:**
- Produces: `normalize_market_research_view(value: object, legacy_market_context_mode: object = None) -> str`
- Produces: `market_research_family_for_view(view: object) -> str`
- Produces: `market_research_views_for_family(family: object) -> tuple[str, ...]`
- Produces: `market_research_default_view_for_family(family: object) -> str`
- Produces: `resolve_market_research_seed_view(*, query_slug, applied_query_slug, widget_view, session_view, legacy_market_context_mode) -> str`
- Produces constants: `MARKET_RESEARCH_VIEW_OPTIONS`, `MARKET_RESEARCH_FAMILY_OPTIONS`, `MARKET_RESEARCH_VIEW_FAMILY`, `MARKET_RESEARCH_VIEW_LABELS`

- [ ] **Step 1: Write the failing pure-contract tests**

```python
from pathlib import Path

from app.web.overview.navigation import (
    MARKET_RESEARCH_FAMILY_OPTIONS,
    MARKET_RESEARCH_VIEW_OPTIONS,
    market_research_default_view_for_family,
    market_research_family_for_view,
    market_research_views_for_family,
    normalize_market_research_view,
    resolve_market_research_seed_view,
)


def test_market_research_views_cover_three_purpose_families():
    assert MARKET_RESEARCH_FAMILY_OPTIONS == (
        "market-environment",
        "index-valuation",
        "stock-research",
    )
    assert MARKET_RESEARCH_VIEW_OPTIONS == (
        "economic-cycle",
        "futures-macro",
        "sentiment",
        "events",
        "sp500",
        "market-movers",
        "us-stock",
    )
    assert market_research_views_for_family("market-environment") == (
        "economic-cycle",
        "futures-macro",
        "sentiment",
        "events",
    )
    assert market_research_views_for_family("index-valuation") == ("sp500",)
    assert market_research_views_for_family("stock-research") == (
        "market-movers",
        "us-stock",
    )


def test_market_research_legacy_slug_normalization():
    assert normalize_market_research_view("market-context", "sp500") == "sp500"
    assert normalize_market_research_view("market-context", "us_stock") == "us-stock"
    assert normalize_market_research_view("market-context", None) == "economic-cycle"
    assert normalize_market_research_view("market-movers") == "market-movers"
    assert normalize_market_research_view("does-not-exist") == "economic-cycle"


def test_changed_query_wins_over_stale_widget_state():
    assert resolve_market_research_seed_view(
        query_slug="market-movers",
        applied_query_slug="economic-cycle",
        widget_view="sentiment",
        session_view="events",
        legacy_market_context_mode=None,
    ) == "market-movers"
    assert resolve_market_research_seed_view(
        query_slug="market-movers",
        applied_query_slug="market-movers",
        widget_view="us-stock",
        session_view="market-movers",
        legacy_market_context_mode=None,
    ) == "us-stock"


def test_market_research_defaults_are_stable():
    assert market_research_default_view_for_family("market-environment") == "economic-cycle"
    assert market_research_default_view_for_family("index-valuation") == "sp500"
    assert market_research_default_view_for_family("stock-research") == "market-movers"
    assert market_research_family_for_view("broken") == "market-environment"
```

- [ ] **Step 2: Run the focused tests and verify RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_market_research_navigation.py -q
```

Expected: collection fails because the new constants/functions do not exist.

- [ ] **Step 3: Implement the minimal pure contract in `navigation.py`**

```python
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


def normalize_market_research_view(value: object, legacy_market_context_mode: object = None) -> str:
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
        normalized = "market-environment"
    return tuple(
        view for view in MARKET_RESEARCH_VIEW_OPTIONS
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
    return "economic-cycle"
```

- [ ] **Step 4: Replace old five-tab structural assertions in `tests/test_service_contracts.py`**

Replace the three named tests with assertions against the new constants and retained compatibility exports. Do not assert old English labels or five-tab order.

```python
def test_overview_navigation_surface_owns_market_research_entrypoints(self) -> None:
    from app.web.overview import navigation

    self.assertEqual(len(navigation.MARKET_RESEARCH_FAMILY_OPTIONS), 3)
    self.assertEqual(len(navigation.MARKET_RESEARCH_VIEW_OPTIONS), 7)
    self.assertTrue(callable(navigation.normalize_market_research_view))
    self.assertTrue(callable(navigation.market_research_family_for_view))
    self.assertTrue(callable(navigation._render_overview_tab_selector))
    self.assertTrue(callable(navigation._render_selected_overview_tab))


def test_overview_dashboard_defaults_unknown_view_to_economic_cycle(self) -> None:
    from app.web.overview.navigation import normalize_market_research_view

    self.assertEqual(normalize_market_research_view("does-not-exist"), "economic-cycle")
    self.assertEqual(normalize_market_research_view(None), "economic-cycle")


def test_market_research_slug_contract(self) -> None:
    from app.web.overview.navigation import normalize_market_research_view

    self.assertEqual(normalize_market_research_view("market-context"), "economic-cycle")
    self.assertEqual(normalize_market_research_view("market-movers"), "market-movers")
    self.assertEqual(normalize_market_research_view("futures-macro"), "futures-macro")
```

- [ ] **Step 5: Run focused navigation tests and migrated contracts**

Run:

```bash
.venv/bin/python -m pytest tests/test_market_research_navigation.py -q
.venv/bin/python -m pytest tests/test_service_contracts.py -q -k 'overview_navigation_surface or defaults_unknown or market_research_slug_contract'
```

Expected: all selected tests pass.

- [ ] **Step 6: Commit Task 1**

```bash
git add app/web/overview/navigation.py tests/test_market_research_navigation.py tests/test_service_contracts.py
git commit -m "기능: Market Research 목적형 탐색 계약 추가"
```

---

### Task 2: Two-Level Selector And Canonical Page Dispatch

**Files:**
- Modify: `app/web/overview/navigation.py`
- Modify: `app/web/overview/page.py`
- Modify: `app/web/overview/market_context.py`
- Modify: `tests/test_market_research_navigation.py`
- Modify: `tests/test_service_contracts.py` old page-selector/lazy-dispatch assertions

**Interfaces:**
- Consumes: Task 1 canonical mapping functions/constants
- Produces: `_render_market_research_selector() -> str`
- Produces: `_render_selected_market_research_view(selected_view: object, *, renderers: Mapping[str, Callable[[], None]]) -> str`
- Retains: `_render_overview_tab_selector()` and `_render_selected_overview_tab()` as legacy wrappers

- [ ] **Step 1: Add failing dispatch and page-shell tests**

```python
def test_market_research_dispatch_calls_only_selected_view():
    from app.web.overview.navigation import _render_selected_market_research_view

    calls = []
    selected = _render_selected_market_research_view(
        "us-stock",
        renderers={
            "economic-cycle": lambda: calls.append("economic-cycle"),
            "us-stock": lambda: calls.append("us-stock"),
        },
    )
    assert selected == "us-stock"
    assert calls == ["us-stock"]


def test_market_research_page_removes_overview_global_blocks():
    source = Path("app/web/overview/page.py").read_text(encoding="utf-8")
    body = source[source.index("def render_overview_dashboard"):]
    assert 'st.title("Market Research")' in body
    assert "Today에서 확인한 시장 판단을 환경·가치평가·종목 근거로 확장합니다." in body
    assert "render_reference_contextual_help" not in body
    assert "render_market_session_banner" not in body
    assert "_render_market_research_selector()" in body
```

- [ ] **Step 2: Run RED verification**

```bash
.venv/bin/python -m pytest tests/test_market_research_navigation.py -q
```

Expected: new dispatch and page-shell tests fail.

- [ ] **Step 3: Implement query read/write and 2-level selector**

Add these state keys and helpers in `navigation.py`:

```python
MARKET_RESEARCH_VIEW_KEY = "market_research_active_view"
MARKET_RESEARCH_FAMILY_WIDGET_KEY = "market_research_family_widget"
MARKET_RESEARCH_VIEW_WIDGET_KEY = "market_research_view_widget"
MARKET_RESEARCH_APPLIED_QUERY_KEY = "market_research_applied_query"
OVERVIEW_DEEP_TAB_QUERY_PARAM = "overview_tab"


def _market_research_query_slug() -> str | None:
    raw = st.query_params.get(OVERVIEW_DEEP_TAB_QUERY_PARAM)
    if isinstance(raw, list):
        raw = raw[-1] if raw else None
    value = str(raw or "").strip().lower()
    return value or None


def _store_market_research_view(view: str) -> str:
    canonical = normalize_market_research_view(view)
    st.session_state[MARKET_RESEARCH_VIEW_KEY] = canonical
    st.session_state[MARKET_RESEARCH_APPLIED_QUERY_KEY] = canonical
    st.query_params[OVERVIEW_DEEP_TAB_QUERY_PARAM] = canonical
    return canonical
```

Add the scoped style and selector implementation:

```python
def _market_research_navigation_css() -> str:
    return """
<style>
.st-key-market_research_family_widget div[data-baseweb="button-group"] {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.45rem;
}
.st-key-market_research_family_widget button {
  width: 100%;
  min-height: 2.55rem;
}
.st-key-market_research_view_widget div[data-baseweb="button-group"] {
  display: flex;
  flex-wrap: wrap;
  gap: 0.42rem;
}
@media (max-width: 480px) {
  .st-key-market_research_view_widget div[data-baseweb="button-group"] {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .st-key-market_research_view_widget button {
    width: 100%;
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
        width="stretch",
        **family_options,
    ) or current_family

    family_views = market_research_views_for_family(selected_family)
    selected_view = (
        current_view
        if current_view in family_views
        else market_research_default_view_for_family(selected_family)
    )
    if len(family_views) > 1:
        if st.session_state.get(MARKET_RESEARCH_VIEW_WIDGET_KEY) not in family_views:
            st.session_state.pop(MARKET_RESEARCH_VIEW_WIDGET_KEY, None)
        view_options: dict[str, object] = {}
        if MARKET_RESEARCH_VIEW_WIDGET_KEY not in st.session_state:
            view_options["default"] = selected_view
        selected_view = st.pills(
            "세부 리서치",
            options=list(family_views),
            format_func=lambda value: MARKET_RESEARCH_VIEW_LABELS[str(value)],
            selection_mode="single",
            required=True,
            key=MARKET_RESEARCH_VIEW_WIDGET_KEY,
            label_visibility="collapsed",
            width="stretch",
            **view_options,
        ) or selected_view
    else:
        st.session_state.pop(MARKET_RESEARCH_VIEW_WIDGET_KEY, None)
        selected_view = family_views[0]

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
    """Retained compatibility wrapper for callers using the old helper name."""
    return _render_market_research_selector()


def _render_selected_overview_tab(
    selected_label: object,
    *,
    renderers: dict[str, Callable[[], None]],
) -> str:
    """Normalize legacy English keys before canonical dispatch."""
    canonical_renderers = {
        normalize_market_research_view(key): renderer
        for key, renderer in renderers.items()
    }
    return _render_selected_market_research_view(
        selected_label,
        renderers=canonical_renderers,
    )
```

- [ ] **Step 4: Implement canonical lazy dispatch and page shell**

In `page.py`, remove imports/calls for `render_market_session_banner`, `_market_session_banner_model`, and `render_reference_contextual_help`. Import `render_economic_cycle` and `render_market_context_valuation` directly.

```python
st.caption("MARKET RESEARCH")
st.title("Market Research")
st.caption("Today에서 확인한 시장 판단을 환경·가치평가·종목 근거로 확장합니다.")

active_view = _render_market_research_selector()
_render_selected_market_research_view(
    active_view,
    renderers={
        "economic-cycle": render_economic_cycle,
        "futures-macro": render_futures_macro_tab,
        "sentiment": render_sentiment_tab,
        "events": render_events_tab,
        "sp500": lambda: render_market_context_valuation(
            default_instrument="sp500",
            show_instrument_selector=False,
        ),
        "market-movers": render_market_movers_tab,
        "us-stock": lambda: render_market_context_valuation(
            default_instrument="us_stock",
            show_instrument_selector=False,
        ),
    },
)
```

`render_market_context_tab()` remains unchanged as a retained compatibility caller, but the new page renderer must not call it.

- [ ] **Step 5: Migrate old page/selector structural tests**

Update old assertions that require five English labels, underline-only CSS, or `render_market_context_tab` as the primary page dispatch. New assertions must require:

```python
self.assertIn('"economic-cycle": render_economic_cycle', render_body)
self.assertIn('"market-movers": render_market_movers_tab', render_body)
self.assertIn('default_instrument="sp500"', render_body)
self.assertIn('default_instrument="us_stock"', render_body)
self.assertNotIn("render_market_context_tab", render_body)
self.assertNotIn("render_market_session_banner", render_body)
self.assertNotIn("render_reference_contextual_help", render_body)
```

- [ ] **Step 6: Run focused and structural tests**

```bash
.venv/bin/python -m pytest tests/test_market_research_navigation.py -q
.venv/bin/python -m pytest tests/test_service_contracts.py -q -k 'overview_page or overview_dashboard or market_research'
.venv/bin/python -m py_compile app/web/overview/navigation.py app/web/overview/page.py app/web/overview/market_context.py
```

Expected: all selected tests and compilation pass.

- [ ] **Step 7: Commit Task 2**

```bash
git add app/web/overview/navigation.py app/web/overview/page.py app/web/overview/market_context.py tests/test_market_research_navigation.py tests/test_service_contracts.py
git commit -m "기능: Market Research 목적형 화면 구조 전환"
```

---

### Task 3: Module Header Ownership And Fallback Hierarchy

**Files:**
- Modify: `app/web/overview/page.py`
- Modify: `app/web/overview/market_movers.py`
- Modify: `app/web/overview/futures_macro.py`
- Modify: `app/web/overview/sentiment.py`
- Modify: `app/web/overview/events.py`
- Modify: `tests/test_market_research_navigation.py`
- Modify: `tests/test_service_contracts.py` module-header source assertions

**Interfaces:**
- Produces: `render_market_movers_tab(*, show_header: bool = True) -> None`
- Produces: `render_futures_macro_tab(*, show_header: bool = True) -> None`
- Produces: `render_sentiment_tab(*, show_header: bool = True) -> None`
- Produces: `render_events_tab(*, show_header: bool = True) -> None`

- [ ] **Step 1: Add failing mock tests for optional headers**

```python
from unittest.mock import patch


def test_market_movers_page_dispatch_can_suppress_duplicate_header():
    from app.web.overview.market_movers import render_market_movers_tab

    with (
        patch("app.web.overview.market_movers.render_market_movers_header") as header,
        patch("app.web.overview.market_movers.render_market_movers_controls") as controls,
        patch("app.web.overview.market_movers.render_market_movers_context_captions"),
        patch("app.web.overview.market_movers.normalize_market_movers_refresh_mode"),
        patch("app.web.overview.market_movers.is_market_movers_auto_refresh_enabled", return_value=False),
        patch("app.web.overview.market_movers.render_market_movers_snapshot"),
    ):
        controls.return_value = object()
        render_market_movers_tab(show_header=False)
    header.assert_not_called()


def test_futures_sentiment_events_keep_legacy_header_default():
    from app.web.overview.futures_macro import render_futures_macro_tab

    with (
        patch("app.web.overview.futures_macro.render_futures_macro_header") as header,
        patch("app.web.overview.futures_macro.render_futures_macro_fragment"),
    ):
        render_futures_macro_tab()
    header.assert_called_once_with()


def test_futures_page_dispatch_can_suppress_duplicate_header():
    from app.web.overview.futures_macro import render_futures_macro_tab

    with (
        patch("app.web.overview.futures_macro.render_futures_macro_header") as header,
        patch("app.web.overview.futures_macro.render_futures_macro_fragment"),
    ):
        render_futures_macro_tab(show_header=False)
    header.assert_not_called()


def test_sentiment_page_dispatch_can_suppress_duplicate_header():
    from app.web.overview.sentiment import render_sentiment_tab

    with (
        patch("app.web.overview.sentiment.render_sentiment_header") as header,
        patch("app.web.overview.sentiment.load_sentiment_snapshot", return_value={}),
        patch("app.web.overview.sentiment.render_sentiment_react_workbench_section", return_value=True),
        patch("app.web.overview.sentiment.render_sentiment_job_result"),
        patch("app.web.overview.sentiment.has_sentiment_rows", return_value=False),
        patch("app.web.overview.sentiment.render_sentiment_empty_state"),
    ):
        render_sentiment_tab(show_header=False)
    header.assert_not_called()


def test_events_page_dispatch_can_suppress_duplicate_header():
    from app.web.overview.events import render_events_tab

    with (
        patch("app.web.overview.events.render_events_header") as header,
        patch("app.web.overview.events.events_react_workbench_available", return_value=True),
        patch("app.web.overview.events.load_event_snapshot_context", return_value={}),
        patch("app.web.overview.events.render_events_react_workbench_section", return_value=True),
        patch("app.web.overview.events.has_event_rows", return_value=False),
        patch("app.web.overview.events.render_events_empty_state"),
    ):
        render_events_tab(show_header=False)
    header.assert_not_called()
```

- [ ] **Step 2: Run RED verification**

```bash
.venv/bin/python -m pytest tests/test_market_research_navigation.py -q -k header
```

Expected: functions reject the `show_header` keyword.

- [ ] **Step 3: Add the optional header keyword to each renderer**

Apply the same minimal pattern without changing module body order:

```python
def render_futures_macro_tab(*, show_header: bool = True) -> None:
    """Render the Futures Macro Overview tab."""
    if show_header:
        render_futures_macro_header()
    render_futures_macro_fragment(detail_expanded=False)
```

Use corresponding header functions in Market Movers, Sentiment, and Events. Keep the default `True` for compatibility callers and fallback accessibility.

Then update only the four page dispatch entries to suppress their duplicate Streamlit headings:

```python
"futures-macro": lambda: render_futures_macro_tab(show_header=False),
"sentiment": lambda: render_sentiment_tab(show_header=False),
"events": lambda: render_events_tab(show_header=False),
"market-movers": lambda: render_market_movers_tab(show_header=False),
```

- [ ] **Step 4: Run module and page tests**

```bash
.venv/bin/python -m pytest tests/test_market_research_navigation.py -q
.venv/bin/python -m pytest tests/test_service_contracts.py -q -k 'market_movers_tab or futures_macro_tab or sentiment or events'
.venv/bin/python -m py_compile app/web/overview/market_movers.py app/web/overview/futures_macro.py app/web/overview/sentiment.py app/web/overview/events.py
```

Expected: all selected tests and compilation pass.

- [ ] **Step 5: Commit Task 3**

```bash
git add app/web/overview/page.py app/web/overview/market_movers.py app/web/overview/futures_macro.py app/web/overview/sentiment.py app/web/overview/events.py tests/test_market_research_navigation.py tests/test_service_contracts.py
git commit -m "개선: Market Research 중복 모듈 제목 정리"
```

---

### Task 4: Python Market Movers To U.S. Stock Handoff

**Files:**
- Modify: `app/web/overview/market_movers_helpers.py`
- Modify: `app/web/overview/market_context_helpers.py` only to reuse/export `US_STOCK_SELECTED_SYMBOL_KEY`; do not change loader behavior
- Modify: `tests/test_market_research_navigation.py`
- Modify: `tests/test_service_contracts.py` event action-plan contract

**Interfaces:**
- Consumes: `US_STOCK_SELECTED_SYMBOL_KEY = "overview_us_stock_valuation_selected_symbol"`
- Consumes: Task 1 `MARKET_RESEARCH_VIEW_KEY`
- Produces action plan: `open_us_stock_research -> {"handler": "open_us_stock_research"}`
- Produces state transition: current mover symbol -> U.S. Stock symbol + canonical `us-stock` view/query

- [ ] **Step 1: Add failing success and rejection tests**

```python
from unittest.mock import MagicMock, patch


@patch("app.web.overview.market_movers_helpers.st")
def test_market_movers_handoff_opens_same_selected_symbol(mock_st):
    from app.web.overview.market_context_helpers import US_STOCK_SELECTED_SYMBOL_KEY
    from app.web.overview.market_movers_helpers import (
        MarketMoverControls,
        _dispatch_market_movers_react_event,
    )
    from app.web.overview.navigation import MARKET_RESEARCH_VIEW_KEY

    controls = MarketMoverControls(
        coverage="SP500",
        universe_limit=500,
        period="daily",
        sector="All",
        top_n=20,
        mode="top_gainers",
    )
    mock_st.session_state = {"overview_market_movers_selected_symbol_SP500": "AMD"}
    mock_st.query_params = {}

    handled = _dispatch_market_movers_react_event(
        {"event": {"id": "open_us_stock_research", "symbol": "amd", "nonce": 1}},
        controls=controls,
    )

    assert handled is True
    assert mock_st.session_state[US_STOCK_SELECTED_SYMBOL_KEY] == "AMD"
    assert mock_st.session_state[MARKET_RESEARCH_VIEW_KEY] == "us-stock"
    assert mock_st.query_params["overview_tab"] == "us-stock"
    mock_st.rerun.assert_called_once_with()


@patch("app.web.overview.market_movers_helpers.st")
def test_market_movers_handoff_rejects_symbol_not_currently_selected(mock_st):
    from app.web.overview.market_movers_helpers import (
        MarketMoverControls,
        _dispatch_market_movers_react_event,
    )

    controls = MarketMoverControls(
        coverage="SP500",
        universe_limit=500,
        period="daily",
        sector="All",
        top_n=20,
        mode="top_gainers",
    )
    mock_st.session_state = {"overview_market_movers_selected_symbol_SP500": "AMD"}
    mock_st.query_params = {}

    handled = _dispatch_market_movers_react_event(
        {"event": {"id": "open_us_stock_research", "symbol": "AAPL", "nonce": 2}},
        controls=controls,
    )

    assert handled is False
    assert "overview_us_stock_valuation_selected_symbol" not in mock_st.session_state
    mock_st.rerun.assert_not_called()


def test_market_movers_action_plan_allow_lists_stock_research_handoff():
    from app.web.overview.market_movers_helpers import (
        MarketMoverControls,
        market_movers_react_action_plan,
    )

    controls = MarketMoverControls(
        coverage="SP500",
        universe_limit=500,
        period="daily",
        sector="All",
        top_n=20,
        mode="top_gainers",
    )
    assert market_movers_react_action_plan(
        "open_us_stock_research",
        controls=controls,
    ) == {"handler": "open_us_stock_research"}
```

- [ ] **Step 2: Run RED verification**

```bash
.venv/bin/python -m pytest tests/test_market_research_navigation.py -q -k handoff
```

Expected: handler is `noop` and the success test fails.

- [ ] **Step 3: Add the allow-listed action and state transition**

Extend `market_movers_react_action_plan`:

```python
if action_id == "open_us_stock_research":
    return {"handler": "open_us_stock_research"}
```

Add this branch in `_dispatch_market_movers_react_event` after the one-time event-token guard and before fetch actions:

```python
if handler == "open_us_stock_research":
    from app.web.overview.market_context_helpers import US_STOCK_SELECTED_SYMBOL_KEY
    from app.web.overview.navigation import (
        MARKET_RESEARCH_APPLIED_QUERY_KEY,
        MARKET_RESEARCH_FAMILY_WIDGET_KEY,
        MARKET_RESEARCH_VIEW_KEY,
        MARKET_RESEARCH_VIEW_WIDGET_KEY,
    )

    payload = _market_movers_react_event_payload(event)
    symbol = str(payload.get("symbol") or "").strip().upper()
    selected_key = f"overview_market_movers_selected_symbol_{controls.coverage}"
    selected_symbol = str(st.session_state.get(selected_key) or "").strip().upper()
    if not symbol or symbol != selected_symbol:
        return False
    st.session_state[US_STOCK_SELECTED_SYMBOL_KEY] = symbol
    st.session_state[MARKET_RESEARCH_VIEW_KEY] = "us-stock"
    st.session_state.pop(MARKET_RESEARCH_FAMILY_WIDGET_KEY, None)
    st.session_state.pop(MARKET_RESEARCH_VIEW_WIDGET_KEY, None)
    st.session_state.pop(MARKET_RESEARCH_APPLIED_QUERY_KEY, None)
    st.query_params["overview_tab"] = "us-stock"
    st.rerun()
    return True
```

This branch must not call `run_overview_us_stock_data_refresh`, cache clear, job-result storage, or remote services.

- [ ] **Step 4: Run handoff and event regression tests**

```bash
.venv/bin/python -m pytest tests/test_market_research_navigation.py -q -k handoff
.venv/bin/python -m pytest tests/test_service_contracts.py -q -k 'market_movers_react_event or market_movers_react_action'
.venv/bin/python -m py_compile app/web/overview/market_movers_helpers.py app/web/overview/market_context_helpers.py
```

Expected: handoff and existing event deduplication tests pass.

- [ ] **Step 5: Commit Task 4**

```bash
git add app/web/overview/market_movers_helpers.py app/web/overview/market_context_helpers.py tests/test_market_research_navigation.py tests/test_service_contracts.py
git commit -m "기능: 변동 종목에서 개별주식 분석 연결"
```

---

### Task 5: React `개별 종목 분석` CTA

**Files:**
- Create: `app/web/streamlit_components/market_movers_workbench/src/marketResearchHandoff.ts`
- Create: `app/web/streamlit_components/market_movers_workbench/src/marketResearchHandoff.test.ts`
- Modify: `app/web/streamlit_components/market_movers_workbench/src/MarketMoversWorkbench.tsx`
- Modify: `app/web/streamlit_components/market_movers_workbench/src/style.css`
- Modify: `app/web/streamlit_components/market_movers_workbench/package.json`
- Regenerate: `app/web/streamlit_components/market_movers_workbench/component_static/`

**Interfaces:**
- Produces: `buildStockResearchHandoffEvent(symbol: string) -> {id: "open_us_stock_research"; symbol: string}`
- Consumes: existing `StockResearchTabs` `activeSymbol` and `onEvent`

- [ ] **Step 1: Write the failing TypeScript event-builder test**

```typescript
import assert from "node:assert/strict";
import test from "node:test";

import { buildStockResearchHandoffEvent } from "./marketResearchHandoff.ts";

test("normalizes the selected symbol into the allow-listed handoff event", () => {
  assert.deepEqual(buildStockResearchHandoffEvent(" amd "), {
    id: "open_us_stock_research",
    symbol: "AMD",
  });
});
```

Change the package test script to:

```json
"test": "node --test src/*.test.ts"
```

- [ ] **Step 2: Run the frontend test and verify RED**

```bash
cd app/web/streamlit_components/market_movers_workbench
npm test
```

Expected: module import fails because `marketResearchHandoff.ts` does not exist.

- [ ] **Step 3: Implement the pure event builder**

```typescript
export type StockResearchHandoffEvent = {
  id: "open_us_stock_research";
  symbol: string;
};

export function buildStockResearchHandoffEvent(symbol: string): StockResearchHandoffEvent {
  return {
    id: "open_us_stock_research",
    symbol: symbol.trim().toUpperCase(),
  };
}
```

- [ ] **Step 4: Add the CTA to the selected-stock research header**

Import the builder and change `mm-decision__research-head` to contain the existing tabs plus this button:

```tsx
<button
  className="mm-decision__stock-analysis-link"
  onClick={() => onEvent(buildStockResearchHandoffEvent(activeSymbol))}
  type="button"
>
  개별 종목 분석
</button>
```

The button appears only inside `StockResearchTabs`, so it is rendered only when the detail panel has a selected symbol. Style it as a compact secondary action; under `760px` place it on a new row and keep full visible text.

```css
.mm-decision__stock-analysis-link {
  min-height: 2.25rem;
  padding: 0.45rem 0.78rem;
  border: 1px solid var(--mm-card-line);
  border-radius: 999px;
  background: #ffffff;
  color: var(--mm-ink);
  font-weight: 700;
  white-space: nowrap;
}

@media (max-width: 760px) {
  .mm-decision__research-head {
    align-items: stretch;
    flex-wrap: wrap;
  }
  .mm-decision__stock-analysis-link {
    width: 100%;
  }
}
```

- [ ] **Step 5: Run test, typecheck-equivalent build, and production build**

```bash
cd app/web/streamlit_components/market_movers_workbench
npm test
npx tsc --noEmit
npm run build
```

Expected: Node tests pass, TypeScript exits 0, and Vite rebuilds `component_static/`.

- [ ] **Step 6: Commit Task 5**

```bash
git add app/web/streamlit_components/market_movers_workbench/package.json app/web/streamlit_components/market_movers_workbench/src app/web/streamlit_components/market_movers_workbench/component_static
git commit -m "기능: 변동 종목에 개별 분석 이동 추가"
```

---

### Task 6: Full Verification, Browser QA, And Durable Documentation

**Files:**
- Modify: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/flows/README.md`
- Modify: `.aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md`
- Modify: `.aiworkspace/note/finance/docs/INDEX.md`
- Modify: `.aiworkspace/note/finance/tasks/active/market-research-ia-redesign-v1-20260722/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/market-research-ia-redesign-v1-20260722/NOTES.md`
- Modify: `.aiworkspace/note/finance/tasks/active/market-research-ia-redesign-v1-20260722/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/market-research-ia-redesign-v1-20260722/RISKS.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`

**Interfaces:**
- Consumes: completed Tasks 1–5
- Produces: durable IA map, completed `4/4` status, QA evidence

- [ ] **Step 1: Run focused Python verification**

```bash
.venv/bin/python -m pytest tests/test_market_research_navigation.py -q
.venv/bin/python -m pytest tests/test_today_home.py -q
.venv/bin/python -m pytest tests/test_service_contracts.py -q -k 'overview or market_movers or market_context or sentiment or events'
.venv/bin/python -m py_compile app/web/overview/navigation.py app/web/overview/page.py app/web/overview/market_context.py app/web/overview/market_movers.py app/web/overview/futures_macro.py app/web/overview/sentiment.py app/web/overview/events.py app/web/overview/market_movers_helpers.py
```

Expected: all focused tests and compilation pass. If the broad `-k` selection exposes a pre-existing unrelated failure, record its exact test name and confirm it passes on parent `723de2479` before classifying it as baseline.

- [ ] **Step 2: Run frontend verification**

```bash
cd app/web/streamlit_components/market_movers_workbench
npm test
npx tsc --noEmit
npm run build
```

Expected: all commands exit 0.

- [ ] **Step 3: Run repository hygiene checks**

```bash
git diff --check
git status --short
```

Expected: no whitespace errors. Registry JSONL, run history, QA images, unrelated research bundle, and `.superpowers/` remain unstaged.

- [ ] **Step 4: Perform actual Browser QA**

Use the Browser skill against the current sub-dev Streamlit process and reload after the code/build changes.

Verify:

1. `/overview` opens `시장 환경 > 경제 사이클`.
2. page top shows `Market Research` and no Overview/Reference/session global blocks.
3. primary selector switches among all three families.
4. secondary selector opens all seven canonical views.
5. `?overview_tab=market-context`, `market-movers`, `futures-macro`, `sentiment`, `events` resolve correctly.
6. root Today's two Market Research actions reach Economic Cycle and Market Movers.
7. select a real Market Movers symbol, open detail, click `개별 종목 분석`, and verify the same symbol opens in U.S. Stock.
8. desktop 1280px, 760px, 420px show no horizontal overflow and clear selected state.
9. browser console has no new warning/error.

Save one screenshot under the worktree root with a descriptive `market-research-ia-v1-qa.png` name and keep it unstaged.

- [ ] **Step 5: Synchronize durable documentation**

Update the documents with these exact facts:

- `Market Research` has three purpose families and seven canonical views.
- Today remains the summary owner.
- Market Research has no global session/reference/diagnostic panel.
- module status/refresh stays local.
- Market Movers can hand the selected symbol to U.S. Stock without fetch-on-navigation.
- implementation roadmap is `4/4 complete` only after automated and actual Browser QA pass.

Record commands and counts in `RUNS.md`, final decisions in `NOTES.md`, remaining non-blocking gaps in `RISKS.md`, and concise handoff lines in the two root logs.

- [ ] **Step 6: Commit final documentation**

```bash
git add .aiworkspace/note/finance/docs/PROJECT_MAP.md .aiworkspace/note/finance/docs/flows/README.md .aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md .aiworkspace/note/finance/docs/INDEX.md .aiworkspace/note/finance/tasks/active/market-research-ia-redesign-v1-20260722 .aiworkspace/note/finance/WORK_PROGRESS.md .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git diff --cached --check
git commit -m "문서: Market Research IA 개편 완료 기록"
```

- [ ] **Step 7: Final completion check**

```bash
git log -7 --oneline
git status --short
```

Expected: Task 1–6 coherent commits are visible; only pre-existing/unrelated local artifacts remain unstaged.

---

## Plan Self-Review

- Spec coverage: page identity, 3 families, 7 views, legacy URL, Today CTA, local module metadata, symbol handoff, responsive QA, docs sync are each assigned to a task.
- Scope: no service/loader/DB/provider changes and no separate Stock Research page.
- Type consistency: canonical view strings, family strings, session keys, event id, and symbol state keys match across Python, TypeScript, tests, and Browser QA.
- Placeholder scan: every code-changing step contains exact target code or a fully enumerated render/verification contract.
