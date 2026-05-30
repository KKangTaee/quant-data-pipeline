# Backtest Practical Validation Handoff Gate V1 Plan

Status: Complete
Created: 2026-05-30

## 이걸 하는 이유?

Backtest Analysis의 `검증 후보로 보내기` 버튼은 2차 `Practical Validation`으로 넘기는 handoff이므로, 사용자에게는 1차 후보 판단을 통과했다는 의미로 읽힌다.
따라서 후보 판단 blocker가 남아 있을 때는 버튼을 비활성화하고, 막힌 근거를 짧게 보여줘야 한다.

## Scope

- `Candidate Readiness`의 `can_move_to_compare` 결과로 Practical Validation handoff 버튼을 활성화 / 비활성화한다.
- 비활성 상태에서는 Promotion / 실행 원천 / 검증 원천 blocker 근거를 짧게 표시한다.
- 버튼과 handoff 영역을 상태형 card로 바꿔 사용자가 다음 단계 의미를 빠르게 이해하게 한다.
- 관련 docs / logs / service contract test를 정렬한다.

## Out Of Scope

- 새 registry / JSONL source format 추가
- Practical Validation 내부 검증 기준 재설계
- Final Review gate policy 변경
- live approval, order, account sync, auto rebalance
