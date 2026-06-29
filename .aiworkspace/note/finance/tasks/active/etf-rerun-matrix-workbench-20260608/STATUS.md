# ETF Rerun Matrix Workbench 4B Status

## 2026-06-08

- Started 4B after 4A commit `84f47999`.
- Scope fixed to session-only ETF rerun matrix for Global Relative Strength, Risk Parity Trend, and Dual Momentum.
- Current worktree has untracked generated `.aiworkspace/note/finance/run_history/BACKTEST_RUN_HISTORY.jsonl`; it remains out of scope and will not be staged.
- Implemented `app/services/backtest_etf_rerun_matrix.py` with Streamlit-free matrix plan and selected-strategy runner execution.
- Connected `ETF Rerun Matrix Workbench` to Backtest Analysis after ETF Current Anchor Workbench.
- Browser QA verified panel text, 3 strategies, 9 scenarios, disabled run-on-render / artifact-writes metrics, and run button.
- Final focused regression, py_compile, UI-engine boundary, and `git diff --check` passed.
- Status: completed; pending commit.
