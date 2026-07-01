# Runs

## 2026-07-01

- RED: `.venv/bin/python -m unittest tests.test_service_contracts.BoundaryContractHardeningTests.test_backtest_latest_run_view_prioritizes_result_over_pre_result_guides`
  - Failed on existing `Execution Summary` / guide source.
- GREEN: `.venv/bin/python -m unittest tests.test_service_contracts.BoundaryContractHardeningTests.test_backtest_latest_run_view_prioritizes_result_over_pre_result_guides`
  - Passed after cleanup.
- `.venv/bin/python -m py_compile app/web/backtest_single_runner.py app/web/backtest_result_display.py`
  - Passed.
- `.venv/bin/python -m unittest tests.test_service_contracts.BoundaryContractHardeningTests.test_backtest_latest_run_view_prioritizes_result_over_pre_result_guides tests.test_service_contracts.BoundaryContractHardeningTests.test_backtest_page_removes_unused_guide_snapshot_and_reference_panels`
  - Passed.
- `.venv/bin/python -m unittest tests.test_backtest_refactor_boundaries`
  - Passed, with existing third-party `edgar` deprecation warnings.
- `.venv/bin/python -m unittest tests.test_service_contracts`
  - Passed: 445 tests, with existing Streamlit cache and third-party `edgar` warnings.
- `git diff --check`
  - Passed.
- Browser QA: `.venv/bin/python -m streamlit run app/web/streamlit_app.py --server.port 8510 --server.address 127.0.0.1 --server.headless true --server.runOnSave false --server.fileWatcherType none --browser.gatherUsageStats false`
  - Opened `http://127.0.0.1:8510/backtest`, ran `Run Equal Weight Backtest`.
  - Confirmed `Latest Backtest Run`, `Data Trust Summary`, and `Policy Signal Meta` render.
  - Confirmed `Execution Summary`, `Developer Payload`, `Performance Shape`, and `Action after metrics` do not render.
  - Browser console errors: 0.
  - Screenshot artifacts: `backtest-latest-run-cleanup-qa.png`, `backtest-latest-run-cleanup-result-qa.png` (generated, not staged).
