# Practical Validation Diagnostics Service Boundary Runs

## 2026-05-20

- Inspected Practical Validation helper ownership and imports before moving diagnostic logic.
- Moved `app/web/backtest_practical_validation_helpers.py` to `app/services/backtest_practical_validation_diagnostics.py`.
- Updated service/UI imports and added focused diagnostics contract coverage.
- `.venv/bin/python -m py_compile app/services/backtest_practical_validation.py app/services/backtest_practical_validation_diagnostics.py app/services/backtest_practical_validation_replay.py app/web/backtest_practical_validation.py app/web/backtest_compare.py app/web/backtest_candidate_review_helpers.py tests/test_service_contracts.py` passed.
- `.venv/bin/python -m unittest tests/test_service_contracts.py` passed 15 tests. The first run exposed a test assumption about `profile_label`; the test was corrected to match the existing contract.
- `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py` passed with transitional `app.services -> app.web` advisories.
- `git diff --check` and `git diff --cached --check` passed.
