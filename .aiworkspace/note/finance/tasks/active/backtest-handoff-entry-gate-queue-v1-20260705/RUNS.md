# Runs

## 2026-07-05

- RED focused unittest: Handoff state / React wrapper가 아직 `진입 준비도`, `score`, `criteria`를 사용해 5개 테스트가 실패하는 것을 확인했다.
- GREEN focused unittest: Handoff state / React wrapper 수정 후 다음 테스트가 통과했다.
  - `test_practical_validation_handoff_gate_allows_hold_candidates_as_conditional_review`
  - `test_practical_validation_handoff_gate_still_blocks_missing_source_basis`
  - `test_practical_validation_handoff_gate_allows_ready_candidates`
  - `test_practical_validation_handoff_uses_single_integrated_action_surface`
  - `test_backtest_handoff_react_component_is_production_action_card`
- `npm run build` in `app/web/components/backtest_handoff_action/frontend`: passed.
- `.venv/bin/python -m py_compile app/web/backtest_result_display.py app/web/components/backtest_handoff_action/component.py app/services/backtest_handoff_readiness.py`: passed.
- focused unittest 8개: passed with existing `edgar` deprecation warnings and Streamlit bare-mode warnings.
- `git diff --check`: passed.
- Browser QA on `http://localhost:8502/backtest`: Equal Weight 실행 후 Handoff card가 `1차 진입 기준`, `먼저 해결`, `2차 확인 큐`를 표시하고 `진입 준비도`가 없는 것을 확인했다.
- QA screenshot: `backtest-handoff-entry-gate-queue-v1-qa.png` (generated artifact, not staged).
