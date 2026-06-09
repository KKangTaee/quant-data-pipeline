# Notes

## 2026-06-10

- `run_overview_market_context_refresh_all` already returns bundle-level `status`, `jobs_run`, `jobs_failed`, and per-job `results`.
- The UI currently shows one alert plus raw rows, but does not separate issue rows or translate job statuses for quick review.
- The desired 3차 UX is a clearer read model over existing result payloads, not a new collection path.
- Added `_overview_market_context_refresh_result_model()` so partial / failed / skipped rows are separated from full results before Streamlit rendering.
- Browser QA produced a partial-success sample: 7 jobs run, 2 issue rows, 0 failed jobs, 37,905 saved rows. The UI now shows the issue rows first and keeps full rows collapsed.
