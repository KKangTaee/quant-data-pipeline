# Notes

Status: Complete
Last Updated: 2026-06-07

## Findings

- Overview was not directly fetching providers, but it imported concrete ingestion job wrappers and automation helpers.
- The user-facing behavior should stay unchanged: refresh buttons remain in Overview, and Ingestion remains the broader collector console.
- A small `app/jobs/overview_actions.py` facade is the lowest-risk boundary improvement because it keeps collection calls in the jobs layer and leaves `app/web` as render/session state.
- Ingestion diagnostics are still a follow-up. This task does not split `_render_ingestion_console`.

## Implementation Notes

- The action facade wraps:
  - browser-session auto refresh
  - market intraday snapshot
  - futures live / daily OHLCV refresh
  - FOMC / earnings / macro calendar refresh
  - S&P 500 universe refresh
  - CNN / AAII sentiment refresh
  - quote-gap diagnostics
  - Overview run-history recording
- `app/web/overview_dashboard.py` no longer imports `app.jobs.ingestion_jobs`, `app.jobs.overview_automation`, or `app.jobs.run_history`.
