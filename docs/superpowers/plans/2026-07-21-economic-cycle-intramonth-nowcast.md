# Economic Cycle Intramonth Nowcast Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Preserve every existing month-end economic-cycle snapshot while adding an automatically refreshed, date-specific intramonth nowcast and a clearly labeled month-end-to-current bridge in Overview.

**Architecture:** Extend the existing FRED/ALFRED vintage ledger with an overlap-based incremental collector, then materialize `intramonth_nowcast` rows with the exact latest canonical month-end artifact. A weekday Overview backend job owns collection, closed-month rollover, and materialization; the Overview service and React component remain DB-only and render the optional latest valid intramonth row without adding it to monthly history.

**Tech Stack:** Python 3.12, pandas, MySQL, pytest, Streamlit, React 18, TypeScript, Vite.

## Global Constraints

- Existing `current` and `historical_replay` snapshot rows must never be rewritten as part of intramonth refresh.
- A newly closed calendar month may append one missing canonical `current` row; retries use the existing idempotent business key.
- Intramonth rows use `run_kind=intramonth_nowcast` and are always user-facing `PROVISIONAL`, even if their reused artifact is READY.
- Do not interpolate unpublished monthly data or synthesize dates between the month-end and intramonth points.
- The UI and `browser_safe` automation profile must not fetch providers, fit models, or write DB state.
- Scheduled refresh runs at most once per 24 hours on weekdays in `safe`, `standard`, and `broad`; explicit `force=True` may override the weekday guard.
- Any provider-series failure or unusable h0 result prevents a new intramonth snapshot write and preserves the last-good row.
- Do not lower publication gates, modify NBER semantics, add trading language, or add a visible run/job diagnostic panel.
- Preserve unrelated user work, registry JSONL, saved JSONL, run history, research folders, and generated QA artifacts.

## File Structure

- `finance/data/db/schema.py`: snapshot enum and compact intramonth provenance columns.
- `finance/data/economic_cycle_results.py`: backward-compatible snapshot UPSERT defaults.
- `finance/data/economic_cycle_vintages.py`: bounded vintage-date requests and overlap incremental collection.
- `finance/loaders/economic_cycle.py`: exact artifact, run-kind snapshot, latest nowcast, and coverage readers.
- `finance/economic_cycle_pipeline.py`: partial-origin panel, intramonth materialization, and closed-month rollover.
- `app/jobs/economic_cycle_refresh.py`: focused combined refresh orchestration and failure isolation.
- `app/jobs/overview_automation.py`: weekday-aware job spec and scheduled registration.
- `app/services/overview/economic_cycle.py`: optional DB-only intramonth projection and deltas.
- `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx`: flow block and cycle-map bridge.
- `app/web/streamlit_components/economic_cycle_workbench/src/style.css`: responsive intramonth presentation.
- `app/web/streamlit_components/economic_cycle_workbench/component_static/`: rebuilt tracked production asset.
- Focused tests remain in the existing `tests/test_economic_cycle_*.py`, `tests/test_market_context_economic_cycle.py`, and `tests/test_service_contracts.py` modules.

---

### Task 1: Persist and load a separate intramonth snapshot contract

**Files:**
- Modify: `finance/data/db/schema.py:975-1025`
- Modify: `finance/data/economic_cycle_results.py:181-247`
- Modify: `finance/loaders/economic_cycle.py:285-430`
- Test: `tests/test_economic_cycle_results.py`

**Interfaces:**
- Produces: `load_cycle_model_artifact(model_version: str, *, trained_through: str | date | None = None, query_fn: QueryFn | None = None) -> dict[str, object] | None`
- Extends: `load_cycle_snapshot(*, as_of_date: str | date | None = None, run_kind: Literal["current", "historical_replay", "intramonth_nowcast"] = "current", model_version: str | None = None, query_fn: QueryFn | None = None) -> dict[str, object] | None`
- Produces snapshot fields `baseline_as_of_date`, `source_collected_at`, `source_coverage_json`.

- [ ] **Step 1: Write failing schema and loader tests**

```python
def test_snapshot_schema_supports_intramonth_provenance() -> None:
    sql = " ".join(ECONOMIC_CYCLE_SCHEMAS["economic_cycle_snapshot"].split())
    assert "'intramonth_nowcast'" in sql
    assert "baseline_as_of_date DATE NULL" in sql
    assert "source_collected_at DATETIME NULL" in sql
    assert "source_coverage_json LONGTEXT NULL" in sql

def test_exact_artifact_and_intramonth_snapshot_loaders_do_not_require_ready() -> None:
    artifact = load_cycle_model_artifact(
        "cycle-limited",
        query_fn=lambda *_: [{"model_version": "cycle-limited", "publication_status": "LIMITED"}],
    )
    nowcast = load_cycle_snapshot(
        as_of_date="2026-07-21",
        run_kind="intramonth_nowcast",
        query_fn=lambda *_: [{"as_of_date": "2026-07-21", "run_kind": "intramonth_nowcast"}],
    )
    assert artifact and artifact["model_version"] == "cycle-limited"
    assert nowcast and nowcast["run_kind"] == "intramonth_nowcast"
```

- [ ] **Step 2: Run the focused RED tests**

Run: `.venv/bin/python -m pytest tests/test_economic_cycle_results.py -q`

Expected: FAIL because the enum, provenance columns, exact artifact loader, and intramonth run kind do not exist.

- [ ] **Step 3: Add schema columns and backward-compatible UPSERT normalization**

```python
SNAPSHOT_RUN_KINDS = {"historical_replay", "current", "intramonth_nowcast"}

def _snapshot_storage_row(row: dict[str, object]) -> dict[str, object]:
    normalized = dict(row)
    normalized.setdefault("baseline_as_of_date", None)
    normalized.setdefault("source_collected_at", None)
    normalized.setdefault("source_coverage_json", None)
    return normalized
```

Extend INSERT and ON DUPLICATE KEY UPDATE with the three provenance fields. Existing callers may omit them.

- [ ] **Step 4: Add exact artifact and run-kind loader support**

```python
def load_cycle_model_artifact(
    model_version: str,
    *,
    trained_through: str | date | None = None,
    query_fn: QueryFn | None = None,
) -> dict[str, object] | None:
    """Load one exact persisted artifact without changing publication status."""
```

Keep `load_latest_approved_cycle_artifact()` unchanged for existing model-selection callers. Validate `run_kind` against the three explicit values.

- [ ] **Step 5: Run persistence and loader tests**

Run: `.venv/bin/python -m pytest tests/test_economic_cycle_results.py -q`

Expected: all tests PASS.

- [ ] **Step 6: Commit the persistence unit**

```bash
git add finance/data/db/schema.py finance/data/economic_cycle_results.py finance/loaders/economic_cycle.py tests/test_economic_cycle_results.py
git commit -m "경제사이클 월중 스냅샷 저장 계약 추가"
```

---

### Task 2: Collect only the latest vintage overlap

**Files:**
- Modify: `finance/data/economic_cycle_vintages.py:171-570`
- Test: `tests/test_economic_cycle_vintages.py`

**Interfaces:**
- Produces: `load_latest_vintage_realtime_starts(series_ids: Iterable[str], *, connection: Any = None) -> dict[str, str]`
- Extends: `fetch_fred_vintage_dates(series_id: str, *, api_key: str, session: requests.Session | None = None, realtime_start: str = EARLIEST_REALTIME_DATE) -> list[str]`
- Extends: `iter_fred_vintage_pages(series_id: str, *, api_key: str, session: requests.Session | None = None, realtime_start: str = EARLIEST_REALTIME_DATE, page_size: int = DEFAULT_PAGE_SIZE)`
- Produces: `collect_incremental_economic_cycle_vintages(*, series_ids: Iterable[str] = ECONOMIC_CYCLE_SERIES_IDS, api_key: str | None = None, connection: Any = None, session: requests.Session | None = None) -> dict[str, object]` with `collection_mode`, `overlap_starts`, `failed`, and existing coverage fields.

- [ ] **Step 1: Write RED tests for bounded requests and overlap collection**

```python
def test_fetch_vintage_dates_honors_incremental_realtime_start() -> None:
    session = RecordingSession({"count": 1, "vintage_dates": ["2026-07-15"]})
    fetch_fred_vintage_dates("PAYEMS", api_key="key", session=session, realtime_start="2026-06-01")
    assert session.calls[0]["params"]["realtime_start"] == "2026-06-01"

def test_incremental_collection_overlaps_each_series_latest_vintage() -> None:
    summary = collect_incremental_economic_cycle_vintages(
        series_ids=["PAYEMS"],
        api_key="key",
        realtime_start_loader=lambda *_args, **_kwargs: {"PAYEMS": "2026-07-03"},
        page_iter=lambda _series, **kwargs: recorded.append(kwargs) or iter([fixture_page]),
        writer=lambda rows, **_kwargs: len(rows),
    )
    assert summary["collection_mode"] == "incremental_overlap"
    assert recorded[0]["realtime_start"] == "2026-07-03"
```

- [ ] **Step 2: Run RED collector tests**

Run: `.venv/bin/python -m pytest tests/test_economic_cycle_vintages.py -q`

Expected: FAIL because bounded request arguments and the incremental collector are absent.

- [ ] **Step 3: Add the latest-realtime DB reader and bounded provider parameters**

Use a grouped `MAX(realtime_start)` query. The first-run fallback remains `EARLIEST_REALTIME_DATE`. Change `build_realtime_windows()` to accept an explicit lower bound so it never silently expands an incremental request back to 1776.

```python
def build_realtime_windows(
    vintage_dates: Iterable[str],
    *,
    lower_bound: str = EARLIEST_REALTIME_DATE,
) -> list[tuple[str, str]]:
    ordered = sorted({value for value in vintage_dates if value >= lower_bound})
    if not ordered:
        return [(lower_bound, LATEST_REALTIME_DATE)]
    starts = [lower_bound, *[value for value in ordered if value > lower_bound]]
    ends = [*[(date.fromisoformat(value) - timedelta(days=1)).isoformat() for value in starts[1:]], LATEST_REALTIME_DATE]
    return list(zip(starts, ends, strict=True))
```

- [ ] **Step 4: Implement page-wise incremental orchestration**

Reuse normalization and UPSERT per page. Return all requested series in `overlap_starts`; do not claim success when any series is in `failed` or `missing`.

- [ ] **Step 5: Verify full-bootstrap compatibility and incremental behavior**

Run: `.venv/bin/python -m pytest tests/test_economic_cycle_vintages.py -q`

Expected: all existing full collector and new incremental tests PASS.

- [ ] **Step 6: Commit the collector unit**

```bash
git add finance/data/economic_cycle_vintages.py tests/test_economic_cycle_vintages.py
git commit -m "경제사이클 빈티지 증분 수집 추가"
```

---

### Task 3: Materialize partial-origin nowcasts and closed-month rollover

**Files:**
- Modify: `finance/economic_cycle_pipeline.py:105-700`
- Test: `tests/test_economic_cycle_pipeline.py`

**Interfaces:**
- Produces: `EconomicCyclePipelineLoader.prime_panel(cutoff, *, extra_origins: Sequence[str | date] = ()) -> pd.DataFrame`
- Produces: `materialize_economic_cycle_intramonth_snapshot(*, as_of_date: str | date, baseline_snapshot: Mapping[str, object] | None = None, loader: EconomicCyclePipelineLoader | None = None, writer: EconomicCycleResultWriter | None = None, source_coverage: Mapping[str, object] | None = None) -> CycleSnapshot`
- Produces: `rollover_closed_economic_cycle_month(*, as_of_date: str | date, loader: EconomicCyclePipelineLoader | None = None, writer: EconomicCycleResultWriter | None = None) -> dict[str, object]`
- Consumes Task 1 exact artifact and intramonth persistence interfaces.

- [ ] **Step 1: Write RED tests for partial origin and write isolation**

```python
def test_intramonth_materialization_appends_partial_origin_and_preserves_baseline() -> None:
    snapshot = materialize_economic_cycle_intramonth_snapshot(
        as_of_date="2026-07-21",
        baseline_snapshot=monthly_snapshot,
        loader=loader,
        writer=writer,
        source_coverage=coverage,
    )
    row = next(iter(writer.snapshots.values()))
    assert row["run_kind"] == "intramonth_nowcast"
    assert row["baseline_as_of_date"] == "2026-06-30"
    assert row["as_of_date"] == "2026-07-21"
    assert monthly_key not in writer.snapshots

def test_intramonth_unusable_h0_does_not_write() -> None:
    with pytest.raises(LookupError, match="intramonth h0"):
        materialize_economic_cycle_intramonth_snapshot(
            as_of_date="2026-07-21",
            baseline_snapshot=monthly_snapshot,
            loader=loader_without_usable_h0,
            writer=writer,
            source_coverage=coverage,
        )
    assert writer.snapshots == {}
```

- [ ] **Step 2: Write RED rollover tests**

Verify 2026-08-03 appends 2026-07-31 once, a retry skips it, and 2026-07-31 does not roll July early.

- [ ] **Step 3: Run the pipeline RED tests**

Run: `.venv/bin/python -m pytest tests/test_economic_cycle_pipeline.py -q`

Expected: FAIL because partial origins, nowcast materialization, and rollover do not exist.

- [ ] **Step 4: Extend the cached panel with explicit extra origins**

```python
origins = list(month_end_origins(self.history_start, resolved_cutoff))
for origin in extra_origins:
    resolved = _as_date(origin, field="extra_origin")
    if resolved <= resolved_cutoff and resolved not in origins:
        origins.append(resolved)
origins.sort()
```

Do not change training/replay callers that pass no extra origins.

- [ ] **Step 5: Implement intramonth materialization by reusing the monthly scoring core**

Refactor only enough to pass an explicit `run_kind`, exact artifact row, metadata, and prediction row. Force the persisted publication state to remain the artifact result while the service later labels the origin `PROVISIONAL`.

- [ ] **Step 6: Implement rollover without touching existing dates**

Compute the most recent month-end strictly earlier than `as_of_date`. If an exact `current` row exists, return `{"status": "current", "as_of_date": closed_month_end.isoformat()}`. Otherwise train through the preceding month-end and append one new `current` row.

- [ ] **Step 7: Run pipeline tests**

Run: `.venv/bin/python -m pytest tests/test_economic_cycle_pipeline.py tests/test_economic_cycle_results.py -q`

Expected: all tests PASS; existing replay behavior remains unchanged.

- [ ] **Step 8: Commit the pipeline unit**

```bash
git add finance/economic_cycle_pipeline.py tests/test_economic_cycle_pipeline.py
git commit -m "경제사이클 월중 계산과 월말 롤오버 추가"
```

---

### Task 4: Orchestrate and schedule a fail-closed weekday refresh

**Files:**
- Create: `app/jobs/economic_cycle_refresh.py`
- Modify: `app/jobs/overview_automation.py:30-275`
- Modify: `tests/test_service_contracts.py:11840-12070`
- Create: `tests/test_economic_cycle_refresh.py`

**Interfaces:**
- Produces: `run_economic_cycle_intramonth_refresh(*, as_of_date: str | date | None = None, collector: Callable = collect_incremental_economic_cycle_vintages, rollover: Callable = rollover_closed_economic_cycle_month, materializer: Callable = materialize_economic_cycle_intramonth_snapshot) -> JobResult`
- Extends: `ScheduledJobSpec.weekdays_only: bool = False`
- Adds scheduler job id `economic_cycle_intramonth` and job name `refresh_economic_cycle_intramonth`.

- [ ] **Step 1: Write RED combined-job tests**

```python
def test_refresh_stops_before_rollover_when_one_series_fails() -> None:
    result = run_economic_cycle_intramonth_refresh(
        collector=lambda **_: {"failed": [{"series_id": "PAYEMS"}], "missing": []},
        rollover=lambda **_: pytest.fail("rollover must not run"),
        materializer=lambda **_: pytest.fail("materializer must not run"),
    )
    assert result["status"] == "failed"
    assert result["rows_written"] == 0
```

Also test successful call order `collect -> rollover -> materialize` and `partial_success` for a LIMITED but usable nowcast.

- [ ] **Step 2: Write RED scheduler tests**

Assert the job appears in safe/standard/broad, not browser_safe, is blocked on Saturday with reason `outside weekday schedule`, and is runnable with `force=True`.

- [ ] **Step 3: Run RED job/scheduler tests**

Run: `.venv/bin/python -m pytest tests/test_economic_cycle_refresh.py tests/test_service_contracts.py -q -k 'economic_cycle_intramonth or weekday or browser_safe_profile'`

Expected: FAIL because the module, field, and job spec do not exist.

- [ ] **Step 4: Implement the focused combined job**

```python
def run_economic_cycle_intramonth_refresh(
    *,
    as_of_date: str | date | None = None,
    collector: Callable = collect_incremental_economic_cycle_vintages,
    rollover: Callable = rollover_closed_economic_cycle_month,
    materializer: Callable = materialize_economic_cycle_intramonth_snapshot,
) -> JobResult:
    resolved_date = normalize_as_of_date(as_of_date)
    collection = collector()
    if collection.get("failed") or collection.get("missing"):
        return failed_result_without_snapshot_write(collection, as_of_date=resolved_date)
    rollover_result = rollover(as_of_date=resolved_date)
    snapshot = materializer(as_of_date=resolved_date)
    return normalized_job_result(collection, rollover_result, snapshot)
```

Do not import this module from the Overview service or React bridge.

- [ ] **Step 5: Add the weekday-aware scheduled spec**

Add `weekdays_only` after required dataclass fields so existing constructors remain valid. Automatic planning blocks `weekday() >= 5`; forced execution still runs.

- [ ] **Step 6: Run job and scheduler tests**

Run: `.venv/bin/python -m pytest tests/test_economic_cycle_refresh.py tests/test_service_contracts.py -q -k 'economic_cycle_intramonth or overview_automation or browser_safe_profile or weekday'`

Expected: selected tests PASS.

- [ ] **Step 7: Commit the automation unit**

```bash
git add app/jobs/economic_cycle_refresh.py app/jobs/overview_automation.py tests/test_economic_cycle_refresh.py tests/test_service_contracts.py
git commit -m "경제사이클 월중 자동 갱신 등록"
```

---

### Task 5: Project a safe month-end-to-intramonth service payload

**Files:**
- Modify: `app/services/overview/economic_cycle.py:1-390`
- Modify: `tests/test_economic_cycle_service.py`
- Modify: `tests/test_market_context_economic_cycle.py:145-175`

**Interfaces:**
- Extends: `build_economic_cycle_read_model(*, as_of_date: str | date | None = None, snapshot_loader: Callable = load_cycle_snapshot, history_loader: Callable = load_cycle_history, intramonth_loader: Callable | None = load_latest_intramonth_cycle_snapshot) -> dict[str, object]`
- Produces optional top-level `intramonth: dict[str, object] | None`.
- Consumes Task 1 latest intramonth loader and persisted provenance fields.

- [ ] **Step 1: Write RED service contract tests**

```python
def test_service_pairs_latest_intramonth_with_exact_monthly_baseline() -> None:
    model = build_economic_cycle_read_model(
        snapshot_loader=lambda **_: monthly,
        intramonth_loader=lambda **_: nowcast,
        history_loader=lambda **_: [],
    )
    bridge = model["intramonth"]
    assert bridge["baseline_as_of_date"] == "2026-06-30"
    assert bridge["as_of_date"] == "2026-07-21"
    assert bridge["estimate_status"] == "PROVISIONAL"
    assert bridge["probability_deltas"]["recovery"] == pytest.approx(0.06)
```

Add tests returning `None` for missing, stale-baseline, malformed-probability, and loader-error rows. Assert existing monthly keys and history stay unchanged.

- [ ] **Step 2: Run RED service tests**

Run: `.venv/bin/python -m pytest tests/test_economic_cycle_service.py tests/test_market_context_economic_cycle.py -q`

Expected: FAIL because `intramonth` and the loader seam do not exist.

- [ ] **Step 3: Implement compact normalization and deltas**

```python
def _intramonth_projection(monthly, intramonth):
    if not intramonth or intramonth.get("baseline_as_of_date") != monthly.get("as_of_date"):
        return None
    monthly_h0 = _horizons(monthly)[0]
    nowcast_h0 = _horizons(intramonth)[0]
    if not monthly_h0["probabilities"] or not nowcast_h0["probabilities"]:
        return None
    return {
        "baseline_as_of_date": monthly["as_of_date"],
        "as_of_date": intramonth["as_of_date"],
        "estimate_status": "PROVISIONAL",
        "current_horizon": nowcast_h0,
        "probability_deltas": {
            phase: nowcast_h0["probabilities"].get(phase, 0.0)
            - monthly_h0["probabilities"].get(phase, 0.0)
            for phase in PHASES
        },
        "source_collected_at": intramonth.get("source_collected_at"),
        "source_coverage": parse_source_coverage(intramonth.get("source_coverage_json")),
    }
```

Parse coverage JSON defensively, expose calculation date and collection timestamp separately, and never expose raw million-row vintage data.

- [ ] **Step 4: Verify the DB-only boundary**

Keep service imports limited to loaders and pure interpretation functions. Existing source contract must still reject `finance.data.economic_cycle_vintages`, collector names, job functions, and UI action events.

- [ ] **Step 5: Run service tests**

Run: `.venv/bin/python -m pytest tests/test_economic_cycle_service.py tests/test_market_context_economic_cycle.py -q`

Expected: all tests PASS.

- [ ] **Step 6: Commit the service unit**

```bash
git add app/services/overview/economic_cycle.py tests/test_economic_cycle_service.py tests/test_market_context_economic_cycle.py
git commit -m "경제사이클 월말 월중 비교 계약 추가"
```

---

### Task 6: Render the intramonth flow block and cycle-map bridge

**Files:**
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/style.css`
- Modify: `tests/test_market_context_economic_cycle.py`
- Rebuild: `app/web/streamlit_components/economic_cycle_workbench/component_static/`

**Interfaces:**
- Consumes Task 5 `CyclePayload.intramonth`.
- Produces `IntramonthFlow` and optional `intramonth-bridge-path` SVG elements.

- [ ] **Step 1: Write RED source-contract tests**

```python
def test_cycle_component_renders_intramonth_flow_without_touching_ribbon() -> None:
    assert "type IntramonthSnapshot" in source
    assert "function IntramonthFlow" in source
    assert "현재 입수정보 기반 잠정 계산" in source
    assert 'className="intramonth-bridge-path"' in source
    assert "payload.intramonth" in source
    assert "history.concat(payload.intramonth" not in source
```

Assert CSS contains desktop and 420px layouts plus distinct bridge legend styling.

- [ ] **Step 2: Run RED UI tests**

Run: `.venv/bin/python -m pytest tests/test_market_context_economic_cycle.py -q`

Expected: FAIL because the flow block and bridge do not exist.

- [ ] **Step 3: Add TypeScript payload types and a compact flow block**

Render monthly and intramonth date/phase/confidence, signed probability deltas, four factor deltas, `source_collected_at`, and a bounded latest-source summary. Do not render raw job counts or provider diagnostics.

- [ ] **Step 4: Add the separate cycle-map bridge**

Compute one coordinate from `intramonth.current_horizon.probabilities`. Draw exactly one dashed segment from monthly h0 to intramonth h0, add a distinct point, legend, keyboard-focus tooltip, and no intermediate points.

- [ ] **Step 5: Add responsive styles**

Desktop uses a three-part baseline/change/current layout. At 760px and 420px it stacks to one column, allows label wrapping, and preserves `overflow-x: hidden`.

- [ ] **Step 6: Run Python UI contract tests and TypeScript build**

Run: `.venv/bin/python -m pytest tests/test_market_context_economic_cycle.py -q`

Run: `npm run build`

Working directory: `app/web/streamlit_components/economic_cycle_workbench`

Expected: tests PASS and Vite production build completes.

- [ ] **Step 7: Commit the UI unit**

```bash
git add app/web/streamlit_components/economic_cycle_workbench/src app/web/streamlit_components/economic_cycle_workbench/component_static tests/test_market_context_economic_cycle.py
git commit -m "Overview 경제사이클 월중 흐름 표시"
```

---

### Task 7: Apply schema and materialize one actual local nowcast safely

**Files:**
- Update runtime DB schema only through existing schema sync functions.
- Update: `.aiworkspace/note/finance/tasks/active/overview-economic-cycle-intramonth-nowcast-v1-20260721/RUNS.md`
- Update: `.aiworkspace/note/finance/tasks/active/overview-economic-cycle-intramonth-nowcast-v1-20260721/RISKS.md`

**Interfaces:**
- Consumes Tasks 1-4 production functions.
- Produces one actual `intramonth_nowcast` row for 2026-07-21 when local stored input is usable.

- [ ] **Step 1: Capture pre-existing monthly invariants**

Run a read-only query that records count and SHA-256 over stable serialized fields for all `run_kind IN ('current','historical_replay') AND as_of_date <= '2026-06-30'`. Save only summary values in `RUNS.md`, not raw rows.

- [ ] **Step 2: Sync only the economic-cycle result schema**

Run: `.venv/bin/python -c "from finance.data.economic_cycle_results import ensure_economic_cycle_result_schemas; ensure_economic_cycle_result_schemas(); print('economic-cycle result schemas ready')"`

Expected: exit 0 and the new nullable columns plus enum value exist.

- [ ] **Step 3: Materialize from already stored vintages before external refresh**

Run the production intramonth materializer with `as_of_date='2026-07-21'`. Expected: one `intramonth_nowcast` row with baseline `2026-06-30`, usable h0 probabilities, and source collection timestamp `2026-07-16 10:02:56` or later.

- [ ] **Step 4: Recheck month-end invariants and nowcast isolation**

Expected: the pre-existing monthly count/hash is identical; exactly one intramonth business key exists for 2026-07-21. Re-run the same materializer and confirm the key count stays one.

- [ ] **Step 5: Exercise the scheduled collector only when the credential exists**

Run: `.venv/bin/python -m app.jobs.overview_automation --profile safe --job economic_cycle_intramonth --force --json`

Expected with `FRED_API_KEY`: success or partial_success and incremental overlap metadata. Expected without the credential: failed job, zero new snapshot writes, and the prior last-good row preserved. Record the observed branch exactly in `RUNS.md`.

- [ ] **Step 6: Commit actual-run documentation only**

```bash
git add .aiworkspace/note/finance/tasks/active/overview-economic-cycle-intramonth-nowcast-v1-20260721/RUNS.md .aiworkspace/note/finance/tasks/active/overview-economic-cycle-intramonth-nowcast-v1-20260721/RISKS.md
git commit -m "경제사이클 월중 실제 데이터 검증 기록"
```

---

### Task 8: Verify the full workflow, Browser QA, and durable docs

**Files:**
- Modify: `.aiworkspace/note/finance/docs/INDEX.md`
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/architecture/DATA_DB_PIPELINE_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/runbooks/OVERVIEW_MARKET_INTELLIGENCE.md`
- Modify: `.aiworkspace/note/finance/docs/runbooks/AUTOMATION_SCRIPTS.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Modify: task `STATUS.md`, `RUNS.md`, `RISKS.md`

**Interfaces:**
- Verifies all previous tasks and closes the durable documentation boundary.

- [ ] **Step 1: Run the focused Python suite**

Run: `.venv/bin/python -m pytest tests/test_economic_cycle_vintages.py tests/test_economic_cycle_results.py tests/test_economic_cycle_pipeline.py tests/test_economic_cycle_refresh.py tests/test_economic_cycle_service.py tests/test_market_context_economic_cycle.py -q`

Expected: all focused tests PASS.

- [ ] **Step 2: Run service-boundary and compile verification**

Run: `.venv/bin/python -m pytest tests/test_service_contracts.py -q -k 'economic_cycle or overview_automation or browser_safe_profile'`

Run: `.venv/bin/python -m py_compile finance/data/economic_cycle_vintages.py finance/data/economic_cycle_results.py finance/loaders/economic_cycle.py finance/economic_cycle_pipeline.py app/jobs/economic_cycle_refresh.py app/jobs/overview_automation.py app/services/overview/economic_cycle.py`

Expected: selected tests and compilation PASS.

- [ ] **Step 3: Rebuild the React component from a clean output directory**

Run: `npm run build`

Working directory: `app/web/streamlit_components/economic_cycle_workbench`

Expected: production bundle generated under tracked `component_static/`.

- [ ] **Step 4: Perform actual desktop and 420px Browser QA**

Open `Workspace > Overview > Market Context > 경제 사이클` and verify:

- 월말 날짜 and latest intramonth calculation date are both visible.
- `현재 입수정보 기반 잠정 계산` is visible.
- one dashed monthly-to-intramonth segment appears; ribbon cell count is unchanged.
- source collection timestamp and latest observation dates do not masquerade as calculation date.
- desktop and 420px horizontal overflow are zero; console/page errors are zero.

Capture one generated screenshot outside Git staging.

- [ ] **Step 5: Synchronize durable documentation**

Document incremental collection, weekday scheduler profiles, closed-month rollover, snapshot run-kind semantics, DB-only service path, last-good failure behavior, and current roadmap completion. Keep root logs to 3-5 lines and detailed commands in task `RUNS.md`.

- [ ] **Step 6: Run final diff and documentation checks**

Run: `git diff --check`

Run: `git status --short`

Expected: no whitespace errors; only intended code/docs/static assets are staged, while pre-existing research, `.superpowers/`, and QA PNG files remain untracked and excluded.

- [ ] **Step 7: Commit closeout**

```bash
git add finance/data/db/schema.py finance/data/economic_cycle_results.py finance/data/economic_cycle_vintages.py finance/loaders/economic_cycle.py finance/economic_cycle_pipeline.py
git add app/jobs/economic_cycle_refresh.py app/jobs/overview_automation.py app/services/overview/economic_cycle.py
git add app/web/streamlit_components/economic_cycle_workbench/src app/web/streamlit_components/economic_cycle_workbench/component_static
git add tests/test_economic_cycle_vintages.py tests/test_economic_cycle_results.py tests/test_economic_cycle_pipeline.py tests/test_economic_cycle_refresh.py tests/test_economic_cycle_service.py tests/test_market_context_economic_cycle.py tests/test_service_contracts.py
git add docs/superpowers/specs/2026-07-21-economic-cycle-intramonth-nowcast-design.md docs/superpowers/plans/2026-07-21-economic-cycle-intramonth-nowcast.md
git add .aiworkspace/note/finance/docs/INDEX.md .aiworkspace/note/finance/docs/ROADMAP.md .aiworkspace/note/finance/docs/PROJECT_MAP.md .aiworkspace/note/finance/docs/architecture/DATA_DB_PIPELINE_FLOW.md .aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md .aiworkspace/note/finance/docs/runbooks/OVERVIEW_MARKET_INTELLIGENCE.md .aiworkspace/note/finance/docs/runbooks/AUTOMATION_SCRIPTS.md
git add .aiworkspace/note/finance/WORK_PROGRESS.md .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md .aiworkspace/note/finance/tasks/active/overview-economic-cycle-intramonth-nowcast-v1-20260721
git commit -m "경제사이클 월중 나우캐스트 완료"
```

Do not stage registries, saved JSONL, run history, research work, `.superpowers/`, or generated screenshots.
