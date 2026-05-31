# Robustness Lab V1 Runs

Status: Active
Created: 2026-05-28

## Commands

- `.venv/bin/python -m py_compile app/services/backtest_practical_validation_stress_sensitivity.py app/services/backtest_practical_validation_diagnostics.py app/services/backtest_evidence_read_model.py app/web/backtest_practical_validation.py app/web/backtest_final_review.py` - PASS
- `.venv/bin/python -m unittest tests/test_service_contracts.py` - PASS, 30 tests
- `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py` - PASS
- `git diff --check` - PASS
- `.venv/bin/python -m streamlit run app/web/streamlit_app.py --server.port 8502 --server.headless true` + Browser smoke - Practical Validation and Final Review tabs rendered. The direct `/backtest` tab carried stale `_stcore` 404 console errors from opening the page before the server was ready; the root-loaded app rendered without app exception.
