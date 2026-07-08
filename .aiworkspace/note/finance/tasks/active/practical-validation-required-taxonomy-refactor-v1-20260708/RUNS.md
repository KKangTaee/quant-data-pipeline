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
- GREEN: `.venv/bin/python -m unittest tests.test_service_contracts.ValidationEfficacyAuditContractTests tests.test_service_contracts.PracticalValidationServiceContractTests tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow4_uses_criteria_detail_board tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests`
  - Result: 67 tests passed.
- GREEN: `.venv/bin/python -m py_compile app/services/backtest_validation_efficacy.py app/services/backtest_practical_validation_modules.py app/services/backtest_practical_validation_board_registry.py app/services/backtest_practical_validation_workspace.py app/web/backtest_practical_validation/page.py app/services/backtest_evidence_read_model.py`
  - Result: passed.
- GREEN: `git diff --check`
  - Result: passed.
- BROWSER QA: `.venv/bin/python -m streamlit run app/web/streamlit_app.py --server.port 8537 --server.headless true --server.runOnSave false --server.fileWatcherType none`
  - In-app Browser plugin did not expose `iab`; available browser list only showed a Chrome extension backend.
  - Fallback Playwright QA opened `http://localhost:8537/backtest`, clicked `실전 검증 · Practical Validation`, and verified `실전 검증 센터`, `검증 방법론 강도`, `검증 방법론`, `강건성` are visible.
  - Verified `Practical Validation Workbench`, `Input Evidence`, `Reference help`, and market sentiment overlay are not visible on the Practical Validation entry path.
  - Screenshot: `/tmp/practical-validation-required-taxonomy-refactor-qa.png`.
