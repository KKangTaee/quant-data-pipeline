# Runs

## 2026-07-08

- RED: `.venv/bin/python -m unittest tests.test_service_contracts.ValidationEfficacyAuditContractTests`
  - Expected failure: `validation_efficacy`가 runtime / benchmark / provider / survivorship row를 포함하고 있었다.
- GREEN: `.venv/bin/python -m unittest tests.test_service_contracts.ValidationEfficacyAuditContractTests`
  - Result: 9 tests passed.
- RED: `.venv/bin/python -m unittest tests.test_service_contracts.PracticalValidationServiceContractTests`
  - Expected failure: module planner가 아직 `Validation Efficacy`와 `Validation Strength / Robustness` 결합 taxonomy를 사용했다.
- GREEN: `.venv/bin/python -m unittest tests.test_service_contracts.PracticalValidationServiceContractTests`
  - Result: 25 tests passed.
- RED: `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow4_uses_criteria_detail_board`
  - Expected failure: 화면에 `Practical Validation Workbench`, `Input Evidence`, `Practical Diagnostics` 같은 영어 중심 제목이 남아 있었다.
- GREEN: `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow4_uses_criteria_detail_board`
  - Result: 1 test passed.
- RED: `.venv/bin/python -m unittest tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_integrated_investability_gate_all_ready_allows_selected_route tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_gate_policy_blocks_selected_route_on_validation_efficacy_needs_input tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_evidence_rows_expand_current_and_wrapped_decision_shapes`
  - Expected failure: Final Review gate가 `validation_efficacy`를 아직 `Validation Efficacy` / runtime 중심 문구로 표시했다.
- GREEN: `.venv/bin/python -m unittest tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests`
  - Result: 32 tests passed.
