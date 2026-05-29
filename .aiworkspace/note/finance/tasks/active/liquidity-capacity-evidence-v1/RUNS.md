# Runs

## 2026-05-29

- `.venv/bin/python -m py_compile app/services/backtest_realism_audit.py app/services/backtest_practical_validation_provider_context.py tests/test_service_contracts.py`
  - Result: PASS
- `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRealismAuditContractTests tests.test_service_contracts.ProviderContextProvenanceContractTests`
  - Result: PASS, 9 tests
- `git diff --check`
  - Result: PASS
- `.venv/bin/python -m unittest tests.test_service_contracts`
  - Result: PASS, 86 tests
