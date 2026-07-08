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

## 2026-07-05 Entry Gate Ownership Correction

- RED contract update:
  - Adjusted Backtest result display / Handoff / Policy Signal tests so Backtest Analysis may only show first-stage source registration checks.
  - Expected failures confirmed before implementation: Data Trust still surfaced warning queues, Policy Signal still exposed second-stage counts, and Handoff still showed readiness-style second-stage queue copy.
- GREEN focused regression:
  - `.venv/bin/python -m unittest` for 13 Backtest Runtime contract tests passed.
  - Coverage focused on Handoff gate summary, Practical Validation source transfer, Policy Signal board props, Handoff React component props, Candidate Review draft, and Data Trust compact rendering.
- Python compile:
  - `.venv/bin/python -m py_compile app/web/backtest_result_display.py app/services/backtest_handoff_readiness.py app/web/components/backtest_handoff_action/component.py app/web/components/backtest_policy_signal_board/component.py app/web/backtest_practical_validation/page.py app/services/backtest_practical_validation_source.py`
  - Passed.
- React component build:
  - `npm run build` in `app/web/components/backtest_handoff_action/frontend`: passed.
  - `npm run build` in `app/web/components/backtest_policy_signal_board/frontend`: passed.
- Static checks:
  - `git diff --check`: passed.
  - Stale UI phrase search confirmed removed phrases only remain as negative assertions in tests; unrelated `strict_factor` score copy is not part of Backtest Analysis gate UI.
- Browser QA:
  - Checked current Streamlit Backtest screen at `http://localhost:8502/backtest`.
  - Confirmed entry gate card no longer shows readiness score / `2차 확인 큐` as a first-stage metric.
  - Re-ran Equal Weight / Dividend ETFs after reloading the latest Streamlit bundle.
  - Confirmed Policy Signals now says it only shows source registration criteria that can be decided in Backtest Analysis.
  - Screenshot: `backtest-entry-gate-ownership-correction-policy-latest-qa.png` (generated artifact, not staged).
