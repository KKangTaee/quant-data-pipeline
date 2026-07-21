# Runs

- 구현 전: local code, DB freshness, existing OHLCV job, NYSE calendar, React event bridge 경계를 검토했다.
- TDD RED: 새 서비스 import 4 errors, execution stub 4 failures, page event/helper와 React summary/action contract 실패를 확인했다.
- `.venv/bin/python -m unittest tests.test_portfolio_monitoring_price_refresh`: 8 tests OK.
- `.venv/bin/python -m unittest tests.test_portfolio_monitoring_page tests.test_portfolio_monitoring_price_refresh`: 25 tests OK.
- `.venv/bin/python -m unittest discover -s tests -p 'test_portfolio_monitoring*.py'`: 168 tests OK.
- Portfolio Monitoring React: `npm run typecheck`, `npm test -- --run` 33 tests, `npm run build` 통과.
- Python component contract: 18 tests OK; 새 service/page `py_compile`와 `git diff --check` 통과.
- actual Browser QA: 갱신 전 공통 기준일 2026-07-16, target 2026-07-21, stale AMD/RKLB/TEM/QQQ/SOXX를 확인했다. action 1회 실행 후 성공 feedback, 공통 기준일 2026-07-21, up-to-date 안내, refresh action 0개를 확인했다.
- QA screenshot: `portfolio-monitoring-price-refresh-qa.png` (generated artifact, commit 제외).
- 이 환경에는 pytest가 없어 계획서의 pytest 예시는 동일 test module을 `unittest`로 실행했다.
