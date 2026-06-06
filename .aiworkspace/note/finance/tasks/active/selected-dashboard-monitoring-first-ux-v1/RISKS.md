# Risks

- Browser QA passed on the existing local Streamlit server at port `8503`.
- Dirty worktree already included `SELECTED_DASHBOARD_PORTFOLIOS.jsonl`, `finance/.DS_Store`, and many generated screenshots before this task; do not stage those unrelated generated/local artifacts.
- Scenario replay remains synchronous and can still be slow for full refresh; this task only changed information architecture and explicit update placement.
