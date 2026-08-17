# Institutional Holdings Hybrid Quarter Review V1 Status

State: complete
Started: 2026-08-17

## Current Step

전체 roadmap `5/5차`. 외부 요청 없는 수동 hybrid refresh, amendment-aware history,
share-based position change, 두 성과 proxy와 v3 React `분기 리뷰`를 actual SEC/MySQL/
Browser QA 및 durable documentation까지 완료했다.

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
- 2026-08-17: 5차 live SEC에서 Q2 bulk 미공개와 Berkshire raw XML 89 rows를 확인하고,
  watchlist 12개 Q2 filing을 MySQL에 반영한 뒤 replay idempotency를 확인했다.
- 2026-08-17: 실제 EDGAR flat filename과 `13F-NT` 제출 완료 경계를 보정하고 1280/760/420
  Browser QA, console 0건, durable docs sync를 완료했다.
- 2026-08-17: 독립 코드 리뷰의 data-integrity finding을 반영해 bulk notice/empty/unknown
  pointer 승격을 차단하고, adjusted-close common-equity proxy, live due clock, bulk ledger replay
  skip, 저장 분기 전환 selector, bounded error와 request-level SEC pacing을 회귀 테스트로 닫았다.
- 2026-08-17: 최종 실제 DB에서 Berkshire adjusted-close proxy +8.42%/+6.48%, coverage
  99.99%, local current 12/12를 재확인하고 최신 freshness `2026-06-30` 브라우저 표시를 검증했다.
- 2026-08-17: 2차 재리뷰에서 pointer 단조성, `tableEntryTotal` 완전성, due/partial freshness
  분리를 보강했다. Incomplete filing은 filing-only evidence로 남지만 완료/portfolio 승격에서는
  제외하고, 실제 Q2 제출 최신성 query는 12/12를 유지했다.

## Next Action

완료 상태를 유지한다. 다음 분기 제출기한 이후 같은 수동 버튼/runbook으로 갱신하고,
official bulk 공개 후 필요하면 Data Operations에서 full reconciliation한다.

## Current Scope Boundary

- 이 task는 Institutional Holdings source discovery, ingestion, historical comparison,
  performance proxy, React UI, focused QA와 durable documentation을 소유한다.
- unattended scheduler, notification, actual fund NAV, trading recommendation과 broker action은
  범위 밖이다.
