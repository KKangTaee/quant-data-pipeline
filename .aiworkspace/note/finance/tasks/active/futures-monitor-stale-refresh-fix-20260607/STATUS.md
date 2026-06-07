# Status

## Current

- 2026-06-07: Completed.

## Completed

- Root cause identified: Futures Monitor service loaded 1m candles from `UTC_TIMESTAMP() - lookback`, so valid stored candles disappeared from the chart when yfinance's latest candle was delayed or the futures market was closed.
- Fix implemented: service now loads each selected symbol's chart window relative to that symbol's latest stored candle while preserving current-time stale status.
- Regression coverage added for latest-stored-candle anchored chart loading.

## Next

- No immediate follow-up. If yfinance returns unchanged latest candles, the UI will show latest stored data as `Stale`; provider freshness still depends on yfinance availability.
