# Practical Validation Flow4 Action Steps V3 Runs

## 2026-07-07

- Failed: `.venv/bin/python -m pytest tests/test_service_contracts.py -k "practical_validation_workspace_model_builds_criteria_detail_groups or practical_validation_workspace_model_builds_issue_queue_items or practical_validation_flow4_uses_criteria_detail_board"`
  - Result: `.venv`에 `pytest` module이 없음.
- Failed: `.venv/bin/python -m unittest tests.test_service_contracts.BacktestServiceContractTests...`
  - Result: 테스트 class명을 잘못 지정함. 실제 class는 `BacktestRuntimeContractTests`.
- Passed: `.venv/bin/python -m py_compile app/services/backtest_practical_validation_workspace.py app/web/backtest_practical_validation/page.py app/web/backtest_practical_validation/components.py`
- Passed: `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_workspace_model_builds_criteria_detail_groups tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_workspace_model_builds_issue_queue_items tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow4_uses_criteria_detail_board`
- Passed: Browser QA on `http://localhost:8512/backtest`
  - Opened `실전 검증 · Practical Validation`.
  - Opened Flow 4 Data Quality `기술 기준 상세`.
  - Confirmed `해결 방법` renders as numbered list items.
  - Screenshot: `practical-validation-flow4-action-steps-v3-action-list-qa.png`.
