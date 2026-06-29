# Overview Legacy Cleanup V6-V10 Plan

## 이걸 하는 이유?

V2-V5에서 Overview의 page / tab / component surface / service surface 경계는 생겼지만, 실제 renderer body와 read-model body 일부는 아직 `legacy_dashboard.py`, `overview_ui_components.py`, `overview_market_intelligence.py`에 남아 있다. 이번 V6-V10은 사용자가 요청한 대로 차수별 QA를 거치며 active path가 쓰지 않는 legacy를 식별하고, 확인된 범위부터 제거한다.

## Roadmap

1. V6: legacy 사용 현황을 감사하고 active / retained / removable 후보를 문서화한다.
2. V7: active tab render helper 일부를 domain module로 물리 이동해 `legacy_dashboard.py` 의존을 줄인다.
3. V8: service/read-model 계산 body 일부를 `app/services/overview/*`로 물리 이동한다.
4. V9: V6에서 확인된 unused legacy를 제거하거나 compatibility-only로 명확히 격리한다.
5. V10: boundary guard, durable docs, root handoff log, final QA를 정리한다.

## Out Of Scope

- provider / DB schema / registry / saved JSONL 변경
- render 중 external provider fetch 추가
- trading signal / recommendation / validation gate / monitoring signal / broker order / auto rebalance semantics 추가
- Overview UI redesign 또는 새 기능 추가

