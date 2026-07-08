# Runs

## 2026-07-08

- RED:
  - `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow4_keeps_final_review_items_as_handoff_reference tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_fix_queue_react_component_is_ui_only tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow3_excludes_final_review_reference_from_actionable_summary tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow4_uses_criteria_detail_board`
  - Failed on Final Review handoff wording, Flow 3 review count, and Flow 4 Final Review blocks.
- RED:
  - `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow4_uses_criteria_detail_board`
  - Failed on `_render_validation_gate_section(validation_result)` still being called from Flow 4.
- RED:
  - `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_fix_queue_react_component_is_ui_only tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow3_uses_conclusion_summary`
  - Failed on Flow 3 still using Final Review move copy and gate verdict.
- GREEN:
  - `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_fix_queue_react_component_is_ui_only tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow3_uses_conclusion_summary tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow3_excludes_final_review_reference_from_actionable_summary tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow4_uses_criteria_detail_board`
- Related:
  - `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_workspace_model_builds_criteria_detail_groups tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow4_keeps_final_review_items_as_handoff_reference tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_fix_queue_react_component_is_ui_only tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow3_excludes_final_review_reference_from_actionable_summary tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow3_uses_conclusion_summary tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow4_uses_criteria_detail_board tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_module_plan_preserves_review_input_checks tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_workspace_distinguishes_blocked_from_repairable_gap`
- Compile:
  - `.venv/bin/python -m py_compile app/services/backtest_practical_validation_workspace.py app/web/backtest_practical_validation/page.py app/web/backtest_practical_validation/workspace_panel.py app/web/components/practical_validation_fix_queue/component.py`
- Build:
  - `npm ci && npm run build && rm -rf node_modules` in `app/web/components/practical_validation_fix_queue/frontend`
- Browser QA:
  - Streamlit on `http://localhost:8541/backtest`
  - Confirmed Flow 3 / Flow 4 section has no `Final Review 참고`, `Final Review 이동 요약`, `Final Review 이동 보류`, `Final Review 이동 가능`, `검증 모듈 / 기술 상세`, `확인 필요`, or `보류 항목`.
