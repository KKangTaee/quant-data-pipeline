# Overview Futures Macro Refresh State V1 Runs

## Commands

- DB latest futures 1D query:
  - All 16 core futures symbols latest `interval_code='1d'` candle: `2026-06-24 00:00:00`.
  - Latest `manual_macro_daily` run: success, 16/16 symbols, latest candle `2026-06-24 00:00:00`.
- `./.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_tab_exposes_daily_refresh_and_cache_reload tests.test_service_contracts.FuturesMacroThermometerContractTests.test_overview_macro_snapshot_cache_key_tracks_latest_daily_marker`
  - RED: failed before helper/control implementation.
  - GREEN: passed after implementation.
- `./.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests tests.test_service_contracts.FuturesMacroThermometerContractTests`
  - Passed: 101 tests.
- `./.venv/bin/python -m py_compile app/services/futures_macro_thermometer.py app/web/overview_dashboard.py tests/test_service_contracts.py`
  - Passed.
- `git diff --check`
  - Passed.
- Browser QA: `http://localhost:8514/?overview_tab=futures-macro`
  - Confirmed visible `일봉 매크로 갱신`, `최신 데이터 다시 읽기`, and `기준일 2026-06-24`.
  - Screenshot artifact: `overview-futures-macro-refresh-state-v1-qa.png`.
