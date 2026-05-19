# Compare Service Boundary Status

Status: In progress
Created: 2026-05-19

## Current State

- Slice 1, Slice 2, and Slice 3 are implemented.
- `app/services/backtest_compare_execution.py` owns manual compare execution loop and error normalization.
- `app/services/backtest_compare_catalog.py` owns compare strategy runner defaults, preset/manual universe resolution, runtime dispatch, and runner signature filtering.
- `app/services/backtest_weighted_portfolio.py` owns weighted portfolio result bundle construction.
- `app/services/backtest_result_read_model.py` owns Streamlit-free data trust rows and monthly component contribution views used by weighted portfolio construction.
- `app/web/backtest_compare.py` delegates manual compare execution and strategy dispatch to services, while keeping session state / history append / render behavior.
- The UI still supplies `ComparePresetCatalog` because preset dictionaries currently live in Streamlit-adjacent `app/web/backtest_common.py`.
- Saved portfolio replay orchestration remains in `app/web/backtest_compare.py`, but it now uses the weighted portfolio service for bundle construction.

## Next Step

Decide whether the next slice should move:

- the saved portfolio replay execution path.

The next slice is saved portfolio replay execution, which still combines strategy reruns, session state, notices, and history append in the UI file.
