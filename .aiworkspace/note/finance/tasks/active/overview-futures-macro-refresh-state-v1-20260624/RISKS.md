# Overview Futures Macro Refresh State V1 Risks

## Risks

- `일봉 매크로 갱신` still depends on yfinance provider availability and should be read as data refresh, not guaranteed exchange-grade data.
- Adding a latest-marker query means each cached load performs a small DB read before deciding whether to reuse the heavy snapshot.

## Mitigation

- The marker query is a single `MAX(candle_time_utc)` over selected symbols and is much cheaper than recomputing historical validation.
- If provider collection fails, the existing job result display remains the source of failure details.
