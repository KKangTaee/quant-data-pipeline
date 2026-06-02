# Futures Macro Thermometer V1 Runs

## 2026-06-02

- `uv run python -m py_compile app/services/futures_macro_thermometer.py finance/data/futures_market.py app/web/overview_dashboard.py app/web/streamlit_app.py tests/test_service_contracts.py`
  - Result: PASS.
- `uv run python -m unittest tests.test_service_contracts.FuturesMacroThermometerContractTests`
  - Result: PASS, 3 tests.
- `uv run python -m unittest tests.test_service_contracts.FuturesMarketMonitoringContractTests tests.test_service_contracts.FuturesMacroThermometerContractTests`
  - Result: PASS, 7 tests.
- Daily futures macro backfill smoke:
  - Command: `collect_and_store_futures_ohlcv(DEFAULT_CORE_FUTURES_SYMBOLS, period="1y", interval="1d", cadence_mode="manual_macro_daily_smoke", max_symbols=16, batch_size=4, sleep_sec=0.5)`.
  - Result: `status=success`, `rows_written=4032`, `symbols_processed=16`, `failed_symbols=[]`, `latest_candle_time_utc=2026-06-01 00:00:00`.
- Macro thermometer read-model smoke:
  - Result: `status=OK`, `standardized_count=16/16`, `min_data_days=252`, `max_data_days=252`, `latest_daily_date=2026-06-01`.
  - Scenario at smoke time: `혼재된 매크로 흐름`.
- `uv run python -m unittest tests.test_service_contracts`
  - Result: PASS, 229 tests.
- `uv run python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py`
  - Result: PASS.
- `git diff --check`
  - Result: PASS.
- Browser QA:
  - Ran Streamlit on `http://localhost:8516`.
  - Verified `Overview > Futures Monitor > Macro Thermometer` renders today's interpretation, 16 / 16 daily coverage, six score cards, score table, and stale 1m warning separately from daily macro coverage.
  - Current-page browser console errors: none.
  - Screenshot: `futures-macro-thermometer-qa-body.png`.
