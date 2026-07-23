# Today Live Island Rerun Isolation V1 Status

Status: Complete
Roadmap: 2/2 implementation stages complete
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
- `today_portfolio_island_v1` minimal payload와 portfolio-only DB loader를 추가했다.
- 15초 fragment를 OPEN 또는 EOD waiting/running portfolio island로 제한하고 CLOSED confirmed에서는 중단한다.
- regular-session phase transition만 allowlist해 필요한 시점에 app run 한 번으로 heartbeat를 켜거나 끈다.
- Python 88개, React 17개/typecheck/build와 actual CLOSED 21초 Browser QA를 통과했다.
- 1280·760·420px overflow 0, console error 0, loading 0회, iframe 교체 0회, countdown 변화와 chart path 유지를 확인했다.

## Remaining Boundary

- 실제 정규장 OPEN provider completion timing 실측은 거래시간 외라 수행하지 못했다. OPEN heartbeat와 broad-loader 비호출은 deterministic Python 계약으로 검증했다.
- 별도 API/SSE/WebSocket과 OPEN fragment 자체의 짧은 running indicator 제거는 이번 범위 밖이다.
