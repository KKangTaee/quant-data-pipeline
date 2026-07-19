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
- 2026-07-19: 가독성 후속 baseline은 Portfolio Monitoring Python 101개, React 24개와 typecheck PASS.
- 2026-07-19: 35:65 layout·11px axis static contract가 기존 56:44·9px CSS에서 의도대로 RED였고, 최소 CSS 변경 후 focused component 12개와 전체 Portfolio Monitoring Python 102개가 PASS했다.
- 2026-07-19: React 24개, typecheck와 Vite production build PASS. 새 bundle은 `index-CHoWrRyt.css`, `index-DY2_I_Xi.js`이며 static entry relative asset assert도 직접 실행해 PASS했다.
- 2026-07-19: `.venv`에는 pytest가 없어 `python -m pytest tests/test_component_static_distribution.py`는 runner import 전에 중단됐다. pytest fixture가 없는 Portfolio Monitoring static distribution 함수만 직접 실행해 동일 assert 본문을 검증했다.
- 2026-07-19: local Streamlit server를 8522에서 정상 기동했으나 in-app Browser reload가 URL security policy로 다시 차단됐다. 대체 browser/raw automation으로 우회하지 않고 서버를 종료했으며 desktop/900px/420px QA와 신규 screenshot은 미완료다.
