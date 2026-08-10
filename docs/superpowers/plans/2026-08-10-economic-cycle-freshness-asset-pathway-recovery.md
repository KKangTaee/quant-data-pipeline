# Economic Cycle Freshness and Asset Pathway Recovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reduce the synchronous economic-cycle refresh bottleneck, keep asset-pathway source data current, and show delayed last-good measurements without using them as current signals.

**Architecture:** Split provider fetch from DB write so the 17 ALFRED series can be fetched with at most four workers and written idempotently in catalog order. Add one bounded asset-pathway ingestion job that reuses the existing FRED/EIA/futures/equity writers, then combine cycle and asset freshness in a DB-only service contract so the manual action runs only stale scopes. Preserve delayed measurements in the pure pathway layer while keeping them ineligible for direction/support aggregation.

**Tech Stack:** Python 3, pytest, MySQL helpers already in the repository, `concurrent.futures.ThreadPoolExecutor`, Streamlit, React 18, TypeScript, Vitest, Vite.

## Global Constraints

- Keep `Ingestion -> DB -> Loader -> Service -> UI`; normal render paths remain provider-free and write-free.
- Keep the existing `자산별 확인 포인트` card layout, asset order, visual hierarchy, and economic-cycle phase calculation.
- Do not add a raw run/job/row diagnostic panel.
- Use at most four concurrent ALFRED fetch workers; perform DB UPSERTs on the caller thread in catalog order.
- Keep existing stable business keys and UPSERT behavior; no DB schema change is allowed in this task.
- Keep daily-series freshness at five business days and weekly EIA freshness at fourteen calendar days.
- A delayed last-good measurement may be displayed with its date, but must not contribute to current pathway direction, support, coverage, or transition logic.
- Keep S&P 500 actual TTM EPS on the existing official completed-quarter workbook boundary; do not infer or substitute EPS.
- Preserve last-good snapshots and rows when any provider or postcondition fails.
- Preserve unrelated dirty worktree files and do not stage run history, run artifacts, screenshots, registries, or `.superpowers/`.

## File Structure

- `finance/data/economic_cycle_vintages.py`: fetch/normalize the 17 revision-aware series concurrently and write them serially.
- `app/jobs/economic_cycle_asset_refresh.py`: compose the existing bounded FRED/EIA/futures/SPX-SPY ingestion jobs.
- `app/services/overview/economic_cycle_asset_freshness.py`: pure source-frequency freshness evaluation plus DB-only loader adapter.
- `app/jobs/overview_automation.py`: register the daily weekday asset refresh without adding a new scheduler.
- `app/jobs/overview_actions.py`: run only stale cycle/asset scopes and verify both postconditions.
- `finance/economic_cycle_asset_pathways.py`: preserve stale measurement values while excluding them from current signals.
- `app/services/overview/economic_cycle.py`: attach asset freshness to the economic-cycle read model.
- `app/web/overview/market_context_helpers.py`: reflect compact staged progress and invalidate the economic-cycle cache only after usable results.
- `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx`: render `갱신 지연` values and the combined freshness summary without changing card structure.
- `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.test.tsx`: lock the delayed-state and freshness UI behavior.
- `tests/test_economic_cycle_vintages.py`: verify bounded concurrency, deterministic writes, and failure isolation.
- `tests/test_economic_cycle_asset_refresh.py`: verify bounded source composition and result aggregation.
- `tests/test_economic_cycle_asset_freshness.py`: verify daily/weekly freshness and DB-only scope decisions.
- `tests/test_economic_cycle_refresh.py`: verify selective orchestration, postconditions, and last-good preservation.
- `tests/test_economic_cycle_asset_pathways.py`: verify delayed measurement preservation and signal exclusion.
- `tests/test_economic_cycle_service.py`: verify the combined read-model contract.
- `tests/test_market_context_economic_cycle.py`: verify event/cache and source-level UI contracts.
- `.aiworkspace/note/finance/tasks/active/economic-cycle-freshness-asset-pathway-recovery-v1-20260810/`: task plan, status, evidence, runs, and risks.
- `.aiworkspace/note/finance/docs/architecture/DATA_DB_PIPELINE_FLOW.md`: document the new daily asset job and selective manual fallback.
- `.aiworkspace/note/finance/docs/data/DATA_QUALITY_AND_PIT_NOTES.md`: document delayed-measurement display versus current-signal eligibility.

---

### Task 1: Bounded Concurrent Economic-Cycle Vintage Collection

**Files:**
- Modify: `finance/data/economic_cycle_vintages.py`
- Modify: `tests/test_economic_cycle_vintages.py`
- Create: `.aiworkspace/note/finance/tasks/active/economic-cycle-freshness-asset-pathway-recovery-v1-20260810/PLAN.md`
- Create: `.aiworkspace/note/finance/tasks/active/economic-cycle-freshness-asset-pathway-recovery-v1-20260810/DESIGN.md`
- Create: `.aiworkspace/note/finance/tasks/active/economic-cycle-freshness-asset-pathway-recovery-v1-20260810/STATUS.md`
- Create: `.aiworkspace/note/finance/tasks/active/economic-cycle-freshness-asset-pathway-recovery-v1-20260810/NOTES.md`
- Create: `.aiworkspace/note/finance/tasks/active/economic-cycle-freshness-asset-pathway-recovery-v1-20260810/RUNS.md`
- Create: `.aiworkspace/note/finance/tasks/active/economic-cycle-freshness-asset-pathway-recovery-v1-20260810/RISKS.md`

**Interfaces:**
- Consumes: existing `iter_fred_vintage_pages(...)`, `normalize_fred_vintage_rows(...)`, `upsert_economic_cycle_vintages(...)`, and `load_latest_vintage_realtime_starts(...)`.
- Produces: `collect_incremental_economic_cycle_vintages(..., max_workers: int = 4) -> dict[str, object]` with the existing summary keys and deterministic catalog-order writes.

- [ ] **Step 1: Create the active task record with the approved scope**

Create `PLAN.md` with:

```markdown
# Economic Cycle Freshness and Asset Pathway Recovery Plan

## 이걸 하는 이유

경제사이클 수동 최신화의 실제 75.616~96.836초 지연을 줄이고, 별도 자산 경로의 stale DB rows 때문에 측정값 전체가 `자료 부족`으로 사라지는 문제를 해결한다.

## Roadmap

- 1차: bounded concurrent vintage fetch와 deterministic DB write
- 2차: asset refresh, scope freshness, delayed measurement/UI
- 3차: actual refresh, Browser QA, durable documentation

## Completion

- stale scope만 갱신한다.
- delayed last-good measurement는 날짜와 함께 보이지만 현재 신호에서 제외된다.
- 기존 자산 카드 구조와 경제사이클 phase 계산을 유지한다.
```

Create the remaining task files with this exact starting content:

`DESIGN.md`

```markdown
# Economic Cycle Freshness and Asset Pathway Recovery Design

Approved design: [2026-08-10 economic-cycle freshness and asset pathway recovery](../../../../../../docs/superpowers/specs/2026-08-10-economic-cycle-freshness-asset-pathway-recovery-design.md)
```

`STATUS.md`

```markdown
# Economic Cycle Freshness and Asset Pathway Recovery Status

State: active
Last Updated: 2026-08-10

## Current Position

- 1차 구현 시작
- 설계 승인과 실제 지연/DB stale 진단 완료
```

`NOTES.md`

```markdown
# Notes

- 실제 manual refresh baseline: 96.836초, 75.616초.
- 2026-08-10 cycle snapshot은 최신이지만 asset pathway daily rows는 2026-07-27~31에 머물러 별도 freshness scope가 필요하다.
- delayed last-good measurement는 표시하되 current signal eligibility는 false로 둔다.
```

`RUNS.md`

```markdown
# Runs

- 2026-08-10: 구현 전 read-only 진단 완료.
```

`RISKS.md`

```markdown
# Risks

- FRED/ALFRED, EIA와 yfinance 응답 시간·rate limit은 로컬 코드 밖의 변동 요인이다.
- bounded concurrency는 worker 4개를 넘기지 않고 DB write는 단일 caller thread에서 수행한다.
- official S&P actual EPS가 없으면 그 경로의 제한은 의도적으로 남는다.
```

- [ ] **Step 2: Write a failing concurrency and write-order test**

Add to `tests/test_economic_cycle_vintages.py`:

```python
def test_incremental_collection_fetches_in_parallel_and_writes_catalog_order() -> None:
    module = _load_vintage_module()
    barrier = threading.Barrier(2)
    active = 0
    max_active = 0
    lock = threading.Lock()
    written: list[str] = []

    def page_iter(series_id: str, **_kwargs):
        nonlocal active, max_active
        with lock:
            active += 1
            max_active = max(max_active, active)
        barrier.wait(timeout=2)
        yield [{
            "date": "2026-06-01",
            "realtime_start": "2026-07-03",
            "realtime_end": "9999-12-31",
            "value": "100",
        }]
        with lock:
            active -= 1

    def writer(rows, **_kwargs):
        written.extend(str(row["series_id"]) for row in rows)
        return len(rows)

    result = module.collect_incremental_economic_cycle_vintages(
        series_ids=["PAYEMS", "INDPRO"],
        api_key="x" * 32,
        connection=object(),
        realtime_start_loader=lambda *_args, **_kwargs: {},
        page_iter=page_iter,
        writer=writer,
        max_workers=2,
    )

    assert max_active == 2
    assert written == ["PAYEMS", "INDPRO"]
    assert result["stored"] == 2
    assert result["failed"] == []
```

Add `import threading` at the top of the test module.

- [ ] **Step 3: Run the concurrency test and confirm RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_economic_cycle_vintages.py::test_incremental_collection_fetches_in_parallel_and_writes_catalog_order -q
```

Expected: FAIL because `max_workers` is not accepted and the existing collector is serial.

- [ ] **Step 4: Implement fetch/normalize isolation and caller-thread writes**

Add `ThreadPoolExecutor` and `as_completed` imports and a focused helper:

```python
def _fetch_incremental_vintage_rows(
    series_id: str,
    *,
    spec: IndicatorSpec,
    collected_at: datetime,
    realtime_start: str,
    api_key: str,
    session: Any,
    page_size: int,
    timeout: int,
    retries: int,
    page_iter: Any,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for payload_rows in page_iter(
        series_id,
        api_key=api_key,
        session=session,
        realtime_start=realtime_start,
        page_size=page_size,
        timeout=timeout,
        retries=retries,
    ):
        rows.extend(
            normalize_fred_vintage_rows(
                spec,
                payload_rows,
                collected_at=collected_at,
            )
        )
    return rows
```

Extend `collect_incremental_economic_cycle_vintages` with `max_workers: int = 4`. Resolve `worker_count = max(1, min(int(max_workers), 4, len(requested)))`, submit one helper call per requested series, store successful rows in `fetched_by_series`, and store exceptions in `failed_by_series`. After all futures finish, iterate `requested` and call `writer(rows, connection=db)` only on the caller thread. Rebuild `stored`, `coverage`, `found`, `missing`, and `failed` in requested order. Keep `collection_mode="incremental_overlap"` and add `fetch_workers` to the summary.

- [ ] **Step 5: Add a failing partial-failure preservation test**

Add:

```python
def test_incremental_parallel_collection_keeps_other_series_when_one_fetch_fails() -> None:
    module = _load_vintage_module()
    written: list[str] = []

    def page_iter(series_id: str, **_kwargs):
        if series_id == "PAYEMS":
            raise RuntimeError("provider gap")
        yield [{
            "date": "2026-06-01",
            "realtime_start": "2026-07-03",
            "realtime_end": "9999-12-31",
            "value": "100",
        }]

    result = module.collect_incremental_economic_cycle_vintages(
        series_ids=["PAYEMS", "INDPRO"],
        api_key="x" * 32,
        connection=object(),
        realtime_start_loader=lambda *_args, **_kwargs: {},
        page_iter=page_iter,
        writer=lambda rows, **_kwargs: written.extend(
            str(row["series_id"]) for row in rows
        ) or len(rows),
        max_workers=2,
    )

    assert written == ["INDPRO"]
    assert result["stored"] == 1
    assert result["missing"] == ["PAYEMS"]
    assert result["failed"][0]["series_id"] == "PAYEMS"
```

- [ ] **Step 6: Run the vintage suite and confirm GREEN**

Run:

```bash
.venv/bin/python -m pytest tests/test_economic_cycle_vintages.py tests/test_economic_cycle_refresh.py -q
```

Expected: all tests pass, including existing overlap and failure-stop contracts.

- [ ] **Step 7: Record the run and commit Task 1**

Append the command and pass count to the active task `RUNS.md`, update `STATUS.md` to `Current Position: 1차 완료 · 2차 준비`, then run:

```bash
git add finance/data/economic_cycle_vintages.py tests/test_economic_cycle_vintages.py .aiworkspace/note/finance/tasks/active/economic-cycle-freshness-asset-pathway-recovery-v1-20260810
git commit -m "성능: 경제사이클 빈티지 수집 병렬화"
```

---

### Task 2: Bounded Asset-Pathway Refresh Job and Daily Automation

**Files:**
- Create: `app/jobs/economic_cycle_asset_refresh.py`
- Create: `tests/test_economic_cycle_asset_refresh.py`
- Modify: `app/jobs/overview_automation.py`
- Modify: `tests/test_service_contracts.py`

**Interfaces:**
- Consumes: `run_collect_macro_market_context`, `run_collect_futures_ohlcv`, `run_collect_ohlcv`, `DEFAULT_PATHWAY_SERIES`, and `DEFAULT_ASSET_SYMBOLS`.
- Produces: `run_economic_cycle_asset_pathway_refresh(...) -> JobResult` with `job_name="refresh_economic_cycle_asset_pathways"` and source-level results under `details["steps"]`.

- [ ] **Step 1: Write failing bounded-scope job tests**

Create `tests/test_economic_cycle_asset_refresh.py` with three fake runners and these assertions:

```python
def test_asset_refresh_uses_only_economic_cycle_pathway_sources() -> None:
    from app.jobs.economic_cycle_asset_refresh import (
        run_economic_cycle_asset_pathway_refresh,
    )

    calls: dict[str, object] = {}

    def macro_runner(**kwargs):
        calls["macro"] = kwargs
        return {"job_name": "macro", "status": "success", "rows_written": 9, "failed_symbols": []}

    def futures_runner(**kwargs):
        calls["futures"] = kwargs
        return {"job_name": "futures", "status": "success", "rows_written": 4, "failed_symbols": []}

    def equity_runner(symbols, **kwargs):
        calls["equity"] = {"symbols": symbols, **kwargs}
        return {"job_name": "equity", "status": "success", "rows_written": 2, "failed_symbols": []}

    result = run_economic_cycle_asset_pathway_refresh(
        macro_runner=macro_runner,
        futures_runner=futures_runner,
        equity_runner=equity_runner,
    )

    assert tuple(calls["macro"]["series_ids"]) == (
        "DGS2", "DGS10", "DFII10", "T10YIE", "VIXCLS", "BAA10Y",
        "WCESTUS1", "WCRFPUS2", "WRPUPUS2",
    )
    assert calls["futures"]["symbols"] == ["GC=F", "DX-Y.NYB", "CL=F", "HG=F"]
    assert calls["futures"]["period"] == "1y"
    assert calls["futures"]["interval"] == "1d"
    assert calls["equity"]["symbols"] == ["^GSPC", "SPY"]
    assert result["status"] == "success"
    assert result["rows_written"] == 15
```

Add the partial-failure case:

```python
def test_asset_refresh_keeps_price_success_when_macro_fails() -> None:
    from app.jobs.economic_cycle_asset_refresh import (
        run_economic_cycle_asset_pathway_refresh,
    )

    result = run_economic_cycle_asset_pathway_refresh(
        macro_runner=lambda **_kwargs: {
            "job_name": "macro",
            "status": "failed",
            "rows_written": 0,
            "failed_symbols": ["DGS2"],
        },
        futures_runner=lambda **_kwargs: {
            "job_name": "futures",
            "status": "success",
            "rows_written": 4,
            "failed_symbols": [],
        },
        equity_runner=lambda *_args, **_kwargs: {
            "job_name": "equity",
            "status": "success",
            "rows_written": 2,
            "failed_symbols": [],
        },
    )

    assert result["status"] == "partial_success"
    assert result["rows_written"] == 6
    assert result["failed_symbols"] == ["DGS2"]
    assert [row["scope"] for row in result["details"]["steps"]] == [
        "macro", "futures", "equity",
    ]
```

- [ ] **Step 2: Run the new tests and confirm RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_economic_cycle_asset_refresh.py -q
```

Expected: FAIL because the job module does not exist.

- [ ] **Step 3: Implement the asset refresh composer**

Create the module with constants copied from the existing loader and a single public job function:

```python
from __future__ import annotations

from datetime import datetime
from time import perf_counter
from typing import Any, Callable

from app.jobs.ingestion_jobs import (
    JobResult,
    run_collect_futures_ohlcv,
    run_collect_macro_market_context,
    run_collect_ohlcv,
)
from finance.loaders.economic_cycle_assets import DEFAULT_PATHWAY_SERIES

ASSET_FUTURES_SYMBOLS = ("GC=F", "DX-Y.NYB", "CL=F", "HG=F")
ASSET_EQUITY_SYMBOLS = ("^GSPC", "SPY")

def _failed_step(scope: str, exc: Exception) -> JobResult:
    return {
        "scope": scope,
        "job_name": f"economic_cycle_asset_{scope}",
        "status": "failed",
        "rows_written": 0,
        "failed_symbols": [],
        "message": f"{type(exc).__name__}: {exc}",
    }

def run_economic_cycle_asset_pathway_refresh(
    *,
    macro_runner: Callable[..., JobResult] = run_collect_macro_market_context,
    futures_runner: Callable[..., JobResult] = run_collect_futures_ohlcv,
    equity_runner: Callable[..., JobResult] = run_collect_ohlcv,
) -> JobResult:
    started_at = datetime.now()
    started = perf_counter()
    calls = (
        (
            "macro",
            lambda: macro_runner(series_ids=DEFAULT_PATHWAY_SERIES),
        ),
        (
            "futures",
            lambda: futures_runner(
                symbols=list(ASSET_FUTURES_SYMBOLS),
                period="1y",
                interval="1d",
                cadence_mode="economic_cycle_asset_daily",
                max_symbols=4,
                batch_size=4,
                sleep_sec=0.1,
                materialize_snapshot=False,
            ),
        ),
        (
            "equity",
            lambda: equity_runner(
                list(ASSET_EQUITY_SYMBOLS),
                period="1mo",
                interval="1d",
                execution_profile="managed_safe",
            ),
        ),
    )
    steps: list[JobResult] = []
    for scope, call in calls:
        try:
            row = dict(call())
            row["scope"] = scope
        except Exception as exc:
            row = _failed_step(scope, exc)
        steps.append(row)
    statuses = {str(row.get("status") or "failed") for row in steps}
    rows_written = sum(int(row.get("rows_written") or 0) for row in steps)
    failed_symbols = sorted({
        str(symbol)
        for row in steps
        for symbol in row.get("failed_symbols") or []
    })
    status = (
        "failed"
        if statuses <= {"failed", "error"}
        else "partial_success"
        if statuses - {"success"}
        else "success"
    )
    finished_at = datetime.now()
    return {
        "job_name": "refresh_economic_cycle_asset_pathways",
        "status": status,
        "started_at": started_at.strftime("%Y-%m-%d %H:%M:%S"),
        "finished_at": finished_at.strftime("%Y-%m-%d %H:%M:%S"),
        "duration_sec": round(perf_counter() - started, 3),
        "rows_written": rows_written,
        "symbols_requested": 15,
        "symbols_processed": 15 - len(failed_symbols),
        "failed_symbols": failed_symbols,
        "message": "Economic-cycle asset pathway refresh completed.",
        "details": {"steps": steps},
    }
```

Call macro with `series_ids=DEFAULT_PATHWAY_SERIES`; call futures with the four symbols, `period="1y"`, `interval="1d"`, `cadence_mode="economic_cycle_asset_daily"`, `max_symbols=4`, `batch_size=4`, `sleep_sec=0.1`, and `materialize_snapshot=False`; call equity with the two symbols, `period="1mo"`, `interval="1d"`, and `execution_profile="managed_safe"`. Execute the three bounded steps serially to avoid multiplying provider concurrency beyond the ALFRED worker pool. Return `success`, `partial_success`, or `failed` based on step results and keep each compact result in `details["steps"]`.

- [ ] **Step 4: Write a failing automation registration test**

Add to the existing automation contract section in `tests/test_service_contracts.py`:

```python
def test_overview_automation_registers_daily_economic_cycle_asset_refresh(self) -> None:
    from app.jobs import overview_automation

    spec = next(
        item
        for item in overview_automation.OVERVIEW_AUTOMATION_JOB_SPECS
        if item.job_id == "economic_cycle_asset_pathways"
    )

    self.assertEqual(spec.job_name, "refresh_economic_cycle_asset_pathways")
    self.assertEqual(spec.cadence_minutes, 24 * 60)
    self.assertTrue(spec.weekdays_only)
    self.assertFalse(spec.market_hours_only)
    self.assertIn("safe", spec.profiles)
```

- [ ] **Step 5: Register the existing-automation job**

Import `run_economic_cycle_asset_pathway_refresh`, add `_run_economic_cycle_asset_pathways(_: datetime) -> JobResult`, and add a `ScheduledJobSpec` directly after `economic_cycle_intramonth`:

```python
ScheduledJobSpec(
    job_id="economic_cycle_asset_pathways",
    job_name="refresh_economic_cycle_asset_pathways",
    label="Economic Cycle Asset Pathways",
    cadence_minutes=24 * 60,
    profiles=("safe", "standard", "broad"),
    market_hours_only=False,
    runner=_run_economic_cycle_asset_pathways,
    description="Refresh DB-backed rates, EIA, futures, and SPX/SPY inputs used by Economic Cycle asset pathways.",
    weekdays_only=True,
),
```

- [ ] **Step 6: Run focused job and automation tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_economic_cycle_asset_refresh.py tests/test_service_contracts.py -k 'economic_cycle_asset or overview_automation' -q
```

Expected: all selected tests pass.

- [ ] **Step 7: Commit Task 2**

Append results to `RUNS.md`, then run:

```bash
git add app/jobs/economic_cycle_asset_refresh.py app/jobs/overview_automation.py tests/test_economic_cycle_asset_refresh.py tests/test_service_contracts.py .aiworkspace/note/finance/tasks/active/economic-cycle-freshness-asset-pathway-recovery-v1-20260810/RUNS.md
git commit -m "기능: 경제사이클 자산 경로 일일 갱신 추가"
```

---

### Task 3: Frequency-Aware Asset Freshness Read Model

**Files:**
- Create: `app/services/overview/economic_cycle_asset_freshness.py`
- Create: `tests/test_economic_cycle_asset_freshness.py`
- Modify: `app/services/overview/economic_cycle.py`
- Modify: `tests/test_economic_cycle_service.py`

**Interfaces:**
- Consumes: DB-only rows from `load_economic_cycle_market_series` and `load_economic_cycle_asset_prices`.
- Produces: `build_asset_pathway_freshness(market_rows, price_rows, *, reference_date) -> dict[str, object]` and `load_asset_pathway_freshness(*, reference_date) -> dict[str, object]`.

- [ ] **Step 1: Write failing daily/weekly freshness tests**

Create `tests/test_economic_cycle_asset_freshness.py` with row factories and these cases:

```python
def test_asset_freshness_separates_daily_business_age_and_weekly_calendar_age() -> None:
    from app.services.overview.economic_cycle_asset_freshness import (
        build_asset_pathway_freshness,
    )

    market_rows = [
        {"series_id": series_id, "observation_date": "2026-08-07", "value": 1.0}
        for series_id in ("DGS2", "DGS10", "DFII10", "T10YIE", "VIXCLS", "BAA10Y")
    ] + [
        {"series_id": series_id, "observation_date": "2026-07-31", "value": 1.0}
        for series_id in ("WCESTUS1", "WCRFPUS2", "WRPUPUS2")
    ]
    price_rows = [
        {"provider_symbol": symbol, "candle_time_utc": "2026-08-07", "close": 100.0}
        for symbol in ("GC=F", "DX-Y.NYB", "CL=F", "HG=F", "^GSPC", "SPY")
    ]

    result = build_asset_pathway_freshness(
        market_rows,
        price_rows,
        reference_date="2026-08-10",
    )

    assert result["status"] == "READY"
    assert result["refresh_required"] is False
    assert result["stale_series"] == []
```

Add exact stale/missing coverage:

```python
def test_asset_freshness_reports_exact_stale_and_missing_series() -> None:
    from app.services.overview.economic_cycle_asset_freshness import (
        build_asset_pathway_freshness,
    )

    market_rows = [
        {"series_id": series_id, "observation_date": "2026-08-07", "value": 1.0}
        for series_id in ("DGS10", "T10YIE", "VIXCLS", "BAA10Y")
    ] + [
        {"series_id": "DGS2", "observation_date": "2026-07-27", "value": 1.0},
        {"series_id": "WCESTUS1", "observation_date": "2026-07-24", "value": 1.0},
        {"series_id": "WCRFPUS2", "observation_date": "2026-07-31", "value": 1.0},
        {"series_id": "WRPUPUS2", "observation_date": "2026-07-31", "value": 1.0},
    ]
    price_rows = [
        {"provider_symbol": symbol, "candle_time_utc": "2026-08-07", "close": 100.0}
        for symbol in ("GC=F", "DX-Y.NYB", "CL=F", "HG=F", "^GSPC", "SPY")
    ]

    result = build_asset_pathway_freshness(
        market_rows,
        price_rows,
        reference_date="2026-08-10",
    )

    assert result["status"] == "REFRESH_AVAILABLE"
    assert result["refresh_required"] is True
    assert result["stale_series"] == ["DGS2", "WCESTUS1"]
    assert result["missing_series"] == ["DFII10"]
```

- [ ] **Step 2: Run the freshness tests and confirm RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_economic_cycle_asset_freshness.py -q
```

Expected: FAIL because the new service module does not exist.

- [ ] **Step 3: Implement the pure freshness evaluator and DB-only adapter**

Define exact source groups:

```python
DAILY_MACRO_SERIES = ("DGS2", "DGS10", "DFII10", "T10YIE", "VIXCLS", "BAA10Y")
WEEKLY_MACRO_SERIES = ("WCESTUS1", "WCRFPUS2", "WRPUPUS2")
DAILY_PRICE_SERIES = ("GC=F", "DX-Y.NYB", "CL=F", "HG=F", "^GSPC", "SPY")
DAILY_MAX_BUSINESS_AGE = 5
WEEKLY_MAX_CALENDAR_AGE = 14
```

For each group, select the maximum stored date not after `reference_date`. Daily age uses `len(pd.bdate_range(latest, reference, inclusive="right"))`; weekly age uses `(reference - latest).days`. Return:

```python
{
    "status": "READY" | "REFRESH_AVAILABLE" | "MISSING" | "ERROR",
    "reference_date": "YYYY-MM-DD",
    "latest_observation_date": "YYYY-MM-DD" | None,
    "refresh_required": bool,
    "stale_series": list[str],
    "missing_series": list[str],
    "series": {
        "DGS2": {"latest_date": "2026-08-07", "status": "READY"},
    },
    "message": str,
}
```

The loader adapter must call only the two existing DB readers with a bounded date window and must never import a provider or job module.

- [ ] **Step 4: Write a failing combined service-contract test**

Add to `tests/test_economic_cycle_service.py`:

```python
def test_service_combines_cycle_and_asset_freshness_without_provider_access() -> None:
    service = _load_service()
    intramonth = _intramonth_snapshot()
    intramonth["as_of_date"] = "2026-08-10"
    model = service.build_economic_cycle_read_model(
        snapshot_loader=lambda **_kwargs: _ready_snapshot(),
        intramonth_loader=lambda **_kwargs: intramonth,
        history_loader=lambda **_kwargs: [],
        market_series_loader=lambda **_kwargs: [],
        asset_price_loader=lambda **_kwargs: [],
        sp500_earnings_loader=lambda **_kwargs: {},
        freshness_date=date(2026, 8, 10),
    )

    freshness = model["data_freshness"]
    assert freshness["cycle_snapshot"]["status"] == "READY"
    assert freshness["asset_pathways"]["status"] == "MISSING"
    assert freshness["overall_status"] == "MISSING"
    assert freshness["refresh_required_scopes"] == ["asset_pathways"]
    assert freshness["action"]["id"] == "refresh_economic_cycle_data"
```

- [ ] **Step 5: Attach the combined freshness payload in the service**

After `market_rows` and `asset_price_rows` are loaded, build asset freshness from those same rows. Keep the existing cycle freshness keys for compatibility and add:

```python
data_freshness = {
    **cycle_freshness,
    "status": overall_status,
    "overall_status": overall_status,
    "cycle_snapshot": cycle_freshness,
    "asset_pathways": asset_freshness,
    "refresh_required_scopes": required_scopes,
    "refresh_required": bool(required_scopes),
    "message": combined_user_message,
}
```

Expose the existing action whenever either scope requires refresh. Do not place provider diagnostics or row counts in the read model.

- [ ] **Step 6: Run freshness and service tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_economic_cycle_asset_freshness.py tests/test_economic_cycle_freshness.py tests/test_economic_cycle_service.py -q
```

Expected: all tests pass; update only existing service expectations that intentionally treated cycle-only freshness as the entire page freshness.

Before changing an existing assertion, confirm its fixture omits asset rows and update the expected top-level status to the new overall status while preserving its `cycle_snapshot` assertion.

- [ ] **Step 7: Commit Task 3**

Append results to `RUNS.md`, then run:

```bash
git add app/services/overview/economic_cycle_asset_freshness.py app/services/overview/economic_cycle.py tests/test_economic_cycle_asset_freshness.py tests/test_economic_cycle_service.py .aiworkspace/note/finance/tasks/active/economic-cycle-freshness-asset-pathway-recovery-v1-20260810/RUNS.md
git commit -m "기능: 경제사이클 자산 최신성 범위 분리"
```

---

### Task 4: Scope-Aware Manual Refresh and Postconditions

**Files:**
- Modify: `app/jobs/overview_actions.py`
- Modify: `app/web/overview/market_context_helpers.py`
- Modify: `tests/test_economic_cycle_refresh.py`
- Modify: `tests/test_market_context_economic_cycle.py`

**Interfaces:**
- Consumes: `load_asset_pathway_freshness`, `run_economic_cycle_asset_pathway_refresh`, existing cycle snapshot loader, and existing cycle refresh runner.
- Produces: extended `run_overview_economic_cycle_refresh(...) -> JobResult` details with `requested_scopes`, `refreshed_scopes`, `failed_scopes`, and `cache_scopes`.

- [ ] **Step 1: Write failing selective-orchestration tests**

Add three tests to `tests/test_economic_cycle_refresh.py`:

```python
def test_overview_refresh_runs_only_stale_asset_scope() -> None:
    from app.jobs.overview_actions import run_overview_economic_cycle_refresh
    calls: list[str] = []
    asset_rows = iter([
        {"status": "REFRESH_AVAILABLE", "refresh_required": True},
        {"status": "READY", "refresh_required": False},
    ])

    result = run_overview_economic_cycle_refresh(
        as_of_date=date(2026, 8, 10),
        refresh_runner=lambda **_kwargs: (_ for _ in ()).throw(
            AssertionError("cycle refresh must not run")
        ),
        snapshot_loader=lambda **_kwargs: {"as_of_date": "2026-08-10"},
        asset_freshness_loader=lambda **_kwargs: next(asset_rows),
        asset_refresh_runner=lambda: calls.append("asset") or {
            "job_name": "refresh_economic_cycle_asset_pathways",
            "status": "success",
            "rows_written": 10,
            "failed_symbols": [],
        },
    )

    assert calls == ["asset"]
    assert result["status"] == "success"
    assert result["details"]["requested_scopes"] == ["asset_pathways"]
    assert result["details"]["cache_scopes"] == ["asset_pathways"]
```

Add cycle-only coverage:

```python
def test_overview_refresh_runs_only_stale_cycle_scope() -> None:
    from app.jobs.overview_actions import run_overview_economic_cycle_refresh
    snapshots = iter([{"as_of_date": "2026-08-07"}, {"as_of_date": "2026-08-10"}])
    cycle_calls: list[date] = []

    result = run_overview_economic_cycle_refresh(
        as_of_date=date(2026, 8, 10),
        refresh_runner=lambda *, as_of_date: cycle_calls.append(as_of_date) or {
            "job_name": "refresh_economic_cycle_intramonth",
            "status": "success",
            "rows_written": 1,
            "failed_symbols": [],
        },
        snapshot_loader=lambda **_kwargs: next(snapshots),
        asset_freshness_loader=lambda **_kwargs: {
            "status": "READY",
            "refresh_required": False,
        },
        asset_refresh_runner=lambda: (_ for _ in ()).throw(
            AssertionError("asset refresh must not run")
        ),
    )

    assert cycle_calls == [date(2026, 8, 10)]
    assert result["details"]["requested_scopes"] == ["cycle_snapshot"]
    assert result["details"]["cache_scopes"] == ["cycle_snapshot"]
```

Add both-stale partial-failure coverage:

```python
def test_overview_refresh_keeps_successful_asset_scope_when_cycle_fails() -> None:
    from app.jobs.overview_actions import run_overview_economic_cycle_refresh
    snapshots = iter([{"as_of_date": "2026-08-07"}, {"as_of_date": "2026-08-07"}])
    assets = iter([
        {"status": "REFRESH_AVAILABLE", "refresh_required": True, "stale_series": ["DGS2"]},
        {"status": "READY", "refresh_required": False, "stale_series": []},
    ])

    result = run_overview_economic_cycle_refresh(
        as_of_date=date(2026, 8, 10),
        refresh_runner=lambda **_kwargs: {
            "job_name": "refresh_economic_cycle_intramonth",
            "status": "failed",
            "rows_written": 0,
            "failed_symbols": ["PAYEMS"],
        },
        snapshot_loader=lambda **_kwargs: next(snapshots),
        asset_freshness_loader=lambda **_kwargs: next(assets),
        asset_refresh_runner=lambda: {
            "job_name": "refresh_economic_cycle_asset_pathways",
            "status": "success",
            "rows_written": 10,
            "failed_symbols": [],
        },
    )

    assert result["status"] == "partial_success"
    assert result["details"]["cache_scopes"] == ["asset_pathways"]
    assert result["details"]["failed_scopes"] == ["cycle_snapshot"]
    assert result["details"]["after_as_of_date"] == "2026-08-07"
```

- [ ] **Step 2: Run the selective tests and confirm RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_economic_cycle_refresh.py -q
```

Expected: FAIL because the action has no asset freshness/runner parameters.

- [ ] **Step 3: Implement scope planning and postcondition checks**

Extend the function signature:

```python
def run_overview_economic_cycle_refresh(
    *,
    as_of_date: str | date | datetime | None = None,
    refresh_runner: Callable[..., JobResult] = run_economic_cycle_intramonth_refresh,
    snapshot_loader: Callable[..., dict[str, object] | None] = load_cycle_snapshot,
    asset_freshness_loader: Callable[..., dict[str, object]] = load_asset_pathway_freshness,
    asset_refresh_runner: Callable[[], JobResult] = run_economic_cycle_asset_pathway_refresh,
    progress_callback: Callable[[str], None] | None = None,
) -> JobResult:
```

Read before-state for both scopes, form `requested_scopes`, emit compact stages (`경기 지표 확인`, `자산 경로 확인`, `화면 다시 계산`), run only requested scopes, then re-read both scopes. A cycle scope succeeds only when persisted `as_of_date >= target`; an asset scope succeeds only when after-state is `READY` or its stale/missing series count strictly improves. No requested scopes returns an immediate no-op success without provider calls.

- [ ] **Step 4: Write a failing UI progress/cache test**

Add to `tests/test_market_context_economic_cycle.py`:

```python
def test_cycle_ui_refresh_uses_compact_progress_and_usable_cache_scopes() -> None:
    helpers = importlib.import_module("app.web.overview.market_context_helpers")
    writes: list[str] = []
    status = Mock()
    status.__enter__ = Mock(return_value=status)
    status.__exit__ = Mock(return_value=None)

    with (
        patch.object(helpers.st, "status", return_value=status),
        patch.object(status, "write", side_effect=writes.append),
        patch.object(
            helpers,
            "run_overview_economic_cycle_refresh",
            side_effect=lambda progress_callback: (
                progress_callback("자산 경로 확인")
                or {"status": "success", "message": "반영 완료", "details": {"cache_scopes": ["asset_pathways"]}}
            ),
        ),
    ):
        result = helpers._run_economic_cycle_refresh_for_ui()

    assert result["status"] == "success"
    assert writes == ["자산 경로 확인"]
```

- [ ] **Step 5: Connect compact progress without adding diagnostics**

Pass `progress_callback=status.write` from `_run_economic_cycle_refresh_for_ui`. Keep the existing one-shot result reflection to only `status` and `message`. The event handler clears `load_economic_cycle_model` when `details.cache_scopes` is non-empty and the result is not `failed`; it does not render scope IDs, rows, failures, or provider payloads.

- [ ] **Step 6: Run action and helper tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_economic_cycle_refresh.py tests/test_market_context_economic_cycle.py -q
```

Expected: all tests pass, including duplicate nonce and incomplete cache-preservation tests.

- [ ] **Step 7: Commit Task 4**

Append results to `RUNS.md`, then run:

```bash
git add app/jobs/overview_actions.py app/web/overview/market_context_helpers.py tests/test_economic_cycle_refresh.py tests/test_market_context_economic_cycle.py .aiworkspace/note/finance/tasks/active/economic-cycle-freshness-asset-pathway-recovery-v1-20260810/RUNS.md
git commit -m "기능: 경제사이클 최신화 범위 선택 실행"
```

---

### Task 5: Preserve Delayed Measurements but Exclude Current Signals

**Files:**
- Modify: `finance/economic_cycle_asset_pathways.py`
- Modify: `tests/test_economic_cycle_asset_pathways.py`

**Interfaces:**
- Consumes: existing daily/weekly point sequences and context builders.
- Produces: series evaluations with `freshness="CURRENT" | "DELAYED" | "UNAVAILABLE"`, `supports_current_signal: bool`, and delayed values/changes preserved.

- [ ] **Step 1: Replace the stale-rejection test with a failing delayed-measurement test**

Keep the short-history assertion and add:

```python
def test_evaluate_series_preserves_stale_measurement_but_blocks_current_signal() -> None:
    pathways = importlib.import_module("finance.economic_cycle_asset_pathways")
    points = _daily_points(
        start="2021-01-01",
        count=1400,
        start_value=3.0,
        step=0.001,
    )
    reference = pd.Timestamp(points[-1]["date"]) + pd.offsets.BDay(8)

    result = pathways.evaluate_series(
        points,
        series_id="DGS2",
        reference_date=reference.date(),
        change_mode="BASIS_POINT",
    )

    assert result["freshness"] == "DELAYED"
    assert result["reason_code"] == "STALE_SERIES"
    assert result["supports_current_signal"] is False
    assert result["current_value"] is not None
    assert result["changes"]["21d"] is not None
    assert result["changes"]["63d"] is not None
```

Add the weekly EIA contract:

```python
def test_weekly_evaluator_preserves_delayed_measurement() -> None:
    pathways = importlib.import_module("finance.economic_cycle_asset_pathways")
    points = [
        {"date": timestamp.date(), "value": 400_000.0 + index * 100.0}
        for index, timestamp in enumerate(
            pd.date_range(end="2026-07-24", periods=260, freq="W-FRI")
        )
    ]

    result = pathways.evaluate_weekly_series(
        points,
        series_id="WCESTUS1",
        reference_date="2026-08-10",
    )

    assert result["freshness"] == "DELAYED"
    assert result["reason_code"] == "STALE_SERIES"
    assert result["supports_current_signal"] is False
    assert result["current_value"] is not None
    assert result["changes"]["4w"] is not None
    assert result["changes"]["52w"] is not None
```

Add the context-level exclusion test:

```python
def test_delayed_rates_measurements_are_visible_but_not_current_support() -> None:
    pathways = importlib.import_module("finance.economic_cycle_asset_pathways")
    rows = _macro_history({
        "DGS2": "UP",
        "DGS10": "UP",
        "DFII10": "UP",
        "T10YIE": "DOWN",
    })
    latest = max(pd.Timestamp(row["observation_date"]) for row in rows)
    reference = (latest + pd.offsets.BDay(8)).date()

    rates = pathways.build_asset_pathway_contexts(
        evidence=_economic_evidence(),
        market_rows=rows,
        price_rows=[],
        reference_date=reference,
    )["rates"]

    assert rates["data_status"] == "DELAYED"
    assert rates["coverage"] == "INSUFFICIENT"
    assert all(row["current_value"] is not None for row in rates["current_movement"])
    assert {row["status"] for row in rates["observed_pathways"]} == {"DELAYED"}
```

- [ ] **Step 2: Run the pathway tests and confirm RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_economic_cycle_asset_pathways.py -q
```

Expected: FAIL because stale evaluation currently returns null measurements.

- [ ] **Step 3: Compute before applying the stale status**

In `evaluate_series`, determine `is_stale` after finding the latest date, but continue through history, changes, and threshold calculations. Return:

```python
{
    "series_id": series_id,
    "as_of_date": latest_date.isoformat(),
    "current_value": values[-1],
    "unit": unit,
    "freshness": "DELAYED" if is_stale else "CURRENT",
    "reason_code": "STALE_SERIES" if is_stale else None,
    "supports_current_signal": not is_stale,
    "changes": changes,
    "thresholds": thresholds,
    "directions": derived_directions,
}
```

For missing/short history return `supports_current_signal=False`. Apply the same structure to the weekly evaluator. `evaluate_spread` must preserve `current_level_bp` and display directions when its source evaluation is delayed, but must set `structure_status="UNAVAILABLE"` for current-signal aggregation.

- [ ] **Step 4: Mark delayed pathways explicitly and keep aggregation conservative**

Change `build_observed_pathway` to return `DELAYED` when `freshness=="DELAYED"`; return `UNAVAILABLE` only when no usable measurement exists. Keep `_series_status` returning `UNAVAILABLE` whenever `supports_current_signal` is false. Add `data_status="DELAYED"` to an asset context when at least one delayed measurement exists and the context is not fully current; otherwise use `CURRENT` or `INSUFFICIENT`.

Change `_daily_direction_text` and `_weekly_direction_text` so delayed data says `갱신 지연 · 마지막 확인 YYYY-MM-DD` rather than `자료가 부족합니다`. Do not describe its directions as current support.

- [ ] **Step 5: Run pathway and interpretation regression tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_economic_cycle_asset_pathways.py tests/test_economic_cycle_asset_prices.py tests/test_economic_cycle_service.py -q
```

Expected: all tests pass; current fixtures retain existing directions and stale fixtures retain measurements without current support.

- [ ] **Step 6: Commit Task 5**

Append results and the eligibility rule to `NOTES.md`/`RUNS.md`, then run:

```bash
git add finance/economic_cycle_asset_pathways.py tests/test_economic_cycle_asset_pathways.py .aiworkspace/note/finance/tasks/active/economic-cycle-freshness-asset-pathway-recovery-v1-20260810/NOTES.md .aiworkspace/note/finance/tasks/active/economic-cycle-freshness-asset-pathway-recovery-v1-20260810/RUNS.md
git commit -m "수정: 지연된 자산 측정값과 현재 신호 분리"
```

---

### Task 6: Combined Freshness and Delayed-State UI

**Files:**
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.test.tsx`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/style.css`
- Modify: `tests/test_market_context_economic_cycle.py`
- Rebuild: `app/web/streamlit_components/economic_cycle_workbench/component_static/`

**Interfaces:**
- Consumes: combined `data_freshness`, `SeriesEvaluation.freshness="DELAYED"`, `ObservedPathway.status="DELAYED"`, and asset `data_status`.
- Produces: existing card markup with corrected `갱신 지연` labels, preserved measurements, and scope-aware freshness copy.

- [ ] **Step 1: Add failing React assertions for delayed values and combined freshness**

Add an exact fixture helper:

```tsx
function delayedFixture(): CyclePayload {
  const payload = fixture();
  payload.data_freshness = {
    ...payload.data_freshness!,
    status: "REFRESH_AVAILABLE",
    overall_status: "REFRESH_AVAILABLE",
    refresh_required: true,
    refresh_required_scopes: ["asset_pathways"],
    cycle_snapshot: {
      ...payload.data_freshness!,
      status: "READY",
      refresh_required: false,
    },
    asset_pathways: {
      status: "REFRESH_AVAILABLE",
      refresh_required: true,
      latest_observation_date: "2026-07-27",
      message: "자산 경로 갱신 필요",
    },
    action: {
      id: "refresh_economic_cycle_data",
      label: "최신 데이터 반영",
      enabled: true,
    },
  };
  payload.market_implications[0] = {
    ...payload.market_implications[0],
    coverage: "INSUFFICIENT",
    data_status: "DELAYED",
    current_movement: [{
      metric_id: "DGS2",
      label: "미국 2년 국채 수익률",
      as_of_date: "2026-07-27",
      current_value: 4.12,
      level_unit: "percent",
      change_unit: "bp",
      freshness: "DELAYED",
      reason_code: "STALE_SERIES",
      changes: { "21d": -8.0, "63d": -17.0 },
      directions: { "21d": "DOWN", "63d": "DOWN" },
    }],
    observed_pathways: [],
    current_interpretation: ["갱신 지연 · 마지막 확인 2026-07-27"],
  };
  return payload;
}
```

Add tests:

```tsx
it("shows delayed last-good measurements without calling them missing", () => {
  const html = renderToStaticMarkup(<EconomicCycleWorkbenchView payload={delayedFixture()} />);
  expect(html).toContain("갱신 지연");
  expect(html).toContain("마지막 확인 2026-07-27");
  expect(html).toContain("1개월(21거래일)");
  expect(html).not.toContain("DGS2</strong><span>1개월(21거래일) -");
});

it("describes only the stale freshness scopes", () => {
  const html = renderToStaticMarkup(<EconomicCycleWorkbenchView payload={delayedFixture()} />);
  expect(html).toContain("경제사이클 계산 최신");
  expect(html).toContain("자산 경로 갱신 필요");
  expect(html).toContain("최신 데이터 반영");
  expect(html).not.toContain("보통 1분 내외");
});
```

- [ ] **Step 2: Run React tests and confirm RED**

Run:

```bash
cd app/web/streamlit_components/economic_cycle_workbench && npm test
```

Expected: FAIL because TypeScript and labels support only current/unavailable states.

- [ ] **Step 3: Extend types and presentation mappings**

Add `DELAYED` to series freshness and observed pathway status. Add:

```tsx
type FreshnessStatus = "READY" | "REFRESH_AVAILABLE" | "MISSING" | "ERROR";
type FreshnessScope = {
  status: FreshnessStatus;
  refresh_required: boolean;
  message: string;
  latest_observation_date?: string | null;
};
type AssetDataStatus = "CURRENT" | "DELAYED" | "INSUFFICIENT";

const SERIES_FRESHNESS_LABEL = {
  CURRENT: "정상",
  DELAYED: "갱신 지연",
  UNAVAILABLE: "자료 부족",
} as const;

const PATHWAY_STATUS_LABEL = {
  OBSERVED: "관찰됨",
  DELAYED: "갱신 지연",
  UNAVAILABLE: "자료 부족",
} as const;
```

Change `SeriesEvaluation.freshness`, `MovementMetric.freshness`, and `PriceContext.freshness` to `"CURRENT" | "DELAYED" | "UNAVAILABLE"`; add `DELAYED` to `ObservedPathway.status`; add `data_status?: AssetDataStatus` to `MarketImplication` and `CommodityAsset`. Extend `EconomicCycleFreshness` with:

```tsx
overall_status?: FreshnessStatus;
cycle_snapshot?: FreshnessScope & {
  persisted_as_of_date?: string | null;
  target_as_of_date?: string | null;
};
asset_pathways?: FreshnessScope;
refresh_required_scopes?: ("cycle_snapshot" | "asset_pathways")[];
```

Use the mappings in `SeriesMetrics` and `ObservedPathwaysBlock`. When delayed, show `마지막 확인 {as_of_date}` and keep numeric metrics. For a price context that contains delayed returns, show a neutral `갱신 지연` badge rather than `확인 불가`.

- [ ] **Step 4: Update the Data Freshness copy without changing layout**

Keep the existing `.cycle-freshness-bar` structure. Replace the hard-coded one-minute copy with scope-aware text derived from `cycle_snapshot.status` and `asset_pathways.status`. Button label becomes `최신 데이터 반영`; collecting copy becomes `필요한 자료만 확인하는 중`. Keep the three compact dates/status facts and do not add job names, rows, provider response, or failure lists.

Add only neutral delayed-state CSS selectors (`.pathway-delayed`, `[data-status="DELAYED"]`) using the existing palette and spacing. Do not alter card grid, asset ordering, font scale, or expansion behavior.

- [ ] **Step 5: Update Python source-contract assertions**

In `tests/test_market_context_economic_cycle.py`, assert the source contains `DELAYED`, `갱신 지연`, `최신 데이터 반영`, and `필요한 자료만 확인하는 중`; remove only the outdated `보통 1분 내외` expectation. Keep assertions that `rows_written`, `failed_symbols`, and raw diagnostic copy are absent.

- [ ] **Step 6: Run React/Python tests, typecheck, and build**

Run:

```bash
cd app/web/streamlit_components/economic_cycle_workbench
npm test
npx tsc --noEmit
npm run build
cd ../../../../..
.venv/bin/python -m pytest tests/test_market_context_economic_cycle.py -q
git diff --check
```

Expected: React tests, TypeScript, Vite build, focused Python tests, and diff check pass.

- [ ] **Step 7: Commit Task 6**

Append build/test results to `RUNS.md`, then run:

```bash
git add app/web/streamlit_components/economic_cycle_workbench/src app/web/streamlit_components/economic_cycle_workbench/component_static tests/test_market_context_economic_cycle.py .aiworkspace/note/finance/tasks/active/economic-cycle-freshness-asset-pathway-recovery-v1-20260810/RUNS.md
git commit -m "UI: 경제사이클 갱신 지연과 선택 최신화 표시"
```

---

### Task 7: Actual Refresh, Performance Evidence, Browser QA, and Documentation

**Files:**
- Modify: `.aiworkspace/note/finance/tasks/active/economic-cycle-freshness-asset-pathway-recovery-v1-20260810/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/economic-cycle-freshness-asset-pathway-recovery-v1-20260810/NOTES.md`
- Modify: `.aiworkspace/note/finance/tasks/active/economic-cycle-freshness-asset-pathway-recovery-v1-20260810/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/economic-cycle-freshness-asset-pathway-recovery-v1-20260810/RISKS.md`
- Modify: `.aiworkspace/note/finance/docs/architecture/DATA_DB_PIPELINE_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/data/DATA_QUALITY_AND_PIT_NOTES.md`
- Modify if canonical ownership changed: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Generate but do not commit: `economic-cycle-freshness-asset-recovery-qa.png`

**Interfaces:**
- Consumes: completed jobs/read model/UI from Tasks 1-6.
- Produces: actual DB freshness evidence, measured duration comparison, Browser QA screenshot, and closeout documentation.

- [ ] **Step 1: Run the complete focused regression suite**

Run:

```bash
.venv/bin/python -m pytest \
  tests/test_economic_cycle_vintages.py \
  tests/test_economic_cycle_refresh.py \
  tests/test_economic_cycle_asset_refresh.py \
  tests/test_economic_cycle_asset_freshness.py \
  tests/test_economic_cycle_asset_pathways.py \
  tests/test_economic_cycle_asset_prices.py \
  tests/test_economic_cycle_freshness.py \
  tests/test_economic_cycle_service.py \
  tests/test_market_context_economic_cycle.py -q
```

Expected: all focused Python tests pass.

- [ ] **Step 2: Capture the pre-refresh monthly fingerprint**

Run:

```bash
.venv/bin/python - <<'PY'
from finance.data.db.mysql import MySQLClient

db = MySQLClient("localhost", "root", "1234", 3306)
try:
    db.use_db("finance_meta")
    rows = db.query("""
        SELECT run_kind,
               COUNT(*) AS row_count,
               MIN(as_of_date) AS first_date,
               MAX(as_of_date) AS last_date,
               SHA2(GROUP_CONCAT(
                   CONCAT_WS('|', as_of_date, run_kind, model_version, status)
                   ORDER BY as_of_date, run_kind SEPARATOR '\n'
               ), 256) AS stable_checksum
        FROM economic_cycle_snapshot
        WHERE run_kind IN ('current', 'historical_replay')
        GROUP BY run_kind
        ORDER BY run_kind
    """)
    print(rows)
finally:
    db.close()
PY
```

Record the compact result in task `RUNS.md`. This is the invariant baseline for the provider-writing steps that follow.

- [ ] **Step 3: Measure the optimized 17-series incremental collector**

Run:

```bash
.venv/bin/python - <<'PY'
import json
from time import perf_counter

from app.runtime_env import load_project_local_env
from finance.data.economic_cycle_vintages import (
    collect_incremental_economic_cycle_vintages,
)

load_project_local_env()
started = perf_counter()
result = collect_incremental_economic_cycle_vintages(max_workers=4)
print(json.dumps({
    "elapsed_sec": round(perf_counter() - started, 3),
    "requested": result.get("requested"),
    "stored": result.get("stored"),
    "failed": result.get("failed"),
    "missing": result.get("missing"),
    "fetch_workers": result.get("fetch_workers"),
}, ensure_ascii=False, default=str))
PY
```

Record only this compact output in `RUNS.md`; do not record the API key or raw provider payload. Compare elapsed time with 96.836s and 75.616s.

- [ ] **Step 4: Execute the real asset-pathway refresh and verify DB dates**

Run:

```bash
.venv/bin/python - <<'PY'
import json
from datetime import date

from app.jobs.economic_cycle_asset_refresh import (
    run_economic_cycle_asset_pathway_refresh,
)
from app.services.overview.economic_cycle_asset_freshness import (
    load_asset_pathway_freshness,
)

result = run_economic_cycle_asset_pathway_refresh()
freshness = load_asset_pathway_freshness(reference_date=date.today())
print(json.dumps({
    "job_status": result.get("status"),
    "duration_sec": result.get("duration_sec"),
    "failed_symbols": result.get("failed_symbols"),
    "freshness_status": freshness.get("status"),
    "stale_series": freshness.get("stale_series"),
    "missing_series": freshness.get("missing_series"),
    "series": freshness.get("series"),
}, ensure_ascii=False, default=str))
PY
```

Record:

```text
DGS2, DGS10, DFII10, T10YIE, VIXCLS, BAA10Y latest dates
WCESTUS1, WCRFPUS2, WRPUPUS2 latest dates
GC=F, DX-Y.NYB, CL=F, HG=F, ^GSPC, SPY latest dates
asset freshness status and stale/missing IDs
```

Expected: provider-supported series advance into their frequency-aware freshness windows. Any provider-specific failure remains explicit in `RISKS.md`, while last-good rows stay readable.

- [ ] **Step 5: Verify last-good and PIT invariants**

Before/after checks must establish:

```text
prior monthly economic_cycle_snapshot rows unchanged
intramonth business key remains unique
macro_series_vintage_observation writes remain idempotent
future observation dates are excluded by loaders
DELAYED measurements have supports_current_signal=false
actual EPS remains official completed-quarter only
```

Record compact counts/checksums and conclusions in `RUNS.md`; do not commit generated query dumps.

Repeat the Step 2 fingerprint command and assert the `current`/`historical_replay` row counts, first/last dates, and checksum are unchanged. Then run:

```bash
.venv/bin/python -m pytest \
  tests/test_economic_cycle_pipeline.py \
  tests/test_economic_cycle_results.py \
  tests/test_economic_cycle_asset_pathways.py \
  -q
```

Expected: PIT snapshot, business-key/idempotency, future-date exclusion, and delayed-signal eligibility tests pass.

- [ ] **Step 6: Start or reuse the local app and perform Browser QA**

Open `http://localhost:8503/overview?view=economic-cycle&overview_tab=economic-cycle` with the in-app browser. Verify:

```text
Data Freshness identifies only stale scopes
fresh asset data shows US Treasury yields, real yield, spread, VIX, and changes
delayed fixture/state shows values plus `갱신 지연`, not blank dashes
asset card layout/order is unchanged
no raw diagnostics are visible
no horizontal overflow at desktop and 420px width
no browser console error
```

Capture one screenshot to `/Users/taeho/Project/quant-data-pipeline-worktrees/main-dev/economic-cycle-freshness-asset-recovery-qa.png` and leave it untracked.

- [ ] **Step 7: Synchronize durable and task documentation**

Use `finance-doc-sync`. Add the daily asset ingestion and scope-aware fallback to `DATA_DB_PIPELINE_FLOW.md`. Add the distinction between `DELAYED` display and current-signal eligibility to `DATA_QUALITY_AND_PIT_NOTES.md`. Update `PROJECT_MAP.md` only if the implemented ownership boundary differs from its existing economic-cycle flow. Set task `STATUS.md` to `State: complete`, record completed 1차/2차/3차, and move unresolved provider-only limitations to `RISKS.md`.

- [ ] **Step 8: Run final verification**

Run:

```bash
git status --short
git diff --check
.venv/bin/python -m py_compile \
  finance/data/economic_cycle_vintages.py \
  finance/economic_cycle_asset_pathways.py \
  app/jobs/economic_cycle_asset_refresh.py \
  app/jobs/overview_actions.py \
  app/jobs/overview_automation.py \
  app/services/overview/economic_cycle_asset_freshness.py \
  app/services/overview/economic_cycle.py \
  app/web/overview/market_context_helpers.py
```

Expected: no syntax errors, no whitespace errors, and only intended tracked files plus pre-existing unrelated dirty files.

- [ ] **Step 9: Commit closeout documentation**

Stage only the task and durable documentation files, excluding the QA screenshot and all run artifacts:

```bash
git add \
  .aiworkspace/note/finance/tasks/active/economic-cycle-freshness-asset-pathway-recovery-v1-20260810 \
  .aiworkspace/note/finance/docs/architecture/DATA_DB_PIPELINE_FLOW.md \
  .aiworkspace/note/finance/docs/data/DATA_QUALITY_AND_PIT_NOTES.md \
  .aiworkspace/note/finance/docs/PROJECT_MAP.md
git diff --cached --check
git commit -m "문서: 경제사이클 최신성과 자산 경로 복구 정리"
```

If `PROJECT_MAP.md` has no ownership change, omit it from `git add` and state `canonical PROJECT_MAP change 없음` in task `STATUS.md`.
