# Notes

- `Ticker.get_earnings_dates()` returns richer timestamps and estimates but was observed taking several seconds per symbol in a small smoke. It is too slow for an Overview button prototype.
- `Ticker.calendar` returns the upcoming `Earnings Date` and estimate fields much faster after provider session warmup.
- Earnings dates from free Yahoo/yfinance are provider estimates and should be treated as low-to-medium confidence schedule hints, not official company IR truth.
- Prototype event rows use `event_type=EARNINGS`, `source=yfinance_calendar`, and `confidence=0.65`.
- Overview refresh defaults to latest S&P 500 movers from `market_intraday_snapshot` with `top_movers_limit=20`; Ingestion also supports a manual symbol mode for targeted checks.
- Broad Coverage 1000/2000 earnings scans remain out of scope because Yahoo/yfinance calendar calls are per-symbol and can become slow or rate-limited.
