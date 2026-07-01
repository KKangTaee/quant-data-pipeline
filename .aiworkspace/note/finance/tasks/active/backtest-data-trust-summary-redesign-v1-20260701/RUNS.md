# Runs

## 2026-07-01

- RED: `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_data_trust_brief_model_uses_user_first_questions tests.test_service_contracts.BacktestRuntimeContractTests.test_data_trust_summary_renderer_does_not_use_old_metric_cards`
  - Failed because `_build_data_trust_brief` did not exist and the renderer still used old metric cards.
- GREEN: same focused test command
  - Passed after adding the brief model and custom panel.
- `.venv/bin/python -m py_compile app/web/backtest_result_display.py`
  - Passed.
- `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_data_trust_brief_model_uses_user_first_questions tests.test_service_contracts.BacktestRuntimeContractTests.test_data_trust_summary_renderer_does_not_use_old_metric_cards tests.test_service_contracts.BoundaryContractHardeningTests.test_backtest_latest_run_view_prioritizes_result_over_pre_result_guides`
  - Passed, with existing third-party `edgar` deprecation warnings.
- `.venv/bin/python -m unittest tests.test_backtest_refactor_boundaries`
  - Passed, with existing third-party `edgar` deprecation warnings.
- `.venv/bin/python -m unittest tests.test_service_contracts`
  - Passed: 447 tests, with existing Streamlit cache and third-party `edgar` warnings.
- `git diff --check`
  - Passed.
- Browser QA: `.venv/bin/python -m streamlit run app/web/streamlit_app.py --server.port 8510 --server.address 127.0.0.1 --server.headless true --server.runOnSave false --server.fileWatcherType none --browser.gatherUsageStats false`
  - Opened `http://127.0.0.1:8510/backtest`, ran `Run Equal Weight Backtest`.
  - Confirmed `데이터 기준 요약`, `먼저 볼 결론`, `어디까지 계산했나`, `데이터는 충분한가`, `무엇을 먼저 볼까`, and `세부 데이터 기준` render.
  - Confirmed old `Result Integrity`, `Price Freshness`, and `Requested End` surfaces do not render in the Data Trust area.
  - Fresh browser console errors after current run: 0. Older health-check logs were stale from a previous stopped Streamlit server.
  - Screenshot artifact: `backtest-data-trust-summary-redesign-qa.png` (generated, not staged).
