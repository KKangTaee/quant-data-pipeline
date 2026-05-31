# Final Review Selected Dashboard Handoff V1

Status: Active
Started: 2026-05-31

## 이걸 하는 이유?

Final Review는 최종 판단을 기록하고, Selected Portfolio Dashboard는 선정 이후의 운영 점검을 읽는다.
하지만 현재 화면에서는 저장된 Final Review 판단 중 어떤 row가 dashboard 대상이 되는지, dashboard로 넘어가기 전에 무엇이 막히는지, 사용자가 다음에 어디로 가야 하는지가 한 화면에서 충분히 명확하지 않다.

이 작업은 기존 검증을 다시 수행하지 않고, Final Decision V2 row를 읽어 Selected Dashboard handoff 상태를 보여주는 read-only 연결 레이어를 추가한다.

## Scope

- Final Review saved decision review에 Selected Dashboard handoff 요약을 추가한다.
- Selected Portfolio Dashboard 상단에 Final Review handoff 상태를 추가한다.
- 런타임 read model은 Final Decision V2 row를 읽어 handoff route, 대상 row, checklist, execution boundary를 만든다.
- service contract로 선정 row 연결 / 비선정 row 차단 / read-only boundary를 고정한다.
- 관련 durable docs와 root handoff log를 정렬한다.

## Out Of Scope

- 새 registry / saved file schema 추가
- monitoring log 자동 저장
- live approval, broker order, auto rebalance
- provider / FRED 직접 fetch
- Practical Validation 재검증 또는 Final Review selected-route gate 재계산

## Done Criteria

- Final Review에서 저장된 판단과 Selected Dashboard 연결 가능 상태를 볼 수 있다.
- Dashboard에서 Final Review selected row가 없거나 차단된 이유를 상단에서 볼 수 있다.
- handoff read model은 read-only execution boundary를 포함한다.
- focused unit tests, py_compile, diff check, Browser QA를 통과한다.
- 관련 docs / task log가 업데이트되고 coherent commit이 생성된다.
