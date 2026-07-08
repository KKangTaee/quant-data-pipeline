# Runs

## 2026-07-08

- RED:
  - `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow4_keeps_final_review_items_as_handoff_reference tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow4_uses_criteria_detail_board`
  - Failed as expected: missing `final_review_reference_count`; Flow 4 still mentioned Final Review judgment in main summary.
- GREEN focused:
  - `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow4_keeps_final_review_items_as_handoff_reference tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow4_uses_criteria_detail_board`
  - Passed.
- GREEN related:
  - `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_workspace_model_builds_criteria_detail_groups tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow4_keeps_final_review_items_as_handoff_reference tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_module_plan_preserves_review_input_checks tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_workspace_distinguishes_blocked_from_repairable_gap tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_workspace_model_builds_issue_queue_items tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow4_uses_criteria_detail_board`
  - Passed 6 tests.
- Compile:
  - `.venv/bin/python -m py_compile app/services/backtest_practical_validation_workspace.py app/web/backtest_practical_validation/page.py`
  - Passed.
- Full Backtest service contracts:
  - `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests`
  - Passed 68 tests. Third-party `edgar` deprecation warnings and Streamlit bare-mode warnings only.
- Browser QA:
  - In-app Browser `iab` was unavailable; Chrome extension was listed but no in-app browser target was provided.
  - Fallback local automation checked `http://localhost:8540/backtest`.
  - Verified Flow 4 has `Final Review 참고`, no `Final Review 판단` column, updated `카테고리별 통과 / 보강 필요 / 차단 항목` header, and `통과 / 보강 후 재검증 / 실전 사용 어려움` main outcome copy.
  - Screenshots:
    - `/tmp/practical-validation-flow4-final-review-handoff-v1-final-qa.png`
    - `/tmp/practical-validation-flow4-final-review-reference-v1-final-qa.png`
