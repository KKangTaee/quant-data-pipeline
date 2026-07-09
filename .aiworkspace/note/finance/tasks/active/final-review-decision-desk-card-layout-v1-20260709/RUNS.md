# Runs

Command log for Final Review Decision Desk Card Layout V1.

## RED / GREEN

- `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_decision_desk_model_prioritizes_candidate_status`
  - RED result: failed because `route_detail` still contained the concatenated `먼저 볼 후보:` / `이유:` / `다음 행동:` text and `featured_candidate` did not exist.
  - GREEN result: passed after adding `featured_candidate` and 3-column KPI CSS contract.

## QA

- `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_decision_desk_model_prioritizes_candidate_status tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_top_summary_is_short_and_action_focused tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_sentiment_display_is_compact_context_only tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_sentiment_timing_rebalance_boundary_is_documented tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_investment_report_react_component_is_ui_only tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests`
  - Result: passed. 51 tests ran.
- `.venv/bin/python -m py_compile app/web/backtest_final_review/page.py app/web/backtest_final_review/components.py`
  - Result: passed.
- `git diff --check`
  - Result: passed.
- Browser QA: `http://127.0.0.1:8532/backtest`
  - Result: confirmed 3-column KPI grid from computed DOM style, structured candidate fields (`후보`, `왜 먼저 보나`, `추천 근거`, `다음 행동`), no old concatenated route text, and retained Decision Desk shadow.
  - Screenshots: `final-review-decision-desk-card-layout-v1-qa.png`, `final-review-decision-desk-card-layout-v1-full-qa.png` generated artifacts, not staged.
