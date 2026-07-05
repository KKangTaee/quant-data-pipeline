# Runs

## 2026-07-05

- RED focused unittest:
  - `test_practical_validation_handoff_gate_allows_hold_candidates_as_conditional_review`
  - `test_data_trust_brief_model_compacts_basis_and_warning_queue`
  - `test_data_trust_summary_renderer_keeps_warnings_inside_compact_panel`
  - Expected failures confirmed: Handoff still showed 2차 상세 reason and Data Trust still expanded warnings as issue cards.
- GREEN focused unittest:
  - Same 3 tests passed after display model cleanup.
- Focused Backtest contract regression:
  - 14 Handoff / Policy Signal / Data Trust / Practical Validation entry queue tests passed.
- `.venv/bin/python -m py_compile app/web/backtest_result_display.py app/web/backtest_practical_validation/page.py app/services/backtest_handoff_readiness.py`: passed.
- `git diff --check`: passed.
- Browser QA:
  - Started current worktree Streamlit server on `http://localhost:8502/backtest`.
  - Ran Equal Weight / Dividend ETFs.
  - Confirmed Data Trust shows `2차 확인 항목` count / destination only, without old `이번 실행 검토 큐` detailed warning list.
  - Confirmed Handoff card remains visible and summarizes 1차 entry gate plus 2차 queue.
  - Screenshot: `backtest-second-stage-visibility-v1-qa.png` (generated artifact, not staged).
