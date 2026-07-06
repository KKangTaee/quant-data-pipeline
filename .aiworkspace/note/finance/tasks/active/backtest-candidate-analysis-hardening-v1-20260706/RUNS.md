# Runs

## 2026-07-06

- `.venv/bin/python -m unittest tests.test_service_contracts.BacktestPresetCatalogContractTests -v`
  - Result: pass.
  - Note: edgar dependency deprecation warnings only.
- `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_policy_signal_tab_is_evidence_only_after_handoff_summary tests.test_service_contracts.BacktestRuntimeContractTests.test_backtest_policy_signal_react_board_component_is_ui_only tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests -v`
  - Result: pass.
  - Note: validates stale result hiding, Data Trust gate blocking, and existing Policy Signal React contract.
- `.venv/bin/python -m py_compile app/web/backtest_single_strategy.py app/services/backtest_handoff_readiness.py app/web/backtest_result_display.py tests/test_service_contracts.py`
  - Result: pass.
- `git diff --check`
  - Result: pass.
- `.venv/bin/python -m unittest tests.test_service_contracts -v`
  - Result: pass, 483 tests.
