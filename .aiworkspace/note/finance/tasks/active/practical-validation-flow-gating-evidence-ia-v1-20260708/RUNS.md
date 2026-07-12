# Practical Validation Flow Gating / Evidence IA V1 Runs

## Commands

- 1차 RED: `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_downstream_flows_wait_for_explicit_replay`
  - Result: failed with missing `_has_current_session_replay_result`, confirming downstream flow gate was absent.
- 1차 GREEN focused tests: `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_downstream_flows_wait_for_explicit_replay tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_profile_belongs_to_flow2_execution_setup tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow3_uses_conclusion_summary tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow4_uses_criteria_detail_board`
  - Result: OK, 4 tests.
- 1차 QA: `.venv/bin/python -m py_compile app/web/backtest_practical_validation/page.py`
  - Result: OK.
- 1차 QA: `git diff --check -- app/web/backtest_practical_validation/page.py tests/test_service_contracts.py .aiworkspace/note/finance/tasks/active/practical-validation-flow-gating-evidence-ia-v1-20260708`
  - Result: OK.
- 2차 RED/GREEN: `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_workspace_model_builds_criteria_detail_groups tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow4_uses_criteria_detail_board tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow4_keeps_final_review_items_as_handoff_reference`
  - RED result: failed before implementation because `collection_action` and `pv-provider-data-action` were absent.
  - GREEN result: OK, 3 tests.
- 2차 QA: `.venv/bin/python -m py_compile app/services/backtest_practical_validation_workspace.py app/web/backtest_practical_validation/page.py app/web/backtest_practical_validation/components.py`
  - Result: OK.
- 2차 QA: `git diff --check -- app/services/backtest_practical_validation_workspace.py app/web/backtest_practical_validation/page.py app/web/backtest_practical_validation/components.py tests/test_service_contracts.py`
  - Result: OK.
- 3차 RED/GREEN: `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_workspace_builds_stage_ownership_inventory tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow4_uses_criteria_detail_board tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_workspace_model_builds_criteria_detail_groups`
  - RED result: failed before implementation because `stage_ownership_inventory` and Flow 4 renderer were absent.
  - GREEN result: OK, 3 tests.
- 3차 QA: `.venv/bin/python -m py_compile app/services/backtest_practical_validation_workspace.py app/web/backtest_practical_validation/page.py`
  - Result: OK.
- 3차 QA: `git diff --check -- app/services/backtest_practical_validation_workspace.py app/web/backtest_practical_validation/page.py tests/test_service_contracts.py`
  - Result: OK.
- 4차 RED: `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow4_uses_criteria_detail_board`
  - Result: failed before implementation because `근거 부록` and `수집 대상 근거` were absent and `Provider 부족 근거` was still visible.
- 4차 GREEN focused tests: `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow4_uses_criteria_detail_board tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_workspace_model_builds_criteria_detail_groups tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_workspace_builds_stage_ownership_inventory`
  - Result: OK, 3 tests.
- 4차 QA: `.venv/bin/python -m py_compile app/web/backtest_practical_validation/page.py`
  - Result: OK.
- 4차 QA: `git diff --check -- app/web/backtest_practical_validation/page.py tests/test_service_contracts.py`
  - Result: OK.
- 4차 Browser QA: `http://127.0.0.1:8560/backtest`
  - Result: Practical Validation 첫 진입에서 Flow 2 replay button과 미실행 안내가 보이고, Flow 3 / Flow 4 / `근거 부록`은 현재 세션 replay 전 렌더링되지 않음을 DOM으로 확인했다. QA screenshot은 `practical-validation-flow-gating-evidence-ia-v1-qa.png`로 저장했으며 generated artifact라 stage하지 않는다.
