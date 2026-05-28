# RUNS - Practical Validation V2

Status: Active
Last Updated: 2026-05-28

## P2 Closeout Verification

- `.venv/bin/python -m unittest tests/test_service_contracts.py`
  - Result: passed, 34 tests.
  - Scope: Practical Validation service contracts, provider context, look-through evidence, robustness lab, Final Review evidence read model, selected-route gate.
- `.venv/bin/python -m py_compile app/services/backtest_practical_validation.py app/services/backtest_practical_validation_diagnostics.py app/services/backtest_practical_validation_provider_context.py app/services/backtest_practical_validation_stress_sensitivity.py app/web/backtest_practical_validation.py app/web/backtest_final_review.py app/web/final_selected_portfolio_dashboard.py`
  - Result: passed.
- `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py`
  - Result: passed; hard violations none, advisories none.
