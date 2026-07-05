# Runs

## 2026-07-05

- `npm install` in `app/web/components/backtest_policy_signal_board/frontend`: completed; npm reported existing dependency audit warnings in the shared Vite/React set.
- `npm run build` in `app/web/components/backtest_policy_signal_board/frontend`: passed.
- Browser QA on `http://localhost:8502/backtest`: Equal Weight 실행 후 Policy Signals 탭 확인. Handoff iframe `2차 확인 6 · 먼저 해결 0`, Policy Signals React board `먼저 해결 0 / 1차 통과 6 / 2차 전달 6`으로 표시됨.
- QA screenshot: `backtest-policy-signal-stage-split-final-qa.png` (generated artifact, not staged).
- First focused unittest run failed because `검증 기준 상세` moved from Python HTML source to React component source; test ownership assertion updated.
- `.venv/bin/python -m py_compile app/services/backtest_handoff_readiness.py app/web/backtest_result_display.py app/web/backtest_practical_validation/page.py app/web/backtest_candidate_review_helpers.py app/web/components/backtest_policy_signal_board/component.py`: passed.
- `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_handoff_gate_allows_hold_candidates_as_conditional_review tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_handoff_gate_still_blocks_missing_source_basis tests.test_service_contracts.BacktestRuntimeContractTests.test_policy_signal_inventory_splits_first_stage_and_second_stage_rows tests.test_service_contracts.BacktestRuntimeContractTests.test_backtest_policy_signal_react_board_component_is_ui_only tests.test_service_contracts.BacktestRuntimeContractTests.test_policy_signal_tab_is_evidence_only_after_handoff_summary tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_step1_receives_backtest_review_focus_queue tests.test_service_contracts.BacktestRuntimeContractTests.test_candidate_review_draft_marks_hold_as_practical_validation_review_focus`: passed with existing `edgar` deprecation warnings and Streamlit bare-mode warnings.
- `git diff --check`: passed.
