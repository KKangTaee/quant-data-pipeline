# Risk-On Momentum 5D V1 Runs

## Commands

- `.venv/bin/python -m py_compile finance/transform.py finance/loaders/futures.py finance/swing.py`
  - Result: pass.
- Synthetic core smoke through `finance.swing.run_risk_on_momentum_backtest`
  - Result: 36 result rows, 8 trade rows, 30 scanner rows.
  - Found and fixed `holding_days` log semantics so max-hold exits show signal holding days, not D+1 execution day count.
- `.venv/bin/python -m unittest tests.test_service_contracts.RiskOnMomentumSwingContractTests`
  - Result: pass, 3 tests.
- `.venv/bin/python -m py_compile finance/swing.py app/runtime/backtest.py app/services/backtest_execution.py app/web/backtest_single_forms.py app/web/backtest_result_display.py app/web/backtest_history_helpers.py app/services/backtest_compare_catalog.py`
  - Result: pass.
- Manual DB-backed smoke with `NVDA, MSFT, AAPL, AMZN, META`, `2024-01-01 -> 2024-03-31`, `random_iterations=0`
  - First result: failed on pandas `merge_asof` datetime dtype mismatch between price dates and statement availability timestamps.
  - Fix: normalize feature `date`, `period_end`, and `latest_available_at` to `datetime64[ns]`.
  - Re-run result: pass. `Risk-On Momentum 5D`, 61 result rows, 9 trade rows, 17 scanner rows, 187 macro score rows, generated artifact under `.aiworkspace/note/finance/backtest_artifacts/`.
- Top1000 resolver smoke
  - Result: 1000 symbols from `market_cap_universe_members:TOP1000`, first symbols `AAPL, NVDA, GOOGL, GOOG, MSFT`.
- Browser QA on `http://localhost:8560/backtest`
  - Scenario: `Backtest Analysis > Single Strategy > Risk-On Momentum 5D`, switch Universe Mode to `Manual`, input `NVDA,MSFT,AAPL,AMZN,META`, run `2024-01-01 -> 2024-03-31` with `random_iterations=0` and `scanner_rows_per_day=5`.
  - Result: pass. Form rendered, Manual ticker input updated immediately, run completed in 2.945s, result had 61 rows / 5 assets, and `Swing Detail` tab rendered.
  - Screenshot: `risk-on-momentum-5d-qa.png` (generated QA artifact, not staged).
- `git diff --check`
  - Result: pass.
- `.venv/bin/python -m py_compile finance/transform.py finance/swing.py finance/loaders/futures.py finance/loaders/__init__.py app/runtime/backtest.py app/runtime/__init__.py app/runtime/history.py app/services/backtest_execution.py app/services/backtest_compare_catalog.py app/web/backtest_strategy_catalog.py app/web/backtest_single_strategy.py app/web/backtest_single_forms.py app/web/backtest_common.py app/web/backtest_result_display.py app/web/backtest_history_helpers.py tests/test_service_contracts.py`
  - Result: pass.
- `.venv/bin/python -m unittest tests.test_service_contracts`
  - Result: pass, 237 tests.
