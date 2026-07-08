# Runs

- `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_workspace_model_builds_criteria_detail_groups tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_module_plan_preserves_review_input_checks tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_workspace_distinguishes_blocked_from_repairable_gap`
  - RED: missing Flow 4 outcome summary fields and `Current=REVIEW` was downgraded to `NEEDS_INPUT`.
- Same targeted command after implementation
  - PASS: 3 tests.
- `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow4_uses_criteria_detail_board tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_workspace_model_builds_issue_queue_items tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_workspace_model_builds_criteria_detail_groups tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_module_plan_preserves_review_input_checks tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_workspace_distinguishes_blocked_from_repairable_gap`
  - PASS: 5 tests.
- `.venv/bin/python -m py_compile app/services/backtest_practical_validation_modules.py app/services/backtest_practical_validation_workspace.py app/web/backtest_practical_validation/page.py`
  - PASS.
- `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests`
  - PASS: 67 tests. Third-party `edgar` deprecation warnings and Streamlit bare-mode warnings only.
- `git diff --check`
  - PASS.
- Browser QA fallback
  - In-app browser `iab` was unavailable, so Playwright fallback was used against `http://localhost:8539/backtest`.
  - Verified initial Flow 4 outcome summary and replay-result behavior. After runtime replay returned `REVIEW` / coverage `REVIEW`, `후보 source / 최신 재검증` moved from `아직 실행 안 됨` to `Final Review에서 확인`, with no `NEEDS_INPUT` downgrade.
  - Screenshot saved to `/tmp/pv-flow4-outcome-taxonomy-v1-qa.png`.
