# Economic Cycle Interpretability & Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Make the economic-cycle screen reliably refresh the official RTDSM state and explain current state, recent movement, conditional transition direction, and unchanged asset pathways in the approved UI.

**Architecture:** Keep `Ingestion → DB → Loader → Service → React UI`. Replace the manual cycle refresh owner with the official RTDSM monthly publication path, enrich the compact observed-state contract, and adapt the React workbench without moving provider access into the UI. Preserve asset pathway calculations while deduplicating presentation.

**Tech Stack:** Python 3, pandas, MySQL loaders/writers, Streamlit, React 18, TypeScript, Vitest, Testing Library, pytest.

## Global Constraints

- Current phase uses confirmed RTDSM four-indicator state and two consecutive release confirmation.
- Transition pressure and destination probabilities remain unchanged and are presented as separate contracts.
- Asset pathway calculations and card content remain unchanged except removal of repeated common background and duplicate gold in commodities.
- UI must never fetch providers directly.
- Positive/negative color indicates direction, not favorable/unfavorable interpretation.
- Production code is written only after the corresponding failing test is observed.

---

### Task 1: Official Monthly Freshness and Refresh Pipeline

**Files:**
- Modify: `app/services/overview/economic_cycle_freshness.py`
- Modify: `app/jobs/economic_cycle_refresh.py`
- Modify: `app/jobs/overview_actions.py`
- Modify: `app/services/overview/economic_cycle.py`
- Test: `tests/test_economic_cycle_refresh.py`
- Test: `tests/test_economic_cycle_service.py`

**Interfaces:**
- Produces: `latest_closed_economic_cycle_month_end(value) -> date`
- Produces: `build_economic_cycle_freshness(snapshot, today=...) -> dict`
- Produces: `run_economic_cycle_official_refresh(as_of_date=...) -> JobResult`
- Consumes: `run_collect_economic_cycle_rtdsm_history`, `rollover_closed_economic_cycle_month`, `load_cycle_snapshot(run_kind="current")`

- [x] **Step 1: Write failing freshness tests**

Add literal assertions that 2026-08-17 targets 2026-07-31, a current 2026-07-31 snapshot is READY, a 2026-06-30 snapshot is REFRESH_AVAILABLE, and a missing snapshot is MISSING.

- [x] **Step 2: Run freshness tests and confirm RED**

Run: `.venv/bin/pytest tests/test_economic_cycle_service.py -k 'freshness or closed_month' -q`

Expected: existing weekday target reports 2026-08-17 and fails the month-end assertions.

- [x] **Step 3: Implement official snapshot freshness**

Use `pandas.offsets.MonthEnd(1)` or calendar arithmetic to resolve the last closed month and compare the `current` snapshot date, not an intramonth row. Preserve per-scope messages and expose action only when stale.

- [x] **Step 4: Write failing official refresh job tests**

Assert that the cycle scope calls the RTDSM collection runner once, publishes the closed month once, reads `run_kind="current"` before/after, and never calls the legacy intramonth materializer.

- [x] **Step 5: Run refresh job tests and confirm RED**

Run: `.venv/bin/pytest tests/test_economic_cycle_refresh.py -q`

Expected: tests fail because `run_economic_cycle_official_refresh` does not exist and overview refresh still requests `intramonth_nowcast`.

- [x] **Step 6: Implement the RTDSM official refresh path**

Collect four RTDSM sources, fail closed on provider gaps, call confirmed monthly rollover/publication, and verify exact target month from the persisted `current` snapshot. Keep the existing asset scope runner and scope-level result accounting.

- [x] **Step 7: Run focused Python tests and commit**

Run: `.venv/bin/pytest tests/test_economic_cycle_refresh.py tests/test_economic_cycle_service.py -q`

Commit files from this task with message: `경제사이클 공식 월말 갱신 경로 정렬`.

### Task 2: RTDSM Quality, Comparison Dates, and Current Evidence

**Files:**
- Modify: `finance/economic_cycle_realtime_history.py`
- Modify: `finance/economic_cycle_transition_production.py`
- Modify: `app/services/overview/economic_cycle.py`
- Test: `tests/test_economic_cycle_realtime_history.py`
- Test: `tests/test_economic_cycle_transition_production.py`
- Test: `tests/test_economic_cycle_service.py`

**Interfaces:**
- Produces observed state keys: `available_series`, `total_series`, `series_quality`
- Produces recent change keys: `comparison_start_date`, `comparison_end_date`
- Produces UI `evidence` derived from the same current RTDSM observed state
- Preserves legacy snapshot `top_evidence_json` for asset interpretation inputs only

- [x] **Step 1: Write failing RTDSM quality tests**

Build a four-series panel fixture where RUC is 121 days behind the origin and assert `data_status == "READY"`, `available_series == 4`, `total_series == 4`, and `series_quality` identifies RUC as quarterly with a release lag rather than missing data.

- [x] **Step 2: Run quality tests and confirm RED**

Run: `.venv/bin/pytest tests/test_economic_cycle_realtime_history.py -q`

Expected: RUC is marked stale at 121 days and quality fields are absent.

- [x] **Step 3: Implement cadence-aware quality metadata**

Set the quarterly stale boundary to 150 days, retain the monthly 75-day boundary, and persist compact per-series cadence/date/status metadata into each observed state.

- [x] **Step 4: Write failing service contract tests**

Assert the July snapshot returns comparison windows `2026-06 → 2026-07`, `2026-04 → 2026-07`, `2026-01 → 2026-07`; coverage is `4/4`; and `evidence` values equal the current observed state activity/labor values instead of legacy top evidence values.

- [x] **Step 5: Run service tests and confirm RED**

Run: `.venv/bin/pytest tests/test_economic_cycle_service.py -q`

Expected: comparison dates and quality metadata are missing, denominator semantics are not explicit, and evidence comes from legacy `top_evidence_json`.

- [x] **Step 6: Implement read-model separation**

Decode current evidence from `observed_state_json`; pass the legacy evidence only into `build_market_implications`; add exact comparison dates using the official snapshot month; normalize unavailable revision copy as a pending future-vintage comparison.

- [x] **Step 7: Run focused tests and commit**

Run: `.venv/bin/pytest tests/test_economic_cycle_realtime_history.py tests/test_economic_cycle_transition_production.py tests/test_economic_cycle_service.py -q`

Commit files from this task with message: `RTDSM 현재 국면 품질 계약 보강`.

### Task 3: Diagnosis, Cycle Route, Transition, Evidence, and Ribbon UI

**Files:**
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/style.css`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.test.tsx`
- Test: `tests/test_market_context_economic_cycle.py`

**Interfaces:**
- Consumes enriched `observed_state`, `recent_changes`, `transition_forecast`, `cycle_map`, `evidence`
- Produces accessible `CurrentObservedState`, `CycleRouteMap`, grouped forecast drivers, judgment summary, and confirmed-state ribbon

- [x] **Step 1: Write failing React behavior tests**

Render a literal recovery fixture and assert visible comparison dates, `4/4`, migration explanation, current judgment, separate raising/lowering driver headings, conditional probability boundary, and route side cards of equal semantic roles.

- [x] **Step 2: Run component tests and confirm RED**

Run: `npm test -- --run EconomicCycleWorkbench.test.tsx` in `app/web/streamlit_components/economic_cycle_workbench`.

Expected: new copy and grouped structures are absent.

- [x] **Step 3: Implement current diagnosis and quality strip**

Replace role labels such as `최신 변화 감지` with exact `N개월 전 대비`, render start/end month, composite delta, `개선 지표 N/4`, and the three quality explanations. Add the RTDSM method migration disclosure in the current phase card.

- [x] **Step 4: Implement the approved Cycle route**

Keep the standard phase order, use a square SVG/viewBox, place the visual and two same-height side cards in a wide grid, and render the conditional primary path as an amber dashed arrow while preserving all alternative probabilities in text.

- [x] **Step 5: Implement transition and evidence hierarchy**

Add the consolidated judgment first; separate pressure probability from conditional destination probability; group drivers by `RAISES_PRESSURE` and `LOWERS_PRESSURE`; collapse neutral drivers; show current RTDSM evidence under the judgment instead of the legacy forecast-context group.

- [x] **Step 6: Implement ribbon and disclosure consistency**

Infer phase-change months from adjacent confirmed points, display a transition summary, replace unavailable confidence/revision tooltip lines with official phase/transition status, and give both disclosures the same closed summary structure and chevron.

- [x] **Step 7: Fix the React refresh state regression test**

Use Testing Library to click refresh, rerender with a success and then a failed `refresh_result`, and assert the button returns from collecting state in both cases. Implement `useEffect` keyed by result/freshness identity to reset state.

- [x] **Step 8: Run React tests, typecheck, build, and commit**

Run in component directory:

```bash
npm test
npm run typecheck
npm run build
```

Run: `.venv/bin/pytest tests/test_market_context_economic_cycle.py -q`

Commit files from this task with message: `경제사이클 진단과 순환 경로 UI 개편`.

### Task 4: Preserve Asset Cards While Removing Repetition

**Files:**
- Modify: `finance/economic_cycle_asset_pathways.py`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/style.css`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.test.tsx`
- Test: `tests/test_economic_cycle_asset_prices.py`
- Test: `tests/test_market_context_economic_cycle.py`

**Interfaces:**
- Consumes unchanged `MarketImplication` and `EconomicState` contracts
- Produces one section-level common economic background
- Produces commodities `assets == [wti, copper]`
- Produces reusable signed `SeriesMetrics` cells for 21d and 63d

- [x] **Step 1: Write failing deduplication tests**

Assert the commodities context has WTI and copper but no gold, the standalone gold implication remains, and rendered HTML contains the common background exactly once while retaining every asset card heading and observation block heading.

- [x] **Step 2: Run asset tests and confirm RED**

Run: `.venv/bin/pytest tests/test_economic_cycle_asset_prices.py tests/test_market_context_economic_cycle.py -q`

Expected: commodities includes gold and every card renders `EconomicStateBlock`.

- [x] **Step 3: Implement presentation-only deduplication**

Remove the reused gold asset from `build_commodities_context`, render one `SharedEconomicBackground` before `implication-grid`, and remove only the card-level `EconomicStateBlock` call. Do not change current movement, observed pathways, interpretation, next checks, or coverage calculations outside the removed asset.

- [x] **Step 4: Write failing signed metric tests**

Render +7.0bp, -20.0bp, and -0.0bp fixtures and assert `▲ +7.0bp` uses positive class, `▼ -20.0bp` uses negative class, and zero normalizes to `— 0.0bp` with flat class. Assert 21d and 63d each occupy a separate metric cell in current movement and observed pathways.

- [x] **Step 5: Implement signed period cells and legend**

Create a direction classifier with an epsilon that treats formatted negative zero as flat, reuse it in `SeriesMetrics` and price returns, and add the explicit `방향 표시이며 좋고 나쁨을 뜻하지 않음` legend.

- [x] **Step 6: Run asset/React tests, build, and commit**

Run:

```bash
.venv/bin/pytest tests/test_economic_cycle_asset_prices.py tests/test_market_context_economic_cycle.py -q
cd app/web/streamlit_components/economic_cycle_workbench
npm test
npm run typecheck
npm run build
```

Commit files from this task with message: `자산 확인 포인트 중복 제거와 기간 비교 개선`.

### Task 5: Integration Verification, Browser QA, and Documentation

**Files:**
- Modify: `.aiworkspace/note/finance/tasks/active/economic-cycle-interpretability-refresh-v1-20260817/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/economic-cycle-interpretability-refresh-v1-20260817/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/economic-cycle-interpretability-refresh-v1-20260817/NOTES.md`
- Modify: `.aiworkspace/note/finance/tasks/active/economic-cycle-interpretability-refresh-v1-20260817/RISKS.md`
- Modify only if triggered: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`, `.aiworkspace/note/finance/docs/flows/*`, `.aiworkspace/note/finance/docs/data/*`

**Interfaces:**
- Produces one verified Streamlit economic-cycle surface and a durable test/run record

- [x] **Step 1: Run full focused regression suite**

Run:

```bash
.venv/bin/pytest \
  tests/test_economic_cycle_refresh.py \
  tests/test_economic_cycle_realtime_history.py \
  tests/test_economic_cycle_transition_production.py \
  tests/test_economic_cycle_service.py \
  tests/test_economic_cycle_asset_prices.py \
  tests/test_market_context_economic_cycle.py -q
```

- [x] **Step 2: Run repository hygiene checks**

Run:

```bash
git diff --check
.venv/bin/python -m py_compile \
  app/services/overview/economic_cycle_freshness.py \
  app/jobs/economic_cycle_refresh.py \
  app/jobs/overview_actions.py \
  app/services/overview/economic_cycle.py \
  finance/economic_cycle_realtime_history.py \
  finance/economic_cycle_asset_pathways.py
```

- [x] **Step 3: Perform Browser QA on the real Streamlit page**

Open `http://localhost:8503/overview?view=economic-cycle&overview_tab=economic-cycle` and verify desktop plus narrow viewport: freshness no longer falsely requests a daily refresh; recovery/7 months and exact comparison windows appear; route is not distorted; pressure/destination and grouped drivers are readable; ribbon tooltips name month and transition; common economic background appears once; asset cards retain all existing sections; 21d/63d signed cells show correct colors.

- [x] **Step 4: Save one QA screenshot outside tracked source**

Save a generated screenshot such as `economic-cycle-interpretability-refresh-v1-qa.png` and do not stage it.

- [x] **Step 5: Update task and canonical documentation**

Record commands/results in `RUNS.md`, implementation decisions in `NOTES.md`, unresolved provider/runtime caveats in `RISKS.md`, and set `STATUS.md` to `complete` only if all required checks pass. Update canonical docs only if owner boundaries or durable data semantics changed.

- [x] **Step 6: Final integration commit**

Stage only task-owned source, tests, and documentation. Exclude registries, run history, `.superpowers`, screenshots, and `run_artifacts`. Commit with message: `경제사이클 해석성과 갱신 흐름 통합 검증`.

