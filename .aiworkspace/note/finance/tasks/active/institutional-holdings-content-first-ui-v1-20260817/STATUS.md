# Institutional Holdings Content-First UI V1 Status

State: active
Last Updated: 2026-08-17

## Current Progress

- 전체 roadmap `1/3차` 설계 단계 진행 중.
- current code, flow docs와 prior Institutional Holdings redesign 기록을 확인했다.
- manager selection regression의 server-side search/selection normalization 충돌을 특정했다.
- 사용자는 visual companion의 A안 `Content-first 하이브리드`와 상세 interaction contract를
  승인했다.
- written design spec을 작성했고 사용자가 검토·승인했다.
- TDD, semantic shell, visual/runtime bundle, actual Browser QA의 네 task로 나눈
  implementation plan을 작성했다.

## Next Action

실행 방식을 확정한 뒤 Task 1의 failing manager-selection regression부터 2차 구현을
시작한다.

## Current Scope Boundary

- 이번 task는 Institutional Holdings manager selection state, React shell, responsive UI,
  focused tests, production component build와 Browser QA만 소유한다.
- 13F ingestion, DB schema, amendment/quarter performance semantics와 다른 top-level surface는
  변경하지 않는다.
