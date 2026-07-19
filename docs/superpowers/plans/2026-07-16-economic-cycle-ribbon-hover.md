# Economic Cycle Ribbon And Hover Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 최근 60개월 ribbon이 전체 너비를 채우게 하고 Cycle Map 지점 정보를 hover/focus 때만 보여준다.

**Architecture:** React가 실제 history 길이를 CSS custom property로 전달하고 CSS Grid가 이를 열 수로 사용한다. Cycle Map은 기존 확률 좌표 위에 데이터별 SVG hover group을 렌더링하며 CSS가 pointer hover와 keyboard focus 상태에서만 tooltip을 노출한다.

**Tech Stack:** React 18, TypeScript, SVG, CSS Grid, Vite, pytest source contracts, Playwright Browser QA.

## Global Constraints

- DB, service 60개월 read model, forecast probability와 validation status를 변경하지 않는다.
- 결측 지점 사이를 연결하거나 결측 tooltip을 합성하지 않는다.
- tooltip은 기본 상태에서 보이지 않고 hover/focus에서만 나타난다.
- desktop과 420px에서 가로 overflow가 없어야 한다.

---

### Task 1: Dynamic ribbon grid

**Files:**
- Modify: `tests/test_market_context_economic_cycle.py`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/style.css`

**Interfaces:**
- Consumes: `history: HistoryPoint[]`
- Produces: `--history-month-count` CSS custom property와 실제 history 개수 기반 grid

- [ ] **Step 1: Write the failing source contract**

Require `--history-month-count`, `history.length`, `repeat(var(--history-month-count)` and reject `repeat(121`.

- [ ] **Step 2: Verify RED**

Run:

```bash
uv run --with pytest python -m pytest tests/test_market_context_economic_cycle.py -k ribbon_grid -q
```

Expected: dynamic grid tokens are missing and hardcoded 121 remains.

- [ ] **Step 3: Implement minimal dynamic grid**

Add a typed `RibbonStyle` custom property and pass `Math.max(history.length, 1)` to the ribbon. Replace desktop/mobile hardcoded 121 columns with `repeat(var(--history-month-count), minmax(...))`.

- [ ] **Step 4: Verify GREEN**

Run the focused test and `npm run build`.

### Task 2: Hover-only cycle point tooltip

**Files:**
- Modify: `tests/test_market_context_economic_cycle.py`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/style.css`

**Interfaces:**
- Consumes: recent 12 history points and h0/h1/h2 horizons
- Produces: accessible `cycle-hover-target` groups and hidden-by-default SVG `cycle-tooltip`

- [ ] **Step 1: Write the failing source/CSS contract**

Require hover target, tooltip, keyboard `tabIndex`, `aria-label`, and hover/focus CSS selectors.

- [ ] **Step 2: Verify RED**

Run:

```bash
uv run --with pytest python -m pytest tests/test_market_context_economic_cycle.py -k hover_tooltip -q
```

Expected: tooltip tokens are missing.

- [ ] **Step 3: Implement tooltip helpers and SVG groups**

Create tooltip label/position helpers, retain only points with probabilities, and render tooltip groups after the visual paths so hit areas remain available. Use the same phase/confidence/status values already in the payload.

- [ ] **Step 4: Verify GREEN**

Run focused UI tests and the React production build.

### Task 3: Browser QA, docs, and commit

**Files:**
- Modify: economic-cycle active task `STATUS.md`, `NOTES.md`, `RUNS.md`
- Modify: finance root handoff logs and smallest stale durable UI docs

- [ ] **Step 1: Restart the local Streamlit process**

Use the existing port 8502 command so the rebuilt component and CSS are loaded.

- [ ] **Step 2: Run Browser QA**

Verify 62 ribbon cells fill the rendered ribbon width, historical and forecast tooltips appear only after hover/focus, console/page errors are empty, and mobile overflow is <= 1px.

- [ ] **Step 3: Run final verification**

Run the 10 economic-cycle/valuation test files, Python compile, React build, and `git diff --check`.

- [ ] **Step 4: Commit scoped files**

Exclude unrelated untracked research, `.superpowers/`, screenshots, and QA scripts.
