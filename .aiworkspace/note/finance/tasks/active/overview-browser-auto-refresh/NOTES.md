# Notes

- `browser_safe` should be intentionally narrower than `safe`; it is for an open Overview browser session, not unattended daily calendar refresh.
- S&P 500 daily snapshot recently measured around 5 seconds, so it is acceptable for the first Streamlit-session implementation.
- Top1000 / Top2000 / Events should remain opt-in later to avoid provider pressure and long UI pauses.
- The Overview panel stores skipped / locked / failed heartbeat summaries in `st.session_state`; only due collector jobs append persistent run history.
- Data Health treats `scheduled` and `browser_auto` as auto modes, while `Auto Source` distinguishes Scheduled from Browser Auto.
- Loading UX stays local to the top auto-refresh panel; full-screen blocking was intentionally avoided so users can keep reading tables during the 5-second S&P 500 snapshot refresh.
