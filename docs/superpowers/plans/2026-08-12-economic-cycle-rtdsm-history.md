# Economic Cycle RTDSM History Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a repeatable Philadelphia Fed RTDSM ingestion-to-DB-to-audit path and decide whether the expanded history is suitable for next-transition model experiments.

**Architecture:** A source module validates and streams four official wide XLSX workbooks into the existing source-neutral macro vintage ledger with provider-native IDs. A source-filtered loader reads only the observation window required by the transforms. A research-only module builds four-indicator point-in-time phases, reuses the independent transition sample gate, and evaluates pre-registered common-period parity against the current eight-indicator state.

**Tech Stack:** Python 3.12, openpyxl read-only XLSX parsing, pandas, PyMySQL, pytest, existing finance vintage schema and transition feasibility module.

## Global Constraints

- Use only official Philadelphia Fed RTDSM workbooks for long real-time history.
- Keep the current eight-indicator observed state and every asset checkpoint contract unchanged.
- Do not create or publish destination probabilities in this plan.
- Preserve point-in-time eligibility using conservative month-end known-at dates.
- Fail closed on malformed workbook contracts or partial source coverage.
- Write tests first and observe each relevant test fail before implementation.

---

### Task 1: RTDSM source parser and normalized batch writer

**Files:**
- Create: `finance/data/philadelphia_rtdsm.py`
- Create: `tests/test_philadelphia_rtdsm.py`

**Interfaces:**
- Consumes: `finance.data.fred_vintages.upsert_fred_vintage_rows`, `finance.data.db.schema.PROVIDER_SCHEMAS`.
- Produces: `RtdsmSeriesSpec`, `get_rtdsm_catalog()`, `parse_rtdsm_vintage_header()`, `iter_rtdsm_normalized_batches()`, `download_rtdsm_workbook()`, and `collect_rtdsm_history()`.

- [ ] **Step 1: Write failing catalog and header-date tests**

```python
def test_rtdsm_catalog_locks_four_provider_native_series():
    catalog = {item.series_id: item for item in get_rtdsm_catalog()}
    assert set(catalog) == {"IPT", "H", "EMPLOY", "RUC"}
    assert catalog["RUC"].vintage_frequency == "quarterly"

def test_rtdsm_headers_use_conservative_known_at_month_end():
    assert parse_rtdsm_vintage_header("EMPLOY64M12", "EMPLOY", "monthly") == date(1964, 12, 31)
    assert parse_rtdsm_vintage_header("RUC26Q2", "RUC", "quarterly") == date(2026, 5, 31)
```

- [ ] **Step 2: Run the header tests and confirm import failure**

Run: `.venv/bin/python -m pytest tests/test_philadelphia_rtdsm.py -k 'catalog or headers' -q`  
Expected: FAIL because `finance.data.philadelphia_rtdsm` does not exist.

- [ ] **Step 3: Implement the catalog, header parsing, and exact source constants**

```python
@dataclass(frozen=True)
class RtdsmSeriesSpec:
    series_id: str
    workbook_url: str
    sheet_name: str
    series_name: str
    factor_group: str
    vintage_frequency: str
    units: str
    transform: str
    direction: int
```

Reject prefix/frequency mismatches. Monthly headers map to calendar month-end; quarterly headers map to February, May, August, or November month-end.

- [ ] **Step 4: Write failing in-memory workbook normalization tests**

Build a tiny XLSX fixture, corrupt only its core timestamp to contain `T 8:`, and assert literal source, interval, value, missing-cell, incremental-overlap, malformed-sheet, duplicate-header, invalid-date, and all-missing behavior.

```python
rows = [
    row
    for batch in iter_rtdsm_normalized_batches(
        spec,
        payload,
        collected_at="2026-08-12 00:00:00",
        batch_size=2,
    )
    for row in batch
]
assert rows[0]["source"] == "philadelphia_fed_rtdsm"
assert rows[0]["realtime_start"] == "2020-01-31"
assert rows[0]["realtime_end"] == "2020-02-28"
assert rows[-1]["realtime_end"] == "9999-12-31"
```

- [ ] **Step 5: Run normalization tests and confirm the missing parser failure**

Run: `.venv/bin/python -m pytest tests/test_philadelphia_rtdsm.py -k 'normaliz or malformed or missing' -q`  
Expected: FAIL because workbook parsing is absent.

- [ ] **Step 6: Implement metadata-only repair and streaming wide-to-long batches**

Repair only `docProps/core.xml` in memory, validate workbook structure, precompute selected vintage intervals, and emit finite numeric cells in bounded batches. Include the stored latest vintage on incremental runs so its open interval is closed.

- [ ] **Step 7: Write failing download retry and batch-collection tests**

Use a request double that fails twice then returns bytes and a writer double that records batches. Assert three bounded attempts, source-specific incremental overlap, stable business keys, connection ownership, and compact coverage/failure summaries.

- [ ] **Step 8: Implement bounded download, schema setup, and idempotent collection**

Use the existing vintage schema and source-neutral UPSERT. Record a series failure without substituting revised data.

- [ ] **Step 9: Run all source tests**

Run: `.venv/bin/python -m pytest tests/test_philadelphia_rtdsm.py -q`  
Expected: PASS.

### Task 2: Source-filtered loader and four-indicator point-in-time panel

**Files:**
- Create: `finance/loaders/economic_cycle_realtime.py`
- Create: `finance/economic_cycle_realtime_history.py`
- Create: `tests/test_economic_cycle_realtime_history.py`

**Interfaces:**
- Produces: `load_rtdsm_signal_history()`, `build_rtdsm_monthly_panel()`, and `build_rtdsm_observed_history()`.

- [ ] **Step 1: Write a failing source-filtered loader test**

Inject mixed-source rows and assert only requested `philadelphia_fed_rtdsm` rows with eligible realtime dates and a twelve-month signal window are returned.

- [ ] **Step 2: Run the loader test and confirm import failure**

Run: `.venv/bin/python -m pytest tests/test_economic_cycle_realtime_history.py -k loader -q`  
Expected: FAIL because the loader module does not exist.

- [ ] **Step 3: Implement the DB-only loader**

Query the shared ledger with an exact source predicate, requested IDs, bounded vintage dates, and a twelve-month observation window.

- [ ] **Step 4: Write failing PIT transform tests with literal values**

Create two vintages where one observation is revised. Assert the early origin uses the first value, the later origin uses the revision, the three/six-month transforms are hand-derived, scaling uses only expanding history, and phase stays unavailable until all four signals plus level/momentum exist.

- [ ] **Step 5: Run panel tests and confirm the builder failure**

Run: `.venv/bin/python -m pytest tests/test_economic_cycle_realtime_history.py -k 'panel or transform or revision' -q`  
Expected: FAIL because the panel builder is absent.

- [ ] **Step 6: Implement the four-indicator research panel and observed history**

Group rows by provider series and vintage, select the newest eligible vintage per origin, apply the locked transforms and 60-month robust scale, calculate activity/labor composites and level/momentum, and return `ObservedStateResult` values without writing production snapshots.

- [ ] **Step 7: Run loader and panel tests**

Run: `.venv/bin/python -m pytest tests/test_economic_cycle_realtime_history.py -k 'loader or panel or transform or revision' -q`  
Expected: PASS.

### Task 3: Pre-registered parity and combined readiness audit

**Files:**
- Modify: `finance/economic_cycle_realtime_history.py`
- Modify: `tests/test_economic_cycle_realtime_history.py`

**Interfaces:**
- Produces: `RtdsmParityGate`, `RtdsmParityReport`, `RtdsmReadinessReport`, `evaluate_rtdsm_parity()`, and `evaluate_rtdsm_model_readiness()`.

- [ ] **Step 1: Write failing literal parity tests**

Use a hand-checked confusion fixture and assert overlap, exact agreement, level-side agreement, Cohen's kappa, reason codes, and the zero-variance kappa branch.

- [ ] **Step 2: Run parity tests and confirm missing functions**

Run: `.venv/bin/python -m pytest tests/test_economic_cycle_realtime_history.py -k parity -q`  
Expected: FAIL because parity evaluation is absent.

- [ ] **Step 3: Implement the locked parity gate**

Defaults are 96 overlapping months, 0.60 exact agreement, 0.40 Cohen's kappa, and 0.75 level-side agreement. Return `PASS` or `NO_GO_PARITY`.

- [ ] **Step 4: Write a failing combined-decision test**

Assert sample pass plus parity pass yields `GO_MODEL_EXPERIMENT`, sample failure yields `NO_GO_DATA`, and parity failure yields `NO_GO_PARITY`. Partial source coverage must never yield GO.

- [ ] **Step 5: Implement and verify the combined report**

Run: `.venv/bin/python -m pytest tests/test_economic_cycle_realtime_history.py -q`  
Expected: PASS.

### Task 4: Explicit job, actual official-file/DB audit, and closeout

**Files:**
- Modify: `app/jobs/ingestion_jobs.py`
- Modify: `tests/test_ingestion_jobs.py`
- Modify: `.aiworkspace/note/finance/docs/data/README.md`
- Modify: `.aiworkspace/note/finance/docs/data/TABLE_SEMANTICS.md`
- Modify: `.aiworkspace/note/finance/docs/architecture/DATA_DB_PIPELINE_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify: `.aiworkspace/note/finance/researches/active/2026-08-economic-cycle-independent-reaudit/FEATURE_CANDIDATES.md`
- Modify: `.aiworkspace/note/finance/researches/active/2026-08-economic-cycle-independent-reaudit/RECOMMENDATION.md`
- Modify: `.aiworkspace/note/finance/tasks/active/economic-cycle-rtdsm-history-v1-20260812/{STATUS,NOTES,RUNS,RISKS}.md`

**Interfaces:**
- Produces: `run_collect_economic_cycle_rtdsm_history()` and an actual recorded readiness result.

- [ ] **Step 1: Write a failing job result test**

Inject success, partial, and exception summaries. Assert stable job name/status, row count, failed IDs, source, and target table. Do not add a Streamlit diagnostics panel.

- [ ] **Step 2: Implement the explicit job wrapper and run its focused test**

Run: `.venv/bin/python -m pytest tests/test_ingestion_jobs.py -k rtdsm -q`  
Expected: PASS.

- [ ] **Step 3: Run focused tests before external ingestion**

Run: `.venv/bin/python -m pytest tests/test_philadelphia_rtdsm.py tests/test_economic_cycle_realtime_history.py tests/test_ingestion_jobs.py -k 'rtdsm or realtime_history' -q`  
Expected: PASS.

- [ ] **Step 4: Run official initial ingestion and DB reload**

Call `collect_rtdsm_history()` for all four IDs, assert no failed/missing IDs, reload through `load_rtdsm_signal_history()`, and record source coverage and elapsed time. Do not save workbooks in the repository.

- [ ] **Step 5: Run the actual combined readiness audit**

Build RTDSM and current strict-PIT histories through the latest complete common origin. Record overlap, exact agreement, kappa, level-side agreement, usable origins, independent events, holdout support, and final decision.

- [ ] **Step 6: Synchronize data/architecture, roadmap, research, and active task docs**

Document source semantics and the actual result. If either gate fails, keep model/UI blocked. If both pass, mark only model experimentation as next.

- [ ] **Step 7: Run full focused verification**

```bash
.venv/bin/python -m pytest tests/test_philadelphia_rtdsm.py tests/test_economic_cycle_realtime_history.py tests/test_economic_cycle_transition_feasibility.py tests/test_economic_cycle_vintages.py tests/test_economic_cycle_features.py tests/test_economic_cycle_observed_state.py tests/test_ingestion_jobs.py -q
.venv/bin/python -m py_compile finance/data/philadelphia_rtdsm.py finance/loaders/economic_cycle_realtime.py finance/economic_cycle_realtime_history.py app/jobs/ingestion_jobs.py
git diff --check
```

Expected: focused tests PASS, compilation PASS, and no whitespace errors.

- [ ] **Step 8: Commit only the coherent implementation unit**

Exclude registries, run history, screenshots, `.superpowers/`, and `run_artifacts/`.

