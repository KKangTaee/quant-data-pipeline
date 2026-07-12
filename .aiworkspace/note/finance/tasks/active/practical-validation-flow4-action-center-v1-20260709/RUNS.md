# Runs

Commands and QA outcomes will be recorded here.

## 2026-07-09

- `npm install && npm run build && rm -rf node_modules` in `app/web/components/practical_validation_data_action_board/frontend`: passed. npm audit reported 2 existing vulnerabilities, 1 moderate and 1 high; no forced dependency update was applied.
- `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_workspace_builds_data_action_board tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow4_uses_criteria_detail_board tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_data_action_board_react_component_is_ui_only`: failed first as expected for RED on new action-center copy.
- `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_workspace_model_builds_criteria_detail_groups tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow4_uses_criteria_detail_board tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_workspace_builds_data_action_board tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_service_attaches_provider_plan_to_data_action_board tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_data_action_board_react_component_is_ui_only`: passed after implementation.
- `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests`: passed, 74 tests.
- `.venv/bin/python -m py_compile app/services/backtest_practical_validation_workspace.py app/web/backtest_practical_validation/page.py app/web/components/practical_validation_data_action_board/component.py`: passed.
- Browser QA on `http://localhost:8563/backtest`: passed after Practical Validation replay. Confirmed Flow4 contains `데이터 보강 / 수집 실행`, `수집하는 것`, `하지 않는 것`, `실행 후 다음 단계`, and `부족한 외부 데이터 일괄 수집 / 보강`; confirmed old standalone `Provider 보강 액션` and `수집 대상 근거` visible copy are absent. Screenshot saved locally as `practical-validation-flow4-action-center-v1-qa.png`.
- `git diff --check`: passed.
- Final pre-commit rerun: full `BacktestRuntimeContractTests`, `py_compile`, React `npm install && npm run build && rm -rf node_modules`, `git diff --check`, and `git diff --cached --check` passed.
