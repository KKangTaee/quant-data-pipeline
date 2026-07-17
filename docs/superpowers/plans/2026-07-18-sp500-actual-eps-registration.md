# S&P 500 실제 EPS 등록 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 사용자가 S&P 공식 Index Earnings XLSX와 발표일을 등록하면 actual As-Reported 분기 EPS를 release vintage로 저장하고, 8개 분기가 확보된 시점부터 경제 사이클의 실제 TTM EPS가 point-in-time 기준으로 활성화되게 한다.

**Architecture:** Workspace Ingestion은 업로드 파일의 bytes와 발표일만 job wrapper에 전달하고, `finance/data/sp500_valuation.py`의 canonical parser/importer가 명시적 period/status/basis를 검증해 `finance_meta.sp500_index_earnings`에 저장한다. Loader는 기준일 이후 발표 vintage를 SQL에서 제외하고 같은 분기의 당시 최신 vintage만 사용한다. S&P 서버의 403을 우회하지 않으며 Shiller proxy를 공식 actual로 승격하지 않는다.

**Tech Stack:** Python 3, pandas/openpyxl, PyMySQL, Streamlit, unittest/pytest, MySQL

## Global Constraints

- canonical source는 `sp_dow_jones_index_earnings`다.
- canonical source URL은 `https://www.spglobal.com/spdji/en/documents/additional-material/sp-500-eps-est.xlsx`다.
- 경제 사이클 계산에는 `quarterly + as_reported + actual + eps > 0`만 사용한다.
- current/prior TTM과 YoY 계산에는 서로 다른 완료 분기 8개가 필요하다.
- `period_end <= as_of_date`와 `source_release_date <= as_of_date`를 모두 적용한다.
- 추정치, mixed, Operating EPS, Shiller proxy는 실제 TTM EPS에 섞지 않는다.
- 파일명, 색상, 셀 위치 또는 발표일과 period의 상대적 위치만으로 actual/estimate를 추론하지 않는다.
- 공식 workbook에서 status/basis를 명시적으로 식별하지 못하면 저장하지 않는다.
- 공식 사이트의 403/Access Denied를 우회하거나 무인 scraping하지 않는다.
- 업로드 bytes와 임시 파일 경로를 DB의 `source_ref`에 저장하지 않는다.
- DB 저장 실패는 earnings batch 전체를 rollback한다.
- 첫 화면에는 raw job/row 진단보다 반영 분기 수, 최신 완료 분기, 8개까지 남은 분기를 보여준다.

---

## File Structure

- `finance/data/sp500_valuation.py`: 공식/정규화 workbook 구조 탐색, 명시적 EPS 정규화, transactional import, coverage 요약.
- `finance/data/db/mysql.py`: earnings batch에 사용할 명시적 transaction 경계.
- `finance/loaders/sp500_valuation.py`: as-of release-vintage 필터와 8분기 TTM read model.
- `app/jobs/ingestion_jobs.py`: 업로드 bytes를 canonical importer에 연결하는 단일 job wrapper.
- `app/web/ingestion/{registry.py,guides.py,dispatcher.py,sections.py}`: 등록 action, 설명, dispatch, 사용자 업로드 흐름.
- `tests/test_sp500_valuation.py`: parser/importer/loader 단위 테스트.
- `tests/test_ingestion_guides.py`, `tests/test_ingestion_sections.py`: action 및 화면 계약 테스트.
- `.aiworkspace/note/finance/tasks/active/overview-economic-cycle-sp500-actual-eps-registration-v1-20260718/`: 구현 기록.
- `.aiworkspace/note/finance/docs/data/{README.md,DATA_FLOW_MAP.md,TABLE_SEMANTICS.md}` 및 `.aiworkspace/note/finance/docs/architecture/DATA_DB_PIPELINE_FLOW.md`: durable data contract.

### Task 1: Active Task와 공식 workbook 파서 계약

**Files:**
- Create: `.aiworkspace/note/finance/tasks/active/overview-economic-cycle-sp500-actual-eps-registration-v1-20260718/{PLAN.md,DESIGN.md,STATUS.md,NOTES.md,RUNS.md,RISKS.md}`
- Modify: `tests/test_sp500_valuation.py`
- Modify: `finance/data/sp500_valuation.py`

**Interfaces:**
- Consumes: `bytes | str | pathlib.Path`, `source_release_date: str`.
- Produces: `read_sp500_index_earnings_workbook(workbook, *, source_release_date, source_ref=None, collected_at=None) -> list[dict[str, Any]]`.
- Produces: normalized rows with `period_end`, `period_type`, `earnings_basis`, `value_status`, `eps`, `source`, `source_ref`, `source_release_date`.

- [ ] **Step 1: Create the active task documents**

Write the approved spec path, three-stage roadmap, current stage 2, exact scope, verification commands, official-download 403 constraint, and raw-workbook sample risk into the six task files.

- [ ] **Step 2: Write failing parser tests**

Add tests that build in-memory XLSX fixtures with `pd.ExcelWriter(BytesIO(), engine="openpyxl")`:

```python
def test_index_earnings_reader_accepts_explicit_official_quarterly_sheet(self):
    workbook = _xlsx_bytes({
        "QUARTERLY DATA": pd.DataFrame({
            "Quarter End": ["2025-12-31", "2026-03-31", "2026-06-30"],
            "Status": ["Actual", "Actual", "Estimate"],
            "As Reported EPS": [70.0, 72.0, 74.0],
            "Operating EPS": [71.0, 73.0, 75.0],
        })
    })
    rows = read_sp500_index_earnings_workbook(
        workbook,
        source_release_date="2026-05-15",
        source_ref=SP500_INDEX_EARNINGS_URL,
    )
    assert {(row["earnings_basis"], row["value_status"]) for row in rows} == {
        ("as_reported", "actual"), ("as_reported", "estimate"),
        ("operating", "actual"), ("operating", "estimate"),
    }
```

Also add one test for the existing normalized first-sheet layout and one test asserting a workbook without explicit `Status` raises `ValueError` containing `actual/estimate 상태`.

- [ ] **Step 3: Run parser tests and verify RED**

Run: `.venv/bin/python -m pytest tests/test_sp500_valuation.py -k "index_earnings_reader" -q`

Expected: FAIL because the reader cannot consume bytes or search `QUARTERLY DATA` sheets.

- [ ] **Step 4: Implement the minimal explicit parser**

Add `BytesIO` and `BinaryIO` support, canonical URL constant, header canonicalization, and sheet iteration. A sheet is accepted only when the same header row explicitly exposes period, status, and at least one EPS basis column. Normalize with the existing `normalize_index_earnings_frame`; do not infer missing status.

```python
SP500_INDEX_EARNINGS_URL = (
    "https://www.spglobal.com/spdji/en/documents/additional-material/"
    "sp-500-eps-est.xlsx"
)

def _excel_source(workbook: str | Path | bytes | BinaryIO) -> Any:
    return BytesIO(workbook) if isinstance(workbook, bytes) else workbook

def read_sp500_index_earnings_workbook(...):
    excel = pd.ExcelFile(_excel_source(workbook))
    errors = []
    for sheet_name in excel.sheet_names:
        frame = pd.read_excel(excel, sheet_name=sheet_name)
        try:
            normalized = _normalize_explicit_earnings_sheet(
                frame,
                source_release_date=source_release_date,
                source_ref=source_ref or SP500_INDEX_EARNINGS_URL,
                collected_at=collected_at,
            )
        except ValueError as exc:
            errors.append(f"{sheet_name}: {exc}")
            continue
        if normalized:
            return normalized
    raise ValueError("S&P workbook에서 period, actual/estimate 상태, EPS basis를 명시적으로 확인할 수 없습니다.")
```

- [ ] **Step 5: Run parser tests and verify GREEN**

Run: `.venv/bin/python -m pytest tests/test_sp500_valuation.py -k "index_earnings_reader or normalize_index_earnings" -q`

Expected: PASS.

- [ ] **Step 6: Commit parser contract**

```bash
git add finance/data/sp500_valuation.py tests/test_sp500_valuation.py .aiworkspace/note/finance/tasks/active/overview-economic-cycle-sp500-actual-eps-registration-v1-20260718
git commit -m "S&P 500 공식 EPS workbook 파서 추가"
```

### Task 2: Transactional 저장과 coverage 요약

**Files:**
- Modify: `tests/test_sp500_valuation.py`
- Modify: `finance/data/db/mysql.py`
- Modify: `finance/data/sp500_valuation.py`

**Interfaces:**
- Consumes: Task 1 reader, `workbook: bytes | str | Path`, `source_release_date: str`.
- Produces: `import_and_store_sp500_index_earnings(...) -> dict[str, Any]` with `rows_written`, `actual_quarter_count`, `latest_actual_period_end`, `remaining_quarters`, `release_date`, `source_ref`.
- Produces: `MySQLClient.begin()`, `commit()`, `rollback()`.

- [ ] **Step 1: Write failing importer tests**

Add a success test asserting canonical `source_ref`, begin → UPSERT → coverage query → commit, and `remaining_quarters == max(0, 8 - actual_quarter_count)`. Add a failure test where `executemany` raises and assert `rollback()` and `close()` are called while `commit()` is not.

```python
def test_index_earnings_import_reports_actual_coverage_and_commits(self):
    db = Mock()
    db.query.side_effect = [
        [{"cnt": 0}],
        [{"actual_quarter_count": 6, "latest_actual_period_end": "2026-03-31"}],
    ]
    result = import_and_store_sp500_index_earnings(
        b"xlsx",
        source_release_date="2026-05-15",
        workbook_reader=Mock(return_value=[_actual_eps_row()]),
        db_factory=lambda *_args, **_kwargs: db,
    )
    assert result["actual_quarter_count"] == 6
    assert result["remaining_quarters"] == 2
    assert result["source_ref"] == SP500_INDEX_EARNINGS_URL
    db.begin.assert_called_once()
    db.commit.assert_called_once()
```

- [ ] **Step 2: Run importer tests and verify RED**

Run: `.venv/bin/python -m pytest tests/test_sp500_valuation.py -k "index_earnings_import" -q`

Expected: FAIL because transaction methods and coverage fields are absent.

- [ ] **Step 3: Implement transaction methods and importer summary**

```python
class MySQLClient:
    ...
    def begin(self):
        self.conn.begin()

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()
```

Ensure the schema before `begin()`. Then begin, UPSERT, run the strict actual coverage query, commit, and rollback on any exception. Pass `SP500_INDEX_EARNINGS_URL` to the reader and overwrite every normalized row's `source_ref` with that URL before the UPSERT.

- [ ] **Step 4: Run importer tests and verify GREEN**

Run: `.venv/bin/python -m pytest tests/test_sp500_valuation.py -k "index_earnings_import" -q`

Expected: PASS.

- [ ] **Step 5: Commit transactional import**

```bash
git add finance/data/db/mysql.py finance/data/sp500_valuation.py tests/test_sp500_valuation.py
git commit -m "S&P 500 실제 EPS를 vintage 단위로 저장"
```

### Task 3: Point-in-time actual EPS loader

**Files:**
- Modify: `tests/test_sp500_valuation.py`
- Modify: `finance/loaders/sp500_valuation.py`

**Interfaces:**
- Consumes: `load_sp500_actual_eps_history(quarter_count=8, end_date=None, query_fn=None)`.
- Produces: SQL that filters both `period_end` and `source_release_date` by the same as-of date; default uses `CURRENT_DATE()` for both.

- [ ] **Step 1: Write failing PIT tests**

Capture SQL and params for an explicit `end_date="2026-03-31"` and assert:

```python
assert "source_release_date <= %s" in captured["sql"]
assert captured["params"] == ("2026-03-31", "2026-03-31")
```

Add a default-date test asserting `source_release_date <= CURRENT_DATE()` is present. Keep the existing 7/8 distinct quarter behavior.

- [ ] **Step 2: Run PIT tests and verify RED**

Run: `.venv/bin/python -m pytest tests/test_sp500_valuation.py -k "actual_eps_history" -q`

Expected: FAIL because only `period_end` is bounded.

- [ ] **Step 3: Implement the PIT SQL guard**

```python
if end_date is None:
    end_clause = "AND period_end <= CURRENT_DATE() AND source_release_date <= CURRENT_DATE()"
    params = ()
else:
    end_clause = "AND period_end <= %s AND source_release_date <= %s"
    as_of = str(end_date)[:10]
    params = (as_of, as_of)
```

- [ ] **Step 4: Run loader tests and verify GREEN**

Run: `.venv/bin/python -m pytest tests/test_sp500_valuation.py -k "actual_eps_history or ttm_loader" -q`

Expected: PASS.

- [ ] **Step 5: Commit PIT loader**

```bash
git add finance/loaders/sp500_valuation.py tests/test_sp500_valuation.py
git commit -m "실제 EPS 조회에 발표 vintage 기준일 적용"
```

### Task 4: Ingestion job/action 계약

**Files:**
- Modify: `app/jobs/ingestion_jobs.py`
- Modify: `app/web/ingestion/registry.py`
- Modify: `app/web/ingestion/guides.py`
- Modify: `app/web/ingestion/dispatcher.py`
- Modify: `tests/test_sp500_valuation.py`
- Modify: `tests/test_ingestion_guides.py`

**Interfaces:**
- Produces: `run_import_sp500_index_earnings_xlsx(*, workbook_content: bytes, source_release_date: str, source_name: str | None = None) -> JobResult`.
- Produces action: `import_sp500_index_earnings_xlsx` in registry and dispatcher.

- [ ] **Step 1: Write failing job and registry tests**

Patch the canonical importer to return 8 actual quarters and assert the job result exposes a success message containing `8/8`, plus the coverage details. Assert the action registry has mode `manual_official_file_import`, target `finance_meta.sp500_index_earnings`, and dispatcher calls the wrapper.

- [ ] **Step 2: Run action tests and verify RED**

Run: `.venv/bin/python -m pytest tests/test_sp500_valuation.py tests/test_ingestion_guides.py -k "sp500_index_earnings" -q`

Expected: FAIL because the job/action does not exist.

- [ ] **Step 3: Implement the job wrapper and action metadata**

The job wrapper calls only the canonical importer. Its user message is one of:

```python
message = (
    f"S&P 500 실제 EPS {count}/8개 분기를 확보했습니다. 경제 사이클의 실제 TTM EPS를 계산할 수 있습니다."
    if remaining == 0
    else f"S&P 500 실제 EPS {count}/8개 분기를 확보했습니다. 계산까지 {remaining}개 분기가 더 필요합니다."
)
```

Do not include uploaded bytes in `details`, run metadata, or history. `source_name` may be used only in the immediate success copy.

- [ ] **Step 4: Run action tests and verify GREEN**

Run: `.venv/bin/python -m pytest tests/test_sp500_valuation.py tests/test_ingestion_guides.py -k "sp500_index_earnings" -q`

Expected: PASS.

- [ ] **Step 5: Commit ingestion action**

```bash
git add app/jobs/ingestion_jobs.py app/web/ingestion/registry.py app/web/ingestion/guides.py app/web/ingestion/dispatcher.py tests/test_sp500_valuation.py tests/test_ingestion_guides.py
git commit -m "S&P 500 실제 EPS 등록 job 연결"
```

### Task 5: 사용자 업로드 UI

**Files:**
- Modify: `app/web/ingestion/sections.py`
- Modify: `tests/test_ingestion_sections.py`

**Interfaces:**
- Consumes action `import_sp500_index_earnings_xlsx`.
- Produces a collapsed expander `S&P 500 실제 EPS 등록` with official source link, XLSX uploader, release-date input, disabled-state button, and meaning-focused completion copy.

- [ ] **Step 1: Write failing source-contract test**

Assert the section source contains:

```python
assert '"S&P 500 실제 EPS 등록"' in source
assert 'type=["xlsx"]' in source
assert '"import_sp500_index_earnings_xlsx"' in source
assert '"https://www.spglobal.com/spdji/en/indices/equity/sp-500/"' in source
assert 'disabled=_has_running_job() or sp500_eps_file is None' in source
```

- [ ] **Step 2: Run UI contract test and verify RED**

Run: `.venv/bin/python -m pytest tests/test_ingestion_sections.py -k "sp500_actual_eps" -q`

Expected: FAIL because the expander is absent.

- [ ] **Step 3: Implement the upload flow**

Place the expander in `render_operational_section()` before the market-event calendar. Explain that the user must download `Index Earnings` from the official S&P 500 page, then upload the `.xlsx`. Use `st.date_input("자료 발표일", value=date.today())`, pass `sp500_eps_file.getvalue()` and `str(release_date)`, and schedule the action without persisting a temporary path.

- [ ] **Step 4: Run UI contract tests and verify GREEN**

Run: `.venv/bin/python -m pytest tests/test_ingestion_sections.py tests/test_ingestion_guides.py -k "sp500_actual_eps or sp500_index_earnings" -q`

Expected: PASS.

- [ ] **Step 5: Commit UI**

```bash
git add app/web/ingestion/sections.py tests/test_ingestion_sections.py
git commit -m "Ingestion에 S&P 500 실제 EPS 등록 화면 추가"
```

### Task 6: 문서 정렬, 실제 등록, 회귀 및 Browser QA

**Files:**
- Modify: `.aiworkspace/note/finance/docs/data/README.md`
- Modify: `.aiworkspace/note/finance/docs/data/DATA_FLOW_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/data/TABLE_SEMANTICS.md`
- Modify: `.aiworkspace/note/finance/docs/architecture/DATA_DB_PIPELINE_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-economic-cycle-sp500-actual-eps-registration-v1-20260718/{STATUS.md,NOTES.md,RUNS.md,RISKS.md}`

**Interfaces:**
- Consumes: Tasks 1–5.
- Produces: durable source/flow/PIT semantics and verified user workflow.

- [ ] **Step 1: Sync durable docs**

Document the manual official-file registration path, strict 8-quarter gate, canonical URL, release-vintage PIT rule, Shiller exclusion, and source download restriction. Replace the existing misleading `four distinct completed` README wording with the correct distinction: four quarters are enough for a current TTM value, but eight are required for current/prior TTM YoY in Economic Cycle.

- [ ] **Step 2: Run focused and regression tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_sp500_valuation.py tests/test_ingestion_guides.py tests/test_ingestion_sections.py -q
.venv/bin/python -m pytest tests/test_economic_cycle_asset_pathways.py tests/test_overview_economic_cycle.py -q
.venv/bin/python -m py_compile finance/data/sp500_valuation.py finance/loaders/sp500_valuation.py app/jobs/ingestion_jobs.py app/web/ingestion/dispatcher.py app/web/ingestion/sections.py
git diff --check
```

Expected: all tests PASS, py_compile exits 0, diff check has no output.

- [ ] **Step 3: Register an official workbook when available**

If the user-downloaded official workbook exists locally, upload it through the new UI and confirm `actual_quarter_count >= 8`, current/prior TTM values, and latest release date. If no official workbook exists, record the exact remaining external input in `RISKS.md`; keep the code complete but do not claim that the database has been populated.

- [ ] **Step 4: Run Browser QA**

Start or reuse the local Streamlit app, open `Workspace > Ingestion`, expand `S&P 500 실제 EPS 등록`, and verify official-source guidance, XLSX-only upload, release-date input, disabled button before file selection, and usable Korean copy. Save one screenshot under `/tmp/codex-browser-qa/sp500-actual-eps-registration.png`; do not commit it.

- [ ] **Step 5: Final status and documentation commit**

Update task status with completed tests and the actual-data population state. Keep root handoff logs to 3–5 lines. Then commit:

```bash
git add .aiworkspace/note/finance/docs .aiworkspace/note/finance/tasks/active/overview-economic-cycle-sp500-actual-eps-registration-v1-20260718 .aiworkspace/note/finance/WORK_PROGRESS.md .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git commit -m "S&P 500 실제 EPS 등록 문서와 검증 정리"
```

## Self-Review Result

- Spec coverage: official upload, explicit parser, canonical source URL, release vintage, transactional rollback, 8-quarter gate, PIT loader, user-facing coverage, Shiller exclusion, Browser QA, durable docs are each mapped to Tasks 1–6.
- Placeholder scan: no implementation placeholder remains; the only conditional step is the external official workbook population, which is explicitly separated from code completion and recorded as a data availability risk when absent.
- Type consistency: the workbook type, importer result fields, action name, job wrapper signature, and loader as-of parameters match across tasks.

