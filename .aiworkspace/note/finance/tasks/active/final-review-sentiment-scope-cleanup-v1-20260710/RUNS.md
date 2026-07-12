# Runs

Command log for Final Review sentiment scope cleanup V1.

- `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_first_read_excludes_market_sentiment_panel tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_sentiment_timing_rebalance_boundary_is_documented`
  - RED result: failed because `app/web/backtest_final_review/page.py` still imported and rendered `build_market_sentiment_context_overlay`, and flow docs still described compact Final Review sentiment context.
  - GREEN result: passed after removing the Final Review render path and updating flow docs.
- `.venv/bin/python -m unittest tests.test_service_contracts.PracticalValidationServiceContractTests.test_market_sentiment_overlay_is_context_only_for_practical_validation tests.test_service_contracts.PracticalValidationServiceContractTests.test_market_sentiment_overlay_remains_context_only_on_downstream_surfaces tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_first_read_excludes_market_sentiment_panel tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_sentiment_timing_rebalance_boundary_is_documented tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_decision_desk_model_prioritizes_candidate_status tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_top_summary_is_short_and_action_focused tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_investment_report_react_component_is_ui_only tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests`
  - Result: passed, 53 tests.
- `.venv/bin/python -m py_compile app/web/backtest_final_review/page.py app/web/final_selected_portfolio_dashboard.py app/services/backtest_practical_validation.py`
  - Result: passed.
- `git diff --check`
  - Result: passed.
- Browser QA on `http://127.0.0.1:8536/backtest`
  - Result: Final Review Decision Desk, Candidate Board, and investment report rendered.
  - Confirmed absent: `Market Context`, `시장 심리`, `CNN / AAII detail`, `Timing / Rebalance`.
  - Screenshot: `final-review-sentiment-scope-cleanup-v1-qa.png` (generated artifact, not staged).
