# Design

## Search Shape

- 우선 직전 fix의 대상 후보인 `GRS Liquid Macro Top2`를 fresh 실행해 selected-route 통과 여부를 확인한다.
- 시간이 허용되면 GTAA / Risk Parity / Dual Momentum 같은 ETF dynamic 후보도 같은 dry-run pipeline으로 확인한다.
- 각 후보는 `runtime bundle -> candidate draft -> selection source -> stored-period replay -> Practical Validation result -> selected-route preflight -> Final Review selected gate` 순서로 평가한다.

## Boundaries

- Persistence helper는 호출하지 않는다.
- `PORTFOLIO_SELECTION_SOURCES.jsonl`, `PRACTICAL_VALIDATION_RESULTS.jsonl`, saved setup, run history는 탐색 결과로 stage하지 않는다.
- 결과는 task docs와 최종 응답에 요약한다.
