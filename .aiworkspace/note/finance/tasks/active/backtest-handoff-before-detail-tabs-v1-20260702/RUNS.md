# Runs

## 2026-07-02

- RED: `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_latest_backtest_run_prioritizes_result_then_data_trust_then_handoff_then_tabs`
  - Failed because `_render_practical_validation_next_action(bundle)` still appeared after `tabs = st.tabs(tab_labels)`.
- GREEN: same focused command
  - Passed after moving `_render_practical_validation_next_action(bundle)` directly below `_render_data_trust_summary(meta)`.
- `.venv/bin/python -m py_compile app/web/backtest_result_display.py`
  - Passed.
- Focused post-change check:
  - `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_latest_backtest_run_prioritizes_result_then_data_trust_then_handoff_then_tabs tests.test_service_contracts.BacktestRuntimeContractTests.test_data_trust_summary_renderer_keeps_warnings_inside_compact_panel tests.test_service_contracts.BacktestRuntimeContractTests.test_backtest_result_header_owns_integrated_kpi_band` passed.
- Browser QA: `http://127.0.0.1:8513/backtest`
  - Ran `Run Equal Weight Backtest`.
  - Confirmed latest run order is result header -> Data Trust panel -> `2차 실전성 검증 Handoff` -> detailed result tabs.
  - Confirmed `.bt-handoff-card` renders before the first tab list.
  - Confirmed no browser console errors after the run button click.
  - Screenshots: `backtest-handoff-before-tabs-qa-view.png`, `backtest-handoff-before-tabs-order-qa.png` (generated artifacts, not staged).
- `.venv/bin/python -m unittest tests.test_backtest_refactor_boundaries`
  - Passed 11 tests, with existing third-party `edgar` deprecation warnings.
- `.venv/bin/python -m unittest tests.test_service_contracts`
  - Passed 449 tests, with existing third-party `edgar` deprecation warnings and Streamlit cache warnings.
- `git diff --check`
  - Passed.
