# Overview Legacy Dashboard Removal V17-V24 Risks

- `legacy_dashboard.py` still mixes Streamlit UI glue, chart builders, cached read wrappers, action facade calls, and tests importing private helpers through `overview_dashboard.py`.
- Moving the file by renaming it would not meet the goal. The migration should move helper bodies into domain owners or remove obsolete helpers.
- Hidden risk is highest in Market Movers and Futures Macro because tests still exercise private helper functions there.

