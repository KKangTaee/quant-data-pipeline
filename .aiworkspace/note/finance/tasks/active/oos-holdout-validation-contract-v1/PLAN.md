# OOS Holdout Validation Contract V1 Plan

Status: Complete
Created: 2026-05-29

## 이걸 하는 이유?

Phase 10의 10-2에서 walk-forward evidence는 생겼지만, 전체기간을 앞쪽 / 뒤쪽 구간으로 나눠 뒤쪽 미사용 구간에서도 benchmark 대비 성과가 유지되는지는 아직 독립 audit evidence가 아니었다.
이 task의 목적은 좋은 전체기간 백테스트가 in-sample에만 맞춰진 결과인지 확인할 수 있도록 OOS holdout evidence를 compact contract로 추가하는 것이다.

새 JSONL registry, 사용자 메모, preset 저장, 승인, 주문, 자동 리밸런싱을 추가하지 않는다.

## Scope

포함한다.

- benchmark-aligned in-sample / out-sample holdout helper 추가
- Practical Validation result payload에 compact `oos_holdout_validation` evidence 연결
- Validation Efficacy Audit에 `OOS holdout validation` row 추가
- service contract tests 추가
- Project Map / script map / roadmap / phase handoff sync

포함하지 않는다.

- historical regime split 구현
- 새 DB schema
- 새 JSONL registry
- raw split curve artifact 저장
- user memo / preset persistence
- broker order / live approval / auto rebalance

## Done Criteria

- missing portfolio / benchmark / short split history는 `PASS`가 아니다.
- proxy-only curve source는 강한 `PASS`가 아니라 `REVIEW`로 남는다.
- 충분한 runtime / embedded curve와 benchmark parity가 있으면 OOS rows가 `PASS` 또는 `REVIEW`로 계산된다.
- Validation Efficacy Audit이 OOS holdout row를 읽고 route에 반영한다.
- compile, service contract, boundary, hygiene, diff check가 통과한다.
