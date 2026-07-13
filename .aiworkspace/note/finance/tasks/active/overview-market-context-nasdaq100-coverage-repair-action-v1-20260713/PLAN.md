# Nasdaq-100 60-Month Coverage Repair Action Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Nasdaq-100 coverage blocker에서 버튼 한 번으로 최근 60개월의 누락 EPS와 가격을 보강하고, 같은 화면에서 재계산 결과를 자동으로 다시 표시한다.

**Architecture:** React는 `{id, nonce}` action event만 Python에 전달한다. Python Overview action facade가 planner, SEC statement ingestion, OHLCV ingestion, DB-backed 60개월 materialization을 동기 실행하고 valuation cache를 비운다. 월별 weighted coverage 95%와 existing point-in-time/calibration 계약은 유지한다.

**Tech Stack:** Python 3, pandas, MySQL, Streamlit, React/TypeScript, unittest, Vite

Status: Ready For Inline Execution
Last Updated: 2026-07-13

## Global Constraints

- 최근 60개월 historical QQQ holdings universe를 대상으로 한다.
- UI는 provider를 직접 호출하지 않고 `Ingestion -> DB -> Loader/Service -> UI`를 따른다.
- 사용자는 현재 화면에서 synchronous execution 완료까지 기다린다.
- 월별 weighted EPS/price coverage `95%`와 기존 calibration gate를 유지한다.
- foreign/FY-only annual proxy, missing value 합성, blocked month 보간을 도입하지 않는다.
- account/token/subscription provider, background queue, raw job row 중심 패널을 추가하지 않는다.
- 성공 batch는 DB에 유지하고 다음 실행에서 이미 충족된 target을 제외한다.
- unrelated untracked research folder, run history artifact, generated screenshot은 stage하지 않는다.

## 이걸 하는 이유?

Nasdaq-100 · QQQ proxy 가치평가는 실제 희석 EPS로 설명되는 보유 비중이 95% 미만이면 의도적으로 차단된다. 현재 화면은 차단 이유를 설명하지만 사용자가 같은 화면에서 부족한 자료를 보강하고 다시 계산할 수 없다. 사용자가 별도 명령을 실행하지 않아도 차단 카드에서 한 번의 action으로 최근 60개월 자료 보강, 재계산, 화면 갱신까지 끝내도록 한다.

## Goal

- Nasdaq coverage blocker에 `60개월 가치평가 자료 보강` action을 제공한다.
- action은 최근 60개월의 과거 편입·퇴출 종목까지 대상으로 누락 EPS와 가격 이력을 선별 보강한다.
- 실행은 현재 Streamlit 화면에서 동기적으로 기다리며 단계별 진행 상태를 표시한다.
- 수집 결과는 종목 단위로 DB에 즉시 저장해 부분 실패 후 재실행을 이어받는다.
- 완료 후 60개월을 재계산하고 cache를 비운 뒤 같은 화면을 자동 재조회한다.
- 모든 월이 95% gate를 통과하면 그래프를 표시하고, 통과하지 못하면 갱신된 coverage와 남은 원인을 표시한다.

## Five-Stage Roadmap

### 1차 — Coverage Repair Plan

- 최근 60개월 holdings/EPS/price 상태를 월별로 진단한다.
- non-equity 보유를 계산 대상에서 제외하고 EPS, price, identity, unsupported-source gap을 구분한다.
- 이미 충분한 종목은 제외한 repeat-safe repair plan을 만든다.

완료 조건: 같은 DB snapshot에서 동일한 대상 symbol/CIK/date range/reason을 반환하는 pure/service contract가 테스트를 통과한다.

### 2차 — Resumable Ingestion / Persistence

- 기존 SEC EDGAR statement ingestion과 OHLCV ingestion을 repair plan 대상에만 적용한다.
- 작은 batch, progress callback, 종목 단위 UPSERT, partial failure evidence를 제공한다.
- 무료 원천에서 제공하지 않는 상장폐지 가격이나 해외 issuer 분기 EPS는 합성하지 않는다.

완료 조건: 중간 실패 뒤 재실행이 이미 저장된 coverage를 재사용하고 중복 business row를 만들지 않는다.

### 3차 — 60-Month Rematerialization / Quality Gate

- 저장된 holdings/statements/prices로 최근 60개월을 다시 materialize한다.
- 월별 weighted coverage 95%, aggregate earnings yield, calibration contract를 그대로 적용한다.
- pass/fail 뒤 최신 read model과 remaining gap summary를 생성한다.

완료 조건: pass면 60개월 graph-ready row가 생성되고 fail이면 임의 보간 없이 월/원인별 blocker가 남는다.

### 4차 — React Action / Synchronous Progress UX

- coverage blocker에 `60개월 가치평가 자료 보강` 버튼을 추가한다.
- React event를 Python action facade가 nonce 기반으로 한 번만 소비한다.
- 대상 확인, EPS 보강, 가격 이력 보강, 가치평가 재계산, 완료 순서의 사용자 중심 진행 상태를 표시한다.
- 완료 후 valuation cache를 clear하고 rerun한다.

완료 조건: 성공 시 그래프로 자동 전환하고 부분 성공/실패 시 갱신된 blocker와 재시도 action을 표시한다.

### 5차 — QA / Docs / Commit

- unit, service contract, ingestion failure/resume, idempotency, React event, cache/rerun을 검증한다.
- 실제 DB에서 최근 60개월 ready count와 coverage를 확인한다.
- desktop과 420px Browser QA를 수행하고 task/canonical docs/runbook을 동기화한다.
- unrelated untracked research folder와 generated screenshot은 stage하지 않는다.

완료 조건: fresh verification evidence, Browser QA screenshot, 문서 동기화, coherent Korean commit이 생성된다.

## Scope

### In Scope

- Nasdaq valuation coverage blocker 전용 repair plan과 one-click synchronous action
- 최근 60개월 holdings constituent의 SEC diluted EPS와 EOD price gap 보강
- existing ingestion/DB/loader/service/React 경계 재사용
- partial failure, resume, event dedup, cache clear, updated blocker feedback

### Out Of Scope

- UI에서 SEC/provider 직접 fetch
- background queue/daemon 신설
- coverage gate 완화
- foreign/FY-only annual EPS proxy 도입
- 상장폐지 가격이나 missing EPS 합성/보간
- 유료/account/token provider 도입
- raw job row 중심 운영 패널

## Stop Conditions

- 무료·무계정 원천으로 제공되지 않는 값을 임의로 생성하지 않는다.
- 월별 weighted coverage가 95% 미만이면 그 달을 READY로 승격하지 않는다.
- action 재실행이 duplicate event 또는 duplicate business row를 만들면 UI 연결을 진행하지 않는다.
- 수집이 UI layer에서 직접 실행되거나 DB를 우회하면 구현을 중단하고 경계를 수정한다.

## Verification Outline

```bash
.venv/bin/python -m unittest tests.test_nasdaq100_valuation tests.test_market_context_valuation -v
.venv/bin/python -m unittest tests.test_service_contracts -v
npm run build --prefix app/web/streamlit_components/market_context_valuation
.venv/bin/python -m py_compile finance/data/nasdaq100_valuation.py app/jobs/ingestion_jobs.py app/jobs/overview_actions.py app/web/overview/market_context_helpers.py
git diff --check
git status --short
```

## Detailed TDD Execution

### Task 1: Coverage Repair Planner

**Files:**
- Modify: `finance/data/nasdaq100_valuation.py`
- Test: `tests/test_nasdaq100_valuation.py`
- Update: task `STATUS.md`, `RUNS.md`, `NOTES.md`, `RISKS.md`

**Interfaces:**
- Consumes: `derive_filing_aware_ttm_eps`, `_price_history_frame`, `_latest_prices_as_of`, `materialize_monthly_valuation_rows`
- Produces: `nasdaq100_repair_window`, `is_nasdaq100_equity_holding`, `build_nasdaq100_coverage_repair_plan`, `load_nasdaq100_coverage_repair_plan`

- [x] **Step 1: Write the failing planner tests.**

Use fixtures containing a covered equity, missing-EPS equity, missing-price equity, unresolved holding, Currency, and Index Future. Assert exact `needs`, date range, affected month count, excluded non-equity symbols, unsupported reasons, and `before.ready_months`.

```python
def test_builds_repair_plan_without_non_equity_targets(self) -> None:
    from finance.data.nasdaq100_valuation import build_nasdaq100_coverage_repair_plan

    plan = build_nasdaq100_coverage_repair_plan(
        holding_rows=repair_holdings,
        statement_rows=repair_statements,
        price_rows=repair_prices,
        issue_rows=[],
        start_month="2026-06-01",
        end_month="2026-07-31",
    )
    by_symbol = {row["symbol"]: row for row in plan["targets"]}
    self.assertEqual(by_symbol["MISS_EPS"]["needs"], ["quarterly_diluted_eps"])
    self.assertEqual(by_symbol["MISS_PRICE"]["needs"], ["eod_price"])
    self.assertNotIn("USD", by_symbol)
    self.assertNotIn("NQZ6", by_symbol)
```

- [x] **Step 2: Run the new test and verify RED.**

```bash
.venv/bin/python -m unittest \
  tests.test_nasdaq100_valuation.Nasdaq100ValuationCoverageTests.test_builds_repair_plan_without_non_equity_targets -v
```

Expected: missing `build_nasdaq100_coverage_repair_plan` failure.

- [x] **Step 3: Implement the repair window and non-equity boundary.**

```python
NON_EQUITY_ASSET_CLASSES = {"currency", "cash", "index future", "future", "synthetic cash"}

def nasdaq100_repair_window(*, end_month: str, months: int = 60) -> tuple[str, str]:
    end = pd.Timestamp(end_month).to_period("M").to_timestamp()
    start = end - pd.DateOffset(months=max(1, int(months)) - 1)
    return start.strftime("%Y-%m-%d"), (end + pd.offsets.MonthEnd(0)).strftime("%Y-%m-%d")

def is_nasdaq100_equity_holding(row: Mapping[str, Any]) -> bool:
    asset_class = str(row.get("asset_class") or "equity").strip().lower()
    name = str(row.get("holding_name") or "").strip().lower()
    symbol = str(row.get("holding_symbol") or "").strip().upper()
    return asset_class not in NON_EQUITY_ASSET_CLASSES and symbol != "USD" and "future" not in name
```

- [x] **Step 4: Implement deterministic monthly diagnosis and target merge.**

For each month select the latest eligible snapshot, derive filing-aware TTM EPS, inspect snapshot/month-end prices, and merge symbol targets. Return JSON-safe targets sorted by descending `max_weight_pct`, then symbol.

```python
def build_nasdaq100_coverage_repair_plan(
    holding_rows: Iterable[dict[str, Any]],
    statement_rows: Iterable[dict[str, Any]],
    price_rows: Iterable[dict[str, Any]],
    issue_rows: Iterable[dict[str, Any]] | None = None,
    *, start_month: str, end_month: str,
) -> dict[str, Any]:
    """Return repeat-safe missing EPS/price targets for the requested monthly window."""
    holdings = pd.DataFrame(list(holding_rows))
    prices = _price_history_frame(price_rows)
    statements = list(statement_rows)
    exhausted_prices = {
        str(row.get("symbol") or "").upper()
        for row in list(issue_rows or [])
        if str(row.get("latest_status") or "active") == "active"
    }
    targets: dict[str, dict[str, Any]] = {}
    unsupported: list[dict[str, Any]] = []
    for month in pd.date_range(
        pd.Timestamp(start_month).to_period("M").to_timestamp(),
        pd.Timestamp(end_month).to_period("M").to_timestamp(),
        freq="MS",
    ):
        calendar_end = month + pd.offsets.MonthEnd(0)
        eligible = holdings.loc[pd.to_datetime(holdings["as_of_date"]) <= calendar_end]
        if eligible.empty:
            continue
        snapshot_date = pd.Timestamp(pd.to_datetime(eligible["as_of_date"]).max())
        snapshot = eligible.loc[pd.to_datetime(eligible["as_of_date"]) == snapshot_date].to_dict("records")
        snapshot_prices = _latest_prices_as_of(prices, snapshot_date)
        month_prices = _latest_prices_as_of(prices, calendar_end)
        eps_by_symbol = derive_filing_aware_ttm_eps(
            statements, as_of_date=calendar_end.strftime("%Y-%m-%d")
        )
        for holding in snapshot:
            if not is_nasdaq100_equity_holding(holding):
                continue
            symbol = str(holding.get("holding_symbol") or "").upper()
            weight = float(holding.get("weight_pct") or 0.0)
            if not symbol:
                unsupported.append({"reason": "missing_identity", "month": month.strftime("%Y-%m-%d"), "weight_pct": weight})
                continue
            needs: list[str] = []
            if symbol not in eps_by_symbol:
                needs.append("quarterly_diluted_eps")
            if symbol not in snapshot_prices or symbol not in month_prices:
                if symbol in exhausted_prices:
                    unsupported.append({"symbol": symbol, "reason": "unsupported_free_source", "month": month.strftime("%Y-%m-%d"), "weight_pct": weight})
                else:
                    needs.append("eod_price")
            if not needs:
                continue
            target = targets.setdefault(symbol, {
                "symbol": symbol,
                "issuer_cik": holding.get("issuer_cik"),
                "needs": set(),
                "affected_months": set(),
                "max_weight_pct": 0.0,
                "start_date": snapshot_date.strftime("%Y-%m-%d"),
                "end_date": calendar_end.strftime("%Y-%m-%d"),
            })
            target["needs"].update(needs)
            target["affected_months"].add(month.strftime("%Y-%m-%d"))
            target["max_weight_pct"] = max(target["max_weight_pct"], weight)
            target["start_date"] = min(target["start_date"], snapshot_date.strftime("%Y-%m-%d"))
            target["end_date"] = max(target["end_date"], calendar_end.strftime("%Y-%m-%d"))
    normalized_targets = [
        {**row, "needs": sorted(row["needs"]), "affected_months": len(row["affected_months"])}
        for row in targets.values()
    ]
    materialized = materialize_monthly_valuation_rows(
        holdings.to_dict("records"), statements, prices.rename(columns={"price": "close"}).to_dict("records"),
        start_month=start_month, end_month=end_month,
    )
    return {
        "window": {"start_month": start_month, "end_month": end_month, "months": len(pd.date_range(start_month, end_month, freq="MS"))},
        "targets": sorted(normalized_targets, key=lambda row: (-row["max_weight_pct"], row["symbol"])),
        "unsupported": unsupported,
        "before": {"ready_months": sum(row.get("data_quality") == "reconstructed_actual" for row in materialized), "blocked_months": sum(row.get("data_quality") != "reconstructed_actual" for row in materialized)},
    }
```

Required reasons are `missing_quarterly_eps`, `missing_price_history`, `missing_identity`, `non_equity`, and `unsupported_free_source`.

- [x] **Step 5: Add the DB-backed planner loader.**

Extend the holdings input query with `holding_name`, `asset_class`, and `issuer_cik`; load existing `limited_price_history` evidence for Nasdaq targets; then call the pure planner.

```python
def load_nasdaq100_coverage_repair_plan(
    *, months: int = 60, end_month: str | None = None,
    db_factory: Any = MySQLClient, host: str = "localhost",
    user: str = "root", password: str = "1234", port: int = 3306,
) -> dict[str, Any]:
    resolved_end = end_month or pd.Timestamp.today().strftime("%Y-%m-%d")
    start, end = nasdaq100_repair_window(end_month=resolved_end, months=months)
    holdings, statements, prices = _load_nasdaq100_materialization_inputs(
        start_month=start, end_month=end, db_factory=db_factory,
        host=host, user=user, password=password, port=port,
    )
    issues = load_market_data_issues(
        universe_code="NASDAQ100", issue_type="limited_price_history", limit=500,
        host=host, user=user, password=password, port=port,
    )
    return build_nasdaq100_coverage_repair_plan(
        holdings, statements, prices, issues, start_month=start, end_month=end,
    )
```

- [x] **Step 6: Run the full planner suite and verify GREEN.**

```bash
.venv/bin/python -m unittest tests.test_nasdaq100_valuation -v
.venv/bin/python -m py_compile finance/data/nasdaq100_valuation.py
git diff --check
```

Expected: unittest `OK`, compile exit `0`, empty diff check.

- [x] **Step 7: Record evidence and commit 1차.**

```bash
git add finance/data/nasdaq100_valuation.py tests/test_nasdaq100_valuation.py \
  .aiworkspace/note/finance/tasks/active/overview-market-context-nasdaq100-coverage-repair-action-v1-20260713
git commit -m "나스닥100 60개월 coverage 보강 계획 추가"
```

### Task 2: Resumable Missing EPS / Price Ingestion

**Files:**
- Modify: `app/jobs/ingestion_jobs.py`
- Modify: `finance/data/nasdaq100_valuation.py`
- Test: `tests/test_nasdaq100_valuation.py`
- Update: task docs

**Interfaces:**
- Consumes: Task 1 `load_nasdaq100_coverage_repair_plan()` payload
- Produces: `collect_nasdaq100_repair_inputs(plan, *, batch_size=20, progress_callback=None, statement_runner=run_collect_financial_statements, price_runner=run_collect_ohlcv)`

- [x] **Step 1: Write failing batch, progress, and partial-failure tests.**

```python
def test_repair_collection_keeps_successful_batches(self) -> None:
    from app.jobs.ingestion_jobs import collect_nasdaq100_repair_inputs
    events = []
    result = collect_nasdaq100_repair_inputs(
        repair_plan,
        batch_size=1,
        progress_callback=events.append,
        statement_runner=statement_runner_with_second_batch_failure,
        price_runner=successful_price_runner,
    )
    self.assertEqual(result["status"], "partial_success")
    self.assertEqual(result["failed_symbols"], ["MISS_EPS_2"])
```

- [x] **Step 2: Run the new test and verify RED.**

Expected: missing `collect_nasdaq100_repair_inputs` failure.

- [x] **Step 3: Implement stable EPS and price batches.**

```python
def collect_nasdaq100_repair_inputs(
    plan: Mapping[str, Any], *, batch_size: int = 20,
    progress_callback: Callable[[dict[str, Any]], None] | None = None,
    statement_runner: Callable = run_collect_financial_statements,
    price_runner: Callable = run_collect_ohlcv,
) -> dict[str, Any]:
    """Persist successful repair batches and return compact partial-failure evidence."""
    targets = [dict(row) for row in plan.get("targets", [])]
    stage_targets = {
        "eps": [row for row in targets if "quarterly_diluted_eps" in row.get("needs", [])],
        "prices": [row for row in targets if "eod_price" in row.get("needs", [])],
    }
    results: list[dict[str, Any]] = []
    failed_symbols: list[str] = []
    for stage, rows in stage_targets.items():
        total = len(rows)
        if progress_callback:
            progress_callback({"event": "stage_start", "stage": stage, "completed": 0, "total": total, "message": f"{stage} 보강을 시작합니다."})
        for offset in range(0, total, max(1, int(batch_size))):
            batch = rows[offset: offset + max(1, int(batch_size))]
            symbols = [str(row["symbol"]) for row in batch]
            try:
                if stage == "eps":
                    result = dict(statement_runner(symbols, freq="quarterly", periods=0, period="quarterly"))
                else:
                    result = dict(price_runner(
                        symbols,
                        start=min(str(row["start_date"]) for row in batch),
                        end=max(str(row["end_date"]) for row in batch),
                        interval="1d",
                        execution_profile="managed_safe",
                    ))
            except Exception as exc:
                result = {"status": "failed", "rows_written": 0, "failed_symbols": symbols, "message": str(exc)}
            results.append({"stage": stage, "symbols": symbols, **result})
            if str(result.get("status")) in {"failed", "error"}:
                failed_symbols.extend(result.get("failed_symbols") or symbols)
            if progress_callback:
                progress_callback({"event": "stage_progress", "stage": stage, "completed": min(offset + len(batch), total), "total": total, "message": f"{stage} {min(offset + len(batch), total)}/{total}"})
    statuses = {str(row.get("status") or "failed") for row in results}
    status = "failed" if results and statuses <= {"failed", "error"} else "partial_success" if failed_symbols else "success"
    return {
        "status": status,
        "rows_written": sum(int(row.get("rows_written") or 0) for row in results),
        "failed_symbols": sorted(set(failed_symbols)),
        "steps": results,
    }
```

EPS uses quarterly canonical SEC statement ingestion. Price uses explicit plan `start_date`/`end_date`, `interval="1d"`, and `execution_profile="managed_safe"`. Every callback contains `event`, `stage`, `completed`, `total`, and `message`.

- [x] **Step 4: Persist exhausted price-history evidence.**

After attempted full-window price collection, rebuild the plan. Persist symbols still missing price history through existing `build_price_history_limit_issue_rows` and `upsert_market_data_issue_rows` with `universe_code="NASDAQ100"` and `period="max"`.

- [x] **Step 5: Run ingestion tests and verify GREEN.**

```bash
.venv/bin/python -m unittest tests.test_nasdaq100_valuation -v
.venv/bin/python -m py_compile app/jobs/ingestion_jobs.py finance/data/nasdaq100_valuation.py
git diff --check
```

- [x] **Step 6: Record evidence and commit 2차.**

```bash
git add app/jobs/ingestion_jobs.py finance/data/nasdaq100_valuation.py \
  tests/test_nasdaq100_valuation.py \
  .aiworkspace/note/finance/tasks/active/overview-market-context-nasdaq100-coverage-repair-action-v1-20260713
git commit -m "나스닥100 누락 자료 재수집 파이프라인 추가"
```

### Task 3: 60-Month Rematerialization And Result Contract

**Files:**
- Modify: `app/jobs/ingestion_jobs.py`
- Modify: `app/services/overview/nasdaq100_valuation.py`
- Test: `tests/test_nasdaq100_valuation.py`
- Test: `tests/test_market_context_valuation.py`
- Update: task docs

**Interfaces:**
- Consumes: Task 1 planner and Task 2 collection result
- Produces: `run_repair_nasdaq100_valuation_coverage(*, months=60, batch_size=20, progress_callback=None) -> JobResult`; BLOCKED `coverage.repair_action`

- [x] **Step 1: Write failing orchestration tests for success, partial success, and failure.**

Assert call order `before plan -> collection -> materialization -> after plan`, partial collection still materializes, and `success` requires `after.ready_months == after.window.months`.

```python
def test_repair_job_rematerializes_after_partial_collection(self) -> None:
    from app.jobs.ingestion_jobs import run_repair_nasdaq100_valuation_coverage
    result = run_repair_nasdaq100_valuation_coverage(
        plan_loader=before_then_after_plan_loader,
        input_collector=lambda *_args, **_kwargs: {
            "status": "partial_success", "rows_written": 10, "failed_symbols": ["OLD"]
        },
        materializer=lambda **_kwargs: {"rows_written": 60, "ready_rows": 48, "blocked_rows": 12},
    )
    self.assertEqual(result["status"], "partial_success")
    self.assertEqual(result["details"]["after"]["ready_months"], 48)
```

- [x] **Step 2: Run orchestration tests and verify RED.**

Expected: missing `run_repair_nasdaq100_valuation_coverage` failure.

- [x] **Step 3: Implement strict orchestration and compact summary.**

```python
def run_repair_nasdaq100_valuation_coverage(
    *, months: int = 60, batch_size: int = 20,
    progress_callback: Callable[[dict[str, Any]], None] | None = None,
    plan_loader: Callable = load_nasdaq100_coverage_repair_plan,
    input_collector: Callable = collect_nasdaq100_repair_inputs,
    materializer: Callable = materialize_and_store_nasdaq100_monthly,
) -> JobResult:
    """Repair stored inputs, rematerialize 60 months, and report strict readiness."""
    started_at = _now_str()
    t0 = perf_counter()
    try:
        if progress_callback:
            progress_callback({"event": "stage_start", "stage": "diagnose", "completed": 0, "total": 1, "message": "60개월 누락 자료를 확인합니다."})
        before = plan_loader(months=months)
        collection = input_collector(
            before, batch_size=batch_size, progress_callback=progress_callback,
        ) if before.get("targets") else {"status": "success", "rows_written": 0, "failed_symbols": [], "steps": []}
        if progress_callback:
            progress_callback({"event": "stage_start", "stage": "materialize", "completed": 0, "total": 1, "message": "60개월 가치평가를 다시 계산합니다."})
        materialized = materializer(
            start_month=before["window"]["start_month"],
            end_month=before["window"]["end_month"],
        )
        after = plan_loader(months=months)
        ready = int(after.get("before", {}).get("ready_months") or 0)
        required = int(after.get("window", {}).get("months") or months)
        status = "success" if ready == required else "partial_success"
        if progress_callback:
            progress_callback({"event": "stage_complete", "stage": "complete", "completed": ready, "total": required, "message": f"60개월 중 {ready}개월이 준비됐습니다."})
        return _build_result(
            job_name="repair_nasdaq100_valuation_coverage",
            status=status,
            started_at=started_at,
            finished_at=_now_str(),
            duration_sec=perf_counter() - t0,
            rows_written=int(collection.get("rows_written") or 0) + int(materialized.get("rows_written") or 0),
            symbols_requested=len(before.get("targets") or []),
            symbols_processed=max(0, len(before.get("targets") or []) - len(collection.get("failed_symbols") or [])),
            failed_symbols=list(collection.get("failed_symbols") or []),
            message=f"Nasdaq-100 60-month repair finished with {ready}/{required} ready months.",
            details={"pipeline_type": "nasdaq100_valuation_repair", "before": before["before"], "after": after["before"], "window": after["window"], "collection": collection, "materialization": materialized, "remaining_targets": after.get("targets") or [], "unsupported": after.get("unsupported") or []},
        )
    except Exception as exc:
        return _build_result(
            job_name="repair_nasdaq100_valuation_coverage", status="failed",
            started_at=started_at, finished_at=_now_str(),
            duration_sec=perf_counter() - t0, rows_written=0,
            symbols_requested=0, symbols_processed=0,
            message=f"Nasdaq-100 60-month repair failed: {exc}",
            details={"pipeline_type": "nasdaq100_valuation_repair"},
        )
```

Emit `diagnose`, `eps`, `prices`, `materialize`, `complete`. A zero-target 60/60 plan is success; zero targets with unresolved gaps is partial success.

- [x] **Step 4: Write the failing service action test.**

BLOCKED Nasdaq must expose action id/label/detail/enabled. READY Nasdaq must omit or disable it.

- [x] **Step 5: Add the BLOCKED repair-action contract.**

```python
coverage["repair_action"] = {
    "id": "repair_nasdaq100_60m",
    "label": "60개월 가치평가 자료 보강",
    "detail": "누락된 구성 종목 EPS와 가격 이력을 보강한 뒤 다시 계산합니다.",
    "enabled": True,
}
```

- [x] **Step 6: Run job/service tests and verify GREEN.**

```bash
.venv/bin/python -m unittest tests.test_nasdaq100_valuation tests.test_market_context_valuation -v
.venv/bin/python -m py_compile app/jobs/ingestion_jobs.py app/services/overview/nasdaq100_valuation.py
git diff --check
```

- [x] **Step 7: Record evidence and commit 3차.**

```bash
git add app/jobs/ingestion_jobs.py app/services/overview/nasdaq100_valuation.py \
  tests/test_nasdaq100_valuation.py tests/test_market_context_valuation.py \
  .aiworkspace/note/finance/tasks/active/overview-market-context-nasdaq100-coverage-repair-action-v1-20260713
git commit -m "나스닥100 60개월 재계산과 결과 계약 추가"
```

### Task 4: React Action And Synchronous Progress UX

**Files:**
- Modify: `app/jobs/overview_actions.py`
- Modify: `app/web/overview/market_context_helpers.py`
- Modify: `app/web/streamlit_components/market_context_valuation/src/MarketContextValuation.tsx`
- Modify: `app/web/streamlit_components/market_context_valuation/src/style.css`
- Regenerate: `app/web/streamlit_components/market_context_valuation/component_static/*`
- Test: `tests/test_market_context_valuation.py`
- Test: `tests/test_service_contracts.py`
- Update: task docs

**Interfaces:**
- Consumes: Task 3 repair job and action payload
- Produces: `run_overview_nasdaq100_valuation_repair`, `_handle_market_context_valuation_event`; React `{event: {id, nonce}}`

- [x] **Step 1: Write failing Python event tests.**

Assert nested event parsing, nonce dedup, facade invocation once, result storage, `load_market_context_valuation_model.clear()`, and `st.rerun()`.

```python
def test_market_context_repair_event_runs_once_and_clears_cache(self) -> None:
    event = {"event": {"id": "repair_nasdaq100_60m", "nonce": 123}}
    self.assertTrue(market_context_helpers._handle_market_context_valuation_event(event))
    repair_job.assert_called_once()
    valuation_cache.clear.assert_called_once()
```

- [x] **Step 2: Write failing React source contracts.**

Assert exact tokens `repair_nasdaq100_60m`, `Streamlit.setComponentValue`, `60개월 가치평가 자료 보강`, `남은 자료 다시 보강`, and pending disabled state.

- [x] **Step 3: Run new UI/event tests and verify RED.**

```bash
.venv/bin/python -m unittest tests.test_market_context_valuation -v
.venv/bin/python -m unittest tests.test_service_contracts -k market_context_valuation_repair -v
```

- [x] **Step 4: Add the Overview action facade.**

```python
def run_overview_nasdaq100_valuation_repair(
    *, months: int = 60,
    progress_callback: Callable[[dict[str, Any]], None] | None = None,
) -> JobResult:
    result = dict(run_repair_nasdaq100_valuation_coverage(
        months=months, progress_callback=progress_callback
    ))
    result["job_name"] = "overview_nasdaq100_valuation_repair"
    return result
```

- [x] **Step 5: Add event consume/dedup and synchronous progress.**

```python
def _handle_market_context_valuation_event(event: dict[str, Any] | None) -> bool:
    payload = _market_context_valuation_event_payload(event)
    if payload.get("id") != "repair_nasdaq100_60m" or not _consume_market_context_valuation_event(payload):
        return False
    with st.status("60개월 가치평가 자료를 보강하는 중입니다.", expanded=True) as status:
        result = run_overview_nasdaq100_valuation_repair(
            months=60,
            progress_callback=lambda update: _render_nasdaq100_repair_progress(status, update),
        )
    _store_overview_job_result(NASDAQ100_REPAIR_RESULT_KEY, result)
    load_market_context_valuation_model.clear()
    st.rerun()
    return True
```

Inject the compact previous result into the Nasdaq payload before render. The first screen shows user stages, not raw rows.

- [x] **Step 6: Add the React CTA, pending state, and result reflection.**

```tsx
const [pendingRepair, setPendingRepair] = useState(false);
const emitRepair = () => {
  setPendingRepair(true);
  Streamlit.setComponentValue({
    event: { id: "repair_nasdaq100_60m", nonce: Date.now() },
  });
};
```

Render only for BLOCKED Nasdaq. Partial results keep the blocker and show before/after summary plus retry; READY rerun shows a one-time success notice above graphs.

- [x] **Step 7: Add responsive CSS and rebuild the component.**

```bash
npm run build --prefix app/web/streamlit_components/market_context_valuation
```

Expected: Vite exits `0`; current hashed assets/index are regenerated.

- [x] **Step 8: Run UI/service regression and verify GREEN.**

```bash
.venv/bin/python -m unittest tests.test_market_context_valuation -v
.venv/bin/python -m unittest tests.test_service_contracts -k market_context -v
.venv/bin/python -m py_compile app/jobs/overview_actions.py app/web/overview/market_context_helpers.py
git diff --check
```

- [x] **Step 9: Record evidence and commit 4차.**

```bash
git add app/jobs/overview_actions.py app/web/overview/market_context_helpers.py \
  app/web/streamlit_components/market_context_valuation \
  tests/test_market_context_valuation.py tests/test_service_contracts.py \
  .aiworkspace/note/finance/tasks/active/overview-market-context-nasdaq100-coverage-repair-action-v1-20260713
git commit -m "나스닥100 60개월 자료 보강 버튼 연결"
```

### Task 5: Actual QA, Durable Docs, And Closeout

**Files:**
- Modify: `.aiworkspace/note/finance/docs/INDEX.md`
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/architecture/DATA_DB_PIPELINE_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/data/README.md`
- Modify: `.aiworkspace/note/finance/docs/data/SCHEMA_REFERENCE.md`
- Modify: `.aiworkspace/note/finance/docs/runbooks/OVERVIEW_MARKET_INTELLIGENCE.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Modify: task `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`

**Interfaces:**
- Consumes: completed Tasks 1–4
- Produces: fresh verification, actual DB outcome, Browser QA screenshot, runbook, closeout commit

- [ ] **Step 1: Run complete automated verification.**

```bash
.venv/bin/python -m unittest \
  tests.test_nasdaq100_valuation tests.test_sp500_valuation tests.test_market_context_valuation -v
.venv/bin/python -m unittest tests.test_service_contracts -k market_context -v
.venv/bin/python -m py_compile \
  finance/data/nasdaq100_valuation.py \
  app/jobs/ingestion_jobs.py app/jobs/overview_actions.py \
  app/services/overview/nasdaq100_valuation.py \
  app/web/overview/market_context_helpers.py
npm run build --prefix app/web/streamlit_components/market_context_valuation
git diff --check
```

Expected: unittest `OK`, compile/build exit `0`, empty diff check.

- [ ] **Step 2: Run the actual DB repair-plan diagnostic without remote writes.**

```bash
.venv/bin/python - <<'PY'
from finance.data.nasdaq100_valuation import load_nasdaq100_coverage_repair_plan
plan = load_nasdaq100_coverage_repair_plan(months=60)
print(plan["window"])
print(plan["before"])
print("targets", len(plan["targets"]), "unsupported", len(plan["unsupported"]))
PY
```

Record target counts, reason counts, window, and before-ready months in task `RUNS.md`.

- [ ] **Step 3: Run a bounded real collection smoke.**

Run the first small planner batch through `collect_nasdaq100_repair_inputs`. Confirm DB rows persist and the next planner run removes or narrows completed needs. Do not manually insert fixtures into production tables.

- [ ] **Step 4: Run the full synchronous 60-month repair.**

```bash
.venv/bin/python - <<'PY'
from app.jobs.ingestion_jobs import run_repair_nasdaq100_valuation_coverage
result = run_repair_nasdaq100_valuation_coverage(
    months=60,
    progress_callback=lambda row: print(row),
)
print(result)
PY
```

Record status, rows written, before/after ready months, latest/minimum coverage, failed symbols, and unsupported counts. Never report partial success as READY.

- [ ] **Step 5: Verify the DB materialization directly.**

Query the latest 60 `finance_meta.nasdaq100_monthly_valuation` rows. Confirm unique business keys, READY/BLOCKED counts, and latest coverage parity with the service payload.

- [ ] **Step 6: Run desktop and 420px Browser QA.**

Verify one CTA, one event per click, synchronous progress order, partial blocker retention or READY graph transition, S&P regression, console errors, and horizontal overflow. Save one screenshot outside staged paths.

- [ ] **Step 7: Synchronize durable docs and runbook.**

Document the one-click flow, strict gate, resume semantics, actual source gaps, command fallback, and current DB outcome. Keep detailed logs in task docs; root logs receive only 3–5 lines.

- [ ] **Step 8: Run final integration review.**

```bash
git status --short
git diff --check
git diff --stat
git diff --name-status
```

Confirm registry/saved/run-history/generated screenshot/unrelated research paths are unstaged.

- [ ] **Step 9: Commit 5차 closeout.**

```bash
git add .aiworkspace/note/finance/docs \
  .aiworkspace/note/finance/tasks/active/overview-market-context-nasdaq100-coverage-repair-action-v1-20260713 \
  .aiworkspace/note/finance/WORK_PROGRESS.md \
  .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git commit -m "나스닥100 자료 보강 QA와 문서 정리"
```

## Final Completion Gate

- 1차~5차 각각 fresh RED/GREEN 또는 verification evidence와 coherent commit이 있다.
- one-click action이 같은 화면에서 수집, 재계산, cache refresh까지 연결된다.
- actual result가 60/60 READY가 아니면 remaining blocker를 정확히 보고한다.
- unrelated untracked research folder는 처음부터 끝까지 unstaged다.
