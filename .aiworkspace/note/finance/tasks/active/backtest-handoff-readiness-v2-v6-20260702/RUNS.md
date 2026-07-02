# Backtest Handoff Readiness V2-V6 Runs

## 2026-07-02 V2

- `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_candidate_readiness_scores_source_checks_not_legacy_deployment_status tests.test_service_contracts.BacktestRuntimeContractTests.test_handoff_readiness_policy_lives_in_streamlit_free_service`
  - RED result: failed because `app.services.backtest_handoff_readiness` did not exist.
- `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_candidate_readiness_scores_source_checks_not_legacy_deployment_status tests.test_service_contracts.BacktestRuntimeContractTests.test_handoff_readiness_policy_lives_in_streamlit_free_service tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_handoff_gate_blocks_hold_candidates tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_handoff_gate_allows_ready_candidates`
  - GREEN result: passed after service extraction. Existing edgar deprecation warnings observed, unrelated.
- `.venv/bin/python -m py_compile app/services/backtest_handoff_readiness.py app/web/backtest_result_display.py app/web/backtest_compare/page.py`
  - Result: passed.
- `git diff --check`
  - Result: passed.
- `.venv/bin/python -m unittest tests.test_service_contracts`
  - Result: passed, 451 tests. Existing edgar deprecation warnings and Streamlit no-runtime cache warnings observed, unrelated.
- `.venv/bin/python -m unittest tests.test_backtest_refactor_boundaries`
  - Result: passed, 11 tests. Existing edgar deprecation warnings observed, unrelated.
- `git diff --check`
  - Result: passed after V2 docs update.
