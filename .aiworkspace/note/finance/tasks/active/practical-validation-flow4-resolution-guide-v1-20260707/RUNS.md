# Runs

## 2026-07-07

- `.venv/bin/python -m py_compile app/services/backtest_practical_validation_workspace.py app/services/backtest_practical_validation_modules.py app/web/backtest_practical_validation/page.py app/web/backtest_practical_validation/workspace_panel.py`
  - Result: pass
- `.venv/bin/python -m unittest tests.test_service_contracts.PracticalValidationServiceContractTests.test_validation_module_gate_blocks_missing_required_runtime_replay tests.test_service_contracts.PracticalValidationServiceContractTests.test_validation_module_gate_skips_construction_risk_for_single_factor_source tests.test_service_contracts.PracticalValidationServiceContractTests.test_validation_module_gate_blocks_selected_route_preflight_gaps tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_workspace_model_builds_criteria_detail_groups tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_workspace_model_builds_issue_queue_items tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow4_uses_criteria_detail_board`
  - Result: pass, 6 tests
- `.venv/bin/python -m unittest tests.test_backtest_refactor_boundaries.BacktestRefactorBoundaryTests.test_practical_validation_page_uses_workspace_first_read_flow`
  - Result: pass, 1 test
- `git diff --check`
  - Result: pass
- Browser QA: `http://localhost:8512/backtest` > `실전 검증 · Practical Validation` > Flow4.
  - Result: pass
  - Verified: detail cards render `검증한 것`, `부족한 것`, `해야 할 일`, `보강 위치`.
  - Verified: Data Coverage card uses `Flow4 > 데이터 > 데이터 품질 / 편향 통제 상세 / 실행: Flow4 > Provider / Data 보강 액션`.
  - Screenshot: `practical-validation-flow4-resolution-guide-qa.png` (generated, not committed).
