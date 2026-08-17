# Market Research Flat Navigation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Flatten Market Research so 경기 국면 and 물가·정책 are sibling views and keep mobile subtabs in a compact one-line rail.

**Architecture:** Python remains the canonical route/session owner and adds `inflation-policy` as a view. Both 경기 국면 and 물가·정책 reuse the economic-cycle transport, while the React workbench becomes controlled by a Python-provided selected view and removes its duplicate inner tab state.

**Tech Stack:** Python 3.12, Streamlit, React 18, TypeScript, Vitest, Vite, pytest

## Global Constraints

- Keep `/overview` and existing `economic-cycle` deep links compatible.
- Do not change provider, DB, loader, calculation, refresh, or command semantics.
- Mobile subtabs must not use a two-column stretched grid.
- Mobile subtabs must remain one compact row and allow bounded horizontal swipe only when the labels cannot fit.
- Do not add sticky navigation, drawer, status panel, or operational diagnostics.

---

### Task 1: Canonical navigation and direct renderer routes

**Files:**
- Modify: `tests/test_market_research_navigation.py`
- Modify: `app/web/overview/navigation.py`
- Modify: `app/web/overview/page.py`

**Interfaces:**
- Produces: canonical view `inflation-policy`, label mapping `economic-cycle -> 경기 국면`, and direct renderer dispatch for both analysis views.

- [ ] Write failing Python tests that expect eight canonical views, five market-environment views, direct `inflation-policy` event acceptance, and distinct renderer dispatch.
- [ ] Run `.venv/bin/python -m pytest tests/test_market_research_navigation.py -q` and confirm the failures are caused by the missing view and old label.
- [ ] Add `inflation-policy` to the canonical view tuple, label and family maps; route page renderers to `render_economic_cycle(selected_view="cycle")` and `render_economic_cycle(selected_view="inflation")`.
- [ ] Re-run the focused pytest file and confirm it passes.

### Task 2: Controlled economic analysis surface

**Files:**
- Modify: `tests/test_market_context_economic_cycle.py`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/InflationPolicyWorkbench.test.tsx`
- Modify: `app/web/overview/economic_cycle_react_component.py`
- Modify: `app/web/overview/market_context_helpers.py`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/style.css`

**Interfaces:**
- Consumes: `selected_view: "cycle" | "inflation"` from Python renderer.
- Produces: one directly selected workbench with no nested `경제 분석 보기` tablist.

- [ ] Write failing Python and React tests proving the bridge forwards `selected_view`, `cycle` renders 경기 국면, `inflation` renders 물가·정책, and neither render contains the old inner tablist.
- [ ] Run the focused pytest and economic-cycle Vitest tests and confirm expected failures.
- [ ] Add selected-view normalization in Python, pass the argument through the component bridge, make the React view controlled, and delete the inner navigation markup/styles.
- [ ] Re-run both focused suites and confirm they pass.

### Task 3: A-style navigation and compact mobile subtabs

**Files:**
- Modify: `app/web/streamlit_components/market_research_navigation/src/MarketResearchNavigation.test.tsx`
- Modify: `app/web/streamlit_components/market_research_navigation/src/style.css`
- Modify: `app/web/overview/navigation.py`

**Interfaces:**
- Consumes: five market-environment views in the navigation payload.
- Produces: desktop editorial rail and mobile single-row view rail.

- [ ] Update the React fixture and assertions to require `경기 국면`, `물가·정책`, and all five sibling tabs.
- [ ] Run navigation Vitest and confirm the old four-view fixture/label fails.
- [ ] Replace the mobile two-column view grid with a nowrap row, compact padding, bounded overflow-x, hidden visual scrollbar, and underline-focused selected state; mirror the contract in the Streamlit fallback CSS.
- [ ] Re-run navigation Vitest and focused Python tests.

### Task 4: Build, browser QA, docs and commit

**Files:**
- Update generated production bundles under both modified React components.
- Update: `.aiworkspace/note/finance/tasks/active/market-research-flat-navigation-v1-20260817/`
- Update canonical docs only when implemented ownership facts changed.

**Interfaces:**
- Produces: deployable bundles, QA evidence, and a coherent task closeout.

- [ ] Run both component typechecks, Vitest suites, and Vite production builds.
- [ ] Run focused Python tests, `py_compile`, `git diff --check`, and inspect `git status --short`.
- [ ] Start the real Streamlit app and Browser-QA `/overview?overview_tab=economic-cycle` and `/overview?overview_tab=inflation-policy` at desktop, 736px, and 360px; verify the mobile rail does not cover the module and console errors are zero.
- [ ] Save one generated QA screenshot without staging it.
- [ ] Update task STATUS/NOTES/RUNS/RISKS, record whether canonical docs changed, self-review the diff, request code review, fix valid findings, and commit only task-owned files.

