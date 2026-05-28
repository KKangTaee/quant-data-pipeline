# Status

- 2026-05-28: Task opened after FOMC collector completion. Prototype source selected: `yfinance.Ticker(...).calendar` for bounded symbol sets.
- 2026-05-28: Implemented `EARNINGS` event collection into `finance_meta.market_event_calendar`, job wrapper, Ingestion prototype tab, and Overview Events refresh/filter UI.
- 2026-05-28: Local smoke wrote 3 earnings rows for `AAPL`, `MSFT`, `NVDA`; latest movers symbol loader reads the latest S&P 500 intraday snapshot.
- 2026-05-28: Contract tests, diff check, DB smoke, and Browser smoke passed.
