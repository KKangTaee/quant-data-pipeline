# Runs

## 2026-05-29

- `.venv/bin/python -m py_compile app/services/backtest_realism_audit.py app/services/backtest_practical_validation_source.py app/runtime/backtest.py app/runtime/history.py app/web/backtest_candidate_review_helpers.py`
  - Result: pass
- `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRealismAuditContractTests tests.test_service_contracts.PracticalValidationServiceContractTests`
  - Result: pass, 11 tests
- `.venv/bin/python -m unittest tests.test_service_contracts`
  - Result: pass, 81 tests
- `git diff --check`
  - Result: pass
- `.venv/bin/python -m unittest tests.test_service_contracts.PracticalValidationServiceContractTests.test_selection_source_preserves_cost_model_snapshot_without_new_registry tests.test_service_contracts.BacktestRealismAuditContractTests`
  - Result: pass, 4 tests
