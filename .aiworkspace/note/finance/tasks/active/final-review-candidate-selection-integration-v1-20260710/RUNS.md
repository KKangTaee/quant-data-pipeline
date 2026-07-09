# Runs

Command log for Final Review candidate selection integration V1.

- `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_candidate_queue_is_integrated_into_decision_desk`
  - RED result: failed because `app/web/backtest_final_review/page.py` still used standalone `Step 1 / Candidate Board` and did not define `_render_candidate_selection_panel`.
  - GREEN result: passed after moving `Review Queue`, `검토 대상`, and 후보 비교 상세 into a compact candidate selection panel.
- `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_candidate_queue_is_integrated_into_decision_desk tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_decision_desk_model_prioritizes_candidate_status tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_first_read_excludes_market_sentiment_panel tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_top_summary_is_short_and_action_focused tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_investment_report_react_component_is_ui_only`
  - Result: passed, 5 tests.
- `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_candidate_queue_is_integrated_into_decision_desk tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_decision_desk_model_prioritizes_candidate_status tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_first_read_excludes_market_sentiment_panel tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_sentiment_timing_rebalance_boundary_is_documented tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_top_summary_is_short_and_action_focused tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_investment_report_react_component_is_ui_only tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests`
  - Result: passed, 52 tests.
- `.venv/bin/python -m py_compile app/web/backtest_final_review/page.py`
  - Result: passed.
- `git diff --check`
  - Result: passed.
- Browser QA on `http://127.0.0.1:8536/backtest`
  - Result: Final Review shows `후보 현황과 다음 판단`, `Review Queue`, `검토 대상`, `후보 비교 상세`, and `Final Review 투자 검토서`.
  - Confirmed absent: `Step 1`, `Candidate Board`, `Market Context`, and `시장 심리`.
  - Screenshot: `final-review-candidate-selection-integration-v1-qa.png` (generated artifact, not staged).
