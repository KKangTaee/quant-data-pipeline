# Runs

- Diagnosis: actual AMD/AAPL/NVDA/META service payloads were Graph 2 READY with complete
  scenario prices but `current_price=None` on 2026-08-02.
- Boundary reproduction: AMD as-of 2026-07-31 had current price 476.15; as-of 2026-08-01
  created a missing-price August row and lost current price.
- Pre-change baseline: `tests.test_us_stock_valuation tests.test_market_context_valuation`
  ran 76 tests with 0 failures, confirming the month-rollover case was not covered.
- TDD RED: the month-rollover regression returned `current_price=None` instead of `209.0`.
- TDD RED: the default loader call omitted `as_of_date="2026-07-31"`.
- TDD GREEN: both new focused regression tests passed after the service change.
- Regression: `.venv/bin/python -m unittest tests.test_nyse_calendar
  tests.test_us_stock_freshness tests.test_us_stock_valuation
  tests.test_market_context_valuation -v` ran 92 tests with 0 failures.
- Actual DB: AMD returned Graph 2 `READY`, current price `476.1499938964844`, price basis and
  scenario as-of `2026-07-31`, current TTM EPS `3.05`, and freshness `READY`.
- Browser QA: AMD Graph 2 rendered current `476`, baseline `690`, conservative `224`, optimistic
  `2,356`; the empty-data notice count and browser error count were both zero.
- QA screenshot: `/Users/taeho/.codex/visualizations/2026/08/01/019fbfa7-9668-7ae2-9dec-5bfe162a73a0/overview-us-stock-latest-session-valuation-fix-qa.png`
- Static verification: `py_compile` and `git diff --check` passed.
- Independent review: no functional or freshness regression finding; reviewer independently
  reran all 92 targeted tests successfully.
- Full repository discovery: `.venv/bin/python -m unittest discover -s tests` ran 1,910 tests
  with 12 failures and 298 errors. The reported failures were outside this task, dominated by
  repeated Streamlit `DeltaGeneratorSingleton` initialization and existing Backtest/macro contract
  assertions; no failure referenced either changed valuation file.
- Post-discovery isolation: the 92-test valuation/calendar/freshness/market-context suite was rerun
  in a clean process and passed with 0 failures.
