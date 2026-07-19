# Runs

- 2026-07-19: 기존 OHLCV V1 task, React chart source/CSS/helper와 최근 commit을 확인했다.
- 2026-07-19: user가 direct security-only 범위와 client-side SVG viewport A안을 승인했다.
- 2026-07-19: written spec 사용자 검토 승인 후 3차 TDD/QA/commit 구현 계획을 작성하고 spec coverage, placeholder, type/signature consistency를 자체 검토했다.
- 2026-07-19: linked worktree `codex/main-dev` baseline Python 100개, React 20개와 typecheck PASS.
- 2026-07-19: 1차 RED는 신규 viewport helper 4개 미구현으로 `4 failed / 20 passed`; GREEN은 React 24개와 typecheck PASS. Commit `79cb9b75`.
- 2026-07-19: 2차 source contract RED 후 wheel/drag/controls/range label/mobile styles를 구현. component Python 11개, React 24개, typecheck/build PASS. Commit `b824a98d`.
- 2026-07-19: 전체 Portfolio Monitoring Python 101개, React 24개, typecheck/build와 `git diff --check` PASS.
- 2026-07-19: 설계 재대조에서 lost pointer capture 복구 gap을 발견해 RED contract 후 `cancelPointerDrag`를 추가하고 focused Python, React 24개, typecheck/build를 재검증했다.
- 2026-07-19: in-app Browser가 `http://localhost:8522/selected-portfolio-dashboard` DOM 접근을 URL security policy로 차단해 desktop/420px interaction QA와 신규 screenshot을 수행하지 못했다. 우회 browser automation은 사용하지 않았다.
