# Practical Validation Replay Service Boundary Runs

## 2026-05-20

- `git mv app/web/backtest_practical_validation_replay.py app/services/backtest_practical_validation_replay.py`
  - Result: moved replay helper to service layer.
- `.venv/bin/python -m py_compile app/services/backtest_practical_validation_replay.py app/web/backtest_practical_validation.py`
  - Result: pass.
- `.venv/bin/python - <<'PY' ... import app.services.backtest_practical_validation_replay ...`
  - Result: `streamlit_loaded False`.
- `.venv/bin/python -m unittest tests/test_service_contracts.py`
  - Result: pass, 14 tests.
- `.venv/bin/python -m py_compile app/services/backtest_practical_validation_replay.py app/web/backtest_practical_validation.py tests/test_service_contracts.py`
  - Result: pass.
- `.venv/bin/python -m py_compile app/services/backtest_practical_validation_replay.py app/web/backtest_practical_validation.py tests/test_service_contracts.py app/services/backtest_practical_validation.py`
  - Result: pass.
- `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py`
  - Result: pass.
  - Note: moved replay service introduces expected transitional `app.services -> app.web` advisories for curve / runtime helpers.
- `git diff --check && git diff --cached --check`
  - Result: pass.
