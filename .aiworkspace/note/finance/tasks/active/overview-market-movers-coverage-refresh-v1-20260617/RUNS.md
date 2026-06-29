# Runs

## 2026-06-17

- `git status --short`
  - Existing unrelated dirty paths before edits: `M finance/.DS_Store`, `?? .superpowers/`.
- `uv run python -m pytest tests/test_service_contracts.py::... -q`
  - Failed before running tests because `.venv` has no `pytest` module.
- `uv run python -m unittest` focused RED set
  - Expected failures confirmed missing Nasdaq coverage normalization, diagnostics evidence columns, action facade loader, and automation jobs.
- `uv run python -m unittest` focused GREEN set
  - Passed 5 focused tests. Existing edgar deprecation warnings appeared during import.
- `uv run python -m py_compile finance/data/market_intelligence.py app/services/overview_market_intelligence.py app/jobs/overview_actions.py app/jobs/overview_automation.py app/jobs/ingestion_jobs.py app/web/overview_dashboard.py`
  - Passed.
- `uv run python -m app.jobs.overview_automation --profile standard --dry-run`
  - Passed. Plan shows `nasdaq_symbol_directory` due and `nasdaq_intraday` skipped outside US market hours.
- `uv run python -m app.jobs.overview_automation --profile intraday --job nasdaq_intraday --dry-run`
  - Passed. Job filter recognized; skipped outside US market hours.
- `uv run python -m pytest tests/test_service_contracts.py -q`
  - Failed before running tests because `.venv` has no `pytest` module.
- `uv run python -m py_compile finance/data/market_intelligence.py app/services/overview_market_intelligence.py app/jobs/overview_actions.py app/jobs/overview_automation.py app/jobs/ingestion_jobs.py app/web/overview_dashboard.py`
  - Passed.
- `uv run python -m unittest tests.test_service_contracts -q`
  - Passed. Ran 353 tests. Existing edgar deprecation warnings and Streamlit cache warnings appeared during import.
- `uv run python -m app.jobs.overview_automation --profile standard --dry-run`
  - Passed. Plan shows `nasdaq_symbol_directory` due and `nasdaq_intraday` skipped outside US market hours.
- `uv run python -m app.jobs.overview_automation --profile intraday --job nasdaq_intraday --dry-run`
  - Passed. Job filter recognized; skipped outside US market hours.
- `uv run streamlit run app/web/streamlit_app.py --server.port 8525 --server.headless true`
  - Started local server for Browser QA at `http://localhost:8525`.
- Browser QA
  - Confirmed Market Movers coverage dropdown includes `Nasdaq-listed current snapshot`.
  - Confirmed S&P 500, Top1000, and Top2000 render existing ranking / diagnostics flow.
  - Confirmed Nasdaq empty state shows Symbol Directory refresh guidance instead of stale previous coverage rows.
  - Confirmed Coverage Diagnostics exposes cause / evidence / next-check columns.
  - Screenshot: `.aiworkspace/note/finance/run_artifacts/overview-market-movers-coverage-refresh-v1-qa.png`.
- `curl -I --max-time 5 http://localhost:8525`
  - Passed with HTTP 200 while Browser QA server was running.
