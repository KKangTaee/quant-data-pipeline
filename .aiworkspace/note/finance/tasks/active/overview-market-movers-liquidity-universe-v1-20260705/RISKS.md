# Risks

- Full DB smoke may be limited by local provider speed and current DB state.
- Browser QA depends on local Streamlit/component runtime availability.
- Materialized Top2000 can contain fewer than 2000 rows when listing coverage or recent EOD price rows are insufficient; UI copy must make that explicit.
