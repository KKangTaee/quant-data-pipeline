# Backtest Component Static Distribution V1 Notes

## Decisions

- Backtest 계열 React component는 Overview와 같은 committed static artifact 정책을 사용한다.
- canonical output은 `frontend/component_static/`이며 `frontend/build/` dual fallback은 두지 않는다.
- Python loader는 directory 존재가 아니라 `component_static/index.html` 존재로 availability를 판정한다.
- 모든 Vite config에 `emptyOutDir: true`를 명시해 stale hashed asset이 남지 않게 한다.
- React source 변경과 생성된 `component_static/` 변경은 같은 commit unit으로 취급한다.
- repository contract는 output path, `emptyOutDir`, entry/asset 완전성, Git tracking을 검사한다. source와 minified bundle의 byte 동일성은 closeout rebuild에서 확인하며 자동 비교는 후속 CI 범위다.

## Inventory

- Backtest Analysis: workflow shell, decision workspace, result workspace, factor readiness, handoff, policy signal, price freshness, price refresh
- Practical Validation: decision workspace, data action board, fix queue
- Final Review: investment report compatibility directory/current decision workspace

## Non-Changes

- component props, emitted intent, Python handler, workflow Gate, persistence와 DB source boundary는 그대로다.
- fallback renderer는 불완전하거나 누락된 `index.html`에서 계속 사용된다.
