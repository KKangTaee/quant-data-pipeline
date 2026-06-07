# Design

## Data Flow

```text
Refresh Futures OHLCV
  -> app/jobs/overview_actions.py
  -> app/jobs/ingestion_jobs.py
  -> finance/data/futures_market.py
  -> finance_price.futures_ohlcv
  -> app/services/futures_market_monitoring.py
  -> app/web/overview_dashboard.py
```

## Initial Finding

`app/services/futures_market_monitoring.py` loads 1m candles with `candle_time_utc >= DATE_SUB(UTC_TIMESTAMP(), INTERVAL lookback MINUTE)`.

This makes the visible chart window depend on wall-clock UTC instead of the latest stored candle. During futures breaks, weekends, holidays, delayed yfinance responses, or sparse symbol responses, a successful refresh can store rows whose latest candle is outside the selected lookback from current UTC. The service then returns empty chart data and `Missing`, even though stored rows exist and should be displayed as latest available stale context.

## Direction

- Change the service candle query to anchor each selected symbol's window to that symbol's latest stored candle.
- Keep staleness calculation anchored to actual current time, so old data is still labeled `Stale`.
- Do not change ingestion semantics or provider status.
