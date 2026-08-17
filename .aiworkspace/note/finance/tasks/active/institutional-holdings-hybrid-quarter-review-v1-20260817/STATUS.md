# Institutional Holdings Hybrid Quarter Review V1 Status

State: active
Started: 2026-08-17

## Current Step

전체 roadmap `0/5차`. 사용자와 하이브리드 source, 두 performance window, 로컬 일정
기반 button 노출과 explicit-click 갱신 방향을 합의했다. Written design spec을 작성했고
구현 계획 전 사용자 검토를 기다린다.

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

## Next Action

사용자가 written design을 검토·승인하면 `superpowers:writing-plans`로 TDD 기반 상세
구현 계획을 작성한다. 그 전에는 implementation code를 변경하지 않는다.

## Current Scope Boundary

- 이 task는 Institutional Holdings source discovery, ingestion, historical comparison,
  performance proxy, React UI, focused QA와 durable documentation을 소유한다.
- unattended scheduler, notification, actual fund NAV, trading recommendation과 broker action은
  범위 밖이다.
