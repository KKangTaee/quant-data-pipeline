# Data Provenance Coverage V1 Runs

Status: Complete
Created: 2026-05-28

## Commands

| Command | Result |
|---|---|
| `git status --short` | Only pre-existing `finance/.DS_Store` modification was present before this task. |
| `rg -n "build_provider_context|provider_coverage_display_rows|provider_coverage" app/services app/web tests/test_service_contracts.py` | Located provider context, Practical Validation display, Final Review display, and tests. |
| `sed -n ... finance/loaders/provider.py finance/loaders/macro.py app/services/backtest_practical_validation_provider_context.py` | Confirmed loader fields already carry source / freshness metadata. |

## Verification

| Command | Result |
|---|---|
| `.venv/bin/python -m py_compile app/services/backtest_practical_validation_provider_context.py app/services/backtest_practical_validation_diagnostics.py tests/test_service_contracts.py` | Passed. |
| `.venv/bin/python -m unittest tests/test_service_contracts.py` | Passed, 29 tests. Third-party `edgar` deprecation warnings only. |
| `.venv/bin/python -m py_compile app/services/backtest_practical_validation_provider_context.py app/services/backtest_practical_validation_diagnostics.py app/web/backtest_practical_validation.py app/web/backtest_final_review.py tests/test_service_contracts.py` | Passed after final doc sync, provenance coverage weight adjustment, and compact validation metrics update. |
| `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py` | Passed. No hard violations or advisories. |
| `git diff --check` | Passed. |
| `.venv/bin/streamlit run app/web/streamlit_app.py --server.address 127.0.0.1 --server.port 8502` | Failed because the copied script shebang points to a stale `phase/.venv` path. |
| `.venv/bin/python -m streamlit run app/web/streamlit_app.py --server.address 127.0.0.1 --server.port 8502` + Browser smoke | Passed. Opened Overview, Backtest, and Practical Validation at `http://127.0.0.1:8502`; browser console showed 0 errors. Practical Validation had no selected source, so provider table rendering was covered by the service contract test rather than live data. |
