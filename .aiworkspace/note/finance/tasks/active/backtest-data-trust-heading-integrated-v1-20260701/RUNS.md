# Runs

## 2026-07-01

- RED: `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_data_trust_summary_renderer_keeps_warnings_inside_compact_panel`
  - Failed because the custom panel did not own `data-trust-brief__section-title` / `data-trust-brief__section-kicker`, and the standalone heading still existed.
- GREEN: same focused command
  - Passed after moving `데이터 기준 요약` into the Data Trust panel and removing the standalone Streamlit heading.
- `.venv/bin/python -m py_compile app/web/backtest_result_display.py`
  - Passed.
- Focused post-change check:
  - `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_data_trust_summary_renderer_keeps_warnings_inside_compact_panel tests.test_service_contracts.BacktestRuntimeContractTests.test_latest_backtest_run_prioritizes_result_then_data_trust_then_handoff tests.test_service_contracts.BacktestRuntimeContractTests.test_backtest_result_header_owns_integrated_kpi_band` passed.
- Browser QA: `http://127.0.0.1:8512/backtest`
  - Ran `Run Equal Weight Backtest`.
  - Confirmed `standaloneDataTrustHeadingCount` is `0`.
  - Confirmed `.data-trust-brief__section-title` is `데이터 기준 요약`.
  - Confirmed `.data-trust-brief__section-kicker` is `먼저 볼 결론`.
  - Confirmed result header -> Data Trust panel -> detail tabs order.
  - Confirmed no new browser console errors after the run button click.
  - Screenshot: `backtest-data-trust-heading-integrated-qa.png` (generated artifact, not staged).
- `.venv/bin/python -m unittest tests.test_backtest_refactor_boundaries`
  - Passed 11 tests, with existing third-party `edgar` deprecation warnings.
- `.venv/bin/python -m unittest tests.test_service_contracts`
  - Passed 449 tests, with existing third-party `edgar` deprecation warnings and Streamlit cache warnings.
- `git diff --check`
  - Passed.
