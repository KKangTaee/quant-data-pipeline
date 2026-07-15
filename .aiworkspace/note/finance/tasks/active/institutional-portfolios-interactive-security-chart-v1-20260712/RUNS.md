# Institutional Portfolios Interactive Security Chart V1 Runs

## 2026-07-12

- RED: `.venv/bin/python -m unittest tests.test_institutional_portfolios.InstitutionalPortfolioReadModelTests.test_selected_security_model_combines_holding_chart_and_holder_list tests.test_institutional_portfolios.InstitutionalPortfoliosNavigationTests.test_selected_security_chart_supports_hover_candles_guides_and_pan_controls` failed on missing `open` field and missing `InteractiveSecurityChart`.
- GREEN targeted: same command passed after service payload and React chart implementation.
- Focused suite: `.venv/bin/python -m unittest tests.test_institutional_portfolios` passed. Existing edgar deprecation and Streamlit bare-mode warnings were observed.
- Compile: `.venv/bin/python -m py_compile app/services/institutional_portfolios.py app/web/institutional_portfolios.py` passed.
- Build: `npm run build` passed in `app/web/streamlit_components/institutional_portfolios_workbench/`.
- Browser QA:
  - Local server: `.venv/bin/python -m streamlit run app/web/streamlit_app.py --server.port 8527 --server.headless true`.
  - Opened `http://localhost:8527/institutional-portfolios`.
  - Drilled into AAPL selected security.
  - Verified counts through iframe locator: chart stage `1`, range input `1`, high/low guides `2`, line chart `1`, line toggle `1`, candle toggle `1`.
  - Hover over chart produced tooltip `1`, crosshair `2`, hover dot `1`.
  - Filtered current-port console errors for `8527`; none found.
  - Screenshot: `institutional-portfolios-interactive-chart-qa.png` generated locally, not committed.
