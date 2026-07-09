# Runs

Command log for V2-V6.

## V2

- `npm install` in `app/web/components/final_review_investment_report/frontend`
  - Result: passed; npm reported 2 dependency vulnerabilities inherited from the Vite / Streamlit component dependency set.
- `npm run build` in `app/web/components/final_review_investment_report/frontend`
  - Result: passed.
- `.venv/bin/python -m unittest tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_investment_report_turns_packet_into_readable_review tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_investment_report_surfaces_weaknesses_when_blocked tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_investment_report_react_component_is_ui_only`
  - Result: passed.
- `.venv/bin/python -m py_compile app/services/backtest_evidence_read_model.py app/web/backtest_final_review/page.py app/web/components/final_review_investment_report/component.py`
  - Result: passed.
- `.venv/bin/python -m unittest tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_investment_report_react_component_is_ui_only`
  - Result: passed.
- `git diff --check`
  - Result: passed.
- Browser QA on `http://127.0.0.1:8532/backtest`
  - Result: passed. Final Review stage displayed the new `Final Review 투자 검토서` React iframe, including `강점`, `약점`, and `Monitoring 조건`; no Traceback / Exception found.

## V3

- `.venv/bin/python -m unittest tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_level2_review_disposition_splits_stage_roles`
  - Result: passed.
- `npm run build` in `app/web/components/final_review_investment_report/frontend`
  - Result: passed.
- `.venv/bin/python -m unittest tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_level2_review_disposition_splits_stage_roles tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_investment_report_turns_packet_into_readable_review tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_investment_report_surfaces_weaknesses_when_blocked tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_investment_report_react_component_is_ui_only`
  - Result: passed.
- `.venv/bin/python -m py_compile app/services/backtest_evidence_read_model.py app/web/backtest_final_review/page.py app/web/components/final_review_investment_report/component.py`
  - Result: passed.
- `git diff --check`
  - Result: passed.
- Browser QA on `http://127.0.0.1:8532/backtest`
  - Result: passed. Final Review report iframe displayed `Level2 REVIEW 처리 결과`, `Open Review`, and `Monitoring Follow-up`; no Traceback / Exception found.

## V4

- `.venv/bin/python -m unittest tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_scorecard_maps_gate_to_recommendation_taxonomy tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_scorecard_downgrades_blocked_candidate`
  - Result: passed.
- `.venv/bin/python -m unittest tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_investment_report_turns_packet_into_readable_review tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_investment_report_surfaces_weaknesses_when_blocked tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_level2_review_disposition_splits_stage_roles`
  - Result: passed.
- `npm run build` in `app/web/components/final_review_investment_report/frontend`
  - Result: passed.
- `.venv/bin/python -m unittest tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_scorecard_maps_gate_to_recommendation_taxonomy tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_scorecard_downgrades_blocked_candidate tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_investment_report_turns_packet_into_readable_review tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_investment_report_surfaces_weaknesses_when_blocked tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_investment_report_react_component_is_ui_only`
  - Result: passed.
- `.venv/bin/python -m py_compile app/services/backtest_evidence_read_model.py app/web/backtest_final_review/page.py app/web/components/final_review_investment_report/component.py`
  - Result: passed.
- `git diff --check`
  - Result: passed.
- Browser QA on `http://127.0.0.1:8532/backtest`
  - Result: passed. Final Review report iframe displayed `최종 점수 체계`, `/100`, `Selection Gate`, `Evidence Packet`, and `Review Burden`; no Traceback / Exception found.

## V5

- `.venv/bin/python -m unittest tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_save_handoff_summary_separates_judgment_and_monitoring tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_save_handoff_summary_blocks_selected_handoff_when_gate_blocks`
  - Result: passed.
- `npm run build` in `app/web/components/final_review_investment_report/frontend`
  - Result: passed.
- `.venv/bin/python -m unittest tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_save_handoff_summary_separates_judgment_and_monitoring tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_save_handoff_summary_blocks_selected_handoff_when_gate_blocks tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_scorecard_maps_gate_to_recommendation_taxonomy tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_scorecard_downgrades_blocked_candidate tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_investment_report_react_component_is_ui_only`
  - Result: passed.
- `.venv/bin/python -m py_compile app/services/backtest_evidence_read_model.py app/web/backtest_final_review/page.py app/web/components/final_review_investment_report/component.py`
  - Result: passed.
- `git diff --check`
  - Result: passed.
- Browser QA on `http://127.0.0.1:8532/backtest`
  - Result: passed. React report and Final Decision Action displayed Final Review judgment save, Portfolio Monitoring handoff, Record Type, and Order / Auto Rebalance disabled boundary; no Traceback / Exception found.

## V6

- `.venv/bin/python -m unittest tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_weakness_improvement_plan_proposes_verifiable_changes tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_weakness_improvement_plan_keeps_monitoring_for_no_blocker_candidate`
  - Result: passed.
- `npm run build` in `app/web/components/final_review_investment_report/frontend`
  - Result: passed.
- `.venv/bin/python -m unittest tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_weakness_improvement_plan_proposes_verifiable_changes tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_weakness_improvement_plan_keeps_monitoring_for_no_blocker_candidate tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_save_handoff_summary_separates_judgment_and_monitoring tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_scorecard_maps_gate_to_recommendation_taxonomy tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_investment_report_react_component_is_ui_only`
  - Result: passed.
- `.venv/bin/python -m py_compile app/services/backtest_evidence_read_model.py app/web/backtest_final_review/page.py app/web/components/final_review_investment_report/component.py`
  - Result: passed.
- `git diff --check`
  - Result: passed.
- Browser QA on `http://127.0.0.1:8532/backtest`
  - Result: passed. Final Review report iframe displayed `약점 개선안`, current-vs-improved expectation, verification wording, scorecard, handoff boundary, and Level2 REVIEW disposition; no Traceback / Exception found.
- QA screenshot
  - Artifact: `final-review-level3-v6-browser-qa.png` (generated; not staged).
