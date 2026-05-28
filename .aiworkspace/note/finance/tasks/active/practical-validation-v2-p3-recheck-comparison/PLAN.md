# Practical Validation V2 P3 Recheck Comparison

## 이걸 하는 이유?

Selected Portfolio Dashboard에서 Performance Recheck를 실행해도, 현재 결과가 원래 Final Review 선정 근거를 얼마나 유지하거나 훼손했는지 한 번 더 구조적으로 읽기 어렵다. 실전 검토 흐름에서는 “재검증을 했다”보다 “재검증 결과가 기존 선정 thesis를 계속 지지하는가”가 더 중요하다.

## Scope

- Selected Dashboard에 read-only recheck comparison view를 추가한다.
- 최신 Performance Recheck session result와 Final Review baseline을 비교한다.
- `NOT_RUN` / error / partial evidence를 pass로 숨기지 않는다.
- DB, JSONL, monitoring log, 사용자 memo, preset 저장 기능은 추가하지 않는다.

## Non-Goals

- 새 portfolio comment / time record / memo persistence.
- selected monitoring log 자동 append.
- broker order, live approval, auto rebalance.
- provider / FRED 직접 fetch.

## Done Criteria

- Runtime read model이 recheck 미실행을 `NEEDS_INPUT`으로 반환한다.
- Runtime read model이 CAGR / MDD / benchmark spread / component coverage를 `PASS`, `WATCH`, `BREACHED`, `NEEDS_INPUT`으로 분류한다.
- Dashboard Review Signals에서 비교 결과를 확인할 수 있다.
- Service contract tests와 boundary 검증이 통과한다.
