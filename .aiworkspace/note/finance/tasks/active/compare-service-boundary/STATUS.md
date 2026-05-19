# Compare Service Boundary Status

Status: In progress
Created: 2026-05-19

## Current State

- Slice 1 is implemented.
- `app/services/backtest_compare_execution.py` owns manual compare execution loop and error normalization.
- `app/web/backtest_compare.py` delegates manual compare execution to the service and keeps session state / history append / render behavior.
- Strategy runner catalog, weighted portfolio builder, and saved portfolio replay remain in `app/web/backtest_compare.py`.

## Next Step

Decide whether the next slice should move:

- the strategy runner catalog (`_strategy_compare_defaults`, `_run_compare_strategy`), or
- the weighted portfolio builder data-only helpers.

The safer next slice is the strategy runner catalog, but it requires extracting strict universe presets without importing `backtest_common.py` into `app/services`.
