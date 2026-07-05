# Runs

## 2026-07-05

- `python -m unittest ...BacktestRuntimeContractTests.test_policy_signal_inventory_includes_plain_help_for_first_stage_rows ...`
  - RED: `checked_items`, React grouping / help UI, 2차 큐 제거 계약이 아직 없어 실패함.
- `npm install`
  - component-local `node_modules`가 없어 Vite 설치. Audit warning 2개는 lockfile 보안 업데이트 범위를 벗어나 조치하지 않음.
- `npm run build`
  - PASS. `backtest_policy_signal_board` production bundle regenerated.
- `.venv/bin/python -m py_compile app/services/backtest_handoff_readiness.py app/web/backtest_result_display.py app/web/backtest_candidate_review_helpers.py app/web/components/backtest_policy_signal_board/component.py`
  - PASS.
- `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_policy_signal_inventory_splits_first_stage_and_second_stage_rows tests.test_service_contracts.BacktestRuntimeContractTests.test_policy_signal_inventory_includes_plain_help_for_first_stage_rows tests.test_service_contracts.BacktestRuntimeContractTests.test_backtest_policy_signal_react_board_component_is_ui_only tests.test_service_contracts.BacktestRuntimeContractTests.test_policy_signal_tab_is_evidence_only_after_handoff_summary tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_step1_receives_backtest_review_focus_queue tests.test_service_contracts.BacktestRuntimeContractTests.test_candidate_review_draft_captures_handoff_readiness_snapshot`
  - PASS.
- `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_policy_signal_inventory_splits_first_stage_and_second_stage_rows tests.test_service_contracts.BacktestRuntimeContractTests.test_policy_signal_inventory_includes_plain_help_for_first_stage_rows tests.test_service_contracts.BacktestRuntimeContractTests.test_backtest_policy_signal_react_board_component_is_ui_only tests.test_service_contracts.BacktestRuntimeContractTests.test_policy_signal_tab_is_evidence_only_after_handoff_summary tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_step1_receives_backtest_review_focus_queue tests.test_service_contracts.BacktestRuntimeContractTests.test_backtest_handoff_react_adoption_decision_is_documented tests.test_service_contracts.BacktestRuntimeContractTests.test_candidate_review_draft_captures_handoff_readiness_snapshot`
  - PASS.
- `git diff --check`
  - PASS.
- `.venv/bin/streamlit run app/web/streamlit_app.py --server.port 8502 --server.headless true`
  - Browser QA PASS. Equal Weight 실행 후 `검증 신호 · Policy Signals` 탭에서 category board / `?` help / 2차 count notice를 확인했다.
  - Screenshot: `backtest-policy-signal-help-board-v1-qa.png`.
  - Existing Streamlit deprecation warning: `use_container_width` -> `width`; 이번 변경 범위 밖.
