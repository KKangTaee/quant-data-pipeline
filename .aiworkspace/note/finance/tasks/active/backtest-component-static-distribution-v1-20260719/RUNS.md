# Backtest Component Static Distribution V1 Runs

## 2026-07-19

1. Baseline focused service contract
   - Command: `uv run --with pytest python -m pytest tests/test_service_contracts.py -k 'react_component or workflow_shell' -q`
   - Result: 14 passed, 2 failed.
   - Interpretation: Final Review legacy function-name expectation과 Practical Validation legacy overview expectation의 기존 baseline 실패이며 사용자 승인 후 범위 밖으로 유지했다.

2. TDD RED
   - Config/loader contract: `outDir: "build"` 때문에 예상 실패.
   - Static entry/asset contract: `component_static/index.html` 부재 때문에 예상 실패.

3. TDD GREEN after source migration
   - Config/loader contract: 1 passed.
   - Python compile: 12개 wrapper와 두 test module 성공.

4. Frontend builds
   - 12개 `app/web/components/*/frontend`에서 `npm ci --no-audit --no-fund && npm run build` 실행.
   - Result: 12/12 Vite build 성공, 각 `component_static/index.html`과 relative JS/CSS 생성.

5. Static distribution contract
   - Command: `uv run --with pytest python -m pytest tests/test_component_static_distribution.py -q`
   - Result: 2 passed.

6. Focused service contract after build
   - Result: 14 passed, 동일 baseline 2 failed. component_static missing-entry 실패 6건은 모두 해소됐다.

7. Git distribution check
   - Tracked `component_static/index.html`: 12.
   - Tracked `frontend/build/**`: 0.

8. Clean archive
   - `git archive HEAD`를 임시 directory에 풀고 npm 없이 repository contract 실행.
   - 첫 시도는 저장소 `.venv`에 pytest가 없어 test collection 전에 종료.
   - `uv run --no-project --with pytest`로 pytest만 제공한 재시도: 2 passed.

9. Actual Browser QA
   - Port 8531에서 Streamlit을 임시 실행하고 `/backtest` 확인.
   - React workflow shell, Level1 decision workspace, settings workspace가 렌더링됨.
   - Browser console error: 0.
   - Screenshot: `backtest-component-static-distribution-qa.png`; generated artifact로 commit 제외.
