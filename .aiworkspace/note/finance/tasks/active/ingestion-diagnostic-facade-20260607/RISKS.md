# Risks

Status: Completed
Last Verified: 2026-06-07

## Residual Risks

- The PIT source inspection still performs one live EDGAR sample fetch when the user explicitly presses the button. This is read-only and does not write DB rows, but it can still be affected by provider availability.
- The Ingestion job execution dispatch remains in `app/web/ingestion_console.py`. This task only addressed read-only diagnostics, not all job dispatch code.

## Verified QA

- Browser QA confirmed the Ingestion page renders and the manual diagnostics tab exposes Price Stale, Statement Coverage, and PIT Inspection sections after the facade split.

## Do Not Infer

- This task does not change collector persistence, DB schema, UPSERT behavior, or provider retry policy.
- This task does not make diagnostic `NOT_RUN`, provider gap, or partial coverage states pass conditions.
