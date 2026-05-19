# Compare Service Boundary Notes

Status: In progress
Created: 2026-05-19

## Findings

- `app/web/backtest_compare.py` contains the strategy runner catalog near the top of the file.
- Manual compare submit flow validates UI inputs, then loops over selected strategy execution names and calls `_run_compare_strategy`.
- The previous compare submit flow caught `BacktestInputError`, `BacktestDataError`, and generic exceptions directly inside the Streamlit file.
- Weighted portfolio construction depends on `make_monthly_weighted_portfolio`, `build_backtest_result_bundle`, and data-only helper functions currently imported through `backtest_result_display.py`.
- Saved portfolio replay also calls `_run_compare_strategy` and `_build_weighted_portfolio_bundle`, but it additionally owns session state and history append side effects.

## Implemented Slice

### Slice 1

Manual compare execution now calls `execute_strategy_compare(...)`.
The service receives the selected execution names, common date/timeframe/option inputs, strategy override map, and the temporary runner callback.

This keeps the first slice small:

- no chart behavior change
- no history append behavior change
- no registry change
- no weighted portfolio behavior change
- no saved replay behavior change

### Slice 2

Strategy runner catalog and compare defaults now live in `app/services/backtest_compare_catalog.py`.
`app/web/backtest_compare.py` keeps a small `_compare_preset_catalog()` wrapper and passes current preset dictionaries into the service.

This deliberately avoids a service import of `app/web/backtest_common.py`, because that module imports Streamlit and owns broad UI/session-state helpers.

Moved responsibilities:

- `_strategy_compare_defaults`
- strict annual / quarterly default parameter assembly
- Equal Weight / GTAA / Global Relative Strength preset vs manual ticker resolution
- strict Quality / Value preset universe resolution
- runtime runner signature filtering

## Follow-Up Design Constraint

The next move should avoid importing display modules into a service.
Weighted portfolio construction currently reaches data-only helper behavior through `app/web/backtest_result_display.py`, which is display-oriented.
Before moving `_build_weighted_portfolio_bundle`, extract or identify a Streamlit-free result-bundle helper boundary.
