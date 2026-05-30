# Runs

Commands and verification results will be recorded here.

## 2026-05-28

- `uv run python -m py_compile finance/data/market_intelligence.py app/jobs/ingestion_jobs.py app/jobs/run_history.py app/services/overview_market_intelligence.py app/web/streamlit_app.py tests/test_service_contracts.py` -> PASS
- `uv run python -m unittest tests.test_service_contracts` -> PASS, 52 tests
- `uv run python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py` -> PASS
- `git diff --check` -> PASS
- Browser smoke on `http://localhost:8501/ingestion` -> PASS; Macro tab shows `.ics` uploader and import button
