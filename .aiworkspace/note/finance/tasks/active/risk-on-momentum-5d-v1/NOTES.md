# Risk-On Momentum 5D V1 Notes

## Decisions

- User approved Single Strategy placement.
- User approved generated run artifact storage for full trade / scanner rows.
- User approved Top1000 as default universe.
- User approved macro hard filter based on `Mean Z`.
- User approved Equal Slot position sizing.
- V1 implementation keeps unsupported modes out of the UI contract: `execution_mode=close_based`, `exit_mode=fixed_pct`.
- `holding_days` in the trade log is the signal holding-day count through the exit signal close. The actual exit still executes at next trading-day open.
- Top1000 / Top2000 are resolved from market-cap universe members first, with asset-profile market-cap fallback.

## Existing Dirty Worktree

- `.aiworkspace/note/finance/saved/SELECTED_DASHBOARD_PORTFOLIOS.jsonl`, `finance/.DS_Store`, and existing QA images are pre-existing dirty/generated files and are not part of this task.
- Generated Risk-On Momentum DB smoke artifact under `.aiworkspace/note/finance/backtest_artifacts/` is validation output and should not be committed unless explicitly requested.
