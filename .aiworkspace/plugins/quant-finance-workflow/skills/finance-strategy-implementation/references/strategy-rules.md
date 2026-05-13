# Strategy Implementation Rules

## Primary Code Areas

- `finance/engine.py`
- `finance/strategy.py`
- `finance/transform.py`
- `finance/performance.py`
- `finance/display.py`
- `finance/visualize.py`
- `finance/sample.py`

## Separation Rules

Use `transform.py` for reusable preprocessing:

- moving averages
- returns
- ranking inputs
- date alignment
- interval sampling
- shared merges and filters

Use `strategy.py` for:

- asset selection
- allocation logic
- cash handling
- rebalance timing
- time-step simulation
- result row construction

Use `engine.py` for orchestration only. Do not move core strategy rules into the engine.

## Input Contract Rules

Before implementing, state:

1. required columns in each asset DataFrame
2. whether dates are already aligned
3. data frequency after filtering
4. required indicators, scores, benchmark series, or cash proxy

If a strategy depends on derived columns like `MA200` or `12MReturn`, generate them in a sample/engine chain or add a reusable engine/transform pattern.

For DB-backed indicator strategies, make warmup history explicit and avoid computing indicators only on the final display slice.

## Result Schema

Minimum compatibility target:

- `Date`
- `Total Balance`
- `Total Return`

If the strategy tracks more state, use additional columns such as `End Ticker`, `Next Ticker`, `End Balance`, `Next Balance`, `Cash`, `Rebalancing`, or `Next Weight`.

If result shape changes materially, document it and check whether `performance.py` still works.

## Strategy Design

- Make rebalance conditions explicit.
- Keep first-period behavior explicit.
- Distinguish end-of-period valuation from next-period allocation.
- State whether uninvested capital is idle cash, cash proxy asset, or partially invested reserve.
- Separate ranking logic from investability filters.
- Keep held positions, next balances, cash, and previous prices readable.

## Reporting And Samples

Check:

- `portfolio_performance_summary(...)`
- `round_columns(...)`
- plotting functions in `visualize.py`

Update `finance/sample.py` when a new core strategy is added, required preprocessing changes, or preferred universe/parameter defaults materially change.

When both direct and DB-backed paths exist, keep direct-fetch samples as reference/smoke examples and `*_from_db` functions as DB-backed runtime examples.

## DB-Backed Runtime

For price-only strategies with loader support:

- prefer `finance/loaders/*` plus a runtime adapter over direct SQL or ad hoc DataFrame reshaping
- keep public path in the order: DB read, runtime preprocessing, strategy run, reporting/result bundle
- preserve strategy-specific runtime inputs in result bundle meta and history records so replay paths can restore forms

If DB-backed paths are expected to match direct paths, check start date, row-count, and final-balance parity or document expected drift.

## Bias And Assumptions

Always check:

- look-ahead bias from future-derived columns
- survivorship bias in the chosen universe
- mismatched frequency assumptions
- implicit use of close prices where adjusted or total-return logic may matter

If the strategy uses accounting or factor data, make point-in-time assumptions explicit.

## Done Condition

- Strategy input contract is explicit.
- Reusable preprocessing lives in `transform.py` when appropriate.
- Simulation logic is clear in `strategy.py`.
- Result output is compatible with reporting or limits are documented.
- `sample.py` reflects new usage patterns.
- Direct-fetch vs DB-backed roles are explicit when both exist.
- DB-backed warmup and parity assumptions are explicit when relevant.
- Project, architecture, or flow docs are updated when durable behavior changes.
