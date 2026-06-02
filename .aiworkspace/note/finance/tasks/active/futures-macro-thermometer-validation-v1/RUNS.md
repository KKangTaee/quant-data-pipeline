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
- Historical validation smoke after 5y backfill, before follow-up review fixes:
  - Result: `validation_status=OK`, `validation_dates=1198`, `history_span_years=5.0`, `target_sources=["futures"]`, `used_etf_proxy_target=False`.
  - Current scenario: `혼재된 매크로 흐름`; confidence: `Medium Confidence`, score `5`, sample `942`, 5D hit rate not forced because mixed scenario has no directional hit rule. Follow-up review corrected this display contract so mixed scenario occurrence count is not reported as directional sample size.
- Browser QA:
  - Ran Streamlit on `http://localhost:8517`.
  - in-app Browser DOM confirmed `Interpretation Confidence`, `Historical Validation Summary`, `Strong Evidence`, `Weak Evidence`, `Conflicting Evidence`, `Score / Forward Return Relationships`, and `Score Threshold Sensitivity` render in `Overview > Futures Monitor > Macro Thermometer`.
  - in-app Browser console errors: none.
  - in-app screenshot API timed out on this long Streamlit page, so QA screenshot was captured with an isolated headless Chrome DevTools session after DOM verification.
  - Screenshot: `futures-macro-thermometer-validation-qa.png`.

## 2026-06-02 follow-up review fixes

- `uv run python -m py_compile app/services/futures_macro_validation.py app/services/futures_macro_thermometer.py app/web/overview_dashboard.py tests/test_service_contracts.py`
  - Result: PASS.
- `uv run python -m unittest tests.test_service_contracts.FuturesMacroThermometerContractTests`
  - Result: PASS, 8 tests.
- `uv run python -m unittest tests.test_service_contracts`
  - Result: PASS, 234 tests.
- `uv run python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py`
  - Result: PASS, hard violations none, advisories none.
- `git diff --check`
  - Result: PASS.
- Performance smoke:
  - Before follow-up review fix: default validated snapshot measured about `25.1s` to `25.6s`; first vectorized pass measured about `15.9s` to `16.2s`.
  - After target-return vectorization and Overview cache: first compute `7.185s`; repeated same-process calls `0.000s`, `0.000s`.
- Historical validation smoke after follow-up:
  - Result: `validation_status=OK`, `validation_dates=1198`, `history_span_years=5.0`.
  - Current scenario: `혼재된 매크로 흐름`; confidence: `Medium Confidence`, score `3`, directional sample `0`, occurrence count `938`, hit rate N/A because mixed scenarios are not forced into a directional hit rule.
- Browser QA after follow-up:
  - Ran Streamlit on `http://localhost:8517`.
  - in-app Browser DOM confirmed `Interpretation Confidence`, `directional hit n/a`, `Current Scenario History`, `5D False Positive`, `Score / Forward Return Relationships`, and `Score Threshold Sensitivity`.
  - in-app Browser console errors: none.
  - in-app screenshot API timed out again, so final screenshot was captured through an isolated headless Chrome DevTools session.
  - Screenshot: `futures-macro-thermometer-followup-qa.png`.
