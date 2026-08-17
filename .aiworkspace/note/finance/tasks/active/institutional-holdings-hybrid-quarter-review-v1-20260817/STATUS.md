# Institutional Holdings Hybrid Quarter Review V1 Status

State: active
Started: 2026-08-17

## Current Step

전체 roadmap `0/5차`. 사용자와 하이브리드 source, 두 performance window, 로컬 일정
기반 button 노출과 explicit-click 갱신 방향을 합의했고 written design 승인을 받았다.
TDD 기반 9-task 상세 구현 계획을 self-review했으며 1차 구현을 시작한다.

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

## Next Action

Task 1부터 inline execution으로 진행한다. 먼저 외부 요청 없는 local due action을
RED/GREEN 테스트로 구현하고, Task 2 SEC bulk discovery까지 1차 완료 조건을 검증한다.

## Current Scope Boundary

- 이 task는 Institutional Holdings source discovery, ingestion, historical comparison,
  performance proxy, React UI, focused QA와 durable documentation을 소유한다.
- unattended scheduler, notification, actual fund NAV, trading recommendation과 broker action은
  범위 밖이다.
