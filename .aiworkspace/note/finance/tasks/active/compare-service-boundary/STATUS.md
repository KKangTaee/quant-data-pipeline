# Compare Service Boundary Status

Status: Implementation complete
Created: 2026-05-19

## Current State

- Slice 1, Slice 2, Slice 3, and Slice 4 are implemented.
- `app/services/backtest_compare_execution.py` owns manual compare execution loop and error normalization.
- `app/services/backtest_compare_catalog.py` owns compare strategy runner defaults, preset/manual universe resolution, runtime dispatch, and runner signature filtering.
- `app/services/backtest_weighted_portfolio.py` owns weighted portfolio result bundle construction.
- `app/services/backtest_result_read_model.py` owns Streamlit-free data trust rows and monthly component contribution views used by weighted portfolio construction.
- `app/services/backtest_saved_portfolio_replay.py` owns saved portfolio replay execution and replay history context assembly.
- `app/web/backtest_compare.py` delegates manual compare execution, strategy dispatch, weighted bundle construction, and saved replay data assembly to services, while keeping session state / history append / render behavior.
- The UI still supplies `ComparePresetCatalog` because preset dictionaries currently live in Streamlit-adjacent `app/web/backtest_common.py`.
- Saved replay dynamic PIT universe handling is injected as a UI callback because the resolver still lives in `app/web/backtest_common.py`.

## Next Step

Move back to the phase board and start `practical-validation-service-boundary`.
For Compare, remaining validation is manual DB-backed app QA when a suitable DB state is available.
