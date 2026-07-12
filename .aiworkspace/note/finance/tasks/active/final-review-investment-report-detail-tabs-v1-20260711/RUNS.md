# Runs

## 2026-07-11

- RED: `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_investment_report_react_component_is_ui_only` failed as expected before implementation because `DetailTabs` was not present.
- Build: `npm run build` in `app/web/components/final_review_investment_report/frontend` passed.
- GREEN focused contract: `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_investment_report_react_component_is_ui_only` passed.
- GREEN focused Final Review tests: `.venv/bin/python -m unittest tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_investment_report_react_component_is_ui_only tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_candidate_queue_is_integrated_into_decision_desk tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_first_read_excludes_market_sentiment_panel` passed: 51 tests.
- Compile: `.venv/bin/python -m py_compile app/services/backtest_evidence_read_model.py app/web/backtest_final_review/page.py app/web/components/final_review_investment_report/component.py` passed.
- Diff hygiene: `git diff --check` passed.
- Browser QA: Streamlit `http://localhost:8540/backtest` opened, Final Review report rendered with `detail-tabs=1`, `tablist=1`, `tabs=5`, `activeTabs=1`, `panels=1`, and old `detail-disclosure=0`. Playwright clicked `저장 경계` and `개선 후보`, verifying `aria-selected=true` and panel content switch. Screenshot: `final-review-investment-report-detail-tabs-v1-qa.png` (not staged).
