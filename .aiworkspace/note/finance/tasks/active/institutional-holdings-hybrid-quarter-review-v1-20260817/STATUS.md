# Institutional Holdings Hybrid Quarter Review V1 Status

State: active
Started: 2026-08-17

## Current Step

전체 roadmap `4/5차`. 외부 요청 없는 수동 hybrid refresh, amendment-aware history,
share-based position change와 두 성과 proxy를 v3 React `분기 리뷰` 화면까지 연결했다.
5차 actual SEC/DB/browser QA와 durable documentation을 진행한다.

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
- 2026-08-17: 2차 EDGAR watchlist ingestion, effective-quarter resolver와 bulk-first hybrid
  manual event를 구현하고 stored-data-only render boundary를 유지했다.
- 2026-08-17: 3차 `NEW/ADD/KEEP/REDUCE/DROP/NOT_COMPARABLE`, coverage-aware covered-sleeve
  proxy와 두 승인 window를 구현했다.
- 2026-08-17: 4차 v3 workbench에 조건부 수동 갱신 action과 `분기 리뷰` 목적지를 연결하고
  React/Python 집중 회귀 검증을 통과했다.

## Next Action

Task 9에서 live SEC discovery, actual MySQL replay, desktop/mobile Browser QA와 durable
documentation closeout을 수행한다.

## Current Scope Boundary

- 이 task는 Institutional Holdings source discovery, ingestion, historical comparison,
  performance proxy, React UI, focused QA와 durable documentation을 소유한다.
- unattended scheduler, notification, actual fund NAV, trading recommendation과 broker action은
  범위 밖이다.
