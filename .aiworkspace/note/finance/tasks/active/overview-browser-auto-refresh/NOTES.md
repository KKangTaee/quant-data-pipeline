# Notes

- `browser_safe` should be intentionally narrower than `safe`; it is for an open Overview browser session, not unattended daily calendar refresh.
- S&P 500 daily snapshot recently measured around 5 seconds, so it is acceptable for the first Streamlit-session implementation.
- Top1000 / Top2000 / Events should remain opt-in later to avoid provider pressure and long UI pauses.
- The Overview panel stores skipped / locked / failed heartbeat summaries in `st.session_state`; only due collector jobs append persistent run history.
- Data Health treats `scheduled` and `browser_auto` as auto modes, while `Auto Source` distinguishes Scheduled from Browser Auto.
- Loading UX stays local to the Market Movers `데이터 갱신` area; full-screen blocking was intentionally avoided so users can keep reading tables during the 5-second S&P 500 snapshot refresh.
- The cadence bar represents elapsed time toward the next 5-minute refresh opportunity, not provider fetch progress.
- The separate top Overview auto-refresh panel was removed after user feedback; manual and browser-auto refresh now share one Market Movers refresh surface.
- The countdown / cadence bar updates every second in browser-side JS, while provider collection still goes through the 5-minute cadence guard.
- UI stability means preserving the investment research workflow and data guardrails, not repeating the same `container / badge / card` visual pattern. Market Movers `데이터 갱신` should behave like a status / action bar, with internal run details hidden behind an expander.
