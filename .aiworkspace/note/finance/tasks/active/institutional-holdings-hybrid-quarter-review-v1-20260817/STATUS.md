# Institutional Holdings Hybrid Quarter Review V1 Status

State: active
Started: 2026-08-17

## Current Step

전체 roadmap `1/5차`. 외부 요청 없는 local due/current/partial action과 explicit-click 뒤에만
사용할 SEC 공식 bulk listing parser/discovery를 구현했다. 2차 EDGAR 개별 수집과
amendment-aware loader를 진행한다.

## Progress

- 2026-08-17: 현재 SEC bulk collector, DB freshness, latest/previous loader, React Studio와
  actual local DB snapshot을 조사했다.
- 2026-08-17: 2026 Q2 watchlist filing은 EDGAR에 공개됐지만 SEC bulk dataset은 아직
  March-April-May까지임을 공식 source로 대조했다.
- 2026-08-17: 자동 page-entry remote probe 대신 local due decision + explicit click을
  최종 UX로 승인받았다.
- 2026-08-17: quarter-end proxy와 filing-to-filing public-follow proxy를 함께 표시하기로
  승인받았다.
- 2026-08-17: active task plan/design/risks/notes/runs shell과 written spec을 작성했다.
- 2026-08-17: placeholder, internal consistency, scope와 ambiguity self-review를 통과했다.
- 2026-08-17: 승인된 spec을 local due, hybrid ingestion, amendment-aware history,
  quarter review, React, actual QA의 9개 TDD task로 구체화했다.
- 2026-08-17: 1차 local due decision과 SEC bulk candidate discovery를 RED/GREEN으로
  구현하고 focused regression을 통과했다.

## Next Action

Task 3에서 curated watchlist의 EDGAR submissions/index/XML을 정규화하고 manager별
transaction으로 저장하는 2차 ingestion 경계를 구현한다.

## Current Scope Boundary

- 이 task는 Institutional Holdings source discovery, ingestion, historical comparison,
  performance proxy, React UI, focused QA와 durable documentation을 소유한다.
- unattended scheduler, notification, actual fund NAV, trading recommendation과 broker action은
  범위 밖이다.
