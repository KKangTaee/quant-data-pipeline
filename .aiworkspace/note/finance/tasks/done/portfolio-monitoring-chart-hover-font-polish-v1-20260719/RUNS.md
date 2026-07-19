# Runs

- 시작 상태: `codex/main-dev`, tracked working tree clean. 기존 untracked QA 산출물은 보존한다.
- RED: React state test 2건은 helper 부재로 실패했고 Python component contract 2건은 hover layer/+1px style 부재로 실패했다.
- GREEN: focused React 17 tests, Python component 7 tests PASS.
- Final regression: Portfolio Monitoring Python 89 tests, React 17 tests, `tsc --noEmit`, Vite production build, `git diff --check` PASS.
- Browser QA: actual `디폴트` group의 392-point 가치곡선, enlarged typography/layout, date/value tooltip DOM, guide line, active point를 확인했다.
- Screenshot: `portfolio-monitoring-chart-hover-font-qa.png` (generated artifact, commit 제외).
