# Risk Parity / Dual Momentum 5B Runs

Commands and verification results will be appended here during implementation.

## 2026-06-10

- `.venv/bin/python -m pytest tests/test_etf_runtime_strategy_contracts.py -q`
  - Result: failed to start because `.venv` does not have `pytest` installed.
- `.venv/bin/python -m unittest tests.test_etf_runtime_strategy_contracts -v`
  - Result: RED confirmed. Failures are missing `Selected Count`, missing `Raw Selected Ticker`, and missing `risk_parity_trend_contract` runtime meta.
- `.venv/bin/python -m unittest tests.test_etf_runtime_strategy_contracts -v`
  - Result: PASS. 4 focused tests cover Risk Parity row diagnostics, Dual Momentum top-N/cash/whipsaw row diagnostics, runtime bundle metadata, and existing Selection History reuse.
- `.venv/bin/python -m unittest tests.test_etf_runtime_strategy_contracts tests.test_global_relative_strength_strategy tests.test_backtest_etf_evidence_expansion tests.test_backtest_etf_current_anchor tests.test_backtest_etf_rerun_matrix -v`
  - Result: PASS. 21 related ETF / GRS / workbench contract tests passed.
- `.venv/bin/python -m py_compile finance/strategy.py app/runtime/backtest.py app/web/backtest_common.py app/web/backtest_result_display.py tests/test_etf_runtime_strategy_contracts.py`
  - Result: PASS.
- `git diff --check`
  - Result: PASS.
- Browser QA: started Streamlit on `http://localhost:8509`, opened `/backtest`, confirmed Backtest / Backtest Analysis rendered, and saved screenshot to `/tmp/risk-parity-dual-momentum-5b-browser-qa.png`.
  - Note: Streamlit printed an existing `use_container_width` deprecation warning during shutdown; no blocking render error was observed.
