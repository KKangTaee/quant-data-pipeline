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

## V3

- `.venv/bin/python -m unittest tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_scorecard_maps_level2_review_roles_to_dimension_impacts`
  - GREEN result: passed after mapping Level2 REVIEW roles to score dimensions and review impact records.
- `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_investment_report_react_component_is_ui_only`
  - RED result: failed because `Level2 REVIEW 점수 영향` was missing from the React source.
- `npm run build` in `app/web/components/final_review_investment_report/frontend`
  - Result: passed.
- `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_investment_report_react_component_is_ui_only`
  - GREEN result: passed.
- `.venv/bin/python -m unittest tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_detailed_scorecard_exposes_weighted_dimensions tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_level2_review_disposition_splits_stage_roles tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_scorecard_maps_gate_to_recommendation_taxonomy tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_scorecard_downgrades_blocked_candidate`
  - Result: passed.
- `.venv/bin/python -m py_compile app/services/backtest_evidence_read_model.py app/web/components/final_review_investment_report/component.py`
  - Result: passed.
- `git diff --check`
  - Result: passed.

## V4

- `.venv/bin/python -m unittest tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_scorecard_applies_caps_before_route_decision`
  - RED result: failed with empty `score_limits` before implementation.
  - GREEN result: passed after adding hard blocker, selected-route not-ready, gate review-required, and excessive open-review caps.
- `.venv/bin/python -m unittest tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_detailed_scorecard_exposes_weighted_dimensions tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_scorecard_maps_level2_review_roles_to_dimension_impacts tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_scorecard_maps_gate_to_recommendation_taxonomy tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_scorecard_downgrades_blocked_candidate`
  - Result: passed.
- `.venv/bin/python -m py_compile app/services/backtest_evidence_read_model.py`
  - Result: passed.
- `git diff --check`
  - Result: passed.

## V5

- `.venv/bin/python -m unittest tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_investment_report_exposes_selection_rationale_and_required_notes`
  - RED result: failed with missing `selection_rationale` before implementation.
  - GREEN result: passed after adding selection rationale and required decision note read models.
- `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_investment_report_react_component_is_ui_only`
  - RED result: failed because `최종 선택 사유` was missing from the React source.
  - GREEN result: passed after adding the selection rationale and decision-note panels.
- `npm run build` in `app/web/components/final_review_investment_report/frontend`
  - Result: passed.
- `.venv/bin/python -m unittest tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_investment_report_exposes_selection_rationale_and_required_notes tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_scorecard_applies_caps_before_route_decision tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_detailed_scorecard_exposes_weighted_dimensions tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_scorecard_maps_gate_to_recommendation_taxonomy`
  - Result: passed.
- `.venv/bin/python -m py_compile app/services/backtest_evidence_read_model.py app/web/components/final_review_investment_report/component.py`
  - Result: passed.
- `git diff --check`
  - Result: passed.

## V6

- `.venv/bin/python -m unittest tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_investment_report_react_component_is_ui_only`
  - Result: passed. 47 focused tests ran.
- `npm run build` in `app/web/components/final_review_investment_report/frontend`
  - Result: passed.
- `.venv/bin/python -m py_compile app/services/backtest_evidence_read_model.py app/web/backtest_final_review/page.py app/web/components/final_review_investment_report/component.py`
  - Result: passed.
- `git diff --check`
  - Result: passed.
- `.venv/bin/streamlit run app/web/streamlit_app.py --server.port 8532 --server.address 127.0.0.1 --server.headless true`
  - Browser QA result: opened `http://127.0.0.1:8532/backtest`, selected `최종 검토 · Final Review`, and confirmed the investment report iframe rendered `세부 점수`, `Level2 REVIEW 점수 영향`, `최종 선택 사유`, `판단 저장 전 메모`, and `점수 제한` with no Traceback / Exception text.
  - Screenshot artifacts: `final-review-detailed-scorecard-v6-qa.png`, `final-review-detailed-scorecard-v6-top-qa.png`, `final-review-detailed-scorecard-v6-rationale-qa.png` (generated QA artifacts, not staged).
