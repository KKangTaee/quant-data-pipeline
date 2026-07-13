# Nasdaq-100 Scenario History Warmup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Keep the 60-month rolling PER and 95% coverage contracts while enabling Nasdaq-100 1/3/5-year reconstructed scenario history through a user-triggered, resumable, maximum-119-month repair.

**Architecture:** The shared calculator reports exact rolling-warmup readiness. Nasdaq adds actual EPS provenance and a READY-state history repair action; React forwards only action id/nonce, while Python maps it to the bounded 60- or 119-month ingestion job. Existing ingestion, canonical DB, loader, service, and rerun boundaries remain unchanged.

**Tech Stack:** Python 3, pandas, MySQL, Streamlit, React/TypeScript, unittest, Vite

## Global Constraints

- Keep the rolling PER window at exactly `60` months.
- Keep monthly reconstructed actual EPS/price weighted coverage at exactly `95%` or higher for READY.
- A 1/3/5-year display requires exactly `71/95/119` positive READY PER months respectively.
- Screen render remains read-only; only an explicit action may call providers.
- Reuse `Ingestion -> DB -> Loader/Service -> UI`; React must not fetch providers.
- Do not synthesize, interpolate, forward-fill blocked PER, or introduce annual/sector proxy EPS.
- Keep the existing 60-month coverage-blocker action separate from the 119-month history action.
- Preserve filing availability, historical holdings, and observation-month price boundaries.
- Do not stage the unrelated research bundle, generated screenshots, or run-history artifacts.

---

## 이걸 하는 이유?

현재 Nasdaq DB의 positive READY PER는 60개월이라 graph 1은 표시되지만, graph 2의 각 월이 다시 직전 60개월 분포를 요구해 마지막 한 점만 계산된다. SEP vintage 부족이 아니라 rolling PER warmup 부족이므로, 통계를 바꾸지 않고 실제 과거 입력을 최대 119개월까지 보강해야 한다.

### Task 1: Rolling Warmup Diagnostic Contract

**Files:**
- Modify: `app/services/overview/sp500_valuation.py`
- Test: `tests/test_sp500_valuation.py`
- Update: task `STATUS.md`, `RUNS.md`

**Interfaces:**
- Consumes: `calculate_historical_index_scenario(..., visible_months=12, rolling_window=60)`.
- Produces: `reason_code`, `required_history_months`, `available_history_months`, `missing_history_months`, `requested_display_months`, `rolling_window_months`.

- [x] **Step 1: Write the failing 60-month warmup regression.**

```python
result = calculate_historical_index_scenario(
    monthly_pe_frame(60, start="2021-08-01"),
    five_year_sep_history_frame(),
    current_spx={"date": "2026-07-10", "price": 7575.0},
    visible_months=60,
)
self.assertEqual(result["status"], "INSUFFICIENT_HISTORY")
self.assertEqual(result["observation_count"], 1)
self.assertEqual(result["reason_code"], "INSUFFICIENT_ROLLING_PER_WARMUP")
self.assertEqual(result["required_history_months"], 119)
self.assertEqual(result["available_history_months"], 60)
self.assertEqual(result["missing_history_months"], 59)
```

- [x] **Step 2: Run RED.**

Run: `.venv/bin/python -m unittest tests.test_sp500_valuation.Sp500ValuationTests.test_historical_scenario_explains_rolling_warmup_shortfall -v`

Expected: missing diagnostic fields.

- [x] **Step 3: Implement the minimal diagnostic.**

```python
required_history_months = int(rolling_window) + window_months - 1
available_history_months = int(
    frame.loc[
        (frame["observation_month"] <= end_month)
        & frame["trailing_pe"].notna()
        & (frame["trailing_pe"] > 0),
        "observation_month",
    ].nunique()
)
```

Attach the six fields to the normal return and set `INSUFFICIENT_ROLLING_PER_WARMUP` only when the result is not READY and available history is below required history.

- [x] **Step 4: Run GREEN and S&P regression.**

Run: `.venv/bin/python -m unittest tests.test_sp500_valuation -v`

Expected: all tests pass, including existing 12/36/60-point READY assertions.

- [x] **Step 5: Commit.**

Commit message: `적정구간 rolling 이력 부족 계약 추가`

### Task 2: 119-Month Repair Window Contract

**Files:**
- Modify: `finance/data/nasdaq100_valuation.py`
- Modify: `app/jobs/overview_actions.py`
- Test: `tests/test_nasdaq100_valuation.py`
- Test: `tests/test_market_context_valuation.py`
- Update: task `STATUS.md`, `RUNS.md`

**Interfaces:**
- Produces: `NASDAQ100_SCENARIO_HISTORY_REPAIR_MONTHS = 119`.
- Reuses: `nasdaq100_repair_window` and `run_repair_nasdaq100_valuation_coverage(months=...)`.
- Preserves: Overview facade default `months=60`.

- [x] **Step 1: Write failing exact-window and facade tests.**

```python
self.assertEqual(NASDAQ100_SCENARIO_HISTORY_REPAIR_MONTHS, 119)
self.assertEqual(
    nasdaq100_repair_window(end_month="2026-07-31", months=119),
    ("2016-09-01", "2026-07-31"),
)
```

```python
result = run_overview_nasdaq100_valuation_repair(months=119)
runner.assert_called_once_with(months=119, progress_callback=None)
self.assertEqual(result["details"]["requested_months"], 119)
```

- [x] **Step 2: Run RED.**

Run: `.venv/bin/python -m unittest tests.test_nasdaq100_valuation tests.test_market_context_valuation -v`

Expected: the constant and requested-month evidence are absent.

- [x] **Step 3: Add the constant and dynamic facade evidence.**

```python
NASDAQ100_SCENARIO_HISTORY_REPAIR_MONTHS = 119
details["requested_months"] = int(months)
details["purpose"] = f"Market Context Nasdaq-100 {int(months)}-month valuation/history repair"
```

- [x] **Step 4: Run GREEN.**

Run: `.venv/bin/python -m unittest tests.test_nasdaq100_valuation tests.test_market_context_valuation -v`

Expected: all focused tests pass and 60-month behavior remains compatible.

- [x] **Step 5: Commit.**

Commit message: `나스닥100 적정구간 119개월 보강 계약 추가`

### Task 3: Nasdaq History Action And EPS Provenance

**Files:**
- Modify: `app/services/overview/nasdaq100_valuation.py`
- Test: `tests/test_market_context_valuation.py`
- Test: `tests/test_service_contracts.py`
- Update: task `STATUS.md`, `RUNS.md`, `NOTES.md`

**Interfaces:**
- Produces `index_scenario.history_repair_action` only when valuation is READY and rolling warmup is insufficient.
- Produces Nasdaq `earnings_scenario.eps_source`, `eps_source_quality`, `eps_basis_date`.

- [x] **Step 1: Write failing service assertions.**

```python
self.assertEqual(
    model["index_scenario"]["history_repair_action"]["id"],
    "repair_nasdaq100_history_119m",
)
self.assertEqual(model["index_scenario"]["history_repair_action"]["months"], 119)
self.assertEqual(
    model["earnings_scenario"]["eps_source"],
    "QQQ 구성종목 실제 희석 EPS 재구성",
)
self.assertEqual(model["earnings_scenario"]["eps_source_quality"], "reconstructed_actual")
self.assertEqual(model["earnings_scenario"]["eps_basis_date"], "2026-07-01")
```

- [x] **Step 2: Run RED.**

Run: `.venv/bin/python -m unittest tests.test_market_context_valuation -v`

Expected: READY Nasdaq has no history action and calculated earnings omit source metadata.

- [x] **Step 3: Add provenance and conditional history action.**

```python
earnings.update({
    "eps_source": "QQQ 구성종목 실제 희석 EPS 재구성",
    "eps_source_quality": evidence.get("eps_source_quality"),
    "eps_basis_date": evidence.get("eps_basis_date")
        or evidence.get("earnings_available_through"),
})
```

The action id is `repair_nasdaq100_history_119m`, label is `1·3·5년 적정구간 자료 보강`, and detail explains the 60-month rolling warmup. Do not expose it after all three options are READY.

- [x] **Step 4: Run GREEN and focused service contracts.**

Run: `.venv/bin/python -m unittest tests.test_market_context_valuation -v`

Expected: all tests pass.

- [x] **Step 5: Commit.**

Commit message: `나스닥100 적정구간 상태와 EPS 출처 보완`

### Task 4: Python/React History Repair UX

**Files:**
- Modify: `app/web/overview/market_context_helpers.py`
- Modify: `app/web/streamlit_components/market_context_valuation/src/MarketContextValuation.tsx`
- Modify: `app/web/streamlit_components/market_context_valuation/src/style.css` only if narrow-layout styling needs it.
- Test: `tests/test_market_context_valuation.py`
- Update: task `STATUS.md`, `RUNS.md`

**Interfaces:**
- Maps `repair_nasdaq100_60m` to `60` and `repair_nasdaq100_history_119m` to `119`.
- `ScenarioHistoryChart` consumes instrument/action/result/pending props and emits the selected action id.

- [x] **Step 1: Write failing Python and TSX contract tests.**

```python
handled = market_context_helpers._handle_market_context_valuation_event(
    {"event": {"id": "repair_nasdaq100_history_119m", "nonce": 456}},
    state={}, run_action=run_action, store_result=Mock(),
    clear_cache=Mock(), rerun=Mock(),
)
self.assertTrue(handled)
run_action.assert_called_once_with(119)
```

Assert the component contains `적정구간 계산 이력이 부족합니다`, `required_history_months`, `available_history_months`, and dynamic QQQ history labels.

- [x] **Step 2: Run RED.**

Run: `.venv/bin/python -m unittest tests.test_market_context_valuation -v`

Expected: only the 60-month event is accepted and the empty state still blames SEP.

- [x] **Step 3: Generalize Python routing.**

```python
NASDAQ100_REPAIR_MONTHS_BY_ACTION = {
    "repair_nasdaq100_60m": 60,
    "repair_nasdaq100_history_119m": 119,
}
```

Change `_run_nasdaq100_repair_for_ui(*, months: int)` and injected `run_action` so the handler passes the selected month count. Include `requested_months` in the repair reflection and dynamic status copy.

- [x] **Step 4: Implement the actionable history empty state.**

For the selected period render `5년 흐름에는 119개월이 필요하지만 현재 60개월이 준비됐습니다.` and emit `repairAction.id`. Replace history-only hardcoded `SPX` with `instrument.proxy_symbol`; replace the earnings fallback with `EPS 출처 미확정`.

- [x] **Step 5: Run GREEN and build.**

Run: `.venv/bin/python -m unittest tests.test_market_context_valuation -v`

Run: `npm run build --prefix app/web/streamlit_components/market_context_valuation`

Run: `.venv/bin/python -m py_compile app/web/overview/market_context_helpers.py`

Expected: tests/build/compile pass.

- [x] **Step 6: Commit.**

Commit message: `나스닥100 적정구간 보강 화면 연결`

### Task 5: Actual Repair, QA, Documentation, And Closeout

**Files:**
- Update: task `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`
- Update: `.aiworkspace/note/finance/docs/INDEX.md`
- Update: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Update: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Update: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Update: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`

**Interfaces:**
- Full success returns 1y/3y/5y history with 12/36/60 points.
- Honest partial success retains required/current/missing evidence and never synthesizes blocked months.

- [ ] **Step 1: Run a read-only 119-month repair plan.**

Call `load_nasdaq100_coverage_repair_plan(months=119)` and print only window, target count, unsupported count, and before READY/BLOCKED counts.

- [ ] **Step 2: Run a bounded smoke and actual 119-month repair.**

Call `run_overview_nasdaq100_valuation_repair(months=119)` through the canonical ingestion path. Do not write repository temp artifacts.

- [ ] **Step 3: Verify DB/service parity.**

Check unique observation months, READY/BLOCKED counts, latest coverage, and each history option's point/required/available fields. Full success is 119 READY months and 12/36/60 points; otherwise document exact remaining free-source gaps.

- [ ] **Step 4: Run full automated verification.**

Run: `.venv/bin/python -m unittest tests.test_nasdaq100_valuation tests.test_sp500_valuation tests.test_market_context_valuation -v`

Run: `.venv/bin/python -m unittest tests.test_service_contracts -v`

Run: `.venv/bin/python -m py_compile finance/data/nasdaq100_valuation.py app/jobs/ingestion_jobs.py app/jobs/overview_actions.py app/services/overview/sp500_valuation.py app/services/overview/nasdaq100_valuation.py app/web/overview/market_context_helpers.py`

Run: `npm run build --prefix app/web/streamlit_components/market_context_valuation`

Run: `git diff --check`

- [ ] **Step 5: Perform desktop and 420px Browser QA.**

Verify graph 1, graph 2 options/action, QQQ EPS source/labels, pending/result reflection, zero console errors, and zero horizontal overflow. Keep one screenshot outside the repository and do not stage it.

- [ ] **Step 6: Synchronize docs and task evidence.**

Record actual counts, test commands, Browser QA, residual gaps, and the distinction between 60-month coverage repair and 119-month history warmup. Keep root logs concise.

- [ ] **Step 7: Review and commit closeout.**

Run: `git status --short`

Run: `git diff --cached --check`

Commit message: `나스닥100 적정구간 이력 보강 QA와 문서 정리`
