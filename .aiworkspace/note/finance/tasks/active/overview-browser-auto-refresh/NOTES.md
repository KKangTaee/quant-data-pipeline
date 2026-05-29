# Notes

- `browser_safe` should be intentionally narrower than `safe`; it is for an open Overview browser session, not unattended daily calendar refresh.
- S&P 500 daily snapshot recently measured around 5 seconds, so it is acceptable for the first Streamlit-session implementation.
- Top1000 / Top2000 / Events should remain opt-in later to avoid provider pressure and long UI pauses.
- The Overview panel stores skipped / locked / failed heartbeat summaries in `st.session_state`; only due collector jobs append persistent run history.
