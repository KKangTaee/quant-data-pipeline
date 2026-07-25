# Overview Sentiment AAII Canonical Dedup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** AAII 공식 XLS의 주간 날짜를 canonical 기준으로 유지해 HTML/XLS 동일 주차 중복이 Sentiment 그래프에 재발하지 않게 한다.

**Architecture:** 기존 source-isolated capture 트랜잭션 안에서 완전한 AAII XLS capture에만 canonical date-window reconciliation을 적용한다. 실제 기존 데이터는 이미 존재하는 full-workbook atomic backfill을 실행해 정리하며 immutable capture tables는 건드리지 않는다.

**Tech Stack:** Python 3, unittest, pandas, MySQL, Streamlit service payload

## Global Constraints

- `market_sentiment_observation_snapshot`과 collection batch는 보존한다.
- 공식 XLS `Reported Date`를 canonical observation date로 사용한다.
- HTML fallback, CNN, 차트 표현, AAII 판정 기준은 변경하지 않는다.
- 실제 DB 정리는 fetch-before-delete와 transaction rollback 경계를 유지한다.

---

### Task 1: AAII XLS Canonical Window Reconciliation

**Files:**
- Modify: `tests/test_sentiment_pit.py`
- Modify: `finance/data/sentiment_store.py`

**Interfaces:**
- Consumes: `persist_market_sentiment_source_capture(db, ..., rows)`
- Produces: `_reconcile_aaii_canonical_window(db, rows) -> dict[str, Any] | None`

- [ ] **Step 1: Write the failing XLS reconciliation test**

`tests/test_sentiment_pit.py`의 `FakeTransactionDb`에 canonical-window delete event와 params capture를 추가하고, 두 XLS 주차 capture가 batch/snapshot 뒤 canonical UPSERT 전에 `start_date`, `end_date`, 두 keep date를 전달해 window cleanup을 실행한다고 단언한다.

- [ ] **Step 2: Run the focused test and verify RED**

Run:

```bash
.venv/bin/python -m unittest tests.test_sentiment_pit.SentimentPitPersistenceTests.test_aaii_xls_capture_reconciles_canonical_window_before_upsert -v
```

Expected: 현재 구현에는 reconciliation event가 없어 assertion failure.

- [ ] **Step 3: Implement minimal canonical-window reconciliation**

`finance/data/sentiment_store.py`에 다음 동작을 추가한다.

```python
def _reconcile_aaii_canonical_window(
    db: MySQLClient,
    rows: list[dict[str, Any]],
) -> dict[str, Any] | None:
    # Only aligned, complete AAII XLS rows qualify.
    # Delete canonical AAII dates between min/max except incoming dates.
    # Return start/end/date_count for logging/tests; otherwise None.
```

`persist_market_sentiment_source_capture()`는 `source == "aaii_sentiment_survey"`일 때 snapshot insert 후, canonical UPSERT 전에 이 함수를 호출한다.

- [ ] **Step 4: Run focused test and verify GREEN**

Run:

```bash
.venv/bin/python -m unittest tests.test_sentiment_pit.SentimentPitPersistenceTests.test_aaii_xls_capture_reconciles_canonical_window_before_upsert -v
```

Expected: PASS.

- [ ] **Step 5: Add negative and rollback coverage**

HTML rows에는 reconciliation event가 없고, reconciliation delete 실패 시 transaction이 rollback되며 canonical UPSERT가 실행되지 않는 테스트를 추가한다.

- [ ] **Step 6: Run complete sentiment PIT suite**

Run:

```bash
.venv/bin/python -m unittest tests.test_sentiment_pit -v
```

Expected: all tests PASS.

### Task 2: Existing Canonical Data Cleanup

**Files:**
- Update: `.aiworkspace/note/finance/tasks/active/overview-sentiment-aaii-canonical-dedup-v1-20260725/RUNS.md`
- Update: `.aiworkspace/note/finance/tasks/active/overview-sentiment-aaii-canonical-dedup-v1-20260725/NOTES.md`

**Interfaces:**
- Consumes: `finance.data.sentiment.backfill_aaii_sentiment_history()`
- Produces: official XLS-backed `finance_meta.macro_series_observation` AAII canonical history

- [ ] **Step 1: Capture exact pre-cleanup duplicate rows**

Read only `AAII_BULL_BEAR_SPREAD` rows from 2026-06-15 through 2026-07-17 and record HTML/XLS adjacent pairs.

- [ ] **Step 2: Run atomic official workbook backfill**

Run:

```bash
.venv/bin/python -c "from finance.data.sentiment import backfill_aaii_sentiment_history; print(backfill_aaii_sentiment_history())"
```

Expected: four aligned series, full official workbook history, transaction commit.

- [ ] **Step 3: Verify canonical and immutable boundaries**

Verify:

- recent canonical AAII dates have exact 7-day cadence
- `2026-06-17`, `2026-07-08`, `2026-07-15` legacy HTML canonical rows are absent
- `2026-06-18`, `2026-07-09`, `2026-07-16` official XLS rows remain
- immutable snapshot and batch row counts are unchanged

- [ ] **Step 4: Verify downstream React payload**

Build `build_market_sentiment_snapshot()` and `build_sentiment_react_workbench_payload()` and confirm recent AAII spread points have one point per official week.

### Task 3: Documentation, Verification, and Commit

**Files:**
- Modify: `.aiworkspace/note/finance/docs/data/README.md`
- Modify: `.aiworkspace/note/finance/docs/architecture/DATA_DB_PIPELINE_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/INDEX.md`
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-sentiment-aaii-canonical-dedup-v1-20260725/*`

**Interfaces:**
- Consumes: verified implementation and DB cleanup evidence
- Produces: durable canonical refresh semantics and task handoff

- [ ] **Step 1: Sync durable docs**

Document that official AAII XLS capture owns the canonical recent date window, while immutable captures remain append-only.

- [ ] **Step 2: Run verification**

Run:

```bash
.venv/bin/python -m unittest tests.test_sentiment_pit -v
.venv/bin/python -m py_compile finance/data/sentiment.py finance/data/sentiment_store.py finance/loaders/sentiment.py
git diff --check
git status --short
```

- [ ] **Step 3: Review scoped diff**

Confirm no registry, saved setup, run history, QA image, or unrelated dirty file is staged.

- [ ] **Step 4: Commit coherent implementation**

Stage only the task’s code, tests, specs, task docs, and durable docs, then commit with a Korean message.

