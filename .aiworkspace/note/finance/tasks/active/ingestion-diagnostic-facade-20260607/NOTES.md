# Notes

Status: Completed
Last Verified: 2026-06-07

## Findings

- 7A moved Ingestion render/state/job UI into `app/web/ingestion_console.py`, but the module still directly imported read-only diagnostic sources.
- Price Stale and Statement Coverage already had reusable job-level helpers under `app/jobs/diagnostics.py`.
- Statement PIT Inspection had orchestration directly in the UI: coverage summary loader, timing audit loader, and one optional live EDGAR source inspection.
- A service facade is a better owner than another web helper because the code is Streamlit-free and can be checked by the existing UI / Engine boundary script.

## Decisions

- Keep result payloads unchanged to avoid UI/render churn.
- Keep diagnostic writes out of scope. This task does not change ingestion collectors, DB schema, or run-history behavior.
- Remove `Ingestion diagnostic facade` from Roadmap next decisions after completion.
