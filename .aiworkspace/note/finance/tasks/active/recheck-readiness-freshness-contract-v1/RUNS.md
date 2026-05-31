# Recheck Readiness / Freshness Contract V1 Runs

Status: Complete
Created: 2026-05-29

## Runs

| Command | Result |
|---|---|
| `.venv/bin/python -m py_compile app/runtime/final_selected_portfolios.py app/runtime/__init__.py app/web/final_selected_portfolio_dashboard.py app/web/final_selected_portfolio_dashboard_helpers.py` | Passed |
| `.venv/bin/python -m unittest tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests` | Passed; 18 tests. Existing `edgar` deprecation warnings appeared |
| `git diff --check` | Passed |
| `.venv/bin/python -m unittest tests.test_service_contracts` | Passed; 116 tests. Existing `edgar` deprecation warnings appeared |
| `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py` | Passed |
| `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py` | Passed; `finance/.DS_Store` remains generated / unstaged |
