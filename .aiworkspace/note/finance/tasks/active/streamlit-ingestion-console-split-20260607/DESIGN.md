# Streamlit Ingestion Console Split Design

Status: Completed
Date: 2026-06-07

## Boundary

| File | Responsibility After 7A |
|---|---|
| `app/web/streamlit_app.py` | Finance Console shell. direct-run import path guard, runtime marker, top navigation, page wrappers, glossary |
| `app/web/ingestion_console.py` | `Workspace > Ingestion` render/session-state boundary. job guide, symbol presets, pending/running job state, explicit job scheduling, result/history/log/failure artifact display, diagnostics panels |
| `app/jobs/ingestion_jobs.py` | Existing explicit ingestion job wrappers. No behavior change in 7A |
| `finance/data/*`, `finance/loaders/*` | Existing collector / DB / loader boundaries. No behavior change in 7A |

## Runtime Context

`streamlit_app.py` still owns `APP_RUNTIME_MARKER`, `APP_RUNTIME_LOADED_AT`, and `CURRENT_GIT_SHORT_SHA`.
`render_ingestion_page(runtime_marker, loaded_at, git_sha)` stores those values in the Ingestion module for run metadata and Runtime / Build display.

## State Contract

`main()` calls these Ingestion-owned public functions before page routing:

- `init_ingestion_state()`
- `promote_pending_job()`
- `apply_pending_ingestion_prefill()`

This preserves the previous session state names while moving ownership out of the shell.

## Not Changed

- No DB schema changes.
- No provider / FRED / external source behavior changes.
- No run history / registry / saved JSONL rewrites.
- No Ingestion diagnostic service extraction yet. That remains a follow-up.
