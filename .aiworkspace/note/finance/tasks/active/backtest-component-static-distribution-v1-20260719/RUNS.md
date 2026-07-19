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
   - Initial result: path/asset 2 passed.
   - Review hardening: `emptyOutDir`과 entry/referenced asset Git tracking assertion을 추가해 3 passed.

6. Focused service contract after build
   - Result: 14 passed, 동일 baseline 2 failed. component_static missing-entry 실패 6건은 모두 해소됐다.

7. Git distribution check
   - Tracked `component_static/index.html`: 12.
   - Tracked `frontend/build/**`: 0.

8. Clean archive
   - `git archive HEAD`를 임시 directory에 풀고 npm 없이 repository contract 실행.
   - 첫 시도는 저장소 `.venv`에 pytest가 없어 test collection 전에 종료.
   - `uv run --no-project --with pytest`로 pytest만 제공하고 Git metadata가 필요 없는 path/asset test 두 개만 실행한 재시도: 2 passed.

9. Actual Browser QA
   - Port 8531에서 Streamlit을 임시 실행하고 `/backtest` 확인.
   - React workflow shell, Level1 decision workspace, settings workspace가 렌더링됨.
   - Browser console error: 0.
   - Screenshot: `backtest-component-static-distribution-qa.png`; generated artifact로 commit 제외.

10. Independent review
   - 12 tracked entries, 24 referenced assets, legacy tracked build 0, archived rebuild byte identity를 확인했다.
   - Important finding인 Git tracking / `emptyOutDir` 자동 assertion을 보완했다.
   - loader fallback과 multi-commit rollback 문서를 실제 동작에 맞게 수정했다.

## 2026-07-20 Master Merge Integration

1. Merge RED
   - `tests/test_component_static_distribution.py`가 merge base 이후 추가된 `backtest_portfolio_mix_workspace`와 남은 `frontend/build/` 3개를 찾아 2 failures로 실패했다.
2. Merge GREEN
   - Portfolio Mix wrapper/Vite output을 `component_static/index.html` 계약으로 전환하고 최신 source를 build했다.
   - Static distribution contract: `4 passed`; tracked Backtest React package 13개, tracked `frontend/build/**` 0개.
3. Integrated verification
   - Python focused: `222 passed`, `8 subtests passed`.
   - Portfolio Monitoring React: `25 passed`; typecheck/build 성공.
   - Broad service/reference contracts: `834 passed`, 기존 baseline과 같은 `12 failed`, `35 subtests passed`.
   - Browser: `/backtest` Portfolio Mix one-shell과 `/selected-portfolio-dashboard` Portfolio Monitoring one-shell 렌더, console error/warn 0.
