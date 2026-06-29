# Overview Market Movers Polish V3 Follow-up

## 이걸 하는 이유?

Market Movers Polish V3 이후 사용자가 확인한 실제 화면에서 두 가지 잔여 UX 문제가 남았다.

- Daily refresh action row가 coverage별로 caption/button 혼합 구조가 되어 레이아웃이 흔들린다.
- Sector / market breadth map 하단 leader strip이 위 lane 정보와 중복되어 화면이 길어진다.

## Scope

- Daily refresh row의 4개 슬롯을 coverage와 무관하게 같은 형태로 유지한다.
- SP500 / NASDAQ은 기존 refresh action을 유지하고, Top universe 계열은 같은 슬롯에 비활성 기준 버튼을 둔다.
- Sector breadth map의 하단 duplicate leader strip 렌더링을 제거한다.
- 새 provider, DB schema, 직접 외부 fetch, recommendation / signal 표현은 추가하지 않는다.

## 완료 조건

- 회귀 테스트가 refresh slot 고정과 duplicate strip 제거를 확인한다.
- Browser QA에서 SP500, Top universe, NASDAQ coverage의 refresh row가 깨지지 않는다.
- QA screenshot은 generated artifact로 남기고 stage하지 않는다.
