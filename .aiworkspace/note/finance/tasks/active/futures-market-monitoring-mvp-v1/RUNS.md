# Futures Market Monitoring MVP V1 Runs

## 2026-06-02

- `uv run python -m py_compile finance/data/futures_market.py finance/data/db/schema.py app/jobs/ingestion_jobs.py app/jobs/run_history.py app/services/futures_market_monitoring.py app/services/overview_market_intelligence.py app/web/overview_dashboard.py app/web/streamlit_app.py`
  - Result: PASS.
- `uv run python -m unittest tests.test_service_contracts.FuturesMarketMonitoringContractTests tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_collection_ops_snapshot_combines_db_freshness_and_run_history tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_collection_ops_snapshot_supports_legacy_event_calendar_schema tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_collection_ops_snapshot_marks_macro_calendar_due_when_some_macro_types_missing`
  - Result: PASS.
- `uv run python -m unittest tests.test_service_contracts`
  - Result: PASS, 225 tests.
- Futures collector smoke:
  - Command: `run_collect_futures_ohlcv(["ES=F", "NQ=F"], period="1d", interval="1m", max_symbols=2, batch_size=2, sleep_sec=0)`
  - Result: success; `rows_written=2354`, `symbols_processed=2`, `latest_candle_time_utc=2026-06-02 00:36:00`.
- Futures read-model smoke:
  - Command: `build_futures_monitor_snapshot(group="Equity Index", symbols=["ES=F", "NQ=F"], selected_symbol="ES=F", lookback_minutes=360)`
  - Result: `status=REVIEW`, `returnable_count=2`, `stale_count=2`, `candles=286`; stale warning expected because free provider latest candle was about 13-14 minutes old during QA.
- `uv run python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py`
  - Result: PASS.
- `git diff --check`
  - Result: PASS.
- Browser QA:
  - Ran Streamlit on `http://localhost:8511`.
  - Verified `Overview > Futures Monitor` renders status cards, `Shock Board`, `Candles`, `Provider Run`, stale / missing warnings, and an `ES=F` candlestick chart.
  - Browser console errors: none.
  - Screenshot: `.playwright-mcp/futures-monitor-qa.png`.

## 2026-06-02 Follow-up: 2x2 Mini Chart Grid

- `uv run python -m py_compile app/web/overview_dashboard.py app/services/futures_market_monitoring.py tests/test_service_contracts.py`
  - Result: PASS.
- `uv run python -m unittest tests.test_service_contracts.FuturesMarketMonitoringContractTests`
  - Result: PASS, 3 tests.
- `uv run python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py`
  - Result: PASS.
- `git diff --check`
  - Result: PASS.
- `uv run python -m unittest tests.test_service_contracts`
  - Result: PASS, 225 tests.
- Browser QA:
  - Ran Streamlit on `http://localhost:8512`.
  - Verified `Overview > Futures Monitor > Candles` renders a two-column mini chart grid for selected symbols.
  - Verified `ES=F` / `NQ=F` mini candlesticks render, `YM=F` / `RTY=F` missing cards show `-` for unavailable 15m / age metrics, and the selected-symbol detail chart remains below.
  - Browser console errors: none.
  - Screenshots: `futures-monitor-grid-qa-top-fixed.png`, `futures-monitor-grid-qa-lower-fixed.png`.

## 2026-06-02 Follow-up: Human-Readable Symbol Titles

- `uv run python -m py_compile app/web/overview_dashboard.py`
  - Result: PASS.
- `uv run python -m unittest tests.test_service_contracts.FuturesMarketMonitoringContractTests`
  - Result: PASS, 3 tests.
- Browser QA:
  - Ran Streamlit on `http://localhost:8514`.
  - Verified `Overview > Futures Monitor > Candles` shows contract subtitles under mini chart symbols, including `ES=F` -> `E-mini S&P 500 · Equity Index` and `NQ=F` -> `E-mini Nasdaq 100 · Equity Index`.
  - Browser console errors: none.
  - Screenshot: `futures-monitor-symbol-title-qa.png`.
