# Runs

Commands and QA evidence for this task.

## 2026-07-06

- RED: focused `tests.test_service_contracts.BacktestRuntimeContractTests` cases failed before implementation because Flow 3 / Flow 4 did not expose user-language blocker fields.
- GREEN: `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_fix_queue_react_component_is_ui_only tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_workspace_model_builds_criteria_detail_groups tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_workspace_model_explains_fix_items_in_user_language tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow4_uses_criteria_detail_board`
- GREEN: `.venv/bin/python -m unittest tests.test_backtest_refactor_boundaries.BacktestRefactorBoundaryTests`
- GREEN: `.venv/bin/python -m py_compile app/services/backtest_practical_validation_workspace.py app/services/backtest_practical_validation_modules.py app/services/reference_guides_catalog.py app/web/backtest_practical_validation/page.py app/web/backtest_practical_validation/workspace_panel.py app/web/components/practical_validation_fix_queue/component.py`
- GREEN: `npm run build` in `app/web/components/practical_validation_fix_queue/frontend` after reinstalling frontend dependencies locally.
- GREEN: `git diff --check`
- Browser QA: Streamlit `http://localhost:8531/backtest`, Practical Validation tab. Confirmed `무엇을 검증했나`, `부족한 점`, `해야 할 일`, `기술 기준`, `Final Review로 넘기기 전 확인 기준`, and `새 검증 단계가 아니라` are visible; confirmed `NEEDS_INPUT row`, `Reference help`, and Practical Validation default `시장 심리` overlay are not visible.
- QA screenshot: `/Users/taeho/Project/quant-data-pipeline-worktrees/backtest-dev/backtest-practical-validation-readable-fix-queue-v1-qa.png` (generated artifact, not committed).
