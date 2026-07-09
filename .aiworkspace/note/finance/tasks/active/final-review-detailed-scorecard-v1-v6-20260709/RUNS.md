# Runs

Command log for Final Review detailed scorecard V1-V6.

## V1

- `.venv/bin/python -m unittest tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_detailed_scorecard_exposes_weighted_dimensions`
  - RED result: failed with `KeyError: 'dimensions'` before implementation.
  - GREEN result: passed after adding weighted dimensions.
- `.venv/bin/python -m unittest tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_scorecard_maps_gate_to_recommendation_taxonomy tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_scorecard_downgrades_blocked_candidate`
  - Result: passed.
- `.venv/bin/python -m py_compile app/services/backtest_evidence_read_model.py`
  - Result: passed.
- `git diff --check`
  - Result: passed.

## V2

- `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_investment_report_react_component_is_ui_only`
  - RED result: failed because `세부 점수` was missing from the React source.
- `npm run build` in `app/web/components/final_review_investment_report/frontend`
  - Result: passed.
- `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_investment_report_react_component_is_ui_only`
  - GREEN result: passed.
- `.venv/bin/python -m py_compile app/web/components/final_review_investment_report/component.py`
  - Result: passed.
- `git diff --check`
  - Result: passed.
