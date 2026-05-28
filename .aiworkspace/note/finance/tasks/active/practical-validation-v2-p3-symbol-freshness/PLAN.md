# Practical Validation V2 P3 Symbol Freshness

## 이걸 하는 이유?

Selected Dashboard의 Performance Recheck가 실행 가능하더라도, 실제 ticker별 가격 데이터가 최신 DB 시장일을 따라가지 못하면 최신 기간 검증 효력이 약해진다. Recheck 전에 symbol-level freshness를 보여주면 데이터 부족을 결과 해석 전에 확인할 수 있다.

## Scope

- Selected component replay payload에서 ticker와 benchmark symbol을 추출한다.
- DB price freshness summary를 읽어 symbol별 latest date / row count / lag를 표시한다.
- missing / stale symbol은 pass가 아니라 review 또는 blocked evidence로 표시한다.
- 새 DB write, JSONL write, memo, preset, monitoring log 저장 기능은 추가하지 않는다.

## Non-Goals

- 가격 데이터 수집 또는 보강 job 실행.
- provider / holdings / exposure selected monitoring 보강.
- live approval, broker order, auto rebalance.

## Done Criteria

- Runtime read model이 symbol-level freshness route와 rows를 반환한다.
- Selected Dashboard Performance Recheck 영역에서 freshness table을 볼 수 있다.
- Service contract tests가 ready / missing-or-stale 상태와 read-only boundary를 검증한다.
