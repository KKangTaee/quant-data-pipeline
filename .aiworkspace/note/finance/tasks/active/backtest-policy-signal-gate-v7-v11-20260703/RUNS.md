# Runs

실행한 QA 명령과 결과를 단계별로 기록한다.

## V7

- ` .venv/bin/python -m py_compile app/services/backtest_handoff_readiness.py tests/test_service_contracts.py` 통과.
- `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_policy_signal_inventory_classifies_gate_review_and_context_rows tests.test_service_contracts.BacktestRuntimeContractTests.test_candidate_readiness_scores_source_checks_not_legacy_deployment_status tests.test_service_contracts.BacktestRuntimeContractTests.test_handoff_gate_summary_groups_blockers_for_user_display` 통과.
- `git diff --check` 통과.
