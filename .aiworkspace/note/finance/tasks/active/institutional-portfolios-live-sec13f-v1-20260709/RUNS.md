# Institutional Portfolios Live SEC 13F V1 Runs

Commands and verification evidence will be appended during implementation.

## 2026-07-09

- `git status --short` before implementation: clean.
- RED: `.venv/bin/python -m unittest tests.test_institutional_portfolios`
  - Expected failures: missing `build_sec_13f_refresh_status`, refresh/watchlist schema, refresh payload, refresh panel, and registry target table.
- GREEN: `.venv/bin/python -m unittest tests.test_institutional_portfolios`
  - Result: 11 tests OK after refresh status / watchlist / payload implementation.
- RED: `.venv/bin/python -m unittest tests.test_institutional_portfolios.Sec13FDataSetParserTests.test_cusip_symbol_map_rows_use_unique_asset_profile_name_matches`
  - Expected failure: missing `build_cusip_symbol_map_rows`.
- GREEN: `.venv/bin/python -m unittest tests.test_institutional_portfolios.Sec13FDataSetParserTests.test_cusip_symbol_map_rows_use_unique_asset_profile_name_matches`
  - Result: 1 test OK.
- Focused test: `.venv/bin/python -m unittest tests.test_institutional_portfolios`
  - Result: 12 tests OK. Warnings were Streamlit bare-mode / edgar package deprecation warnings.
- Python compile: `.venv/bin/python -m py_compile finance/data/institutional_13f.py finance/loaders/institutional_13f.py app/services/institutional_portfolios.py app/web/institutional_portfolios.py app/jobs/ingestion_jobs.py app/web/ingestion/registry.py app/web/ingestion/sections.py`
  - Result: exit 0.
- React build: `npm run build` in `app/web/streamlit_components/institutional_portfolios_workbench`
  - Result: Vite build exit 0; generated `component_static` asset hashes updated.
- Whitespace check: `git diff --check`
  - Result: exit 0.
- UI / engine boundary check: `rg -n "download_sec|urlopen|urllib|requests|collect_and_store_sec_13f_dataset|read_sec_13f_dataset_zip|run_collect_sec_13f_dataset" app/web/institutional_portfolios.py app/services/institutional_portfolios.py finance/loaders/institutional_13f.py`
  - Result: only `app/web/institutional_portfolios.py` imports / calls `run_collect_sec_13f_dataset` inside the explicit secondary refresh button path.
- Browser QA: Streamlit served with `.venv/bin/python -m streamlit run app/web/streamlit_app.py --server.port 8530 --server.headless true`.
  - Desktop route loaded `Institutional Portfolios`, React workbench rendered preview mode, refresh panel marker present.
  - Mobile viewport 390x844 marker check found `Institutional Portfolios`, `Portfolio Allocation`, `SEC 13F data refresh`, and `Institutional Interest`.
  - Screenshot artifact: `.aiworkspace/note/finance/run_artifacts/institutional-portfolios-live-sec13f-v1-qa.png` (not committed).
  - Note: direct `/institutional-portfolios` route emitted one Streamlit route fallback console log, but workbench DOM and component markers rendered.
