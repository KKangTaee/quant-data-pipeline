# Futures Macro Thermometer Validation V1 Runs

## 2026-06-02

- `uv run python -m py_compile app/services/futures_macro_thermometer.py app/services/futures_macro_validation.py`
  - Result: PASS.
- `uv run python -m py_compile app/services/futures_macro_thermometer.py app/services/futures_macro_validation.py app/web/overview_dashboard.py app/web/streamlit_app.py`
  - Result: PASS.
- `uv run python -m unittest tests.test_service_contracts.FuturesMacroThermometerContractTests`
  - Result: PASS, 5 tests.
- `uv run python -m unittest tests.test_service_contracts`
  - Result: PASS, 231 tests.
- `uv run python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py`
  - Result: PASS, hard violations none, advisories none.
- `git diff --check`
  - Result: PASS.
- Historical validation smoke before 5y backfill:
  - Result: `validation_status=REVIEW`, `validation_dates=191`, `history_span_years=1.0`, reason: stored daily futures history was under 3 years.
- 5y daily futures backfill smoke:
  - Command: `collect_and_store_futures_ohlcv(DEFAULT_CORE_FUTURES_SYMBOLS, period="5y", interval="1d", cadence_mode="manual_macro_validation_5y_smoke", max_symbols=16, batch_size=4, sleep_sec=0.5)`.
  - Result: `status=success`, `rows_written=20138`, `symbols_processed=16/16`, `failed_symbols=[]`, `latest_candle_time_utc=2026-06-01 00:00:00`.
- Historical validation smoke after 5y backfill:
  - Result: `validation_status=OK`, `validation_dates=1198`, `history_span_years=5.0`, `target_sources=["futures"]`, `used_etf_proxy_target=False`.
  - Current scenario: `혼재된 매크로 흐름`; confidence: `Medium Confidence`, score `5`, sample `942`, 5D hit rate not forced because mixed scenario has no directional hit rule.
- Browser QA:
  - Ran Streamlit on `http://localhost:8517`.
  - in-app Browser DOM confirmed `Interpretation Confidence`, `Historical Validation Summary`, `Strong Evidence`, `Weak Evidence`, `Conflicting Evidence`, `Score / Forward Return Relationships`, and `Score Threshold Sensitivity` render in `Overview > Futures Monitor > Macro Thermometer`.
  - in-app Browser console errors: none.
  - in-app screenshot API timed out on this long Streamlit page, so QA screenshot was captured with an isolated headless Chrome DevTools session after DOM verification.
  - Screenshot: `futures-macro-thermometer-validation-qa.png`.
