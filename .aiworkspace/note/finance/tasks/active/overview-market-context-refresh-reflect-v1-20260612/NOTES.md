# Overview Market Context Refresh Reflect V1 Notes

## Discoveries

- `load_overview_macro_context_cockpit` is cached with `st.cache_data`.
- `load_overview_group_leadership_snapshot` and `load_overview_market_sentiment_snapshot` are cached helper reads used by the cockpit.
- `load_overview_futures_macro_snapshot` uses a service-level cache cleared by `clear_overview_futures_macro_snapshot_cache`.
- `load_overview_market_movers_snapshot`, `load_overview_market_events_snapshot`, and `load_overview_collection_ops_snapshot` are direct read paths in `overview_dashboard_helpers.py`; clearing the composite cockpit cache plus rerun is enough for them to be invoked again.
- The current refresh button runs below the cockpit, so cache clearing alone cannot update the already-rendered top brief in that same Streamlit pass.

## Decisions

- Use `st.rerun()` after storing the result so the next run renders the top cockpit from freshly cleared caches.
- Keep job result rows in the existing collapsed expander.
- Show reflection state as compact top-of-tab guidance, not as a diagnostic table.
- Clear the same cached read layers after every manual refresh attempt. Success / partial success copy says the top brief was re-read; failure copy says existing data remains, so a cache rerun is not misrepresented as fresh data.
- Do not add market movers / events / collection ops `.clear()` calls because these helpers are not `st.cache_data` wrapped in the current read path. They are re-invoked when the composite cockpit cache is cleared and the app reruns.
