# Futures Macro On-Demand Daily Finalization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 한국시간 오전 7시 이후 `일봉 갱신` 한 번으로 다음 저녁 세션 가격을 섞지 않은 직전 완료 미국 선물 세션을 17개 core symbol 전체에 즉시 확정하고 Futures Macro 기준일에 반영한다.

**Architecture:** 기존 `1d/yfinance` row의 raw OHLCV는 계속 갱신하되, 직전 완료 세션의 exact `18:00 ET <= bar < 17:00 ET` 5분봉 집계를 additive `final_*` columns에 원자적으로 저장한다. 공용 daily loader와 completed-session resolver는 유효한 explicit final 값을 우선 사용하고, 수동 refresh facade는 pending session일 때만 bounded `2d/5m` 수집·DB 재조회·17/17 확정·snapshot materialization을 한 번의 action 안에서 순서대로 실행한다.

**Tech Stack:** Python 3.12, Streamlit action facade, pandas, yfinance, PyMySQL/MySQL, `zoneinfo`, pytest, React Futures Macro workbench Browser QA

## Global Constraints

- Finalization basis는 정확히 `yfinance_5m_session_aggregate_v1`을 사용한다.
- `FUTURES_DAILY_SESSION_VERSION`은 정확히 `futures_daily_session_v3`으로 올린다.
- `PATTERN_ALGORITHM_VERSION`은 정확히 `pattern_outlook_v7_same_state_nested_hybrid_session_aggregate`로 올린다.
- pending session `D`의 집계 구간은 `D-1 18:00:00 ET` 이상, `D 17:00:00 ET` 미만이다.
- `ZoneInfo("America/New_York")`로 EDT/EST를 계산하고 UTC offset을 하드코딩하지 않는다.
- 17개 `DEFAULT_CORE_FUTURES_SYMBOLS`가 모두 complete일 때만 한 transaction으로 final columns를 저장한다.
- 16/17 이하 coverage, 수집 실패, transaction 실패에서는 final row를 한 건도 부분 저장하지 않는다.
- 일반 `1d` UPSERT는 `final_*`, `finalization_basis`, `final_source_ref`, `finalized_at`을 갱신하지 않는다.
- raw `2d/5m` row를 먼저 `finance_price.futures_ohlcv`에 저장하고, aggregate는 provider frame이 아니라 저장된 DB row를 다시 읽어 계산한다.
- schema sync 전 read는 `NULL AS final_*` legacy projection으로 한 번 fallback한다.
- explicit final이 없는 기존 history의 date/settlement-gap 판정은 그대로 유지한다.
- 새 run/job/row 진단 패널은 만들지 않는다. 성공 시 기존 기준일이 이동하고 실패 시 기존 pending 안내가 유지되는 사용자 흐름만 바꾼다.
- `다시 읽기`는 provider fetch나 materialization을 실행하지 않는다.
- raw 1d 수집이 성공하고 finalization만 실패하면 action은 `partial_success`, snapshot은 latest-good 기준일을 유지한다.
- historical forecast row와 registry/saved JSONL은 삭제하거나 재작성하지 않는다.

## File Structure

| File | Responsibility |
|---|---|
| `finance/data/db/schema.py` | `futures_ohlcv` additive finalization columns의 canonical DDL |
| `app/services/futures_macro_daily_loader.py` | final-aware daily projection과 unknown-column legacy fallback |
| `app/services/futures_macro_thermometer.py` | 공용 daily loader 사용 |
| `app/services/futures_macro_validation.py` | 공용 daily loader 사용 |
| `finance/data/futures_session_finalization.py` | ET session window, stored 5m aggregate, compact DB reads, 17/17 transactional daily final writer |
| `app/services/futures_macro_sessions.py` | explicit aggregate finality와 normalized final OHLCV 선택 |
| `app/services/futures_macro_pattern_validation.py` | 새 input semantics의 algorithm identity |
| `app/jobs/futures_macro_daily_finalization.py` | pending eligibility, 5m collection, stored-row aggregate/write orchestration |
| `app/jobs/overview_actions.py` | 기존 daily groups 뒤 finalization을 실행하고 materialization 전에 결과를 병합 |
| `tests/test_futures_macro_sessions.py` | explicit final resolver와 final-value normalization 회귀 |
| `tests/test_futures_macro_daily_loader.py` | final projection 및 legacy fallback |
| `tests/test_futures_session_finalization.py` | ET window, OHLCV aggregate, coverage gate, transaction |
| `tests/test_overview_futures_macro_refresh.py` | 같은 클릭의 pending-to-final orchestration과 failure/skip paths |
| `tests/test_futures_macro_snapshot.py` | final aggregate fingerprint stability와 version invalidation |
| `.aiworkspace/note/finance/docs/data/DB_SCHEMA_MAP.md` | additive final columns와 raw/final 의미 |
| `.aiworkspace/note/finance/docs/data/TABLE_SEMANTICS.md` | source-of-truth, idempotency, 17/17 gate |
| `.aiworkspace/note/finance/docs/data/DATA_FLOW_MAP.md` | `1d -> pending -> 5m DB -> final daily -> snapshot` 흐름 |
| `.aiworkspace/note/finance/docs/architecture/DATA_DB_PIPELINE_FLOW.md` | collector/service/snapshot 경계 |
| active task `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md` | 구현 상태, 검증 근거, 남은 위험 |

---

### Task 1: Final-Aware Daily Read And Resolver Contract

**Files:**
- Create: `app/services/futures_macro_daily_loader.py`
- Create: `finance/data/futures_session_finalization.py` (shared finalization basis constant only in this task)
- Modify: `app/services/futures_macro_thermometer.py`
- Modify: `app/services/futures_macro_validation.py`
- Modify: `app/services/futures_macro_sessions.py`
- Modify: `app/services/futures_macro_pattern_validation.py`
- Test: `tests/test_futures_macro_daily_loader.py`
- Test: `tests/test_futures_macro_sessions.py`

**Interfaces:**
- Consumes: existing `QueryFn`, `select_completed_futures_daily_rows(...)`, raw daily rows.
- Produces: `load_futures_macro_daily_rows(query_fn, *, symbols, lookback_days) -> list[dict[str, Any]]`; exact constants `FUTURES_SESSION_FINALIZATION_BASIS`, `FUTURES_DAILY_SESSION_VERSION`; resolver normalization that replaces model OHLCV with valid `final_*`.

- [ ] **Step 1: Add failing resolver tests for explicit finality and value replacement**

Append tests equivalent to:

```python
def test_explicit_session_aggregate_is_final_after_evening_reopen() -> None:
    from app.services.futures_macro_sessions import (
        FUTURES_SESSION_FINALIZATION_BASIS,
        resolve_futures_daily_session,
    )

    result = resolve_futures_daily_session(
        "ES=F",
        "2026-07-23 00:00:00",
        "2026-07-23 22:02:00",
        datetime(2026, 7, 23, 22, 2, tzinfo=timezone.utc),
        finalization_basis=FUTURES_SESSION_FINALIZATION_BASIS,
        final_close=6401.25,
    )

    assert result.status == "FINAL"
    assert result.reason == "explicit_session_aggregate"
    assert result.session_date == "2026-07-23"


def test_completed_rows_prefer_explicit_final_ohlcv() -> None:
    from app.services.futures_macro_sessions import (
        FUTURES_SESSION_FINALIZATION_BASIS,
        select_completed_futures_daily_rows,
    )

    completed = select_completed_futures_daily_rows(
        [{
            "provider_symbol": "ES=F",
            "candle_time_utc": "2026-07-23 00:00:00",
            "collected_at": "2026-07-23 22:02:00",
            "open": 7000.0,
            "high": 7100.0,
            "low": 6900.0,
            "close": 7050.0,
            "adj_close": 7050.0,
            "volume": 999999.0,
            "final_open": 6300.0,
            "final_high": 6420.0,
            "final_low": 6280.0,
            "final_close": 6401.25,
            "final_adj_close": 6401.25,
            "final_volume": 123456.0,
            "finalization_basis": FUTURES_SESSION_FINALIZATION_BASIS,
        }],
        evaluation_time=datetime(2026, 7, 23, 22, 2, tzinfo=timezone.utc),
    )

    row = completed.rows[0]
    assert completed.latest_final_session == "2026-07-23"
    assert completed.pending_session is None
    assert row["session_reason"] == "explicit_session_aggregate"
    assert (row["open"], row["high"], row["low"], row["close"]) == (
        6300.0, 6420.0, 6280.0, 6401.25
    )
    assert row["adj_close"] == 6401.25
    assert row["volume"] == 123456.0
```

Also add a negative test proving the exact basis with `final_close=None`, or an unknown basis with a non-null close, remains `IN_PROGRESS`.

- [ ] **Step 2: Run the resolver tests and confirm RED**

Run:

```bash
.venv/bin/python -m pytest \
  tests/test_futures_macro_sessions.py::FuturesDailySessionResolverTests::test_explicit_session_aggregate_is_final_after_evening_reopen \
  tests/test_futures_macro_sessions.py::FuturesDailySessionResolverTests::test_completed_rows_prefer_explicit_final_ohlcv -q
```

Expected: FAIL because the new keyword arguments/constants and final-value normalization do not exist.

- [ ] **Step 3: Implement the minimal explicit-final resolver**

Create `finance/data/futures_session_finalization.py` with the single shared
constant:

```python
FUTURES_SESSION_FINALIZATION_BASIS = "yfinance_5m_session_aggregate_v1"
```

Import that constant into `app/services/futures_macro_sessions.py`, then set:

```python
FUTURES_DAILY_SESSION_VERSION = "futures_daily_session_v3"


def _valid_explicit_finalization(
    *,
    finalization_basis: object,
    final_close: object,
) -> bool:
    if str(finalization_basis or "").strip() != FUTURES_SESSION_FINALIZATION_BASIS:
        return False
    try:
        return final_close is not None and math.isfinite(float(final_close))
    except (TypeError, ValueError):
        return False
```

Extend `resolve_futures_daily_session(...)` with keyword-only
`finalization_basis: object = None` and `final_close: object = None`. After
the invalid timestamp/Saturday checks and canonical `session_date` mapping,
classify a valid explicit final as `FINAL/explicit_session_aggregate` before
the evaluation-date/gap logic.

Pass both fields from `select_completed_futures_daily_rows(...)`. When the
resolved reason is `explicit_session_aggregate`, replace each normalized
`open/high/low/close/adj_close/volume` with the corresponding non-null
`final_*`; use `final_close` as the `adj_close` fallback.

- [ ] **Step 4: Run all session tests and confirm GREEN**

Run:

```bash
.venv/bin/python -m pytest tests/test_futures_macro_sessions.py -q
```

Expected: all tests PASS, including the unchanged settlement-gap and prior-date behavior.

- [ ] **Step 5: Add failing daily-loader tests for new and legacy schemas**

Create `tests/test_futures_macro_daily_loader.py` with:

```python
from __future__ import annotations

from typing import Any


def test_daily_loader_selects_finalization_columns() -> None:
    from app.services.futures_macro_daily_loader import (
        load_futures_macro_daily_rows,
    )

    captured: list[str] = []

    def query(_database: str, sql: str, _params: list[Any]) -> list[dict[str, Any]]:
        captured.append(sql)
        return []

    load_futures_macro_daily_rows(query, symbols=("ES=F",), lookback_days=30)

    assert len(captured) == 1
    assert "final_open" in captured[0]
    assert "finalization_basis" in captured[0]
    assert "finalized_at" in captured[0]


def test_daily_loader_retries_unknown_columns_with_null_projection() -> None:
    from app.services.futures_macro_daily_loader import (
        load_futures_macro_daily_rows,
    )

    captured: list[str] = []

    def query(_database: str, sql: str, _params: list[Any]) -> list[dict[str, Any]]:
        captured.append(sql)
        if len(captured) == 1:
            raise RuntimeError("Unknown column 'final_open' in 'field list'")
        return [{"provider_symbol": "ES=F", "final_open": None}]

    rows = load_futures_macro_daily_rows(
        query,
        symbols=("ES=F",),
        lookback_days=30,
    )

    assert rows == [{"provider_symbol": "ES=F", "final_open": None}]
    assert len(captured) == 2
    assert "NULL AS final_open" in captured[1]
    assert "NULL AS finalized_at" in captured[1]


def test_daily_loader_does_not_mask_non_schema_errors() -> None:
    from app.services.futures_macro_daily_loader import (
        load_futures_macro_daily_rows,
    )

    def query(_database: str, _sql: str, _params: list[Any]) -> list[dict[str, Any]]:
        raise RuntimeError("connection refused")

    try:
        load_futures_macro_daily_rows(query, symbols=("ES=F",), lookback_days=30)
    except RuntimeError as exc:
        assert str(exc) == "connection refused"
    else:
        raise AssertionError("non-schema errors must propagate")
```

- [ ] **Step 6: Run loader tests and confirm RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_futures_macro_daily_loader.py -q
```

Expected: FAIL because `app.services.futures_macro_daily_loader` does not exist.

- [ ] **Step 7: Implement the shared final-aware loader**

Create `app/services/futures_macro_daily_loader.py` with one public function:

```python
from collections.abc import Callable, Sequence
from typing import Any

QueryFn = Callable[
    [str, str, list[Any] | None],
    list[dict[str, Any]],
]

FINAL_COLUMNS = (
    "final_open", "final_high", "final_low", "final_close",
    "final_adj_close", "final_volume", "finalization_basis",
    "final_source_ref", "finalized_at",
)


def load_futures_macro_daily_rows(
    query_fn: QueryFn,
    *,
    symbols: Sequence[str],
    lookback_days: int,
) -> list[dict[str, Any]]:
    selected = [
        str(symbol).strip().upper()
        for symbol in symbols
        if str(symbol).strip()
    ]
    if not selected:
        return []
    placeholders = ", ".join(["%s"] * len(selected))
    params: list[Any] = [
        "1d",
        *selected,
        max(1, int(lookback_days)),
    ]
    raw_projection = """
        provider_symbol, interval_code, candle_time_utc,
        open, high, low, close, adj_close, volume,
        source, provider_status, collected_at
    """
    final_projection = ", ".join(FINAL_COLUMNS)
    legacy_projection = ", ".join(
        f"NULL AS {column}" for column in FINAL_COLUMNS
    )

    def run(final_fields: str) -> list[dict[str, Any]]:
        return query_fn(
            "finance_price",
            f"""
            SELECT {raw_projection}, {final_fields}
            FROM futures_ohlcv
            WHERE interval_code = %s
              AND provider_symbol IN ({placeholders})
              AND candle_time_utc >= DATE_SUB(
                    UTC_TIMESTAMP(), INTERVAL %s DAY
                  )
            ORDER BY provider_symbol, candle_time_utc
            """,
            params,
        )

    try:
        return run(final_projection)
    except Exception as exc:
        message = str(exc).lower()
        if "unknown column" not in message or not any(
            column in message for column in FINAL_COLUMNS
        ):
            raise
        return run(legacy_projection)
```

The primary projection must select raw fields plus every `FINAL_COLUMNS`
field. Catch only exceptions whose lower-cased message contains
`"unknown column"` and one of the final column names; retry the same query
with `NULL AS <column>` aliases. Re-raise all other errors.

Replace `_load_daily_rows(...)` in `futures_macro_thermometer.py` and
`_load_validation_futures_rows(...)` in `futures_macro_validation.py` with
thin calls to this function. Preserve their current defensive behavior at
the caller boundary: normal no-row results remain `[]`, while schema fallback
is centralized and identical.

- [ ] **Step 8: Bump the pattern algorithm identity and run focused GREEN tests**

Set:

```python
PATTERN_ALGORITHM_VERSION = (
    "pattern_outlook_v7_same_state_nested_hybrid_session_aggregate"
)
```

Run:

```bash
.venv/bin/python -m pytest \
  tests/test_futures_macro_daily_loader.py \
  tests/test_futures_macro_sessions.py \
  tests/test_futures_macro_pattern_validation.py \
  tests/test_futures_macro_snapshot.py -q
```

Expected: PASS. Any assertion that intentionally pins the old version must
be updated to the exact new version; do not loosen it to a prefix match.

- [ ] **Step 9: Commit Task 1**

```bash
git add \
  app/services/futures_macro_daily_loader.py \
  finance/data/futures_session_finalization.py \
  app/services/futures_macro_thermometer.py \
  app/services/futures_macro_validation.py \
  app/services/futures_macro_sessions.py \
  app/services/futures_macro_pattern_validation.py \
  tests/test_futures_macro_daily_loader.py \
  tests/test_futures_macro_sessions.py \
  tests/test_futures_macro_pattern_validation.py \
  tests/test_futures_macro_snapshot.py
git commit -m "선물 매크로 확정 일봉 읽기 계약 추가"
```

---

### Task 2: Exact ET Session Aggregation

**Files:**
- Modify: `finance/data/futures_session_finalization.py`
- Test: `tests/test_futures_session_finalization.py`

**Interfaces:**
- Consumes: stored `5m/yfinance` rows, pending `session_date`, exact raw daily row target per symbol.
- Produces:
  - `futures_session_window_utc(session_date: str | date) -> tuple[datetime, datetime]`
  - `SessionFinalizationBatch(session_date, window_start_utc, window_end_utc, rows, missing_symbols)`
  - `build_session_finalization_batch(intraday_rows, *, session_date, daily_targets, required_symbols, finalized_at) -> SessionFinalizationBatch`

- [ ] **Step 1: Add failing exact-window and aggregation tests**

Create fixtures around the boundary:

```python
def _bar(symbol: str, timestamp: str, **values: float) -> dict[str, object]:
    return {
        "provider_symbol": symbol,
        "candle_time_utc": timestamp,
        "open": values.get("open", 100.0),
        "high": values.get("high", 101.0),
        "low": values.get("low", 99.0),
        "close": values.get("close", 100.5),
        "volume": values.get("volume", 10.0),
    }


def test_edt_window_excludes_next_evening_session() -> None:
    from finance.data.futures_session_finalization import (
        build_session_finalization_batch,
    )

    rows = [
        _bar("ES=F", "2026-07-22 21:59:59", close=1.0),
        _bar("ES=F", "2026-07-22 22:00:00", open=100.0, close=100.5),
        _bar("ES=F", "2026-07-23 20:55:00", high=110.0, low=95.0, close=108.0),
        _bar("ES=F", "2026-07-23 21:00:00", close=999.0),
        _bar("ES=F", "2026-07-23 22:00:00", close=777.0),
    ]
    batch = build_session_finalization_batch(
        rows,
        session_date="2026-07-23",
        daily_targets={"ES=F": "2026-07-23 00:00:00"},
        required_symbols=("ES=F",),
        finalized_at=datetime(2026, 7, 23, 22, 2, tzinfo=timezone.utc),
    )

    assert batch.missing_symbols == ()
    assert batch.window_start_utc.isoformat() == "2026-07-22T22:00:00+00:00"
    assert batch.window_end_utc.isoformat() == "2026-07-23T21:00:00+00:00"
    assert batch.rows[0]["final_open"] == 100.0
    assert batch.rows[0]["final_close"] == 108.0
    assert batch.rows[0]["final_high"] == 110.0
    assert batch.rows[0]["final_low"] == 95.0
```

Add:

- an EST test for a January session whose UTC boundaries differ from July;
- a volume-sum and `final_adj_close == final_close` test;
- a `16/17` equivalent fixture that returns the absent symbol in
  `missing_symbols`;
- a test that a symbol with rows but no finite close is missing;
- a test that `final_source_ref` contains `yfinance:5m`, the ET start, and
  the ET exclusive end.

- [ ] **Step 2: Run aggregation tests and confirm RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_futures_session_finalization.py -q
```

Expected: FAIL because the module and interfaces do not exist.

- [ ] **Step 3: Implement timezone-safe pure aggregation**

Create the frozen dataclass:

```python
@dataclass(frozen=True)
class SessionFinalizationBatch:
    session_date: str
    window_start_utc: datetime
    window_end_utc: datetime
    rows: tuple[dict[str, object], ...]
    missing_symbols: tuple[str, ...]

    @property
    def complete(self) -> bool:
        return not self.missing_symbols
```

Implementation requirements (reuse the Task 1 constant; do not define a
second copy):

```python
NEW_YORK = ZoneInfo("America/New_York")
```

- Convert `D-1 18:00 ET` and `D 17:00 ET` to aware UTC datetimes.
- Parse DB timestamps as UTC; naive DB `DATETIME` values are UTC.
- Filter with `start_utc <= timestamp < end_utc`.
- Sort per symbol by timestamp.
- Select first finite open, maximum finite high, minimum finite low, last
  finite close, and sum finite volume.
- Output `daily_candle_time_utc` from `daily_targets[symbol]`.
- Output `source="yfinance"`,
  `finalization_basis=FUTURES_SESSION_FINALIZATION_BASIS`,
  `final_source_ref` with the exact ET window, and UTC-naive timestamp text
  for `finalized_at`.
- Do not manufacture rows for missing symbols.

- [ ] **Step 4: Run aggregation tests and confirm GREEN**

Run:

```bash
.venv/bin/python -m pytest tests/test_futures_session_finalization.py -q
```

Expected: all pure aggregation/window tests PASS.

- [ ] **Step 5: Commit Task 2**

```bash
git add \
  finance/data/futures_session_finalization.py \
  tests/test_futures_session_finalization.py
git commit -m "선물 세션 5분봉 확정 집계 추가"
```

---

### Task 3: Additive Schema And Atomic Final Storage

**Files:**
- Modify: `finance/data/db/schema.py`
- Modify: `finance/data/futures_session_finalization.py`
- Test: `tests/test_futures_session_finalization.py`
- Test: `tests/test_service_contracts.py`

**Interfaces:**
- Consumes: `SessionFinalizationBatch` from Task 2 and canonical `futures_ohlcv` UPSERT key.
- Produces:
  - `load_latest_futures_daily_rows(symbols, *, host, user, password, port) -> list[dict[str, Any]]`
  - `load_stored_futures_intraday_rows(symbols, *, start_utc, end_utc, interval_code="5m", ...) -> list[dict[str, Any]]`
  - `write_futures_daily_finalization(batch, *, required_symbols, ...) -> int`

- [ ] **Step 1: Add failing schema and regular-UPSERT preservation tests**

In `tests/test_service_contracts.py`, assert the canonical DDL contains all
nine new columns:

```python
schema = FUTURES_MARKET_SCHEMAS["futures_ohlcv"]
for token in (
    "final_open DOUBLE NULL",
    "final_high DOUBLE NULL",
    "final_low DOUBLE NULL",
    "final_close DOUBLE NULL",
    "final_adj_close DOUBLE NULL",
    "final_volume DOUBLE NULL",
    "finalization_basis VARCHAR(64) NULL",
    "final_source_ref VARCHAR(255) NULL",
    "finalized_at TIMESTAMP NULL",
):
    assert token in schema
```

Patch `_db` with a capturing fake, call `upsert_futures_ohlcv_rows(...)`,
and assert the SQL’s `ON DUPLICATE KEY UPDATE` section contains none of:

```python
("final_open", "final_close", "finalization_basis", "finalized_at")
```

The INSERT column list must also remain raw-only so routine provider writes
cannot clear an established final.

- [ ] **Step 2: Add failing transaction tests**

Use a fake DB with `begin/commit/rollback/executemany` call recording:

```python
def test_write_finalization_commits_only_complete_required_set(monkeypatch) -> None:
    batch = _complete_batch(("ES=F", "NQ=F"))
    fake = FakeDB()
    monkeypatch.setattr(finalization, "_db", lambda *_args, **_kwargs: fake)

    written = finalization.write_futures_daily_finalization(
        batch,
        required_symbols=("ES=F", "NQ=F"),
    )

    assert written == 2
    assert fake.events == ["use_db", "sync", "begin", "executemany:2", "commit", "close"]


def test_write_finalization_rejects_incomplete_batch_without_begin(monkeypatch) -> None:
    batch = _batch_with_missing("NQ=F")
    fake = FakeDB()
    monkeypatch.setattr(finalization, "_db", lambda *_args, **_kwargs: fake)

    written = finalization.write_futures_daily_finalization(
        batch,
        required_symbols=("ES=F", "NQ=F"),
    )

    assert written == 0
    assert "begin" not in fake.events
    assert not any(event.startswith("executemany") for event in fake.events)


def test_write_finalization_rolls_back_on_update_error(monkeypatch) -> None:
    batch = _complete_batch(("ES=F", "NQ=F"))
    fake = FakeDB(fail_executemany=True)
    monkeypatch.setattr(finalization, "_db", lambda *_args, **_kwargs: fake)

    with pytest.raises(RuntimeError, match="write failed"):
        finalization.write_futures_daily_finalization(
            batch,
            required_symbols=("ES=F", "NQ=F"),
        )

    assert "rollback" in fake.events
    assert "commit" not in fake.events
```

Add query tests that enforce:

- latest daily projection includes `final_*` and `source='yfinance'`;
- stored intraday query uses `interval_code='5m'`;
- time predicates are `candle_time_utc >= start` and `< end`;
- parameter order contains every selected symbol exactly once.

- [ ] **Step 3: Run storage tests and confirm RED**

Run:

```bash
.venv/bin/python -m pytest \
  tests/test_futures_session_finalization.py \
  tests/test_service_contracts.py -q
```

Expected: focused new tests FAIL because columns and DB functions are absent.
If the full contract file is slow, use the exact new node IDs during the RED
cycle, then run the full file before commit.

- [ ] **Step 4: Add the nine nullable schema columns**

In `FUTURES_MARKET_SCHEMAS["futures_ohlcv"]`, insert after raw `volume`:

```sql
final_open DOUBLE NULL,
final_high DOUBLE NULL,
final_low DOUBLE NULL,
final_close DOUBLE NULL,
final_adj_close DOUBLE NULL,
final_volume DOUBLE NULL,
finalization_basis VARCHAR(64) NULL,
final_source_ref VARCHAR(255) NULL,
finalized_at TIMESTAMP NULL,
```

Do not add a new uniqueness key or table. Existing `sync_table_schema(...)`
must remain the additive migration mechanism.

- [ ] **Step 5: Implement compact DB readers**

In `finance/data/futures_session_finalization.py`, add `_db(...)` using
`MySQLClient`.

`load_latest_futures_daily_rows(...)` must query only the latest
`interval_code='1d'`, `source='yfinance'` row per requested symbol and select:

```text
provider_symbol, candle_time_utc, collected_at,
open, high, low, close, adj_close, volume,
final_open, final_high, final_low, final_close,
final_adj_close, final_volume,
finalization_basis, final_source_ref, finalized_at
```

Use an inner grouped `MAX(candle_time_utc)` subquery joined on
`provider_symbol/candle_time_utc`, not a full ten-year daily load.

`load_stored_futures_intraday_rows(...)` must select only requested symbols,
`interval_code='5m'`, `source='yfinance'`, and the half-open UTC range.
Both functions close the DB in `finally`.

- [ ] **Step 6: Implement the all-or-nothing writer**

Before opening a transaction:

```python
required = tuple(dict.fromkeys(normalized_required_symbols))
present = {str(row["provider_symbol"]).upper() for row in batch.rows}
if batch.missing_symbols or present != set(required) or len(batch.rows) != len(required):
    return 0
```

Then:

```python
db.use_db(DB_PRICE)
sync_table_schema(db, "futures_ohlcv", FUTURES_MARKET_SCHEMAS["futures_ohlcv"], DB_PRICE)
db.begin()
try:
    db.executemany(update_sql, list(batch.rows))
    db.commit()
except Exception:
    db.rollback()
    raise
finally:
    db.close()
```

`update_sql` must update only the nine finalization columns and must target:

```sql
WHERE provider_symbol = %(provider_symbol)s
  AND interval_code = '1d'
  AND candle_time_utc = %(daily_candle_time_utc)s
  AND source = 'yfinance'
```

After `executemany`, return `len(batch.rows)`. Do not overwrite raw OHLCV,
`collected_at`, or `source_ref`.

- [ ] **Step 7: Run storage and collector regression tests and confirm GREEN**

Run:

```bash
.venv/bin/python -m pytest \
  tests/test_futures_session_finalization.py \
  tests/test_service_contracts.py \
  tests/test_overview_futures_macro_refresh.py -q
```

Expected: PASS. In particular, existing collector normalization/fallback
tests and regular daily UPSERT behavior remain unchanged.

- [ ] **Step 8: Commit Task 3**

```bash
git add \
  finance/data/db/schema.py \
  finance/data/futures_session_finalization.py \
  tests/test_futures_session_finalization.py \
  tests/test_service_contracts.py
git commit -m "선물 확정 일봉 원자 저장 경계 추가"
```

---

### Task 4: Pending-To-Final Refresh Orchestration

**Files:**
- Create: `app/jobs/futures_macro_daily_finalization.py`
- Modify: `app/jobs/overview_actions.py`
- Test: `tests/test_overview_futures_macro_refresh.py`

**Interfaces:**
- Consumes:
  - `collect_runner(symbols, period, interval, ..., materialize_snapshot=False) -> JobResult`
  - `load_latest_futures_daily_rows(...)`
  - `load_stored_futures_intraday_rows(...)`
  - `build_session_finalization_batch(...)`
  - `write_futures_daily_finalization(...)`
- Produces:
  - `run_pending_futures_daily_finalization(*, symbols, evaluation_time, collect_runner, daily_rows_loader, intraday_rows_loader, writer) -> dict[str, Any]`
  - `run_overview_futures_daily_ohlcv(...)` that runs finalization before the existing one-time materialization.

- [ ] **Step 1: Add failing eligibility tests**

Test the pending helper with injected DB/provider boundaries:

```python
def test_refresh_after_reopen_finalizes_pending_session_before_materialization() -> None:
    from app.jobs.futures_macro_daily_finalization import (
        run_pending_futures_daily_finalization,
    )
    from finance.data.futures_market import DEFAULT_CORE_FUTURES_SYMBOLS

    events: list[str] = []
    symbols = tuple(DEFAULT_CORE_FUTURES_SYMBOLS)
    pending_rows = [
        {
            "provider_symbol": symbol,
            "candle_time_utc": "2026-07-23 00:00:00",
            "collected_at": "2026-07-23 22:02:00",
            "final_close": None,
            "finalization_basis": None,
        }
        for symbol in symbols
    ]
    stored_rows = [
        {
            "provider_symbol": symbol,
            "candle_time_utc": "2026-07-23 20:55:00",
            "open": 100.0,
            "high": 102.0,
            "low": 99.0,
            "close": 101.0,
            "volume": 10.0,
        }
        for symbol in symbols
    ]

    def collect_runner(**kwargs: Any) -> dict[str, Any]:
        events.append(f"collect:{kwargs['interval']}")
        return _collection_result(list(kwargs["symbols"]))

    def intraday_loader(**_kwargs: Any) -> list[dict[str, Any]]:
        events.append("load:5m")
        return stored_rows

    def writer(batch: Any, **_kwargs: Any) -> int:
        events.append(f"write:{len(batch.rows)}")
        return len(batch.rows)

    result = run_pending_futures_daily_finalization(
        symbols=symbols,
        evaluation_time=datetime(
            2026, 7, 23, 22, 2, tzinfo=timezone.utc
        ),
        collect_runner=collect_runner,
        daily_rows_loader=lambda _symbols: pending_rows,
        intraday_rows_loader=intraday_loader,
        writer=writer,
    )

    events.append("materialize")
    assert events == ["collect:5m", "load:5m", "write:17", "materialize"]
    assert result["session_date"] == "2026-07-23"
    assert result["status"] == "finalized"
```

Add an Overview facade ordering test with an injected
`finalization_runner` and `materialize_fn`; assert its tail is exactly
`["finalize", "materialize"]`. The existing 1d `collect_runner` event must
precede both, proving the complete order is
`1d collection -> finalization -> materialization`.

Use evaluation time `2026-07-23 22:02:00+00:00` (18:02 EDT).

Add:

- at `17:14:59 ET`, no `5m` collection and status `not_due`;
- when evaluation New York date is already `D+1`, raw prior-date finality
  uses the existing path and status `not_required`;
- when all 17 rows already have the exact basis/non-null final close, status
  `reused` and no 5m collection/write;
- when pending rows do not cover the same session for all 17 symbols, no 5m
  collection and action becomes `partial_success`;
- when 5m collection returns one failed symbol, no aggregate writer call and
  action becomes `partial_success`;
- when stored aggregate is 16/17, writer is not called and latest-good
  materialization still runs;
- when writer raises, action is `partial_success`, materialization still runs,
  and finalization detail has `status="error"` without leaking a traceback.

- [ ] **Step 2: Run orchestration tests and confirm RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_overview_futures_macro_refresh.py -q
```

Expected: FAIL because the orchestration module/injection points do not exist.

- [ ] **Step 3: Implement a compact finalization decision**

In `app/jobs/futures_macro_daily_finalization.py`, normalize evaluation time
to UTC and ET. Build per-symbol latest row resolutions using:

```python
resolve_futures_daily_session(
    symbol,
    row.get("candle_time_utc"),
    row.get("collected_at"),
    evaluation_time,
    finalization_basis=row.get("finalization_basis"),
    final_close=row.get("final_close"),
)
```

Return without collection:

- `reused` if all required symbols resolve as
  `FINAL/explicit_session_aggregate` for the same latest session;
- `not_required` if the latest candidate session precedes current ET date;
- `not_due` if current ET time is before `17:15`;
- `incomplete_daily_coverage` if the latest rows do not yield the same
  same-date pending session and raw daily target for all required symbols.

The result dict must contain only compact action evidence:

```python
{
    "status": "not_due|not_required|reused|finalized|incomplete|error",
    "session_date": "2026-07-23" or None,
    "symbols_required": 17,
    "symbols_finalized": 0 or 17,
    "missing_symbols": [],
    "reason": "stable_machine_readable_reason",
}
```

This remains job detail; do not add it as a new visible diagnostics panel.

- [ ] **Step 4: Implement DB-first intraday finalization execution**

Only for eligible pending state:

```python
intraday_result = collect_runner(
    symbols=list(required_symbols),
    period="2d",
    interval="5m",
    cadence_mode="manual_macro_daily_finalization",
    max_symbols=len(required_symbols),
    batch_size=17,
    sleep_sec=0.0,
    materialize_snapshot=False,
)
```

Require `rows_written > 0`, no failed symbols, and success status. Then:

1. Compute the exact UTC window with `futures_session_window_utc`.
2. Reload stored 5m rows from DB using that half-open window.
3. Build the batch using raw daily `candle_time_utc` targets.
4. Require `batch.complete` and exact required-symbol coverage.
5. Call the transactional writer.
6. Return `finalized` only if the writer returns exactly 17.

Catch finalization exceptions inside this helper and return `status="error"`;
do not erase the successful raw daily action.

- [ ] **Step 5: Wire the helper before materialization**

Extend `run_overview_futures_daily_ohlcv(...)` with injectable:

```python
evaluation_time: datetime | None = None
finalization_runner: Callable[..., dict[str, Any]] | None = None
```

After building the combined raw daily result and before calling
`attach_futures_macro_materialization(...)`:

```python
finalization = finalization_runner_or_default(
    symbols=selected,
    evaluation_time=evaluation_time or datetime.now(timezone.utc),
    collect_runner=collect_runner,
)
combined["details"]["daily_finalization"] = finalization
```

If finalization status is `incomplete` or `error` and raw daily status was
`success`, change the combined action to `partial_success` and append a
short user-facing failure clause to the existing message. Keep
`not_due/not_required/reused/finalized` non-error.

Call `attach_futures_macro_materialization(...)` exactly once after this
step. Its DB-only preparation will re-read the now-final-aware daily rows,
compute the new fingerprint, and advance the current snapshot in the same
click.

- [ ] **Step 6: Add fingerprint isolation regression**

In `tests/test_futures_macro_snapshot.py`, construct two raw daily inputs
whose raw `close` values differ because of next-session movement but whose
valid explicit `final_*` values are identical. Pass each through
`select_completed_futures_daily_rows(...)` and
`compute_futures_macro_input_fingerprint(...)`.

Assert:

```python
assert first_completed.rows[0]["close"] == second_completed.rows[0]["close"]
assert first_fingerprint == second_fingerprint
```

Then change `final_close` and assert the fingerprint changes. This proves
the next session cannot mutate the completed-session model input.

- [ ] **Step 7: Run focused and cross-service tests**

Run:

```bash
.venv/bin/python -m pytest \
  tests/test_overview_futures_macro_refresh.py \
  tests/test_futures_macro_sessions.py \
  tests/test_futures_macro_daily_loader.py \
  tests/test_futures_session_finalization.py \
  tests/test_futures_macro_pattern_validation.py \
  tests/test_futures_macro_snapshot.py \
  tests/test_futures_macro_v2_integration.py \
  tests/test_overview_futures_macro_short_horizon.py -q
```

Expected: all PASS. Confirm the existing test
`test_split_collection_materializes_once_after_both_groups` still observes
exactly one materialization call.

- [ ] **Step 8: Commit Task 4**

```bash
git add \
  app/jobs/futures_macro_daily_finalization.py \
  app/jobs/overview_actions.py \
  tests/test_overview_futures_macro_refresh.py \
  tests/test_futures_macro_snapshot.py
git commit -m "선물 일봉 요청형 확정 흐름 연결"
```

---

### Task 5: Real DB Verification, Browser QA, And Durable Documentation

**Files:**
- Modify: `.aiworkspace/note/finance/docs/data/DB_SCHEMA_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/data/TABLE_SEMANTICS.md`
- Modify: `.aiworkspace/note/finance/docs/data/DATA_FLOW_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/architecture/DATA_DB_PIPELINE_FLOW.md`
- Modify: active task `STATUS.md`
- Modify: active task `NOTES.md`
- Modify: active task `RUNS.md`
- Modify: active task `RISKS.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Create locally, do not commit: `futures-macro-daily-finalization-qa.png`

**Interfaces:**
- Consumes: Tasks 1–4 complete implementation and local MySQL/Streamlit app.
- Produces: evidence that schema migration, 17/17 finalization, same-click
  snapshot advancement, UI disclosure, and no-overflow behavior work against
  the real local environment.

- [ ] **Step 1: Run static and focused verification**

Run:

```bash
git diff --check
.venv/bin/python -m py_compile \
  app/services/futures_macro_daily_loader.py \
  app/services/futures_macro_sessions.py \
  app/jobs/futures_macro_daily_finalization.py \
  app/jobs/overview_actions.py \
  finance/data/futures_session_finalization.py \
  finance/data/futures_market.py \
  finance/data/db/schema.py
.venv/bin/python -m pytest \
  tests/test_futures_macro_daily_loader.py \
  tests/test_futures_macro_sessions.py \
  tests/test_futures_session_finalization.py \
  tests/test_overview_futures_macro_refresh.py \
  tests/test_futures_macro_pattern_validation.py \
  tests/test_futures_macro_snapshot.py \
  tests/test_futures_macro_v2_integration.py \
  tests/test_overview_futures_macro_short_horizon.py -q
```

Expected: `git diff --check` has no output, compilation exits 0, all selected
tests PASS.

- [ ] **Step 2: Exercise additive schema sync without destructive migration**

Run the existing futures table sync entry point, then query:

```sql
SHOW COLUMNS FROM finance_price.futures_ohlcv
WHERE Field IN (
  'final_open', 'final_high', 'final_low', 'final_close',
  'final_adj_close', 'final_volume', 'finalization_basis',
  'final_source_ref', 'finalized_at'
);
```

Expected: exactly nine rows, all nullable. Do not drop/recreate the table.
Record command and result summary in active task `RUNS.md`.

- [ ] **Step 3: Run one real daily refresh and verify stored evidence**

Use the existing Overview app action once. After it completes, query:

```sql
SELECT provider_symbol, candle_time_utc, final_close,
       finalization_basis, final_source_ref, finalized_at
FROM finance_price.futures_ohlcv
WHERE interval_code = '1d'
  AND source = 'yfinance'
  AND finalization_basis = 'yfinance_5m_session_aggregate_v1'
ORDER BY candle_time_utc DESC, provider_symbol;
```

Expected for an eligible pending day:

- latest finalized session has 17 distinct core symbols;
- every `final_close` is non-null;
- all rows share the same exact ET window in `final_source_ref`;
- no row from the next `18:00 ET` session is represented;
- `finance_meta.futures_macro_snapshot.as_of_date` equals the finalized
  session date after the same click.

If current time has naturally moved to the next New York date and the raw
prior-date path is already final, record the `not_required` result and run
the deterministic integration test for the 18:02 ET same-day case instead
of falsifying a live pending condition.

- [ ] **Step 4: Verify idempotency and raw/final separation**

Run the refresh again. Expected:

- finalization status is `reused` for an already completed 17/17 set;
- no additional 5m download/write occurs for that same session;
- final values and input fingerprint remain unchanged;
- routine raw daily UPSERT may update raw values but does not clear or change
  `final_*`.

Record the before/after counts and fingerprint in `RUNS.md`.

- [ ] **Step 5: Perform Browser QA using the Browser skill**

Open:

```text
http://localhost:8501/overview?overview_tab=futures-macro
```

Verify on desktop:

- clicking `일봉 갱신` advances hero and command-area 기준일 to the same new
  completed session when finalization succeeds;
- the prior pending banner disappears on success;
- no new raw job/row diagnostics panel appears;
- `다시 읽기` does not start a collection;
- browser console has no new errors.

Use a deterministic incomplete-coverage test fixture or injected local
test path, not production row deletion, to verify:

- 기준일 remains latest-good;
- the existing pending disclosure remains visible;
- action feedback states that completed-session finalization was incomplete.

Resize to 420px and verify no horizontal overflow or clipped action labels.
Save one representative desktop screenshot to:

```text
/Users/taeho/Project/quant-data-pipeline-worktrees/sub-dev/futures-macro-daily-finalization-qa.png
```

Do not stage the screenshot.

- [ ] **Step 6: Synchronize durable and task documentation**

Use `finance-doc-sync`.

Document:

- `futures_ohlcv` raw columns versus immutable-per-session `final_*` columns;
- exact `yfinance_5m_session_aggregate_v1` provenance;
- half-open ET session window and DST handling;
- 17/17 atomic coverage gate and rollback behavior;
- render-time DB-only rule;
- manual daily refresh trigger and idempotent reuse;
- snapshot algorithm/session version bump;
- remaining limitation that Yahoo continuous futures is not exchange-grade
  settlement data.

Update active task:

- `STATUS.md`: implementation/QA completion state;
- `NOTES.md`: why explicit final values are separate from mutable raw daily;
- `RUNS.md`: exact test, DB, and Browser QA results;
- `RISKS.md`: any live-time path not directly exercised.

Keep root handoff logs to 3–5 lines for this follow-up.

- [ ] **Step 7: Run final verification**

Run:

```bash
git status --short
git diff --check
.venv/bin/python -m pytest \
  tests/test_futures_macro_daily_loader.py \
  tests/test_futures_macro_sessions.py \
  tests/test_futures_session_finalization.py \
  tests/test_overview_futures_macro_refresh.py \
  tests/test_futures_macro_pattern_validation.py \
  tests/test_futures_macro_snapshot.py \
  tests/test_futures_macro_v2_integration.py \
  tests/test_overview_futures_macro_short_horizon.py -q
```

Expected:

- all tests PASS;
- no whitespace errors;
- only intended code/tests/docs are staged for the final commit;
- unrelated registry, research bundle, run history, `.superpowers/`, and
  existing QA images remain untouched and unstaged.

- [ ] **Step 8: Commit Task 5**

```bash
git add \
  .aiworkspace/note/finance/docs/data/DB_SCHEMA_MAP.md \
  .aiworkspace/note/finance/docs/data/TABLE_SEMANTICS.md \
  .aiworkspace/note/finance/docs/data/DATA_FLOW_MAP.md \
  .aiworkspace/note/finance/docs/architecture/DATA_DB_PIPELINE_FLOW.md \
  .aiworkspace/note/finance/tasks/active/overview-futures-macro-short-horizon-v1-20260723/STATUS.md \
  .aiworkspace/note/finance/tasks/active/overview-futures-macro-short-horizon-v1-20260723/NOTES.md \
  .aiworkspace/note/finance/tasks/active/overview-futures-macro-short-horizon-v1-20260723/RUNS.md \
  .aiworkspace/note/finance/tasks/active/overview-futures-macro-short-horizon-v1-20260723/RISKS.md \
  .aiworkspace/note/finance/WORK_PROGRESS.md \
  .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git commit -m "선물 일봉 확정 흐름 문서와 QA 정렬"
```

Do not add `futures-macro-daily-finalization-qa.png`.

---

## Completion Criteria

- 같은 뉴욕 거래일 `18:02 ET`의 수동 refresh 통합 테스트에서 기준일이
  같은 클릭 안에 pending `D`로 이동한다.
- 집계 input은 저장된 `5m` rows이고 next-session `D 18:00 ET` 이후 bar는
  model input/fingerprint에 영향을 주지 않는다.
- 17/17일 때만 atomic commit하며 16/17, collection error, transaction
  error에서는 partial final state가 없다.
- 이미 확정된 session은 추가 provider 호출 없이 재사용한다.
- 다음 뉴욕 날짜의 prior-date raw path는 불필요한 5m 수집을 하지 않는다.
- legacy schema read fallback, regular daily UPSERT final preservation,
  snapshot version invalidation이 테스트로 고정된다.
- 실제 Browser QA에서 기준일, pending disclosure, refresh/read-only
  action 경계, 420px overflow, console error를 확인하고 스크린샷 한 장을
  남긴다.
- durable docs와 active task/root handoff logs가 구현 사실과 일치한다.
