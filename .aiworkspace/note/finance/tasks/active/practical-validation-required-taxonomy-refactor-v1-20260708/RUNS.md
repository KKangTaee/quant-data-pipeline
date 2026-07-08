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
