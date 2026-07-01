# Runs

## 2026-07-01

- RED: `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_latest_backtest_run_prioritizes_result_then_data_trust_then_handoff`
  - Failed because `_render_last_run` still rendered `Latest Backtest Run`, Data Trust before metrics, and Practical Validation handoff before detail tabs.
- GREEN: same focused command
  - Passed after adding `_render_backtest_result_header` and reordering the latest run render flow.
- `.venv/bin/python -m py_compile app/web/backtest_result_display.py`
  - Passed.
- `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_data_trust_brief_model_compacts_basis_and_warning_queue tests.test_service_contracts.BacktestRuntimeContractTests.test_data_trust_summary_renderer_keeps_warnings_inside_compact_panel tests.test_service_contracts.BacktestRuntimeContractTests.test_latest_backtest_run_prioritizes_result_then_data_trust_then_handoff`
  - Passed, with existing third-party `edgar` deprecation warnings.
- `.venv/bin/python -m unittest tests.test_backtest_refactor_boundaries`
  - Passed, with existing third-party `edgar` deprecation warnings.
- `.venv/bin/python -m unittest tests.test_service_contracts`
  - Passed 448 tests, with existing third-party `edgar` deprecation warnings and Streamlit cache warnings.
- `git diff --check`
  - Passed.
- Browser QA: `http://127.0.0.1:8510/backtest`
  - Ran `Run Equal Weight Backtest`.
  - Confirmed the displayed order is strategy result header, core metrics, Data Trust summary, detail tabs, then Practical Validation handoff.
  - Confirmed `Latest Backtest Run` is absent.
  - Confirmed old Data Trust guide labels (`세부 데이터 기준`, `어디까지 계산했나`, `데이터는 충분한가`, `무엇을 먼저 볼까`) are absent.
  - Confirmed no new browser console errors after clicking the run button.
  - Screenshot: `backtest-result-flow-reorder-qa.png` (generated artifact, not staged).
- Final pre-commit check:
  - `.venv/bin/python -m py_compile app/web/backtest_result_display.py` passed.
  - Focused 3-test service contract command passed, with existing third-party `edgar` deprecation warnings.
  - `git diff --check` passed.
- Final staged verification:
  - `.venv/bin/python -m unittest tests.test_backtest_refactor_boundaries` passed 11 tests, with existing third-party `edgar` deprecation warnings.
  - `.venv/bin/python -m unittest tests.test_service_contracts` passed 448 tests, with existing third-party `edgar` deprecation warnings and Streamlit cache warnings.
