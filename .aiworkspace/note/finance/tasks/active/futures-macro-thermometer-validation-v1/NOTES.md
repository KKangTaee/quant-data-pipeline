# Futures Macro Thermometer Validation V1 Notes

## Initial Observations

- V1 computes symbol metrics from daily `futures_ohlcv` rows, then derives six score rows and a scenario summary.
- `compute_symbol_metrics`, `compute_macro_scores`, and `generate_market_interpretation` can be reused by a validation service if historical slices are converted to the same candle frame format.
- Current daily refresh uses `period=1y`, `interval=1d`; validation needs a longer lookback, preferably `5y`.
- No new persistence is needed for the first validation UI: the summary can be recomputed from existing price ledgers.

## Data Caveats

- yfinance continuous futures symbols are provider-maintained continuous series, not exchange-grade roll-adjusted tradable contract histories.
- ETF proxies are validation substitutes, not futures validation.
- Historical consistency metrics are not prediction guarantees.
