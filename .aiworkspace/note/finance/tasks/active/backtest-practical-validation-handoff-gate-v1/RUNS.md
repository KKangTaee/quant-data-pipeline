# Backtest Practical Validation Handoff Gate V1 Runs

## 2026-05-30

- `.venv/bin/python -m py_compile app/web/backtest_result_display.py tests/test_service_contracts.py`
  - Result: passed.
- `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_candidate_readiness_scores_source_checks_not_legacy_deployment_status tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_handoff_gate_blocks_hold_candidates tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_handoff_gate_allows_ready_candidates`
  - Result: passed.
  - Notes: edgar package emitted upstream deprecation warnings; tests passed.
- `git diff --check`
  - Result: passed.
- Browser smoke on `http://127.0.0.1:8502/backtest`
  - Restarted the main-dev Streamlit server on port 8502.
  - Ran the default Equal Weight backtest and checked the handoff surface.
  - Result: status card rendered, button label changed to `실전성 검증으로 보내기`, button was disabled for a hold/caution candidate, and blocker reasons were visible.
