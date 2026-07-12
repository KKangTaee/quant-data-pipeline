# Runs

Command log for Final Review top UX cleanup V1-V4.

## Baseline

- `.venv/bin/python -m unittest tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_investment_report_react_component_is_ui_only`
  - Result: passed. 47 tests ran.
- `git diff --check`
  - Result: passed.

## V3

- `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_sentiment_display_is_compact_context_only`
  - RED result: failed with `ImportError: cannot import name '_build_final_review_sentiment_display_model'`.
  - GREEN result: passed after adding the compact sentiment display model and replacing the lane-grid overlay.
- `.venv/bin/python -m unittest tests.test_service_contracts.PracticalValidationServiceContractTests.test_market_sentiment_overlay_is_context_only_for_practical_validation tests.test_service_contracts.PracticalValidationServiceContractTests.test_market_sentiment_overlay_remains_context_only_on_downstream_surfaces tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_sentiment_display_is_compact_context_only tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_decision_desk_model_prioritizes_candidate_status tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_top_summary_is_short_and_action_focused tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_investment_report_react_component_is_ui_only tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests`
  - Result: passed. 52 tests ran.
- `.venv/bin/python -m py_compile app/web/backtest_final_review/page.py`
  - Result: passed.
- `git diff --check`
  - Result: passed.

## V4

- `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_sentiment_timing_rebalance_boundary_is_documented`
  - RED result: failed because `PORTFOLIO_SELECTION_FLOW.md` did not yet document compact Final Review sentiment context.
  - GREEN result: passed after updating Portfolio Selection / Backtest UI flow docs and ROADMAP with the research-only boundary.
- `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_top_summary_is_short_and_action_focused`
  - RED result: failed after adding a source assertion for the shared Backtest selector because it still mentioned `Selected Dashboard` and the old run-history caption.
  - GREEN result: passed after changing the shared Backtest selector to `Portfolio Monitoring` and removing the old run-history caption.
- `.venv/bin/python -m unittest tests.test_service_contracts.PracticalValidationServiceContractTests.test_market_sentiment_overlay_is_context_only_for_practical_validation tests.test_service_contracts.PracticalValidationServiceContractTests.test_market_sentiment_overlay_remains_context_only_on_downstream_surfaces tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_sentiment_display_is_compact_context_only tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_sentiment_timing_rebalance_boundary_is_documented tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_decision_desk_model_prioritizes_candidate_status tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_top_summary_is_short_and_action_focused tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_investment_report_react_component_is_ui_only tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests.test_selected_dashboard_handoff_review_links_selected_final_review_rows tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests.test_selected_dashboard_handoff_review_blocks_without_selected_route`
  - Result: passed. 55 tests ran.
- `.venv/bin/python -m py_compile app/web/backtest_final_review/page.py app/web/backtest_page.py app/web/backtest_final_review_helpers.py app/services/backtest_evidence_read_model.py app/runtime/backtest/read_models/final_selected_portfolios.py app/services/backtest_selected_route_preflight.py app/services/backtest_practical_validation_diagnostics.py app/services/reference_contextual_help.py`
  - Result: passed.
- `git diff --check`
  - Result: passed.
- Browser QA: `http://127.0.0.1:8532/backtest` fresh Streamlit server.
  - Result: confirmed Final Review Decision Desk, compact sentiment context, `Operations > Portfolio Monitoring` route wording, no top Reference help, no old run-history caption, and no `Selected Dashboard` top/handoff wording.
  - Screenshot: `final-review-top-ux-cleanup-v1-v4-qa.png` generated artifact, not staged.

## V2

- `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_decision_desk_model_prioritizes_candidate_status`
  - RED result: failed with `ImportError: cannot import name '_build_final_review_decision_desk_model'`.
  - GREEN result: passed after adding the decision desk display model and removing the top 1~5 flow-card guide.
- `.venv/bin/python -m py_compile app/web/backtest_final_review/page.py`
  - Result: passed.
- `.venv/bin/python -m unittest tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_investment_report_react_component_is_ui_only tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_top_summary_is_short_and_action_focused tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_decision_desk_model_prioritizes_candidate_status`
  - Result: passed. 49 tests ran.
- `git diff --check`
  - Result: passed.

## V1

- `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_top_summary_is_short_and_action_focused`
  - RED result: failed with `ImportError: cannot import name '_build_final_review_top_summary'`.
  - GREEN result: passed after adding the top summary helper and removing contextual Reference help from the first-read intro.
- `.venv/bin/python -m py_compile app/web/backtest_final_review/page.py`
  - Result: passed.
- `.venv/bin/python -m unittest tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_investment_report_react_component_is_ui_only tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_top_summary_is_short_and_action_focused`
  - Result: passed. 48 tests ran.
- `git diff --check`
  - Result: passed.
