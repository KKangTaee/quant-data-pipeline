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
