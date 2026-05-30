# Plan

## 이걸 하는 이유?

Market Movers daily snapshot은 장중 판단의 핵심 화면이지만, TOP1000 / TOP2000까지 확장된 뒤에는 운영자가 refresh 필요 여부, stale 정도, partial 상태, 다음 조치를 빠르게 판단해야 한다.

## Scope

- Market Movers daily snapshot read model에 운영 상태 세부 정보를 보강한다.
- SP500뿐 아니라 TOP1000 / TOP2000 daily view에서도 status check와 refresh due 표시가 동작하게 한다.
- Market Movers 탭에 Ops Summary / Refresh Guidance를 추가해 stale, partial, missing, failed 상태의 다음 조치를 명확히 한다.
- 외부 데이터 수집 경로, DB schema, 자동 refresh schedule은 변경하지 않는다.
