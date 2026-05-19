# Service Contract Tests Runs

## 2026-05-20

- `.venv/bin/python -m pytest --version`
  - Result: failed as expected, `pytest` is not installed in `.venv`.
- `.venv/bin/python -m unittest tests/test_service_contracts.py`
  - Result: pass, 9 tests.
  - Note: importing current service dependencies emits third-party `edgar` deprecation warnings; they do not fail the contract checks.
- `.venv/bin/python -m py_compile tests/test_service_contracts.py app/services/backtest_practical_validation.py app/services/backtest_evidence_read_model.py`
  - Result: pass.
- `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py`
  - Result: pass.
  - Note: existing `app.services -> app.web` transitional imports remain advisory.
- `git diff --check`
  - Result: pass.
