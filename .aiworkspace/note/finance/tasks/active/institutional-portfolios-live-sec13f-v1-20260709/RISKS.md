# Institutional Portfolios Live SEC 13F V1 Risks

- SEC official dataset ZIP can be large; focused tests should use synthetic ZIP fixtures and avoid requiring a live full download.
- CUSIP to ticker mapping is best effort and may leave sector / industry unmapped.
- 13F filings are delayed and incomplete; UI copy must avoid buy / sell recommendations.
- Local MySQL may be unavailable during QA; tests should cover pure parser/service contracts without requiring DB where possible.
- Direct route Browser QA can trigger Streamlit's route fallback log. Normal app rendering still displayed the workbench, but future QA can also navigate through the top-level Workspace menu to avoid this console noise.
- The local DB was not populated with the full 94MB official SEC dataset during this task. The implemented path is ready for explicit refresh, but a real production load still depends on running the official SEC dataset job with a valid SEC user agent.
