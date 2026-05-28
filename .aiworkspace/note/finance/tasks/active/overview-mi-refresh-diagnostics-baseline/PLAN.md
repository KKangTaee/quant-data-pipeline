# Plan

## 이걸 하는 이유?

Overview Market Movers daily snapshot은 이미 5분 refresh와 missing diagnostics를 제공하지만, 운영자가 한눈에 `fresh / due / stale / partial / failed` 상태와 다음 조치를 판단하기에는 아직 부족하다. 정식화 2차의 첫 작업은 refresh 상태와 diagnostics를 명확하게 만드는 것이다.

## Scope

- Market Movers daily refresh state를 service read model에서 계산한다.
- 5분 refresh UX를 상태 badge, next refresh text, 버튼 help로 개선한다.
- missing diagnostics에 recommended action을 추가한다.
- latest snapshot source / age / failed count를 status card와 panel에서 더 명확히 노출한다.
- schema 변경과 새 provider 수집은 하지 않는다.

## Done Criteria

- daily Market Movers에서 refresh 필요 여부를 화면 상단에서 바로 판단할 수 있다.
- partial/fail일 때 missing symbol, reason, recommended action을 확인할 수 있다.
- service contract tests와 browser smoke가 통과한다.
