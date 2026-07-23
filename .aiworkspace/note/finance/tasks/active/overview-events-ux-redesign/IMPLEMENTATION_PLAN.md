# Market Calendar Coverage And React A Layout Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Alphabet 같은 주요 실적을 놓치지 않는 혼합 수집 계약과 FOMC / 미국 휴장 완전성을 구현하고, 시장일정 탭을 승인된 `A · 브리프 + 캘린더` React 화면으로 바꾼다.

**Architecture:** 순수한 priority / shard 계산은 새 `finance/data/market_event_coverage.py`에 두고, DB schema·provider 수집·checkpoint persistence는 `finance/data/market_intelligence.py`와 `finance/data/db/schema.py`가 소유한다. Overview job은 `Ingestion -> DB`만 실행하고, `app/services/overview/events.py`는 issuer grouping·KST 표시·필터별 일관된 view를 생성하며 React는 선택한 view를 렌더링한다.

**Tech Stack:** Python 3.12, unittest, MySQL schema sync / PyMySQL, pandas, Streamlit custom components, React 18, TypeScript 5, Vite 6.

## Global Constraints

- 기본 earnings 보장 범위는 미국 시가총액 상위 100 + 명시적 portfolio + 명시적 watchlist + 45일 이내 기존 실적 종목이다.
- S&P 500 전체는 약 100종목씩 순환하며 provider 실패가 없는 cycle은 5회 이내 완료한다.
- 실패 종목이 남아 있으면 coverage는 `partial`이고 retry queue가 비워진 뒤에만 `complete`다.
- GOOG / GOOGL raw row는 보존하되 issuer key가 같으면 화면에서는 `Alphabet · GOOG/GOOGL` 한 일정으로 표시한다.
- Exact datetime이 없으면 KST 자정을 만들지 않는다. 장전 / 장후 label도 없으면 `미국 기준 · 한국시간 미확인`으로 표시한다.
- FOMC와 미국 휴장 / 조기폐장 일정은 earnings 행 수와 무관하게 조회한다.
- UI와 service는 provider를 직접 호출하지 않는다. `Ingestion -> DB -> Service -> React`를 유지한다.
- Provider estimate는 issuer-confirmed 또는 official 일정으로 승격하지 않는다.
- 첫 화면은 사용자의 일정 판단이 중심이며 raw run / row / status 진단은 접힌 보조 근거에 둔다.
- 시장일정은 거래 신호, validation gate, broker action, 자동 리밸런싱이 아니다.
- 기존 registry, saved portfolio, run history, generated screenshot과 사용자 변경은 이 작업의 commit에 포함하지 않는다.
- 새 npm dependency는 추가하지 않는다.

---

## File Responsibility Map

- Create `finance/data/market_event_coverage.py`
  - symbol 정규화, priority 합집합, S&P 500 shard plan, checkpoint result 계산만 담당한다.
  - DB, provider, Streamlit을 import하지 않는다.
- Modify `finance/data/db/schema.py`
  - `market_event_calendar` issuer identity column과 `market_event_collection_coverage` table DDL을 소유한다.
- Modify `finance/data/market_intelligence.py`
  - event / coverage persistence, identity lookup, hybrid earnings orchestrator, official-year coverage 기록을 소유한다.
- Modify `app/jobs/ingestion_jobs.py`
  - hybrid earnings collector를 공통 `JobResult`로 감싼다.
- Modify `app/jobs/overview_actions.py`
  - 수동 Events refresh facade가 hybrid earnings job을 호출한다.
- Modify `app/jobs/overview_automation.py`
  - daily hybrid earnings와 current / next-year market-structure schedule을 등록한다.
- Modify `app/services/overview/events.py`
  - family-aware row loading, issuer display grouping, relevance, KST semantics, Korean warning, filter별 workbench view를 소유한다.
- Modify `app/web/overview_dashboard_helpers.py`
  - Overview Events의 날짜 범위와 family별 cap을 서비스에 전달한다.
- Modify `app/web/overview/events_helpers.py`
  - React payload / action dispatch adapter만 유지한다.
- Modify `app/web/streamlit_components/events_workbench/src/EventsWorkbench.tsx`
  - `events_workbench_v2` view 선택, A안 calendar/detail interaction을 렌더한다.
- Modify `app/web/streamlit_components/events_workbench/src/style.css`
  - A안 desktop / mobile layout과 기존 tab theme 정렬을 담당한다.
- Modify `tests/test_service_contracts.py`
  - data, job, service, React source contract의 RED / GREEN 회귀 테스트를 소유한다.
- Modify `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
  - 최종 ownership과 payload contract를 반영한다.
- Modify `.aiworkspace/note/finance/docs/architecture/DATA_DB_PIPELINE_FLOW.md`
  - hybrid coverage와 checkpoint data flow를 반영한다.
- Modify `.aiworkspace/note/finance/docs/runbooks/OVERVIEW_MARKET_INTELLIGENCE.md`
  - 수집 / 조회 / QA 운영 절차를 반영한다.
- Modify `.aiworkspace/note/finance/tasks/active/overview-events-ux-redesign/{STATUS,NOTES,RUNS,RISKS}.md`
  - 실행 상태, 발견, 검증, 남은 위험을 기록한다.

---

### Task 1: Event Identity And Coverage Persistence Contract

**Files:**
- Modify: `finance/data/db/schema.py:491-530`
- Modify: `finance/data/market_intelligence.py:330-370`
- Modify: `finance/data/market_intelligence.py:575-665`
- Test: `tests/test_service_contracts.py:28465-29420`

**Interfaces:**
- Consumes: existing `sync_table_schema()`, `_db()`, `_json_payload()`, `_timestamp_str()`.
- Produces:
  - `normalize_market_event_collection_coverage(row: dict[str, Any]) -> dict[str, Any]`
  - `upsert_market_event_collection_coverage(row: dict[str, Any], **db_kwargs) -> int`
  - `load_market_event_collection_coverage(coverage_key: str, **db_kwargs) -> dict[str, Any] | None`
  - event rows with nullable `issuer_key` and `issuer_name`.

- [ ] **Step 1: Write failing schema and normalization tests**

Add these tests to `MarketIntelligenceEventCalendarContractTests`:

```python
def test_market_event_schema_contains_issuer_and_coverage_contract(self) -> None:
    from finance.data.db.schema import MARKET_INTELLIGENCE_SCHEMAS

    event_sql = MARKET_INTELLIGENCE_SCHEMAS["market_event_calendar"]
    coverage_sql = MARKET_INTELLIGENCE_SCHEMAS["market_event_collection_coverage"]

    self.assertIn("issuer_key VARCHAR(64) NULL", event_sql)
    self.assertIn("issuer_name VARCHAR(255) NULL", event_sql)
    self.assertIn("coverage_key VARCHAR(128) NOT NULL", coverage_sql)
    self.assertIn("coverage_status VARCHAR(16) NOT NULL", coverage_sql)
    self.assertIn("UNIQUE KEY uk_market_event_coverage_key", coverage_sql)

def test_market_event_normalization_preserves_issuer_identity(self) -> None:
    from finance.data import market_intelligence as mi

    rows = mi.normalize_market_event_rows(
        [{
            "event_date": "2026-07-23",
            "event_type": "EARNINGS",
            "symbol": "GOOG",
            "issuer_key": "sec_cik:1652044",
            "issuer_name": "Alphabet Inc.",
            "title": "GOOG Earnings Release",
            "source": mi.EARNINGS_CALENDAR_SOURCE,
        }]
    )

    self.assertEqual(rows[0]["issuer_key"], "sec_cik:1652044")
    self.assertEqual(rows[0]["issuer_name"], "Alphabet Inc.")
```

- [ ] **Step 2: Run the focused tests and verify RED**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.MarketIntelligenceEventCalendarContractTests.test_market_event_schema_contains_issuer_and_coverage_contract \
  tests.test_service_contracts.MarketIntelligenceEventCalendarContractTests.test_market_event_normalization_preserves_issuer_identity
```

Expected: FAIL because `market_event_collection_coverage`, `issuer_key`, and `issuer_name` do not exist.

- [ ] **Step 3: Add schema definitions and sync registration**

Add the two event columns and the new table:

```python
"market_event_collection_coverage": """
    CREATE TABLE IF NOT EXISTS market_event_collection_coverage (
      id BIGINT AUTO_INCREMENT PRIMARY KEY,
      coverage_key VARCHAR(128) NOT NULL,
      event_family VARCHAR(32) NOT NULL,
      universe_scope VARCHAR(64) NOT NULL,
      window_start DATE NULL,
      window_end DATE NULL,
      expected_items INT NOT NULL DEFAULT 0,
      covered_items INT NOT NULL DEFAULT 0,
      failed_items INT NOT NULL DEFAULT 0,
      cursor_offset INT NOT NULL DEFAULT 0,
      batch_size INT NOT NULL DEFAULT 100,
      coverage_status VARCHAR(16) NOT NULL DEFAULT 'pending',
      cycle_started_at TIMESTAMP NULL,
      cycle_completed_at TIMESTAMP NULL,
      last_attempted_at TIMESTAMP NULL,
      last_success_at TIMESTAMP NULL,
      details_json JSON NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      UNIQUE KEY uk_market_event_coverage_key (coverage_key),
      KEY ix_market_event_coverage_family (event_family, universe_scope),
      KEY ix_market_event_coverage_status (coverage_status)
    );
""",
```

Add this sync call immediately after `market_event_calendar`:

```python
sync_table_schema(
    meta_db,
    "market_event_collection_coverage",
    MARKET_INTELLIGENCE_SCHEMAS["market_event_collection_coverage"],
    DB_META,
)
```

Extend event normalization and SQL columns:

```python
"issuer_key": str(item.get("issuer_key") or "").strip() or None,
"issuer_name": str(item.get("issuer_name") or "").strip() or None,
```

The `INSERT`, `VALUES`, and `ON DUPLICATE KEY UPDATE` clauses must include both fields between `symbol` and `title`.

- [ ] **Step 4: Add failing coverage persistence tests**

```python
def test_coverage_upsert_normalizes_complete_state(self) -> None:
    from finance.data import market_intelligence as mi

    class FakeDb:
        def __init__(self) -> None:
            self.rows = []
        def use_db(self, _name: str) -> None:
            pass
        def execute(self, _sql: str, params=None) -> None:
            self.rows.append(dict(params or {}))
        def close(self) -> None:
            pass

    fake_db = FakeDb()
    with (
        patch.object(mi, "_db", return_value=fake_db),
        patch.object(mi, "sync_table_schema"),
    ):
        written = mi.upsert_market_event_collection_coverage({
            "coverage_key": "earnings:sp500_cycle",
            "event_family": "earnings",
            "universe_scope": "sp500",
            "expected_items": 2,
            "covered_items": 2,
            "failed_items": 0,
            "cursor_offset": 0,
            "batch_size": 100,
            "details": {"covered_symbols": ["GOOG", "GOOGL"]},
        })

    self.assertEqual(written, 1)
    self.assertEqual(fake_db.rows[0]["coverage_status"], "complete")
    self.assertEqual(fake_db.rows[0]["details_json"], '{"covered_symbols":["GOOG","GOOGL"]}')
```

- [ ] **Step 5: Run the persistence test and verify RED**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.MarketIntelligenceEventCalendarContractTests.test_coverage_upsert_normalizes_complete_state
```

Expected: FAIL with missing `upsert_market_event_collection_coverage`.

- [ ] **Step 6: Implement coverage normalization, upsert, and load**

Use this contract:

```python
VALID_EVENT_COVERAGE_STATUSES = {"pending", "partial", "complete", "stale", "error"}

def normalize_market_event_collection_coverage(row: dict[str, Any]) -> dict[str, Any]:
    expected = max(0, int(row.get("expected_items") or 0))
    covered = max(0, int(row.get("covered_items") or 0))
    failed = max(0, int(row.get("failed_items") or 0))
    requested_status = str(row.get("coverage_status") or "").strip().lower()
    if requested_status not in VALID_EVENT_COVERAGE_STATUSES:
        requested_status = "complete" if expected > 0 and covered == expected and failed == 0 else "partial"
    return {
        "coverage_key": str(row.get("coverage_key") or "").strip(),
        "event_family": str(row.get("event_family") or "").strip().lower(),
        "universe_scope": str(row.get("universe_scope") or "").strip().lower(),
        "window_start": _event_date_str(row.get("window_start")),
        "window_end": _event_date_str(row.get("window_end")),
        "expected_items": expected,
        "covered_items": covered,
        "failed_items": failed,
        "cursor_offset": max(0, int(row.get("cursor_offset") or 0)),
        "batch_size": max(1, int(row.get("batch_size") or 100)),
        "coverage_status": requested_status,
        "cycle_started_at": row.get("cycle_started_at"),
        "cycle_completed_at": row.get("cycle_completed_at"),
        "last_attempted_at": row.get("last_attempted_at"),
        "last_success_at": row.get("last_success_at"),
        "details_json": _json_payload(row.get("details_json") or row.get("details") or {}),
    }

def upsert_market_event_collection_coverage(row: dict[str, Any], **db_kwargs: Any) -> int:
    normalized = normalize_market_event_collection_coverage(row)
    if not normalized["coverage_key"] or not normalized["event_family"] or not normalized["universe_scope"]:
        return 0
    db = _db(
        db_kwargs.get("host", "localhost"),
        db_kwargs.get("user", "root"),
        db_kwargs.get("password", "1234"),
        int(db_kwargs.get("port", 3306)),
    )
    try:
        db.use_db(DB_META)
        sync_table_schema(
            db,
            "market_event_collection_coverage",
            MARKET_INTELLIGENCE_SCHEMAS["market_event_collection_coverage"],
            DB_META,
        )
        db.execute(
            """
            INSERT INTO market_event_collection_coverage (
              coverage_key, event_family, universe_scope, window_start, window_end,
              expected_items, covered_items, failed_items, cursor_offset, batch_size,
              coverage_status, cycle_started_at, cycle_completed_at,
              last_attempted_at, last_success_at, details_json
            ) VALUES (
              %(coverage_key)s, %(event_family)s, %(universe_scope)s, %(window_start)s, %(window_end)s,
              %(expected_items)s, %(covered_items)s, %(failed_items)s, %(cursor_offset)s, %(batch_size)s,
              %(coverage_status)s, %(cycle_started_at)s, %(cycle_completed_at)s,
              %(last_attempted_at)s, %(last_success_at)s, %(details_json)s
            )
            ON DUPLICATE KEY UPDATE
              expected_items=VALUES(expected_items), covered_items=VALUES(covered_items),
              failed_items=VALUES(failed_items), cursor_offset=VALUES(cursor_offset),
              batch_size=VALUES(batch_size), coverage_status=VALUES(coverage_status),
              cycle_started_at=VALUES(cycle_started_at), cycle_completed_at=VALUES(cycle_completed_at),
              last_attempted_at=VALUES(last_attempted_at), last_success_at=VALUES(last_success_at),
              details_json=VALUES(details_json)
            """,
            normalized,
        )
        return 1
    finally:
        db.close()
```

`load_market_event_collection_coverage()` must select one row by exact `coverage_key`, decode `details_json` into `details`, and return `None` when no row exists.

- [ ] **Step 7: Run Task 1 tests and commit**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.MarketIntelligenceEventCalendarContractTests.test_market_event_schema_contains_issuer_and_coverage_contract \
  tests.test_service_contracts.MarketIntelligenceEventCalendarContractTests.test_market_event_normalization_preserves_issuer_identity \
  tests.test_service_contracts.MarketIntelligenceEventCalendarContractTests.test_coverage_upsert_normalizes_complete_state \
  tests.test_service_contracts.MarketIntelligenceEventCalendarContractTests.test_market_event_upsert_normalizes_payload_and_business_key \
  tests.test_service_contracts.MarketIntelligenceEventCalendarContractTests.test_market_intelligence_sync_includes_event_calendar_table
```

Expected: 5 tests PASS.

Commit:

```bash
git add finance/data/db/schema.py finance/data/market_intelligence.py tests/test_service_contracts.py
git commit -m "시장일정 수집 커버리지 스키마 추가"
```

---

### Task 2: Pure Priority And S&P 500 Shard Planner

**Files:**
- Create: `finance/data/market_event_coverage.py`
- Test: `tests/test_service_contracts.py:28465-29420`

**Interfaces:**
- Consumes: sequences of symbols, prior checkpoint dict, provider diagnostic rows.
- Produces:
  - `merge_priority_earnings_symbols(...) -> list[str]`
  - `build_sp500_shard_plan(universe_symbols, checkpoint, batch_size=100) -> dict[str, Any]`
  - `apply_sp500_shard_result(plan, diagnostics, checked_at) -> dict[str, Any]`
- No DB or provider dependency.

- [ ] **Step 1: Write failing pure-function tests**

```python
def test_priority_earnings_merge_keeps_alphabet_and_source_order(self) -> None:
    from finance.data.market_event_coverage import merge_priority_earnings_symbols

    symbols = merge_priority_earnings_symbols(
        retry_symbols=["ERR"],
        portfolio_symbols=["GOOGL", "MSFT"],
        watchlist_symbols=["GOOG"],
        major_cap_symbols=["AAPL", "GOOG", "GOOGL"],
        known_event_symbols=["NVDA", "MSFT"],
    )

    self.assertEqual(symbols, ["ERR", "GOOGL", "MSFT", "GOOG", "AAPL", "NVDA"])

def test_sp500_shard_plan_completes_five_clean_batches(self) -> None:
    from finance.data.market_event_coverage import apply_sp500_shard_result, build_sp500_shard_plan

    universe = [f"S{index:03d}" for index in range(500)]
    checkpoint = None
    for run_index in range(5):
        plan = build_sp500_shard_plan(universe, checkpoint, batch_size=100)
        diagnostics = [
            {"symbol": symbol, "status": "event_found", "reason": "ok"}
            for symbol in plan["batch_symbols"]
        ]
        checkpoint = apply_sp500_shard_result(
            plan,
            diagnostics,
            checked_at=f"2026-07-{23 + run_index:02d} 00:00:00",
        )

    self.assertEqual(checkpoint["covered_items"], 500)
    self.assertEqual(checkpoint["failed_items"], 0)
    self.assertEqual(checkpoint["coverage_status"], "complete")
    self.assertEqual(checkpoint["cursor_offset"], 0)

def test_sp500_shard_result_keeps_failed_symbol_partial(self) -> None:
    from finance.data.market_event_coverage import apply_sp500_shard_result, build_sp500_shard_plan

    plan = build_sp500_shard_plan(["GOOG", "GOOGL"], None, batch_size=100)
    checkpoint = apply_sp500_shard_result(
        plan,
        [
            {"symbol": "GOOG", "status": "event_found", "reason": "ok"},
            {"symbol": "GOOGL", "status": "failed", "reason": "provider_error"},
        ],
        checked_at="2026-07-23 00:00:00",
    )

    self.assertEqual(checkpoint["coverage_status"], "partial")
    self.assertEqual(checkpoint["details"]["covered_symbols"], ["GOOG"])
    self.assertEqual(checkpoint["details"]["failed_symbols"], ["GOOGL"])
```

- [ ] **Step 2: Run tests and verify RED**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.MarketIntelligenceEventCalendarContractTests.test_priority_earnings_merge_keeps_alphabet_and_source_order \
  tests.test_service_contracts.MarketIntelligenceEventCalendarContractTests.test_sp500_shard_plan_completes_five_clean_batches \
  tests.test_service_contracts.MarketIntelligenceEventCalendarContractTests.test_sp500_shard_result_keeps_failed_symbol_partial
```

Expected: FAIL because `finance.data.market_event_coverage` does not exist.

- [ ] **Step 3: Implement symbol merge and deterministic shard plan**

Create the module with these core functions:

```python
from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence
from typing import Any

SUCCESS_DIAGNOSTIC_STATUSES = {"event_found", "missing"}

def _symbols(values: Sequence[Any] | None) -> list[str]:
    output: list[str] = []
    seen: set[str] = set()
    for value in values or []:
        symbol = str(value or "").strip().upper()
        if symbol and symbol not in seen:
            seen.add(symbol)
            output.append(symbol)
    return output

def merge_priority_earnings_symbols(
    *,
    retry_symbols: Sequence[Any] = (),
    portfolio_symbols: Sequence[Any] = (),
    watchlist_symbols: Sequence[Any] = (),
    major_cap_symbols: Sequence[Any] = (),
    known_event_symbols: Sequence[Any] = (),
) -> list[str]:
    return _symbols([
        *retry_symbols,
        *portfolio_symbols,
        *watchlist_symbols,
        *major_cap_symbols,
        *known_event_symbols,
    ])

def _universe_hash(symbols: list[str]) -> str:
    return hashlib.sha256(json.dumps(symbols, separators=(",", ":")).encode("utf-8")).hexdigest()

def build_sp500_shard_plan(
    universe_symbols: Sequence[Any],
    checkpoint: dict[str, Any] | None,
    *,
    batch_size: int = 100,
) -> dict[str, Any]:
    universe = _symbols(universe_symbols)
    prior = dict(checkpoint or {})
    details = dict(prior.get("details") or {})
    universe_hash = _universe_hash(universe)
    reset = details.get("universe_hash") != universe_hash
    cursor = 0 if reset else max(0, int(prior.get("cursor_offset") or 0))
    size = max(1, int(batch_size or 100))
    batch = universe[cursor:cursor + size]
    if not batch and universe:
        cursor = 0
        batch = universe[:size]
    return {
        "coverage_key": "earnings:sp500_cycle",
        "event_family": "earnings",
        "universe_scope": "sp500",
        "expected_symbols": universe,
        "expected_items": len(universe),
        "batch_symbols": batch,
        "batch_size": size,
        "cursor_offset": cursor,
        "prior": {} if reset else prior,
        "universe_hash": universe_hash,
        "cycle_reset": reset,
    }
```

- [ ] **Step 4: Implement checkpoint result calculation**

```python
def apply_sp500_shard_result(
    plan: dict[str, Any],
    diagnostics: Sequence[dict[str, Any]],
    *,
    checked_at: str,
) -> dict[str, Any]:
    prior = dict(plan.get("prior") or {})
    prior_details = dict(prior.get("details") or {})
    covered = set(_symbols(prior_details.get("covered_symbols")))
    failed = set(_symbols(prior_details.get("failed_symbols")))
    missing_streaks = {
        str(key).upper(): int(value)
        for key, value in dict(prior_details.get("missing_streaks") or {}).items()
    }
    for diagnostic in diagnostics:
        symbol = str(diagnostic.get("symbol") or "").strip().upper()
        status = str(diagnostic.get("status") or "").strip().lower()
        if not symbol:
            continue
        if status in SUCCESS_DIAGNOSTIC_STATUSES:
            covered.add(symbol)
            failed.discard(symbol)
            if status == "missing":
                missing_streaks[symbol] = missing_streaks.get(symbol, 0) + 1
            else:
                missing_streaks[symbol] = 0
        else:
            failed.add(symbol)

    expected = list(plan.get("expected_symbols") or [])
    next_cursor = int(plan.get("cursor_offset") or 0) + len(plan.get("batch_symbols") or [])
    if next_cursor >= len(expected):
        next_cursor = 0
    complete = bool(expected) and len(covered) == len(expected) and not failed
    return {
        "coverage_key": "earnings:sp500_cycle",
        "event_family": "earnings",
        "universe_scope": "sp500",
        "expected_items": len(expected),
        "covered_items": len(covered),
        "failed_items": len(failed),
        "cursor_offset": next_cursor,
        "batch_size": int(plan.get("batch_size") or 100),
        "coverage_status": "complete" if complete else "partial",
        "cycle_started_at": prior.get("cycle_started_at") or checked_at,
        "cycle_completed_at": checked_at if complete else None,
        "last_attempted_at": checked_at,
        "last_success_at": checked_at if diagnostics and not failed else prior.get("last_success_at"),
        "details": {
            "universe_hash": plan.get("universe_hash"),
            "covered_symbols": sorted(covered),
            "failed_symbols": sorted(failed),
            "missing_streaks": dict(sorted(missing_streaks.items())),
        },
    }
```

- [ ] **Step 5: Run Task 2 tests and commit**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.MarketIntelligenceEventCalendarContractTests.test_priority_earnings_merge_keeps_alphabet_and_source_order \
  tests.test_service_contracts.MarketIntelligenceEventCalendarContractTests.test_sp500_shard_plan_completes_five_clean_batches \
  tests.test_service_contracts.MarketIntelligenceEventCalendarContractTests.test_sp500_shard_result_keeps_failed_symbol_partial
```

Expected: 3 tests PASS.

Commit:

```bash
git add finance/data/market_event_coverage.py tests/test_service_contracts.py
git commit -m "실적 우선군과 S&P500 순환 계획 추가"
```

---

### Task 3: Hybrid Earnings Orchestrator, Issuer Grouping Evidence, And Time Labels

**Files:**
- Modify: `finance/data/market_intelligence.py:2199-2920`
- Modify: `finance/data/market_event_coverage.py`
- Test: `tests/test_service_contracts.py:29064-29390`

**Interfaces:**
- Consumes Task 1 coverage persistence and Task 2 pure plan functions.
- Produces:
  - `load_known_upcoming_earnings_symbols(lookahead_days=45, **db_kwargs) -> list[str]`
  - `load_event_issuer_identity_map(symbols, **db_kwargs) -> dict[str, dict[str, str]]`
  - `collect_and_store_overview_earnings_calendar(...) -> dict[str, Any]`
  - `collect_and_store_earnings_calendar(..., symbol_scope_map=None, issuer_identity_map=None)` enrichment.

- [ ] **Step 1: Write failing hybrid orchestrator test**

```python
def test_overview_earnings_hybrid_includes_alphabet_and_updates_checkpoint(self) -> None:
    from finance.data import market_intelligence as mi

    captured: dict[str, object] = {}

    def fake_collector(**kwargs):
        captured.update(kwargs)
        symbols = list(kwargs["symbols"])
        return {
            "rows_written": 2,
            "events_found": 2,
            "symbols_requested": len(symbols),
            "symbols_processed": len(symbols),
            "symbol_diagnostics": [
                {"symbol": symbol, "status": "event_found", "reason": "ok"}
                for symbol in symbols
            ],
            "failed_symbols": [],
            "missing_symbols": [],
            "collected_at": "2026-07-23 00:00:00",
        }

    checkpoints: list[dict[str, object]] = []
    result = mi.collect_and_store_overview_earnings_calendar(
        portfolio_symbols=["GOOGL"],
        watchlist_symbols=["GOOG"],
        major_cap_loader=lambda: [{"symbol": "AAPL"}, {"symbol": "GOOG"}, {"symbol": "GOOGL"}],
        sp500_loader=lambda: [{"symbol": "GOOG"}, {"symbol": "GOOGL"], {"symbol": "MSFT"}],
        known_events_loader=lambda: ["NVDA"],
        checkpoint_loader=lambda _key: None,
        checkpoint_writer=lambda row: checkpoints.append(row) or 1,
        collector=fake_collector,
        shard_size=100,
    )

    self.assertIn("GOOG", captured["symbols"])
    self.assertIn("GOOGL", captured["symbols"])
    self.assertEqual(len(captured["symbols"]), len(set(captured["symbols"])))
    self.assertEqual(result["coverage"]["coverage_status"], "complete")
    self.assertEqual(checkpoints[0]["coverage_key"], "earnings:sp500_cycle")
```

- [ ] **Step 2: Write failing issuer and Nasdaq time tests**

```python
def test_earnings_rows_receive_shared_issuer_identity(self) -> None:
    from finance.data import market_intelligence as mi

    captured_rows: list[dict[str, object]] = []
    with (
        patch.object(mi, "upsert_market_event_rows", side_effect=lambda rows, **_: captured_rows.extend(rows) or len(rows)),
        patch.object(mi, "mark_superseded_earnings_events", return_value=0),
        patch.object(mi, "mark_stale_earnings_estimates", return_value=0),
    ):
        mi.collect_and_store_earnings_calendar(
            symbols=["GOOG", "GOOGL"],
            max_symbols=2,
            issuer_identity_map={
                "GOOG": {"issuer_key": "sec_cik:1652044", "issuer_name": "Alphabet Inc."},
                "GOOGL": {"issuer_key": "sec_cik:1652044", "issuer_name": "Alphabet Inc."},
            },
            earnings_fetcher=lambda symbols, **_: {
                "events": [
                    {
                        "event_date": "2026-07-23",
                        "event_type": "EARNINGS",
                        "symbol": symbol,
                        "title": f"{symbol} Earnings Release",
                        "source": mi.EARNINGS_CALENDAR_SOURCE,
                    }
                    for symbol in symbols
                ],
                "symbol_diagnostics": [
                    {"symbol": symbol, "status": "event_found", "reason": "ok"}
                    for symbol in symbols
                ],
                "failed_symbols": [],
                "missing_symbols": [],
            },
        )

    self.assertEqual({row["issuer_key"] for row in captured_rows}, {"sec_cik:1652044"})
    self.assertEqual({row["issuer_name"] for row in captured_rows}, {"Alphabet Inc."})

def test_nasdaq_crosscheck_maps_after_hours_time_label(self) -> None:
    from finance.data import market_intelligence as mi

    result = mi.fetch_yfinance_earnings_calendar_events(
        ["GOOG"],
        start_date="2026-07-20",
        end_date="2026-07-25",
        validate_with_nasdaq=True,
        ticker_factory=lambda _symbol: type(
            "Ticker",
            (),
            {"calendar": {"Earnings Date": [date(2026, 7, 22)]}},
        )(),
        nasdaq_fetcher=lambda _dates: {
            "2026-07-22": {
                "symbols": ["GOOG"],
                "rows_by_symbol": {"GOOG": {"time": "After Hours"}},
                "status": "ok",
            }
        },
    )

    self.assertEqual(result["events"][0]["event_time_label"], "after_market")
```

- [ ] **Step 3: Run tests and verify RED**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.MarketIntelligenceEventCalendarContractTests.test_overview_earnings_hybrid_includes_alphabet_and_updates_checkpoint \
  tests.test_service_contracts.MarketIntelligenceEventCalendarContractTests.test_earnings_rows_receive_shared_issuer_identity \
  tests.test_service_contracts.MarketIntelligenceEventCalendarContractTests.test_nasdaq_crosscheck_maps_after_hours_time_label
```

Expected: FAIL on missing hybrid function / keyword arguments / time label.

- [ ] **Step 4: Add identity and known-event DB loaders**

Use exact date and identity boundaries:

```python
def load_known_upcoming_earnings_symbols(*, lookahead_days: int = 45, **db_kwargs: Any) -> list[str]:
    start_date = datetime.now(UTC).date()
    end_date = start_date + timedelta(days=max(1, int(lookahead_days or 45)))
    rows = load_market_event_calendar(
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat(),
        event_type="EARNINGS",
        limit=5000,
        **db_kwargs,
    )
    return _normalize_symbol_list([row.get("symbol") for row in rows], max_symbols=5000)

def load_event_issuer_identity_map(symbols: Sequence[Any], **db_kwargs: Any) -> dict[str, dict[str, str]]:
    normalized = _normalize_symbol_list(symbols, max_symbols=5000)
    if not normalized:
        return {}
    placeholders = ",".join(["%s"] * len(normalized))
    db = _db(
        db_kwargs.get("host", "localhost"),
        db_kwargs.get("user", "root"),
        db_kwargs.get("password", "1234"),
        int(db_kwargs.get("port", 3306)),
    )
    try:
        db.use_db(DB_META)
        rows = db.query(
            f"""
            SELECT symbol, related_cik, name
            FROM nyse_symbol_lifecycle
            WHERE symbol IN ({placeholders})
              AND source = %s
              AND related_cik IS NOT NULL
            """,
            [*normalized, "sec_company_tickers_exchange"],
        )
    finally:
        db.close()
    return {
        str(row["symbol"]).upper(): {
            "issuer_key": f"sec_cik:{int(row['related_cik'])}",
            "issuer_name": str(row.get("name") or row["symbol"]),
        }
        for row in rows
    }
```

- [ ] **Step 5: Extend earnings enrichment and time normalization**

Add:

```python
def _normalize_earnings_time_label(value: Any) -> str:
    text = str(value or "").strip().lower().replace("_", " ")
    if any(token in text for token in ("after hour", "after market", "amc")):
        return "after_market"
    if any(token in text for token in ("before hour", "before market", "bmo")):
        return "before_market"
    return "time_unknown"
```

`fetch_nasdaq_earnings_calendar_symbols_by_date()` must return:

```python
"rows_by_symbol": {
    str(row["symbol"]): dict(row)
    for row in result.get("rows") or []
    if row.get("symbol")
},
```

When a cross-check matches, set:

```python
nasdaq_row = dict(nasdaq_result.get("rows_by_symbol", {}).get(symbol) or {})
row["event_time_label"] = _normalize_earnings_time_label(nasdaq_row.get("time"))
```

Extend `collect_and_store_earnings_calendar()` with:

```python
symbol_scope_map: dict[str, Sequence[str]] | None = None,
issuer_identity_map: dict[str, dict[str, str]] | None = None,
```

Enrich each event:

```python
symbol = str(enriched.get("symbol") or "").strip().upper()
identity = dict((issuer_identity_map or {}).get(symbol) or {})
scopes = [str(value) for value in (symbol_scope_map or {}).get(symbol, []) if str(value)]
enriched["issuer_key"] = identity.get("issuer_key") or f"symbol:{symbol}"
enriched["issuer_name"] = identity.get("issuer_name") or symbol
enriched["universe_scope"] = scopes[0] if scopes else enriched.get("universe_scope") or universe_scope
raw_payload["coverage_scopes"] = scopes
```

- [ ] **Step 6: Implement the hybrid orchestrator**

Use dependency injection only for tests; defaults must call the canonical loaders:

```python
def collect_and_store_overview_earnings_calendar(
    *,
    portfolio_symbols: Sequence[Any] = (),
    watchlist_symbols: Sequence[Any] = (),
    lookahead_days: int = 120,
    known_event_days: int = 45,
    major_cap_limit: int = 100,
    shard_size: int = 100,
    validate_with_nasdaq: bool = True,
    major_cap_loader: Callable[[], list[dict[str, Any]]] | None = None,
    sp500_loader: Callable[[], list[dict[str, Any]]] | None = None,
    known_events_loader: Callable[[], list[str]] | None = None,
    checkpoint_loader: Callable[[str], dict[str, Any] | None] | None = None,
    checkpoint_writer: Callable[[dict[str, Any]], int] | None = None,
    collector: Callable[..., dict[str, Any]] | None = None,
) -> dict[str, Any]:
    from finance.data.market_event_coverage import (
        apply_sp500_shard_result,
        build_sp500_shard_plan,
        merge_priority_earnings_symbols,
    )

    load_major = major_cap_loader or (
        lambda: load_market_cap_universe_members("TOP1000")[:major_cap_limit]
    )
    load_sp500 = sp500_loader or (lambda: load_market_universe_members("SP500"))
    load_known = known_events_loader or (
        lambda: load_known_upcoming_earnings_symbols(lookahead_days=known_event_days)
    )
    load_checkpoint = checkpoint_loader or load_market_event_collection_coverage
    write_checkpoint = checkpoint_writer or upsert_market_event_collection_coverage
    run_collector = collector or collect_and_store_earnings_calendar

    sp500_symbols = [row.get("symbol") for row in load_sp500()]
    checkpoint = load_checkpoint("earnings:sp500_cycle")
    shard_plan = build_sp500_shard_plan(sp500_symbols, checkpoint, batch_size=shard_size)
    retry_symbols = list(dict((checkpoint or {}).get("details") or {}).get("failed_symbols") or [])
    major_cap_symbols = [row.get("symbol") for row in load_major()][:major_cap_limit]
    priority_symbols = merge_priority_earnings_symbols(
        retry_symbols=retry_symbols,
        portfolio_symbols=portfolio_symbols,
        watchlist_symbols=watchlist_symbols,
        major_cap_symbols=major_cap_symbols,
        known_event_symbols=load_known(),
    )
    target_symbols = merge_priority_earnings_symbols(
        retry_symbols=priority_symbols,
        major_cap_symbols=shard_plan["batch_symbols"],
    )
```

Build `symbol_scope_map` deterministically (`portfolio`, `watchlist`, `major_cap`, `sp500`), load identity once for `target_symbols`, run the collector, calculate `coverage = apply_sp500_shard_result(...)`, persist it, and return the collector result plus `priority_symbols`, `shard_symbols`, `target_symbols`, and `coverage`.

If `missing_streaks[symbol] >= 2`, mark only that symbol's active provider estimate rows `stale`. Never mark rows for provider-error symbols.

- [ ] **Step 7: Run Task 3 tests and the existing earnings suite**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.MarketIntelligenceEventCalendarContractTests.test_overview_earnings_hybrid_includes_alphabet_and_updates_checkpoint \
  tests.test_service_contracts.MarketIntelligenceEventCalendarContractTests.test_earnings_rows_receive_shared_issuer_identity \
  tests.test_service_contracts.MarketIntelligenceEventCalendarContractTests.test_nasdaq_crosscheck_maps_after_hours_time_label \
  tests.test_service_contracts.MarketIntelligenceEventCalendarContractTests.test_yfinance_earnings_calendar_builds_event_rows_for_window \
  tests.test_service_contracts.MarketIntelligenceEventCalendarContractTests.test_yfinance_earnings_calendar_can_cross_check_nasdaq_source \
  tests.test_service_contracts.MarketIntelligenceEventCalendarContractTests.test_collect_earnings_calendar_writes_event_rows \
  tests.test_service_contracts.MarketIntelligenceEventCalendarContractTests.test_mark_superseded_earnings_events_marks_prior_active_rows
```

Expected: 7 tests PASS.

Commit:

```bash
git add finance/data/market_event_coverage.py finance/data/market_intelligence.py tests/test_service_contracts.py
git commit -m "시장일정 혼합 실적 수집 구현"
```

---

### Task 4: Ingestion Jobs, Automation, And Official-Year Coverage

**Files:**
- Modify: `app/jobs/ingestion_jobs.py:1224-1365`
- Modify: `app/jobs/overview_actions.py:295-345`
- Modify: `app/jobs/overview_automation.py:13-24`
- Modify: `app/jobs/overview_automation.py:126-145`
- Modify: `app/jobs/overview_automation.py:263-293`
- Modify: `finance/data/market_intelligence.py:950-1010`
- Modify: `finance/data/market_intelligence.py:2161-2195`
- Test: `tests/test_service_contracts.py:6753-12100`
- Test: `tests/test_service_contracts.py:28465-29420`

**Interfaces:**
- Consumes `collect_and_store_overview_earnings_calendar()` and coverage upsert.
- Produces:
  - `run_collect_overview_earnings_calendar(...) -> JobResult`
  - Overview manual / automatic hybrid routing.
  - daily market-structure job for current and next year.
  - `fomc:<year>` and `market_holiday:<year>` coverage checkpoints.

- [ ] **Step 1: Write failing job routing tests**

```python
def test_overview_action_uses_hybrid_earnings_job(self) -> None:
    from app.jobs import overview_actions

    with patch.object(
        overview_actions,
        "run_collect_overview_earnings_calendar",
        return_value={"job_name": "collect_overview_earnings_calendar", "status": "success"},
    ) as runner:
        result = overview_actions.run_overview_earnings_calendar()

    runner.assert_called_once_with(lookahead_days=120, validate_with_nasdaq=True)
    self.assertEqual(result["job_name"], "collect_overview_earnings_calendar")

def test_overview_automation_registers_hybrid_earnings_and_market_structure(self) -> None:
    from app.jobs import overview_automation

    jobs = {spec.job_id: spec for spec in overview_automation.OVERVIEW_AUTOMATION_JOB_SPECS}
    self.assertIn("market_structure_calendar", jobs)
    self.assertIn("priority", jobs["earnings_calendar"].description.lower())
    self.assertEqual(jobs["market_structure_calendar"].cadence_minutes, 24 * 60)
```

- [ ] **Step 2: Run routing tests and verify RED**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.OverviewAutomationContractTests.test_overview_action_uses_hybrid_earnings_job \
  tests.test_service_contracts.OverviewAutomationContractTests.test_overview_automation_registers_hybrid_earnings_and_market_structure
```

Expected: FAIL because the hybrid wrapper and market-structure scheduled spec do not exist.

- [ ] **Step 3: Add the ingestion JobResult wrapper**

Implement:

```python
def run_collect_overview_earnings_calendar(
    *,
    lookahead_days: int = 120,
    validate_with_nasdaq: bool = True,
    progress_callback: Callable[[dict[str, Any]], None] | None = None,
) -> JobResult:
    job_name = "collect_overview_earnings_calendar"
    started_at = _now_str()
    t0 = perf_counter()
    try:
        _emit_stage_progress(progress_callback, event="stage_start", stage="earnings_calendar")
        result = collect_and_store_overview_earnings_calendar(
            lookahead_days=lookahead_days,
            validate_with_nasdaq=validate_with_nasdaq,
        )
        _emit_stage_progress(progress_callback, event="stage_complete", stage="earnings_calendar")
        coverage = dict(result.get("coverage") or {})
        status = "success" if coverage.get("coverage_status") == "complete" else "partial_success"
        return _build_result(
            job_name=job_name,
            status=status,
            started_at=started_at,
            finished_at=_now_str(),
            duration_sec=perf_counter() - t0,
            rows_written=int(result.get("rows_written") or 0),
            symbols_requested=int(result.get("symbols_requested") or 0),
            symbols_processed=int(result.get("symbols_processed") or 0),
            failed_symbols=list(result.get("failed_symbols") or []),
            message="Hybrid earnings coverage refresh completed.",
            details=result,
        )
    except Exception as exc:
        return _build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=_now_str(),
            duration_sec=perf_counter() - t0,
            rows_written=0,
            message=f"Hybrid earnings coverage refresh failed: {exc}",
            details={"lookahead_days": lookahead_days},
        )
```

- [ ] **Step 4: Rewire Overview manual and automatic jobs**

`run_overview_earnings_calendar()` becomes:

```python
def run_overview_earnings_calendar() -> JobResult:
    return run_collect_overview_earnings_calendar(
        lookahead_days=120,
        validate_with_nasdaq=True,
    )
```

Automation uses:

```python
def _run_earnings_calendar(_: datetime) -> JobResult:
    return run_collect_overview_earnings_calendar(
        lookahead_days=120,
        validate_with_nasdaq=True,
    )

def _run_market_structure_calendar(value: datetime) -> JobResult:
    return run_collect_market_structure_calendar(years=(value.year, value.year + 1))
```

Add a daily `ScheduledJobSpec` for `market_structure_calendar` and change the earnings description to `"Refresh daily priority earnings plus the next S&P 500 coverage shard."`.

- [ ] **Step 5: Write failing official coverage tests**

```python
def test_official_collectors_persist_year_coverage(self) -> None:
    from finance.data import market_intelligence as mi

    checkpoints: list[dict[str, object]] = []
    with (
        patch.object(mi, "upsert_market_event_rows", return_value=2),
        patch.object(mi, "upsert_market_event_collection_coverage", side_effect=lambda row, **_: checkpoints.append(row) or 1),
    ):
        mi.collect_and_store_fomc_calendar(
            years=[2026],
            fomc_fetcher=lambda **_: {
                "events": [
                    {"event_date": "2026-07-29", "event_type": "FOMC_MEETING", "title": "FOMC", "source": "fed"},
                    {"event_date": "2026-09-16", "event_type": "FOMC_MEETING", "title": "FOMC", "source": "fed"},
                ],
                "events_found": 2,
            },
        )

    self.assertEqual(checkpoints[0]["coverage_key"], "fomc:2026")
    self.assertEqual(checkpoints[0]["expected_items"], 2)
    self.assertEqual(checkpoints[0]["covered_items"], 2)
```

- [ ] **Step 6: Persist FOMC and holiday coverage per year**

After successful official event upsert:

```python
for year in target_years:
    year_rows = [row for row in events if str(row.get("event_date") or "").startswith(f"{year}-")]
    upsert_market_event_collection_coverage({
        "coverage_key": f"fomc:{year}",
        "event_family": "central_bank",
        "universe_scope": "official_macro",
        "window_start": f"{year}-01-01",
        "window_end": f"{year}-12-31",
        "expected_items": len(year_rows),
        "covered_items": len(year_rows),
        "failed_items": 0,
        "coverage_status": "complete" if year_rows else "error",
        "last_attempted_at": collected_at,
        "last_success_at": collected_at if year_rows else None,
        "details": {"event_dates": sorted(str(row["event_date"]) for row in year_rows)},
    }, host=host, user=user, password=password, port=port)
```

For market structure, use only `MARKET_HOLIDAY` and `EARLY_CLOSE` rows and keys `market_holiday:<year>`. If the Nasdaq holiday source is listed in `failed_sources`, keep the prior checkpoint and upsert a new `partial` state without deleting event rows.

- [ ] **Step 7: Run Task 4 tests and commit**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.OverviewAutomationContractTests.test_overview_action_uses_hybrid_earnings_job \
  tests.test_service_contracts.OverviewAutomationContractTests.test_overview_automation_registers_hybrid_earnings_and_market_structure \
  tests.test_service_contracts.OverviewAutomationContractTests.test_overview_action_facade_runs_events_calendar_refresh_all \
  tests.test_service_contracts.MarketIntelligenceEventCalendarContractTests.test_official_collectors_persist_year_coverage \
  tests.test_service_contracts.MarketIntelligenceEventCalendarContractTests.test_collect_fomc_calendar_writes_event_rows \
  tests.test_service_contracts.MarketIntelligenceEventCalendarContractTests.test_collect_market_structure_calendar_writes_event_rows
```

Expected: 6 tests PASS.

Commit:

```bash
git add app/jobs/ingestion_jobs.py app/jobs/overview_actions.py app/jobs/overview_automation.py finance/data/market_intelligence.py tests/test_service_contracts.py
git commit -m "시장일정 혼합 수집 자동 실행 연결"
```

---

### Task 5: Family-Aware Read Model, Issuer Display Grouping, KST Semantics, And Filter Views

**Files:**
- Modify: `app/services/overview/events.py:186-211`
- Modify: `app/services/overview/events.py:430-875`
- Modify: `app/services/overview/events.py:950-1383`
- Modify: `app/web/overview_dashboard_helpers.py:105-116`
- Test: `tests/test_service_contracts.py:16211-22190`

**Interfaces:**
- Consumes event rows with issuer identity and coverage checkpoint rows.
- Produces `events_workbench_v2`:

```text
payload
  schema_version
  filter_options
  views
    all
    central_bank
    earnings
    market_holiday
      brief
      calendar
      trust_summary
      empty_state
  coverage_summary
  command
  evidence
```

- [ ] **Step 1: Write failing issuer grouping and KST tests**

```python
def test_events_workbench_groups_alphabet_share_classes(self) -> None:
    from app.services.overview.events import build_events_workbench_payload, build_market_events_snapshot

    rows = [
        {
            "event_date": "2026-07-22",
            "event_type": "EARNINGS",
            "event_family": "earnings",
            "event_subtype": "earnings_release",
            "event_time_label": "after_market",
            "issuer_key": "sec_cik:1652044",
            "issuer_name": "Alphabet Inc.",
            "symbol": symbol,
            "title": f"{symbol} Earnings Release",
            "source": "yfinance_calendar",
            "source_type": "provider_estimate",
            "source_authority": "provider_estimate",
            "event_status": "active",
            "collected_at": "2026-07-22 00:00:00",
        }
        for symbol in ("GOOG", "GOOGL")
    ]
    snapshot = build_market_events_snapshot(
        event_type=None,
        today=date(2026, 7, 22),
        query_fn=lambda *_args: rows,
    )
    payload = build_events_workbench_payload(snapshot, today=date(2026, 7, 22))
    items = payload["views"]["earnings"]["calendar"]["days"][0]["items"]

    self.assertEqual(len(items), 1)
    self.assertEqual(items[0]["issuer_name"], "Alphabet Inc.")
    self.assertEqual(items[0]["symbols"], ["GOOG", "GOOGL"])
    self.assertEqual(items[0]["display_date"], "2026-07-23")
    self.assertEqual(items[0]["time_basis"], "한국시간 예정")

def test_unknown_earnings_time_does_not_invent_kst_date(self) -> None:
    from app.services.overview.events import _event_kst_display

    display = _event_kst_display({
        "Date": "2026-07-22",
        "Event Time": "time_unknown",
        "Event Datetime UTC": "-",
    })

    self.assertIsNone(display["display_date_kst"])
    self.assertEqual(display["label"], "미국 기준 · 한국시간 미확인")

def test_exact_utc_earnings_time_converts_to_kst(self) -> None:
    from app.services.overview.events import _event_kst_display

    display = _event_kst_display({
        "Date": "2026-07-22",
        "Event Time": "time_confirmed",
        "Event Datetime UTC": "2026-07-22T20:05:00+00:00",
    })

    self.assertEqual(display["display_date_kst"], "2026-07-23")
    self.assertEqual(display["display_time_kst"], "05:05")
    self.assertEqual(display["time_basis"], "한국시간 확정")
```

- [ ] **Step 2: Write failing priority, warning, and family-limit tests**

```python
def test_workbench_prefers_today_alphabet_over_later_fomc(self) -> None:
    from app.services.overview.events import build_events_workbench_payload, build_market_events_snapshot

    rows = [
        {
            "event_date": "2026-07-23",
            "event_type": "EARNINGS",
            "event_family": "earnings",
            "universe_scope": "major_cap",
            "symbol": "GOOG",
            "title": "Alphabet Earnings",
            "source": "yfinance_calendar",
            "source_type": "provider_estimate",
            "event_status": "active",
        },
        {
            "event_date": "2026-07-29",
            "event_type": "FOMC_MEETING",
            "event_family": "central_bank",
            "title": "FOMC Meeting",
            "source": "federal_reserve_fomc_calendar",
            "source_type": "official",
            "event_status": "active",
        },
    ]
    snapshot = build_market_events_snapshot(
        event_type=None,
        today=date(2026, 7, 23),
        query_fn=lambda *_args: rows,
    )
    payload = build_events_workbench_payload(snapshot, today=date(2026, 7, 23))

    self.assertEqual(payload["views"]["all"]["brief"]["next_event"]["title"], "Alphabet Earnings")
    self.assertEqual(payload["views"]["all"]["brief"]["next_fomc"]["title"], "FOMC Meeting")

def test_market_event_warnings_are_korean(self) -> None:
    from app.services.overview.events import _event_warnings

    warnings = _event_warnings({"stale_estimate_count": 2, "not_confirmed_count": 1})
    self.assertIn("오래된 실적 추정 일정 2개", warnings[0])
    self.assertFalse(any("row(s)" in warning for warning in warnings))

def test_overview_event_loader_uses_family_limits_not_global_200(self) -> None:
    import inspect
    from app.web import overview_dashboard_helpers

    source = inspect.getsource(overview_dashboard_helpers.load_overview_market_events_snapshot)
    self.assertIn("family_limits", source)
    self.assertNotIn("limit=200", source)

def test_events_workbench_distinguishes_incomplete_coverage_from_checked_no_event(self) -> None:
    import pandas as pd
    from app.services.overview.events import EVENT_COLUMNS, build_events_workbench_payload

    partial_snapshot = {
        "status": "NO_EVENTS",
        "rows": pd.DataFrame(columns=EVENT_COLUMNS),
        "coverage": {},
        "collection_coverage": [{
            "coverage_key": "earnings:sp500_cycle",
            "expected_items": 503,
            "covered_items": 100,
            "failed_items": 0,
            "coverage_status": "partial",
        }],
    }
    partial = build_events_workbench_payload(partial_snapshot, today=date(2026, 7, 23))
    self.assertEqual(
        partial["views"]["earnings"]["empty_state"]["status"],
        "coverage_incomplete",
    )
    self.assertIn("전체 확인 진행 중", partial["coverage_summary"]["description"])

    complete_snapshot = {
        **partial_snapshot,
        "collection_coverage": [{
            "coverage_key": "earnings:sp500_cycle",
            "expected_items": 503,
            "covered_items": 503,
            "failed_items": 0,
            "coverage_status": "complete",
        }],
    }
    complete = build_events_workbench_payload(complete_snapshot, today=date(2026, 7, 23))
    self.assertEqual(
        complete["views"]["earnings"]["empty_state"]["status"],
        "checked_no_event",
    )
```

- [ ] **Step 3: Run service tests and verify RED**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_events_workbench_groups_alphabet_share_classes \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_unknown_earnings_time_does_not_invent_kst_date \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_exact_utc_earnings_time_converts_to_kst \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_workbench_prefers_today_alphabet_over_later_fomc \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_event_warnings_are_korean \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_overview_event_loader_uses_family_limits_not_global_200 \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_events_workbench_distinguishes_incomplete_coverage_from_checked_no_event
```

Expected: FAIL because v2 views, grouping, KST helper, Korean warnings, family limits, and collection-coverage empty states do not exist.

- [ ] **Step 4: Add family-aware DB loading and coverage rows**

Change `build_market_events_snapshot()` to accept:

```python
family_limits: dict[str, int] | None = None,
```

When `event_type is None`, query each configured family independently:

```python
DEFAULT_EVENT_FAMILY_LIMITS = {
    "central_bank": 500,
    "earnings": 5000,
    "market_structure": 1000,
    "macro": 1000,
    "fixed_income": 1000,
    "other": 500,
}
```

Each query must apply `event_date >=`, `event_date <=`, `event_family =`, and `event_status <> 'superseded'` before its own `LIMIT`. Merge rows by `event_key` when available and by `(event_date, event_type, symbol, title, source)` for legacy rows.

Extend the underlying `SELECT` and row-to-record mapping with `issuer_key` and `issuer_name`. Use `COALESCE(event_status, 'active') <> 'superseded'` so legacy rows with a null status are not silently dropped.

`load_overview_market_events_snapshot()` must call:

```python
snapshot = build_market_events_snapshot(
    event_type=event_type,
    horizon_days=horizon_days,
    family_limits=DEFAULT_EVENT_FAMILY_LIMITS,
)
```

Do not pass a cross-family `limit=200`.

After building the event snapshot, load the two earnings checkpoints with the Task 1 loader and attach only their normalized rows:

```python
try:
    snapshot["collection_coverage"] = [
        row
        for key in ("earnings:priority_daily", "earnings:sp500_cycle")
        if (row := load_market_event_collection_coverage(key)) is not None
    ]
except Exception as exc:
    snapshot["collection_coverage"] = []
    snapshot["collection_coverage_error"] = str(exc)
return snapshot
```

The checkpoint load is DB evidence, not a provider call. A missing checkpoint is a valid cold-start state and must not make the event-row query fail.

- [ ] **Step 5: Add issuer grouping and KST display helpers**

Extend `EVENT_COLUMNS` with `Issuer Key`, `Issuer Name`, `Symbols`, `Relevance`, `Display Date KST`, `Display Time KST`, and `Time Basis`.

Implement:

```python
def _event_kst_display(record: dict[str, Any]) -> dict[str, Any]:
    utc_text = str(record.get("Event Datetime UTC") or "").strip()
    if utc_text and utc_text != "-":
        value = pd.Timestamp(utc_text)
        value = value.tz_localize("UTC") if value.tzinfo is None else value.tz_convert("UTC")
        value = value.tz_convert("Asia/Seoul")
        return {
            "display_date_kst": value.date().isoformat(),
            "display_time_kst": value.strftime("%H:%M"),
            "label": f"{value.strftime('%Y-%m-%d %H:%M')} KST",
            "time_basis": "한국시간 확정",
        }
    event_date = _date_value(record.get("Date"))
    time_label = str(record.get("Event Time") or "").strip().lower()
    if event_date and time_label == "after_market":
        display_date = event_date + timedelta(days=1)
        return {
            "display_date_kst": display_date.isoformat(),
            "display_time_kst": None,
            "label": f"{display_date.isoformat()} KST · 장후 예정",
            "time_basis": "한국시간 예정",
        }
    if event_date and time_label == "before_market":
        return {
            "display_date_kst": event_date.isoformat(),
            "display_time_kst": None,
            "label": f"{event_date.isoformat()} KST · 장전 예정",
            "time_basis": "한국시간 예정",
        }
    return {
        "display_date_kst": None,
        "display_time_kst": None,
        "label": "미국 기준 · 한국시간 미확인",
        "time_basis": "미국 기준",
    }
```

Group rows with:

```python
def _group_issuer_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    passthrough: list[dict[str, Any]] = []
    for record in records:
        if str(record.get("Event Family") or "") != "earnings":
            passthrough.append(record)
            continue
        issuer_key = str(record.get("Issuer Key") or f"symbol:{record.get('Symbol')}")
        grouped.setdefault(
            (issuer_key, str(record.get("Date") or ""), str(record.get("Event Subtype") or "earnings_release")),
            [],
        ).append(record)
    for rows in grouped.values():
        representative = dict(max(rows, key=lambda row: str(row.get("Collected At") or "")))
        representative["Symbols"] = sorted({
            str(row.get("Symbol"))
            for row in rows
            if row.get("Symbol") not in (None, "", "-")
        })
        representative["Title"] = (
            f"{representative.get('Issuer Name')} 실적"
            if representative.get("Issuer Name") not in (None, "", "-")
            else representative.get("Title")
        )
        passthrough.append(representative)
    return passthrough
```

- [ ] **Step 6: Build v2 filtered views in Python**

Implement a single helper:

```python
def _events_workbench_view(
    records: list[dict[str, Any]],
    *,
    filter_key: str,
    today: date,
    coverage_summary: dict[str, Any],
) -> dict[str, Any]:
    selected = [
        record
        for record in records
        if filter_key == "all" or _workbench_filter_key(record) == filter_key
    ]
    items = [_workbench_item(record) for record in selected]
    upcoming = [item for item in items if item.get("days_until") is not None and item["days_until"] >= 0]
    next_event = min(upcoming, key=_workbench_next_event_key) if upcoming else None
    next_fomc = next(
        (item for item in sorted(upcoming, key=_workbench_next_event_key) if item.get("family") == "central_bank"),
        None,
    )
    return {
        "brief": {
            "next_event": next_event,
            "next_fomc": next_fomc,
            "counts": _workbench_counts(items, today=today),
        },
        "calendar": _events_workbench_calendar(selected, today=today),
        "trust_summary": _events_workbench_trust_summary(selected),
        "empty_state": _events_workbench_empty_state(
            filter_key=filter_key,
            item_count=len(items),
            coverage_summary=coverage_summary,
        ),
    }
```

`_workbench_next_event_key()` must sort by proximity bucket first, then relevance (`FOMC`, portfolio/watchlist, major_cap, holiday, other), then source authority, datetime, and title. Exclude stale / superseded items.

Return:

```python
coverage_summary = _events_collection_coverage_summary(
    list(snapshot.get("collection_coverage") or []),
    error=str(snapshot.get("collection_coverage_error") or ""),
)
return {
    "schema_version": "events_workbench_v2",
    "filter_options": [
        {"id": "all", "label": "전체"},
        {"id": "central_bank", "label": "FOMC"},
        {"id": "earnings", "label": "실적"},
        {"id": "market_holiday", "label": "휴장·조기폐장"},
    ],
    "views": {
        key: _events_workbench_view(
            grouped_records,
            filter_key=key,
            today=today_value,
            coverage_summary=coverage_summary,
        )
        for key in ("all", "central_bank", "earnings", "market_holiday")
    },
    "coverage_summary": coverage_summary,
    # command, evidence, warnings, and taxonomy follow unchanged at the payload root.
}
```

`_events_collection_coverage_summary()` must use `earnings:sp500_cycle` for expected / covered / failed cycle totals and `earnings:priority_daily` only for last-check context. It returns:

- `complete`: `label="수집 범위 확인 완료"` and a checked-no-event empty state when the earnings view is empty.
- `partial` / `pending`: `label="수집 범위 확인 중"` and description `S&P 500 전체 확인 진행 중 · {covered}/{expected}`.
- missing checkpoint: `status="unknown"`, `label="수집 범위 확인 필요"`, and the same coverage-incomplete empty-state semantics.
- `error` / `stale`: an actionable Korean description that preserves stored events and asks for refresh / source confirmation.

For an empty earnings view, `_events_workbench_empty_state()` returns `coverage_incomplete` unless the cycle status is `complete`; only a complete cycle may return `checked_no_event`. Other filter views use their event-family rows and official coverage without treating an absent earnings checkpoint as their own failure.

Keep `command`, collapsed coverage summary, and raw evidence at payload root. Remove operational rail tabs from the primary contract.

- [ ] **Step 7: Translate warnings and label relevance**

Replace warnings with:

```python
def _event_warnings(coverage: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    stale = int(coverage.get("stale_estimate_count") or 0)
    if stale:
        warnings.append(f"오래된 실적 추정 일정 {stale}개가 있습니다. 발표일이 가까우면 다시 확인하세요.")
    unconfirmed = int(coverage.get("not_confirmed_count") or 0)
    if unconfirmed:
        warnings.append(f"교차 확인되지 않은 실적 추정 일정 {unconfirmed}개가 있습니다.")
    return warnings
```

Replace generic `Medium` with service-owned `Relevance`:

```python
def _event_relevance_label(row: dict[str, Any]) -> str:
    scope = _event_universe_scope(row)
    event_type = _normalize_event_type_value(row.get("event_type"))
    if event_type == "FOMC_MEETING":
        return "핵심"
    if scope in {"portfolio", "watchlist"}:
        return "보유·관심"
    if event_type == "EARNINGS" and scope == "major_cap":
        return "핵심"
    return "일반"
```

- [ ] **Step 8: Run Task 5 service tests and commit**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_events_workbench_groups_alphabet_share_classes \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_unknown_earnings_time_does_not_invent_kst_date \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_exact_utc_earnings_time_converts_to_kst \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_workbench_prefers_today_alphabet_over_later_fomc \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_event_warnings_are_korean \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_overview_event_loader_uses_family_limits_not_global_200 \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_events_workbench_distinguishes_incomplete_coverage_from_checked_no_event \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_events_workbench_payload_groups_brief_trust_calendar_and_evidence \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_events_workbench_near_term_uses_calendar_week_not_rolling_seven_days
```

Expected: 9 tests PASS after updating the two prior v1 expectations to the explicit v2 contract.

Commit:

```bash
git add app/services/overview/events.py app/web/overview_dashboard_helpers.py tests/test_service_contracts.py
git commit -m "시장일정 필터별 읽기 모델 재구성"
```

---

### Task 6: React A · Brief + Calendar Layout

**Files:**
- Modify: `app/web/streamlit_components/events_workbench/src/EventsWorkbench.tsx:1-1040`
- Modify: `app/web/streamlit_components/events_workbench/src/style.css:1-900`
- Modify: `app/web/overview/events_helpers.py:260-520`
- Test: `tests/test_service_contracts.py:6753-8690`

**Interfaces:**
- Consumes `events_workbench_v2.filter_options`, `events_workbench_v2.views`, root `coverage_summary`, `command`, and `evidence`.
- Produces family-filter selection, three-item brief, two-column calendar / selected-day detail, filtered density, collapsed trust / coverage / evidence.
- Emits only existing Python action ids with a nonce.

- [ ] **Step 1: Write failing React source contract**

```python
def test_events_react_renders_a_layout_from_service_views(self) -> None:
    from pathlib import Path

    source = Path(
        "app/web/streamlit_components/events_workbench/src/EventsWorkbench.tsx"
    ).read_text(encoding="utf-8")

    self.assertIn('payload.schema_version === "events_workbench_v2"', source)
    self.assertIn("const activeView = payload.views?.[familyFilter]", source)
    self.assertIn("가장 중요한 다음 일정", source)
    self.assertIn("다음 FOMC", source)
    self.assertIn("events-workbench__calendar-layout", source)
    self.assertIn("events-workbench__selected-day", source)
    self.assertIn("events-workbench__support-details", source)
    self.assertNotIn("events-workbench__rail-tabs", source)
    self.assertNotIn("weekMatchesFilter", source)
```

- [ ] **Step 2: Run the React contract and verify RED**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.OverviewAutomationContractTests.test_events_react_renders_a_layout_from_service_views
```

Expected: FAIL because the component still renders v1 rail / trust / command sections and locally filters pre-aggregated density.

- [ ] **Step 3: Replace payload types and view selection**

Define:

```typescript
type EventsView = {
  brief?: {
    next_event?: EventItem | null;
    next_fomc?: EventItem | null;
    counts?: Record<string, number>;
  };
  calendar?: {
    today?: string;
    current_week_start?: string;
    current_week_end?: string;
    weekday_labels?: string[];
    days?: CalendarDay[];
    density?: DensityBucket[];
  };
  trust_summary?: {
    official_count?: number;
    estimate_count?: number;
    unconfirmed_count?: number;
    warnings?: string[];
  };
  empty_state?: {
    status?: "has_events" | "coverage_incomplete" | "checked_no_event";
    label?: string;
    description?: string;
  };
};

type EventsPayload = {
  schema_version?: string;
  status?: string;
  filter_options?: EventFilterOption[];
  views?: Record<string, EventsView>;
  coverage_summary?: {
    status?: string;
    label?: string;
    description?: string;
    expected_items?: number;
    covered_items?: number;
    failed_items?: number;
  };
  command?: {
    actions?: EventAction[];
    last_results?: CommandResult[];
  };
  evidence?: EvidencePayload;
};
```

At component start:

```typescript
const payload = ((args || {}).payload || {}) as EventsPayload;
const [familyFilter, setFamilyFilter] = useState("all");
const activeView = payload.views?.[familyFilter] || payload.views?.all || {};
const brief = activeView.brief || {};
const calendar = activeView.calendar || { days: [], density: [] };
const calendarDays = calendar.days || [];
const calendarDensity = calendar.density || [];
const filterOptions = payload.filter_options || [
  { id: "all", label: "전체" },
  { id: "central_bank", label: "FOMC" },
  { id: "earnings", label: "실적" },
  { id: "market_holiday", label: "휴장·조기폐장" },
];
const isPayloadReady = payload.schema_version === "events_workbench_v2";
```

Delete local review filter, rail filtering, `weekMatchesFilter`, and density bucket filtering. The active service view is the single source for hero, calendar, selected date, density, and trust counts.

- [ ] **Step 4: Render the approved three-part brief and one refresh action**

Use:

```tsx
<header className="events-workbench__hero">
  <div>
    <span className="events-workbench__eyebrow">시장 일정</span>
    <h2>이번 주 시장 일정</h2>
    <p>한국시간 기준 · 공식 일정과 실적 추정을 구분합니다.</p>
  </div>
  <button
    className="events-workbench__refresh"
    onClick={() => emitEvent("refresh_all")}
    type="button"
  >
    일정 갱신
  </button>
</header>

<div className="events-workbench__brief-grid">
  <BriefCard label="가장 중요한 다음 일정" item={brief.next_event} />
  <BriefCard
    label="이번 주 핵심 일정"
    value={`${valueText(brief.counts?.this_week, "0")}개`}
  />
  <BriefCard label="다음 FOMC" item={brief.next_fomc} />
</div>
```

Do not render the existing six-count strip or full command band. Put `last_results`, collection coverage, and individual refresh actions inside the support details in Step 6.

- [ ] **Step 5: Render two-column calendar, selected day, and active-view density**

Use this structure:

```tsx
<section className="events-workbench__calendar-layout">
  <div className="events-workbench__calendar-main">
    <CalendarHeader
      activeMonth={activeCalendarMonth}
      eventCount={calendarMonthEventCount}
      eventDays={calendarMonthEventDays.length}
      onMove={moveCalendarMonth}
    />
    <div className="events-workbench__month-grid">
      {/* existing weekday and 42-day button rendering */}
    </div>
    <DensityChart buckets={calendarDensity} />
  </div>
  <aside className="events-workbench__selected-day">
    {selectedCalendarDay ? (
      <>
        <h3>{selectedCalendarDay.date}</h3>
        <div className="events-workbench__selected-day-list">
          {(selectedCalendarDay.items || []).map((item) => (
            <EventCard
              item={item}
              key={`${selectedCalendarDay.date}-${item.issuer_key || item.symbol || item.title}`}
            />
          ))}
        </div>
      </>
    ) : (
      <p>{activeView.empty_state?.description || "날짜를 선택하면 해당 날짜의 중요 일정과 출처를 확인할 수 있습니다."}</p>
    )}
  </aside>
</section>
```

On family filter change, clear `selectedDate` only when the selected day does not exist in the new active view.

- [ ] **Step 6: Move trust, coverage, refresh evidence, and raw rows into support details**

```tsx
<details className="events-workbench__support-details">
  <summary>자료 신뢰와 수집 범위</summary>
  <div className="events-workbench__support-grid">
    <div>
      <strong>{payload.coverage_summary?.label || "수집 범위"}</strong>
      <p>{payload.coverage_summary?.description}</p>
    </div>
    <div>
      <strong>공식 {valueText(activeView.trust_summary?.official_count, "0")}개</strong>
      <span>추정 {valueText(activeView.trust_summary?.estimate_count, "0")}개</span>
    </div>
  </div>
  {(activeView.trust_summary?.warnings || []).map((warning) => (
    <p className="events-workbench__warning" key={warning}>{warning}</p>
  ))}
  <div className="events-workbench__secondary-actions">
    {(payload.command?.actions || [])
      .filter((action) => action.id !== "refresh_all")
      .map((action) => (
        <button key={action.id} onClick={() => emitEvent(action.id)} type="button">
          {action.label}
        </button>
      ))}
  </div>
  {/* existing last-results and raw evidence rows, collapsed under this details */}
</details>
```

This is a support area, not a new run/status panel. It must follow the calendar, not precede it.

- [ ] **Step 7: Replace CSS with A-layout desktop and mobile geometry**

Keep the existing component class prefix and palette. Required geometry:

```css
.events-workbench__brief-grid {
  display: grid;
  gap: 10px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  margin-top: 12px;
}

.events-workbench__calendar-layout {
  display: grid;
  gap: 16px;
  grid-template-columns: minmax(0, 1.7fr) minmax(18rem, 0.8fr);
  margin-top: 14px;
}

.events-workbench__selected-day {
  min-width: 0;
}

.events-workbench__selected-day-list {
  display: grid;
  gap: 8px;
  max-height: 42rem;
  overflow-y: auto;
}

.events-workbench__support-details {
  margin-top: 14px;
}

@media (max-width: 760px) {
  .events-workbench__brief-grid,
  .events-workbench__calendar-layout {
    grid-template-columns: 1fr;
  }

  .events-workbench__filtergroup > div {
    flex-wrap: wrap;
  }
}
```

Delete CSS used only by `.events-workbench__rail*`, the six-count grid, and the primary trust grid after the TSX references are removed.

- [ ] **Step 8: Build React and run focused contracts**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.OverviewAutomationContractTests.test_events_react_renders_a_layout_from_service_views \
  tests.test_service_contracts.OverviewAutomationContractTests.test_events_react_refresh_actions_are_python_dispatched

cd app/web/streamlit_components/events_workbench
npm install
npm run build
cd -
rm -rf app/web/streamlit_components/events_workbench/node_modules
```

Expected: 2 tests PASS, Vite build exits 0, and only the exact generated `events_workbench/node_modules` directory is removed. Keep source, lockfile, and `component_static` assets consistent with repository policy.

Commit:

```bash
git add \
  app/web/streamlit_components/events_workbench/src/EventsWorkbench.tsx \
  app/web/streamlit_components/events_workbench/src/style.css \
  app/web/streamlit_components/events_workbench/package-lock.json \
  app/web/streamlit_components/events_workbench/component_static \
  app/web/overview/events_helpers.py \
  tests/test_service_contracts.py
git commit -m "시장일정 캘린더 중심 React 화면 개편"
```

---

### Task 7: End-To-End Verification, Browser QA, And Durable Documentation

**Files:**
- Modify: `.aiworkspace/note/finance/docs/PROJECT_MAP.md:113`
- Modify: `.aiworkspace/note/finance/docs/architecture/DATA_DB_PIPELINE_FLOW.md:51-58`
- Modify: `.aiworkspace/note/finance/docs/runbooks/OVERVIEW_MARKET_INTELLIGENCE.md:250-430`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-events-ux-redesign/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-events-ux-redesign/NOTES.md`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-events-ux-redesign/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-events-ux-redesign/RISKS.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`

**Interfaces:**
- Consumes all prior tasks.
- Produces verified DB / service / React behavior, one generated QA screenshot, durable docs, and final coherent commit.

- [ ] **Step 1: Run focused and broad Python tests**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.MarketIntelligenceEventCalendarContractTests \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests \
  tests.test_service_contracts.OverviewAutomationContractTests
```

Expected: all three classes PASS. Existing non-failing Streamlit runtime or third-party deprecation warnings may remain, but no test failure is acceptable.

- [ ] **Step 2: Run compile and React build verification**

Run:

```bash
.venv/bin/python -m py_compile \
  finance/data/market_event_coverage.py \
  finance/data/market_intelligence.py \
  finance/data/db/schema.py \
  app/jobs/ingestion_jobs.py \
  app/jobs/overview_actions.py \
  app/jobs/overview_automation.py \
  app/services/overview/events.py \
  app/web/overview_dashboard_helpers.py \
  app/web/overview/events_helpers.py \
  tests/test_service_contracts.py

cd app/web/streamlit_components/events_workbench
npm install
npm run build
cd -
rm -rf app/web/streamlit_components/events_workbench/node_modules
```

Expected: compile exits 0, Vite build exits 0, and the exact generated `events_workbench/node_modules` directory is removed.

- [ ] **Step 3: Run DB schema and read-model smoke checks**

Run:

```bash
.venv/bin/python - <<'PY'
from finance.data.market_intelligence import (
    load_market_event_collection_coverage,
    sync_market_intelligence_tables,
)
from app.services.overview.events import build_events_workbench_payload

sync_market_intelligence_tables()
payload = build_events_workbench_payload(today=None, horizon_days=540)
assert payload["schema_version"] == "events_workbench_v2"
assert {"all", "central_bank", "earnings", "market_holiday"} <= set(payload["views"])
print({
    "schema_version": payload["schema_version"],
    "view_counts": {
        key: value["brief"]["counts"]
        for key, value in payload["views"].items()
    },
    "sp500_coverage": load_market_event_collection_coverage("earnings:sp500_cycle"),
})
PY
```

Expected: schema sync completes, payload is v2, and the four views exist. A missing cold-start S&P 500 checkpoint is acceptable before the first hybrid collection and must appear as incomplete coverage in the UI.

- [ ] **Step 4: Run one real hybrid earnings refresh and verify Alphabet**

Run:

```bash
.venv/bin/python - <<'PY'
from app.jobs.ingestion_jobs import run_collect_overview_earnings_calendar
from finance.data.market_intelligence import (
    load_market_event_calendar,
    load_market_event_collection_coverage,
)

result = run_collect_overview_earnings_calendar(
    lookahead_days=120,
    validate_with_nasdaq=True,
)
assert result["status"] in {"success", "partial_success"}
rows = load_market_event_calendar(
    start_date="2026-07-20",
    end_date="2026-07-25",
    event_type="EARNINGS",
    limit=5000,
)
alphabet = [
    row for row in rows
    if str(row.get("symbol") or "").upper() in {"GOOG", "GOOGL"}
]
assert alphabet, "Alphabet earnings rows were not collected"
print({
    "job_status": result["status"],
    "alphabet_rows": [
        {
            "symbol": row.get("symbol"),
            "date": str(row.get("event_date")),
            "issuer_key": row.get("issuer_key"),
            "time": row.get("event_time_label"),
        }
        for row in alphabet
    ],
})
PY
```

Expected: `success` or `partial_success`, with at least one GOOG / GOOGL row. If the external provider fails, record the exact provider error in `RUNS.md`, keep the focused mocked contracts as the correctness proof, and do not claim live provider success.

- [ ] **Step 5: Verify official 2027 rows are not hidden**

Run:

```bash
.venv/bin/python - <<'PY'
from finance.data.market_intelligence import load_market_event_calendar

fomc = load_market_event_calendar(
    start_date="2027-01-01",
    end_date="2027-12-31",
    event_type="FOMC_MEETING",
    limit=5000,
)
holidays = load_market_event_calendar(
    start_date="2027-01-01",
    end_date="2027-12-31",
    limit=5000,
)
holidays = [
    row for row in holidays
    if str(row.get("event_type") or "") in {"MARKET_HOLIDAY", "EARLY_CLOSE"}
]
assert fomc, "2027 FOMC rows missing"
assert holidays, "2027 market holiday / early-close rows missing"
fomc_coverage = load_market_event_collection_coverage("fomc:2027")
holiday_coverage = load_market_event_collection_coverage("market_holiday:2027")
assert fomc_coverage and fomc_coverage["covered_items"] == fomc_coverage["expected_items"]
assert holiday_coverage and holiday_coverage["covered_items"] == holiday_coverage["expected_items"]
print({
    "fomc_2027": len(fomc),
    "holidays_2027": len(holidays),
    "fomc_coverage": fomc_coverage,
    "holiday_coverage": holiday_coverage,
})
PY
```

Expected: both counts are greater than zero after official collectors run, and each persisted year checkpoint has `covered_items == expected_items`.

- [ ] **Step 6: Perform desktop and mobile Browser QA**

Start a fresh Streamlit server on an unused port, open:

```text
http://localhost:<port>/?overview_tab=events
```

Verify in DOM and screenshot:

- `이번 주 시장 일정`
- `가장 중요한 다음 일정`
- `다음 FOMC`
- filters `전체 / FOMC / 실적 / 휴장·조기폐장`
- one two-column calendar / selected-day layout on desktop
- stacked layout at 390px
- Alphabet appears once with `GOOG · GOOGL`
- filter changes update brief, calendar, selected-day items, and density together
- `자료 신뢰와 수집 범위` is below the main calendar and collapsed initially
- no English `row(s)` warning
- no generic `Medium` relevance label
- no horizontal overflow or browser console error

Save at least one screenshot in the workspace root with a name such as `overview-events-a-layout-browser-qa.png`. Keep it untracked and attach it in the final response.

- [ ] **Step 7: Update durable docs and task logs**

Use these exact durable statements:

```markdown
- Overview Events earnings coverage uses a daily priority set (US market-cap top 100, explicit portfolio/watchlist, and known near-term earnings) plus a persisted 100-symbol S&P 500 shard.
- `finance_meta.market_event_collection_coverage` distinguishes checked-no-event from not-checked and stores retry / cycle state; it is supporting trust evidence, not a primary run-status panel.
- Events React consumes service-owned filter views so hero, calendar, selected-day detail, density, and trust counts always use the same event set.
- Raw ticker evidence remains separate, while issuer-matched GOOG / GOOGL rows render as one Alphabet display event.
```

In `STATUS.md`, mark roadmap 3/4 implementation and 4/4 verification complete only after all applicable checks pass. In `RUNS.md`, record every command and outcome. In `RISKS.md`, retain only live provider / identity gaps that remain after QA. Root logs get 3-5 summary lines and pointers to the active task.

- [ ] **Step 8: Run final hygiene and commit**

Run:

```bash
git diff --check
git status --short
```

Expected: `git diff --check` has no output. Stage only market-calendar code, tests, committed component build assets, and approved docs. Do not stage registry JSONL, saved JSONL, run history, `node_modules`, screenshots, `.superpowers/`, `.DS_Store`, or unrelated files.

Commit:

```bash
git add \
  finance/data/market_event_coverage.py \
  finance/data/market_intelligence.py \
  finance/data/db/schema.py \
  app/jobs/ingestion_jobs.py \
  app/jobs/overview_actions.py \
  app/jobs/overview_automation.py \
  app/services/overview/events.py \
  app/web/overview_dashboard_helpers.py \
  app/web/overview/events_helpers.py \
  app/web/streamlit_components/events_workbench/src/EventsWorkbench.tsx \
  app/web/streamlit_components/events_workbench/src/style.css \
  app/web/streamlit_components/events_workbench/package-lock.json \
  app/web/streamlit_components/events_workbench/component_static \
  tests/test_service_contracts.py \
  .aiworkspace/note/finance/docs/PROJECT_MAP.md \
  .aiworkspace/note/finance/docs/architecture/DATA_DB_PIPELINE_FLOW.md \
  .aiworkspace/note/finance/docs/runbooks/OVERVIEW_MARKET_INTELLIGENCE.md \
  .aiworkspace/note/finance/tasks/active/overview-events-ux-redesign/STATUS.md \
  .aiworkspace/note/finance/tasks/active/overview-events-ux-redesign/NOTES.md \
  .aiworkspace/note/finance/tasks/active/overview-events-ux-redesign/RUNS.md \
  .aiworkspace/note/finance/tasks/active/overview-events-ux-redesign/RISKS.md \
  .aiworkspace/note/finance/WORK_PROGRESS.md \
  .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md

git commit -m "시장일정 수집과 캘린더 개편 완료"
```

Expected: final commit succeeds without generated or unrelated artifacts.
