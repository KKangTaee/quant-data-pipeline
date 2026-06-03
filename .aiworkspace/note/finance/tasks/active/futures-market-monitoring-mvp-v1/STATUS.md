# Futures Market Monitoring MVP V1 Status

## 2026-06-03

- Fixed `Overview > Futures Monitor > Live Futures Charts` missing coverage after yfinance returned empty `period=1d`, `interval=1m` data for `NQ=F`, `6E=F`, and `6J=F`.
- Root cause: Yahoo/yfinance returned no 1d intraday rows for some futures while `period=2d`, `interval=1m` returned the latest candles for the same symbols.
- `finance/data/futures_market.py` now retries only empty 1d / 1m futures symbols once with 2d / 1m, removes recovered symbols from failed coverage, and records `fallback_retries` in run diagnostics.
- Restarted the 8501 Streamlit server so the running app loaded the new collector; refreshed the current Pre-open Core set and verified Live Futures Charts at 6/6 returnable symbols with Provider Run `success`.

## 2026-06-02

- Started after user approval to implement the researched Futures Monitor direction.
- Classified as DB ingestion + Overview market intelligence UI work.
- Research source: `.aiworkspace/note/finance/researches/active/2026-06-futures-market-monitoring/`.
- Implemented DB-backed futures monitoring MVP:
  - `finance/data/futures_market.py` provides `yfinance` pilot 1m OHLCV collection, instrument seed rows, idempotent UPSERT, and provider run diagnostics.
  - `finance/data/db/schema.py` now includes `futures_instrument`, `futures_market_monitor_run`, and `futures_ohlcv`.
  - `app/jobs/ingestion_jobs.py` exposes `collect_futures_ohlcv`; run history maps it to the Overview futures monitor context.
  - `app/services/futures_market_monitoring.py` builds the Streamlit-free read model for status cards, shock rows, selected candles, stale / missing warnings, and latest run evidence.
  - `app/web/overview_dashboard.py` adds `Overview > Futures Monitor` with bounded manual / 60s / 20s refresh modes, shock board, candlestick chart, and provider run view.
  - `app/web/streamlit_app.py` adds a manual futures OHLCV collection control in `Workspace > Ingestion`.
- Durable docs updated for schema, table semantics, data flow, project map, and Overview market intelligence runbook.
- Focused contracts, full `tests.test_service_contracts`, UI-engine boundary check, collector smoke, and Browser QA passed.
- Follow-up UI change:
  - `Candles` now renders a 2x2 mini candlestick grid for up to four selected futures symbols, with the selected symbol pinned first.
  - The selected symbol detail chart and latest candle table remain below the mini grid.
- Symbol title follow-up:
  - Each mini chart now shows the human-readable contract name and group under the provider symbol, for example `NQ=F` -> `E-mini Nasdaq 100 · Equity Index`.
  - The selected-symbol detail chart also repeats the contract title.
- Cross-asset verification follow-up:
  - Ran the full non-optional core futures set across equity index, rates, commodities, and FX.
  - All 16 symbols wrote 1m OHLCV rows through the yfinance pilot source.
  - `Overview > Futures Monitor` now defaults to `Pre-open Core`: `NQ=F`, `ZN=F`, `CL=F`, `6E=F`.
  - The default 2x2 grid is cross-asset by default instead of equity-index-only.
