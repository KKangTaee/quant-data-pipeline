# Compare Service Boundary Status

Status: In progress
Created: 2026-05-19

## Current State

- Slice 1 and Slice 2 are implemented.
- `app/services/backtest_compare_execution.py` owns manual compare execution loop and error normalization.
- `app/services/backtest_compare_catalog.py` owns compare strategy runner defaults, preset/manual universe resolution, runtime dispatch, and runner signature filtering.
- `app/web/backtest_compare.py` delegates manual compare execution and strategy dispatch to services, while keeping session state / history append / render behavior.
- The UI still supplies `ComparePresetCatalog` because preset dictionaries currently live in Streamlit-adjacent `app/web/backtest_common.py`.
- Weighted portfolio builder and saved portfolio replay remain in `app/web/backtest_compare.py`.

## Next Step

Decide whether the next slice should move:

- the weighted portfolio builder data-only helpers.
- the saved portfolio replay execution path.

The safer next slice is the weighted portfolio builder, but it requires extracting data-only bundle helpers currently imported through `app/web/backtest_result_display.py`.
