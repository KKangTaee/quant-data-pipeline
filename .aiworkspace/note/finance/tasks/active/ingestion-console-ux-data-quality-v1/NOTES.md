# Ingestion Console UX / Data Quality V1 Notes

## Decisions

- Preserve existing user-controlled collection shape: symbols, date windows, source mode, provider mode, and collection options remain editable.
- Prefer Korean display names for users and keep internal English job ids as secondary metadata.
- Do not treat lifecycle current snapshots as historical survivorship proof.
- Do not add new DB tables or provider connectors in this slice.
- Keep run history and result artifacts compatible by changing presentation / dispatch only, not the `JobResult` schema.
- Surface lifecycle collectors that already existed in `app/jobs/ingestion_jobs.py` instead of creating duplicate collection paths.

## Initial Review Summary

- The current code already has run history, artifacts, symbol source selection, large-run guard, and diagnostics.
- Main weakness is product comprehension: users cannot quickly tell what each job collects, where it stores data, or how reliable the data is for validation.
- Lifecycle evidence capability exists below the UI surface and should be exposed with strong caveats.

## Implementation Summary

- Added a `JOB_GUIDE` registry in `app/web/streamlit_app.py` to centralize Korean titles, purpose text, DB targets, downstream use, caveats, and next actions for Ingestion jobs.
- Added result guidance helpers so a partial / failed collection explains the next operator check instead of only showing raw metrics.
- Added UI controls for `collect_symbol_directory_snapshots`, `collect_sec_company_ticker_crosscheck`, and `collect_computed_snapshot_lifecycle`.
- Kept direct provider fetch out of Practical Validation; the flow remains `Ingestion -> DB -> Loader -> UI`.
- Responsive follow-up replaced truncating Streamlit metrics in Ingestion result summaries with custom wrapping stat cards, added wrapping metadata rows for DB targets / downstream use, and added compact Korean `format_func` labels for symbol-source / preset selectors.
- Persistent run-history selection now uses compact display labels and a full `현재 선택` caption, so the selected run remains identifiable when the browser is narrow.
