# Risk-On Momentum 5D V2 Runs

Commands and QA results will be recorded during implementation.

## Commands

- `.venv/bin/python -m py_compile finance/indicators.py finance/swing_macro.py finance/swing.py finance/swing_analysis.py finance/transform.py app/runtime/backtest.py app/runtime/history.py app/services/backtest_execution.py app/services/backtest_compare_catalog.py app/web/backtest_single_forms.py app/web/backtest_result_display.py app/web/backtest_history_helpers.py`
  - Result: pass.
- `.venv/bin/python -m unittest tests.test_service_contracts.RiskOnMomentumSwingContractTests`
  - Result: pass, 7 tests.
- `.venv/bin/python -m unittest tests.test_service_contracts`
  - Result: pass, 241 tests.
- Direct DB-backed runtime smoke with Manual `NVDA, MSFT, AAPL, AMZN, META`, `2024-01-01 -> 2024-03-31`, `exit_mode=atr_based`, `macro_filter_mode=ranking_penalty`, `random_iterations=0`, comparison suite on.
  - Result: pass. `comparison_rows=8`, `quality_rows=3`, `trade_rows=9`.
- `git diff --check`
  - Result: pass.
- `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py`
  - Result: pass. Existing generated artifacts remain unstaged.
- `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py`
  - Result: pass.
- Browser QA fallback via isolated `/tmp/rom-v2-qa` Playwright Core + system Chrome.
  - MCP Browser failed because the shared Chrome profile was locked.
  - Computer Use remained pending on Accessibility / Screen Recording permission.
  - Fallback run used `http://localhost:8560/backtest`, Manual `NVDA,MSFT,AAPL,AMZN,META`, `2024-01-01 -> 2024-03-31`, `random_iterations=0`, `scanner_rows_per_day=5`, comparison suite disabled for fast UI rendering.
  - Result: pass. Run completed in 3.723s and `Swing Detail` showed V2 Comparison / Sensitivity / Stability / Trade Causes / Quality Warnings sections.
  - Screenshot: `/tmp/rom-v2-qa/risk-on-momentum-5d-v2-qa.png` (generated QA artifact, not a commit target).
- Follow-up S&P 500 universe mode:
  - `.venv/bin/python -m py_compile app/runtime/backtest.py app/web/backtest_single_forms.py app/web/backtest_common.py`
    - Result: pass.
  - `.venv/bin/python -m unittest tests.test_service_contracts.RiskOnMomentumSwingContractTests`
    - Result: pass, 9 tests.
  - `load_market_cap_universe_members("SP500", universe_limit=500)` smoke.
    - Result: pass. Current DB returned 503 active membership rows.
  - `git diff --check`
    - Result: pass.
  - `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py`
    - Result: pass after root concise logs were reviewed. Existing generated artifacts remain unstaged.
  - UI QA fallback via isolated `/tmp/rom-v2-qa` Playwright Core + system Chrome.
    - MCP Browser failed because the shared Chrome profile was locked.
    - Result: pass. `Risk-On Momentum 5D` form rendered `S&P 500` alongside `Top1000`.
    - Screenshot: `/tmp/rom-v2-qa/risk-on-momentum-sp500-option-qa.png` (generated QA artifact, not a commit target).
