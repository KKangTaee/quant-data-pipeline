# Today Contributor Coverage / Review Layout V1 Runs

## 2026-07-23 Investigation

- Inspected the supplied 2048×623 screenshot at original detail.
- Read `TodayPortfolioPanel.tsx`, Today projection code, CSS, existing tests, and recent contributor commits.
- Loaded the actual default portfolio read-only: active count 5; AMD, RKLB, TEM, QQQ, and SOXX all have numeric contribution values.
- Confirmed the projected output contains only AMD, TEM, and RKLB because of positive top-2 / negative bottom-2 slicing.

## 2026-07-23 TDD And Regression

- RED: EOD completeness test omitted SOXX/QQQ; live ordering test retained input order and treated zero as negative.
- GREEN: Today Python suite passed 61 tests after complete projection, coverage copy, fallback, and CSS contract changes.
- Relevant regression: `tests.test_today_home`, `tests.test_portfolio_monitoring_intraday_refresh`, and `tests.test_portfolio_monitoring_valuation` passed 93 tests.
- React: 19 tests passed; TypeScript typecheck and Vite production build completed successfully.
- `python -m py_compile app/services/today.py app/web/today_page.py` completed successfully.

## 2026-07-23 Actual Browser QA

- Fresh Streamlit server at port 8523 loaded the actual default portfolio.
- Verified coverage label `전체 5개 · 영향 큰 순` and order AMD, TEM, RKLB, SOXX, QQQ.
- Measured review panel: contributor/review tops both 680px, `align-content: start`, three row heights 16px, gaps `[8, 8]`.
- At 1280, 760, and 420px, the top document and all three component iframes had horizontal overflow 0.
- Browser console errors: 0.
- Saved generated screenshot `today-contributor-coverage-layout-v1-qa.png`; excluded from staging.
