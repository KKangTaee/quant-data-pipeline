# Risks

- Streamlit fragment execution can briefly block the visible session when the collector runs, though the blocking is now local to the Market Movers `Data Refresh` surface.
- Multiple browser tabs can trigger checks, so the existing automation lock and cadence guard must stay in the path.
- US market-hours guard still does not include a full exchange holiday calendar.
- Browser-side JS attempts a page reload when the countdown reaches zero; if a browser blocks iframe top navigation, the Streamlit 5-minute fragment heartbeat remains the fallback check path.
