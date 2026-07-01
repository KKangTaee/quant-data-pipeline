# Risks

## 2026-07-01

- Streamlit UI is a large single file; structural edits can accidentally change widget keys or session-state behavior.
- Browser QA may need a running app and DB availability; if DB connection fails, QA should still verify the top-level layout renders to the first recoverable point.
- Existing untracked/generated files must not be staged: `.aiworkspace/note/finance/run_history/BACKTEST_RUN_HISTORY.jsonl`, `.superpowers/`, and `finance/.DS_Store`.
