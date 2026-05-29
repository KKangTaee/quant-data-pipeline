# Plan

## 이걸 하는 이유?

Events 탭은 FOMC / earnings / macro calendar 데이터를 이미 저장해서 보여주지만, 기존 화면은 refresh buttons, status cards, filters, nested tabs, tables가 기능 단위로 흩어져 있어 사용자가 먼저 봐야 할 일정과 데이터 신뢰도를 빠르게 파악하기 어려웠다.

## Scope

- `app/web/overview_dashboard.py`의 Events 탭 화면 흐름을 재구성한다.
- `app/web/overview_ui_components.py`에 Events 전용 summary / source / agenda 렌더러를 추가한다.
- DB schema, collector, service read model은 바꾸지 않는다.
- 기존 저장 테이블 `finance_meta.market_event_calendar` read model만 사용한다.

## Acceptance

- Events 상단이 source status / refresh action / summary 중심으로 읽힌다.
- Main view가 `Agenda / Calendar / Quality / Raw`로 정리된다.
- Nested `Focus -> Upcoming / Needs Review / High Impact` 구조를 제거한다.
- 기존 Calendar와 raw table 확인 경로는 유지한다.
