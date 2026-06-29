# GTAA Result Cadence Monthly Valuation Runs

## 2026-06-29

- `.venv/bin/python -m unittest tests.test_gtaa_strategy.GtaaStrategyCadenceTests.test_latest_common_row_can_extend_month_end_rows_to_current_available_trade_date -v`
  - Expected red: `ImportError` for missing `append_latest_common_row`.
- `.venv/bin/python -m unittest tests.test_gtaa_strategy -v`
  - Passed 3 tests after implementation.
- `.venv/bin/python -m py_compile finance/transform.py finance/sample.py finance/strategy.py`
  - Passed.
- DB-backed GTAA smoke via `app.runtime.backtest.run_gtaa_backtest_from_db(...)`
  - Requested end: `2026-06-29`
  - Actual result end: `2026-03-16`
  - Result rows: `123`
  - CAGR: `0.23368276308709346`
  - MDD: `-0.17708079132505594`
  - Last row `Rebalancing=False`, `Raw Selected Ticker=[IAU, SOXX]`, `Signal Investable Ticker=[IAU, SOXX]`, `Next Ticker=[IAU, SOXX]`.
- DB latest price check for GTAA universe:
  - `IAU=2026-05-29`, `IEF=2026-05-29`, `MTUM=2026-03-16`, `QQQ=2026-06-18`, `QUAL=2026-03-16`, `SOXX=2026-03-16`, `TLT=2026-06-18`, `USMV=2026-03-16`.
- `.venv/bin/python -m unittest tests.test_gtaa_strategy tests.test_global_relative_strength_strategy tests.test_etf_runtime_strategy_contracts -v`
  - Passed 11 tests.
- `.venv/bin/python -m unittest tests.test_service_contracts.BacktestPresetCatalogContractTests tests.test_service_contracts.BacktestRuntimeContractTests -v`
  - Passed 16 tests.
- `git diff --check`
  - Passed.
