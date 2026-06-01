# Risks

- Portfolio-wide recheck remains sequential and can still be slow for many strategies or long replay periods.
- Streamlit does not support true lazy tabs, so the lower detail surface must avoid `st.tabs` for per-strategy rendering if only one strategy should compute.
- Existing session results from before this implementation do not have the new signature and will be treated as stale / not current.
- Future speed work should consider replay-result caching, per-strategy incremental queues, or background job progress if full refresh becomes a regular workflow.
