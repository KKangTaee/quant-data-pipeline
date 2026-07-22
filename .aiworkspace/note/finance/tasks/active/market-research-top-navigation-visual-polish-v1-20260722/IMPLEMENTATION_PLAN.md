# Market Research Top Navigation Visual Polish V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Preserve the existing 3-family / 7-view Market Research state contract while replacing the stretched two-row button form with a compact page header, content-width family rail, and bounded local view navigation.

**Architecture:** `app/web/overview/page.py` continues to own page identity and gains only a keyed, scoped header presentation helper. `app/web/overview/navigation.py` continues to own query/session/widget state and renderer dispatch; it gains a pure local-navigation context helper plus scoped CSS and renders every family, including the single-view S&P 500 family, through the same local navigation surface. Module renderers, services, loaders, DB, and provider contracts do not change.

**Tech Stack:** Python 3.12, Streamlit 1.57 native controls and keyed containers, scoped CSS, pytest, Codex in-app Browser QA.

## Global Constraints

- Keep `/overview`, `overview_tab`, legacy slug normalization, query > widget > session precedence, and all seven canonical view identifiers unchanged.
- Keep Today CTA continuity and Market Movers -> U.S. Stock selected-symbol handoff unchanged.
- Do not add a left drawer, off-canvas navigation, page-global session/freshness/Reference information, provider fetch, persistence, or module-body redesign.
- Do not add sticky navigation initially; record it only as a follow-up if actual QA proves a need.
- Use `RESEARCH WORKSPACE`, `Market Research`, and `Today에서 발견한 질문을 시장·지수·종목 근거로 확장합니다.` exactly.
- Desktop controls are content-width; 420px keeps three equal family columns and two view columns without horizontal overflow.
- Selected navigation must not use the destructive/red tone and must remain identifiable without color alone.
- Preserve unrelated dirty artifacts and stage only allow-listed paths.

## File Structure

- Modify `app/web/overview/page.py`: keyed compact header and scoped header CSS.
- Modify `app/web/overview/navigation.py`: presentation context helper, primary/secondary CSS, unified single/multi-view surface.
- Modify `tests/test_market_research_navigation.py`: presentation and state-preservation contracts.
- Modify task docs, durable finance docs, and root handoff logs only during closeout.
- Create one generated Browser QA screenshot at workspace root and leave it unstaged.

---

### Task 1: Compact Keyed Page Header

**Files:**
- Modify: `tests/test_market_research_navigation.py`
- Modify: `app/web/overview/page.py`

**Interfaces:**
- Consumes: `render_overview_dashboard(...) -> None`.
- Produces: `_market_research_page_css() -> str` and keyed container `market_research_page_header`; renderer map remains unchanged.

- [ ] **Step 1: Write the failing header test**

Append to `tests/test_market_research_navigation.py`:

```python
def test_market_research_page_uses_compact_keyed_header():
    from app.web.overview.page import _market_research_page_css

    source = Path("app/web/overview/page.py").read_text(encoding="utf-8")
    css = _market_research_page_css()
    assert 'st.container(key="market_research_page_header")' in source
    assert 'st.caption("RESEARCH WORKSPACE")' in source
    assert "Today에서 발견한 질문을 시장·지수·종목 근거로 확장합니다." in source
    assert ".st-key-market_research_page_header" in css
    assert "clamp(" in css
```

- [ ] **Step 2: Run RED**

```bash
.venv/bin/python -m pytest tests/test_market_research_navigation.py::test_market_research_page_uses_compact_keyed_header -q
```

Expected: FAIL because `_market_research_page_css` does not exist.

- [ ] **Step 3: Add the complete scoped header helper**

Add after imports in `app/web/overview/page.py`:

```python
def _market_research_page_css() -> str:
    """Return page-header styles scoped to the Market Research shell."""
    return """
<style>
.st-key-market_research_page_header {
  padding-top: 0.1rem;
  padding-bottom: 0.35rem;
}
.st-key-market_research_page_header [data-testid="stCaptionContainer"] {
  margin-bottom: 0.15rem;
}
.st-key-market_research_page_header h1 {
  margin: 0;
  padding: 0;
  font-size: clamp(2.45rem, 4.8vw, 3.55rem);
  line-height: 1.05;
  letter-spacing: -0.04em;
}
@media (max-width: 480px) {
  .st-key-market_research_page_header h1 {
    font-size: clamp(2.1rem, 11vw, 2.75rem);
  }
}
</style>
"""
```

- [ ] **Step 4: Replace only the header calls**

Use this exact block at the start of `render_overview_dashboard` after its `del` statement:

```python
    st.markdown(_market_research_page_css(), unsafe_allow_html=True)
    with st.container(key="market_research_page_header"):
        st.caption("RESEARCH WORKSPACE")
        st.title("Market Research")
        st.caption("Today에서 발견한 질문을 시장·지수·종목 근거로 확장합니다.")
```

- [ ] **Step 5: Migrate the existing page-shell assertion**

Replace the old caption assertion in `test_market_research_page_removes_overview_global_blocks` with:

```python
assert "Today에서 발견한 질문을 시장·지수·종목 근거로 확장합니다." in body
assert 'st.container(key="market_research_page_header")' in body
```

- [ ] **Step 6: Run GREEN and commit**

```bash
.venv/bin/python -m pytest tests/test_market_research_navigation.py -q -k 'page_uses_compact_keyed_header or page_removes_overview_global_blocks'
.venv/bin/python -m py_compile app/web/overview/page.py
git diff --check
git add app/web/overview/page.py tests/test_market_research_navigation.py
git commit -m "기능: Market Research 헤더 밀도 정리"
```

Expected: 2 tests pass; compile/diff checks exit 0; one focused commit is created.

---

### Task 2: Content-Width Family Rail And Local View Surface

**Files:**
- Modify: `tests/test_market_research_navigation.py`
- Modify: `app/web/overview/navigation.py`

**Interfaces:**
- Consumes: existing family/view labels, widget keys, query/session precedence, `_store_market_research_view`.
- Produces: `market_research_local_navigation_context(family: object) -> tuple[str, tuple[str, ...]]`, key `market_research_local_navigation`, and the same canonical view return value as today.

- [ ] **Step 1: Write failing context and CSS tests**

Import `_market_research_navigation_css` and `market_research_local_navigation_context`, then add:

```python
def test_market_research_local_navigation_context_covers_single_and_multi_view_families():
    assert market_research_local_navigation_context("market-environment") == (
        "시장 환경",
        ("economic-cycle", "futures-macro", "sentiment", "events"),
    )
    assert market_research_local_navigation_context("index-valuation") == (
        "지수 가치평가",
        ("sp500",),
    )
    assert market_research_local_navigation_context("unknown")[0] == "시장 환경"


def test_market_research_navigation_css_uses_compact_and_responsive_contract():
    css = _market_research_navigation_css()
    source = Path("app/web/overview/navigation.py").read_text(encoding="utf-8")
    assert ".st-key-market_research_local_navigation" in css
    assert "width: fit-content" in css
    assert 'button[aria-pressed="true"]' in css
    assert "repeat(3, minmax(0, 1fr))" in css
    assert "repeat(2, minmax(0, 1fr))" in css
    assert "button:only-child" in css
    assert "key=MARKET_RESEARCH_LOCAL_NAV_KEY" in source
```

- [ ] **Step 2: Run RED**

```bash
.venv/bin/python -m pytest tests/test_market_research_navigation.py -q -k 'local_navigation_context or navigation_css_uses_compact'
```

Expected: import/collection FAIL because the helper and local-nav key do not exist.

- [ ] **Step 3: Add the key and pure context helper**

```python
MARKET_RESEARCH_LOCAL_NAV_KEY = "market_research_local_navigation"


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
```

- [ ] **Step 4: Replace the navigation CSS**

Use this full scoped CSS body:

```css
.st-key-market_research_family_widget div[data-baseweb="button-group"] {
  display: flex; width: fit-content; max-width: 100%; gap: 0.25rem;
  padding: 0; border-bottom: 1px solid color-mix(in srgb, var(--text-color) 14%, transparent);
}
.st-key-market_research_family_widget button {
  width: auto !important; min-height: 2.35rem; padding: 0.4rem 0.75rem !important;
  border: 0 !important; border-bottom: 2px solid transparent !important;
  border-radius: 0 !important; background: transparent !important;
  color: color-mix(in srgb, var(--text-color) 66%, transparent) !important;
  box-shadow: none !important;
}
.st-key-market_research_family_widget button:hover {
  color: var(--text-color) !important;
  background: color-mix(in srgb, #7c96ad 7%, transparent) !important;
}
.st-key-market_research_family_widget button[aria-pressed="true"] {
  color: var(--text-color) !important; font-weight: 700 !important;
  border-bottom-color: #647b8f !important; background: transparent !important;
}
.st-key-market_research_local_navigation {
  margin: 0.15rem 0 0.7rem; padding: 0.8rem 0.95rem;
  border: 1px solid color-mix(in srgb, #7c96ad 26%, transparent) !important;
  border-radius: 0.85rem;
  background: color-mix(in srgb, #dce7ef 34%, var(--background-color));
}
.st-key-market_research_local_navigation [data-testid="stCaptionContainer"] { margin-bottom: 0.05rem; }
.st-key-market_research_local_navigation [data-testid="stMarkdownContainer"] p { margin: 0; }
.st-key-market_research_view_widget div[data-baseweb="button-group"] {
  display: flex; width: fit-content; max-width: 100%; flex-wrap: wrap; gap: 0.35rem;
}
.st-key-market_research_view_widget [data-testid="stBaseButton-pills"],
.st-key-market_research_view_widget [data-testid="stBaseButton-pillsActive"] {
  width: auto; min-height: 2.2rem; padding: 0.35rem 0.7rem;
  border-radius: 999px; box-shadow: none !important;
}
.st-key-market_research_view_widget [data-testid="stBaseButton-pills"] {
  border: 1px solid transparent !important; background: transparent !important;
  color: color-mix(in srgb, var(--text-color) 70%, transparent) !important;
}
.st-key-market_research_view_widget [data-testid="stBaseButton-pillsActive"] {
  border: 1px solid color-mix(in srgb, #647b8f 34%, transparent) !important;
  background: color-mix(in srgb, #b9ccda 30%, var(--background-color)) !important;
  color: var(--text-color) !important; font-weight: 700 !important;
}
@media (max-width: 760px) {
  .st-key-market_research_local_navigation [data-testid="stHorizontalBlock"] {
    flex-wrap: wrap;
  }
}
@media (max-width: 480px) {
  .st-key-market_research_family_widget div[data-baseweb="button-group"] {
    display: grid; width: 100%; grid-template-columns: repeat(3, minmax(0, 1fr));
  }
  .st-key-market_research_family_widget button { width: 100% !important; padding-inline: 0.3rem !important; white-space: normal; }
  .st-key-market_research_view_widget div[data-baseweb="button-group"] {
    display: grid; width: 100%; grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .st-key-market_research_view_widget [data-testid="stBaseButton-pills"],
  .st-key-market_research_view_widget [data-testid="stBaseButton-pillsActive"] { width: 100%; }
  .st-key-market_research_view_widget button:only-child { grid-column: 1 / -1; }
}
```

Wrap it in the existing `<style>...</style>` return string. Do not use `var(--primary-color)` because the app theme maps it to red.

- [ ] **Step 5: Replace the selector presentation while retaining state logic**

After resolving `current_view/current_family`, render the primary with `width="content"`. Resolve `family_label, family_views = market_research_local_navigation_context(selected_family)`, reset stale view-widget state exactly as today, and always render:

```python
with st.container(
    key=MARKET_RESEARCH_LOCAL_NAV_KEY,
    border=True,
    horizontal=True,
    horizontal_alignment="left",
    vertical_alignment="center",
    gap="medium",
):
    with st.container(width=150):
        st.caption("선택한 리서치")
        st.markdown(f"**{family_label}**")
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
```

Return `_store_market_research_view(str(selected_view))`. Render the one-item `S&P 500` control too, so family changes do not collapse the local surface. Export the new key/helper in `__all__`.

- [ ] **Step 6: Run focused/connected GREEN checks**

```bash
.venv/bin/python -m pytest tests/test_market_research_navigation.py -q
.venv/bin/python -m pytest tests/test_today_home.py -q
.venv/bin/python -m pytest tests/test_service_contracts.py -q -k '(overview or market_movers or market_research or today) and not market_sentiment_overlay_is_context_only_for_practical_validation and not market_sentiment_overlay_remains_context_only_on_downstream_surfaces'
.venv/bin/python -m py_compile app/web/overview/navigation.py app/web/overview/page.py
git diff --check
```

Expected: focused and connected scope selections pass. Record exact counts; do not claim unrelated full service-contract baseline failures are fixed.

- [ ] **Step 7: Commit Task 2**

```bash
git add app/web/overview/navigation.py tests/test_market_research_navigation.py
git commit -m "기능: Market Research 상단 탐색 계층 개선"
```

---

### Task 3: Browser QA, Documentation Sync, And Closeout

**Files:**
- Modify: task `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`
- Modify: `docs/PROJECT_MAP.md`, `docs/flows/README.md`, `docs/INDEX.md`, `docs/ROADMAP.md`
- Modify: `WORK_PROGRESS.md`, `QUESTION_AND_ANALYSIS_LOG.md`
- Create generated/unstaged: `market-research-top-navigation-qa.png`

**Interfaces:**
- Consumes: completed compact header/rail and local Streamlit runtime.
- Produces: actual responsive evidence, sticky decision, complete `3/3` status, durable documentation alignment.

- [ ] **Step 1: Start a fresh QA server and inspect actual `/overview`**

Use a free port and current worktree. Verify the eyebrow/header, content-width family rail, bounded local surface, all three family states, and all seven views.

- [ ] **Step 2: Verify responsive and navigation behavior**

At desktop, 760px, and 420px verify selected state without red, no excessive header/nav whitespace, no overlap, and no horizontal overflow. At 420px confirm exactly three primary columns and two secondary columns for multi-view families. Verify Today CTA and Market Movers -> U.S. Stock handoff.

- [ ] **Step 3: Decide sticky scope and capture evidence**

Scroll long Economic Cycle and Market Movers views. Record `sticky deferred/not needed in V1` unless repeated switching is materially blocked; if blocked, record evidence and request a separate approved follow-up rather than adding sticky CSS now. Save `market-research-top-navigation-qa.png` and keep it unstaged. Confirm browser warnings/errors are empty.

- [ ] **Step 4: Run final verification**

```bash
.venv/bin/python -m pytest tests/test_market_research_navigation.py tests/test_today_home.py -q
.venv/bin/python -m pytest tests/test_service_contracts.py -q -k '(overview or market_movers or market_research or today) and not market_sentiment_overlay_is_context_only_for_practical_validation and not market_sentiment_overlay_remains_context_only_on_downstream_surfaces'
.venv/bin/python -m py_compile app/web/overview/navigation.py app/web/overview/page.py
git diff --check
```

- [ ] **Step 5: Synchronize docs and commit closeout**

Record exact test counts/QA, `Roadmap: 3/3`, final visual/state/sticky decisions, and current ownership in task/durable docs. Stage only allow-listed docs and commit:

```bash
git commit -m "문서: Market Research 상단 개선 완료 기록"
```

## Plan Self-Review

- Spec coverage: header, content-width family rail, bounded local view surface, S&P single-view stability, responsive states, drawer exclusion, sticky decision, compatibility, Browser QA, and docs sync map to Tasks 1-3.
- Placeholder scan: no placeholder markers or implicit test steps remain; code snippets and exact verification commands are included.
- Type consistency: `_market_research_page_css() -> str`, `MARKET_RESEARCH_LOCAL_NAV_KEY`, and `market_research_local_navigation_context(family: object) -> tuple[str, tuple[str, ...]]` are consistent across tests and implementation.
- Scope check: no module renderer, service, loader, DB, provider, drawer, or sticky implementation is included.
