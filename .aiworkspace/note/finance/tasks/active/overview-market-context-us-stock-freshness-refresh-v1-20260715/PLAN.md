# Overview Market Context US Stock Freshness Refresh V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 선택한 미국 개별주식의 저장 화면은 즉시 열고, 실제 최신 완료 거래일과 저장 근거가 어긋날 때만 상단의 `최신 데이터로 다시 계산` action으로 exact selected-symbol 자료를 갱신한다.

**Architecture:** 공용 NYSE 완료-session helper가 가격 기대일을 계산하고, Overview freshness service가 기존 PER/turnaround read model을 하나의 `data_freshness` 계약으로 합친다. Explicit Streamlit event만 Overview facade를 통해 canonical ingestion job을 실행하며, profile/price는 CIK 없이 먼저 보존하고 SEC statement만 identity 검증 뒤 실행한다.

**Tech Stack:** Python 3, pandas, Streamlit, MySQL-backed finance loaders, React 18, TypeScript, Vite, unittest.

## Global Constraints

- 검색·종목 선택·PER/전환 분석 전환은 DB-only이며 provider 호출이 0회여야 한다.
- 가격 최신성은 오늘이 아니라 미국 동부시간의 마지막 완료 NYSE session을 기준으로 한다.
- 시장가치는 `nyse_asset_profile.last_collected_at`과 latest price basis가 7일 넘게 벌어진 경우에만 repair scope로 둔다.
- 재무 `period_end`가 과거라는 이유만으로 stale 처리하지 않고 기존 raw coverage gap만 수집 대상으로 삼는다.
- profile/price는 CIK 없이 수집하고 SEC statement만 selected symbol/CIK identity equality를 요구한다.
- selected symbol 한 종목만 수집하며 자동 수집, 전체 종목 refresh, 새 DB table/schema, 새 run/job/row 진단 패널을 추가하지 않는다.
- 현재 S&P payload와 legacy PER/turnaround service action contract는 compatibility test로 보존하되 current React는 unified action만 렌더링한다.
- unrelated untracked `researches/active/2026-07-market-interest-free-source-benchmark/`는 stage/commit하지 않는다.

---

### Task 1: 공용 NYSE 완료 거래일 계약

**Files:**
- Create: `app/services/nyse_calendar.py`
- Modify: `app/services/backtest_price_refresh.py`
- Create: `tests/test_nyse_calendar.py`

**Interfaces:**
- Produces: `latest_completed_nyse_session(now: datetime | None = None) -> date`
- Produces: `previous_nyse_trading_day(value: date) -> date`
- Preserves: `app.services.backtest_price_refresh._latest_completed_nyse_session` private compatibility alias.

- [x] **Step 1: Write failing calendar tests**

```python
def test_latest_completed_session_uses_previous_day_before_regular_close():
    now = datetime(2026, 7, 15, 15, 59, tzinfo=ZoneInfo("America/New_York"))
    assert latest_completed_nyse_session(now) == date(2026, 7, 14)

def test_latest_completed_session_accepts_current_day_after_regular_close():
    now = datetime(2026, 7, 15, 16, 1, tzinfo=ZoneInfo("America/New_York"))
    assert latest_completed_nyse_session(now) == date(2026, 7, 15)

def test_latest_completed_session_handles_weekend_holiday_and_early_close():
    assert latest_completed_nyse_session(datetime(2026, 7, 4, 12, tzinfo=US_EASTERN_TZ)) == date(2026, 7, 2)
    assert latest_completed_nyse_session(datetime(2026, 11, 27, 13, 1, tzinfo=US_EASTERN_TZ)) == date(2026, 11, 27)
```

- [x] **Step 2: Run the new tests and confirm RED**

Run: `.venv/bin/python -m unittest tests.test_nyse_calendar -v`

Expected: FAIL with `ModuleNotFoundError: app.services.nyse_calendar`.

- [x] **Step 3: Extract the existing calendar logic without changing semantics**

```python
US_EASTERN_TZ = ZoneInfo("America/New_York")
US_MARKET_CLOSE_TIME = time(16, 0)
US_MARKET_EARLY_CLOSE_TIME = time(13, 0)

def previous_nyse_trading_day(value: date) -> date:
    current = value
    for _ in range(15):
        if _is_nyse_trading_day(current):
            return current
        current -= timedelta(days=1)
    return value

def latest_completed_nyse_session(now: datetime | None = None) -> date:
    now_et = (now or datetime.now(tz=US_EASTERN_TZ)).astimezone(US_EASTERN_TZ)
    session_date = now_et.date()
    if not _is_nyse_trading_day(session_date):
        return previous_nyse_trading_day(session_date - timedelta(days=1))
    close_time = US_MARKET_EARLY_CLOSE_TIME if session_date in _nyse_early_close_dates(session_date.year) else US_MARKET_CLOSE_TIME
    if now_et.time() <= close_time:
        return previous_nyse_trading_day(session_date - timedelta(days=1))
    return session_date
```

In `backtest_price_refresh.py`, import public helpers with compatibility aliases:

```python
from app.services.nyse_calendar import (
    latest_completed_nyse_session as _latest_completed_nyse_session,
    previous_nyse_trading_day as _previous_nyse_trading_day,
)
```

- [x] **Step 4: Run calendar and backtest refresh regressions**

Run: `.venv/bin/python -m unittest tests.test_nyse_calendar tests.test_service_contracts.BacktestRuntimeContractTests.test_backtest_price_refresh_plan_uses_latest_completed_trading_day -v`

Expected: all selected tests PASS.

- [x] **Step 5: Commit the calendar extraction**

```bash
git add app/services/nyse_calendar.py app/services/backtest_price_refresh.py tests/test_nyse_calendar.py
git commit -m "NYSE 완료 거래일 계산을 공용화"
```

### Task 2: 통합 freshness read model

**Files:**
- Create: `app/services/overview/us_stock_freshness.py`
- Modify: `finance/loaders/us_stock_turnaround.py`
- Modify: `app/services/overview/market_context_valuation.py`
- Create: `tests/test_us_stock_freshness.py`
- Modify: `tests/test_market_context_valuation.py`

**Interfaces:**
- Consumes: `latest_completed_nyse_session(now) -> date` from Task 1.
- Produces: `build_us_stock_data_freshness(symbol: str, *, per_model: Mapping[str, Any], turnaround_model: Mapping[str, Any], now: datetime | None = None) -> dict[str, Any]`.
- Produces on combined stock payload: `data_freshness.status`, basis dates, ordered gaps, and optional `refresh_us_stock_data` action.

- [x] **Step 1: Write failing NET-like freshness tests**

```python
def test_net_like_stale_market_data_remains_refreshable_without_cik():
    result = build_us_stock_data_freshness(
        "NET",
        per_model={"selection": {"symbol": "NET", "cik": None, "latest_price_date": "2026-07-07"}},
        turnaround_model={
            "coverage": {
                "profile_basis_date": "2026-02-04",
                "price_basis_date": "2026-07-07",
                "statement_period_end": "2026-03-31",
                "statement_available_at": "2026-05-08",
                "statement_core_missing": False,
            },
            "collection_plan": {"scopes": ["asset_profile", "prices"]},
        },
        now=datetime(2026, 7, 15, 18, tzinfo=US_EASTERN_TZ),
    )
    assert result["status"] == "REFRESH_AVAILABLE"
    assert result["expected_price_date"] == "2026-07-15"
    assert result["action"]["scopes"] == ["asset_profile", "prices"]

def test_statement_period_end_age_alone_does_not_create_refresh_action():
    result = build_us_stock_data_freshness(
        "AAPL",
        per_model={"selection": {"symbol": "AAPL", "cik": "320193", "latest_price_date": "2026-07-15"}},
        turnaround_model={"coverage": {"profile_basis_date": "2026-07-15", "price_basis_date": "2026-07-15", "statement_period_end": "2026-03-28", "statement_available_at": "2026-05-02", "statement_core_missing": False}, "collection_plan": {"scopes": []}},
        now=datetime(2026, 7, 15, 18, tzinfo=US_EASTERN_TZ),
    )
    assert result["status"] == "READY"
    assert "action" not in result

def test_statement_gap_adds_identity_but_keeps_market_scopes_collectable():
    result = build_us_stock_data_freshness(
        "NET",
        per_model={
            "selection": {"symbol": "NET", "cik": None, "latest_price_date": "2026-07-07"},
            "collection_action": {"scopes": ["sec_statements"]},
        },
        turnaround_model={
            "coverage": {"profile_basis_date": "2026-02-04", "price_basis_date": "2026-07-07", "statement_core_missing": True},
            "collection_plan": {"scopes": ["asset_profile", "prices", "sec_statements"]},
        },
        now=datetime(2026, 7, 15, 18, tzinfo=US_EASTERN_TZ),
    )
    assert result["action"]["scopes"] == ["asset_profile", "prices", "sec_identity", "sec_statements"]
```

- [x] **Step 2: Run the freshness tests and confirm RED**

Run: `.venv/bin/python -m unittest tests.test_us_stock_freshness -v`

Expected: FAIL because `app.services.overview.us_stock_freshness` does not exist.

- [x] **Step 3: Expose exact basis evidence from the turnaround loader**

Extend `_coverage()` with JSON-safe dates while preserving existing keys:

```python
return {
    "profile_stale": bool(profile_stale),
    "profile_basis_date": None if pd.isna(profile_date) else profile_date.strftime("%Y-%m-%d"),
    "price_missing": bool(price_missing),
    "price_basis_date": latest_text,
    "statement_core_missing": bool(statement_core_missing),
    "statement_period_end": latest.get("period_end"),
    "statement_available_at": latest.get("available_at"),
    "available_quarters": len(available),
    "missing_concepts": missing_concepts,
}
```

- [x] **Step 4: Implement the pure unified freshness builder**

```python
SCOPE_ORDER = ("asset_profile", "prices", "sec_identity", "sec_statements")

def build_us_stock_data_freshness(symbol, *, per_model, turnaround_model, now=None):
    normalized = str(symbol or "").strip().upper()
    expected = latest_completed_nyse_session(now)
    selection = dict(per_model.get("selection") or {})
    coverage = dict(turnaround_model.get("coverage") or {})
    plan = dict(turnaround_model.get("collection_plan") or {})
    price_basis = _as_date(selection.get("latest_price_date") or coverage.get("price_basis_date"))
    profile_basis = _as_date(coverage.get("profile_basis_date"))
    per_action = dict(per_model.get("collection_action") or {})
    scopes = set(plan.get("scopes") or []) | set(per_action.get("scopes") or [])
    if price_basis is None or price_basis < expected:
        scopes.add("prices")
    if profile_basis is None or price_basis is None or abs((profile_basis - price_basis).days) > 7:
        scopes.add("asset_profile")
    if "sec_statements" in scopes and not str(selection.get("cik") or "").strip():
        scopes.add("sec_identity")
    ordered = [scope for scope in SCOPE_ORDER if scope in scopes]
    reason_codes = {
        "prices": "PRICE_BEHIND_COMPLETED_SESSION",
        "asset_profile": "PROFILE_PRICE_BASIS_MISALIGNED",
        "sec_identity": "SEC_IDENTITY_MISSING",
        "sec_statements": "STATEMENT_RAW_GAP",
    }
    gaps = [
        {"scope": scope, "reason_code": reason_codes[scope], "repairable": True}
        for scope in ordered
    ]
    result = {
        "status": "REFRESH_AVAILABLE" if ordered else "READY",
        "expected_price_date": expected.isoformat(),
        "price_basis_date": price_basis.isoformat() if price_basis else None,
        "profile_basis_date": profile_basis.isoformat() if profile_basis else None,
        "statement_period_end": coverage.get("statement_period_end"),
        "statement_available_at": coverage.get("statement_available_at"),
        "gaps": gaps,
    }
    if ordered:
        result["action"] = {"id": "refresh_us_stock_data", "label": "최신 데이터로 다시 계산", "symbol": normalized, "scopes": ordered, "enabled": True}
    return result
```

Each gap must use one exact reason code: `PRICE_BEHIND_COMPLETED_SESSION`, `PROFILE_PRICE_BASIS_MISALIGNED`, `SEC_IDENTITY_MISSING`, or `STATEMENT_RAW_GAP`.

- [x] **Step 5: Attach freshness to the combined selected-stock model**

```python
freshness = build_us_stock_data_freshness(
    selected_symbol or "",
    per_model=stock_per,
    turnaround_model=turnaround,
)
recommendation = "per" if per_ready else "turnaround" if selected_symbol else None
stock = {
    **stock_per,
    "turnaround_analysis": turnaround,
    "data_freshness": freshness,
    "recommended_analysis": recommendation,
}
```

Keep S&P unchanged and increment the combined schema to `market_context_valuation_v5`.

- [x] **Step 6: Run focused read-model regressions**

Run: `.venv/bin/python -m unittest tests.test_us_stock_freshness tests.test_us_stock_turnaround tests.test_market_context_valuation`

Expected: all tests PASS; S&P isolation and PER/turnaround recommendation tests remain green.

- [x] **Step 7: Commit the freshness contract**

```bash
git add app/services/overview/us_stock_freshness.py finance/loaders/us_stock_turnaround.py app/services/overview/market_context_valuation.py tests/test_us_stock_freshness.py tests/test_market_context_valuation.py
git commit -m "개별주 최신성 판정 계약 추가"
```

### Task 3: CIK-independent market collection and partial-success facade

**Files:**
- Modify: `app/jobs/ingestion_jobs.py`
- Modify: `app/jobs/overview_actions.py`
- Modify: `tests/test_us_stock_freshness.py`
- Modify: `tests/test_us_stock_turnaround.py`
- Modify: `tests/test_us_stock_valuation.py`

**Interfaces:**
- Produces: `run_collect_us_stock_refresh_inputs(symbol: str, *, cik: str = "", identity_cik: str = "", price_start: str | None, price_end: str | None, collect_profile: bool, collect_prices: bool, collect_statements: bool, progress_callback: Callable[[dict[str, Any]], None] | None = None, profile_runner: Callable[..., JobResult] = run_collect_asset_profiles, price_runner: Callable[..., JobResult] = run_collect_ohlcv, statement_runner: Callable[..., JobResult] = run_collect_financial_statements) -> JobResult`.
- Produces: `run_overview_us_stock_data_refresh(symbol: str, *, progress_callback=None, model_builder=build_market_context_valuation_read_model, identity_runner=run_collect_sec_company_ticker_crosscheck, collection_runner=run_collect_us_stock_refresh_inputs) -> JobResult`.
- Preserves: legacy valuation/turnaround jobs and facades for compatibility; current UI will stop emitting their ids in Task 4.

- [x] **Step 1: Write failing low-level collection boundary tests**

```python
def test_market_scopes_run_without_cik_and_statement_scope_is_rejected_separately():
    result = run_collect_us_stock_refresh_inputs(
        "NET", cik="", identity_cik="", price_start="2026-07-07", price_end="2026-07-15",
        collect_profile=True, collect_prices=True, collect_statements=True,
        profile_runner=profile_runner, price_runner=price_runner, statement_runner=statement_runner,
    )
    profile_runner.assert_called_once()
    price_runner.assert_called_once()
    statement_runner.assert_not_called()
    assert result["status"] == "partial_success"
    assert result["details"]["remaining_scopes"] == ["sec_statements"]

def test_invalid_symbol_runs_no_scope():
    result = run_collect_us_stock_refresh_inputs(
        "BAD SYMBOL", cik="", identity_cik="", price_start="2026-07-07", price_end="2026-07-15",
        collect_profile=True, collect_prices=True, collect_statements=False,
        profile_runner=profile_runner, price_runner=price_runner,
    )
    assert result["status"] == "failed"
    profile_runner.assert_not_called()
    price_runner.assert_not_called()
```

- [x] **Step 2: Run the low-level tests and confirm RED**

Run: `.venv/bin/python -m unittest tests.test_us_stock_freshness -v`

Expected: FAIL because `run_collect_us_stock_refresh_inputs` is missing.

- [x] **Step 3: Implement the unified low-level job**

```python
def run_collect_us_stock_refresh_inputs(
    symbol: str,
    *,
    cik: str = "",
    identity_cik: str = "",
    price_start: str | None,
    price_end: str | None,
    collect_profile: bool,
    collect_prices: bool,
    collect_statements: bool,
    progress_callback: Callable[[dict[str, Any]], None] | None = None,
    profile_runner: Callable[..., JobResult] = run_collect_asset_profiles,
    price_runner: Callable[..., JobResult] = run_collect_ohlcv,
    statement_runner: Callable[..., JobResult] = run_collect_financial_statements,
) -> JobResult:
    job_name = "collect_us_stock_refresh_inputs"
    started_at = _now_str()
    t0 = perf_counter()
    parsed, invalid = split_valid_invalid_symbols([symbol])
    if not parsed or invalid:
        return _build_result(
            job_name=job_name, status="failed", started_at=started_at,
            finished_at=_now_str(), duration_sec=perf_counter() - t0,
            rows_written=0, symbols_requested=1, symbols_processed=0,
            failed_symbols=[str(symbol or "").strip().upper()],
            message="Selected symbol validation failed before collection.",
            details={"symbol": str(symbol or "").strip().upper()},
        )
    normalized_symbol = parsed[0]
    normalized_cik = str(cik or "").strip().lstrip("0")
    normalized_identity_cik = str(identity_cik or "").strip().lstrip("0")
    cik_valid = bool(normalized_cik and normalized_cik == normalized_identity_cik)
    steps: list[dict[str, Any]] = []
    if collect_profile:
        steps.append({"stage": "profile", **dict(profile_runner(kinds=("stock",), symbols=[normalized_symbol], progress_callback=None))})
    if collect_prices:
        if not price_start or not price_end:
            price_result = {"status": "failed", "rows_written": 0, "failed_symbols": [normalized_symbol], "message": "Exact price range is required."}
        else:
            provider_end = (datetime.strptime(price_end, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
            price_result = dict(price_runner([normalized_symbol], start=price_start, end=provider_end, interval="1d", execution_profile="managed_safe"))
        steps.append({"stage": "prices", **price_result})
    if collect_statements and cik_valid:
        steps.append({"stage": "sec", **dict(statement_runner([normalized_symbol], freq="quarterly", periods=0, period="quarterly"))})
    elif collect_statements:
        steps.append({"stage": "sec", "status": "failed", "rows_written": 0, "reason_code": "CIK_IDENTITY_REQUIRED"})
    statuses = [str(step.get("status") or "failed").lower() for step in steps]
    status = "success" if not steps or all(value == "success" for value in statuses) else "failed" if all(value in {"failed", "error"} for value in statuses) else "partial_success"
    remaining_scopes = ["sec_statements"] if collect_statements and not cik_valid else []
    failures = list(dict.fromkeys(str(item).strip().upper() for step in steps for item in step.get("failed_symbols", []) if str(item).strip()))
    rows_written = sum(int(step.get("rows_written") or 0) for step in steps)
    return _build_result(
        job_name=job_name, status=status, started_at=started_at,
        finished_at=_now_str(), duration_sec=perf_counter() - t0,
        rows_written=rows_written, symbols_requested=1,
        symbols_processed=0 if status == "failed" else 1,
        failed_symbols=failures,
        message=f"{normalized_symbol} refresh inputs collected with status {status}.",
        details={"symbol": normalized_symbol, "steps": steps, "remaining_scopes": remaining_scopes},
    )
```

- [x] **Step 4: Write failing facade sequence and replan tests**

```python
def test_facade_collects_market_before_identity_then_sec_and_replans():
    result = run_overview_us_stock_data_refresh("NET", model_builder=model_builder, identity_runner=identity_runner, collection_runner=collection_runner)
    assert calls == ["model:before", "collect:market", "identity", "model:identity", "collect:sec", "model:after"]
    assert result["details"]["before"]["action"]["symbol"] == "NET"

def test_facade_preserves_market_success_when_identity_remains_missing():
    result = run_overview_us_stock_data_refresh(
        "NET",
        model_builder=missing_identity_model_builder,
        identity_runner=identity_runner,
        collection_runner=collection_runner,
    )
    assert result["status"] == "partial_success"
    assert result["rows_written"] == 12
    assert result["details"]["after"]["action"]["scopes"] == ["sec_identity", "sec_statements"]
```

- [x] **Step 5: Run facade tests and confirm RED**

Run: `.venv/bin/python -m unittest tests.test_us_stock_freshness -v`

Expected: FAIL because `run_overview_us_stock_data_refresh` is missing.

- [x] **Step 6: Implement market-first, identity-second, statement-third orchestration**

```python
before_model = model_builder(selected_symbol=normalized)
before_stock = dict(before_model["instruments"]["us_stock"])
before = dict(before_stock.get("data_freshness") or {})
scopes = set(before.get("action", {}).get("scopes", []))
market_scopes = scopes & {"asset_profile", "prices"}
market_result = collection_runner(
    normalized,
    cik="",
    identity_cik="",
    price_start=before.get("price_basis_date"),
    price_end=before.get("expected_price_date"),
    collect_profile="asset_profile" in market_scopes,
    collect_prices="prices" in market_scopes,
    collect_statements=False,
    progress_callback=progress_callback,
)
if "sec_identity" in scopes:
    identity_result = identity_runner([normalized], progress_callback=None)
identity_model = model_builder(selected_symbol=normalized)
identity_stock = dict(identity_model["instruments"]["us_stock"])
identity_plan = dict(identity_stock.get("data_freshness") or {})
identity = dict(identity_stock.get("selection") or {})
if "sec_statements" in scopes and identity.get("cik"):
    sec_result = collection_runner(
        normalized,
        cik=str(identity["cik"]),
        identity_cik=str(identity["cik"]),
        price_start=None,
        price_end=None,
        collect_profile=False,
        collect_prices=False,
        collect_statements=True,
        progress_callback=progress_callback,
    )
after_model = model_builder(selected_symbol=normalized)
after_stock = dict(after_model["instruments"]["us_stock"])
after = dict(after_stock.get("data_freshness") or {})
```

Use `price_basis_date` as the exact start and `expected_price_date` as end. A READY no-op must call neither identity nor collection runner.

- [x] **Step 7: Run focused ingestion/facade compatibility tests**

Run: `.venv/bin/python -m unittest tests.test_us_stock_freshness tests.test_us_stock_valuation tests.test_us_stock_turnaround`

Expected: all tests PASS, including legacy selected-symbol jobs.

- [x] **Step 8: Commit the 1차 collection boundary**

```bash
git add app/jobs/ingestion_jobs.py app/jobs/overview_actions.py tests/test_us_stock_freshness.py tests/test_us_stock_valuation.py tests/test_us_stock_turnaround.py
git commit -m "개별주 최신 자료 수집 경계를 분리"
```

### Task 4: Unified Streamlit event and DB-only selection contract

**Files:**
- Modify: `app/web/overview/market_context_helpers.py`
- Modify: `tests/test_market_context_valuation.py`

**Interfaces:**
- Consumes: `run_overview_us_stock_data_refresh(symbol, progress_callback: Callable[[dict[str, Any]], None] | None = None)` from Task 3.
- Produces event id: `refresh_us_stock_data`.
- Preserves event ids: `search_us_stock`, `select_us_stock`; both remain read-only.

- [x] **Step 1: Write failing event tests**

```python
def test_unified_refresh_validates_selected_symbol_and_runs_once():
    event = {"event": {"id": "refresh_us_stock_data", "symbol": "NET", "nonce": 801}}
    assert _handle_market_context_valuation_event(event, state=state, run_action=runner, clear_cache=clear, rerun=rerun)
    assert not _handle_market_context_valuation_event(event, state=state, run_action=runner, clear_cache=clear, rerun=rerun)
    runner.assert_called_once_with("NET")

def test_search_and_selection_still_never_run_refresh():
    run_action.assert_not_called()
```

- [x] **Step 2: Run event tests and confirm RED**

Run: `.venv/bin/python -m unittest tests.test_market_context_valuation -v`

Expected: unified refresh event is rejected before implementation.

- [x] **Step 3: Replace current UI dispatch with the unified action**

```python
US_STOCK_EVENT_IDS = {"search_us_stock", "select_us_stock", "refresh_us_stock_data"}

def _run_us_stock_refresh_for_ui(symbol: str) -> dict[str, Any]:
    with st.status(f"{symbol} 최신 자료를 확인하는 중입니다.", expanded=True) as status:
        result = run_overview_us_stock_data_refresh(symbol, progress_callback=lambda update: _render_us_stock_collection_progress(status, update))
        result_status = str(result.get("status") or "failed").lower()
        if result_status == "success":
            status.update(label=f"{symbol} 최신 자료 확인을 마쳤습니다.", state="complete")
        elif result_status == "partial_success":
            status.update(label="수집 가능한 자료를 반영했고 남은 항목이 있습니다.", state="complete")
        else:
            status.update(label="최신 자료를 반영하지 못했습니다.", state="error")
    return result
```

Collection validation must accept only a symbol equal to `US_STOCK_SELECTED_SYMBOL_KEY`. After any non-failed result, clear `load_market_context_valuation_model` once and rerun once.

- [x] **Step 4: Remove row-count reflection from the user payload**

```python
def _us_stock_collection_reflection(result):
    return {
        "status": str(result.get("status") or "failed"),
        "message": str(result.get("message") or ""),
    }
```

The internal JobResult still retains rows for logs/tests; current React receives no visible row-count diagnostic.

- [x] **Step 5: Run Streamlit bridge tests**

Run: `.venv/bin/python -m unittest tests.test_market_context_valuation`

Expected: all event dedup, symbol mismatch, search/selection read-only, and S&P isolation tests PASS.

- [x] **Step 6: Commit the unified event bridge**

```bash
git add app/web/overview/market_context_helpers.py tests/test_market_context_valuation.py
git commit -m "개별주 최신화 단일 이벤트 연결"
```

### Task 5: Header freshness bar and single CTA

**Files:**
- Modify: `app/web/streamlit_components/market_context_valuation/src/MarketContextValuation.tsx`
- Modify: `app/web/streamlit_components/market_context_valuation/src/TurnaroundAnalysis.tsx`
- Modify: `app/web/streamlit_components/market_context_valuation/src/style.css`
- Modify: `tests/test_market_context_valuation.py`

**Interfaces:**
- Consumes: `payload.data_freshness` from Task 2 and `refresh_us_stock_data` from Task 4.
- Produces: one `FreshnessBar` between `.valuation-header` and `.analysis-selector`.
- Removes from current React: child `collect_us_stock_valuation`, child `collect_us_stock_turnaround`, and visible `rows_written` result strip.

- [x] **Step 1: Write failing React source-contract tests**

```python
def test_selected_stock_renders_one_header_refresh_action_outside_analysis_selector():
    source = component.read_text()
    assert "function FreshnessBar" in source
    assert 'emitEvent("refresh_us_stock_data"' in source
    assert source.index("<FreshnessBar") < source.index('className="analysis-selector"')
    assert "최신 데이터로 다시 계산" in source
    assert "collect_us_stock_valuation" not in source
    assert "collect_us_stock_turnaround" not in source

def test_basis_labels_separate_price_statement_and_filing_availability():
    assert "가격 기준일" in source
    assert "재무 기준일" in source
    assert "공개" in source
```

- [x] **Step 2: Run source-contract tests and confirm RED**

Run: `.venv/bin/python -m unittest tests.test_market_context_valuation -v`

Expected: FAIL because the unified bar and copy are absent.

- [x] **Step 3: Add the typed freshness contract and component**

```tsx
type DataFreshness = {
  status: "READY" | "REFRESH_AVAILABLE" | "PARTIAL" | "BLOCKED";
  expected_price_date?: string;
  price_basis_date?: string | null;
  profile_basis_date?: string | null;
  statement_period_end?: string | null;
  statement_available_at?: string | null;
  gaps?: { scope: string; reason_code: string; repairable: boolean }[];
  action?: { id: "refresh_us_stock_data"; label: string; symbol: string; scopes: string[]; enabled: boolean };
};

type ValuationFreshnessFields = {
  data_freshness?: DataFreshness;
  collection_result?: { status?: string; message?: string };
};

function FreshnessBar({ freshness, collecting, result, onRefresh }: FreshnessBarProps) {
  const action = freshness?.action;
  return <section className={`freshness-bar freshness-${freshness?.status?.toLowerCase() || "ready"}`}>
    <div><span>자료 기준</span><strong>가격 {freshness?.price_basis_date || "-"} · 시장가치 {freshness?.profile_basis_date || "-"} · 재무 {freshness?.statement_period_end || "-"}</strong><small>공개 {freshness?.statement_available_at || "-"}</small></div>
    {action?.enabled ? <button type="button" disabled={collecting} onClick={onRefresh}>{collecting ? "갱신 중" : action.label}</button> : null}
  </section>;
}
```

- [x] **Step 4: Render one CTA and remove child collection banners**

```tsx
const refresh = () => {
  const action = payload.data_freshness?.action;
  if (!action?.enabled || action.id !== "refresh_us_stock_data") return;
  setCollecting(true);
  emitEvent(action.id, { symbol: action.symbol });
};

{isStock && payload.selection?.symbol ? <FreshnessBar freshness={payload.data_freshness} collecting={collecting} result={payload.collection_result} onRefresh={refresh}/> : null}
{isStock && payload.selection?.symbol ? <nav className="analysis-selector" aria-label="개별주식 분석 선택"><button type="button" aria-pressed={selectedAnalysis === "per"} onClick={() => chooseAnalysis("per")}><span>PER 상대가치</span><small>{payload.multiple_regime?.status === "READY" ? "적용 가능" : "적용 전"}</small></button><button type="button" aria-pressed={selectedAnalysis === "turnaround"} onClick={() => chooseAnalysis("turnaround")}><span>전환 분석</span><small>{payload.turnaround_analysis?.status || "확인 중"}</small></button></nav> : null}
```

`StockState` and `TurnaroundAnalysis` keep their analysis states but render no collection button. Change header label to `가격 기준일` for PER and `재무 기준일` for turnaround; turnaround small copy includes `공개 {statement_available_at} · 가격 {price_basis_date}`.

- [x] **Step 5: Add responsive styles**

```css
.freshness-bar { display:grid; grid-template-columns:minmax(0,1fr) auto; align-items:center; gap:16px; padding:14px 18px; border:1px solid #d9e5ec; border-radius:16px; background:#f7fbfd; }
.freshness-bar > div { display:grid; gap:3px; min-width:0; }
.freshness-bar button { min-height:40px; padding:10px 15px; border-radius:11px; }
@media (max-width: 460px) {
  .freshness-bar { grid-template-columns:1fr; }
  .freshness-bar button { width:100%; }
}
```

- [x] **Step 6: Run React source tests and production build**

Run: `.venv/bin/python -m unittest tests.test_market_context_valuation`

Run: `npm run build`

Working directory: `app/web/streamlit_components/market_context_valuation`

Expected: Python tests PASS; TypeScript/Vite production build exits 0.

- [x] **Step 7: Commit the 2차 UI**

```bash
git add app/web/streamlit_components/market_context_valuation/src tests/test_market_context_valuation.py
git commit -m "개별주 상단 최신 데이터 재계산 UI 추가"
```

### Task 6: Actual NET verification, Browser QA, and documentation closeout

**Files:**
- Modify: `.aiworkspace/note/finance/tasks/active/overview-market-context-us-stock-freshness-refresh-v1-20260715/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-market-context-us-stock-freshness-refresh-v1-20260715/NOTES.md`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-market-context-us-stock-freshness-refresh-v1-20260715/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-market-context-us-stock-freshness-refresh-v1-20260715/RISKS.md`
- Modify: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify: `.aiworkspace/note/finance/docs/INDEX.md`
- Modify: `.aiworkspace/note/finance/tasks/active/README.md`
- Modify: `.aiworkspace/note/finance/tasks/active/STATUS_MANIFEST.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`

**Interfaces:**
- Verifies: actual DB-only NET preflight and, only through the explicit action, selected-symbol collection.
- Produces: one desktop or 420px Browser QA screenshot outside git.

- [x] **Step 1: Run focused Python tests**

Run: `.venv/bin/python -m unittest tests.test_nyse_calendar tests.test_us_stock_freshness tests.test_us_stock_valuation tests.test_us_stock_turnaround tests.test_market_context_valuation`

Expected: all focused tests PASS.

- [x] **Step 2: Run compile and React build verification**

Run: `.venv/bin/python -m py_compile app/services/nyse_calendar.py app/services/overview/us_stock_freshness.py app/services/overview/market_context_valuation.py app/jobs/ingestion_jobs.py app/jobs/overview_actions.py app/web/overview/market_context_helpers.py`

Run: `npm run build`

Working directory: `app/web/streamlit_components/market_context_valuation`

Expected: both commands exit 0.

- [x] **Step 3: Run isolated finance test suite and classify unrelated failures**

Run: `.venv/bin/python -m unittest discover -s tests -p 'test_*.py'`

Expected: no new failure in freshness/PER/turnaround/Market Context; any known unrelated baseline failure is recorded with its exact test id.

- [x] **Step 4: Verify actual NET DB-only preflight before provider mutation**

```python
model = build_market_context_valuation_read_model(selected_symbol="NET")
freshness = model["instruments"]["us_stock"]["data_freshness"]
assert freshness["action"]["symbol"] == "NET"
assert "prices" in freshness["action"]["scopes"]
assert "asset_profile" in freshness["action"]["scopes"]
```

Record expected price date, stored price/profile/statement dates, scopes, and CIK state in `RUNS.md`.

- [x] **Step 5: Exercise the explicit selected-symbol action once if provider access is available**

Call only `run_overview_us_stock_data_refresh("NET")`. Confirm result symbol is NET, no universe scope is present, successful market writes survive missing SEC identity, and the after-plan reflects remaining gaps. If provider access is unavailable, do not substitute broad collection; record the exact block and complete UI QA with a deterministic stale payload.

- [x] **Step 6: Perform Browser QA at desktop and 420px**

Verify:

- cached selected-company UI appears before any refresh action;
- one CTA exists between the company header and analysis selector;
- switching PER/turnaround creates no provider call and no duplicate CTA;
- generic `기준일` is replaced by price or financial basis copy;
- partial result shows updated basis/remaining reason without rows/job panel;
- horizontal overflow and browser console errors are both 0.

Save one representative screenshot under `/Users/taeho/.codex/visualizations/2026/07/15/019f65a4-445f-79b2-8e17-0e3b374b88b3/` and do not stage it.

- [x] **Step 7: Synchronize durable docs and task closeout**

Set `STATUS.md` to 3/3 complete only after evidence is recorded. Update `PROJECT_MAP.md` with the shared NYSE calendar, unified freshness service, explicit action, and CIK split. Keep root logs to 3-5 concise milestone lines and move command output to `RUNS.md`.

- [x] **Step 8: Run final repository checks**

Run: `git diff --check`

Run: `git status --short`

Expected: no whitespace error; only intended task/code/docs plus the preserved unrelated research folder appear.

- [x] **Step 9: Commit the 3차 closeout**

```bash
git add .aiworkspace/note/finance/tasks/active/overview-market-context-us-stock-freshness-refresh-v1-20260715 .aiworkspace/note/finance/docs/PROJECT_MAP.md .aiworkspace/note/finance/docs/ROADMAP.md .aiworkspace/note/finance/docs/INDEX.md .aiworkspace/note/finance/tasks/active/README.md .aiworkspace/note/finance/tasks/active/STATUS_MANIFEST.md .aiworkspace/note/finance/WORK_PROGRESS.md .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md app/services app/jobs app/web finance/loaders tests
git commit -m "개별주 최신 데이터 재계산 QA와 문서 정렬"
```
