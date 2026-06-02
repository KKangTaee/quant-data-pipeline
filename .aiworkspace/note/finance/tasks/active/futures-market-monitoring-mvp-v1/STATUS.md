# Futures Market Monitoring MVP V1 Status

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
