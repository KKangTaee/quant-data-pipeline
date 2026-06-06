# Risk-On Momentum 5D V2 Notes

## Decisions

- V2 remains Backtest Analysis research output.
- Practical Validation / Final Review / Selected Dashboard governance is deferred.
- ATR defaults to simple rolling mean because V1 already calculated `atr14` that way.
- `ranking_penalty` does not override the `risk_on_min` hard gate.

## Existing Dirty Worktree

- `.aiworkspace/note/finance/saved/SELECTED_DASHBOARD_PORTFOLIOS.jsonl`
- `finance/.DS_Store`
- `.aiworkspace/note/finance/run_history/BACKTEST_RUN_HISTORY.jsonl`

These are not part of this task and should not be staged.
