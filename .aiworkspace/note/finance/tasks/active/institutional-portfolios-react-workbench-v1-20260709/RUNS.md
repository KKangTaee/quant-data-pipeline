# Institutional Portfolios React Workbench V1 Runs

Commands and QA evidence will be appended during implementation.

## 2026-07-09 RED tests

- `.venv/bin/python -m pytest tests/test_institutional_portfolios.py -q`
  - Result: failed because `pytest` is not installed in the local venv.
- `.venv/bin/python tests/test_institutional_portfolios.py`
  - Result: expected RED.
  - Failures: missing `build_institutional_workbench_payload`, missing `build_institutional_preview_workbench_payload`, and `app/web/institutional_portfolios.py` does not mount the React workbench.

## 2026-07-09 implementation QA

- `.venv/bin/python tests/test_institutional_portfolios.py`
  - Result: pass, 8 tests.
- `(cd app/web/streamlit_components/institutional_portfolios_workbench && npm install)`
  - Result: pass, 107 packages installed / audited, 0 vulnerabilities.
- `(cd app/web/streamlit_components/institutional_portfolios_workbench && npm run build)`
  - Result: pass, generated `component_static/index.html`, CSS, and JS asset.
- `.venv/bin/python -m py_compile app/services/institutional_portfolios.py app/web/institutional_portfolios.py app/web/institutional_portfolios_react_component.py finance/loaders/institutional_13f.py finance/data/institutional_13f.py`
  - Result: pass.
- `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py`
  - Result: PASS, hard violations none, advisories none.

## 2026-07-09 Browser QA

- Restarted `http://127.0.0.1:8510/` with `.venv/bin/python -m streamlit run app/web/streamlit_app.py --server.port 8510 --server.address 127.0.0.1` because the old Streamlit process was serving pre-change UI.
- Verified app root -> Workspace menu -> `Institutional Portfolios` route.
- Verified React workbench iframe renders preview state with manager rail, allocation workbench, reported change board, sector exposure, source caveats, and no raw DB error in the hero.
- Verified component `Holdings` tab switches inside the iframe and displays holding rows.
- Screenshot artifact kept uncommitted: `/tmp/quant-finance-qa/institutional-portfolios-react-workbench-preview-clean.png`.
