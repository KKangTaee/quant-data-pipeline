# Risks

- The selected candidate is a researched backtest candidate and can still be overfit. Practical Validation / Final Review should be run before any selected portfolio workflow.
- The actual result window ends at `2026-02-27` despite the requested end date `2026-05-01`, due to the month-end aligned GTAA result path and local data coverage.
- ADV threshold is part of the strategy contract for this preset. Running the same ticker universe with `Min Avg Dollar Volume 20D=0` disables liquidity policy evidence and will not reproduce the same promotion status.
