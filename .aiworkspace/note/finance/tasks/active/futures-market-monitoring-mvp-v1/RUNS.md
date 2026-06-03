# Futures Market Monitoring MVP V1 Runs

## 2026-06-03 Live Futures Charts Missing Fix

- Reproduction on `http://localhost:8501`:
  - Result: `Overview > Futures Monitor > Live Futures Charts` showed `3/6 symbols`, with `NQ=F`, `6E=F`, and `6J=F` missing after latest yfinance 1d / 1m runs.
- DB evidence:
  - `futures_ohlcv` had older rows for the missing symbols but `rows_in_6h=0`.
  - Recent `futures_market_monitor_run` rows had `partial_success` and `failed_symbols_json=["6E=F", "6J=F", "NQ=F"]`.
- Provider evidence:
  - yfinance `period=1d`, `interval=1m` returned empty rows for `NQ=F`, `6E=F`, `6J=F`.
  - yfinance `period=2d`, `interval=1m` returned current rows for the same symbols.
- TDD:
  - `uv run python -m unittest tests.test_service_contracts.FuturesMarketMonitoringContractTests.test_futures_collector_recovers_empty_1d_intraday_symbols_with_2d_retry`
  - Result before implementation: FAIL, missing second downloader call.
  - Result after implementation: PASS.
- Focused contracts:
  - `uv run python -m unittest tests.test_service_contracts.FuturesMarketMonitoringContractTests`
  - Result: PASS, 5 tests.
- Compile / full contracts / boundary:
  - `uv run python -m py_compile finance/data/futures_market.py app/jobs/ingestion_jobs.py app/services/futures_market_monitoring.py app/web/overview_dashboard.py`
  - Result: PASS.
  - `uv run python -m unittest tests.test_service_contracts`
  - Result: PASS, 244 tests. Streamlit cache and `edgar` deprecation warnings were emitted by dependencies.
  - `uv run python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py`
  - Result: PASS, hard violations none.
  - `git diff --check`
  - Result: PASS.
- Runtime refresh:
  - `run_collect_futures_ohlcv(["NQ=F", "ZN=F", "CL=F", "6E=F", "GC=F", "6J=F"], period="1d", interval="1m", cadence_mode="manual_fix_after_restart", max_symbols=6, batch_size=6, sleep_sec=0)`
  - Result: `status=success`, `rows_written=3973`, `symbols_processed=6`, `failed_symbols=[]`, fallback recovered `NQ=F`, `6E=F`, `6J=F`.
- Browser QA:
  - Restarted Streamlit on port 8501 because the existing process had `--server.runOnSave false`.
  - Verified `Live Futures Charts` shows `6/6 symbols`, Provider Run `success`, no missing warning, and a stale warning only because yfinance latest candles were 11-21 minutes old.
  - Screenshot: `.playwright-mcp/futures-monitor-live-charts-fixed-20260603.jpg` (generated artifact, not for commit).

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

## 2026-06-02 Follow-up: Cross-Asset Core Verification

- Full core futures collection:
  - Command: `run_collect_futures_ohlcv(DEFAULT_CORE_FUTURES_SYMBOLS, period="1d", interval="1m", max_symbols=16, batch_size=4, sleep_sec=0.5)`.
  - Result: `status=success`, `rows_written=19208`, `symbols_processed=16`, `failed_symbols=[]`, `latest_candle_time_utc=2026-06-02 02:10:00`.
  - Batches:
    - Equity index `ES=F`, `NQ=F`, `YM=F`, `RTY=F`: 5067 rows.
    - Rates / major commodities `ZN=F`, `ZB=F`, `CL=F`, `GC=F`: 4773 rows.
    - Commodities / FX `SI=F`, `HG=F`, `NG=F`, `6E=F`: 4770 rows.
    - FX `6J=F`, `6B=F`, `6A=F`, `6C=F`: 4598 rows.
- Symbol-level DB check:
  - All 16 symbols had stored 1m rows after the collection run.
  - Latest provider candles were around `2026-06-02 02:09:00` to `2026-06-02 02:10:00` UTC.
  - Snapshot status remained `REVIEW` because free yfinance futures candles were about 10-13 minutes behind wall-clock time, which is intentionally surfaced as provider freshness risk.
- Default watchlist decision:
  - `Pre-open Core` uses `NQ=F` (equity index / risk growth), `ZN=F` (rates), `CL=F` (oil), and `6E=F` (FX / dollar context) as the default 2x2 grid.
- `uv run python -m py_compile finance/data/futures_market.py app/services/futures_market_monitoring.py app/web/overview_dashboard.py tests/test_service_contracts.py`
  - Result: PASS.
- `uv run python -m unittest tests.test_service_contracts.FuturesMarketMonitoringContractTests`
  - Result: PASS, 4 tests.
- `uv run python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py`
  - Result: PASS.
- `git diff --check`
  - Result: PASS.
- `uv run python -m unittest tests.test_service_contracts`
  - Result: PASS, 226 tests.
- Browser QA:
  - Ran Streamlit on `http://localhost:8515`.
  - Verified default `Pre-open Core` opens with `NQ=F`, `ZN=F`, `CL=F`, `6E=F`.
  - Verified the 2x2 mini chart grid renders the cross-asset set and keeps `NQ=F Detail` below.
  - Browser console errors: none.
  - Screenshots: `futures-preopen-core-qa-top.png`, `futures-preopen-core-qa-lower.png`.
