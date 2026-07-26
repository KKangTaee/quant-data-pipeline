# Risk-On Momentum 5D Productionization Status

State: active
Last Updated: 2026-07-26

## Current Position

- 전체 roadmap: 0/3차 구현 완료
- 진단과 설계: 완료
- 현재 단계: written spec review
- 다음 단계: 승인된 spec을 구현 plan으로 변환한 뒤 1차 TDD 시작

## Confirmed

- 사용자는 1차 runtime, 2차 validation handoff, 3차 maturity/governance 전체 방향을 승인했다.
- V1/V2 core behavior tests와 governance tests 13개가 현재 통과한다.
- Top1000 2년 actual DB profile로 반복 시뮬레이션과 per-day full-universe
  `iterrows()`가 주요 병목임을 확인했다.

## Not Yet Implemented

- prepared simulation object / indexed hot path
- variant execution plan / duplicate reuse
- analysis intensity
- compact Daily Swing evidence
- Practical Validation module
- Final Review / monitoring policy
- production maturity transition

## Scope Exclusions

- broker/account integration
- live approval
- automatic order or automatic rebalancing
- unrelated finance UX polish
- registry/saved/run-history cleanup
