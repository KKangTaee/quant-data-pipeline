# Overview Market Context US Stock Freshness Refresh V1 Runs

Last Updated: 2026-07-15

## Context Audit

- Confirmed branch `codex/sub-dev` and preserved unrelated untracked research folder.
- Inspected PER and turnaround collection planners, low-level jobs, Overview facades, Streamlit event bridge, React header/action routing, tests, and current NET DB read model.
- Confirmed both low-level selected-stock jobs currently validate CIK before every scope, while profile/price do not require SEC identity.
- Confirmed reusable last-completed NYSE session logic currently lives privately in `app/services/backtest_price_refresh.py`.
- No provider call, DB write, registry append, source change, or generated artifact was produced during design.

## Detailed Plan

- User approved cached DB UI first, automatic freshness diagnosis, and explicit provider refresh CTA.
- Expanded `PLAN.md` into six TDD tasks covering shared calendar, unified freshness, CIK-independent collection, Streamlit event, React UI, and actual/Browser QA closeout.
- Self-review checked spec coverage, placeholder patterns, interface names, scope exclusions, and step/commit boundaries before implementation.

## Baseline

- Confirmed the current directory is an existing linked worktree on `codex/sub-dev`; no new worktree or branch was created.
- The local `.venv` does not include `pytest`, so the plan commands were corrected to the repository's available `unittest` runner before code changes.
- Baseline: `python -m unittest tests.test_us_stock_valuation tests.test_us_stock_turnaround tests.test_market_context_valuation` -> 96 tests passed.

## 1차 — Freshness / Collection Boundary

- RED: missing `app.services.nyse_calendar`, missing `us_stock_freshness`, missing unified ingestion/facade functions, and missing coverage basis keys all failed for the expected contract reason.
- GREEN commits: `3645fb40` shared NYSE session; `9cc8edd9` unified freshness/basis; `49413211` market-first collection and partial-success facade.
- Focused verification: 111 calendar/freshness/PER/turnaround/Market Context tests passed; target `py_compile` and `git diff --check` passed.
- No provider call, DB write, schema change, registry append, or generated artifact occurred in 1차.

## 2차 — Unified Event / UI

- RED-GREEN으로 Streamlit event를 `refresh_us_stock_data` 하나로 통합하고 old PER/turnaround collection event를 current bridge에서 거부하도록 고정했다.
- React는 header 아래, analysis selector 위에 freshness bar를 한 번만 렌더링한다. child collection button과 visible `rows_written` result strip은 제거했다.
- `가격 기준일`, `재무 기준일`, `공개`를 분리하고 460px 이하에서는 bar와 CTA를 한 열/full-width로 쌓는다.
- Market Context component production build와 관련 source-contract tests를 통과했다.

## 3차 — Actual NET / Browser QA

- Before explicit action: NET expected price `2026-07-14`, stored price `2026-07-07`, profile `2026-02-04`, statement period `2026-03-31` / available `2026-05-08`, scopes `asset_profile, prices`, CIK missing.
- `run_overview_us_stock_data_refresh("NET")` 한 번만 실행했다. selected NET market scopes 7 rows를 저장했고 universe collection은 실행하지 않았다.
- 첫 실행에서 incomplete current-session `2026-07-15` row를 발견해 inclusive end boundary를 TDD로 보정하고 해당 신규 NET row만 삭제했다.
- Corrected after-plan: price `2026-07-14`, profile `2026-07-15`, statement period `2026-03-31` / available `2026-05-08`, status `READY`, gaps `[]`.
- Browser desktop: AAPL stale 상태에서 freshness bar 1개, CTA 1개, header -> bar -> selector 순서를 확인했다. PER/전환 전환 뒤에도 1개이며 새 provider call과 console error가 없었다.
- Browser 420x900: component/outer horizontal overflow 0, freshness bar one-column, CTA full-width를 확인했다.
- Representative screenshot: `/Users/taeho/.codex/visualizations/2026/07/15/019f65a4-445f-79b2-8e17-0e3b374b88b3/us-stock-freshness-desktop.png` (generated, git 제외).

## Verification

- Focused: `.venv/bin/python -m unittest tests.test_nyse_calendar tests.test_us_stock_freshness tests.test_us_stock_valuation tests.test_us_stock_turnaround tests.test_market_context_valuation` -> 114 passed.
- Compile: target six Python modules `py_compile` -> passed.
- React: `npm run build` in `app/web/streamlit_components/market_context_valuation` -> passed.
- Repository discovery: 1,096 tests, 4 failures, 154 errors. Freshness/PER/turnaround/Market Context tests pass isolated; 154 errors are cascading `DeltaGeneratorSingleton instance already exists!` Streamlit unload/reimport isolation failures.
- Unrelated assertion failures:
  - `tests.test_backtest_refactor_boundaries.BacktestRefactorBoundaryTests.test_practical_validation_page_uses_workspace_first_read_flow`
  - `tests.test_backtest_refactor_boundaries.BacktestRefactorBoundaryTests.test_practical_validation_workspace_panel_owns_first_read_surface`
  - `tests.test_service_contracts.OverviewAutomationContractTests.test_overview_market_movers_eod_history_repairs_bad_or_partial_current_symbols`
  - `tests.test_service_contracts.OverviewAutomationContractTests.test_sentiment_react_summary_surface_prioritizes_state_and_freshness`
