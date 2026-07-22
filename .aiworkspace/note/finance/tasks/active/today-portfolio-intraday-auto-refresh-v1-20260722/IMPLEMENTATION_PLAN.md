# Today Portfolio Intraday Auto Refresh V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Today 화면이 열린 미국 정규장 중 대표 포트폴리오의 direct stock·ETF 가격을 5분마다 비동기 수집·DB 저장하고, 장중 평가액·수익률·기여도·그래프를 로딩 화면 없이 갱신한 뒤 확정 일봉으로 안전하게 전환한다.

**Architecture:** 기존 quote-fast collector와 `finance_price.market_intraday_snapshot` UPSERT에 explicit-symbol 경계를 추가하고, process-cached single-worker coordinator가 15초 Streamlit fragment heartbeat에서 DB due-check 후 job만 제출한다. Python service가 default portfolio의 저장 item/position ledger와 최신 group-scoped quote를 합쳐 `portfolio.live` overlay를 만들며, React는 stable component key로 그 payload만 표시한다. 정규장 마감 후에는 intraday 수집을 중단하고 기존 EOD refresh를 최대 6회 bounded retry해 `nyse_price_history`의 확정 당일 종가가 확인된 뒤 overlay를 제거한다.

**Tech Stack:** Python 3.9, Streamlit fragments/cache resources, `concurrent.futures.ThreadPoolExecutor`, PyMySQL/MySQL advisory locks, pandas/Decimal, React 18, TypeScript, Vite/Vitest, unittest.

## Global Constraints

- provider collection cadence는 portfolio group별 정확히 300초이며 heartbeat는 정확히 15초다.
- quote freshness가 provider `quote_time_utc` 기준 600초를 넘으면 `STALE`로 처리한다.
- 자동 intraday job은 `calendar_quality=CONFIRMED`이고 regular-session phase가 `OPEN`일 때만 허용한다.
- 대상은 status가 `active` 또는 `data_review`인 direct `stock`·`etf` 최대 10개이며 selected strategy와 ended item은 제외한다.
- universe code는 `TODAY_` + `sha256(portfolio_group_id)[:16].upper()` 형식으로 만들고 broad market universe와 분리한다.
- provider 결과와 batch-level error는 UI 표시 전에 `market_intraday_snapshot`에 symbol별로 저장한다.
- React와 Today UI는 provider를 직접 호출하지 않고 `Ingestion -> DB -> Loader -> UI` 경계를 유지한다.
- background collection은 `ThreadPoolExecutor(max_workers=1)`와 group-scoped MySQL advisory lock을 사용한다.
- 장중 snapshot은 절대로 `nyse_price_history.close` 또는 확정 종가로 복사·재명명하지 않는다.
- scheduled close 5분 뒤부터 EOD refresh를 300초 간격, 최대 6회 시도하며 당일 확정 일봉 확인 전에는 `종가 반영 대기`로 표시한다.
- 프리마켓·애프터마켓, WebSocket/SSE 서버, broker/order 기능, selected strategy의 가상 실시간 가격은 범위 밖이다.
- high-frequency 결과를 JSONL run history에 append하지 않고 snapshot table과 in-memory compact state만 사용한다.
- full-page spinner, skeleton reset, loading overlay를 추가하지 않는다.
- 사용자의 기존 dirty worktree 파일과 generated artifact는 stage하지 않는다.

## File Responsibility Map

- `finance/data/market_intelligence.py`: bounded explicit-symbol quote collection, per-symbol error normalization, existing UPSERT reuse.
- `tests/test_service_contracts.py`: collector의 explicit symbol, group scope, replay UPSERT 입력 계약 회귀.
- `app/services/portfolio_monitoring/intraday_refresh.py`: scope/hash/session gate, DB latest-attempt loader, advisory lock, quote freshness, live valuation, EOD handoff plan.
- `tests/test_portfolio_monitoring_intraday_refresh.py`: 위 service의 pure/DB-boundary/valuation/close tests.
- `app/web/today_intraday_auto_refresh.py`: single-worker coordinator, one-future-per-group, 15초 heartbeat orchestration, EOD retry state.
- `app/web/today_page.py`: fragment boundary, default portfolio context 공급, stable Today component render.
- `app/services/today.py`: historical EOD portfolio와 `portfolio.live`의 payload composition.
- `tests/test_today_home.py`: Today schema, read-model merge, fragment/source contract 회귀.
- `app/web/streamlit_components/today_workbench/src/types.ts`: typed live payload contract.
- `app/web/streamlit_components/today_workbench/src/presentation.ts`: live/EOD presentation 선택과 copy helper.
- `app/web/streamlit_components/today_workbench/src/presentation.test.ts`: live/partial/waiting/no-overlay presentation tests.
- `app/web/streamlit_components/today_workbench/src/TodayWorkbench.tsx`: live metrics, coverage/freshness labels, stable numeric transitions.
- `app/web/streamlit_components/today_workbench/src/TodayPortfolioChart.tsx`: one dashed intraday segment and hollow live point.
- `app/web/streamlit_components/today_workbench/src/style.css`: subtle value transitions and live point styling.
- `.aiworkspace/note/finance/docs/data/TABLE_SEMANTICS.md`: intraday snapshot group scope와 EOD 비승격 경계.
- `.aiworkspace/note/finance/docs/flows/TODAY_PORTFOLIO_INTRADAY_FLOW.md`: 화면-open cadence, partial fallback, close handoff 사용자 흐름.
- `.aiworkspace/note/finance/docs/flows/README.md`: 새 Today flow의 canonical link.
- active task docs/root handoff logs: 단계 상태, 검증 근거, 남은 위험.

---

## 1/4차 — Collection, Group Scope, DB Persistence

### Task 1: Explicit Portfolio Symbol Collector

**Files:**
- Modify: `finance/data/market_intelligence.py` near `_collect_quote_snapshot_rows`, `upsert_intraday_snapshot_rows`, and `collect_and_store_market_intraday_snapshot`
- Modify: `tests/test_service_contracts.py` near existing intraday snapshot collector tests around line 27672

**Interfaces:**
- Consumes: existing `_normalize_symbol`, `_collect_quote_snapshot_rows`, `_timestamp_str`, `_utc_now`, `upsert_intraday_snapshot_rows`.
- Produces: `collect_and_store_symbol_intraday_snapshot(*, symbols: Sequence[str], universe_code: str, source_ref: str, interval: str = "5m", quote_batch_size: int = 200, host: str = "localhost", user: str = "root", password: str = "1234", port: int = 3306, quote_fetcher: Callable[..., list[dict[str, Any]]] | None = None, snapshot_time_utc: datetime | None = None, upsert: Callable[[list[dict[str, Any]]], int] | None = None, previous_close_loader: Callable[[list[str]], dict[str, float]] | None = None, alias_loader: Callable[[list[str]], dict[str, dict[str, Any]]] | None = None) -> dict[str, Any]`.
- Invariant: one attempt uses UTC minute precision so replay of the same `snapshot_time_utc` is idempotent under the existing unique key.

- [x] **Step 1: Write failing explicit-symbol and batch-error tests**

Add tests with this shape to `MarketIntradaySnapshotTests`:

```python
def test_explicit_intraday_collector_writes_only_requested_group_symbols(self):
    from finance.data import market_intelligence as mi

    stored = []
    result = mi.collect_and_store_symbol_intraday_snapshot(
        symbols=["amd", "QQQ", "AMD"],
        universe_code="TODAY_0123456789ABCDEF",
        source_ref="portfolio_group_id=group-a;provider=yahoo_quote",
        quote_fetcher=lambda symbols: [
            {"symbol": symbol, "regularMarketPrice": 100.0,
             "regularMarketPreviousClose": 99.0, "regularMarketTime": 1784741400}
            for symbol in symbols
        ],
        snapshot_time_utc=datetime(2026, 7, 22, 14, 35, 42, tzinfo=timezone.utc),
        upsert=lambda rows: stored.extend(rows) or len(rows),
        previous_close_loader=lambda symbols: {symbol: 99.0 for symbol in symbols},
        alias_loader=lambda symbols: {},
    )

    self.assertEqual(result["symbols_requested"], 2)
    self.assertEqual(result["rows_written"], 2)
    self.assertEqual({row["symbol"] for row in stored}, {"AMD", "QQQ"})
    self.assertEqual({row["universe_code"] for row in stored}, {"TODAY_0123456789ABCDEF"})
    self.assertEqual({row["source_ref"] for row in stored}, {"portfolio_group_id=group-a;provider=yahoo_quote"})
    self.assertEqual({row["snapshot_time_utc"] for row in stored}, {"2026-07-22 14:35:00"})

def test_explicit_intraday_collector_persists_error_rows_for_batch_exception(self):
    from finance.data import market_intelligence as mi

    stored = []
    result = mi.collect_and_store_symbol_intraday_snapshot(
        symbols=["AMD", "QQQ"],
        universe_code="TODAY_0123456789ABCDEF",
        source_ref="portfolio_group_id=group-a;provider=yahoo_quote",
        quote_fetcher=lambda symbols: (_ for _ in ()).throw(RuntimeError("provider down")),
        snapshot_time_utc=datetime(2026, 7, 22, 14, 35, tzinfo=timezone.utc),
        upsert=lambda rows: stored.extend(rows) or len(rows),
        previous_close_loader=lambda symbols: {},
        alias_loader=lambda symbols: {},
    )

    self.assertEqual(result["failed_symbols"], ["AMD", "QQQ"])
    self.assertEqual({row["provider_status"] for row in stored}, {"error"})
    self.assertTrue(all("provider down" in row["error_msg"] for row in stored))
```

- [x] **Step 2: Run the focused tests and confirm RED**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.MarketIntradaySnapshotTests.test_explicit_intraday_collector_writes_only_requested_group_symbols \
  tests.test_service_contracts.MarketIntradaySnapshotTests.test_explicit_intraday_collector_persists_error_rows_for_batch_exception -v
```

Expected: both tests fail because `collect_and_store_symbol_intraday_snapshot` does not exist.

- [x] **Step 3: Implement the bounded collector**

Add a public function with injectable boundaries and a private error-row normalizer:

```python
def _snapshot_minute(value: datetime | None = None) -> str:
    instant = value or _utc_now()
    if instant.tzinfo is None:
        instant = instant.replace(tzinfo=UTC)
    return _timestamp_str(instant.astimezone(UTC).replace(second=0, microsecond=0))


def _provider_error_snapshot_rows(*, symbols, universe_code, interval_code,
                                  snapshot_time, message):
    return [
        {
            "universe_code": universe_code,
            "symbol": symbol,
            "quote_symbol": symbol,
            "interval_code": interval_code,
            "snapshot_time_utc": snapshot_time,
            "quote_time_utc": None,
            "source": "yahoo_quote",
            "source_ref": f"portfolio_quote_fast:{universe_code}",
            "previous_close": None,
            "latest_price": None,
            "return_pct": None,
            "volume": None,
            "provider_status": "error",
            "error_msg": str(message)[:2000],
        }
        for symbol in symbols
    ]


def collect_and_store_symbol_intraday_snapshot(
    *, symbols, universe_code, source_ref, interval="5m", quote_batch_size=200,
    host="localhost", user="root", password="1234", port=3306,
    quote_fetcher=None, snapshot_time_utc=None, upsert=None,
    previous_close_loader=None, alias_loader=None,
):
    normalized_symbols = sorted({_normalize_symbol(value) for value in symbols if _normalize_symbol(value)})
    if not normalized_symbols or len(normalized_symbols) > 10:
        raise ValueError("Portfolio intraday symbols must contain 1 to 10 unique symbols.")
    normalized_universe = str(universe_code or "").strip().upper()
    if not re.fullmatch(r"TODAY_[0-9A-F]{16}", normalized_universe):
        raise ValueError("Portfolio intraday universe_code must use TODAY_<16 hex>.")
    if interval != "5m":
        raise ValueError("Portfolio intraday collection supports only 5m.")
    normalized_source_ref = str(source_ref or "").strip()
    if not normalized_source_ref or len(normalized_source_ref) > 255:
        raise ValueError("A compact portfolio source_ref is required.")
    snapshot_time = _snapshot_minute(snapshot_time_utc)
    load_previous = previous_close_loader or (
        lambda requested: _load_db_previous_close_map(requested, host=host, user=user, password=password, port=port)
    )
    load_aliases = alias_loader or (
        lambda requested: load_active_market_symbol_aliases(requested, host=host, user=user, password=password, port=port)
    )
    try:
        rows, failed, diagnostics = _collect_quote_snapshot_rows(
            normalized_symbols,
            universe_code=normalized_universe,
            interval_code=interval,
            snapshot_time=snapshot_time,
            quote_batch_size=quote_batch_size,
            quote_fetcher=quote_fetcher,
            previous_close_map=load_previous(normalized_symbols),
            alias_map=load_aliases(normalized_symbols),
        )
    except Exception as exc:
        rows = _provider_error_snapshot_rows(
            symbols=normalized_symbols, universe_code=normalized_universe,
            interval_code=interval, snapshot_time=snapshot_time, message=exc,
        )
        failed, diagnostics = normalized_symbols, {"quote_batch_error": str(exc)}
    for row in rows:
        row["source_ref"] = normalized_source_ref
    writer = upsert or (
        lambda values: upsert_intraday_snapshot_rows(values, host=host, user=user, password=password, port=port)
    )
    rows_written = writer(rows)
    return {
        "rows_written": rows_written,
        "symbols_requested": len(normalized_symbols),
        "symbols_processed": len(rows),
        "failed_symbols": failed,
        "snapshot_time_utc": snapshot_time,
        "universe_code": normalized_universe,
        "method_used": "quote_fast",
        "diagnostics": diagnostics,
    }
```

Add required `re` and `Sequence` imports without changing the existing broad-universe function.

- [x] **Step 4: Run collector tests and broad-universe regression**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.MarketIntradaySnapshotTests.test_explicit_intraday_collector_writes_only_requested_group_symbols \
  tests.test_service_contracts.MarketIntradaySnapshotTests.test_explicit_intraday_collector_persists_error_rows_for_batch_exception \
  tests.test_service_contracts.MarketIntradaySnapshotTests -v
```

Expected: new tests pass; existing SP500/TOP/NASDAQ collector tests remain green.

- [x] **Step 5: Commit Task 1**

```bash
git add finance/data/market_intelligence.py tests/test_service_contracts.py
git commit -m "기능: Today 포트폴리오 장중 시세 수집 추가"
```

### Task 2: Group Scope, Session Gate, Durable Due Check, and DB Lock

**Files:**
- Create: `app/services/portfolio_monitoring/intraday_refresh.py`
- Create: `tests/test_portfolio_monitoring_intraday_refresh.py`
- Modify: `app/services/portfolio_monitoring/__init__.py`

**Interfaces:**
- Consumes: `MonitoringItemRecord`, `MySQLClient`, Task 1 collector, `market_session_v1` mapping.
- Produces: immutable `IntradayRefreshScope`, `LatestPortfolioQuotes`; `portfolio_intraday_universe_code(group_id)`, `build_intraday_refresh_scope(group, items)`, `resolve_regular_session_state(market_session, now)`, `load_latest_portfolio_quotes(scope, now)`, `run_due_intraday_collection(scope, now)`.
- `LatestPortfolioQuotes.status` is one of `NO_ATTEMPT`, `LIVE_READY`, `LIVE_PARTIAL`, `STALE`, `FAILED`.

- [ ] **Step 1: Write failing pure boundary tests**

Create the test file with deterministic records:

```python
class TodayPortfolioIntradayScopeTests(unittest.TestCase):
    def test_scope_hash_and_eligibility_are_stable(self):
        scope = build_intraday_refresh_scope(
            PortfolioGroupRecord("group-a", "A", True),
            [_item("AMD"), _item("QQQ", kind="etf", status="data_review"),
             _item("strategy-1", source_type="selected_strategy", kind="strategy"),
             _item("OLD", status="ended")],
        )
        self.assertEqual(scope.symbols, ("AMD", "QQQ"))
        self.assertEqual(scope.universe_code, "TODAY_" + sha256(b"group-a").hexdigest()[:16].upper())

    def test_only_confirmed_open_session_is_collectible(self):
        now = datetime(2026, 7, 22, 14, 0, tzinfo=timezone.utc)
        self.assertEqual(resolve_regular_session_state(_session("CONFIRMED"), now).phase, "OPEN")
        self.assertFalse(resolve_regular_session_state(_session("LIMITED"), now).collection_allowed)
```

Add DB-boundary tests using a fake `MySQLClient` for:

- latest attempt age 299 seconds => `due=False`
- latest attempt age 300 seconds => `due=True`
- a 601-second-old `quote_time_utc` => quote excluded as stale
- `GET_LOCK(%s, 0)=0` => normal `lock_contended` skip and no collector call
- process restart equivalent => a new service instance still skips from latest DB attempt.

- [ ] **Step 2: Run tests and confirm RED**

Run:

```bash
.venv/bin/python -m unittest tests.test_portfolio_monitoring_intraday_refresh -v
```

Expected: import failure because the new service module does not exist.

- [ ] **Step 3: Implement types and pure eligibility/session functions**

Use exact contracts:

```python
INTRADAY_CADENCE_SECONDS = 300
QUOTE_STALE_SECONDS = 600
TODAY_INTRADAY_MAX_SYMBOLS = 10

@dataclass(frozen=True)
class IntradayRefreshScope:
    portfolio_group_id: str
    universe_code: str
    symbols: tuple[str, ...]
    items: tuple[MonitoringItemRecord, ...]

@dataclass(frozen=True)
class RegularSessionState:
    phase: str
    trade_date: date | None
    open_at_utc: datetime | None
    close_at_utc: datetime | None
    collection_allowed: bool

def portfolio_intraday_universe_code(portfolio_group_id: str) -> str:
    group_id = str(portfolio_group_id or "").strip()
    if not group_id:
        raise ValueError("portfolio_group_id is required.")
    return f"TODAY_{sha256(group_id.encode('utf-8')).hexdigest()[:16].upper()}"

def build_intraday_refresh_scope(group, items):
    eligible = tuple(item for item in items if item.status in {"active", "data_review"}
                     and item.source_type == "direct_security"
                     and item.instrument_kind in {"stock", "etf"}
                     and str(item.source_ref or "").strip())
    symbols = tuple(sorted({item.source_ref.strip().upper() for item in eligible}))
    if len(symbols) > TODAY_INTRADAY_MAX_SYMBOLS:
        raise ValueError("Today intraday refresh supports at most 10 symbols.")
    return IntradayRefreshScope(group.portfolio_group_id,
                                portfolio_intraday_universe_code(group.portfolio_group_id),
                                symbols, eligible)
```

`resolve_regular_session_state` must parse only the current `TRADING_DAY` row and return `OPEN` for `open_at_utc <= now < close_at_utc`; any `LIMITED`, malformed, holiday, weekend, pre-open, or closed input returns `collection_allowed=False`.

- [ ] **Step 4: Implement DB latest-attempt read and advisory lock**

Use a DB factory injection and one connection for lock ownership:

```python
@contextmanager
def portfolio_refresh_lock(db, universe_code: str):
    lock_name = f"today_intraday:{universe_code}"
    acquired = db.query("SELECT GET_LOCK(%s, 0) AS acquired", [lock_name])
    locked = bool(acquired and int(acquired[0].get("acquired") or 0) == 1)
    try:
        yield locked
    finally:
        if locked:
            db.query("SELECT RELEASE_LOCK(%s) AS released", [lock_name])
```

The latest snapshot query must join the group/interval's maximum `snapshot_time_utc`, return all requested symbols at that attempt, calculate due from `snapshot_time_utc`, and calculate freshness from each row's `quote_time_utc`. Error and missing rows remain attempt markers but not live quotes.

Inside `run_due_intraday_collection`, re-read due after acquiring the lock, then call Task 1 exactly once with `source_ref=f"portfolio_group_id={scope.portfolio_group_id};provider=yahoo_quote"`. Return compact dictionaries with status in `submitted_result`, `not_due`, `lock_contended`, `no_symbols`, or `failed`; do not append run history.

- [ ] **Step 5: Export and run tests**

Export only stable public types/functions through `portfolio_monitoring/__init__.py`, then run:

```bash
.venv/bin/python -m unittest tests.test_portfolio_monitoring_intraday_refresh -v
.venv/bin/python -m unittest tests.test_portfolio_monitoring_price_refresh -v
```

Expected: all new scope/due/lock tests and existing EOD refresh tests pass.

- [ ] **Step 6: Commit Task 2**

```bash
git add app/services/portfolio_monitoring/intraday_refresh.py \
  app/services/portfolio_monitoring/__init__.py \
  tests/test_portfolio_monitoring_intraday_refresh.py
git commit -m "기능: Today 장중 갱신 범위와 중복 방지 추가"
```

---

## 2/4차 — Non-Blocking Coordinator and Five-Minute Cadence

### Task 3: Process-Cached Single-Worker Coordinator

**Files:**
- Create: `app/web/today_intraday_auto_refresh.py`
- Modify: `tests/test_today_home.py`

**Interfaces:**
- Consumes: Task 2 `IntradayRefreshScope`, `RegularSessionState`, `run_due_intraday_collection`, latest quote loader.
- Produces: `TodayIntradayCoordinator.tick(*, scope, session, now) -> CoordinatorSnapshot`, `get_today_intraday_coordinator() -> TodayIntradayCoordinator`.
- Invariant: `tick` never calls `Future.result()` on a running future and never submits a second future for the same group.

- [ ] **Step 1: Write failing coordinator tests with a controlled executor**

Add tests asserting:

```python
def test_tick_submits_due_open_job_without_waiting(self):
    executor = RecordingExecutor()
    coordinator = TodayIntradayCoordinator(executor=executor, quote_runner=lambda **kwargs: {"status": "success"})
    result = coordinator.tick(scope=_scope(), session=_open_session(), now=NOW)
    self.assertEqual(result.collection_state, "running")
    self.assertEqual(executor.submit_count, 1)
    self.assertEqual(executor.future.result_call_count, 0)

def test_tick_keeps_one_inflight_job_per_group(self):
    executor = RecordingExecutor(done=False)
    coordinator = TodayIntradayCoordinator(executor=executor, quote_runner=lambda **kwargs: {})
    coordinator.tick(scope=_scope(), session=_open_session(), now=NOW)
    coordinator.tick(scope=_scope(), session=_open_session(), now=NOW + timedelta(seconds=15))
    self.assertEqual(executor.submit_count, 1)

def test_closed_or_limited_session_never_submits_intraday_job(self):
    executor = RecordingExecutor()
    coordinator = TodayIntradayCoordinator(executor=executor)
    coordinator.tick(scope=_scope(), session=_closed_session(), now=NOW)
    coordinator.tick(scope=_scope(), session=_limited_session(), now=NOW)
    self.assertEqual(executor.submit_count, 0)
```

- [ ] **Step 2: Run coordinator tests and confirm RED**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_today_home.TodayIntradayCoordinatorTests -v
```

Expected: failure because `app.web.today_intraday_auto_refresh` is missing.

- [ ] **Step 3: Implement the coordinator state machine**

Use one executor and per-group future map:

```python
@dataclass(frozen=True)
class CoordinatorSnapshot:
    collection_state: str
    last_result: Mapping[str, Any] | None
    eod_state: str
    eod_attempt_count: int

class TodayIntradayCoordinator:
    def __init__(self, *, executor=None, quote_runner=run_due_intraday_collection,
                 eod_runner=run_portfolio_price_refresh):
        self._executor = executor or ThreadPoolExecutor(max_workers=1, thread_name_prefix="today-intraday")
        self._quote_runner = quote_runner
        self._eod_runner = eod_runner
        self._futures = {}
        self._last_results = {}
        self._eod_attempts = {}

    def tick(self, *, scope, session, now):
        future = self._futures.get(scope.portfolio_group_id)
        if future is not None and future.done():
            try:
                self._last_results[scope.portfolio_group_id] = future.result()
            except Exception as exc:
                self._last_results[scope.portfolio_group_id] = {"status": "failed", "message": str(exc)}
            self._futures.pop(scope.portfolio_group_id, None)
            future = None
        if session.collection_allowed and scope.symbols and future is None:
            self._futures[scope.portfolio_group_id] = self._executor.submit(
                self._quote_runner, scope=scope, now=now
            )
            future = self._futures[scope.portfolio_group_id]
        return CoordinatorSnapshot(
            collection_state="running" if future is not None else "idle",
            last_result=self._last_results.get(scope.portfolio_group_id),
            eod_state="not_applicable", eod_attempt_count=0,
        )
```

Do not add a process daemon, sleep loop, or JSONL writer.

- [ ] **Step 4: Add the Streamlit cache resource boundary**

```python
@st.cache_resource
def get_today_intraday_coordinator() -> TodayIntradayCoordinator:
    return TodayIntradayCoordinator()
```

Keep Streamlit imports in the web module; the service in Task 2 stays Streamlit-free.

- [ ] **Step 5: Run coordinator tests**

```bash
.venv/bin/python -m unittest tests.test_today_home.TodayIntradayCoordinatorTests -v
```

Expected: all coordinator tests pass and no test blocks on an unfinished future.

- [ ] **Step 6: Commit Task 3**

```bash
git add app/web/today_intraday_auto_refresh.py tests/test_today_home.py
git commit -m "기능: Today 장중 비동기 갱신 코디네이터 추가"
```

### Task 4: 15-Second Fragment Integration and Default Portfolio Context

**Files:**
- Modify: `app/web/today_page.py`
- Modify: `app/web/final_selected_portfolio_dashboard.py`
- Modify: `tests/test_today_home.py`

**Interfaces:**
- Consumes: existing default-workspace runtime, Task 2 scope/session functions, Task 3 coordinator.
- Produces: `TodayPortfolioRuntimeContext`, `load_default_portfolio_monitoring_context_for_today(...)`, and `_render_today_dynamic_fragment()` decorated with `@st.fragment(run_every=15)`.
- `render_today_page()` remains the public page entry and delegates one stable component render to the fragment.

- [ ] **Step 1: Write failing context and fragment source-contract tests**

Add tests that verify:

```python
def test_today_runtime_context_uses_default_group_without_creating_it(self):
    context = load_default_portfolio_monitoring_context_for_today(
        repository=FakeRepository(default_group=GROUP, items=ITEMS),
        workspace_loader=lambda: WORKSPACE,
    )
    self.assertEqual(context.group, GROUP)
    self.assertEqual(context.items, tuple(ITEMS))
    self.assertIs(context.workspace, WORKSPACE)

def test_today_page_uses_15_second_fragment_and_stable_component_key(self):
    source = Path("app/web/today_page.py").read_text(encoding="utf-8")
    self.assertIn("@st.fragment(run_every=15)", source)
    self.assertIn('key="today_workbench"', source)
    self.assertNotIn("st.spinner", source)
```

Patch the coordinator in a page test and assert one `tick` per fragment call, then assert the component receives the last DB-backed model immediately while the future remains running.

- [ ] **Step 2: Run focused tests and confirm RED**

```bash
.venv/bin/python -m unittest \
  tests.test_today_home.TodayHomePageContractTests.test_today_runtime_context_uses_default_group_without_creating_it \
  tests.test_today_home.TodayHomePageContractTests.test_today_page_uses_15_second_fragment_and_stable_component_key -v
```

Expected: missing context loader and fragment assertion failures.

- [ ] **Step 3: Expose a read-only default context loader**

In `final_selected_portfolio_dashboard.py`, introduce a small dataclass and injectable loader:

```python
@dataclass(frozen=True)
class TodayPortfolioRuntimeContext:
    group: PortfolioGroupRecord | None
    items: tuple[MonitoringItemRecord, ...]
    workspace: dict[str, Any]

def load_default_portfolio_monitoring_context_for_today(*, repository=None, workspace_loader=None):
    repo = repository or MySQLMonitoringRepository(_monitoring_db_factory)
    workspace = (workspace_loader or load_default_portfolio_monitoring_workspace_for_today)()
    groups = repo.list_groups(include_deleted=False)
    group = next((row for row in groups if row.is_default), None)
    items = tuple(repo.list_items(group.portfolio_group_id)) if group is not None else ()
    return TodayPortfolioRuntimeContext(group=group, items=items, workspace=workspace)
```

This is read-only: it must not call `insert_group`, `insert_item`, or command handlers.

- [ ] **Step 4: Move Today component render into the heartbeat fragment**

Refactor loading so one heartbeat timestamp is shared by calendar/session/context:

```python
@st.fragment(run_every=15)
def _render_today_dynamic_fragment() -> None:
    generated_at = datetime.now(timezone.utc)
    context = _safe_load(
        load_default_portfolio_monitoring_context_for_today,
        label="대표 포트폴리오",
    )
    model = load_today_read_model(
        generated_at=generated_at,
        portfolio_workspace=context.workspace,
    )
    scope, session = build_today_refresh_inputs(context, model["market_session"], generated_at)
    coordinator = get_today_intraday_coordinator()
    coordinator.tick(scope=scope, session=session, now=generated_at)
    component_value = render_today_workbench(model, key="today_workbench")
    _handle_today_component_value(component_value, model)

def render_today_page() -> None:
    _render_today_dynamic_fragment()
```

Give `load_today_read_model` optional `generated_at` and `portfolio_workspace` keyword arguments so the fragment does not reload the same workspace. Split existing event handling into `_handle_today_component_value` without changing its allowlist or navigation semantics. Keep fallback render inside the fragment and do not call `st.rerun()` for quote completion. Task 4 intentionally renders the unchanged EOD projection; Task 6 connects the DB-backed live overlay after Task 5 supplies its valuation function.

- [ ] **Step 5: Run Today page tests**

```bash
.venv/bin/python -m unittest tests.test_today_home.TodayHomePageContractTests -v
```

Expected: fragment, stable key, fallback, read-only, and navigation tests pass.

- [ ] **Step 6: Commit Task 4**

```bash
git add app/web/today_page.py app/web/final_selected_portfolio_dashboard.py tests/test_today_home.py
git commit -m "기능: Today 15초 장중 갱신 흐름 연결"
```

---

## 3/4차 — Live Valuation, Read Model, React Overlay

### Task 5: DB-Backed Live Portfolio Valuation

**Files:**
- Modify: `app/services/portfolio_monitoring/intraday_refresh.py`
- Modify: `tests/test_portfolio_monitoring_intraday_refresh.py`

**Interfaces:**
- Consumes: Task 2 latest fresh quote mapping, default workspace `active_group`, `item_details`, stored monitoring items, DB-only `load_price_history`.
- Produces: `load_workspace_eod_closes(*, workspace: Mapping[str, Any], scope: IntradayRefreshScope, price_loader: Callable[..., pd.DataFrame] = load_price_history) -> dict[str, Decimal]`; `build_live_portfolio_overlay(*, workspace: Mapping[str, Any], scope: IntradayRefreshScope, quotes: LatestPortfolioQuotes, eod_closes: Mapping[str, Decimal], now: datetime) -> dict[str, Any] | None`.
- Output keys: `status`, `as_of_utc`, `trade_date`, `coverage`, `metrics`, `contributors`, `curve_point`, `fallback_symbols`.

- [ ] **Step 1: Write failing valuation tests**

Cover these exact fixtures:

- fixed-notional AMD: 10 virtual shares, EOD close 100, EOD value 1,000, quote 105 => live value 1,050.
- fixed-share QQQ with current 5 shares and $20 accumulated dividend cash: EOD close 200, EOD value 1,020, quote 204 => live value 1,040.
- selected strategy EOD value 500 remains unchanged and is absent from coverage denominator.
- one stale direct quote falls back to its EOD value and produces `LIVE_PARTIAL`, `fresh=1`, `expected=2`.
- all quotes missing returns `None` and does not create a live chart point.
- no intraday external flow: last EOD unit value 1.10 and EOD total 1,500 to live total 1,575 => `live_daily_return=0.05`, `live_total_return=0.155`.
- same-day external flow fixture uses existing `modified_dietz_return(begin, end, flow)` with the fixed 0.5 weight.

Assert money with `Decimal` internally and `float` only in the returned JSON-safe projection.

- [ ] **Step 2: Run valuation tests and confirm RED**

```bash
.venv/bin/python -m unittest \
  tests.test_portfolio_monitoring_intraday_refresh.TodayPortfolioLiveValuationTests -v
```

Expected: missing `build_live_portfolio_overlay`.

- [ ] **Step 3: Implement terminal direct-security valuation**

Implement focused helpers:

```python
def _direct_units(item, detail):
    position = dict(detail.get("position") or {})
    if position.get("current_shares") is not None:
        return Decimal(str(position["current_shares"]))
    if item.funding_mode == "fixed_notional":
        return Decimal(str(item.input_notional)) / Decimal(str(item.entry_close))
    return Decimal(int(item.input_shares or 0))

def _live_item_value(*, item, item_row, detail, latest_close, quote_price):
    units = _direct_units(item, detail)
    eod_value = Decimal(str(item_row["current_value"]))
    eod_market_value = units * Decimal(str(latest_close))
    retained_cash = eod_value - eod_market_value
    return units * Decimal(str(quote_price)) + retained_cash
```

`load_workspace_eod_closes` reads exactly the workspace `active_group.basis_date` for `scope.symbols`; a symbol without a positive close cannot be marked fresh and falls back to EOD. Use the existing workspace's EOD values for missing/stale direct items and selected strategies. Recompute direct contribution as `live_value + gross_withdrawals - gross_contributions`; preserve existing EOD contribution for selected strategies. Build top two positive and bottom two negative contributor rows.

For the group live index, apply `modified_dietz_return` to last EOD total, live total, and same-day external flow. Never append the live point to the stored/pandas EOD curve.

- [ ] **Step 4: Run valuation and existing ledger tests**

```bash
.venv/bin/python -m unittest \
  tests.test_portfolio_monitoring_intraday_refresh.TodayPortfolioLiveValuationTests \
  tests.test_portfolio_monitoring_valuation \
  tests.test_portfolio_monitoring_position_events -v
```

Expected: live fixtures and all existing ledger/Modified Dietz tests pass.

- [ ] **Step 5: Commit Task 5**

```bash
git add app/services/portfolio_monitoring/intraday_refresh.py \
  tests/test_portfolio_monitoring_intraday_refresh.py
git commit -m "기능: Today 장중 포트폴리오 평가 계산 추가"
```

### Task 6: Today `portfolio.live` Read-Model Contract

**Files:**
- Modify: `app/services/today.py`
- Modify: `app/web/today_page.py`
- Modify: `tests/test_today_home.py`

**Interfaces:**
- Consumes: Task 5 overlay or `None`, coordinator compact state.
- Produces: `build_today_read_model(*, economic_cycle: Any, sp500: Any, futures_macro: Any, sentiment: Any, events: Any, portfolio: Any, market_calendar: Any = None, portfolio_live: Mapping[str, Any] | None = None, generated_at: datetime | None = None) -> dict[str, object]` and `portfolio.live` in `today_home_v4`.
- Historical `portfolio.metrics`, `curve`, `curve_metadata`, and `contributors` remain unchanged EOD values.

- [ ] **Step 1: Write failing schema separation tests**

```python
def _build_model(portfolio_live):
    return build_today_read_model(
        economic_cycle=READY_CYCLE,
        sp500=READY_SP500,
        futures_macro=READY_FUTURES,
        sentiment=READY_SENTIMENT,
        events=READY_EVENTS,
        portfolio=READY_PORTFOLIO,
        market_calendar=CONFIRMED_CALENDAR,
        portfolio_live=portfolio_live,
        generated_at=NOW,
    )

def test_today_read_model_keeps_eod_curve_and_adds_live_overlay(self):
    model = _build_model(LIVE_OVERLAY)
    self.assertEqual(model["schema_version"], "today_home_v4")
    self.assertFalse(model["portfolio"]["curve_metadata"]["intraday"])
    self.assertEqual(model["portfolio"]["curve"], EXPECTED_EOD_CURVE)
    self.assertEqual(model["portfolio"]["live"]["status"], "LIVE_READY")
    self.assertEqual(model["portfolio"]["live"]["curve_point"]["kind"], "intraday")

def test_today_read_model_uses_explicit_inactive_live_contract(self):
    model = _build_model(None)
    self.assertEqual(model["portfolio"]["live"]["status"], "INACTIVE")
    self.assertIsNone(model["portfolio"]["live"]["curve_point"])
```

Add partial and `EOD_WAITING` projections with Korean copy but no provider error stack/raw payload.

- [ ] **Step 2: Run read-model tests and confirm RED**

```bash
.venv/bin/python -m unittest \
  tests.test_today_home.TodayHomeReadModelTests.test_today_read_model_keeps_eod_curve_and_adds_live_overlay \
  tests.test_today_home.TodayHomeReadModelTests.test_today_read_model_uses_explicit_inactive_live_contract -v
```

Expected: schema remains v3 and `portfolio.live` is absent.

- [ ] **Step 3: Add the live projection without mutating historical fields**

Use this normalized shape for every portfolio state, including EMPTY/UNAVAILABLE:

```python
def _inactive_live_portfolio():
    return {
        "status": "INACTIVE",
        "label": "확정 종가",
        "as_of_utc": None,
        "trade_date": None,
        "coverage": {"fresh": 0, "expected": 0, "fallback_symbols": []},
        "metrics": None,
        "contributors": [],
        "curve_point": None,
        "message": "저장된 확정 종가 기준입니다.",
    }
```

Set `TODAY_SCHEMA_VERSION = "today_home_v4"`. Normalize only approved fields from the service overlay; never copy arbitrary provider diagnostics into the UI payload. Extend the Task 4 fragment after `coordinator.tick` to call `load_latest_portfolio_quotes(scope=scope, now=generated_at)` and `load_workspace_eod_closes(workspace=context.workspace, scope=scope)`, pass both results to `build_live_portfolio_overlay(workspace=context.workspace, scope=scope, quotes=quotes, eod_closes=eod_closes, now=generated_at)`, and rebuild the Today model with `portfolio_live=overlay`. Thus the first render remains EOD-only when no durable quote exists, and every displayed live value comes from DB.

- [ ] **Step 4: Run Today read-model tests**

```bash
.venv/bin/python -m unittest tests.test_today_home.TodayHomeReadModelTests -v
```

Expected: EOD regressions plus READY/PARTIAL/INACTIVE live contracts pass.

- [ ] **Step 5: Commit Task 6**

```bash
git add app/services/today.py app/web/today_page.py tests/test_today_home.py
git commit -m "기능: Today 장중 포트폴리오 계약 연결"
```

### Task 7: React Live Metrics and Dashed Chart Point

**Files:**
- Modify: `app/web/streamlit_components/today_workbench/src/types.ts`
- Modify: `app/web/streamlit_components/today_workbench/src/presentation.ts`
- Modify: `app/web/streamlit_components/today_workbench/src/presentation.test.ts`
- Modify: `app/web/streamlit_components/today_workbench/src/TodayWorkbench.tsx`
- Modify: `app/web/streamlit_components/today_workbench/src/TodayPortfolioChart.tsx`
- Modify: `app/web/streamlit_components/today_workbench/src/style.css`
- Modify generated bundle through the existing component build command: `app/web/streamlit_components/today_workbench/component_static/`

**Interfaces:**
- Consumes: Task 6 `TodayPayload.portfolio.live`.
- Produces: `displayPortfolio(payload.portfolio)` helper and optional chart `livePoint`; no Streamlit event changes.

- [ ] **Step 1: Write failing TypeScript presentation tests**

Add tests:

```typescript
it("uses live values only when a live point exists", () => {
  const result = displayPortfolio(portfolioWith({ status: "LIVE_READY", curve_point: LIVE_POINT }));
  expect(result.currentValue).toBe(1575);
  expect(result.latestReturnLabel).toBe("오늘 장중 수익률");
  expect(result.badge).toBe("장중 임시");
});

it("keeps EOD values when all quotes fail", () => {
  const result = displayPortfolio(portfolioWith({ status: "LIVE_PARTIAL", metrics: null, curve_point: null }));
  expect(result.currentValue).toBe(EOD_METRICS.current_value);
  expect(result.livePoint).toBeNull();
});

it("shows coverage for partial quotes", () => {
  const result = displayPortfolio(portfolioWith({ status: "LIVE_PARTIAL", coverage: { fresh: 9, expected: 10, fallback_symbols: ["QQQ"] } }));
  expect(result.coverageText).toBe("직접 종목 9/10개 장중 반영");
});
```

- [ ] **Step 2: Run Vitest and confirm RED**

```bash
cd app/web/streamlit_components/today_workbench
npm test -- --run
```

Expected: type/test failure because live types and `displayPortfolio` are missing.

- [ ] **Step 3: Add exact live payload types and selector**

```typescript
export type PortfolioLiveStatus = "INACTIVE" | "LIVE_READY" | "LIVE_PARTIAL" | "EOD_WAITING";
export type PortfolioLivePoint = PortfolioCurveRow & {
  timestamp_utc: string;
  kind: "intraday";
};

export type PortfolioLive = {
  status: PortfolioLiveStatus;
  label: string;
  as_of_utc: string | null;
  trade_date: string | null;
  coverage: { fresh: number; expected: number; fallback_symbols: string[] };
  metrics: TodayPayload["portfolio"]["metrics"] | null;
  contributors: TodayPayload["portfolio"]["contributors"];
  curve_point: PortfolioLivePoint | null;
  message: string;
};
```

Avoid a recursive `TodayPayload` alias by extracting `PortfolioMetrics` and `PortfolioContributor` named types first, then reference those in both historical and live contracts.

- [ ] **Step 4: Render live values and semantic labels**

In `TodayWorkbench.tsx`, select values once:

```tsx
const display = displayPortfolio(payload.portfolio);
```

Use `display.currentValue`, `display.latestObservationReturn`, `display.totalReturn`, and `display.contributors`; show:

- `장중 임시 · HH:mm ET` for READY/PARTIAL with a live point.
- `직접 종목 n/m개 장중 반영` for PARTIAL.
- `종가 반영 대기` for EOD_WAITING.
- existing `YYYY-MM-DD 종가 기준` for INACTIVE.

Add `aria-live="polite"` to the metric container and CSS transitions only on color/opacity/transform; do not introduce a loading overlay.

- [ ] **Step 5: Draw one separate live segment**

Extend chart props with `livePoint: PortfolioLivePoint | null`. Keep `rows` unchanged. Compute the EOD path from rows as before, then draw a separate path from the last EOD point to the projected live point:

```tsx
{liveCoordinates && (
  <g className="today-chart-live">
    <path d={`M${last.x},${last.y} L${liveCoordinates.x},${liveCoordinates.y}`} />
    <circle cx={liveCoordinates.x} cy={liveCoordinates.y} r={6} />
    <text x={liveCoordinates.x - 8} y={liveCoordinates.y - 12} textAnchor="end">장중 임시</text>
  </g>
)}
```

The live point participates in chart domain calculation for visibility but not `metadata.observation_count`, EOD ticks, MDD, or CAGR. Tooltip copy for the live point is `장중 임시`; EOD tooltip remains `저장 종가`.

- [ ] **Step 6: Run React tests, typecheck, and build**

```bash
cd app/web/streamlit_components/today_workbench
npm test -- --run
npm run typecheck
npm run build
```

Expected: all tests pass, TypeScript exits 0, and `component_static/index.html` plus hashed assets are regenerated.

- [ ] **Step 7: Run Python static bundle contracts**

```bash
.venv/bin/python -m unittest \
  tests.test_today_home.TodayHomePageContractTests.test_today_component_availability_requires_built_index \
  tests.test_today_home.TodayHomePageContractTests.test_today_react_source_uses_explicit_risk_labels_and_chart_semantics -v
```

Expected: both tests pass with live semantics added and historical EOD wording preserved.

- [ ] **Step 8: Commit Task 7**

```bash
git add app/web/streamlit_components/today_workbench/src \
  app/web/streamlit_components/today_workbench/component_static \
  tests/test_today_home.py
git commit -m "기능: Today 장중 수익률과 그래프 표시 추가"
```

---

## 4/4차 — Close Handoff, Regression, Browser QA, Documentation

### Task 8: Bounded EOD Close Handoff

**Files:**
- Modify: `app/services/portfolio_monitoring/intraday_refresh.py`
- Modify: `app/web/today_intraday_auto_refresh.py`
- Modify: `app/web/today_page.py`
- Modify: `tests/test_portfolio_monitoring_intraday_refresh.py`
- Modify: `tests/test_today_home.py`

**Interfaces:**
- Consumes: confirmed scheduled close, existing `run_portfolio_price_refresh(items, now=clock)`, existing EOD freshness semantics.
- Produces: `build_eod_handoff_plan(scope, session, freshness, now) -> EodHandoffPlan`; coordinator states `not_applicable`, `waiting`, `running`, `confirmed`, `exhausted`.
- Constants: grace 300 seconds, retry cadence 300 seconds, max attempts 6.

- [ ] **Step 1: Write failing close-boundary and retry tests**

Cover exact boundaries:

```python
def test_eod_handoff_starts_at_close_plus_five_minutes(self):
    inputs = {"scope": _scope(), "session": _closed_session(), "latest_daily_dates": {"AMD": PREVIOUS_DATE}}
    self.assertFalse(build_eod_handoff_plan(**inputs, now=CLOSE + timedelta(seconds=299)).due)
    self.assertTrue(build_eod_handoff_plan(**inputs, now=CLOSE + timedelta(seconds=300)).due)

def test_early_close_uses_scheduled_1300_et_boundary(self):
    plan = build_eod_handoff_plan(
        scope=_scope(), session=_early_close_session(),
        latest_daily_dates={"AMD": PREVIOUS_DATE},
        now=EARLY_CLOSE + timedelta(minutes=5),
    )
    self.assertTrue(plan.due)

def test_coordinator_retries_every_five_minutes_at_most_six_times(self):
    for attempt in range(6):
        coordinator.tick(
            scope=_scope(), session=_closed_session(),
            latest_daily_dates={"AMD": PREVIOUS_DATE},
            now=FIRST_DUE + timedelta(minutes=5 * attempt),
        )
        executor.finish_latest({"status": "failed"})
    coordinator.tick(
        scope=_scope(), session=_closed_session(),
        latest_daily_dates={"AMD": PREVIOUS_DATE},
        now=FIRST_DUE + timedelta(minutes=30),
    )
    self.assertEqual(executor.submit_count, 6)
    self.assertEqual(coordinator.snapshot(_scope().portfolio_group_id).eod_state, "exhausted")

def test_confirmed_daily_rows_remove_live_overlay(self):
    state = attach_today_live_state(
        BASE_TODAY_MODEL,
        context=READY_CONTEXT,
        coordinator_state=CONFIRMED_EOD_STATE,
        eod_freshness={"AMD": TRADE_DATE, "QQQ": TRADE_DATE},
        now=NOW,
    )
    self.assertEqual(state["portfolio"]["live"]["status"], "INACTIVE")
    self.assertIsNone(state["portfolio"]["live"]["curve_point"])
```

Also assert premarket/after-hours snapshots are never accepted as EOD confirmation and that a process restart may retry only when DB EOD freshness still says missing.

- [ ] **Step 2: Run close tests and confirm RED**

```bash
.venv/bin/python -m unittest \
  tests.test_portfolio_monitoring_intraday_refresh.TodayPortfolioEodHandoffTests \
  tests.test_today_home.TodayIntradayCoordinatorTests -v
```

Expected: missing plan/retry state failures.

- [ ] **Step 3: Implement the pure handoff plan**

```python
EOD_GRACE_SECONDS = 300
EOD_RETRY_SECONDS = 300
EOD_MAX_ATTEMPTS = 6

@dataclass(frozen=True)
class EodHandoffPlan:
    status: str
    trade_date: date | None
    missing_symbols: tuple[str, ...]
    due: bool

def build_eod_handoff_plan(*, scope, session, latest_daily_dates, now):
    if session.trade_date is None or session.close_at_utc is None:
        return EodHandoffPlan("not_applicable", None, (), False)
    missing = tuple(symbol for symbol in scope.symbols
                    if latest_daily_dates.get(symbol) != session.trade_date)
    if not missing:
        return EodHandoffPlan("confirmed", session.trade_date, (), False)
    due_at = session.close_at_utc + timedelta(seconds=EOD_GRACE_SECONDS)
    return EodHandoffPlan("waiting", session.trade_date, missing, now >= due_at)
```

- [ ] **Step 4: Extend the coordinator without mixing quote and EOD futures**

Track future kind, last EOD submission time, trade date, and attempt count by group. Reset attempts when trade date changes or EOD becomes confirmed. Submit:

```python
self._executor.submit(self._eod_runner, list(scope.items), now=now)
```

only if `plan.due`, no future is running, attempts `< 6`, and at least 300 seconds elapsed since the last EOD submission. Quote jobs remain prohibited after close. Project `EOD_WAITING` while missing, including missing-symbol count but no provider diagnostics.

- [ ] **Step 5: Run close/EOD regression tests**

```bash
.venv/bin/python -m unittest \
  tests.test_portfolio_monitoring_intraday_refresh \
  tests.test_portfolio_monitoring_price_refresh \
  tests.test_nyse_calendar \
  tests.test_today_home -v
```

Expected: all close, early-close, retry, existing EOD refresh, calendar, and Today tests pass.

- [ ] **Step 6: Commit Task 8**

```bash
git add app/services/portfolio_monitoring/intraday_refresh.py \
  app/web/today_intraday_auto_refresh.py app/web/today_page.py \
  tests/test_portfolio_monitoring_intraday_refresh.py tests/test_today_home.py
git commit -m "기능: Today 장 마감 종가 전환 추가"
```

### Task 9: Full Verification, Actual Browser QA, and Documentation Closeout

**Files:**
- Modify: `.aiworkspace/note/finance/docs/data/TABLE_SEMANTICS.md`
- Create: `.aiworkspace/note/finance/docs/flows/TODAY_PORTFOLIO_INTRADAY_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/flows/README.md`
- Modify: `.aiworkspace/note/finance/tasks/active/today-portfolio-intraday-auto-refresh-v1-20260722/PLAN.md`
- Modify: `.aiworkspace/note/finance/tasks/active/today-portfolio-intraday-auto-refresh-v1-20260722/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/today-portfolio-intraday-auto-refresh-v1-20260722/NOTES.md`
- Modify: `.aiworkspace/note/finance/tasks/active/today-portfolio-intraday-auto-refresh-v1-20260722/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/today-portfolio-intraday-auto-refresh-v1-20260722/RISKS.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Create generated, uncommitted QA screenshot: `/Users/taeho/Project/quant-data-pipeline-worktrees/main-dev/today-portfolio-intraday-auto-refresh-v1-qa.png`

**Interfaces:**
- Consumes: Tasks 1–8 complete implementation.
- Produces: verification evidence, one actual responsive Browser QA image, durable data/flow contract, roadmap 4/4 completion.

- [ ] **Step 1: Run Python focused suites**

```bash
.venv/bin/python -m unittest \
  tests.test_portfolio_monitoring_intraday_refresh \
  tests.test_portfolio_monitoring_price_refresh \
  tests.test_portfolio_monitoring_valuation \
  tests.test_portfolio_monitoring_position_events \
  tests.test_nyse_calendar \
  tests.test_today_home -v
```

Expected: all tests pass with no errors or failures.

- [ ] **Step 2: Run collector and adjacent Market Movers regression**

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.MarketIntradaySnapshotTests \
  tests.test_overview_market_movers_read_models \
  tests.test_overview_market_movers_decision_ui -v
```

Expected: broad-universe collection and Market Movers remain green; TODAY-scoped rows do not affect them.

- [ ] **Step 3: Run React verification**

```bash
cd app/web/streamlit_components/today_workbench
npm test -- --run
npm run typecheck
npm run build
```

Expected: Vitest, typecheck, and build all exit 0.

- [ ] **Step 4: Run syntax, whitespace, and changed-file checks**

```bash
.venv/bin/python -m py_compile \
  finance/data/market_intelligence.py \
  app/services/portfolio_monitoring/intraday_refresh.py \
  app/web/today_intraday_auto_refresh.py \
  app/services/today.py \
  app/web/today_page.py
git diff --check
git status --short
```

Expected: compile and diff checks exit 0. Status shows only task changes plus the pre-existing unrelated dirty/generated files; unrelated files remain unstaged.

- [ ] **Step 5: Run actual Browser QA with controlled OPEN fixtures**

Start the app using the repository's canonical Streamlit runbook. Use controlled calendar/quote fixtures or the existing local QA injection boundary so the test does not depend on the real clock. Verify at desktop, 760px, and 420px:

- initial EOD screen renders without spinner or overlay.
- OPEN state submits in background and remains interactive.
- a newly persisted quote changes metric values and adds one dashed/hollow live point without iframe reset.
- partial state shows exact fresh/expected coverage.
- browser console has 0 errors.

Capture the representative 420px or desktop state to:

```text
/Users/taeho/Project/quant-data-pipeline-worktrees/main-dev/today-portfolio-intraday-auto-refresh-v1-qa.png
```

Keep the screenshot untracked unless the user explicitly asks to commit it.

- [ ] **Step 6: Run controlled close-handoff QA**

With a confirmed early-close fixture, move the controlled clock through close −1s, close, close +299s, and close +300s. Verify quote collection stops at close, EOD is not submitted before grace, `종가 반영 대기` appears at grace, and a confirmed daily row removes the live point and restores `확정 종가` copy.

- [ ] **Step 7: Synchronize durable docs and task evidence**

Document:

- group-scoped TODAY universe key and symbol/error snapshot persistence.
- 300-second provider cadence versus 15-second DB heartbeat.
- `quote_time_utc` 600-second stale threshold and partial fallback.
- live overlay never mutates EOD curve/metrics history.
- close +5 minute EOD handoff and six-attempt bound.
- no premarket/after-hours behavior.

Set task `PLAN.md` and `STATUS.md` to `Roadmap: 4/4 implementation stages complete`, record exact commands/results in `RUNS.md`, decisions in `NOTES.md`, and only genuine remaining gaps in `RISKS.md`. Keep each root handoff log entry to 3–5 lines and point to the active task directory.

- [ ] **Step 8: Review only the intended diff**

```bash
git diff --stat
git diff -- \
  finance/data/market_intelligence.py \
  app/services/portfolio_monitoring/intraday_refresh.py \
  app/web/today_intraday_auto_refresh.py \
  app/services/today.py \
  app/web/today_page.py \
  app/web/streamlit_components/today_workbench \
  tests/test_portfolio_monitoring_intraday_refresh.py \
  tests/test_today_home.py
```

Expected: no pre-existing registry, run-history, `.superpowers`, or unrelated QA artifacts in the intended diff.

- [ ] **Step 9: Commit closeout documentation**

```bash
git add .aiworkspace/note/finance/docs \
  .aiworkspace/note/finance/tasks/active/today-portfolio-intraday-auto-refresh-v1-20260722 \
  .aiworkspace/note/finance/WORK_PROGRESS.md \
  .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git commit -m "문서: Today 장중 자동 갱신 작업 마감"
```

- [ ] **Step 10: Apply verification-before-completion**

Before reporting completion, invoke `superpowers:verification-before-completion`, re-run the exact final verification commands it requires, inspect the output rather than relying on earlier runs, and report:

- full roadmap completion (`4/4`) or the exact incomplete stage.
- test/build/browser evidence and screenshot path.
- any unavailable actual-provider or close-time verification with the reason.
- remaining uncommitted pre-existing files, explicitly separated from this feature.

## Plan Self-Review Result

- Spec coverage: collection/persistence, group hash, 5-minute cadence, 15-second heartbeat, single worker, advisory lock, stale/partial semantics, live valuation, React overlay, close handoff, early close, bounded retry, regression, Browser QA, and docs each map to Tasks 1–9.
- Placeholder scan: the plan contains no deferred implementation markers; each code-bearing step names exact functions, files, commands, and expected outcomes.
- Type consistency: `IntradayRefreshScope`, `RegularSessionState`, `CoordinatorSnapshot`, `EodHandoffPlan`, `PortfolioLive`, and `PortfolioLivePoint` are introduced before their downstream use; status strings and 300/600-second constants remain consistent across tasks.
- Scope boundary: selected strategy remains EOD-only; broad market snapshots, JSONL history, premarket/after-hours, broker/order, and persistent push servers are unchanged.
