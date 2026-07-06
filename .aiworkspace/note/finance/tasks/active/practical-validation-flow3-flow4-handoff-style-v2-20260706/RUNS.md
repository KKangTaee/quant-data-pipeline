# Runs

Commands and QA evidence for this task.

## 2026-07-06

- RED: focused service contract tests failed before implementation for missing Flow 3 criteria copy, Flow 4 criteria board, and workspace summary counts.
- GREEN: `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_fix_queue_react_component_is_ui_only tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_workspace_model_builds_criteria_detail_groups tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow4_uses_criteria_detail_board`
- GREEN: `.venv/bin/python -m unittest tests.test_backtest_refactor_boundaries.BacktestRefactorBoundaryTests.test_practical_validation_fix_queue_react_surface_is_square`
- GREEN: `npm run build` in `app/web/components/practical_validation_fix_queue/frontend`
- GREEN: `.venv/bin/python -m py_compile app/services/backtest_practical_validation_workspace.py app/web/backtest_practical_validation/page.py app/web/backtest_practical_validation/workspace_panel.py app/web/components/practical_validation_fix_queue/component.py`
- GREEN: `.venv/bin/python -m unittest tests.test_backtest_refactor_boundaries.BacktestRefactorBoundaryTests`
- Browser QA: `http://localhost:8530/backtest` Practical Validation tab showed Flow 3 `다음 단계`, `Flow 5에서 저장 / 이동`, `Final Review 이동 기준`, Flow 4 `검증 기준 상세`, `Final Review 이동 기준 상세`, and no `Reference help` / `시장 심리` default entry markers.
- Browser QA screenshot: `backtest-practical-validation-flow3-flow4-handoff-style-v2-qa.png`.
- GREEN final: `.venv/bin/python -m unittest tests.test_backtest_refactor_boundaries.BacktestRefactorBoundaryTests`
- GREEN final: `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_workspace_model_builds_criteria_detail_groups tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow4_uses_criteria_detail_board`
- GREEN final: `git diff --check`
