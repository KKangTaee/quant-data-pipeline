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
