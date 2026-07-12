# Runs

| Command | Result |
|---|---|
| `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow3_excludes_final_review_reference_from_actionable_summary tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow4_keeps_final_review_items_as_handoff_reference` | RED: failed as expected because `visible_in_practical_validation` / `visible_criteria_detail_groups` did not exist and Flow 3 still treated `보강 항목 없음` as pass-like copy. |
| `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow3_excludes_final_review_reference_from_actionable_summary tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow4_keeps_final_review_items_as_handoff_reference tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_workspace_model_builds_criteria_detail_groups` | PASS. |
| `npm ci` in `app/web/components/practical_validation_fix_queue/frontend` | PASS. Installed local frontend dependencies for build; npm reported 1 moderate and 1 high vulnerability in dependency audit. |
| `npm run build` in `app/web/components/practical_validation_fix_queue/frontend` | PASS. Rebuilt Vite assets. |
| `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow3_excludes_final_review_reference_from_actionable_summary tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow4_keeps_final_review_items_as_handoff_reference tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_workspace_model_builds_criteria_detail_groups tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow3_uses_conclusion_summary` | PASS. |
| `.venv/bin/python -m py_compile app/services/backtest_practical_validation_workspace.py app/web/backtest_practical_validation/page.py app/web/backtest_practical_validation/workspace_panel.py` | PASS. |
| `git diff --check` | PASS. |
| Browser QA on `http://127.0.0.1:8560/backtest` | PASS for Practical Validation stage load, no `보강 항목 없음` text in visible snapshot, and no browser console errors. Screenshot saved to local generated artifact `pv-category-empty-state-v1-qa.png` and not staged. |
