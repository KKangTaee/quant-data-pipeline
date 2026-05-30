# Runs

Commands and verification notes will be recorded during implementation.

## 2026-05-30

- `.venv/bin/python -m py_compile app/services/backtest_practical_validation_board_registry.py app/services/backtest_practical_validation_modules.py app/services/backtest_practical_validation_diagnostics.py app/web/backtest_practical_validation.py tests/test_service_contracts.py` PASS
- `.venv/bin/python -m unittest tests.test_service_contracts.PracticalValidationServiceContractTests.test_validation_board_map_marks_single_gtaa_conditional_boards tests.test_service_contracts.PracticalValidationServiceContractTests.test_validation_module_gate_blocks_missing_required_runtime_replay tests.test_service_contracts.PracticalValidationServiceContractTests.test_validation_module_gate_allows_ready_with_review_modules` PASS
- `git diff --check` PASS
- `.venv/bin/python -m unittest tests.test_service_contracts` PASS, 193 tests
- `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py` PASS
- `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py` PASS, generated artifacts remain unstaged
- Browser QA on `http://127.0.0.1:8502/backtest` PASS: Practical Validation shows `Applied Validation Map`, board badges, `Risk Contribution Audit - Not applicable`, `Component Role / Weight Audit - Not applicable`, and browser console error log is empty.
- `.venv/bin/python -m py_compile app/services/backtest_practical_validation_modules.py app/web/backtest_practical_validation.py tests/test_service_contracts.py` PASS after blocker guidance update.
- `.venv/bin/python -m unittest tests.test_service_contracts.PracticalValidationServiceContractTests.test_validation_module_gate_blocks_missing_required_runtime_replay tests.test_service_contracts.PracticalValidationServiceContractTests.test_validation_board_map_marks_single_gtaa_conditional_boards tests.test_service_contracts.PracticalValidationServiceContractTests.test_validation_module_gate_allows_ready_with_review_modules` PASS after blocker guidance update.
- Browser QA on `http://127.0.0.1:8502/backtest` PASS after blocker guidance update: blocker table shows `Fix Location` / `Fix Action`, and `Latest Runtime Replay` points to `3. 최신 데이터 기준 전략 재검증`; browser console error log is empty.
- `.venv/bin/python -m unittest tests.test_service_contracts` PASS, 193 tests, after blocker guidance update.
- `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py` PASS after blocker guidance update.
