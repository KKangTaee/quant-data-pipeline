# Recheck Comparison Review Signal Policy V1 Runs

Status: Active
Created: 2026-05-29

## Runs

| Command | Result |
|---|---|
| `.venv/bin/python -m py_compile app/runtime/final_selected_portfolios.py app/runtime/__init__.py app/web/final_selected_portfolio_dashboard.py app/web/final_selected_portfolio_dashboard_helpers.py` | Passed |
| `.venv/bin/python -m unittest tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests` | Passed; 24 tests. Existing `edgar` deprecation warnings appeared |
| `git diff --check` | Passed |
| `.venv/bin/python -m unittest tests.test_service_contracts` | Passed; 122 tests. Existing `edgar` deprecation warnings appeared |
| `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py` | Passed |
| `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py` | Passed; generated `finance/.DS_Store` remains unstaged |
| `.venv/bin/python -m streamlit run app/web/streamlit_app.py --server.port 8502 --server.headless true` | Passed; app started for local smoke, then stopped |
| Playwright smoke `http://localhost:8502/selected-portfolio-dashboard` | Passed; Selected Portfolio Dashboard loaded with 0 selected rows and no console errors |

## Notes

- Direct `.venv/bin/streamlit` had a stale shebang pointing to another worktree; module execution through `.venv/bin/python -m streamlit` was used for smoke.
- in-app Browser `iab` was unavailable, so Playwright fallback was used for local smoke.
