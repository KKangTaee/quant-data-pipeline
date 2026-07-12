# Institutional Portfolios Portfolio / Security IA V1 Runs

## 2026-07-12

- RED: `.venv/bin/python -m unittest tests.test_institutional_portfolios.InstitutionalPortfoliosNavigationTests.test_workbench_groups_portfolio_and_security_analysis_views` failed because `ViewName` still used `interest` and grouped tabs were absent.
- GREEN targeted: the same test passed after React tab IA changes.
- Focused suite: `.venv/bin/python -m unittest tests.test_institutional_portfolios` passed. Existing edgar deprecation and Streamlit bare-mode warnings were observed.
- Compile: `.venv/bin/python -m py_compile app/web/institutional_portfolios.py app/services/institutional_portfolios.py` passed.
- Build: `npm run build` passed in `app/web/streamlit_components/institutional_portfolios_workbench/`.
- Browser QA:
  - Local server: `.venv/bin/python -m streamlit run app/web/streamlit_app.py --server.port 8528 --server.headless true`.
  - Verified grouped tab counts: `포트폴리오 보기 = 1`, `종목 분석 보기 = 1`, `종목 상세 = 1`, old `보유 기관 조회 = 0`.
  - Clicked AAPL through visible DOM and verified `종목 상세` active state, `AAPL` heading, and chart stage.
  - Filtered current-port console errors for `8528`; none found.
  - Screenshots generated locally and not committed.
