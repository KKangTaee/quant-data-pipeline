# Runs

Commands and QA evidence will be appended per task.

## 2026-07-07 1차 Strategy Detail Panel Removal

- RED: `.venv/bin/python -m unittest tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_single_strategy_workspace_does_not_render_strategy_detail_panel -v` failed because `app/web/backtest_single_strategy.py` still imported and rendered the panel.
- GREEN: focused tests passed for `test_single_strategy_workspace_does_not_render_strategy_detail_panel` and `test_price_freshness_preflight_react_component_is_ui_only`.
- Compile: `.venv/bin/python -m py_compile app/web/backtest_single_strategy.py app/web/backtest_single_forms/__init__.py app/web/backtest_common.py` completed successfully.
- Reference scan: active app/docs references to `backtest_strategy_detail` / `Strategy Detail` are removed except the negative assertion in the test.

## 2026-07-07 2차 Strict Preset Helper Cleanup

- RED: strict preset helper tests failed with missing `display_items`, `preset_tone`, and `preset_role` fields.
- GREEN: focused strict preset helper tests passed after adding compact display fields.
- Compile: `.venv/bin/python -m py_compile app/web/backtest_common.py` completed successfully.
- Diff check: `git diff --check` completed successfully.
