# Overview Sentiment Long History And PIT Capture V2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Preserve immutable CNN·AAII collection-time observations, provide an explicit UTC as-known loader, automate daily capture, and let Overview users switch both history charts between 6M, 1Y, and all available canonical history.

**Architecture:** Keep `macro_series_observation` as the current/latest chart store and add source-batch plus immutable normalized snapshot tables. A focused persistence module owns schema sync and source-level transactions; `finance.data.sentiment` owns fetch orchestration, and a dedicated loader answers PIT cutoffs. The service keeps interpretation on a fixed 180-day window while sending full canonical chart history and compact coverage evidence to the existing React V2 workbench.

**Tech Stack:** Python 3.12, pandas, PyMySQL/MySQL 8 window functions, `unittest`, React 18, TypeScript 5, Vite 6, Streamlit custom component, CSS, in-app Browser QA.

## Global Constraints

- Use `수집 당시 기록` in user-facing Korean copy; do not expose `원장` as product terminology.
- `known_at` means the UTC time when this application observed the response, not the provider's exact publication time.
- Do not fabricate capture history before the first successful new source batch.
- Keep `finance_meta.macro_series_observation` as the canonical current/latest chart store.
- Immutable rows from different batches remain stored even when their values are identical.
- CNN and AAII are independent transaction units; one source failure cannot roll back the other source.
- A source transaction must never commit immutable rows without matching canonical writes, or canonical writes without matching immutable rows.
- Keep the existing `collect_market_sentiment` job name, refresh/reload actions, primary `rows_written` semantics, and `sentiment_react_workbench_v2` schema version.
- Keep current interpretation and recent-range calculations on exactly 180 calendar days.
- The History period control is shared by CNN and AAII, defaults to `6M`, and offers `6M`, `1Y`, and `전체`.
- Keep the approved two-row chart layout, AAII response/spread switch, straight polylines, and edge-safe tooltips.
- Do not add raw provider-payload storage, a run-centric diagnostics panel, a new sentiment provider, a synthetic score, a probability, or a trading signal.
- Keep both 1W and 1M outlook cards `UNAVAILABLE` with empty probability arrays.
- Use `finance-db-pipeline` for Tasks 1-5 and `finance-doc-sync` during Task 8 closeout.
- Do not stage generated Browser screenshots, run-history JSONL, unrelated research folders, or existing untracked artifacts.

## File Structure

- `finance/data/db/schema.py`: two new table DDL contracts.
- `finance/data/sentiment_store.py`: schema sync, normalized-row deduplication, batch/snapshot SQL, canonical UPSERT, and source transaction.
- `finance/data/sentiment.py`: provider fetch orchestration, source completeness, UUIDs, and source isolation.
- `finance/loaders/sentiment.py`: canonical reads plus as-known and capture-summary reads.
- `app/jobs/ingestion_jobs.py`: compatible public job details.
- `app/jobs/overview_automation.py`: 24-hour automatic capture spec.
- `app/web/ingestion/registry.py`: all three write targets.
- `app/services/overview/sentiment.py`: full chart history, 180-day interpretation frame, coverage evidence.
- `app/web/overview/sentiment_helpers.py`: JSON-safe coverage payload.
- `app/web/streamlit_components/sentiment_workbench/src/SentimentWorkbench.tsx`: V2 payload types.
- `app/web/streamlit_components/sentiment_workbench/src/SentimentHistorySection.tsx`: shared period state and filtering.
- `app/web/streamlit_components/sentiment_workbench/src/style.css`: period/coverage presentation.
- `tests/test_sentiment_pit.py`: focused DB, persistence, collector, and loader tests.
- `tests/test_service_contracts.py`: job, automation, service/payload, and React source contracts.
- `.aiworkspace/note/finance/docs/runbooks/OVERVIEW_MARKET_INTELLIGENCE.md`: daily scheduling and recovery.

---

### Task 1: Add Source-Batch And Immutable Snapshot Schemas

**Files:**
- Modify: `finance/data/db/schema.py:833-899`
- Create: `finance/data/sentiment_store.py`
- Create: `tests/test_sentiment_pit.py`

**Interfaces:**
- Consumes: `PROVIDER_SCHEMAS`, `sync_table_schema`, `MySQLClient`.
- Produces: `MARKET_SENTIMENT_BATCH_TABLE`, `MARKET_SENTIMENT_SNAPSHOT_TABLE`, `MARKET_SENTIMENT_TARGET_TABLES`, `ensure_market_sentiment_schema(db) -> None`.

- [ ] **Step 1: Write the failing schema contract**

Create `tests/test_sentiment_pit.py`:

```python
from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch


class FakeSchemaDb:
    def __init__(self) -> None:
        self.used: list[str] = []
        self.executed: list[str] = []

    def use_db(self, name: str) -> None:
        self.used.append(name)

    def execute(self, sql: str, params=None) -> None:
        del params
        self.executed.append(sql)


class SentimentPitSchemaTests(unittest.TestCase):
    def test_schema_and_sync_contracts(self) -> None:
        from finance.data.db.schema import PROVIDER_SCHEMAS
        from finance.data.sentiment_store import (
            MARKET_SENTIMENT_TARGET_TABLES,
            ensure_market_sentiment_schema,
        )

        batch = PROVIDER_SCHEMAS["market_sentiment_collection_batch"]
        snapshot = PROVIDER_SCHEMAS["market_sentiment_observation_snapshot"]
        self.assertIn("batch_id CHAR(36) PRIMARY KEY", batch)
        self.assertIn("observed_at DATETIME(6) NULL", batch)
        self.assertIn("uk_sentiment_snapshot_batch_series_date_source", snapshot)
        self.assertIn("ix_sentiment_snapshot_as_known", snapshot)

        db = FakeSchemaDb()
        with patch("finance.data.sentiment_store.sync_table_schema") as sync:
            ensure_market_sentiment_schema(db)
        self.assertEqual(db.used, ["finance_meta"])
        self.assertEqual(len(MARKET_SENTIMENT_TARGET_TABLES), 3)
        self.assertEqual(sync.call_count, 3)
```

- [ ] **Step 2: Run the test and confirm RED**

```bash
.venv/bin/python -m unittest discover -s tests -p 'test_sentiment_pit.py' -v
```

Expected: `ERROR` because the new schemas and module do not exist.

- [ ] **Step 3: Add the exact DDL**

Add to `PROVIDER_SCHEMAS`:

```python
"market_sentiment_collection_batch": """
    CREATE TABLE IF NOT EXISTS market_sentiment_collection_batch (
      batch_id CHAR(36) PRIMARY KEY,
      collection_id CHAR(36) NOT NULL,
      source VARCHAR(64) NOT NULL,
      source_ref VARCHAR(1024) NULL,
      schema_version VARCHAR(64) NOT NULL,
      status ENUM('success','partial','missing','error') NOT NULL,
      requested_at DATETIME(6) NOT NULL,
      observed_at DATETIME(6) NULL,
      completed_at DATETIME(6) NOT NULL,
      observation_start DATE NULL,
      observation_end DATE NULL,
      row_count INT NOT NULL DEFAULT 0,
      coverage_json JSON NULL,
      error_msg TEXT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      KEY ix_sentiment_batch_collection (collection_id),
      KEY ix_sentiment_batch_source_observed (source, observed_at),
      KEY ix_sentiment_batch_status_completed (status, completed_at)
    );
""",
"market_sentiment_observation_snapshot": """
    CREATE TABLE IF NOT EXISTS market_sentiment_observation_snapshot (
      id BIGINT AUTO_INCREMENT PRIMARY KEY,
      batch_id CHAR(36) NOT NULL,
      collection_id CHAR(36) NOT NULL,
      series_id VARCHAR(64) NOT NULL,
      observation_date DATE NOT NULL,
      source VARCHAR(64) NOT NULL,
      source_type ENUM('official','database_bridge','computed_proxy') NOT NULL DEFAULT 'official',
      source_mode VARCHAR(32) NULL,
      source_ref VARCHAR(1024) NULL,
      series_name VARCHAR(255) NULL,
      category VARCHAR(64) NOT NULL,
      frequency VARCHAR(32) NULL,
      units VARCHAR(64) NULL,
      value DOUBLE NULL,
      release_lag_days INT NULL,
      coverage_status ENUM('actual','partial','bridge','proxy','missing','error') NOT NULL DEFAULT 'actual',
      missing_fields_json JSON NULL,
      observed_at DATETIME(6) NOT NULL,
      error_msg TEXT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      UNIQUE KEY uk_sentiment_snapshot_batch_series_date_source
        (batch_id, series_id, observation_date, source),
      KEY ix_sentiment_snapshot_batch (batch_id),
      KEY ix_sentiment_snapshot_as_known (series_id, source, observed_at, observation_date),
      KEY ix_sentiment_snapshot_collection (collection_id)
    );
""",
```

- [ ] **Step 4: Create schema ownership**

Create `finance/data/sentiment_store.py`:

```python
from __future__ import annotations

from finance.data.db.mysql import MySQLClient
from finance.data.db.schema import PROVIDER_SCHEMAS, sync_table_schema

DB_META = "finance_meta"
MACRO_TABLE = "macro_series_observation"
MARKET_SENTIMENT_BATCH_TABLE = "market_sentiment_collection_batch"
MARKET_SENTIMENT_SNAPSHOT_TABLE = "market_sentiment_observation_snapshot"
MARKET_SENTIMENT_TARGET_TABLES = (
    MACRO_TABLE,
    MARKET_SENTIMENT_BATCH_TABLE,
    MARKET_SENTIMENT_SNAPSHOT_TABLE,
)
SENTIMENT_CAPTURE_SCHEMA_VERSION = "market_sentiment_capture_v1"


def ensure_market_sentiment_schema(db: MySQLClient) -> None:
    """Create or additively sync the three sentiment persistence tables."""
    db.use_db(DB_META)
    for table_name in MARKET_SENTIMENT_TARGET_TABLES:
        sql = PROVIDER_SCHEMAS[table_name]
        db.execute(sql)
        sync_table_schema(db, table_name, sql, DB_META)
```

- [ ] **Step 5: Confirm GREEN and commit**

Run the Step 2 command. Expected: `OK`, 1 test passed.

```bash
git add finance/data/db/schema.py finance/data/sentiment_store.py tests/test_sentiment_pit.py
git commit -m "시장 심리 PIT 저장 스키마 추가"
```

---

### Task 2: Implement Idempotent Source Transactions

**Files:**
- Modify: `finance/data/sentiment_store.py`
- Modify: `tests/test_sentiment_pit.py`

**Interfaces:**
- Produces: `deduplicate_sentiment_rows(rows)`, `persist_market_sentiment_source_capture(...)`, `record_market_sentiment_source_failure(...)`.
- Successful persistence returns `batch_id`, `status`, `snapshot_rows_written`, and `canonical_rows_written`.

- [ ] **Step 1: Write failing transaction tests**

Append a fake DB and these assertions:

```python
class FakeTransactionDb(FakeSchemaDb):
    def __init__(self, fail_snapshot: bool = False) -> None:
        super().__init__()
        self.fail_snapshot = fail_snapshot
        self.events: list[str] = []

    def begin(self) -> None: self.events.append("begin")
    def commit(self) -> None: self.events.append("commit")
    def rollback(self) -> None: self.events.append("rollback")
    def executemany(self, sql: str, rows: list[dict]) -> None:
        del rows
        if self.fail_snapshot and "observation_snapshot" in sql:
            raise RuntimeError("snapshot write failed")
        self.events.append("snapshot" if "observation_snapshot" in sql else "canonical")

    def execute(self, sql: str, params=None) -> None:
        del sql
        if params is not None: self.events.append("batch")


def sentiment_row(value: float) -> dict:
    return {
        "series_id": "CNN_FEAR_GREED", "observation_date": "2026-07-17",
        "source": "cnn_fear_greed", "source_type": "official",
        "source_mode": "json", "source_ref": "https://www.cnn.com/markets/fear-and-greed",
        "series_name": "CNN Fear & Greed Index", "category": "sentiment_index",
        "frequency": "daily", "units": "score_0_100", "value": value,
        "release_lag_days": None, "coverage_status": "actual",
        "missing_fields_json": '{"rating":"fear"}',
        "collected_at": "2026-07-20 01:00:00", "error_msg": None,
    }


class SentimentPitPersistenceTests(unittest.TestCase):
    def test_deduplication_keeps_last_value(self) -> None:
        from finance.data.sentiment_store import deduplicate_sentiment_rows
        rows = deduplicate_sentiment_rows([sentiment_row(37.0), sentiment_row(37.1)])
        self.assertEqual([row["value"] for row in rows], [37.1])

    def test_success_commits_snapshot_and_canonical_together(self) -> None:
        from finance.data.sentiment_store import persist_market_sentiment_source_capture
        db = FakeTransactionDb()
        result = persist_market_sentiment_source_capture(
            db, collection_id="c", batch_id="b", source="cnn_fear_greed",
            source_ref="cnn", requested_at="2026-07-20 00:59:59.000000",
            observed_at="2026-07-20 01:00:00.000000",
            completed_at="2026-07-20 01:00:01.000000", status="success",
            coverage={"expected": 8, "observed": 8, "missing_series": []},
            rows=[sentiment_row(37.1)],
        )
        self.assertEqual(db.events, ["begin", "batch", "snapshot", "canonical", "commit"])
        self.assertEqual(result["snapshot_rows_written"], 1)

    def test_snapshot_failure_rolls_back_before_canonical(self) -> None:
        from finance.data.sentiment_store import persist_market_sentiment_source_capture
        db = FakeTransactionDb(fail_snapshot=True)
        with self.assertRaisesRegex(RuntimeError, "snapshot write failed"):
            persist_market_sentiment_source_capture(
                db, collection_id="c", batch_id="b", source="cnn_fear_greed",
                source_ref="cnn", requested_at="2026-07-20 00:59:59.000000",
                observed_at="2026-07-20 01:00:00.000000",
                completed_at="2026-07-20 01:00:01.000000", status="success",
                coverage={}, rows=[sentiment_row(37.1)],
            )
        self.assertEqual(db.events, ["begin", "batch", "rollback"])
```

- [ ] **Step 2: Run and confirm RED**

Run Task 1 Step 2. Expected: `ERROR` for missing persistence functions.

- [ ] **Step 3: Add deterministic parameters and writers**

Add imports `json`, `Any`, and `Literal`, then implement:

```python
CaptureStatus = Literal["success", "partial", "missing", "error"]


def deduplicate_sentiment_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in rows:
        key = (str(row.get("series_id") or "").upper(),
               str(row.get("observation_date") or ""), str(row.get("source") or ""))
        if all(key): by_key[key] = dict(row)
    return [by_key[key] for key in sorted(by_key)]


def _batch_params(**values: Any) -> dict[str, Any]:
    rows = values.pop("rows")
    coverage = values.pop("coverage")
    error_msg = values.pop("error_msg", None)
    dates = sorted(str(row["observation_date"]) for row in rows if row.get("observation_date"))
    return {
        **values,
        "schema_version": SENTIMENT_CAPTURE_SCHEMA_VERSION,
        "observation_start": dates[0] if dates else None,
        "observation_end": dates[-1] if dates else None,
        "row_count": len(rows),
        "coverage_json": json.dumps(coverage, ensure_ascii=False, sort_keys=True),
        "error_msg": str(error_msg or "")[:500] or None,
    }


def _insert_batch(db: MySQLClient, params: dict[str, Any]) -> None:
    db.execute(f"""
      INSERT INTO {MARKET_SENTIMENT_BATCH_TABLE} (
        batch_id, collection_id, source, source_ref, schema_version, status,
        requested_at, observed_at, completed_at, observation_start,
        observation_end, row_count, coverage_json, error_msg
      ) VALUES (
        %(batch_id)s, %(collection_id)s, %(source)s, %(source_ref)s,
        %(schema_version)s, %(status)s, %(requested_at)s, %(observed_at)s,
        %(completed_at)s, %(observation_start)s, %(observation_end)s,
        %(row_count)s, %(coverage_json)s, %(error_msg)s
      ) ON DUPLICATE KEY UPDATE batch_id = VALUES(batch_id)
    """, params)


def _insert_snapshot_rows(db: MySQLClient, batch_id: str, collection_id: str,
                          observed_at: str, rows: list[dict[str, Any]]) -> None:
    params = [{**row, "batch_id": batch_id, "collection_id": collection_id,
               "observed_at": observed_at} for row in rows]
    db.executemany(f"""
      INSERT INTO {MARKET_SENTIMENT_SNAPSHOT_TABLE} (
        batch_id, collection_id, series_id, observation_date, source,
        source_type, source_mode, source_ref, series_name, category,
        frequency, units, value, release_lag_days, coverage_status,
        missing_fields_json, observed_at, error_msg
      ) VALUES (
        %(batch_id)s, %(collection_id)s, %(series_id)s, %(observation_date)s,
        %(source)s, %(source_type)s, %(source_mode)s, %(source_ref)s,
        %(series_name)s, %(category)s, %(frequency)s, %(units)s, %(value)s,
        %(release_lag_days)s, %(coverage_status)s, %(missing_fields_json)s,
        %(observed_at)s, %(error_msg)s
      ) ON DUPLICATE KEY UPDATE id = id
    """, params)


def _upsert_canonical_rows(db: MySQLClient, rows: list[dict[str, Any]]) -> None:
    db.executemany(f"""
      INSERT INTO {MACRO_TABLE} (
        series_id, observation_date, source, source_type, source_mode,
        source_ref, series_name, category, frequency, units, value,
        release_lag_days, coverage_status, missing_fields_json,
        collected_at, error_msg
      ) VALUES (
        %(series_id)s, %(observation_date)s, %(source)s, %(source_type)s,
        %(source_mode)s, %(source_ref)s, %(series_name)s, %(category)s,
        %(frequency)s, %(units)s, %(value)s, %(release_lag_days)s,
        %(coverage_status)s, %(missing_fields_json)s, %(collected_at)s,
        %(error_msg)s
      ) ON DUPLICATE KEY UPDATE
        source_type=VALUES(source_type), source_mode=VALUES(source_mode),
        source_ref=VALUES(source_ref), series_name=VALUES(series_name),
        category=VALUES(category), frequency=VALUES(frequency),
        units=VALUES(units), value=VALUES(value),
        release_lag_days=VALUES(release_lag_days),
        coverage_status=VALUES(coverage_status),
        missing_fields_json=VALUES(missing_fields_json),
        collected_at=VALUES(collected_at), error_msg=VALUES(error_msg)
    """, rows)
```

- [ ] **Step 4: Add the atomic public functions**

```python
def persist_market_sentiment_source_capture(
    db: MySQLClient, *, collection_id: str, batch_id: str, source: str,
    source_ref: str | None, requested_at: str, observed_at: str,
    completed_at: str, status: Literal["success", "partial"],
    coverage: dict[str, Any], rows: list[dict[str, Any]],
) -> dict[str, Any]:
    normalized = deduplicate_sentiment_rows(rows)
    batch = _batch_params(
        collection_id=collection_id, batch_id=batch_id, source=source,
        source_ref=source_ref, requested_at=requested_at, observed_at=observed_at,
        completed_at=completed_at, status=status, coverage=coverage,
        rows=normalized, error_msg=None,
    )
    db.begin()
    try:
        _insert_batch(db, batch)
        _insert_snapshot_rows(db, batch_id, collection_id, observed_at, normalized)
        _upsert_canonical_rows(db, normalized)
        db.commit()
    except Exception:
        db.rollback()
        raise
    return {"batch_id": batch_id, "status": status,
            "snapshot_rows_written": len(normalized),
            "canonical_rows_written": len(normalized)}


def record_market_sentiment_source_failure(
    db: MySQLClient, *, collection_id: str, batch_id: str, source: str,
    source_ref: str | None, requested_at: str, completed_at: str,
    status: Literal["missing", "error"], error_msg: str,
) -> None:
    _insert_batch(db, _batch_params(
        collection_id=collection_id, batch_id=batch_id, source=source,
        source_ref=source_ref, requested_at=requested_at, observed_at=None,
        completed_at=completed_at, status=status, coverage={}, rows=[],
        error_msg=error_msg,
    ))
```

- [ ] **Step 5: Confirm GREEN and commit**

Run Task 1 Step 2. Expected: 4 tests pass.

```bash
git add finance/data/sentiment_store.py tests/test_sentiment_pit.py
git commit -m "시장 심리 수집 당시 기록 트랜잭션 구현"
```

---

### Task 3: Move CNN And AAII Collection To The Dual Store

**Files:**
- Modify: `finance/data/sentiment.py:1-497`
- Modify: `tests/test_sentiment_pit.py`

**Interfaces:**
- Consumes: Task 2 persistence, existing parsers/fetchers.
- Produces: source-isolated collection summary with `collection_id`, `batch_ids`, `snapshot_rows_stored`, `canonical_rows_stored`, and compatibility `stored`.

- [ ] **Step 1: Write failing source-isolation tests**

Use patched fetch/persist functions and assert:

```python
class SentimentPitCollectorTests(unittest.TestCase):
    def test_cnn_failure_does_not_block_aaii(self) -> None:
        from finance.data import sentiment
        aaii = {**sentiment_row(44.9), "series_id": "AAII_BULLISH",
                "source": "aaii_sentiment_survey"}
        persisted: list[str] = []
        failures: list[str] = []
        db = MagicMock()
        with (
            patch.object(sentiment, "fetch_cnn_fear_greed_rows", side_effect=RuntimeError("CNN blocked")),
            patch.object(sentiment, "fetch_aaii_sentiment_rows", return_value=[aaii]),
            patch.object(sentiment, "MySQLClient", return_value=db),
            patch.object(sentiment, "ensure_market_sentiment_schema"),
            patch.object(sentiment, "persist_market_sentiment_source_capture",
                         side_effect=lambda _db, **kw: persisted.append(kw["source"]) or {
                             "batch_id": kw["batch_id"], "status": kw["status"],
                             "snapshot_rows_written": 1, "canonical_rows_written": 1}),
            patch.object(sentiment, "record_market_sentiment_source_failure",
                         side_effect=lambda _db, **kw: failures.append(kw["source"])),
        ):
            result = sentiment.collect_and_store_market_sentiment()
        self.assertEqual(persisted, ["aaii_sentiment_survey"])
        self.assertEqual(failures, ["cnn_fear_greed"])
        self.assertEqual(result["stored"], 1)
```

Add this success case:

```python
    def test_success_uses_distinct_batches_and_source_observed_times(self) -> None:
        from finance.data import sentiment
        cnn = sentiment_row(37.1)
        aaii = {**sentiment_row(44.9), "series_id": "AAII_BULLISH",
                "source": "aaii_sentiment_survey",
                "collected_at": "2026-07-20 01:05:00"}
        captures: list[dict] = []
        db = MagicMock()
        with (
            patch.object(sentiment, "fetch_cnn_fear_greed_rows", return_value=[cnn]),
            patch.object(sentiment, "fetch_aaii_sentiment_rows", return_value=[aaii]),
            patch.object(sentiment, "MySQLClient", return_value=db),
            patch.object(sentiment, "ensure_market_sentiment_schema"),
            patch.object(sentiment, "persist_market_sentiment_source_capture",
                         side_effect=lambda _db, **kw: captures.append(kw) or {
                             "batch_id": kw["batch_id"], "status": kw["status"],
                             "snapshot_rows_written": 1, "canonical_rows_written": 1}),
        ):
            result = sentiment.collect_and_store_market_sentiment()
        self.assertEqual(len({row["batch_id"] for row in captures}), 2)
        self.assertEqual([row["observed_at"] for row in captures],
                         [cnn["collected_at"], aaii["collected_at"]])
        self.assertEqual(result["snapshot_rows_stored"], 2)
        self.assertEqual(result["stored"], 2)
```

- [ ] **Step 2: Run and confirm RED**

Run Task 1 Step 2. Expected: collection still performs one aggregate canonical UPSERT.

- [ ] **Step 3: Add completeness and one-timestamp contracts**

After source maps add:

```python
EXPECTED_SENTIMENT_SERIES = {
    "cnn_fear_greed": {"CNN_FEAR_GREED", *[value[0] for value in CNN_COMPONENTS.values()]},
    "aaii_sentiment_survey": {value[0] for value in AAII_SERIES.values()},
}


def _source_coverage(source: str, rows: list[dict[str, Any]]) -> tuple[str, dict[str, Any]]:
    expected = EXPECTED_SENTIMENT_SERIES[source]
    observed = {str(row.get("series_id") or "").upper() for row in rows}
    missing = sorted(expected - observed)
    return ("partial" if missing else "success"), {
        "expected": len(expected), "observed": len(expected & observed),
        "missing_series": missing,
    }


def _source_observed_at(rows: list[dict[str, Any]]) -> str:
    values = {str(row.get("collected_at") or "") for row in rows}
    if len(values) != 1 or "" in values:
        raise RuntimeError("One source response must have one collected_at")
    return values.pop()
```

- [ ] **Step 4: Refactor collection per source**

Import `uuid4` and Task 2 functions. Use the module's existing `LOGGER` in this best-effort error recorder so an unavailable error ledger cannot prevent the next source attempt:

```python
def _record_source_failure_safely(db: MySQLClient, **values: Any) -> None:
    try:
        record_market_sentiment_source_failure(db, **values)
    except Exception:
        LOGGER.exception("Failed to record sentiment source failure: %s", values.get("source"))
```

Create one `collection_id`, then for each enabled source:

```python
batch_id = str(uuid4())
requested_at = _utc_now_string()
try:
    source_rows = fetch_rows()
    if not source_rows:
        missing.append(source)
        _record_source_failure_safely(
            db, collection_id=collection_id, batch_id=batch_id, source=source,
            source_ref=source_ref, requested_at=requested_at,
            completed_at=_utc_now_string(), status="missing",
            error_msg="Source returned no normalized observations",
        )
        continue
    status, source_coverage = _source_coverage(source, source_rows)
    saved = persist_market_sentiment_source_capture(
        db, collection_id=collection_id, batch_id=batch_id, source=source,
        source_ref=source_ref, requested_at=requested_at,
        observed_at=_source_observed_at(source_rows),
        completed_at=_utc_now_string(), status=status,
        coverage=source_coverage, rows=source_rows,
    )
    snapshot_rows_stored += saved["snapshot_rows_written"]
    canonical_rows_stored += saved["canonical_rows_written"]
except Exception as exc:
    reason = str(exc)[:500]
    failed.append({"source": source, "reason": reason})
    _record_source_failure_safely(
        db, collection_id=collection_id, batch_id=batch_id, source=source,
        source_ref=source_ref, requested_at=requested_at,
        completed_at=_utc_now_string(), status="error", error_msg=reason,
    )
```

Return `stored=canonical_rows_stored` plus all new summary keys and all three qualified target tables. Keep schema setup and the source loop inside the existing outer `try/finally` so `db.close()` always runs, including schema-sync failures. Remove the local aggregate `_upsert_sentiment_rows` and remove the duplicated current `failed.append(...)`.

- [ ] **Step 5: Verify parsers, collector, and legacy job**

```bash
.venv/bin/python -m unittest discover -s tests -p 'test_sentiment_pit.py' -v
.venv/bin/python -m unittest \
  tests.test_service_contracts.MarketIntelligenceIngestionContractTests.test_cnn_fear_greed_parser_builds_overall_history_and_component_rows \
  tests.test_service_contracts.MarketIntelligenceIngestionContractTests.test_aaii_sentiment_parser_builds_bearish_and_spread_rows \
  tests.test_service_contracts.MarketIntelligenceIngestionContractTests.test_ingestion_job_wraps_market_sentiment_collection_summary -v
```

Expected: focused tests and three legacy contracts pass.

- [ ] **Step 6: Commit**

```bash
git add finance/data/sentiment.py tests/test_sentiment_pit.py
git commit -m "CNN AAII 수집을 PIT 이중 저장으로 전환"
```

---

### Task 4: Add UTC As-Known And Capture-Summary Loaders

**Files:**
- Modify: `finance/loaders/sentiment.py:1-70`
- Modify: `tests/test_sentiment_pit.py`

**Interfaces:**
- Produces: `load_market_sentiment_as_known(*, known_at, series_ids=None, observation_start=None, observation_end=None, query_fn=None) -> pd.DataFrame`; `load_market_sentiment_capture_summary(*, query_fn=None) -> dict`.

- [ ] **Step 1: Write failing query-contract tests**

```python
class SentimentPitLoaderTests(unittest.TestCase):
    def test_as_known_uses_cutoff_and_default_observation_end(self) -> None:
        from finance.loaders.sentiment import load_market_sentiment_as_known
        captured = {}
        def query(database, sql, params):
            captured.update(database=database, sql=sql, params=params)
            return [{**sentiment_row(37.1), "id": 1, "batch_id": "b",
                     "collection_id": "c", "observed_at": "2026-07-20 01:00:00"}]
        frame = load_market_sentiment_as_known(
            known_at="2026-07-20T01:30:00Z",
            series_ids=["CNN_FEAR_GREED"], query_fn=query,
        )
        self.assertIn("ROW_NUMBER() OVER", captured["sql"])
        self.assertIn("observed_at <= %s", captured["sql"])
        self.assertIn("observation_date <= %s", captured["sql"])
        self.assertIn("2026-07-20", captured["params"])
        self.assertEqual(frame.iloc[0]["value"], 37.1)

    def test_capture_summary_groups_sources(self) -> None:
        from finance.loaders.sentiment import load_market_sentiment_capture_summary
        summary = load_market_sentiment_capture_summary(query_fn=lambda *_: [{
            "source": "cnn_fear_greed", "pit_start_at": "2026-07-20 01:00:00",
            "latest_capture_at": "2026-07-21 01:00:00", "capture_count": 2,
        }])
        self.assertEqual(summary["cnn_fear_greed"]["capture_count"], 2)
```

- [ ] **Step 2: Run and confirm RED**

Run Task 1 Step 2. Expected: missing loader functions.

- [ ] **Step 3: Add the injectable query and UTC parser**

```python
QueryFn = Callable[[str, str, tuple[Any, ...]], list[dict[str, Any]]]
PIT_COLUMNS = ["id", "batch_id", "collection_id", "series_id",
               "observation_date", "source", "source_type", "source_mode",
               "source_ref", "series_name", "category", "frequency", "units",
               "value", "release_lag_days", "coverage_status",
               "missing_fields_json", "observed_at", "error_msg"]


def _query_sentiment(sql: str, params: tuple[Any, ...], *, query_fn: QueryFn | None):
    if query_fn is not None: return list(query_fn("finance_meta", sql, params))
    db = MySQLClient("localhost", "root", "1234", 3306)
    try:
        db.use_db("finance_meta")
        return db.query(sql, params)
    except Exception as exc:
        text = str(exc).lower()
        if "market_sentiment_" in text and ("doesn't exist" in text or "unknown table" in text):
            return []
        raise
    finally:
        db.close()
```

Normalize UTC input exactly once:

```python
def _known_at_utc(value: str | pd.Timestamp) -> pd.Timestamp:
    known_at = pd.Timestamp(value)
    if pd.isna(known_at):
        raise ValueError("known_at must be a valid timestamp")
    if known_at.tzinfo is None:
        return known_at.tz_localize("UTC")
    return known_at.tz_convert("UTC")
```

Use `known_at_utc.tz_localize(None).to_pydatetime()` only for the MySQL `observed_at` parameter and `known_at_utc.date()` as the default observation end.

- [ ] **Step 4: Implement the ranked as-known query**

Use this exact selection rule:

```sql
WITH eligible_versions AS (
  SELECT snapshot_rows.*,
         ROW_NUMBER() OVER (
           PARTITION BY series_id, observation_date, source
           ORDER BY observed_at DESC, id DESC
         ) AS version_rank
  FROM market_sentiment_observation_snapshot snapshot_rows
  WHERE observed_at <= %s
    AND observation_date <= %s
)
SELECT id, batch_id, collection_id, series_id, observation_date, source,
       source_type, source_mode, source_ref, series_name, category, frequency,
       units, value, release_lag_days, coverage_status, missing_fields_json,
       observed_at, error_msg
FROM eligible_versions
WHERE version_rank = 1
ORDER BY series_id, observation_date, source
```

Build `predicates = ["observed_at <= %s", "observation_date <= %s"]` and parameters `[known_at_mysql, end_date]`. Append `"observation_date >= %s"` when `observation_start` is provided. Normalize requested IDs to uppercase, append `f"series_id IN ({placeholders})"`, and extend parameters by those IDs. Join predicates with `AND` inside the CTE. Return a `PIT_COLUMNS` DataFrame, parsing `observation_date` and `observed_at` with `pd.to_datetime` and `value` with `pd.to_numeric`.

Implement summary with:

```sql
SELECT source, MIN(observed_at) AS pit_start_at,
       MAX(observed_at) AS latest_capture_at, COUNT(*) AS capture_count
FROM market_sentiment_collection_batch
WHERE status IN ('success','partial') AND observed_at IS NOT NULL
GROUP BY source ORDER BY source
```

Return a dict keyed by source, with timestamp strings truncated to seconds and integer `capture_count`.

- [ ] **Step 5: Confirm GREEN and commit**

Run Task 1 Step 2. Expected: all focused tests pass.

```bash
git add finance/loaders/sentiment.py tests/test_sentiment_pit.py
git commit -m "시장 심리 known-at 조회 계약 추가"
```

---

### Task 5: Wire Job Details, Ingestion Registry, And Daily Automation

**Files:**
- Modify: `app/jobs/ingestion_jobs.py:3137-3205`
- Modify: `app/jobs/overview_automation.py:1-260`
- Modify: `app/web/ingestion/registry.py:66-74`
- Modify: `tests/test_service_contracts.py:11047-11066`
- Modify: `tests/test_service_contracts.py:11830-11844`
- Modify: `tests/test_service_contracts.py:27130-27155`

**Interfaces:**
- Consumes: Task 3 summary and `ScheduledJobSpec`.
- Produces: compatible job details and a 24-hour `market_sentiment` automation spec for safe, standard, broad, and browser-safe profiles.

- [ ] **Step 1: Write failing job and automation assertions**

Extend the mocked collection summary with:

```python
"collection_id": "00000000-0000-0000-0000-000000000001",
"batch_ids": {"cnn_fear_greed": "batch-cnn", "aaii_sentiment_survey": "batch-aaii"},
"snapshot_rows_stored": 260,
"canonical_rows_stored": 260,
"target_tables": [
    "finance_meta.macro_series_observation",
    "finance_meta.market_sentiment_collection_batch",
    "finance_meta.market_sentiment_observation_snapshot",
],
```

Assert the same three target tables, `snapshot_rows_stored == 260`, and two batch IDs. Rename the browser-safe test to `test_browser_safe_profile_includes_intraday_and_daily_sentiment` and assert:

```python
self.assertEqual([row["job_id"] for row in plan], ["sp500_intraday", "market_sentiment"])
sentiment = next(row for row in plan if row["job_id"] == "market_sentiment")
self.assertEqual(sentiment["cadence_minutes"], 24 * 60)
self.assertFalse(sentiment["market_hours_only"])
```

Add `self.assertIn("market_sentiment", job_ids)` to the standard-plan test.

- [ ] **Step 2: Run and confirm RED**

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.OverviewAutomationContractTests.test_overview_automation_standard_plan_includes_symbol_directory_refresh \
  tests.test_service_contracts.OverviewAutomationContractTests.test_browser_safe_profile_includes_intraday_and_daily_sentiment \
  tests.test_service_contracts.MarketIntelligenceIngestionContractTests.test_ingestion_job_wraps_market_sentiment_collection_summary -v
```

Expected: failures for missing automation job and one-table details.

- [ ] **Step 3: Keep rows_written stable and expand details**

Keep `rows_written = int(summary.get("stored") or 0)` and add:

```python
"collection_id": summary.get("collection_id"),
"batch_ids": summary.get("batch_ids") or {},
"snapshot_rows_stored": int(summary.get("snapshot_rows_stored") or 0),
"canonical_rows_stored": int(summary.get("canonical_rows_stored") or rows_written),
"target_tables": summary.get("target_tables") or ["finance_meta.macro_series_observation"],
```

Set the Ingestion registry target list to the same three fully qualified tables.

- [ ] **Step 4: Register daily capture**

Import `run_collect_market_sentiment`, add:

```python
def _run_market_sentiment(_: datetime) -> JobResult:
    return run_collect_market_sentiment()
```

and place this spec immediately after `sp500_intraday`:

```python
ScheduledJobSpec(
    job_id="market_sentiment",
    job_name="collect_market_sentiment",
    label="CNN / AAII Sentiment",
    cadence_minutes=24 * 60,
    profiles=("safe", "standard", "broad", "browser_safe"),
    market_hours_only=False,
    runner=_run_market_sentiment,
    description="Capture daily CNN and AAII source views for Overview Sentiment.",
),
```

- [ ] **Step 5: Confirm GREEN and commit**

Run the entire `OverviewAutomationContractTests` class plus the ingestion test. Expected: all pass.

```bash
git add app/jobs/ingestion_jobs.py app/jobs/overview_automation.py app/web/ingestion/registry.py tests/test_service_contracts.py
git commit -m "Overview 심리 일일 PIT 수집 연결"
```

---

### Task 6: Separate Full Chart History From 180-Day Interpretation

**Files:**
- Modify: `app/services/overview/sentiment.py:964-1105`
- Modify: `app/web/overview/sentiment_helpers.py:569-704`
- Modify: `tests/test_service_contracts.py:22667-22930`

**Interfaces:**
- Consumes: canonical full history and `load_market_sentiment_capture_summary`.
- Produces: full `snapshot["history_rows"]`, 180-day analysis input, and `snapshot/payload["history_coverage"]`.

- [ ] **Step 1: Write a failing full-versus-recent service test**

Add this exact test, using the minimum complete current CNN row and three canonical history points:

```python
def test_market_sentiment_keeps_full_chart_history_but_interprets_recent_180_days(self) -> None:
    from app.services.overview.sentiment import build_market_sentiment_snapshot

    snapshot_rows = pd.DataFrame([{
        "series_id": "CNN_FEAR_GREED",
        "observation_date": pd.Timestamp("2026-07-17"),
        "source": "cnn_fear_greed", "source_type": "official",
        "source_mode": "json", "series_name": "CNN Fear & Greed",
        "category": "sentiment_index", "units": "score_0_100", "value": 37.1,
        "coverage_status": "actual", "missing_fields_json": json.dumps({"rating": "fear"}),
        "collected_at": pd.Timestamp("2026-07-20 01:00:00"),
        "staleness_days": 3, "snapshot_status": "actual",
    }])
    history_rows = pd.DataFrame([
        {"series_id": "CNN_FEAR_GREED", "observation_date": pd.Timestamp("2025-06-04"),
         "source": "cnn_fear_greed", "value": 62.0},
        {"series_id": "CNN_FEAR_GREED", "observation_date": pd.Timestamp("2026-07-16"),
         "source": "cnn_fear_greed", "value": 41.0},
        {"series_id": "CNN_FEAR_GREED", "observation_date": pd.Timestamp("2026-07-17"),
         "source": "cnn_fear_greed", "value": 37.1},
    ])
    snapshot = build_market_sentiment_snapshot(
        snapshot_rows=snapshot_rows, history_rows=history_rows,
        capture_summary={"cnn_fear_greed": {
            "pit_start_at": "2026-07-20 01:00:00",
            "latest_capture_at": "2026-07-20 01:00:00", "capture_count": 1,
        }},
        today=date(2026, 7, 20),
    )
    self.assertEqual(len(snapshot["history_rows"]), 3)
    cnn_range = next(row for row in snapshot["analysis"]["range_context"]
                     if row["series"] == "CNN Fear & Greed")
    self.assertEqual(cnn_range["sample_count"], 2)
    self.assertEqual(snapshot["history_coverage"]["cnn"]["canonical_start"], "2025-06-04")
    self.assertEqual(snapshot["history_coverage"]["cnn"]["pit_start_at"], "2026-07-20 01:00:00")
```

- [ ] **Step 2: Run and confirm RED**

Run the new test by its full unittest name. Expected: unknown `capture_summary` or old row included in the recent sample.

- [ ] **Step 3: Add explicit recent-window and coverage helpers**

```python
SENTIMENT_ANALYSIS_WINDOW_DAYS = 180


def _recent_sentiment_history(history: pd.DataFrame, *, today: date) -> pd.DataFrame:
    if history.empty or "observation_date" not in history: return history.copy()
    cutoff = pd.Timestamp(today) - pd.Timedelta(days=SENTIMENT_ANALYSIS_WINDOW_DAYS)
    dates = pd.to_datetime(history["observation_date"], errors="coerce")
    return history[dates >= cutoff].copy()


def _history_source_coverage(history: pd.DataFrame, *, series_id: str,
                             source: str, capture_summary: dict) -> dict[str, Any]:
    rows = _sentiment_history_observations(history, (series_id,))
    rows = rows[rows["source"].astype(str) == source]
    dates = pd.to_datetime(rows["observation_date"], errors="coerce").dropna()
    capture = dict(capture_summary.get(source) or {})
    return {
        "canonical_start": dates.min().strftime("%Y-%m-%d") if not dates.empty else None,
        "canonical_end": dates.max().strftime("%Y-%m-%d") if not dates.empty else None,
        "observation_count": int(dates.nunique()),
        "pit_start_at": capture.get("pit_start_at"),
        "latest_capture_at": capture.get("latest_capture_at"),
        "capture_count": int(capture.get("capture_count") or 0),
    }
```

- [ ] **Step 4: Load full history and route recent history only to analysis**

Change the signature to accept `capture_summary: dict | None` and remove `max_history_days`. When loading history from DB, pass only `end=end_date`. Resolve the summary from the injected dict or `load_market_sentiment_capture_summary()`.

Create `analysis_history_frame = _recent_sentiment_history(history_frame, today=today_value)`. Return full `history_out`, call `_build_market_sentiment_analysis(..., history_rows=analysis_history_frame)`, and add:

```python
"history_coverage": {
    "cnn": _history_source_coverage(history_frame, series_id="CNN_FEAR_GREED",
        source="cnn_fear_greed", capture_summary=capture_summary_value),
    "aaii": _history_source_coverage(history_frame, series_id="AAII_BULL_BEAR_SPREAD",
        source="aaii_sentiment_survey", capture_summary=capture_summary_value),
    "cnn_components_note": "수집 시작 이후 현재값을 축적 중",
},
```

- [ ] **Step 5: Add JSON-safe V2 coverage fields**

Add without changing `schema_version`:

```python
coverage_source = dict(snapshot.get("history_coverage") or {})


def history_coverage_payload(key: str) -> dict[str, Any]:
    source = dict(coverage_source.get(key) or {})
    return {
        "canonical_start": _display_text(source.get("canonical_start"), ""),
        "canonical_end": _display_text(source.get("canonical_end"), ""),
        "observation_count": int(source.get("observation_count") or 0),
        "pit_start_at": _display_text(source.get("pit_start_at"), ""),
        "latest_capture_at": _display_text(source.get("latest_capture_at"), ""),
        "capture_count": int(source.get("capture_count") or 0),
    }
```

Then add the payload field:

```python
"history_coverage": {
    "default_period": "6M",
    "periods": ["6M", "1Y", "ALL"],
    "cnn": history_coverage_payload("cnn"),
    "aaii": history_coverage_payload("aaii"),
    "cnn_components_note": _display_text(
        coverage_source.get("cnn_components_note"),
        "수집 시작 이후 현재값을 축적 중",
    ),
},
```

Extend the existing payload fixture and assert the three periods, full old point, canonical start, PIT start, and unchanged `outlook.status == "UNAVAILABLE"`.

- [ ] **Step 6: Verify and commit**

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_sentiment_keeps_full_chart_history_but_interprets_recent_180_days \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_sentiment_snapshot_adds_range_divergence_and_component_history \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_sentiment_react_payload_uses_existing_snapshot_fields -v
git add app/services/overview/sentiment.py app/web/overview/sentiment_helpers.py tests/test_service_contracts.py
git commit -m "심리 장기 그래프와 최근 해석 범위 분리"
```

Expected: all three tests pass.

---

### Task 7: Add One Shared 6M, 1Y, And All Period Control

**Files:**
- Modify: `app/web/streamlit_components/sentiment_workbench/src/SentimentWorkbench.tsx:1-330`
- Modify: `app/web/streamlit_components/sentiment_workbench/src/SentimentHistorySection.tsx:1-280`
- Modify: `app/web/streamlit_components/sentiment_workbench/src/style.css:330-410`
- Modify: `tests/test_service_contracts.py:8868-8955`
- Rebuild: `app/web/streamlit_components/sentiment_workbench/component_static/`

**Interfaces:**
- Consumes: Task 6 coverage/full series.
- Produces: `HistoryPeriod`, `HistoryCoverage`, `filterChartPanel(...)`, shared buttons, and compact coverage copy.

- [ ] **Step 1: Write failing React source-contract assertions**

```python
def test_sentiment_history_uses_one_shared_period_for_both_panels(self) -> None:
    root = Path("app/web/streamlit_components/sentiment_workbench/src")
    types = (root / "SentimentWorkbench.tsx").read_text(encoding="utf-8")
    history = (root / "SentimentHistorySection.tsx").read_text(encoding="utf-8")
    style = (root / "style.css").read_text(encoding="utf-8")
    self.assertIn('export type HistoryPeriod = "6M" | "1Y" | "ALL"', types)
    self.assertIn('useState<HistoryPeriod>(coverage.default_period)', history)
    self.assertIn('const periods: HistoryPeriod[] = ["6M", "1Y", "ALL"]', history)
    for key in ("cnn", "aaii_responses", "aaii_spread"):
        self.assertIn(f"filterChartPanel(charts.{key}, period, anchorTimestamp)", history)
    self.assertIn('aria-pressed={period === key}', history)
    self.assertIn("sentiment-workbench__history-periods", style)
    self.assertIn("sentiment-workbench__history-coverage", style)
```

- [ ] **Step 2: Run and confirm RED**

Run the new source-contract test. Expected: missing types and controls.

- [ ] **Step 3: Extend V2 types**

```typescript
export type HistoryPeriod = "6M" | "1Y" | "ALL";
export type SourceHistoryCoverage = {
  canonical_start: string; canonical_end: string; observation_count: number;
  pit_start_at: string; latest_capture_at: string; capture_count: number;
};
export type HistoryCoverage = {
  default_period: HistoryPeriod; periods: HistoryPeriod[];
  cnn: SourceHistoryCoverage; aaii: SourceHistoryCoverage;
  cnn_components_note: string;
};
```

Add `history_coverage: HistoryCoverage` to `SentimentWorkbenchPayload` and pass it as `coverage={payload.history_coverage}` to `SentimentHistorySection`.

- [ ] **Step 4: Add pure shared filtering**

```typescript
function periodStart(period: HistoryPeriod, anchor: number) {
  if (period === "ALL") return Number.NEGATIVE_INFINITY;
  const start = new Date(anchor);
  start.setUTCHours(0, 0, 0, 0);
  start.setUTCMonth(start.getUTCMonth() - (period === "6M" ? 6 : 12));
  return start.getTime();
}

export function filterChartPanel(panel: ChartPanel, period: HistoryPeriod, anchor: number): ChartPanel {
  const cutoff = periodStart(period, anchor);
  return {...panel, series: panel.series.filter((point) => {
    const timestamp = Date.parse(point.date);
    return Number.isFinite(timestamp) && timestamp >= cutoff && timestamp <= anchor;
  })};
}
```

Set `anchorTimestamp` to the maximum valid date across all three panels, not `Date.now()` when observations exist.

- [ ] **Step 5: Render one control and coverage block**

Initialize:

```typescript
const [period, setPeriod] = useState<HistoryPeriod>(coverage.default_period);
const periods: HistoryPeriod[] = ["6M", "1Y", "ALL"];
const visibleCharts = {
  cnn: filterChartPanel(charts.cnn, period, anchorTimestamp),
  aaii_responses: filterChartPanel(charts.aaii_responses, period, anchorTimestamp),
  aaii_spread: filterChartPanel(charts.aaii_spread, period, anchorTimestamp),
};
```

Add these pure display helpers:

```typescript
function coverageDate(value: string) {
  return value ? value.slice(0, 10) : "-";
}

function coverageLine(label: string, source: SourceHistoryCoverage) {
  const range = source.canonical_start && source.canonical_end
    ? `${source.canonical_start}~${source.canonical_end}`
    : "이력 없음";
  const pit = source.pit_start_at
    ? `수집 당시 기록 ${coverageDate(source.pit_start_at)}부터`
    : "수집 당시 기록 축적 시작 전";
  return `${label} · ${range} · ${source.observation_count}개 · ${pit}`;
}
```

Replace the existing section heading with one toolbar shared by both graphs:

```tsx
<div className="sentiment-workbench__history-toolbar">
  <div>
    <span>History</span>
    <h3 id="sentiment-history-title">두 소스의 변화 경로</h3>
    <small>곡선 보정 없이 관측점을 직선으로 연결</small>
  </div>
  <div className="sentiment-workbench__history-tools">
    <div className="sentiment-workbench__history-periods" aria-label="그래프 기간">
      {periods.map((key) => (
        <button
          aria-pressed={period === key}
          key={key}
          onClick={() => setPeriod(key)}
          type="button"
        >
          {key === "ALL" ? "전체" : key}
        </button>
      ))}
    </div>
    <div className="sentiment-workbench__history-coverage">
      <span>{coverageLine("CNN", coverage.cnn)}</span>
      <span>{coverageLine("AAII", coverage.aaii)}</span>
      <small>{coverage.cnn_components_note}</small>
    </div>
  </div>
</div>
```

Pass only `visibleCharts.cnn`, `visibleCharts.aaii_responses`, and `visibleCharts.aaii_spread` to the two chart panels.

- [ ] **Step 6: Add responsive styles**

Add these exact styles, placing the media override inside the component's existing mobile breakpoint. Keep `.sentiment-workbench__history-grid` one column and do not alter chart SVG sizing.

```css
.sentiment-workbench__history-toolbar {
  align-items: flex-start;
  display: flex;
  gap: 20px;
  justify-content: space-between;
}

.sentiment-workbench__history-tools {
  align-items: flex-end;
  display: grid;
  gap: 8px;
  justify-items: end;
}

.sentiment-workbench__history-periods {
  background: #e9eef2;
  border-radius: 9px;
  display: inline-flex;
  gap: 2px;
  padding: 3px;
}

.sentiment-workbench__history-periods button {
  background: transparent;
  border: 0;
  border-radius: 7px;
  color: #66768a;
  cursor: pointer;
  font-size: 0.7rem;
  font-weight: 800;
  padding: 6px 10px;
}

.sentiment-workbench__history-periods button[aria-pressed="true"] {
  background: #fff;
  box-shadow: 0 1px 3px rgb(23 32 51 / 12%);
  color: #172033;
}

.sentiment-workbench__history-coverage {
  color: #718096;
  display: grid;
  font-size: 0.64rem;
  font-weight: 680;
  gap: 2px;
  text-align: right;
}

.sentiment-workbench__history-coverage small {
  color: #8a97a8;
  font-size: inherit;
}

@media (max-width: 720px) {
  .sentiment-workbench__history-toolbar {
    display: grid;
  }

  .sentiment-workbench__history-tools {
    justify-items: start;
  }

  .sentiment-workbench__history-coverage {
    text-align: left;
  }
}
```

- [ ] **Step 7: Verify build and commit**

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.OverviewAutomationContractTests.test_sentiment_history_uses_one_shared_period_for_both_panels \
  tests.test_service_contracts.OverviewAutomationContractTests.test_sentiment_react_evidence_surface_improves_graphs_and_raw_detail \
  tests.test_service_contracts.OverviewAutomationContractTests.test_sentiment_react_chart_tooltip_turns_inward_at_horizontal_edges -v
npm run build --prefix app/web/streamlit_components/sentiment_workbench
git add app/web/streamlit_components/sentiment_workbench/src app/web/streamlit_components/sentiment_workbench/component_static tests/test_service_contracts.py
git commit -m "Overview 심리 장기 그래프 기간 선택 추가"
```

Expected: three tests pass and Vite exits 0.

---

### Task 8: Sync Schema, Capture First Truth, Browser QA, And Closeout

**Files:**
- Modify: `.aiworkspace/note/finance/docs/runbooks/OVERVIEW_MARKET_INTELLIGENCE.md:175-195,400-425`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-sentiment-history-pit-v2-20260720/{STATUS,RUNS,RISKS}.md`
- Modify: `.aiworkspace/note/finance/{WORK_PROGRESS,QUESTION_AND_ANALYSIS_LOG}.md`
- Create uncommitted: `overview-sentiment-history-pit-v2-qa.png`

**Interfaces:**
- Consumes: Tasks 1-7 and local MySQL/Streamlit.
- Produces: additive tables, first source batches, verified cutoff replay, responsive QA, durable handoff.

- [ ] **Step 1: Run all focused checks before DB writes**

```bash
.venv/bin/python -m unittest discover -s tests -p 'test_sentiment_pit.py' -v
.venv/bin/python -m unittest \
  tests.test_service_contracts.OverviewAutomationContractTests \
  tests.test_service_contracts.MarketIntelligenceIngestionContractTests.test_cnn_fear_greed_parser_builds_overall_history_and_component_rows \
  tests.test_service_contracts.MarketIntelligenceIngestionContractTests.test_aaii_sentiment_parser_builds_bearish_and_spread_rows \
  tests.test_service_contracts.MarketIntelligenceIngestionContractTests.test_aaii_fetcher_uses_browser_document_headers \
  tests.test_service_contracts.MarketIntelligenceIngestionContractTests.test_ingestion_job_wraps_market_sentiment_collection_summary \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests -v
npm run build --prefix app/web/streamlit_components/sentiment_workbench
.venv/bin/python -m py_compile finance/data/sentiment.py finance/data/sentiment_store.py finance/loaders/sentiment.py app/jobs/ingestion_jobs.py app/jobs/overview_automation.py app/services/overview/sentiment.py app/web/overview/sentiment_helpers.py
git diff --check
```

Expected: tests pass, build exits 0, compilation succeeds, diff check is silent.

- [ ] **Step 2: Additively sync only approved tables**

```bash
.venv/bin/python - <<'PY'
from finance.data.db.mysql import MySQLClient
from finance.data.sentiment_store import ensure_market_sentiment_schema
db = MySQLClient("localhost", "root", "1234", 3306)
try:
    ensure_market_sentiment_schema(db)
finally:
    db.close()
print("sentiment schema sync: OK")
PY
```

Expected: success without deletion or canonical-row rewriting.

- [ ] **Step 3: Capture and verify the first immutable truth**

```bash
.venv/bin/python - <<'PY'
from finance.data.sentiment import collect_and_store_market_sentiment
from finance.loaders.sentiment import load_market_sentiment_as_known, load_market_sentiment_capture_summary
result = collect_and_store_market_sentiment()
assert result["snapshot_rows_stored"] > 0, result
summary = load_market_sentiment_capture_summary()
latest = max(row["latest_capture_at"] for row in summary.values() if row.get("latest_capture_at"))
as_known = load_market_sentiment_as_known(known_at=latest)
assert not as_known.empty
print({"collection_id": result["collection_id"], "batch_ids": result["batch_ids"],
       "snapshot_rows": result["snapshot_rows_stored"], "as_known_rows": len(as_known),
       "pit_sources": sorted(summary)})
PY
```

Expected: positive counts and source batch IDs. If one external provider is blocked, verify the successful source, record the failed source, and do not invent its batch.

- [ ] **Step 4: Perform Browser QA**

Use `browser:control-in-app-browser`:

1. Open Overview → Sentiment with actual DB data.
2. Confirm default 6M and two vertically stacked chart panels.
3. Select 1Y; confirm both panels share the horizon and shorter AAII coverage still renders.
4. Select 전체; confirm CNN contains a point older than 180 days while Hero/current interpretation remains unchanged.
5. Switch AAII tabs by click and arrow keys; hover first/last CNN points.
6. Confirm canonical range, PIT start, and component capture-only copy.
7. Repeat at 420px; require document/main/component `scrollWidth == clientWidth` and zero console errors.
8. Save `overview-sentiment-history-pit-v2-qa.png` and leave it untracked.

- [ ] **Step 5: Sync durable docs**

Use `finance-doc-sync`. Document these exact facts in the runbook:

```markdown
- `collect_market_sentiment`는 CNN과 AAII를 source별 transaction으로 저장한다.
- `macro_series_observation`은 현재 화면용 최신 이력이고, `market_sentiment_observation_snapshot`은 덮어쓰지 않는 수집 당시 기록이다.
- `known_at`은 공식 발표 시각이 아니라 이 application이 UTC 기준으로 확인한 시각이다.
- 24시간 automation과 수동 갱신은 같은 저장 경로를 사용하며 운영 scheduler는 미국 시장 마감 이후 실행을 권장한다.
- source 하나가 실패하면 성공한 다른 source는 유지하고 실패 source는 다음 실행에서 재시도한다.
- 기존 canonical row를 과거 PIT truth로 소급하지 않는다.
```

Set task status to overall `2/4차` complete, record first PIT dates/counts and QA evidence, and keep 1W/1M `UNAVAILABLE` because chronological sample length is insufficient. Root logs receive only 3-5 lines and link to the active task.

- [ ] **Step 6: Final verification and closeout commit**

```bash
git status --short
git diff --check
git add .aiworkspace/note/finance/docs/runbooks/OVERVIEW_MARKET_INTELLIGENCE.md .aiworkspace/note/finance/tasks/active/overview-sentiment-history-pit-v2-20260720 .aiworkspace/note/finance/WORK_PROGRESS.md .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git diff --cached --check
git commit -m "Overview 심리 PIT 축적 2차 완료"
```

Expected: QA screenshot, run-history JSONL, unrelated research, `.superpowers/`, and existing screenshots remain unstaged. Final handoff reports overall `2/4차`, stages 3-4 remaining, actual PIT start, checks, and active-task location.

---

## Execution Checkpoints

- After Task 2: review transaction ordering and idempotency.
- After Task 4: review a cutoff between two revisions and a cutoff before first capture.
- After Task 5: confirm browser-safe daily capture remains within approved scope.
- After Task 7: review code before production schema sync and live capture.
- After Task 8: report actual PIT sample length and do not claim forecast readiness.
