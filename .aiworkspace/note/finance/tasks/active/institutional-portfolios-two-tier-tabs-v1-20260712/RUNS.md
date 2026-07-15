# Institutional Portfolios Two-Tier Tabs V1 Runs

## 2026-07-12

- RED: `.venv/bin/python -m unittest tests.test_institutional_portfolios.InstitutionalPortfoliosNavigationTests.test_workbench_uses_two_tier_portfolio_and_security_tabs` failed because `WorkspaceSection` / two-tier tab classes were absent.
- GREEN targeted: same test passed after React and CSS changes.
- Focused suite: `.venv/bin/python -m unittest tests.test_institutional_portfolios` passed. Existing edgar deprecation warnings and Streamlit bare-mode warnings were observed.
- Compile: `.venv/bin/python -m py_compile app/web/institutional_portfolios.py app/services/institutional_portfolios.py` passed.
- Build: `npm run build` passed in `app/web/streamlit_components/institutional_portfolios_workbench/`.
- Browser QA:
  - Local server: `.venv/bin/python -m streamlit run app/web/streamlit_app.py --server.port 8529 --server.headless true`.
  - Confirmed initial primary tabs `포트폴리오`, `종목 분석`; active `포트폴리오`; secondary tabs `요약`, `전체 보유`; old `.ip-tab-group` labels absent.
  - Clicked `종목 분석` and confirmed active primary `종목 분석`; secondary tabs `종목 상세`, `기관 보유 랭킹`; old `보유 기관 조회` label absent.
  - Attempted AAPL drilldown via browser automation, but in-app browser coordinate translation inside the Streamlit iframe reported an offscreen point. Existing source contract still verifies `handleDrilldown` sets `activeView("security")`; this browser run did not use that failed click as completion evidence.
  - Screenshot generated locally as `institutional-portfolios-two-tier-tabs-qa.png` and not committed.
