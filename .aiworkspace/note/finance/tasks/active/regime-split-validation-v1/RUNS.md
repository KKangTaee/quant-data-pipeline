# Regime Split Validation V1 Runs

Status: Complete
Created: 2026-05-29
Completed: 2026-05-29

## Runs

### 2026-05-29

- `.venv/bin/python -m py_compile app/services/backtest_temporal_validation.py app/services/backtest_practical_validation_diagnostics.py app/services/backtest_validation_efficacy.py app/services/backtest_evidence_read_model.py finance/loaders/macro.py`
  - Result: PASS
- `.venv/bin/python -m unittest tests.test_service_contracts`
  - Result: PASS, 96 tests
  - Note: edgar dependency emitted deprecation warnings unrelated to this task.
- `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py`
  - Result: PASS
- `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py`
  - Result: PASS
  - Note: `finance/.DS_Store` remains a generated artifact and should stay uncommitted.
- `git diff --check`
  - Result: PASS
