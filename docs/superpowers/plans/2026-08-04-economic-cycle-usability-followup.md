# Economic Cycle Usability Follow-up Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make freshness state, actual-cycle checkpoints, current-versus-anchor transition meaning, and the 12-month phase ribbon immediately understandable without changing the asset checkpoint surface.

**Architecture:** Extend the deterministic observed-state transition record with persistent anchor metadata, normalize legacy metadata in the DB-only Overview service, and keep the 12-month payload while selecting four chart checkpoints in React. Freshness remains synchronous and fail-closed, but the read model and UI distinguish check time, calculation cutoff, and actual source observation date.

**Tech Stack:** Python 3, pandas, pytest, React 18, TypeScript, Vitest, Vite, Streamlit custom components, CSS.

## Global Constraints

- Preserve `market_implications` and `MarketImplicationCard` behavior, copy, order and CSS.
- Do not expose transition target as a probability forecast.
- Do not fetch providers from the UI read path.
- Keep `cycle_map.points` at up to 12 points for the regime ribbon.
- Do not create a run/job diagnostics panel.
- Follow red-green-refactor for every behavior change.

---

### Task 1: Persist active transition-anchor provenance

**Files:**
- Modify: `finance/economic_cycle_observed_state.py`
- Test: `tests/test_economic_cycle_observed_state_v1.py`

**Interfaces:**
- Consumes: sequential PIT feature rows used by `build_observed_state_history()`.
- Produces: `transition_monitor` fields `anchor_started_at: str | None`, `anchor_source: "INITIALIZED" | "CONFIRMED" | None`, and `anchor_confirmed_at: str | None`.

- [ ] **Step 1: Write failing initialization and promotion tests**

Add assertions proving the initial anchor records its first valid origin as `INITIALIZED`, and a promoted anchor retains the prior confirmation origin as `CONFIRMED` on later rows.

- [ ] **Step 2: Run the focused tests and verify RED**

Run: `.venv/bin/pytest tests/test_economic_cycle_observed_state_v1.py -q`

Expected: failure because the three anchor provenance fields are absent.

- [ ] **Step 3: Implement minimal sequential provenance state**

Track `anchor_started_at`, `anchor_source`, `anchor_confirmed_at`, and a pending confirmation date beside the existing pending anchor. Initialize them only on the first valid phase and update them only when a confirmed target is promoted.

- [ ] **Step 4: Run focused tests and verify GREEN**

Run: `.venv/bin/pytest tests/test_economic_cycle_observed_state_v1.py -q`

Expected: all tests pass.

### Task 2: Normalize legacy transition meaning and freshness dates

**Files:**
- Modify: `app/services/overview/economic_cycle.py`
- Modify: `app/services/overview/economic_cycle_freshness.py`
- Test: `tests/test_economic_cycle_service.py`
- Test: `tests/test_economic_cycle_freshness.py`

**Interfaces:**
- Consumes: current snapshot, monthly history snapshots, and intramonth source coverage.
- Produces: normalized anchor provenance labels plus `last_checked_at` and `latest_source_observation_date` in `data_freshness`.

- [ ] **Step 1: Write failing service tests**

Add literal fixtures proving a persisted `CONFIRMED` anchor wins, a legacy first-seen anchor is labeled `LEGACY_OBSERVED`, and source dates are derived from `source_coverage.series[*].latest_observation_date` without replacing the calculation cutoff.

- [ ] **Step 2: Run focused tests and verify RED**

Run: `.venv/bin/pytest tests/test_economic_cycle_service.py tests/test_economic_cycle_freshness.py -q`

Expected: failures for missing normalized provenance and freshness fields.

- [ ] **Step 3: Implement normalization**

Pass history rows into `_transition_monitor`, search chronological monitor records for a confirmed transition into the active anchor, fall back to first anchor observation with `LEGACY_OBSERVED`, and expose Korean basis labels. Parse source collection and observation dates defensively in the freshness builder.

- [ ] **Step 4: Run focused tests and verify GREEN**

Run: `.venv/bin/pytest tests/test_economic_cycle_service.py tests/test_economic_cycle_freshness.py -q`

Expected: all tests pass and JSON serialization remains finite.

### Task 3: Render current-first transition semantics and four chart checkpoints

**Files:**
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx`
- Test: `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.test.tsx`

**Interfaces:**
- Consumes: `CyclePayload.transition_monitor`, `observed_state`, and 12-month `cycle_map.points`.
- Produces: exported pure helpers `selectCycleMapCheckpoints()` and `resolveMapDirectionPhase()` plus current-first markup.

- [ ] **Step 1: Write failing React tests**

Assert that the four selected points are 6M/3M/1M/current, non-adjacent contraction resolves the structural arrow to recovery rather than expansion, the card says `현재 관측` before `전환 기준 앵커`, and conditions are labeled with their exact anchor-to-target route.

- [ ] **Step 2: Run Vitest and verify RED**

Run: `npm test -- --run EconomicCycleWorkbench.test.tsx`

Working directory: `app/web/streamlit_components/economic_cycle_workbench`

Expected: failures for the missing 1M label, helpers, and current-first copy.

- [ ] **Step 3: Implement minimal helpers and markup**

Select indexes `length-7`, `length-4`, `length-2`, `length-1` with stable de-duplication. Resolve non-adjacent direction from the current observed phase sequence. Pass observed state to the transition panel and separate current observation, anchor reference, structural target, and route-specific conditions.

- [ ] **Step 4: Run Vitest and verify GREEN**

Run: `npm test -- --run EconomicCycleWorkbench.test.tsx`

Expected: all component tests pass, including the five frozen asset blocks.

### Task 4: Add truthful freshness feedback and accessible ribbon details

**Files:**
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/style.css`
- Test: `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.test.tsx`

**Interfaces:**
- Consumes: normalized freshness fields and each `CyclePoint`.
- Produces: structured date labels, expected-duration button feedback, four-color legend, and hover/focus tooltips.

- [ ] **Step 1: Write failing markup tests**

Assert all four phase legend labels, a tooltip containing month/phase/NBER/confidence, the separated freshness labels, and `보통 1분 내외` are present.

- [ ] **Step 2: Run Vitest and verify RED**

Run: `npm test -- --run EconomicCycleWorkbench.test.tsx`

Expected: failures because the current ribbon uses one generic legend and native title only.

- [ ] **Step 3: Implement markup and CSS**

Render phase-specific legend swatches, add a focusable custom tooltip per month, allow tooltip overflow with first/last alignment, and add structured freshness metadata without adding a job diagnostics panel.

- [ ] **Step 4: Run tests and production build**

Run: `npm test && npm run build`

Expected: Vitest passes and Vite writes the `component_static` bundle successfully.

### Task 5: Integrated verification, Browser QA and closeout

**Files:**
- Modify: `.aiworkspace/note/finance/tasks/active/economic-cycle-usability-followup-v2-20260804/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/economic-cycle-usability-followup-v2-20260804/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/economic-cycle-usability-followup-v2-20260804/RISKS.md`

**Interfaces:**
- Consumes: completed domain, service, component and build outputs.
- Produces: verification evidence, one generated Browser QA screenshot, and a coherent implementation commit.

- [ ] **Step 1: Run the full focused Python suite**

Run: `.venv/bin/pytest tests/test_economic_cycle_observed_state_v1.py tests/test_economic_cycle_freshness.py tests/test_economic_cycle_service.py tests/test_economic_cycle_refresh.py tests/test_market_context_economic_cycle.py -q`

Expected: all tests pass.

- [ ] **Step 2: Run static checks**

Run: `.venv/bin/python -m py_compile finance/economic_cycle_observed_state.py app/services/overview/economic_cycle.py app/services/overview/economic_cycle_freshness.py && git diff --check`

Expected: exit 0 with no whitespace errors.

- [ ] **Step 3: Verify live Streamlit UI**

Open the existing economic-cycle Overview route, reload the component, verify desktop layout, hover/focus one ribbon month, and capture one screenshot outside the staged source set.

- [ ] **Step 4: Review frozen asset boundary**

Inspect `git diff` and confirm no asset-pathway calculation or `MarketImplicationCard` subtree/CSS changed.

- [ ] **Step 5: Close task docs and commit**

Record exact commands/results, remaining latency risk, and `canonical doc change 없음` when no high-level ownership or product-boundary fact changed. Stage only task-owned source, tests, built component assets, plan and task docs; exclude registries, run history and generated screenshots.
