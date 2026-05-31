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
