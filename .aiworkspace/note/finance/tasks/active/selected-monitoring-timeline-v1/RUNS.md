# Selected Monitoring Timeline V1 Runs

Status: Active
Created: 2026-05-28

## Commands

- `.venv/bin/python -m py_compile app/runtime/final_selected_portfolios.py app/runtime/__init__.py app/web/final_selected_portfolio_dashboard.py app/web/final_selected_portfolio_dashboard_helpers.py` - PASS.
- `.venv/bin/python -m unittest tests/test_service_contracts.py` - PASS, 32 tests. Deprecation warnings from `pydantic` / `websockets` only.
- `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py` - PASS, hard violations none, advisories none.
- `git diff --check` - PASS.
- `.venv/bin/python -m streamlit run app/web/streamlit_app.py --server.port 8502 --server.headless true` + Browser smoke - PASS. `Operations > Selected Portfolio Dashboard` loaded with empty registry state and no console errors. Current selected records were 0, so populated Timeline tab interaction was covered by service contract tests rather than browser data.
