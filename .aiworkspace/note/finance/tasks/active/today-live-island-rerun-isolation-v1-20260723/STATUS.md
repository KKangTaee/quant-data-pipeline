# Today Live Island Rerun Isolation V1 Status

Status: 1/2 implementation stages in progress
Roadmap: 1/2 render isolation implemented
Last Updated: 2026-07-23

## Completed

- actual `main-dev` browser와 source를 대조해 15초 전체 Today fragment와 1초 top-level React clock state를 분리 진단했다.
- static cache, portfolio live island, separate API/push의 세 접근을 비교했다.
- 사용자가 portfolio live island 방향을 승인했다.
- `DESIGN.md`에 static shell, clock child, conditional heartbeat, portfolio island, failure/test 계약을 고정했다.
- 사용자가 written specification을 승인했다.
- `IMPLEMENTATION_PLAN.md`에 1/2차 렌더 격리와 2/2차 conditional live island를 3개 TDD task로 분해했다.
- public portfolio-only projection과 OPEN/EOD-active heartbeat policy를 TDD로 추가했다.
- clock, portfolio, actions를 독립 React view로 분리하고 1초 timer를 `MarketSessionClock`에 격리했다.
- Today Python 54개와 React 16개 회귀, typecheck, production build를 통과했다.

## Next

- 2/2차 minimal island payload, conditional fragment, phase-transition event를 구현한다.
