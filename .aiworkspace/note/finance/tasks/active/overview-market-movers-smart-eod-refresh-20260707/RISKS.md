# Risks

- Delta fetch groups stale symbols by the earliest stale start date, so some stale symbols can receive a few extra rows. This is still much smaller than refreshing the entire universe.
- Browser QA reached the Market Movers action area, but automated Period switching was limited by Streamlit/native select handling in the in-app browser.
- 3차 still uses compact row-count coverage, not a full per-anchor gap map. If future ranking logic needs exact anchor-date repair, add a dedicated window coverage query.
