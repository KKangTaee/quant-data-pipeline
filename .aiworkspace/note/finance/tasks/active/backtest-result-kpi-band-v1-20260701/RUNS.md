# Runs

## 2026-07-01

- RED: `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_latest_backtest_run_prioritizes_result_then_data_trust_then_handoff tests.test_service_contracts.BacktestRuntimeContractTests.test_backtest_result_header_owns_integrated_kpi_band`
  - Failed because `_render_last_run` still called `_render_backtest_result_header(bundle)` followed by `_render_summary_metrics(summary_df)`, and the result header did not own a KPI band.
- GREEN: same focused command
  - Passed after changing `_render_backtest_result_header` to accept `summary_df`, render the KPI band, and remove the separate metric row from latest run.
- `.venv/bin/python -m py_compile app/web/backtest_result_display.py`
  - Passed.
- Focused post-spacing check:
  - `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_latest_backtest_run_prioritizes_result_then_data_trust_then_handoff tests.test_service_contracts.BacktestRuntimeContractTests.test_backtest_result_header_owns_integrated_kpi_band` passed.
- Browser QA: `http://127.0.0.1:8511/backtest`
  - Ran `Run Equal Weight Backtest`.
  - Confirmed the result header owns 4 KPI cells and 6 basis items.
  - Confirmed the old `backtest-result-hero__chips` class is absent.
  - Confirmed basis label spacing such as `기간 2016-01-01` and `계산 기준 2026-06-26`.
  - Confirmed the display order is result header / KPI band, `데이터 기준 요약`, detail tabs, then `2차 실전성 검증 Handoff`.
  - Confirmed no new browser console errors after the run button click.
  - Screenshot: `backtest-result-kpi-band-qa.png` (generated artifact, not staged).
- `.venv/bin/python -m unittest tests.test_backtest_refactor_boundaries`
  - Passed 11 tests, with existing third-party `edgar` deprecation warnings.
- `.venv/bin/python -m unittest tests.test_service_contracts`
  - Passed 449 tests, with existing third-party `edgar` deprecation warnings and Streamlit cache warnings.
- `git diff --check`
  - Passed.
