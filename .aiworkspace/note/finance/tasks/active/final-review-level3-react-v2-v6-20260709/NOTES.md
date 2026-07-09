# Notes

## Constraints

- Existing generated QA screenshots and local run history are untracked and must not be staged.
- Keep Final Review storage append-only. Do not rewrite existing v2/v3 rows.
- Keep Portfolio Monitoring handoff narrower than Final Review judgment record save.

## Implementation Notes

- Prefer adding service read model functions to `app/services/backtest_evidence_read_model.py`.
- Prefer a dedicated React component under `app/web/components/final_review_investment_report/`.
- Keep existing Streamlit fallback because custom component build/runtime can fail locally.

## V2 Notes

- The investment report does not change selected-route gate logic. It reads the existing investability packet and Decision Cockpit state.
- React renders only the report payload. It has no `Streamlit.setComponentValue`, no fetch, and no storage write.
- Score band is still provisional. If selection gate is ready but packet ready-check score is below 6, V2 labels it `선정 가능 / 보강 추적` rather than `취약` to avoid contradicting the gate.

## V3 Notes

- Level2 REVIEW handling is classification only. Final Review does not re-run Practical Validation or solve the underlying issue.
- `final_readiness_blocker` and non-review blocking statuses map to `blocker`.
- `pv_data_caution` and `pv_practical_caution` map to `warning`.
- `final_decision_input` maps to `open_review`.
- `monitoring_followup` maps to `monitoring_followup`.

## V4 Notes

- The scorecard is a Final Review taxonomy, not a new validation engine.
- `select_ready` from the existing selection gate keeps the Monitoring candidate route unless blockers are present.
- Packet score and Level2 REVIEW burden adjust the visible score and watch label.
- The scorecard writes nothing and does not create live approval, order, or auto rebalance.

## V5 Notes

- Final Review judgment persistence and Portfolio Monitoring handoff remain separate.
- The report shows recommended-route boundary, while Final Decision Action shows the currently selected route boundary.
- Non-select routes are `judgment_decision` records and do not become Monitoring candidates.
- Selected route only becomes `monitoring_candidate` when the selected-route gate is ready.

## V6 Notes

- Weakness improvement is read-only proposal / verification guidance.
- It does not generate a new strategy, run a new backtest, save a new portfolio, or mutate registries.
- If no selected-route blocker exists, the proposal becomes monitoring / open-review tracking rather than fake optimization.
