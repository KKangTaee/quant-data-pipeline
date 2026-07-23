# NYSE Listing Universe Refresh V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an atomic stock+ETF NYSE listing refresh and expose it as the first action in the Ingestion operational workflow.

**Architecture:** Fetch and normalize both NYSE listing snapshots before any DB write. A single writer validates retention, replaces both current master tables in one transaction, preserves lifecycle and price history, and returns per-kind diffs. The Ingestion job, registry, dispatcher, guide, and compact UI action consume this contract.

**Tech Stack:** Python 3, pandas, PyMySQL, Streamlit, unittest/pytest

## Global Constraints

- `nyse_stock` and `nyse_etf` are current listing masters; `nyse_symbol_lifecycle` preserves listing evidence.
- Stock and ETF refresh is all-or-nothing. Partial success is not allowed.
- A source failure or suspicious row-count collapse must leave both current masters unchanged.
- Historical `finance_price.nyse_price_history`, registries, and saved setups must not be deleted or rewritten.
- The UI must be action-first and compact; do not add a job/row/raw-status diagnostic dashboard.
- The refresh must not automatically start daily price collection.
- Tests must be written and observed failing before production code is added.

---

### Task 1: Atomic listing source and persistence contract

**Files:**

- Modify: `finance/data/nyse.py`
- Modify: `finance/data/nyse_db.py`
- Create: `tests/test_nyse_listing_universe_refresh.py`

**Interfaces:**

- Produces: `fetch_nyse_listing_snapshot(kind: str) -> tuple[pd.DataFrame, dict[str, int]]`
- Produces: `refresh_nyse_listing_universe(frames: Mapping[str, pd.DataFrame], *, snapshot_date: str | None = None, minimum_retention_ratio: float = 0.8, db_factory: Callable[..., MySQLClient] = MySQLClient, host: str = "localhost", user: str = "root", password: str = "1234", port: int = 3306) -> dict[str, Any]`
- Produces: `load_nyse_listing_universe_status(...) -> dict[str, Any]`

- [ ] **Step 1: Write failing source and atomic-writer tests**

Add tests that define the desired API:

```python
def test_fetch_nyse_listing_snapshot_returns_frame_and_api_stats():
    with patch.object(nyse, "_fetch_api_rows", return_value=[
        {"normalizedTicker": "NEW", "instrumentName": "New Co", "url": "/quote/NEW", "total": 1},
    ]):
        frame, stats = nyse.fetch_nyse_listing_snapshot("stock")
    assert frame["symbol"].tolist() == ["NEW"]
    assert stats["api_total"] == 1


def test_refresh_replaces_stock_and_etf_in_one_transaction():
    db = FakeListingDB({"stock": {"OLD", "KEEP"}, "etf": {"OLDX", "KEEPX"}})
    summary = nyse_db.refresh_nyse_listing_universe(
        {
            "stock": listing_frame(("KEEP", "Keep"), ("NEW", "New")),
            "etf": listing_frame(("KEEPX", "Keep ETF"), ("NEWX", "New ETF")),
        },
        snapshot_date="2026-07-23",
        db_factory=lambda *args, **kwargs: db,
    )
    assert db.begin_count == 1
    assert db.commit_count == 1
    assert db.rollback_count == 0
    assert summary["kinds"]["stock"]["added_symbols"] == ["NEW"]
    assert summary["kinds"]["stock"]["removed_symbols"] == ["OLD"]
    assert summary["kinds"]["etf"]["added_symbols"] == ["NEWX"]
    assert summary["kinds"]["etf"]["removed_symbols"] == ["OLDX"]


def test_refresh_rejects_suspicious_collapse_before_transaction():
    db = FakeListingDB({"stock": {f"S{i}" for i in range(100)}, "etf": {f"E{i}" for i in range(100)}})
    with pytest.raises(ValueError, match="retention"):
        nyse_db.refresh_nyse_listing_universe(
            {"stock": listing_frame(("NEW", "New")), "etf": listing_frame(("NEWX", "New ETF"))},
            db_factory=lambda *args, **kwargs: db,
        )
    assert db.begin_count == 0


def test_refresh_rolls_back_both_kinds_on_write_failure():
    db = FakeListingDB({"stock": {"OLD"}, "etf": {"OLDX"}}, fail_on_write=True)
    with pytest.raises(RuntimeError, match="write failed"):
        nyse_db.refresh_nyse_listing_universe(
            {"stock": listing_frame(("NEW", "New")), "etf": listing_frame(("NEWX", "New ETF"))},
            minimum_retention_ratio=0.0,
            db_factory=lambda *args, **kwargs: db,
        )
    assert db.commit_count == 0
    assert db.rollback_count == 1
```

- [ ] **Step 2: Run tests and verify RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_nyse_listing_universe_refresh.py -q
```

Expected: FAIL because `fetch_nyse_listing_snapshot` and `refresh_nyse_listing_universe` do not exist.

- [ ] **Step 3: Implement snapshot fetcher**

In `finance/data/nyse.py`, extract the existing fetch/parse behavior:

```python
def fetch_nyse_listing_snapshot(kind: str) -> tuple[pd.DataFrame, dict[str, int]]:
    if kind not in NYSE_URLS:
        raise ValueError(f"kind는 {list(NYSE_URLS.keys())} 중 하나여야 합니다.")
    rows = _fetch_api_rows(kind)
    frame, stats = _parse_api_rows(rows)
    if frame.empty:
        raise RuntimeError(f"NYSE listing API returned no usable {kind} rows.")
    return frame, stats
```

Make `load_nyse_listings` call this function and preserve its optional CSV behavior.

- [ ] **Step 4: Implement atomic writer and status loader**

In `finance/data/nyse_db.py`:

```python
LISTING_KINDS = ("stock", "etf")


def refresh_nyse_listing_universe(
    frames,
    *,
    snapshot_date=None,
    minimum_retention_ratio=0.8,
    db_factory=MySQLClient,
    host="localhost",
    user="root",
    password="1234",
    port=3306,
):
    normalized = {kind: _normalize_listing_frame(frames[kind], kind=kind) for kind in LISTING_KINDS}
    db = db_factory(host, user, password, port)
    try:
        db.use_db(DB_NAME)
        _ensure_listing_schemas(db)
        existing = {kind: _load_current_listing_symbols(db, kind) for kind in LISTING_KINDS}
        _validate_listing_retention(normalized, existing, minimum_retention_ratio)
        summary = _build_listing_refresh_summary(normalized, existing, snapshot_date)
        db.begin()
        try:
            for kind in LISTING_KINDS:
                _replace_listing_master(db, kind=kind, frame=normalized[kind], existing_symbols=existing[kind])
                _upsert_symbol_lifecycle_rows(
                    db,
                    kind=kind,
                    frame=normalized[kind],
                    snapshot_date=snapshot_date,
                    ensure_schema=False,
                )
            db.commit()
        except Exception:
            db.rollback()
            raise
        return summary
    finally:
        db.close()
```

Add focused helpers for normalization, schema setup, symbol loading, retention validation, diff summary, master UPSERT/delete, and lifecycle `ensure_schema=False`. Make `load_nyse_csv_to_mysql` reuse the single-kind replace helper without changing its public signature.

Add `load_nyse_listing_universe_status` that reads current counts plus the latest
`nyse_listings_directory` lifecycle dates and returns `{status, kinds, latest_snapshot_date, message}` without mutating DB.

- [ ] **Step 5: Run focused tests and verify GREEN**

Run:

```bash
.venv/bin/python -m pytest tests/test_nyse_listing_universe_refresh.py -q
```

Expected: all Task 1 tests PASS.

- [ ] **Step 6: Commit Task 1**

```bash
git add finance/data/nyse.py finance/data/nyse_db.py tests/test_nyse_listing_universe_refresh.py
git diff --cached --check
git commit -m "기능: NYSE 종목 목록 원자적 최신화 구현"
```

---

### Task 2: Ingestion job, registry, dispatcher, and guide

**Files:**

- Modify: `app/jobs/ingestion_jobs.py`
- Modify: `app/web/ingestion/registry.py`
- Modify: `app/web/ingestion/dispatcher.py`
- Modify: `app/web/ingestion/guides.py`
- Modify: `tests/test_nyse_listing_universe_refresh.py`

**Interfaces:**

- Consumes: `fetch_nyse_listing_snapshot`, `refresh_nyse_listing_universe`
- Produces: `run_refresh_nyse_listing_universe(...) -> JobResult`
- Produces action name: `refresh_nyse_listing_universe`

- [ ] **Step 1: Write failing job and dispatch tests**

```python
def test_job_fetches_both_snapshots_before_writer():
    calls = []
    frames = {
        "stock": listing_frame(("NEW", "New")),
        "etf": listing_frame(("NEWX", "New ETF")),
    }

    def fetcher(kind):
        calls.append(("fetch", kind))
        return frames[kind], {"api_total": 1, "deduped_rows": 1}

    def writer(received, **kwargs):
        calls.append(("write", tuple(received)))
        return refresh_summary()

    result = ingestion_jobs.run_refresh_nyse_listing_universe(
        snapshot_fetcher=fetcher,
        writer=writer,
        snapshot_date="2026-07-23",
    )
    assert calls == [("fetch", "stock"), ("fetch", "etf"), ("write", ("stock", "etf"))]
    assert result["status"] == "success"


def test_job_does_not_write_when_etf_fetch_fails():
    writer = Mock()
    with patch.object(ingestion_jobs, "fetch_nyse_listing_snapshot") as fetcher:
        fetcher.side_effect = [
            (listing_frame(("NEW", "New")), {"api_total": 1}),
            RuntimeError("ETF source unavailable"),
        ]
        result = ingestion_jobs.run_refresh_nyse_listing_universe(writer=writer)
    assert result["status"] == "failed"
    writer.assert_not_called()


def test_action_is_registered_guided_and_dispatched():
    definition = registry.INGESTION_ACTION_REGISTRY["refresh_nyse_listing_universe"]
    assert definition["section"] == registry.INGESTION_COLLECTION_OPERATIONAL
    assert definition["target_tables"] == [
        "finance_meta.nyse_stock",
        "finance_meta.nyse_etf",
        "finance_meta.nyse_symbol_lifecycle",
    ]
    assert guides.JOB_GUIDE["refresh_nyse_listing_universe"]["title"] == "주식·ETF 종목 목록 최신화"
```

Patch the dispatcher runner and assert the action forwards `snapshot_date` and the progress callback.

- [ ] **Step 2: Run focused tests and verify RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_nyse_listing_universe_refresh.py -q
```

Expected: new tests FAIL because the job/action contract is missing.

- [ ] **Step 3: Implement job and action wiring**

Add imports for the fetcher/writer and implement:

```python
def run_refresh_nyse_listing_universe(
    *,
    snapshot_date=None,
    minimum_retention_ratio=0.8,
    snapshot_fetcher=fetch_nyse_listing_snapshot,
    writer=refresh_nyse_listing_universe,
    progress_callback=None,
) -> JobResult:
    job_name = "refresh_nyse_listing_universe"
    started_at = _now_str()
    t0 = perf_counter()
    try:
        frames = {}
        source_stats = {}
        for kind in ("stock", "etf"):
            _emit_stage_progress(progress_callback, event="stage_start", stage=f"fetch_{kind}")
            frames[kind], source_stats[kind] = snapshot_fetcher(kind)
            _emit_stage_progress(progress_callback, event="stage_complete", stage=f"fetch_{kind}")
        summary = writer(
            frames,
            snapshot_date=snapshot_date,
            minimum_retention_ratio=minimum_retention_ratio,
        )
        details = {**summary, "source_stats": source_stats, "masters_preserved": True}
        return _build_result(
            job_name=job_name,
            status="success",
            started_at=started_at,
            finished_at=_now_str(),
            duration_sec=perf_counter() - t0,
            rows_written=int(summary["rows_written"]),
            symbols_requested=int(summary["rows_written"]),
            symbols_processed=int(summary["rows_written"]),
            failed_symbols=[],
            message="NYSE stock and ETF listing universe refresh completed.",
            details=details,
        )
    except Exception as exc:
        return _build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=_now_str(),
            duration_sec=perf_counter() - t0,
            rows_written=0,
            symbols_requested=0,
            symbols_processed=0,
            failed_symbols=[],
            message=f"NYSE listing universe refresh failed; existing masters were preserved: {exc}",
            details={"masters_preserved": True},
        )
```

Register the action as operational/stage progress, add the guide copy, import the runner in
`dispatcher.py`, and dispatch it with `progress_callback`.

- [ ] **Step 4: Run focused and ingestion contract tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_nyse_listing_universe_refresh.py tests/test_ingestion_module_split_contracts.py -q
```

Expected: all tests PASS.

- [ ] **Step 5: Commit Task 2**

```bash
git add app/jobs/ingestion_jobs.py app/web/ingestion/registry.py app/web/ingestion/dispatcher.py app/web/ingestion/guides.py tests/test_nyse_listing_universe_refresh.py
git diff --cached --check
git commit -m "기능: Ingestion 종목 목록 최신화 작업 연결"
```

---

### Task 3: Compact Ingestion operational action

**Files:**

- Modify: `app/web/ingestion/page.py`
- Modify: `app/web/ingestion/sections.py`
- Modify: `tests/test_nyse_listing_universe_refresh.py`

**Interfaces:**

- Consumes: `load_nyse_listing_universe_status`
- Consumes action: `refresh_nyse_listing_universe`
- Produces: first operational action before `일별 가격 업데이트`

- [ ] **Step 1: Write failing UI contract tests**

```python
def test_operational_section_places_universe_refresh_before_daily_price_update():
    source = Path("app/web/ingestion/sections.py").read_text(encoding="utf-8")
    refresh_index = source.index('with st.expander("주식·ETF 종목 목록 최신화"')
    daily_index = source.index('with st.expander("일별 가격 업데이트"')
    assert refresh_index < daily_index
    assert '"action": "refresh_nyse_listing_universe"' in source
    assert '"주식·ETF 종목 목록 최신화"' in source
    assert "load_nyse_listing_universe_status" in Path("app/web/ingestion/page.py").read_text(encoding="utf-8")
```

- [ ] **Step 2: Run focused test and verify RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_nyse_listing_universe_refresh.py -q
```

Expected: UI placement test FAIL because the action is not rendered.

- [ ] **Step 3: Implement compact action-first UI**

Import `load_nyse_listing_universe_status` in `page.py`. At the start of
`render_operational_section`, before daily prices, render:

```python
with st.expander("주식·ETF 종목 목록 최신화", expanded=True):
    _render_job_brief("refresh_nyse_listing_universe")
    universe_status = load_nyse_listing_universe_status()
    kinds = universe_status.get("kinds") or {}
    stock_status = kinds.get("stock") or {}
    etf_status = kinds.get("etf") or {}
    st.caption(
        "전체 가격·자산 프로필 수집은 이 current listing master를 기준으로 합니다. "
        "가격 수집 전에 신규 상장 종목을 포함하려면 먼저 최신화하세요."
    )
    _render_collection_contract(
        "현재 기준",
        [
            ("기준일", universe_status.get("latest_snapshot_date") or "확인 불가"),
            ("주식", f"{int(stock_status.get('row_count') or 0):,} symbols"),
            ("ETF", f"{int(etf_status.get('row_count') or 0):,} symbols"),
            ("Source", "NYSE official listings directory"),
        ],
        note="목록만 최신화하며 가격 이력 수집은 자동으로 시작하지 않습니다.",
    )
    if st.button(
        "주식·ETF 종목 목록 최신화",
        use_container_width=True,
        disabled=_has_running_job(),
    ):
        _schedule_job({
            "action": "refresh_nyse_listing_universe",
            "job_name": "refresh_nyse_listing_universe",
            "spinner_text": "Refreshing NYSE stock and ETF listing universe...",
            "params": {},
            "run_metadata": _job_metadata(
                pipeline_type="nyse_listing_universe_refresh",
                execution_mode="operational",
                symbol_source="NYSE official listings directory",
                symbol_count=int(stock_status.get("row_count") or 0) + int(etf_status.get("row_count") or 0),
                execution_context="Explicit current stock and ETF listing universe refresh before downstream collection.",
            ),
        })
    _render_inline_last_completed_result("refresh_nyse_listing_universe")
```

Wire the standard progress callback while this action is running.

- [ ] **Step 4: Run focused and ingestion contract tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_nyse_listing_universe_refresh.py tests/test_ingestion_module_split_contracts.py -q
```

Expected: all tests PASS.

- [ ] **Step 5: Commit Task 3**

```bash
git add app/web/ingestion/page.py app/web/ingestion/sections.py tests/test_nyse_listing_universe_refresh.py
git diff --cached --check
git commit -m "개선: Ingestion 첫 화면에 종목 목록 최신화 배치"
```

---

### Task 4: Durable docs, actual refresh, Browser QA, and closeout

**Files:**

- Modify: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/architecture/DATA_DB_PIPELINE_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/data/README.md`
- Modify: `.aiworkspace/note/finance/docs/data/TABLE_SEMANTICS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/nyse-listing-universe-refresh-v1-20260723/{STATUS.md,NOTES.md,RUNS.md,RISKS.md}`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Create local-only: `nyse-listing-universe-refresh-v1-qa.png`

**Interfaces:**

- Consumes: completed data/job/UI contract
- Produces: durable source-of-truth docs and QA evidence

- [ ] **Step 1: Run the focused test suite and static checks**

```bash
.venv/bin/python -m pytest tests/test_nyse_listing_universe_refresh.py tests/test_ingestion_module_split_contracts.py -q
.venv/bin/python -m py_compile finance/data/nyse.py finance/data/nyse_db.py app/jobs/ingestion_jobs.py app/web/ingestion/dispatcher.py app/web/ingestion/sections.py
git diff --check
```

Expected: tests PASS, compilation exits 0, diff check emits no errors.

- [ ] **Step 2: Execute the real refresh once**

Run the job wrapper with the local DB and current NYSE API. Confirm:

- status is `success`
- stock and ETF master snapshot date is 2026-07-23
- current row counts match the fetched deduped counts
- `NYSE Stocks + ETFs` symbol source contains a sample of newly added symbols
- historical price row counts are not modified by the universe refresh

- [ ] **Step 3: Update durable docs and task records**

Document:

- NYSE official listings API → atomic current master replacement
- lifecycle preservation and non-deletion of price history
- Ingestion first action and explicit separation from daily price collection
- verification commands and actual added/removed counts
- roadmap status `3/3 complete`

- [ ] **Step 4: Run Browser QA**

Open Workspace > Ingestion and capture one screenshot showing:

- `주식·ETF 종목 목록 최신화` before `일별 가격 업데이트`
- current snapshot date and stock/ETF counts
- action button visible without a diagnostic dashboard

Save the screenshot as local generated evidence and do not stage it.

- [ ] **Step 5: Run final verification**

```bash
.venv/bin/python -m pytest tests/test_nyse_listing_universe_refresh.py tests/test_ingestion_module_split_contracts.py -q
.venv/bin/python -m py_compile finance/data/nyse.py finance/data/nyse_db.py app/jobs/ingestion_jobs.py app/web/ingestion/dispatcher.py app/web/ingestion/sections.py
git diff --check
git status --short
```

Expected: tests PASS, compilation exits 0, diff check clean, only intended source/docs/tests are staged or modified; generated/user artifacts remain unstaged.

- [ ] **Step 6: Commit Task 4**

```bash
git add finance/data/nyse.py finance/data/nyse_db.py app/jobs/ingestion_jobs.py app/web/ingestion/registry.py app/web/ingestion/dispatcher.py app/web/ingestion/guides.py app/web/ingestion/page.py app/web/ingestion/sections.py tests/test_nyse_listing_universe_refresh.py .aiworkspace/note/finance/docs .aiworkspace/note/finance/tasks/active/nyse-listing-universe-refresh-v1-20260723 .aiworkspace/note/finance/WORK_PROGRESS.md .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git diff --cached --check
git commit -m "문서: NYSE 종목 목록 최신화 운영 흐름 정리"
```
