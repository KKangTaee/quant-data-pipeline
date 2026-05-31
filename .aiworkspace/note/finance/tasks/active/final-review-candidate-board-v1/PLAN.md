# Final Review Candidate Board V1 Plan

Status: Complete
Started: 2026-05-31

## 이걸 하는 이유?

Final Review의 Decision Cockpit과 Evidence Appendix는 정리됐지만, Candidate Board는 아직 Gate 통과 후보를 표로 보여주는 수준에 가깝다.

사용자가 Final Review에 들어왔을 때 필요한 것은 단순 목록이 아니라, 어떤 후보를 먼저 볼지, 왜 그 후보가 선정 가능 / 보류 / 차단 상태인지, 다음에 무엇을 확인해야 하는지를 빠르게 파악하는 보드다.

## Goal

- Candidate Board를 최종 선별용 비교 / 우선순위 보드로 고도화한다.
- 기존 Practical Validation result, investability packet, Decision Cockpit read model만 사용한다.
- 후보별 selected-route state, suggested decision, priority, primary reason, next action을 노출한다.
- 새 validation 실행, provider fetch, registry write, DB schema, live approval / order 동작은 추가하지 않는다.

## Scope

- `app/services/backtest_evidence_read_model.py`
  - Candidate Board row ranking / summary read model
- `app/web/backtest_final_review.py`
  - Candidate Board summary cards, review queue, enriched table render
- `tests/test_service_contracts.py`
  - Candidate Board priority / sorting contract
- durable flow / roadmap / task docs

## Stop Condition

- Candidate Board shows the first review candidate and board counts before source selection.
- Board rows are sorted by decision usefulness: select-ready first, then hold / re-review, then blocked, with score and evidence gaps as tie-breakers.
- Existing service contract tests pass.
- Browser QA confirms the Final Review Candidate Board renders without writing workflow registries.
