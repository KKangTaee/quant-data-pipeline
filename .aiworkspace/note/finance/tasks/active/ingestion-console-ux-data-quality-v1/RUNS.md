# Ingestion Console UX / Data Quality V1 Runs

## 2026-06-01

- `py_compile` on current Ingestion-related files passed before edits.
- `git status --short` showed pre-existing untracked/modified local artifact: `finance/.DS_Store`.
- `.venv/bin/python -m py_compile app/web/streamlit_app.py app/jobs/ingestion_jobs.py` passed after implementation.
- `.venv/bin/python -m pytest tests/test_service_contracts.py` could not run because the local `.venv` has no `pytest` module.
- `.venv/bin/python -m unittest tests.test_service_contracts` passed: 207 tests, OK.
- `git diff --check` passed.
- Browser QA passed on `http://localhost:8505/ingestion`: page title copy, Korean tabs, daily market run button, lifecycle section, Nasdaq current listing button, and current-snapshot caveat were visible. Browser console showed Streamlit `_stcore/host-config` and `_stcore/health` 404s under the `/ingestion` subpath, but the page rendered and interacted normally.
- QA screenshot: `.playwright-mcp/ingestion-console-qa.png` generated locally and intentionally left untracked.
- Responsive polish verification passed: `py_compile`, `git diff --check`, and `.venv/bin/python -m unittest tests.test_service_contracts` passed with 207 tests.
- Browser responsive QA passed on the in-app browser: Runtime / Build metadata no longer truncates, source selector shows Korean compact label plus full current selection, persistent run-history selector shows a compact label plus full caption, and result summary stats render as wrapping cards instead of truncated Streamlit metrics.
- Responsive QA screenshot: `.playwright-mcp/ingestion-responsive-qa.png` generated locally and intentionally left untracked.
- Selectbox clickability follow-up passed: removed dropdown internals CSS, `.venv/bin/python -m py_compile app/web/streamlit_app.py`, `git diff --check`, `curl -I http://localhost:8505/ingestion`, and `.venv/bin/python -m unittest tests.test_service_contracts` all passed. Browser direct control remains policy-blocked, so visual confirmation should be done by refreshing the already-open in-app browser.
- Follow-up UX/data-quality pass:
  - `.venv/bin/python -m py_compile app/web/streamlit_app.py app/jobs/preflight_checks.py app/jobs/symbol_sources.py app/jobs/run_history.py` passed.
  - `git diff --check` passed.
  - `.venv/bin/python -m unittest tests.test_service_contracts` passed: 207 tests, OK.
  - `curl -s -o /dev/null -w '%{http_code}\n' http://localhost:8505/ingestion` returned `200`.
  - Browser DOM QA on `http://localhost:8505/ingestion` confirmed the workflow overview, execution contract, daily price card, DB coverage quick check text, and lifecycle warning callout after opening the Practical Validation evidence section.
  - Browser screenshot capture timed out on `Page.captureScreenshot`; DOM QA passed but no screenshot artifact was produced for this follow-up.
