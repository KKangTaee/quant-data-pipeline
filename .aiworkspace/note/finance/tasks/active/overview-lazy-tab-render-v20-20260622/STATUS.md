# Status

## 2026-06-22

- Completed.
- `Workspace > Overview` top-level deep tabs now render only the selected section instead of eagerly rendering all `st.tabs` bodies.
- Default selection remains `Market Context`.
- `Candidate Ops` loads `load_overview_dashboard_snapshot()` only after `Candidate Ops` is selected.
- Browser QA confirmed default `Market Context` shows without `Market Movers` scan content, and selecting `Market Movers` renders that panel on demand.
