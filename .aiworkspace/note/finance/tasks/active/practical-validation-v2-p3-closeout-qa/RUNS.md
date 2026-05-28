# Runs

Commands and results will be appended during QA.

## 2026-05-28

- `.venv/bin/python -m py_compile app/runtime/final_selected_portfolios.py app/runtime/__init__.py app/web/final_selected_portfolio_dashboard.py app/web/final_selected_portfolio_dashboard_helpers.py app/services/backtest_evidence_read_model.py app/services/backtest_practical_validation_diagnostics.py app/services/backtest_practical_validation_provider_context.py` — passed.
- `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py` — passed; hard violations none, advisories none.
- `.venv/bin/python -m unittest tests.test_service_contracts` — passed, 46 tests.
- `rg -n "append_selected_portfolio_monitoring_log\\(|append_saved_portfolio_mix\\(|append_practical_validation_result\\(|append_final_selection_decision_v2\\(" app/web/final_selected_portfolio_dashboard.py app/runtime/final_selected_portfolios.py app/services/backtest_evidence_read_model.py tests/test_service_contracts.py` — no matches; selected dashboard P3 read models do not call these append paths.
