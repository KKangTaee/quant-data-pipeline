# Risks

- Streamlit fragment execution can briefly block the visible session when the collector runs.
- Multiple browser tabs can trigger checks, so the existing automation lock and cadence guard must stay in the path.
- US market-hours guard still does not include a full exchange holiday calendar.
