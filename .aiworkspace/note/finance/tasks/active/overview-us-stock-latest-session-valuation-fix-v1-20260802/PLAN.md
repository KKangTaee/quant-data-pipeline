# Overview US Stock Latest Session Valuation Fix V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 월초·주말에도 미국 개별종목 Graph 2가 가장 최근 완료 거래일의 저장 종가를 현재 가격으로 표시하게 한다.

**Architecture:** Overview service가 최근 완료 NYSE 세션을 loader cutoff로 전달한다. 월별 PIT 결과에서는 최신 가격 보유 행을 current valuation basis로 선택해 stale DB의 월경계도 안전하게 처리하고 기존 freshness service가 지연 상태를 계속 소유한다.

**Tech Stack:** Python 3.12, pandas, unittest, Streamlit service read model, MySQL read-only loader

## Global Constraints

- DB schema, collector, React layout과 사용자 copy는 변경하지 않는다.
- current price와 current TTM EPS는 같은 price-bearing monthly row에서 가져온다.
- 최신 완료 거래일보다 미래인 price/filing evidence를 사용하지 않는다.
- 기존 사용자 변경과 generated artifact는 stage하지 않는다.

---

### Task 1: Month-Rollover Regression Contract

**Files:**
- Modify: `tests/test_us_stock_valuation.py`

**Interfaces:**
- Consumes: `build_us_stock_valuation_read_model(*, selected_symbol, loaded_inputs)`
- Produces: 월초 결측 가격 행에서도 직전 가격 월을 current basis로 쓰는 회귀 계약

- [x] **Step 1: Write the failing test**

  `_ready_loaded_inputs()` 마지막에 `2026-08-01 / missing_price` 월을 추가하고,
  `index_scenario.current_price`, `as_of`, `earnings_scenario.current_ttm_eps`,
  `basis.price.price_basis_date`가 모두 직전 complete 월과 일치한다고 단언한다.

- [x] **Step 2: Run test to verify it fails**

  Run: `.venv/bin/python -m unittest tests.test_us_stock_valuation.UsStockValuationServiceTests.test_service_uses_latest_price_month_when_current_calendar_month_has_no_trade -v`

  Expected: FAIL because `index_scenario.current_price` is `None`.

- [x] **Step 3: Write minimal implementation**

  `app/services/overview/us_stock_valuation.py`에 최신 양수 price와 basis date가 있는
  monthly row selector를 추가하고 scenario/current EPS/basis price가 이를 사용하게 한다.

- [x] **Step 4: Run test to verify it passes**

  Run the same focused unittest; expected PASS.

### Task 2: Completed-Session Loader Cutoff

**Files:**
- Modify: `app/services/overview/us_stock_valuation.py`
- Modify: `tests/test_us_stock_valuation.py`

**Interfaces:**
- Consumes: `app.services.nyse_calendar.latest_completed_nyse_session()`
- Produces: `load_us_stock_valuation_inputs(symbol, as_of_date=<completed session>)`

- [x] **Step 1: Write the failing test**

  실제 service builder를 실행하되 DB query만 격리하고, 주말 완료 세션 날짜가 loader
  cutoff로 전달되며 반환 payload의 current price가 마지막 저장 가격이라고 단언한다.

- [x] **Step 2: Run test to verify it fails**

  Run: `.venv/bin/python -m unittest tests.test_us_stock_valuation.UsStockValuationServiceTests.test_service_defaults_loader_cutoff_to_latest_completed_nyse_session -v`

  Expected: FAIL because loader currently receives only the symbol.

- [x] **Step 3: Write minimal implementation**

  selected symbol의 default load path에서만 completed session ISO date를 전달한다.
  주입된 `loaded_inputs`는 그대로 사용해 deterministic replay 계약을 보존한다.

- [x] **Step 4: Run test to verify it passes**

  Run the same focused unittest; expected PASS.

### Task 3: Regression, Actual DB QA, And Closeout

**Files:**
- Modify: task `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`
- Inspect/update only if durable meaning changes: `docs/data/TABLE_SEMANTICS.md`

**Interfaces:**
- Consumes: completed service implementation
- Produces: verified AMD/current-price payload and durable task handoff

- [x] **Step 1: Run focused regression**

  Run: `.venv/bin/python -m unittest tests.test_nyse_calendar tests.test_us_stock_freshness tests.test_us_stock_valuation tests.test_market_context_valuation -v`

- [x] **Step 2: Run static checks**

  Run: `.venv/bin/python -m py_compile app/services/overview/us_stock_valuation.py`

  Run: `git diff --check`

- [x] **Step 3: Run actual DB and Browser QA**

  Confirm AMD Graph 2 is READY, current price is positive, basis date is 2026-07-31,
  and capture one generated screenshot without staging it.

- [x] **Step 4: Align docs and commit**

  Record RED/GREEN/regression/QA evidence in the active task. Update canonical docs only if
  product or data meaning changed, then stage only owned files and commit in Korean.

## Stop Condition

Stop when the two regression contracts pass, AMD actual payload/chart uses the latest completed
session price, focused regressions and Browser QA pass, documentation is aligned, and only task-owned
files are committed.
