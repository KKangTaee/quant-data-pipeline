# Runs

## 2026-07-10

- RED: `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_investment_report_react_component_is_ui_only` failed as expected before implementation because `MetaStrip` / flat layout classes were not present.
- GREEN build: `npm run build` in `app/web/components/final_review_investment_report/frontend` passed and produced refreshed build assets.
- GREEN focused contract: `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_investment_report_react_component_is_ui_only` passed.
- GREEN focused service / React contracts: `.venv/bin/python -m unittest tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_investment_report_react_component_is_ui_only tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_candidate_queue_is_integrated_into_decision_desk tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_first_read_excludes_market_sentiment_panel` passed: 51 tests.
- Compile: `.venv/bin/python -m py_compile app/services/backtest_evidence_read_model.py app/web/backtest_final_review/page.py app/web/components/final_review_investment_report/component.py` passed.
- Diff hygiene: `git diff --check` passed.
- Browser QA: Streamlit `http://localhost:8538/backtest` opened in the in-app browser. Final Review investment report iframe had `fr-invest-report__meta-strip=1`, `fr-invest-report__decision-brief=1`, `fr-invest-report__evidence-row=5`, `fr-invest-report__detail-disclosure=5`, and old first-read `fr-invest-report__facts` / `fr-invest-report__card` counts were 0. Generated screenshot: `final-review-investment-report-flat-ui-v1-qa.png` (not staged).
- Commit: staged only source, docs, task records, and refreshed built component assets; generated screenshot and run history remained unstaged.
