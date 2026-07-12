# Final Review Decision Flow Simplification V1

## 이걸 하는 이유?

Final Review의 실제 완료 행동인 판단 기록이 긴 투자 검토서 뒤에 늦게 나오고, 그 뒤로 Evidence Appendix와 Saved Decisions가 다시 이어져 사용자가 어디서 판단을 끝내야 하는지 불명확하다. Level1 / Level2와 같은 gate 기반 action 흐름으로 최종 판단을 총평 가까이에 통합하고, 중복 근거와 과거 ledger는 main flow에서 제거한다.

## 단계

1. 총평과 핵심 해석 직후에 route / 판단 사유 / 저장 CTA를 배치한다.
2. Evidence Appendix visible UI를 제거하고 audit trace는 투자 검토서에 유지한다.
3. Saved Decisions ledger를 제거하고 저장 성공 / Portfolio Monitoring 안내만 유지한다.
4. route별 활성화, 저장, responsive layout, 문서 경계를 검증한다.

## 완료 조건

- 최종 판단 CTA가 총평과 핵심 해석 직후에 보인다.
- 판단 사유가 없거나 selected-route gate가 막히면 저장 CTA가 비활성화된다.
- React는 decision intent만 전달하고 Python이 검증 / row 작성 / append를 소유한다.
- Evidence Appendix와 Saved Decisions가 Final Review main flow에 렌더링되지 않는다.
- 기존 Final Decision JSONL row는 삭제하거나 재작성하지 않는다.
