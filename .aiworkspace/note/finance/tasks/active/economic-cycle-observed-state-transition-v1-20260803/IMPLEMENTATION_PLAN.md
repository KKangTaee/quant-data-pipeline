# Economic Cycle Observed State / Transition V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the public current/+1M/+2M probability workflow with a PIT observed-state diagnosis, recent 1/3/6-month changes, and an adjacent-phase transition monitor while preserving the existing asset-checkpoint output and presentation.

**Architecture:** A new Streamlit-free domain module consumes the existing PIT feature panel and produces deterministic observed-state, recent-change, and transition-monitor records. The pipeline persists those records additively in `economic_cycle_snapshot`; the Overview service publishes an `economic_cycle_v3` read model; the React workbench renders actual coordinates and conditional transition evidence. Gaussian horizon artifacts remain shadow-compatible but do not drive the product read model.

**Tech Stack:** Python 3.12, pandas, dataclasses, MySQL schema/UPSERT conventions, pytest, React 18, TypeScript 5, Vite 6, Vitest, React DOM server rendering, Streamlit custom components.

## Global Constraints

- Public phase vocabulary is `recovery / expansion / slowdown / contraction`, rendered as `회복 / 확장 / 둔화 / 위축`.
- Current phase authority is the PIT observed coordinate; NBER chronology is a separate ex-post reference and never overrides it.
- Formula is `raw_level_t = 0.5 * activity_score_t + 0.5 * labor_income_score_t`, `level_t = mean(raw_level_t, t-1, t-2)`, `momentum_t = level_t - level_t-3`.
- Real-economy breadth uses only `INDPRO`, `W875RX1`, `RRSFS`, `CFNAI`, `PAYEMS`, `UNRATE`, `ICSA`, `AWHMAN` after existing direction normalization.
- Product payload must not expose horizons, forecast probabilities, confidence percentages, `forecast_markers`, or +1M/+2M expected phases.
- `finance/economic_cycle_asset_pathways.py`, asset-context logic in `finance/economic_cycle_interpretation.py`, `MarketImplicationCard`, commodity sub-card, asset order, asset copy blocks, and existing asset CSS are frozen.
- Same evidence/market/price/earnings/reference-date input must produce a deep-equal `market_implications` subtree before and after the service migration.
- Intramonth data is provisional, does not replace the month-end headline, and never advances transition persistence.
- UI never fetches provider data directly; the boundary remains ingestion → DB → loader → service → React.
- Do not stage the pre-existing registry JSONL, run-history JSONL, QA PNGs, `.superpowers/`, or `run_artifacts/`.
- Multi-agent dispatch is disabled for this task; execute inline with `superpowers:executing-plans`.

---

### Task 1: Observed-State And Transition Domain

**Files:**
- Create: `finance/economic_cycle_observed_state.py`
- Create: `tests/test_economic_cycle_observed_state_v1.py`

**Interfaces:**
- Consumes: `pandas.DataFrame` rows from `build_monthly_feature_panel()`, including `forecast_origin`, factor scores, the eight real-economy `*_z` / `*_stale` fields, and optional `USREC_signal`.
- Produces: `ObservedStateResult(observed_state: dict[str, object], recent_changes: tuple[dict[str, object], ...], transition_monitor: dict[str, object])`.
- Produces: `build_observed_state_history(panel, *, revised_panel=None) -> tuple[ObservedStateResult, ...]` and `build_observed_state_snapshot(panel, *, revised_panel=None) -> ObservedStateResult`.

- [x] **Step 1: Write failing formula and eligibility tests**

  Add literal fixtures covering all four zero-tie quadrants, the six monthly values needed for two non-overlapping three-month means, eight/fresh versus six/stale versus five-series coverage, and exact breadth values.

  ```python
  result = module.build_observed_state_snapshot(panel)
  assert result.observed_state["level"] == pytest.approx(-0.5)
  assert result.observed_state["momentum"] == pytest.approx(0.5)
  assert result.observed_state["phase"] == "recovery"
  assert result.observed_state["data_status"] == "READY"
  ```

- [x] **Step 2: Run the focused tests and verify RED**

  Run: `.venv/bin/python -m pytest tests/test_economic_cycle_observed_state_v1.py -q`

  Expected: collection/import failure because `finance.economic_cycle_observed_state` does not exist.

- [x] **Step 3: Implement deterministic coordinates, breadth, recent changes, and confidence**

  Implement immutable constants and the public result dataclass. Emit `UNAVAILABLE` when fewer than six real-economy series or either required factor is missing; emit `LIMITED` for six/seven series or any stale available series. Confidence is `HIGH` only for READY + STABLE revision quadrant + two observed months in the same quadrant + breadth support on both axes; it is never a number.

  ```python
  @dataclass(frozen=True)
  class ObservedStateResult:
      observed_state: dict[str, object]
      recent_changes: tuple[dict[str, object], ...]
      transition_monitor: dict[str, object]

  def build_observed_state_snapshot(
      panel: pd.DataFrame,
      *,
      revised_panel: pd.DataFrame | None = None,
  ) -> ObservedStateResult:
      history = build_observed_state_history(panel, revised_panel=revised_panel)
      if not history:
          raise LookupError("No economic-cycle feature rows are available")
      return history[-1]
  ```

- [x] **Step 4: Write failing transition-state tests**

  Cover initialization, first boundary crossing with anchor retained, `WATCH 0/3`, two-release persistence, diffusion, activity/labor corroboration, confirmation on the release where all three conditions pass, anchor promotion on the next valid release, candidate reversal, unavailable-month streak break, and non-adjacent shock handling.

  ```python
  assert crossing.observed_state["phase"] == "recovery"
  assert crossing.transition_monitor["anchor_phase"] == "contraction"
  assert crossing.transition_monitor["target_phase"] == "recovery"
  assert crossing.transition_monitor["status"] == "WATCH"
  ```

- [x] **Step 5: Run transition tests and verify RED for missing state behavior**

  Run: `.venv/bin/python -m pytest tests/test_economic_cycle_observed_state_v1.py -q`

  Expected: formula cases pass; transition cases fail because the anchor state machine is not implemented.

- [x] **Step 6: Implement the sequential anchor/target state machine and revised-history diagnostic**

  Use the sequence `recovery -> expansion -> slowdown -> contraction -> recovery`. Persist condition records with `MET / UNMET / UNAVAILABLE`; leading and inflation-policy factors produce `TOWARD_TARGET / SUPPORT_CURRENT / MIXED` context but never contribute to `conditions_met`. Compare the PIT phase with the same-origin phase from `revised_panel` to emit `STABLE / SENSITIVE / UNAVAILABLE`.

- [x] **Step 7: Verify Task 1 GREEN and commit**

  Run:

  ```bash
  .venv/bin/python -m pytest tests/test_economic_cycle_observed_state_v1.py -q
  .venv/bin/python -m pytest tests/test_economic_cycle_features.py -q
  ```

  Commit files with message: `기능: 경제사이클 관측 국면과 전환 상태 추가`.

---

### Task 2: Snapshot Schema, Materialization, And Loader Contract

**Files:**
- Modify: `finance/data/db/schema.py`
- Modify: `finance/data/economic_cycle_results.py`
- Modify: `finance/loaders/economic_cycle.py`
- Modify: `finance/economic_cycle_pipeline.py`
- Modify: `tests/test_economic_cycle_results.py`
- Modify: `tests/test_economic_cycle_pipeline.py`

**Interfaces:**
- Consumes: Task 1 `build_observed_state_snapshot()` and the loader's full PIT/revised panels.
- Produces: nullable `observed_state_json`, `recent_changes_json`, `transition_monitor_json` columns and writer/loader round-trip.
- Produces: `EconomicCyclePipelineLoader.load_prediction_panel(as_of_date) -> pd.DataFrame` and `load_revised_prediction_panel(as_of_date) -> pd.DataFrame`.
- Produces: `CycleSnapshot.observed_state`, `recent_changes`, and `transition_monitor` optional fields while retaining legacy shadow horizon fields.

- [x] **Step 1: Write failing additive schema and UPSERT tests**

  Require `current_phase ENUM('recovery','expansion','slowdown','recession','contraction')`, three nullable LONGTEXT columns, an in-place current-phase ENUM migration, default `None` values for legacy caller rows, and all three columns in INSERT/UPDATE SQL.

  ```python
  assert "observed_state_json LONGTEXT NULL" in snapshot_sql
  assert stored_snapshot["transition_monitor_json"] is None
  assert "observed_state_json = VALUES(observed_state_json)" in connection.sql[-1]
  ```

- [x] **Step 2: Run result tests and verify RED**

  Run: `.venv/bin/python -m pytest tests/test_economic_cycle_results.py -q`

  Expected: assertions fail because the new columns and ENUM migration do not exist.

- [x] **Step 3: Implement additive schema sync and round-trip persistence**

  Extend the table definition and add `_sync_snapshot_current_phase_enum()` beside the existing run-kind migration. Normalize all new JSON fields with `setdefault(..., None)` and update INSERT/UPSERT column lists without rewriting existing rows.

- [x] **Step 4: Write failing pipeline integration tests**

  Provide a fake loader with seven literal PIT panel rows and a revised panel. Assert persisted `current_phase` equals `observed_state_json.phase`, all three JSON fields are canonical JSON, h0 probabilities may remain stored but do not overwrite the phase, and origin-specific replay coordinates differ when input history differs.

  ```python
  row = writer.rows[-1]
  observed = json.loads(row["observed_state_json"])
  assert row["current_phase"] == observed["phase"] == "contraction"
  assert json.loads(row["transition_monitor_json"])["conditions_total"] == 3
  ```

- [x] **Step 5: Run pipeline tests and verify RED**

  Run: `.venv/bin/python -m pytest tests/test_economic_cycle_pipeline.py -q`

  Expected: new persisted fields are absent and `current_phase` still comes from h0 argmax.

- [x] **Step 6: Implement panel loaders and observed-state materialization**

  `load_prediction_panel()` returns the safe PIT prefix. `load_revised_prediction_panel()` loads the latest eligible versions at the loader's materialization/replay cutoff, removes revision-interval columns, and rebuilds the same monthly transforms for a revision diagnostic only. Materialization calls Task 1, writes its three JSON records, uses its phase for `current_phase`, and retains shadow probability JSON strictly for compatibility.

- [x] **Step 7: Verify Task 2 GREEN and commit**

  Run:

  ```bash
  .venv/bin/python -m pytest tests/test_economic_cycle_results.py tests/test_economic_cycle_pipeline.py -q
  .venv/bin/python -m py_compile finance/economic_cycle_observed_state.py finance/economic_cycle_pipeline.py finance/data/economic_cycle_results.py finance/loaders/economic_cycle.py
  ```

  Commit files with message: `기능: 관측 국면 snapshot 저장 계약 연결`.

---

### Task 3: Overview Service V3 Read Model

**Files:**
- Modify: `app/services/overview/economic_cycle.py`
- Modify: `tests/test_economic_cycle_service.py`

**Interfaces:**
- Consumes: persisted JSON fields from Task 2, recent historical snapshot rows, existing DB-only asset pathway loaders, and existing `build_market_implications()`.
- Produces: `build_economic_cycle_read_model(...) -> dict[str, object]` with `schema_version = economic_cycle_v3` and top-level `headline`, `observed_state`, `recent_changes`, `transition_monitor`, `cycle_map`, `intramonth_change`, `data_freshness`, `evidence`, `market_implications`, `sources`, and `limitations`.

- [x] **Step 1: Replace obsolete service tests with failing V3 contract tests**

  Build literal snapshot fixtures containing the three JSON fields. Assert headline/observed phase identity, 12 actual cycle points, no horizons/probabilities/future markers, transition condition availability, explicit confidence labels, and a stable limited state for legacy rows without observed JSON.

  ```python
  assert model["schema_version"] == "economic_cycle_v3"
  assert model["headline"]["phase"] == model["observed_state"]["phase"]
  assert "horizons" not in model
  assert "probabilities" not in json.dumps(model["headline"])
  assert model["cycle_map"]["points"][-1]["level"] == -0.56
  ```

- [x] **Step 2: Run service tests and verify RED**

  Run: `.venv/bin/python -m pytest tests/test_economic_cycle_service.py -q`

  Expected: V2 key/field assertions fail because the service still emits probability horizons.

- [x] **Step 3: Implement safe JSON decoders, headline copy, cycle map, recent changes, and transition projection**

  Decode only dict/list shapes; never reconstruct current phase from probability JSON. Map confidence to `높음 / 보통 / 제한`, transition status to `유지 / 전환 감시 / 전환 확인`, and phase copy to relative growth-cycle language. History points come only from `observed_state_json`; legacy history rows do not get probability-derived coordinates.

- [x] **Step 4: Implement month-end/intramonth separation and asset deep-equality regression**

  Intramonth output contains provisional raw-level/factor/recent-change deltas and never replaces headline/transition persistence. Call `build_market_implications((), evidence, price_rows, market_rows=..., sp500_earnings=..., economic_as_of_date=..., price_reference_date=...)` with the same non-horizon inputs as V2 and compare against a direct builder call in the test.

  ```python
  assert model["market_implications"] == interpretation.build_market_implications(
      (), evidence, price_rows, market_rows=market_rows,
      sp500_earnings=earnings, economic_as_of_date="2026-06-30",
      price_reference_date="2026-06-30",
  )
  ```

- [x] **Step 5: Verify Task 3 GREEN and commit**

  Run:

  ```bash
  .venv/bin/python -m pytest tests/test_economic_cycle_service.py tests/test_economic_cycle_asset_pathways.py tests/test_economic_cycle_asset_prices.py -q
  .venv/bin/python -m py_compile app/services/overview/economic_cycle.py
  ```

  Commit files with message: `기능: 경제사이클 Overview v3 읽기 모델 전환`.

---

### Task 4: React Observed-State Workbench

**Files:**
- Modify: `app/web/streamlit_components/economic_cycle_workbench/package.json`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/package-lock.json`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleHero.tsx`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/style.css`
- Create: `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.test.tsx`

**Interfaces:**
- Consumes: Task 3 `economic_cycle_v3` payload.
- Produces: exported `EconomicCycleWorkbenchView({ payload })` for real server-rendered component tests and the existing Streamlit-connected default export.
- Produces: actual coordinate projection from fixed `[-2, 2]` domain, 12-month path, current/revision halo, WATCH-only dashed pressure arrow, recent 1/3/6M cards, transition conditions, and context cards.

- [x] **Step 1: Add Vitest and write failing real-render tests**

  Add `"test": "vitest run"` and `vitest` to dev dependencies. Render `EconomicCycleWorkbenchView` through `react-dom/server` using a complete V3 fixture. Assert user-visible section order and absence of probability/future copy; assert the five asset groups and their existing observation sub-blocks remain present and ordered.

  ```tsx
  const html = renderToStaticMarkup(<EconomicCycleWorkbenchView payload={fixture} />);
  expect(html).toContain("현재 국면과 전환 조건");
  expect(html).not.toContain("현재와 앞으로 1·2개월");
  expect(html.indexOf("채권·금리")).toBeLessThan(html.indexOf("주식"));
  expect(html).toContain("함께 관찰된 경로");
  ```

- [x] **Step 2: Run React tests and verify RED**

  Run: `npm test --prefix app/web/streamlit_components/economic_cycle_workbench`

  Expected: test import/render fails because the V3 view export does not exist.

- [x] **Step 3: Implement the V3 types and decision-centered section order**

  Keep `MarketImplicationCard` and its child markup unchanged. Replace the probability horizon, probability-derived quadrant, future ribbon, and forecast evidence sections with current hero, actual cycle map + recent changes, transition monitor, contextual conditions, then the unchanged asset section and method disclosure.

- [x] **Step 4: Implement accessible fixed-domain SVG and responsive CSS**

  Clamp only display coordinates, preserve raw values in accessible labels/tooltips, label 6M/3M/current points, show no future terminal point, and show the dashed direction arrow only for WATCH with `예측 경로가 아님`. Append new upper-section styles without altering asset selectors or the existing `.implication-grid` breakpoints.

- [x] **Step 5: Verify Task 4 GREEN and commit**

  Run:

  ```bash
  npm test --prefix app/web/streamlit_components/economic_cycle_workbench
  npm run build --prefix app/web/streamlit_components/economic_cycle_workbench
  ```

  Commit files with message: `기능: 경제사이클 관측 국면 UI로 교체`.

---

### Task 5: Historical Acceptance, Browser QA, And Durable Documentation

**Files:**
- Create: `tests/test_economic_cycle_observed_state_acceptance.py`
- Modify: `.aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md`
- Modify: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify: `.aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/data/DB_SCHEMA_MAP.md`
- Modify: `.aiworkspace/note/finance/tasks/active/economic-cycle-observed-state-transition-v1-20260803/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/economic-cycle-observed-state-transition-v1-20260803/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/economic-cycle-observed-state-transition-v1-20260803/RISKS.md`

**Interfaces:**
- Consumes: Tasks 1–4 and the local PIT vintage DB.
- Produces: reproducible stability/revision report assertions, aligned canonical docs, final desktop/tablet/phone Browser QA, and one uncommitted QA screenshot.

- [x] **Step 1: Write and run failing historical acceptance test**

  Build a deterministic literal history fixture for CI assertions and run the same summary against
  the configured local DB. If the DB read is unavailable, record the exact reason in `RISKS.md`
  without weakening the literal acceptance assertions. Assert plotted-phase mismatch is zero,
  transition-confirmed one-month flipbacks are zero, NBER never overrides observed phase, and each
  revision-sensitive result is reported rather than silently replaced.

- [x] **Step 2: Implement any acceptance-only corrections through RED/GREEN**

  If a metric fails, add the smallest reproducing unit test before correcting domain/pipeline behavior. Do not tune thresholds to obtain a preferred current phase.

- [x] **Step 3: Run complete automated verification**

  Run:

  ```bash
  .venv/bin/python -m pytest tests/test_economic_cycle_*.py tests/test_market_context_economic_cycle.py -q
  .venv/bin/python -m py_compile finance/economic_cycle_observed_state.py finance/economic_cycle_pipeline.py finance/data/economic_cycle_results.py finance/loaders/economic_cycle.py app/services/overview/economic_cycle.py
  npm test --prefix app/web/streamlit_components/economic_cycle_workbench
  npm run build --prefix app/web/streamlit_components/economic_cycle_workbench
  git diff --check
  ```

- [x] **Step 4: Perform Browser QA at desktop, 760px, and 420px**

  Start the Finance Streamlit app with the repository's normal entry point, open the economic-cycle tab through the in-app browser, verify zero horizontal overflow and section order, verify no probability/future point, and compare the asset checkpoint layout/copy blocks with the pre-change contract. Save one final screenshot outside the commit.

- [x] **Step 5: Synchronize durable docs and task closeout**

  Use `finance-doc-sync`. Update only canonical facts that actually changed: observed-state ownership, v3 product promise, snapshot JSON meaning, and roadmap baseline. Record commands/results in `RUNS.md`; move task state to `complete` only after Browser QA and full verification pass.

- [x] **Step 6: Review staged diff and commit the closeout unit**

  Use `finance-integration-review` for the staged diff because the change spans domain, persistence, service, UI, and documentation. Confirm frozen asset modules are absent from the diff. Commit with message: `완료: 경제사이클 관측 국면 전환 개편 검증`.
