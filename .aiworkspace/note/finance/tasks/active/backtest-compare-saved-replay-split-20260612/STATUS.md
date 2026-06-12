# Backtest Compare Saved Replay Split 6A Status

Status: Complete
Last Updated: 2026-06-12

## Progress

- Created active task shell for 6A.
- Read required project docs and relevant workflow skills.
- Inventoried saved replay functions, service call boundary, session-state updates, Practical Validation handoff, and run-history append behavior in `app/web/backtest_compare.py`.
- Added `app/web/backtest_compare_saved_replay.py` and moved the saved Mix workspace render/helper surface there.
- Kept `render_compare_portfolio_workspace` as the public entrypoint and reduced the saved replay branch in `app/web/backtest_compare.py` to a context object plus module call.
- Added focused boundary tests in `tests/test_service_contracts.py`.
- Updated durable docs and task records for the new ownership boundary.

## Current Step

6A is complete.

## Next Action

Start 6B: split the weighted result / Practical Validation handoff panel from `app/web/backtest_compare.py` while preserving the current weighted mix source contract.
