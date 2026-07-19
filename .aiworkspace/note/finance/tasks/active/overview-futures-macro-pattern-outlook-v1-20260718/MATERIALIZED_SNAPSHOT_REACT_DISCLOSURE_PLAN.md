# Futures Macro Materialized Snapshot And React Disclosure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. This worktree executes inline because repository instructions prohibit unrequested subagent delegation.

**Goal:** Move the five-year Futures Macro calculation behind daily ingestion, persist one compact compatible snapshot, make tab entry DB-read-only, and render both methodology and calculation trace as correctly resizing React disclosures.

**Architecture:** `finance_meta.futures_macro_snapshot` stores one idempotent current snapshot keyed by source marker and algorithm/schema versions. A Streamlit-free service materializes existing thermometer and pattern-outlook outputs into JSON-safe compact records; Overview reads only that persisted row. React receives bounded calculation tables and owns both disclosures, while every toggle re-runs Streamlit component height synchronization.

**Tech Stack:** Python 3.11+, pandas, MySQL/PyMySQL, `unittest`, Streamlit custom components, React 18, TypeScript 5.7, Vite 6.

## Global Constraints

- Preserve the five-year lookback, probability formulas, analog selection, conditional terminal/range, and 30/60 publication gates.
- Do not persist full OHLCV, historical feature frames, forward coordinate frames, provider responses, or Streamlit state.
- Do not compute thermometer or pattern outlook during normal Futures Macro render.
- `일봉 갱신` owns collection plus marker-aware materialization; `다시 읽기` only reloads the persisted row.
- Missing, malformed, or incompatible snapshots show a fast refresh-required state instead of a render-time fallback calculation.
- React receives bounded score, contribution, core-symbol, coverage, materialization, and caution evidence only.
- Preserve unrelated untracked research and `.superpowers/`; do not stage generated screenshots or run history.

---

### Task 1: Persistent Snapshot Schema, Writer, And Loader

**Files:**
- Modify: `finance/data/db/schema.py`
- Modify: `finance/data/futures_market.py`
- Create: `finance/data/futures_macro_snapshot.py`
- Create: `finance/loaders/futures_macro_snapshot.py`
- Create: `tests/test_futures_macro_snapshot.py`

**Interfaces:**
- Produces: `FUTURES_MACRO_SNAPSHOT_SCHEMA_VERSION = "futures_macro_snapshot_v1"`.
- Produces: `upsert_futures_macro_snapshot(row, *, connection=None) -> int`.
- Produces: `load_latest_futures_macro_snapshot(*, snapshot_key="overview_current", query_fn=None) -> dict[str, Any] | None`.
- Snapshot row fields: `snapshot_key`, `source_marker`, `as_of_date`, `schema_version`, `algorithm_version`, `status`, `snapshot_json`, `materialized_at`.

- [ ] **Step 1: Write persistence RED tests**

Add tests that assert the schema and JSON boundary before production code exists:

```python
class FuturesMacroSnapshotPersistenceTests(unittest.TestCase):
    def test_schema_has_versioned_marker_and_unique_current_key(self) -> None:
        from finance.data.db.schema import FUTURES_MARKET_SCHEMAS

        schema = FUTURES_MARKET_SCHEMAS["futures_macro_snapshot"]
        self.assertIn("source_marker", schema)
        self.assertIn("schema_version", schema)
        self.assertIn("algorithm_version", schema)
        self.assertIn("snapshot_json LONGTEXT", schema)
        self.assertIn("UNIQUE KEY uk_futures_macro_snapshot_key", schema)

    def test_loader_returns_latest_row_without_calculation(self) -> None:
        from finance.loaders.futures_macro_snapshot import load_latest_futures_macro_snapshot

        captured = {}
        def query(db_name, sql, params):
            captured.update(db_name=db_name, sql=sql, params=params)
            return [{"snapshot_key": "overview_current", "source_marker": "2026-07-17 00:00:00"}]

        row = load_latest_futures_macro_snapshot(query_fn=query)
        self.assertEqual(row["snapshot_key"], "overview_current")
        self.assertEqual(captured["db_name"], "finance_meta")
        self.assertNotIn("futures_ohlcv", captured["sql"])
```

- [ ] **Step 2: Run persistence RED**

Run:

```bash
.venv/bin/python -m unittest tests.test_futures_macro_snapshot.FuturesMacroSnapshotPersistenceTests -v
```

Expected: FAIL because the table key and snapshot modules do not exist.

- [ ] **Step 3: Implement the schema and idempotent writer**

Add this table to `FUTURES_MARKET_SCHEMAS`:

```sql
CREATE TABLE IF NOT EXISTS futures_macro_snapshot (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  snapshot_key VARCHAR(64) NOT NULL,
  source_marker VARCHAR(64) NOT NULL,
  as_of_date DATE NULL,
  schema_version VARCHAR(64) NOT NULL,
  algorithm_version VARCHAR(128) NOT NULL,
  status ENUM('READY','LIMITED','ERROR') NOT NULL,
  snapshot_json LONGTEXT NOT NULL,
  materialized_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_futures_macro_snapshot_key (snapshot_key),
  KEY ix_futures_macro_snapshot_marker (source_marker),
  KEY ix_futures_macro_snapshot_version (schema_version, algorithm_version)
);
```

`upsert_futures_macro_snapshot()` must use this exact update set:

```sql
ON DUPLICATE KEY UPDATE
  source_marker = VALUES(source_marker),
  as_of_date = VALUES(as_of_date),
  schema_version = VALUES(schema_version),
  algorithm_version = VALUES(algorithm_version),
  status = VALUES(status),
  snapshot_json = VALUES(snapshot_json),
  materialized_at = VALUES(materialized_at)
```

Update `sync_futures_market_tables()` to sync the new table in `finance_meta`.

- [ ] **Step 4: Implement the DB-only loader**

`load_latest_futures_macro_snapshot()` must query only `finance_meta.futures_macro_snapshot`, filter by `snapshot_key`, order by `updated_at DESC`, and return one `dict` or `None`. The default query opens MySQL with the repository-local connection convention; injected `query_fn` remains the unit-test boundary.

- [ ] **Step 5: Run persistence GREEN and commit**

```bash
.venv/bin/python -m unittest tests.test_futures_macro_snapshot.FuturesMacroSnapshotPersistenceTests -v
.venv/bin/python -m py_compile finance/data/futures_macro_snapshot.py finance/loaders/futures_macro_snapshot.py finance/data/futures_market.py
git diff --check
git add finance/data/db/schema.py finance/data/futures_market.py finance/data/futures_macro_snapshot.py finance/loaders/futures_macro_snapshot.py tests/test_futures_macro_snapshot.py
git commit -m "선물 매크로 영속 스냅샷 저장소 추가"
```

Expected: persistence tests pass; compile and diff check exit 0.

---

### Task 2: Compact Materializer And Daily Ingestion Hook

**Files:**
- Create: `app/services/futures_macro_snapshot.py`
- Modify: `app/jobs/ingestion_jobs.py`
- Modify: `tests/test_futures_macro_snapshot.py`
- Modify: `tests/test_service_contracts.py`

**Interfaces:**
- Produces: `materialize_overview_futures_macro_snapshot(*, force=False, marker_fn=None, load_fn=None, macro_builder=None, outlook_builder=None, write_fn=None, now_fn=None) -> dict[str, Any]`.
- Produces: `load_overview_futures_macro_materialized_snapshot(*, load_fn=None) -> dict[str, Any]`.
- Produces: `build_compact_futures_macro_payload(macro, pattern_outlook, *, source_marker, materialized_at) -> dict[str, Any]`.
- Produces: `attach_futures_macro_materialization(result, *, interval, rows_written, materialize_fn=None) -> dict[str, Any]`.

- [ ] **Step 1: Write compact/materialization RED tests**

```python
class FuturesMacroSnapshotServiceTests(unittest.TestCase):
    def test_compact_payload_turns_dataframes_into_json_records(self) -> None:
        from app.services.futures_macro_snapshot import build_compact_futures_macro_payload

        payload = build_compact_futures_macro_payload(
            {"scores": pd.DataFrame([{"Score": "Risk On", "Value": 1.2}]),
             "score_components": pd.DataFrame([{"Symbol": "ES=F", "Contribution": 0.4}]),
             "symbols": pd.DataFrame([{"Symbol": "ES=F", "1D %": 0.2}]),
             "coverage": {"latest_daily_date": "2026-07-17"}, "pattern_feature_frame": pd.DataFrame({"x": [1]})},
            {"schema_version": "futures_macro_pattern_outlook_v1", "horizons": []},
            source_marker="2026-07-17 00:00:00",
            materialized_at="2026-07-19 10:00:00",
        )
        self.assertEqual(payload["macro"]["scores"][0]["Score"], "Risk On")
        self.assertNotIn("pattern_feature_frame", payload["macro"])
        json.dumps(payload, ensure_ascii=False, allow_nan=False)

    def test_same_marker_and_versions_reuse_existing_snapshot(self) -> None:
        from app.services.futures_macro_snapshot import materialize_overview_futures_macro_snapshot

        existing = compatible_row(source_marker="2026-07-17 00:00:00")
        result = materialize_overview_futures_macro_snapshot(
            marker_fn=lambda: "2026-07-17 00:00:00",
            load_fn=lambda: existing,
            macro_builder=lambda: self.fail("macro calculation must be skipped"),
            outlook_builder=lambda: self.fail("outlook calculation must be skipped"),
            write_fn=lambda row: self.fail("write must be skipped"),
        )
        self.assertEqual(result["status"], "reused")

    def test_new_marker_calculates_and_writes_once(self) -> None:
        written = []
        result = materialize_overview_futures_macro_snapshot(
            marker_fn=lambda: "2026-07-18 00:00:00",
            load_fn=lambda: compatible_row(source_marker="2026-07-17 00:00:00"),
            macro_builder=lambda: minimal_macro(),
            outlook_builder=lambda: minimal_outlook(),
            write_fn=lambda row: written.append(row) or 1,
            now_fn=lambda: "2026-07-19 10:00:00",
        )
        self.assertEqual(result["status"], "materialized")
        self.assertEqual(len(written), 1)
```

Add an ingestion test asserting non-`1d` calls skip the materializer and successful `1d` rows add `details["futures_macro_snapshot"]`.

- [ ] **Step 2: Run service RED**

```bash
.venv/bin/python -m unittest tests.test_futures_macro_snapshot.FuturesMacroSnapshotServiceTests -v
```

Expected: FAIL because the materializer APIs do not exist.

- [ ] **Step 3: Implement JSON-safe compact payload**

The compact macro allowlist is exact:

```python
COMPACT_MACRO_KEYS = (
    "status", "coverage", "warnings", "summary", "summary_sentences",
    "evidence", "evidence_groups", "evidence_reading", "weekly_context",
    "flow_context", "pattern", "cautions", "source_note", "as_of_date",
)
COMPACT_TABLE_KEYS = ("scores", "score_components", "symbols")
```

Convert DataFrames to records, normalize timestamps to ISO strings, numpy scalars to Python scalars, and non-finite numbers to `None`. Validate with `json.dumps(..., allow_nan=False)` before writing. Do not include `pattern_feature_frame`, `all_candles`, or validation DataFrames.

- [ ] **Step 4: Implement marker/version-aware materialization and compatible loading**

Use constants:

```python
FUTURES_MACRO_SNAPSHOT_KEY = "overview_current"
FUTURES_MACRO_SNAPSHOT_SCHEMA_VERSION = "futures_macro_snapshot_v1"
```

Compatibility requires matching snapshot schema and `PATTERN_ALGORITHM_VERSION`. `materialize_overview_futures_macro_snapshot()` reuses only when marker and both versions match. Otherwise it calls the existing five-year builders with validation disabled, writes canonical JSON, and returns `materialized`. `load_overview_futures_macro_materialized_snapshot()` returns `{status: "READY", macro, pattern_outlook, metadata}` or `{status: "MISSING", reason}` without calculating.

- [ ] **Step 5: Attach materialization after successful daily ingestion**

Refactor `run_collect_futures_ohlcv()` so the built result passes through:

```python
return attach_futures_macro_materialization(
    job_result,
    interval=interval,
    rows_written=rows_written,
)
```

The helper must:

- return unchanged for intervals other than `1d` or `rows_written <= 0`;
- attach materialization summary under `details.futures_macro_snapshot`;
- keep collection success when materialization is `materialized` or `reused`;
- change collection `success` to `partial_success` and append a message when materialization raises;
- preserve the previously persisted READY row because the writer is never called on failure.

- [ ] **Step 6: Run service GREEN and commit**

```bash
.venv/bin/python -m unittest tests.test_futures_macro_snapshot -v
.venv/bin/python -m unittest tests.test_service_contracts.FuturesMacroThermometerContractTests -v
.venv/bin/python -m py_compile app/services/futures_macro_snapshot.py app/jobs/ingestion_jobs.py
git diff --check
git add app/services/futures_macro_snapshot.py app/jobs/ingestion_jobs.py tests/test_futures_macro_snapshot.py tests/test_service_contracts.py
git commit -m "일봉 수집 후 선물 매크로 스냅샷 계산"
```

Expected: snapshot and selected Futures Macro tests pass; compile and diff check exit 0.

---

### Task 3: Persisted-Only Overview Read And React Calculation Trace

**Files:**
- Modify: `app/web/overview/futures_macro_helpers.py`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/FuturesMacroWorkbench.tsx`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/MethodDisclosure.tsx`
- Create: `app/web/streamlit_components/futures_macro_workbench/src/CalculationTraceDisclosure.tsx`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/style.css`
- Modify: `tests/test_service_contracts.py`
- Rebuild: `app/web/streamlit_components/futures_macro_workbench/component_static/`

**Interfaces:**
- `build_futures_macro_react_workbench_payload(...)["calculation_trace"]` contains metadata, score rows, contribution rows, symbol rows, and cautions.
- `MethodDisclosure` accepts `onToggle: () => void`.
- `CalculationTraceDisclosure` accepts `trace: CalculationTracePayload` and `onToggle: () => void`.

- [ ] **Step 1: Write Overview/React RED contracts**

Update source contracts to require:

```python
self.assertIn("load_overview_futures_macro_materialized_snapshot()", panel_body)
self.assertNotIn("load_overview_futures_macro_snapshot(include_validation=False)", panel_body)
self.assertNotIn("load_overview_futures_macro_pattern_outlook()", panel_body)
self.assertNotIn('with st.expander("원본 데이터 / 계산 추적"', panel_body)
self.assertIn('"calculation_trace"', payload_body)
self.assertIn("CalculationTraceDisclosure", workbench_source)
self.assertIn("onToggle={syncFrameHeightSoon}", workbench_source)
self.assertIn("원본 데이터 / 계산 추적", trace_source)
self.assertIn("현재 점수 원본", trace_source)
self.assertIn("점수 구성 기여", trace_source)
self.assertIn("선물 일봉 변화", trace_source)
self.assertIn("해석 주의점", trace_source)
```

The method source contract must require `onToggle={onToggle}` on its `<details>` element.

- [ ] **Step 2: Run Overview/React RED**

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.OverviewPrimarySurfaceContractTests.test_futures_macro_tab_exposes_daily_refresh_and_cache_reload \
  tests.test_service_contracts.OverviewPrimarySurfaceContractTests.test_futures_macro_raw_tables_are_named_by_calculation_step -v
```

Expected: FAIL because the render path still calculates and the React trace component does not exist.

- [ ] **Step 3: Switch the panel to persisted-only loading**

`_render_futures_macro_panel()` must call `load_overview_futures_macro_materialized_snapshot()` once. On READY it reads `macro` and `pattern_outlook`; on MISSING it passes empty objects plus the refresh-required reason to the React builder. Remove the React-path Streamlit outer expander and raw tables. Keep native fallback bounded and read-only.

Change `다시 읽기` help/copy so it says it reloads the saved snapshot and does not calculate. After `일봉 갱신`, clear only legacy process caches for compatibility; the next render must still read the DB snapshot.

- [ ] **Step 4: Add bounded calculation-trace payload**

Create payload shape:

```typescript
export type CalculationTracePayload = {
  metadata: Array<{ label: string; value: string }>;
  tables: Array<{
    key: "scores" | "components" | "symbols";
    label: string;
    columns: string[];
    rows: Array<Record<string, string | number | null>>;
  }>;
  cautions: string[];
};
```

Python caps each table at 80 rows, derives columns from the first record, and never includes OHLCV history.

- [ ] **Step 5: Implement correctly resizing React disclosures**

`MethodDisclosure` and `CalculationTraceDisclosure` both use:

```tsx
<details className="..." onToggle={onToggle}>
```

`FuturesMacroWorkbench` renders them in this order and passes the same `syncFrameHeightSoon` callback:

```tsx
<MethodDisclosure boundaryNote={payload.boundary_note} method={payload.method} onToggle={syncFrameHeightSoon} />
<CalculationTraceDisclosure trace={payload.calculation_trace} onToggle={syncFrameHeightSoon} />
```

The trace component renders semantic tables inside horizontally scrollable wrappers and formats null as `-`. CSS gives both disclosures the same border, radius, summary padding, open-state border, table header, and mobile overflow treatment.

- [ ] **Step 6: Run React GREEN, build, and commit**

```bash
.venv/bin/python -m unittest tests.test_service_contracts.OverviewPrimarySurfaceContractTests -v
npm run build --prefix app/web/streamlit_components/futures_macro_workbench
.venv/bin/python -m py_compile app/web/overview/futures_macro_helpers.py
git diff --check
git add app/web/overview/futures_macro_helpers.py app/web/streamlit_components/futures_macro_workbench/src app/web/streamlit_components/futures_macro_workbench/component_static tests/test_service_contracts.py
git commit -m "선물 매크로 계산 추적을 React로 통합"
```

Expected: selected contracts pass, Vite exits 0, compile and diff check exit 0.

---

### Task 4: Actual Materialization, Cold-Entry QA, Documentation, And Closeout

**Files:**
- Modify: `.aiworkspace/note/finance/tasks/active/overview-futures-macro-pattern-outlook-v1-20260718/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-futures-macro-pattern-outlook-v1-20260718/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-futures-macro-pattern-outlook-v1-20260718/NOTES.md`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-futures-macro-pattern-outlook-v1-20260718/RISKS.md`
- Modify: `.aiworkspace/note/finance/docs/runbooks/OVERVIEW_MARKET_INTELLIGENCE.md`
- Modify: `.aiworkspace/note/finance/docs/architecture/DATA_DB_PIPELINE_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Generated, do not commit: browser QA screenshot

**Interfaces:**
- Actual snapshot is materialized from the already stored core daily futures rows.
- Browser QA verifies persisted-only cold entry and both disclosures at desktop and 420px.

- [ ] **Step 1: Materialize the actual DB snapshot once**

```bash
.venv/bin/python - <<'PY'
from app.services.futures_macro_snapshot import materialize_overview_futures_macro_snapshot
print(materialize_overview_futures_macro_snapshot(force=True))
PY
```

Expected: `status=materialized`, source marker present, snapshot row written, and no provider fetch.

- [ ] **Step 2: Measure persisted load and prove render boundary**

Run a fresh-process timing of `load_overview_futures_macro_materialized_snapshot()` and inspect the panel source. Expected: DB read is sub-second locally; panel contains neither thermometer builder nor pattern-outlook loader call.

- [ ] **Step 3: Run focused and regression verification**

```bash
.venv/bin/python -m unittest tests.test_futures_macro_snapshot tests.test_futures_macro_pattern tests.test_futures_macro_pattern_validation -v
.venv/bin/python -m unittest tests.test_service_contracts.FuturesMacroThermometerContractTests tests.test_service_contracts.OverviewPrimarySurfaceContractTests -v
npm run build --prefix app/web/streamlit_components/futures_macro_workbench
.venv/bin/python -m py_compile finance/data/futures_macro_snapshot.py finance/loaders/futures_macro_snapshot.py app/services/futures_macro_snapshot.py app/jobs/ingestion_jobs.py app/web/overview/futures_macro_helpers.py
git diff --check
```

Expected: all selected tests pass, build succeeds, compile and diff check exit 0.

- [ ] **Step 4: Browser QA the approved user flow**

Use the existing Streamlit QA process and in-app browser:

- Open `Overview > Futures Macro` in a fresh app process.
- Confirm the tab shows persisted data without a calculation spinner.
- Open `방법론과 품질`; confirm all five metrics, caveats, and boundary note are visible above the next section.
- Open `원본 데이터 / 계산 추적`; confirm metadata plus score, contribution, symbol, and caution sections.
- At desktop and 420px confirm `scrollWidth == clientWidth` for document/workbench, table wrappers scroll internally, content is not clipped, and console errors are zero.
- Save one screenshot under `/Users/taeho/.codex/visualizations/2026/07/19/` and keep it unstaged.

- [ ] **Step 5: Synchronize durable documentation**

Record implemented behavior, actual timing, test counts, screenshot path, and remaining scheduler limitation. Update the runbook from process-cache/render-time wording to ingestion-materialized DB snapshot wording. Keep root logs at 3–5 concise lines and detailed evidence in task docs.

- [ ] **Step 6: Final verification and coherent commit**

```bash
git status --short
git diff --check
.venv/bin/python -m unittest tests.test_futures_macro_snapshot tests.test_futures_macro_pattern tests.test_futures_macro_pattern_validation -v
.venv/bin/python -m unittest tests.test_service_contracts.FuturesMacroThermometerContractTests tests.test_service_contracts.OverviewPrimarySurfaceContractTests -v
npm run build --prefix app/web/streamlit_components/futures_macro_workbench
```

After fresh output confirms success:

```bash
git add .aiworkspace/note/finance/tasks/active/overview-futures-macro-pattern-outlook-v1-20260718 .aiworkspace/note/finance/docs/runbooks/OVERVIEW_MARKET_INTELLIGENCE.md .aiworkspace/note/finance/docs/architecture/DATA_DB_PIPELINE_FLOW.md .aiworkspace/note/finance/docs/PROJECT_MAP.md .aiworkspace/note/finance/WORK_PROGRESS.md .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git commit -m "선물 매크로 영속 스냅샷 마무리"
```

Expected: only intended code/docs and production component bundle are committed; untracked research, `.superpowers/`, run history, and screenshots remain uncommitted.
