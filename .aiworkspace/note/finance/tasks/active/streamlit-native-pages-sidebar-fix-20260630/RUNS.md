# Runs

| Time | Command | Result |
|---|---|---|
| 2026-06-30 | `.venv/bin/python -m pytest tests/test_service_contracts.py -k "legacy_pages_sidebar" -q` | Failed: local venv has no `pytest` module. Re-ran with `unittest`. |
| 2026-06-30 | `.venv/bin/python -m unittest tests.test_service_contracts.BoundaryContractHardeningTests.test_streamlit_shell_does_not_expose_legacy_pages_sidebar` | RED: failed because `app/web/pages/backtest.py` existed. |
| 2026-06-30 | `.venv/bin/python -m unittest tests.test_service_contracts.BoundaryContractHardeningTests.test_streamlit_shell_does_not_expose_legacy_pages_sidebar` | GREEN after moving Backtest shell outside `app/web/pages/`. |
| 2026-06-30 | `.venv/bin/python -m unittest tests.test_service_contracts.BoundaryContractHardeningTests.test_streamlit_shell_does_not_expose_legacy_pages_sidebar` | Passed after removing tracked `app/web/pages/` package. |
| 2026-06-30 | `.venv/bin/python -m py_compile app/web/backtest_page.py app/web/streamlit_app.py app/web/backtest_*.py tests/test_service_contracts.py` | Passed. |
| 2026-06-30 | `.venv/bin/python -m unittest tests.test_service_contracts.BoundaryContractHardeningTests tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests.test_operations_navigation_hides_archive_pages_from_top_level_tabs` | Passed: 15 tests. Existing dependency deprecation warnings from `edgar` and Streamlit cache warning appeared. |
| 2026-06-30 | `git diff --check` | Passed. |
| 2026-06-30 | Browser QA on `http://127.0.0.1:8526/backtest` | Passed: `Workspace / Operations / Reference` top navigation rendered, native sidebar absent, `Page not found` absent. Screenshot: `backtest-startup-top-nav-qa.png`. |
