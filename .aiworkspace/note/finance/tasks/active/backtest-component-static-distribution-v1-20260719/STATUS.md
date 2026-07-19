# Backtest Component Static Distribution V1 Status

Status: Complete
Updated: 2026-07-19
Roadmap: 3/3 complete

## Completed

- Backtest Analysis, Practical Validation, Final Review 계열 React frontend 12개의 Vite output을 `frontend/component_static/`으로 통일했다.
- 12개 Python component loader가 `component_static/index.html` 존재를 availability 기준으로 사용한다.
- 기존 tracked `frontend/build/` 산출물을 제거하고 12개 entry와 relative JS/CSS assets를 Git에 포함했다.
- source/config와 정적 asset 완전성을 검사하는 repository contract test를 추가했다.
- npm 없는 clean archive와 실제 Streamlit Browser QA에서 React workflow shell과 Level1 workspace를 확인했다.

## Verification

- `npm ci && npm run build`: 12/12 성공
- `tests/test_component_static_distribution.py`: 3 passed
- clean `git archive HEAD`, npm build 없음: 2 passed
- focused service contracts: 14 passed, 기존 baseline 2 failed
- Browser QA: `/backtest` React shell/Level1 workspace 렌더, console error 0
- QA screenshot: `backtest-component-static-distribution-qa.png` generated local artifact, commit 제외

## 2026-07-20 Merge Extension

- merge base 이후 추가된 `backtest_portfolio_mix_workspace`도 같은 `component_static/` 계약으로 편입했다.
- 현재 Backtest React package는 13개이며 tracked `frontend/build/**`는 0개다.
- 통합 후 static distribution `4 passed`, focused Python `222 passed`, Portfolio Monitoring React `25 passed`와 actual Browser QA를 확인했다.

## Remaining

- 이번 task의 구현 잔여 작업은 없다.
- 기존 baseline 실패 2건은 `RISKS.md`에 기록했으며 이번 packaging 변경 범위 밖이다.
- frontend source를 수정하는 후속 작업은 해당 `component_static/` bundle도 다시 build해 같은 커밋에 포함해야 한다.
- source와 committed bundle의 deterministic rebuild 비교 자동화는 후속 CI 보강 과제다.

## Scope Guard Preserved

- UI 디자인, payload, event, 계산, registry, DB 동작을 변경하지 않았다.
- qweb 또는 다른 launcher를 다시 도입하지 않았다.
