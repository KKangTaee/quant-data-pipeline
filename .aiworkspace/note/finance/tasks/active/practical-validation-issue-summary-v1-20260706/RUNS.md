# Runs

Commands and QA evidence for this task.

## 2026-07-06

- RED contract check:
  - `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_fix_queue_react_component_is_ui_only tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_workspace_model_builds_criteria_detail_groups tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_workspace_model_builds_issue_queue_items tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow4_uses_criteria_detail_board`
  - Expected failures confirmed before implementation because the workspace model and component still exposed guide-style fields.
- GREEN focused contract check:
  - `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_fix_queue_react_component_is_ui_only tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_workspace_model_builds_criteria_detail_groups tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_workspace_model_builds_issue_queue_items tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow4_uses_criteria_detail_board`
  - Result: 4 tests passed.
- Copy regression check:
  - `rg -n "무엇을 검증했나|무엇을 확인했나|부족한 점|해야 할 일" app/web/components/practical_validation_fix_queue/frontend/src app/web/backtest_practical_validation/page.py app/web/backtest_practical_validation/workspace_panel.py app/services/backtest_practical_validation_workspace.py || true`
  - Result: no matches.
- Python compile:
  - `.venv/bin/python -m py_compile app/services/backtest_practical_validation_workspace.py app/web/backtest_practical_validation/page.py app/web/backtest_practical_validation/workspace_panel.py app/web/backtest_practical_validation/components.py app/web/components/practical_validation_fix_queue/component.py`
  - Result: passed.
- React build:
  - `npm install && npm run build` in `app/web/components/practical_validation_fix_queue/frontend`
  - Result: passed. npm audit still reports existing dependency vulnerabilities; not fixed in this UI scope.
- Boundary regression:
  - `.venv/bin/python -m unittest tests.test_backtest_refactor_boundaries.BacktestRefactorBoundaryTests`
  - Result: 17 tests passed. Existing Streamlit / dependency warnings were observed.
- Browser QA:
  - Streamlit: `.venv/bin/python -m streamlit run app/web/streamlit_app.py --server.port 8532 --server.headless true --server.runOnSave false --server.fileWatcherType none`
  - In-app Browser opened `http://localhost:8532/backtest`, selected `실전 검증 · Practical Validation`.
  - Flow 3 component frame contained `Final Review 이동을 막는 이슈`, `현재 문제`, `완료 기준`, `보강 위치` and did not contain `무엇을 검증했나`, `부족한 점`, `해야 할 일`, or `NEEDS_INPUT row`.
  - QA screenshot: `/Users/taeho/Project/quant-data-pipeline-worktrees/backtest-dev/backtest-practical-validation-issue-summary-v1-qa.png` (generated artifact, not for commit).
- Diff hygiene:
  - `git diff --check`
  - Result: passed.
