# Design

## Summary

Final Review scorecard를 단일 준비도 점수에서 투자 판단용 상세 점수판으로 확장한다. 종합점수는 유지하지만, 사용자는 세부 dimension, 점수 영향 요인, score cap, 최종 선택 사유를 함께 읽는다.

## Score Dimensions

| Dimension | Meaning | Primary Inputs |
|---|---|---|
| Investment Score | 성과 / benchmark / 전략 매력도 | investability packet score, gate evidence, performance labels |
| Risk Score | drawdown / robustness / construction 부담 | selection blockers, robustness / construction review evidence |
| Readiness Score | Final Review 판단 저장과 Monitoring handoff 준비도 | selected-route gate, blocker count |
| Evidence Quality Score | 데이터 / 검증 / REVIEW 근거 품질 | Level2 REVIEW warning / open review, packet evidence |
| Monitoring Suitability Score | 추적 조건과 운영 가능성 | monitoring follow-up, review trigger, handoff status |

## Overall Score

기본 가중치:

- Investment 30%
- Risk 20%
- Readiness 20%
- Evidence Quality 20%
- Monitoring Suitability 10%

Hard cap:

- hard blocker: max 55
- selected-route gate not ready: max 69
- critical open review: max 74
- excessive open review: max 79

## UI

React report는 `최종 점수 체계` section 안에서:

- 종합점수 / classification / route.
- 5개 세부 점수.
- 점수를 올린 요인.
- 점수를 깎은 요인.
- 점수 제한 / route 제한.
- 최종 선택 사유와 판단 저장 전 메모 포인트.

## Boundary

이 작업은 read model과 presentation만 바꾼다. 새 portfolio 생성, 신규 backtest, registry rewrite, saved setup 변경, live approval / order / auto rebalance는 만들지 않는다.
