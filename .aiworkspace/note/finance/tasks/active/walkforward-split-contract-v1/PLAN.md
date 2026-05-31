# Walk-forward Split Contract V1 Plan

Status: Complete
Created: 2026-05-29

## 이걸 하는 이유?

Phase 10의 첫 source map 결과, Practical Validation에는 curve / benchmark / replay source plumbing이 있지만 walk-forward evidence가 독립 audit row로 연결되어 있지 않았다.
이 task의 목적은 좋은 전체기간 백테스트가 rolling 구간별 benchmark-relative 성과에서도 유지되는지 compact contract로 확인하는 것이다.

새 JSONL registry, 사용자 메모, preset 저장, 승인, 주문, 자동 리밸런싱을 추가하지 않는다.

## Scope

포함한다.

- benchmark-aligned walk-forward / rolling temporal validation helper 추가
- Practical Validation result payload에 compact `temporal_validation` evidence 연결
- Validation Efficacy Audit에 `Walk-forward temporal validation` row 추가
- service contract tests 추가
- Project Map / script map / roadmap / phase handoff sync

포함하지 않는다.

- OOS holdout row 전체 구현
- historical regime split 구현
- 새 DB schema
- 새 JSONL registry
- user memo / preset persistence
- broker order / live approval / auto rebalance

## Done Criteria

- missing portfolio / benchmark / short history는 `PASS`가 아니다.
- proxy-only curve source는 강한 `PASS`가 아니라 `REVIEW`로 남는다.
- 충분한 runtime / embedded curve와 benchmark parity가 있으면 walk-forward rows가 `PASS` 또는 `REVIEW`로 계산된다.
- Validation Efficacy Audit이 temporal validation row를 읽고 route에 반영한다.
- compile, service contract, boundary, hygiene, diff check가 통과한다.
