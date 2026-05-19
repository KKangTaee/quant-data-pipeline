# Compare Service Boundary Notes

Status: Implementation complete
Created: 2026-05-19

## Findings

- `app/web/backtest_compare.py` contains the strategy runner catalog near the top of the file.
- Manual compare submit flow validates UI inputs, then loops over selected strategy execution names and calls `_run_compare_strategy`.
- The previous compare submit flow caught `BacktestInputError`, `BacktestDataError`, and generic exceptions directly inside the Streamlit file.
- Weighted portfolio construction depends on `make_monthly_weighted_portfolio`, `build_backtest_result_bundle`, and data-only helper functions currently imported through `backtest_result_display.py`.
- Saved portfolio replay used to combine strategy rerun, weighted bundle construction, session state mutation, and history append in one UI function.

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

### Slice 3

Weighted portfolio bundle construction now lives in `app/services/backtest_weighted_portfolio.py`.
The service receives strategy result bundles, weights, date policy, optional saved portfolio identity, and compare source context.
It returns the same weighted result bundle shape previously built inside the UI file.

To avoid importing `app/web/backtest_result_display.py` into a service, data-only helpers moved to `app/services/backtest_result_read_model.py`:

- strategy data trust rows
- monthly component contribution amount/share views

`app/web/backtest_result_display.py` keeps its existing private helper names as wrappers, so display callers do not need to know about the service split.

### Slice 4

Saved portfolio replay execution / data assembly now lives in `app/services/backtest_saved_portfolio_replay.py`.
The service returns a `SavedPortfolioReplayResult` that includes strategy bundles, weighted bundle, replay source context, and both history append contexts.

`app/web/backtest_compare.py` still owns UI side effects:

- session state mutation
- run history append call
- success / error notice behavior
- saved mix result render

Dynamic PIT universe replay still uses the existing `_resolve_saved_portfolio_dynamic_inputs(...)` callback from the UI module.
That keeps the new service free of `app/web/backtest_common.py` imports until a later preset/universe-helper split.

## Follow-Up Design Constraint

Compare boundary implementation is now complete for this phase slice.
The next phase task should focus on Practical Validation computation/save/handoff boundaries.
