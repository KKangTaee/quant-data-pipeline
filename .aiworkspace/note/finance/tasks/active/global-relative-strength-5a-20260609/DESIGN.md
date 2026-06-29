# Global Relative Strength 5A Design

## Current Flow

```text
app/services/backtest_execution.py
  -> app/runtime/backtest.py::run_global_relative_strength_backtest_from_db
  -> finance/sample.py::get_global_relative_strength_from_db
  -> finance/strategy.py::global_relative_strength_allocation
  -> app/runtime/backtest_result_bundle.py::build_backtest_result_bundle
  -> Backtest Analysis latest result / compare / history / replay surfaces
```

## Root Cause Notes

- GRS currently reduces rows with `.interval(interval)` before running the strategy and also passes `rebalance_interval=interval` to the strategy. For `interval > 1`, this can compound cadence.
- `score_return_columns` is accepted at the runtime boundary but normalized mostly through `score_lookback_months`, so replay contracts can drift.
- Risky ticker exclusion exists after transformed data is built, but raw preflight can fail before the exclusion path has a chance to surface metadata.
- Cash proxy return affects balance, but result rows do not clearly expose cash share, unfilled slots, cash proxy return, or concentration diagnostics.
- Benchmark hardening exists, but GRS does not expose a strategy-specific benchmark contract input in the runtime wrapper.

## Planned Contract

- Strategy rows should expose selection and cash semantics:
  - raw selected tickers / scores
  - selected count and target slot count
  - trend rejected tickers and unfilled slot count
  - cash proxy ticker / cash proxy return
  - cash share and max position weight after rebalance
  - concentration status for top-N interpretation
- Runtime meta should preserve:
  - requested / effective / excluded tickers
  - score lookback months, score return columns, and weights
  - trend filter window and rebalance interval
  - cash proxy contract
  - benchmark contract and benchmark ticker
  - price freshness and malformed rows
  - GRS strategy contract summary for Korean-first display

## Testing Design

- Add focused `unittest` tests that import no Streamlit module.
- Prefer synthetic DataFrame fixtures for `global_relative_strength_allocation`.
- Patch runtime DB loaders for bundle metadata tests rather than touching MySQL or JSONL.
- Run red-green cycles for the interval, cash/concentration, and runtime metadata contract.

## UI Design

- Do not add panels.
- Keep `Backtest Analysis` execution-first.
- Use existing Latest Run result tabs / Data Trust / Meta / warnings.
- Adjust Korean copy only where it clarifies GRS runtime behavior.
