# Runtime Package Boundary Runs

## 2026-05-20

- Inspected `app/web/runtime` file list, line counts, and current `app.web.runtime` imports.
- 5-01: moved `app/web/runtime/*.py` to `app/runtime/*.py`.
- 5-01: rewrote Python imports from `app.web.runtime` to `app.runtime`.
- 5-02: moved `app/web/backtest_candidate_library_helpers.py` to `app/runtime/candidate_library.py`.
- Updated boundary lint to scan both `app/services` and `app/runtime`.
- `.venv/bin/python -m py_compile app/runtime/*.py app/services/*.py app/web/backtest_common.py app/web/backtest_candidate_library.py app/web/backtest_candidate_review.py app/web/backtest_candidate_review_helpers.py app/web/backtest_final_review.py app/web/backtest_final_review_helpers.py app/web/backtest_history.py app/web/backtest_history_helpers.py app/web/backtest_portfolio_proposal.py app/web/backtest_portfolio_proposal_helpers.py app/web/backtest_practical_validation.py app/web/final_selected_portfolio_dashboard.py app/web/final_selected_portfolio_dashboard_helpers.py app/web/overview_dashboard_helpers.py tests/test_service_contracts.py .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py` passed.
- `.venv/bin/python -m unittest tests/test_service_contracts.py` passed 16 tests.
- `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py` passed.
