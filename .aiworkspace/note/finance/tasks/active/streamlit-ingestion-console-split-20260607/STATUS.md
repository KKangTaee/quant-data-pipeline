# Streamlit Ingestion Console Split Status

Status: Completed
Date: 2026-06-07

## Current State

- RED contract tests were added under `tests/test_service_contracts.py`.
- `app/web/ingestion_console.py` now owns the former Ingestion console render/state/job helper code.
- `app/web/streamlit_app.py` is reduced to a shell-sized file and delegates Ingestion rendering to the new module.
- Durable docs now point `Workspace > Ingestion console` to `app/web/ingestion_console.py`.
- Streamlit 8501 was restarted and Browser QA confirmed the Ingestion route.

## Verification

- `py_compile`: passed.
- focused RED/GREEN tests: passed.
- `BoundaryContractHardeningTests`: passed.
- full `tests.test_service_contracts`: passed, 277 tests.
- `check_ui_engine_boundary.py`: PASS.
- `git diff --check`: passed.
- `curl http://localhost:8501/_stcore/health`: `ok`.
- Browser QA: `http://localhost:8501/ingestion` shows Ingestion title, Runtime / Build, and daily price update panel without Traceback / import errors.

## Remaining Follow-Up

- 7B can extract Ingestion read-only diagnostics / live source inspection into Streamlit-free service/job facades.
- A later split can target `app/web/backtest_compare.py`.
