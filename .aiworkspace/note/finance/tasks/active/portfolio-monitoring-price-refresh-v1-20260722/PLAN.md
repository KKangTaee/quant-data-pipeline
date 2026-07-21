# Portfolio Monitoring Price Refresh V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 현재 선택한 Portfolio Monitoring 그룹의 활성 개별 주식·ETF 일봉을 최근 완료 NYSE 거래일까지 갱신하고, 갱신된 DB 가격으로 공통 기준일과 종합 가치곡선을 다시 계산한다.

**Architecture:** Streamlit-free `portfolio_monitoring.price_refresh` 서비스가 활성 direct-security 종목, DB 최신일, NYSE 완료 거래일을 비교해 refresh plan을 만들고 기존 `run_collect_ohlcv`를 호출한다. Portfolio Monitoring Python page adapter는 plan을 workspace에 투영하고 React event를 정확히 한 번 실행한 뒤 기존 Ingestion run history에 결과를 남긴다. React는 공통 기준일 배너 안에 지연 종목과 명시적 갱신 action만 표시하며 가격이나 최신성을 계산하지 않는다.

**Tech Stack:** Python 3, pandas, MySQL price loader, existing OHLCV ingestion job, Streamlit custom component, React 18, TypeScript, Vitest, unittest.

## Global Constraints

- 1차 대상은 현재 선택 그룹의 `active` / `data_review` direct stock·ETF뿐이다.
- selected strategy, 종료 항목, 재무·ETF holdings·macro 데이터는 수집하지 않는다.
- 목표일은 한국 달력의 오늘이 아니라 `latest_completed_nyse_session()`이다.
- 결측 가격을 carry-forward, interpolation, 임의 종가로 채우지 않는다.
- provider 호출은 사용자 클릭 이후 Python job 경계에서만 실행한다.
- Portfolio Monitoring에는 raw run/row 진단 패널을 만들지 않고 상세 기록은 기존 Ingestion history에 남긴다.

---

### Task 1: Portfolio price freshness plan and refresh service

**Files:**
- Create: `app/services/portfolio_monitoring/price_refresh.py`
- Modify: `app/services/portfolio_monitoring/__init__.py`
- Test: `tests/test_portfolio_monitoring_price_refresh.py`

**Interfaces:**
- Consumes: `MonitoringItemRecord`, `load_price_freshness_summary(symbols, end, timeframe)`, `latest_completed_nyse_session(now)`, `run_collect_ohlcv(symbols, start, end, period, interval, execution_profile)`.
- Produces: `build_portfolio_price_refresh_plan(items, now=None, freshness_loader=None) -> dict[str, Any]`, `run_portfolio_price_refresh(items, now=None, freshness_loader=None, runner=None) -> JobResult`.

- [x] **Step 1: Write failing plan tests**

  Cover direct stock/ETF deduplication, selected-strategy/ended exclusion, latest completed NYSE target, stale/missing classification, seven-day bounded overlap, and up-to-date no-action state.

- [x] **Step 2: Run the focused tests and verify RED**

  Run: `.venv/bin/python -m pytest tests/test_portfolio_monitoring_price_refresh.py -q`

  Expected: FAIL because `app.services.portfolio_monitoring.price_refresh` does not exist.

- [x] **Step 3: Implement the minimal plan service**

  Use the exact public functions above. Return `status`, `eligible`, `target_date`, `current_common_latest`, `symbols`, `stale_symbols`, `missing_symbols`, `excluded_strategy_count`, `collection_start`, `collection_end`, `button_label`, `message`, and compact per-symbol rows.

- [x] **Step 4: Write failing execution tests**

  Assert one existing OHLCV job call with `interval="1d"` and `execution_profile="managed_safe"`; verify post-refresh success, unresolved partial success, no-row failure, and already-current skip.

- [x] **Step 5: Implement execution and verify GREEN**

  Re-read DB freshness after the job. `success` requires no unresolved stale/missing symbols; unresolved symbols produce `partial_success`; no written rows with unresolved symbols produces `failed`.

### Task 2: Python workspace and event bridge

**Files:**
- Modify: `app/web/final_selected_portfolio_dashboard.py`
- Test: `tests/test_portfolio_monitoring_page.py`

**Interfaces:**
- Consumes: Task 1 plan/runner.
- Produces: workspace `price_refresh` projection and `refresh_group_prices` event handling with compact command feedback.

- [x] **Step 1: Write failing page tests**

  Assert the page service exposes `refresh_group_prices`, dispatches it once, appends its job result to existing Ingestion run history, and maps `success`, `partial_success`, `failed`, and `skipped` to user-visible command feedback.

- [x] **Step 2: Run the page tests and verify RED**

  Run: `.venv/bin/python -m pytest tests/test_portfolio_monitoring_page.py -q`

  Expected: FAIL because the refresh service/event is absent.

- [x] **Step 3: Implement the bridge**

  Build the plan from the selected group's persisted items, execute only the event's selected group, append a normalized `portfolio_monitoring_price_refresh` result to `WEB_APP_RUN_HISTORY.jsonl`, and rerun so the workspace and value curve are rebuilt from DB.

- [x] **Step 4: Verify GREEN**

  Run: `.venv/bin/python -m pytest tests/test_portfolio_monitoring_page.py tests/test_portfolio_monitoring_price_refresh.py -q`

### Task 3: React basis-banner action

**Files:**
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/contracts.ts`
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/PortfolioMonitoringWorkbench.tsx`
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/workbenchState.ts`
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/style.css`
- Modify generated tracked build: `app/web/streamlit_components/portfolio_monitoring_workbench/component_static/`
- Test: `app/web/streamlit_components/portfolio_monitoring_workbench/src/workbenchState.test.ts`
- Test: `tests/test_portfolio_monitoring_component.py`

**Interfaces:**
- Consumes: workspace `price_refresh` projection.
- Produces: accessible `보유 종목 가격 최신화` button emitting `{id: "refresh_group_prices", command_id, portfolio_group_id}`.

- [x] **Step 1: Write failing TypeScript and integration-contract tests**

  Assert stale symbol summary copy, no action for up-to-date state, button/event contract, and responsive basis action layout.

- [x] **Step 2: Run tests and verify RED**

  Run: `npm test -- --run` in the component directory and `.venv/bin/python -m pytest tests/test_portfolio_monitoring_component.py -q`.

- [x] **Step 3: Implement the compact action**

  Keep the common-basis explanation, add a compact stale-symbol line and conditional button in the same banner, and preserve keyboard/button semantics at desktop and mobile widths.

- [x] **Step 4: Build and verify GREEN**

  Run: `npm run typecheck`, `npm test -- --run`, and `npm run build` in the component directory, then rerun the Python component contract test.

### Task 4: Integrated verification, actual QA, and durable handoff

**Files:**
- Modify: `.aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Modify: task `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`

**Interfaces:**
- Consumes: completed Tasks 1-3.
- Produces: verified feature, one untracked QA screenshot, concise durable documentation, and a coherent Korean commit.

- [x] **Step 1: Run focused and regression verification**

  Run Python tests for price refresh/page/read model/component, `py_compile`, TypeScript typecheck/test/build, `git diff --check`, and inspect `git status --short`.

- [x] **Step 2: Run actual Browser QA**

  Open Portfolio Monitoring, confirm stale symbols and target date, trigger refresh once when safe, verify the recalculated common date/curve and partial failure copy, then capture one screenshot without staging it.

- [x] **Step 3: Synchronize durable docs**

  Record the direct-security-only scope, last-completed-NYSE target, explicit-click ingestion boundary, post-refresh verification, and remaining selected-strategy exclusion.

- [x] **Step 4: Commit the coherent feature**

  Stage only task-owned code, tracked component build, tests, and finance docs. Do not stage run history, QA screenshots, `.superpowers/`, or other existing untracked artifacts.
