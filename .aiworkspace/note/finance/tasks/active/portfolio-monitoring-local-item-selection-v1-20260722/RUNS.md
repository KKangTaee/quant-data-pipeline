# Runs

## 2026-07-22 기준선

- `.venv/bin/python -m unittest tests.test_portfolio_monitoring_read_model tests.test_portfolio_monitoring_component tests.test_portfolio_monitoring_page`
  - 56 tests, PASS
- `npm test -- --run && npm run typecheck`
  - 35 tests, PASS
  - TypeScript, PASS

## 2026-07-22 구현 검증

- `.venv/bin/python -m unittest tests.test_portfolio_monitoring_read_model tests.test_portfolio_monitoring_component tests.test_portfolio_monitoring_page tests.test_portfolio_monitoring_market_chart`
  - 64 tests, PASS
- `npm test -- --run`
  - 36 tests, PASS
- `npm run typecheck`
  - PASS
- `npm run build`
  - Vite production build, 173 modules transformed, PASS
- actual Browser QA: `http://localhost:8512/selected-portfolio-dashboard`
  - AMD에서 RKLB 선택 시 선택 행, 개별 추적 요약, `RKLB 가격 차트`가 즉시 전환됨
  - 그룹 현재가치 `$29,781` 유지, Streamlit Running 0, console warning/error 0
  - screenshot: `portfolio-monitoring-local-item-selection-qa.png` (generated, commit 제외)
