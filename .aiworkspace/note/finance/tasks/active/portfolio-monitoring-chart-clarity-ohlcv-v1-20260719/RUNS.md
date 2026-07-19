# Runs

- 2026-07-19: 설계 승인 후 implementation plan 작성.
- 2026-07-19: linked worktree `codex/main-dev` 확인. Python unittest 90개, React Vitest
  17개 및 typecheck 기준선 PASS. pytest 미설치로 plan 검증 명령을 unittest로 정정.
- 2026-07-19: 1차 `aa21dc90` — 날짜 눈금 helper와 정적 halo 제거를 TDD로 구현. React 18개, component Python 9개, typecheck PASS.
- 2026-07-19: 2차 `634e15d0` — DB-only selected-item OHLCV projection과 Operations read guard를 구현. focused Python 23개 PASS.
- 2026-07-19: 3차 `180f44f5` — direct security line/candle/volume/tooltip과 strategy value-only 상세를 구현. React 20개, component Python 10개, typecheck/build PASS.
- 2026-07-19: 전체 Portfolio Monitoring Python unittest `100 passed`; React Vitest `20 passed`; TypeScript typecheck와 Vite production build PASS.
- 2026-07-19: 실제 Streamlit route의 empty DB 상태에서 console error 0건을 확인했다. 동일 production bundle의 populated fixture로 desktop line/candle toggle, OHLCV tooltip, volume, strategy value-only 전환을 확인했다.
- 2026-07-19: 420×900에서 날짜 눈금 3개, candle/volume 가독성, `clientWidth=405`, `scrollWidth=405`로 가로 overflow 0을 확인했다.
- 2026-07-19: `git diff --check` PASS. QA screenshot은 generated artifact로 남기고 commit에서 제외했다.
