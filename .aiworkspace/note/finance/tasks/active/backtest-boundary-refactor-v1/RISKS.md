# Backtest Boundary Refactor V1 Risks

- Large Streamlit files rely on wildcard imports from `backtest_common.py`; extraction must keep compatibility exports until callers are migrated.
- Generated QA PNG files are present in the worktree and must not be staged.
- Refactor should not alter strategy calculations or validation pass/block thresholds.

## V2-V8 closeout

- Residual risk: `app/web/backtest_common.py` remains a transitional shared helper. This is now smaller follow-up cleanup, not a blocker for the package boundary refactor.
- Compatibility note: ETF price runner modules use `app.runtime.backtest` / runner-module hook resolution so existing tests and service tools that patch facade-level runtime helpers continue to work after the physical runner split.
- Generated QA PNG files remain local artifacts and should continue to stay untracked unless explicitly requested.
