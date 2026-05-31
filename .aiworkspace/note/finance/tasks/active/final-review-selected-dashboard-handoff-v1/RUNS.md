# Runs

## 2026-05-31

- `.venv/bin/python -m py_compile app/runtime/final_selected_portfolios.py app/runtime/__init__.py app/web/backtest_final_review.py app/web/final_selected_portfolio_dashboard.py app/web/final_selected_portfolio_dashboard_helpers.py tests/test_service_contracts.py`
  - Result: pass.
- `.venv/bin/python -m unittest tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests.test_selected_dashboard_handoff_review_links_selected_final_review_rows tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests.test_selected_dashboard_handoff_review_blocks_without_selected_route tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests.test_selected_dashboard_handoff_review_surfaces_blocked_dashboard_contract`
  - Result: pass, 3 tests.
- `.venv/bin/python -m unittest tests.test_service_contracts`
  - Result: pass, 207 tests.
- `git diff --check`
  - Result: pass.
- `.venv/bin/streamlit run app/web/streamlit_app.py --server.port 8503 --server.headless true`
  - Result: failed because the script shebang pointed at another worktree venv path.
- `.venv/bin/python -m streamlit run app/web/streamlit_app.py --server.port 8503 --server.headless true`
  - Result: app started on `http://localhost:8503`.
- Browser QA:
  - Navigated through top nav to `Backtest > Final Review` and confirmed `Selected Dashboard Handoff` renders with no console errors.
  - Navigated through top nav to `Operations > Selected Portfolio Dashboard` and confirmed `Final Review Handoff` renders with no console errors.
  - Console warnings were existing Vega / empty chart warnings from Overview data, not handoff errors.
  - Screenshot: `final-review-selected-dashboard-handoff-v1-qa.png`.
