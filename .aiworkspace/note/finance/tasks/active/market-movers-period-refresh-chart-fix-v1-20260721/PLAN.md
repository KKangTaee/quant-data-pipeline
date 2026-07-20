# Market Movers Period Refresh And Chart Fix V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Weekly/Monthly Market Movers가 최신 완료 시장일까지 bounded overlap으로 가격 이력을 보강하고, 기간 이력이 부족한 신규 상장 종목을 왜곡 없이 제외하며, 재무 tooltip과 가격 X축을 판독 가능하게 만든다.

**Architecture:** 가격 갱신 범위와 종목 상태 분류는 `app/jobs/overview_actions.py`가 소유하고 기존 `run_collect_ohlcv -> finance_price.nyse_price_history UPSERT` 경로를 재사용한다. 랭킹 eligibility와 제외 사유는 `app/services/overview/market_movers.py`가 실제 start/end 가격 경계를 기준으로 결정하며, React component는 서버 payload를 바꾸지 않고 tooltip placement와 adaptive price ticks만 계산한다.

**Tech Stack:** Python 3.12, pandas, Streamlit, MySQL, yfinance ingestion facade, React 18, TypeScript, Vite, pytest

## Global Constraints

- 최신 완료 시장일은 `latest_completed_nyse_session()`을 기준으로 한다.
- Weekly는 필수 1주 + overlap 1주, Monthly는 필수 1개월 + overlap 1개월만 bounded refresh한다.
- yfinance `end`는 provider adapter에서 inclusive 보정을 한 번만 수행한다.
- 신규 상장 종목의 상장 이후 수익률을 선택 기간 전체 수익률처럼 섞지 않는다.
- 빈 provider 응답은 기존 DB 가격행을 삭제하지 않는다.
- 별도 운영 진단 패널은 만들지 않는다.
- 사용자 registry, saved JSONL, run history, 기존 generated QA artifact를 stage하지 않는다.
- 구현은 failing test를 먼저 확인한 뒤 최소 코드로 통과시킨다.

---

### Task 1: Bounded Period Refresh Window And Limited Retry

**Files:**
- Modify: `tests/test_service_contracts.py`
- Modify: `app/jobs/overview_actions.py`

**Interfaces:**
- Consumes: `latest_completed_nyse_session()`, `_load_market_movers_eod_freshness()`, `_load_market_movers_limited_history_symbols()`, `run_collect_ohlcv()`
- Produces: `_market_movers_eod_period_window(*, as_of_date: date, period: str) -> dict[str, date]`
- Produces: `_market_movers_eod_refresh_plan(...)` fields `required_start`, `range_start`, `range_end`, `limited_retry_symbols`, `period_ineligible_symbols`, `collection_batches`

- [ ] **Step 1: Write failing period-window tests**

```python
def test_market_movers_weekly_refresh_uses_one_week_overlap(self) -> None:
    window = overview_actions._market_movers_eod_period_window(
        as_of_date=date(2026, 7, 20), period="weekly"
    )
    self.assertEqual(window["required_start"], date(2026, 7, 13))
    self.assertEqual(window["fetch_start"], date(2026, 7, 6))
    self.assertEqual(window["fetch_end"], date(2026, 7, 20))

def test_market_movers_monthly_refresh_uses_one_month_overlap(self) -> None:
    window = overview_actions._market_movers_eod_period_window(
        as_of_date=date(2026, 7, 20), period="monthly"
    )
    self.assertEqual(window["required_start"], date(2026, 6, 20))
    self.assertEqual(window["fetch_start"], date(2026, 5, 20))
    self.assertEqual(window["fetch_end"], date(2026, 7, 20))
```

- [ ] **Step 2: Run the window tests and confirm RED**

Run: `.venv/bin/python -m pytest tests/test_service_contracts.py -k 'weekly_refresh_uses_one_week_overlap or monthly_refresh_uses_one_month_overlap' -q`

Expected: FAIL because `_market_movers_eod_period_window` does not exist.

- [ ] **Step 3: Implement calendar-safe period window calculation**

```python
def _market_movers_shift_months(value: date, months: int) -> date:
    month_index = value.year * 12 + value.month - 1 + months
    target_year, target_month_index = divmod(month_index, 12)
    target_month = target_month_index + 1
    return date(target_year, target_month, min(value.day, monthrange(target_year, target_month)[1]))

def _market_movers_eod_period_window(*, as_of_date: date, period: str) -> dict[str, date]:
    if period == "weekly":
        required_start = as_of_date - timedelta(weeks=1)
        fetch_start = required_start - timedelta(weeks=1)
    elif period == "monthly":
        required_start = _market_movers_shift_months(as_of_date, -1)
        fetch_start = _market_movers_shift_months(required_start, -1)
    else:
        required_start = _market_movers_shift_months(as_of_date, -12)
        fetch_start = _market_movers_shift_months(required_start, -12)
    return {"required_start": required_start, "fetch_start": fetch_start, "fetch_end": as_of_date}
```

- [ ] **Step 4: Run the Step 2 tests and confirm GREEN**

Expected: `2 passed`.

- [ ] **Step 5: Write failing limited-history classification tests**

```python
def test_market_movers_limited_symbol_retries_when_latest_price_is_stale(self) -> None:
    plan = overview_actions._market_movers_eod_refresh_plan(
        ["HONA"],
        {"HONA": {"first_date": date(2026, 6, 29), "latest_date": date(2026, 7, 10), "close": 100, "volume": 1000}},
        as_of_date=date(2026, 7, 20), period="weekly", known_limited_symbols={"HONA"},
    )
    self.assertEqual(plan["limited_retry_symbols"], ["HONA"])
    self.assertEqual(plan["range_start"], date(2026, 7, 6))
    self.assertEqual(plan["range_end"], date(2026, 7, 20))

def test_market_movers_current_new_listing_is_period_ineligible(self) -> None:
    plan = overview_actions._market_movers_eod_refresh_plan(
        ["HONA"],
        {"HONA": {"first_date": date(2026, 6, 29), "latest_date": date(2026, 7, 20), "close": 100, "volume": 1000}},
        as_of_date=date(2026, 7, 20), period="monthly", known_limited_symbols={"HONA"},
    )
    self.assertEqual(plan["period_ineligible_symbols"], ["HONA"])
    self.assertEqual(plan["collection_batches"], [])
```

- [ ] **Step 6: Run the classification tests and confirm RED**

Run: `.venv/bin/python -m pytest tests/test_service_contracts.py -k 'limited_symbol_retries_when_latest_price_is_stale or current_new_listing_is_period_ineligible' -q`

Expected: FAIL because limited symbols are skipped before stale classification and no period-ineligible state exists.

- [ ] **Step 7: Implement period-boundary classification and one bounded batch**

```python
window = _market_movers_eod_period_window(as_of_date=as_of_date, period=period)
period_ineligible = first_date is None or first_date > window["required_start"]
if latest_date is None:
    missing_symbols.append(symbol)
elif quality_reasons:
    repair_symbols.append(symbol)
elif latest_date < as_of_date:
    stale_symbols.append(symbol)
    if symbol in known_limited:
        limited_retry_symbols.append(symbol)
elif period_ineligible:
    period_ineligible_symbols.append(symbol)
else:
    current_symbols.append(symbol)
```

Create one `collection_batches` row for de-duplicated stale, repair, missing, and limited-retry symbols using `fetch_start` and inclusive `fetch_end`. Remove lifetime `row_count < 10/45` as a permanent skip gate.

- [ ] **Step 8: Update the collector call**

```python
for batch in plan["collection_batches"]:
    collect_results.append(dict(run_collect_ohlcv(
        list(batch["symbols"]),
        start=batch["start_date"].isoformat(),
        end=batch["end_date"].isoformat(),
        period=collection_period,
        interval="1d",
        execution_profile="managed_safe",
    )))
```

Remove the separate period-only missing-symbol call so provider `end` is adjusted only inside `get_ohlcv`.

- [ ] **Step 9: Run focused refresh tests**

Run: `.venv/bin/python -m pytest tests/test_service_contracts.py -k 'market_movers_eod' -q`

Expected: all selected tests pass with bounded range and inclusive end.

- [ ] **Step 10: Commit Task 1**

```bash
git add app/jobs/overview_actions.py tests/test_service_contracts.py
git commit -m "변동 종목 기간별 가격 보강 범위를 수정"
```

---

### Task 2: Period-Ineligible Ranking Evidence

**Files:**
- Modify: `tests/test_service_contracts.py`
- Modify: `app/services/overview/market_movers.py`

**Interfaces:**
- Consumes: global resolved `start_date`, `end_date`, universe symbols, `finance_price.nyse_price_history`
- Produces: `_load_price_date_bounds(*, symbols: list[str], query_fn: QueryFn) -> dict[str, dict[str, str]]`
- Produces: missing row reason `selected period history unavailable`

- [ ] **Step 1: Write a failing new-listing exclusion test**

```python
def test_market_movers_marks_new_listing_without_full_period_history(self) -> None:
    from app.services.overview import market_movers

    def query_fn(db_name, sql, params=None):
        if "AND `date` IN" in sql:
            return [
                {"symbol": "AAA", "date": date(2026, 6, 18), "price": 100.0, "volume": 1000},
                {"symbol": "AAA", "date": date(2026, 7, 20), "price": 110.0, "volume": 1100},
                {"symbol": "HONA", "date": date(2026, 7, 20), "price": 120.0, "volume": 900},
            ]
        if "MIN(`date`) AS first_price_date" in sql:
            return [{
                "symbol": "HONA",
                "first_price_date": date(2026, 6, 29),
                "latest_price_date": date(2026, 7, 20),
            }]
        if "FROM nyse_symbol_lifecycle" in sql or "FROM market_data_issue" in sql:
            return []
        raise AssertionError(sql)

    return_rows, missing_rows = market_movers._build_return_rows(
        universe=[
            {"symbol": "AAA", "long_name": "Alpha", "sector": "Technology", "industry": "Software"},
            {"symbol": "HONA", "long_name": "Honeywell Aerospace", "sector": "Industrials", "industry": "Aerospace & Defense"},
        ],
        universe_code="SP500",
        start_date="2026-06-18",
        end_date="2026-07-20",
        query_fn=query_fn,
    )

    self.assertEqual([row["symbol"] for row in return_rows], ["AAA"])
    self.assertEqual(missing_rows[0]["Reason"], "selected period history unavailable")
    self.assertEqual(missing_rows[0]["First Price Date"], "2026-06-29")
    self.assertEqual(missing_rows[0]["Latest Price Date"], "2026-07-20")
```

- [ ] **Step 2: Run the exact new test and confirm RED**

Run: `.venv/bin/python -m pytest tests/test_service_contracts.py -k 'marks_new_listing_without_full_period_history' -q`

Expected: FAIL because only `missing start price` and latest-price evidence exist.

- [ ] **Step 3: Add price-bound loading and explicit period evidence**

```python
def _load_price_date_bounds(*, symbols: list[str], query_fn: QueryFn) -> dict[str, dict[str, str]]:
    if not symbols:
        return {}
    placeholders = ",".join(["%s"] * len(symbols))
    rows = query_fn(
        "finance_price",
        f"""
        SELECT
            symbol,
            MIN(`date`) AS first_price_date,
            MAX(`date`) AS latest_price_date
        FROM nyse_price_history
        WHERE symbol IN ({placeholders})
          AND timeframe = %s
          AND COALESCE(adj_close, close) IS NOT NULL
        GROUP BY symbol
        """,
        list(symbols) + ["1d"],
    )
    return {
        str(row["symbol"]).upper(): {
            "first_price_date": _iso_date(row.get("first_price_date")) or "",
            "latest_price_date": _iso_date(row.get("latest_price_date")) or "",
        }
        for row in rows
    }
```

Load bounds only for missing candidates. If `start_price is None`, `end_price is not None`, and `first_price_date > start_date`, use `selected period history unavailable`; otherwise preserve provider-gap reasons.

- [ ] **Step 4: Run focused snapshot tests**

Run: `.venv/bin/python -m pytest tests/test_service_contracts.py -k 'market_movers_snapshot or period_history_unavailable' -q`

Expected: HONA-like rows are excluded with an explicit reason, while FDXF-like rows with both boundary prices remain returnable regardless of lifetime row count.

- [ ] **Step 5: Commit Task 2**

```bash
git add app/services/overview/market_movers.py tests/test_service_contracts.py
git commit -m "변동 종목 신규 상장 기간 제외 근거를 추가"
```

---

### Task 3: Tooltip Placement And Price X-Axis

**Files:**
- Modify: `tests/test_overview_market_movers_decision_ui.py`
- Modify: `app/web/streamlit_components/market_movers_workbench/src/MarketMoversWorkbench.tsx`
- Modify: `app/web/streamlit_components/market_movers_workbench/src/style.css`
- Rebuild: `app/web/streamlit_components/market_movers_workbench/component_static/`

**Interfaces:**
- Produces: `priceChartTickIndexes(points: ChartPoint[], range: string) -> number[]`
- Produces: tooltip attributes `data-placement="above|below"` and clamped horizontal positions

- [ ] **Step 1: Write failing source-contract tests**

```python
assert "function priceChartTickIndexes" in source
assert 'className="mm-decision__chart-ticks mm-decision__chart-ticks--price"' in source
assert 'data-placement={priceTooltipPlacement}' in source
assert 'data-placement={financialTooltipPlacement}' in source
assert '.mm-decision__chart-tooltip[data-placement="below"]' in style
assert ".mm-decision__chart-ticks--price" in style
```

- [ ] **Step 2: Run the UI contract test and confirm RED**

Run: `.venv/bin/python -m pytest tests/test_overview_market_movers_decision_ui.py -k 'price_axis or tooltip_clamp' -q`

Expected: FAIL because adaptive ticks and placement attributes do not exist.

- [ ] **Step 3: Implement adaptive tick selection**

```typescript
function priceChartTickIndexes(points: ChartPoint[], range: string) {
  const targetCount = { "1M": 5, "3M": 4, "6M": 7, "1Y": 7 }[range] || 5;
  if (points.length <= targetCount) return points.map((_, index) => index);
  return Array.from(new Set(Array.from(
    { length: targetCount },
    (_, index) => Math.round((index * (points.length - 1)) / (targetCount - 1)),
  )));
}
```

Render actual trading-date ticks at coordinate percentages. Use `MM-DD` for 1M and `YYYY-MM` for longer ranges. Always keep first and last.

- [ ] **Step 4: Implement safe tooltip placement**

Use `below` in the top 72px safety zone, otherwise `above`. Clamp fixed-chart X with CSS `clamp(72px, <percentage>, calc(100% - 72px))`. Clamp financial tooltip X to `scrollLeft + 72` through `scrollLeft + clientWidth - 72`.

```css
.mm-decision__chart-tooltip[data-placement="below"] {
  transform: translate(-50%, 0);
}

.mm-decision__chart-ticks--price {
  margin: 0 28px;
}
```

- [ ] **Step 5: Run all decision UI tests**

Run: `.venv/bin/python -m pytest tests/test_overview_market_movers_decision_ui.py -q`

Expected: all tests pass.

- [ ] **Step 6: Rebuild React**

Run: `npm run build --prefix app/web/streamlit_components/market_movers_workbench`

Expected: Vite production build succeeds and updates the hashed static assets.

- [ ] **Step 7: Commit Task 3**

```bash
git add tests/test_overview_market_movers_decision_ui.py app/web/streamlit_components/market_movers_workbench/src app/web/streamlit_components/market_movers_workbench/component_static
git commit -m "변동 종목 차트 축과 툴팁을 개선"
```

---

### Task 4: Integration Verification, Server Reload, And Documentation

**Files:**
- Create: `.aiworkspace/note/finance/tasks/active/market-movers-period-refresh-chart-fix-v1-20260721/STATUS.md`
- Create: `.aiworkspace/note/finance/tasks/active/market-movers-period-refresh-chart-fix-v1-20260721/NOTES.md`
- Create: `.aiworkspace/note/finance/tasks/active/market-movers-period-refresh-chart-fix-v1-20260721/RUNS.md`
- Create: `.aiworkspace/note/finance/tasks/active/market-movers-period-refresh-chart-fix-v1-20260721/RISKS.md`
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify: `.aiworkspace/note/finance/docs/runbooks/OVERVIEW_MARKET_INTELLIGENCE.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`

**Interfaces:**
- Consumes: Task 1–3 code and test/build output
- Produces: reproducible verification record, latest Streamlit server, Browser QA screenshot

- [ ] **Step 1: Run focused Python verification**

```bash
.venv/bin/python -m pytest tests/test_overview_market_movers_decision_ui.py tests/test_overview_market_movers_read_models.py -q
.venv/bin/python -m pytest tests/test_service_contracts.py -k 'market_movers_eod or market_movers_snapshot' -q
```

- [ ] **Step 2: Run static checks**

```bash
.venv/bin/python -m py_compile app/jobs/overview_actions.py app/services/overview/market_movers.py app/web/overview/market_movers_helpers.py
git diff --check
```

Expected: no error output.

- [ ] **Step 3: Verify DB-backed preflight without provider writes**

Record Weekly/Monthly `as_of_date`, bounded range, selected/current/period-ineligible counts, and HONA status. Do not run the 503-symbol provider refresh during automated verification.

- [ ] **Step 4: Restart the known Streamlit QA server**

Validate PID, command, and port before stopping it. Restart port 8530 with `--server.runOnSave true` and confirm the process start time is later than the implementation commit.

- [ ] **Step 5: Perform Browser QA**

Open Overview > 변동 종목, confirm the two refresh actions remain separate, inspect Weekly timing, verify price intermediate ticks and hover, verify a top-edge financial tooltip, repeat at narrow width, and save one representative screenshot outside staged source files.

- [ ] **Step 6: Synchronize task and durable docs**

Record implementation facts in `STATUS/NOTES/RUNS/RISKS`, keep root logs concise, and update the roadmap/runbook without staging generated artifacts or user JSONL.

- [ ] **Step 7: Commit Task 4**

```bash
git add .aiworkspace/note/finance/tasks/active/market-movers-period-refresh-chart-fix-v1-20260721 .aiworkspace/note/finance/docs/ROADMAP.md .aiworkspace/note/finance/docs/runbooks/OVERVIEW_MARKET_INTELLIGENCE.md .aiworkspace/note/finance/WORK_PROGRESS.md .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git commit -m "변동 종목 기간 갱신과 차트 수정을 마무리"
```

## Self-Review

- Spec coverage: bounded overlap, inclusive provider end, limited retry, period-ineligible exclusion, distinct actions, tooltip clipping, price X-axis, server reload, Browser QA가 Task 1–4에 대응한다.
- Placeholder scan: 각 변경 단계에 실제 함수명, 테스트 assertion, 명령, 기대 결과가 있으며 `TBD`나 포괄적인 후속 구현 문구가 없다.
- Type consistency: refresh 날짜는 `date`, preflight는 ISO string, price-bound 결과는 ISO string, React tick index는 `number[]`로 일치한다.
