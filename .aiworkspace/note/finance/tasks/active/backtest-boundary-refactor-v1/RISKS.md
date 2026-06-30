# Backtest Boundary Refactor V1 Risks

- Large Streamlit files rely on wildcard imports from `backtest_common.py`; extraction must keep compatibility exports until callers are migrated.
- Generated QA PNG files are present in the worktree and must not be staged.
- Refactor should not alter strategy calculations or validation pass/block thresholds.
