# Plan

## 이걸 하는 이유?

Events 탭은 FOMC, Macro, Earnings row를 한 화면에 모으지만, 운영자는 매번 전체 table을 읽기보다
"이번 주에 볼 것", "중요 이벤트", "조치가 필요한 row"를 먼저 알아야 한다.

## Scope

- Events read model에 `Days Until`, `Importance`, `Focus`를 추가한다.
- Overview Events에 Focus view를 추가해 upcoming / needs review / high impact row를 빠르게 확인한다.
- Calendar chart를 event type별 흐름이 보이도록 보강한다.
- 기존 DB-first / Ingestion-first 구조는 유지한다.

## Non-goals

- 새 event source를 추가하지 않는다.
- 자동 refresh schedule을 추가하지 않는다.
- `market_event_calendar` schema를 변경하지 않는다.
