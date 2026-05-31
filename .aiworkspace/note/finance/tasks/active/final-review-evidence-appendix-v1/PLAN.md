# Final Review Evidence Appendix V1 Plan

Status: Complete
Started: 2026-05-31

## 이걸 하는 이유?

사용자가 지적한 핵심 문제는 Decision Cockpit의 선정 / 차단 / 보류 판정 자체가 아니라, 화면 아래에서 Practical Validation 근거 표가 다시 길게 노출되면서 Final Review가 이전 단계를 재검증하는 화면처럼 보인다는 점이다.

Final Review는 새 검증을 실행하는 곳이 아니라, Practical Validation Gate를 통과한 후보를 최종 select / hold / reject / re-review로 기록하는 마지막 decision surface여야 한다.

## Goal

- Candidate Board와 Decision Cockpit은 유지한다.
- 최종 판단 기록을 Decision Cockpit 바로 다음 주 action으로 올린다.
- 상세 Practical Validation / Robustness / Paper Observation / Investability Evidence Packet 표는 Evidence Appendix로 낮춘다.
- 검증 로직, gate policy, registry write contract, DB / provider fetch boundary는 변경하지 않는다.

## Scope

- `app/web/backtest_final_review.py` UI ordering / labels
- Backtest / Portfolio Selection flow docs
- Roadmap / index / root handoff logs
- Task status / run notes

## Stop Condition

- Final Review visible order is Candidate Board -> Decision Cockpit -> Final Decision Record -> Evidence Appendix -> Saved Decisions.
- Evidence Appendix clearly says it reuses stored Practical Validation evidence and does not rerun validation.
- Existing service contract tests still pass.
- Browser QA confirms the reordered sections render in the Streamlit app.
