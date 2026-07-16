# Economic Cycle Provisional Hybrid V2 Risks

Last Updated: 2026-07-16

| Risk | Mitigation |
|---|---|
| 잠정 확률을 검증 완료로 오해 | badge, 색, 사유, 방법론 disclosure를 함께 표시 |
| threshold 완화로 품질 의미 훼손 | validation code와 기준값은 변경하지 않음 |
| history rematerialization 비용 | 기존 origin별 artifact를 재사용하고 PIT panel을 한 번 prime |
| 기존 valuation mode 회귀 | focused routing/valuation regression과 Browser QA 실행 |

## Remaining Boundary

- 세 current horizon은 검증 완료가 아니라 잠정 추정이다. 데이터/모델 개선으로 gate를 통과할 때만 `VERIFIED`로 바뀐다.
- 초기 replay 일부는 phase support가 없어 판단 불가다. 과거 표본을 합성하지 않는다.
