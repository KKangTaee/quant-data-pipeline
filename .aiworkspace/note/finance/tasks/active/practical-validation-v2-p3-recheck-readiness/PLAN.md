# Practical Validation V2 P3 Recheck Readiness

## 이걸 하는 이유?

Selected Dashboard의 Performance Recheck는 선정 이후 검증 효력을 높이는 핵심 동작이다. 하지만 실행 전 DB 최신 시장일과 selected component replay contract가 준비됐는지 명확히 보이지 않으면, 사용자는 오류가 난 뒤에야 데이터 / contract 문제를 알게 된다.

## Scope

- Selected Dashboard에 read-only Recheck Readiness view를 추가한다.
- DB latest market date, baseline 기간, selected component replay contract, execution boundary를 확인한다.
- 미실행 / 데이터 부족 / contract 누락을 pass로 숨기지 않는다.
- 새 DB write, JSONL write, memo, preset, monitoring log 저장 기능은 추가하지 않는다.

## Non-Goals

- provider / price ingestion 실행.
- selected monitoring log 자동 append.
- 사용자 comment / time record / preset 저장.
- live approval, broker order, auto rebalance.

## Done Criteria

- Runtime read model이 DB latest market date와 replay contract readiness를 반환한다.
- Dashboard Performance Recheck 영역에서 readiness badge와 상세 row를 볼 수 있다.
- Service contract tests로 read-only boundary와 blocked / ready 상태를 검증한다.
