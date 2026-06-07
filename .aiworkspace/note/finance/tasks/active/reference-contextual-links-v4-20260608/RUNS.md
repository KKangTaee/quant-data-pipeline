# Runs

| Date | Command | Result |
|---|---|---|
| 2026-06-08 | `.venv/bin/python -m unittest tests.test_reference_contextual_help` | RED: `app.services.reference_contextual_help` did not exist. |
| 2026-06-08 | `.venv/bin/python -m unittest tests.test_reference_contextual_help` | GREEN: 3 tests passed. |
| 2026-06-08 | `.venv/bin/python -m unittest tests.test_reference_contextual_help tests.test_reference_glossary_catalog tests.test_reference_guides_catalog` | Passed: 11 tests. |
| 2026-06-08 | `.venv/bin/python -m py_compile app/services/reference_contextual_help.py app/web/reference_contextual_help.py app/web/backtest_analysis.py app/web/backtest_practical_validation.py app/web/backtest_final_review.py app/web/operations_overview.py app/web/final_selected_portfolio_dashboard.py` | Passed. |
| 2026-06-08 | Browser QA on `http://localhost:8507/backtest`, `/operations`, `/selected-portfolio-dashboard` | Passed render check: contextual Reference help appeared on Backtest Analysis, Operations Console, and Portfolio Monitoring. No `NameError`. Screenshot: `.playwright-mcp/reference-contextual-links-v4-qa-20260608-expanded.png`. |
| 2026-06-08 | `lsof -iTCP:8507 -sTCP:LISTEN -n -P` after shutdown | No listener. |
| 2026-06-08 | `.venv/bin/python -m unittest tests.test_reference_contextual_help tests.test_reference_glossary_catalog tests.test_reference_guides_catalog tests.test_service_contracts` | Passed: 299 tests. Existing edgar deprecation and Streamlit no-runtime warnings only. |
| 2026-06-08 | `.venv/bin/python -m py_compile app/services/reference_contextual_help.py app/services/reference_glossary_catalog.py app/services/reference_guides_catalog.py app/web/reference_contextual_help.py app/web/backtest_analysis.py app/web/backtest_practical_validation.py app/web/backtest_final_review.py app/web/operations_overview.py app/web/final_selected_portfolio_dashboard.py app/web/streamlit_app.py` | Passed. |
| 2026-06-08 | `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py` | PASS: boundary files 49, service 34, runtime 15, no hard violations or advisories. |
| 2026-06-08 | `git diff --check` | Passed. |
| 2026-06-08 | `lsof -iTCP:8507 -sTCP:LISTEN -n -P` after final cleanup | No listener. |
