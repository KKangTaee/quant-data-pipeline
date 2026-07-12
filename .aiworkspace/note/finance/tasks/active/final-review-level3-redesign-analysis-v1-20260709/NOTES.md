# Notes

## Current Structure

- Main UI body is `app/web/backtest_final_review/page.py`.
- `candidate_board.py`, `decision_cockpit.py`, and `handoff_panel.py` currently re-export functions from `page.py`, so physical module split is not yet real.
- Final Review service/read model is mostly `app/services/backtest_evidence_read_model.py`.
- Selected-route preflight bridge is `app/services/backtest_final_review_policy.py` and `app/services/backtest_selected_route_preflight.py`.
- Final Review persistence appends to `.aiworkspace/note/finance/registries/FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl` through `app/runtime/backtest/stores/portfolio_selection.py`.
- Portfolio Monitoring reads selected final decisions through `app/runtime/backtest/read_models/final_selected_portfolios.py` and user setup remains in `SELECTED_DASHBOARD_PORTFOLIOS.jsonl`.

## Initial Diagnosis

- Level3 already separates `selection_gate_policy_snapshot` from stricter `deployment_readiness_policy_snapshot`.
- `REVIEW` is not a single blocker; Practical Validation role taxonomy distinguishes `데이터 주의`, `2단계 실용성 주의`, `최종 판단 참고`, `Monitoring 추적`, `저장 전 보강`.
- Current Final Review consumes evidence mostly as policy rows, packet score, blockers, review-required rows, watch rows, and saved decision ledger.
- Missing product layer: a human-readable final review thesis with strengths, weaknesses, environment fit, expected range / risks, benchmark or alternative comparison, recommendation rationale, and monitoring conditions.

## Implemented Boundary Change

- `FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl` now represents Final Review judgment records, not only selected Monitoring candidates.
- `SELECT_FOR_PRACTICAL_PORTFOLIO` remains the only route that can create a Monitoring handoff, and it still requires the selected-route gate.
- `HOLD_FOR_MORE_PAPER_TRACKING`, `REJECT_FOR_PRACTICAL_USE`, and `RE_REVIEW_REQUIRED` can be saved with operator reason as durable Final Review judgments.
- v3 decision rows add `final_review_record_type`, `monitoring_candidate`, and `monitoring_handoff_state`. Existing rows are not rewritten.
- Portfolio Monitoring read model treats explicit `monitoring_candidate` as authoritative when present; legacy v2 rows remain backward-compatible.
