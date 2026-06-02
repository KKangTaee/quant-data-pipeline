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
- Do not style `div[data-baseweb="select"]` or `div[role="listbox"]` internals globally. It can interfere with Streamlit/BaseWeb option positioning and click targets; keep selectbox reliability native and show long values in adjacent captions/cards instead.
- Follow-up implementation kept button names, common finance terms, option values, and internal IDs where useful, but translated explanatory content that tells the user what the job does and how to interpret results.
- Added a top workflow overview and per-run execution contracts so users see source / count / period / destination before clicking run.
- Added bounded price-window DB coverage quick check using `finance.loaders.price.load_price_window_summary`; it is intentionally skipped for large runs to avoid making the UI rerun expensive.
- Result cards now classify job domains and change labels / interpretation: price rows are not lifecycle evidence rows, provider snapshots are not PIT truth, and current lifecycle snapshots are not survivorship PASS evidence.
- User-facing preflight and source-resolution messages moved to Korean explanatory text in `app/jobs/preflight_checks.py`, `app/jobs/symbol_sources.py`, and `app/jobs/run_history.py`.
