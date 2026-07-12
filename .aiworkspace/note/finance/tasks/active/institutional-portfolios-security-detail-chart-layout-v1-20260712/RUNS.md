# Institutional Portfolios Security Detail Chart Layout V1 Runs

## 2026-07-12

- RED:
  - `.venv/bin/python -m unittest tests.test_institutional_portfolios.InstitutionalPortfoliosNavigationTests.test_selected_security_chart_supports_hover_candles_guides_and_pan_controls tests.test_institutional_portfolios.InstitutionalPortfoliosNavigationTests.test_selected_security_detail_uses_two_row_chart_and_scrollable_holder_layout`
  - Expected failure before implementation: missing `ip-chart-market-strip` / layout contract strings.
- GREEN:
  - `.venv/bin/python -m unittest tests.test_institutional_portfolios.InstitutionalPortfoliosNavigationTests.test_selected_security_chart_supports_hover_candles_guides_and_pan_controls tests.test_institutional_portfolios.InstitutionalPortfoliosNavigationTests.test_selected_security_detail_uses_two_row_chart_and_scrollable_holder_layout` -> OK, 2 tests.
- Focused regression:
  - `.venv/bin/python -m unittest tests.test_institutional_portfolios` -> OK, 32 tests.
- Compile / build:
  - `.venv/bin/python -m py_compile app/web/institutional_portfolios.py app/services/institutional_portfolios.py app/web/streamlit_app.py finance/data/institutional_13f.py finance/loaders/institutional_13f.py finance/data/db/schema.py` -> OK.
  - `npm run build` in `app/web/streamlit_components/institutional_portfolios_workbench/` -> OK.
- Hygiene:
  - `git diff --check` -> OK.
  - UI / engine boundary grep found no UI direct fetch; matches were SEC external-link strings in `app/services/institutional_portfolios.py`.
- Browser QA:
  - Streamlit started on `http://localhost:8530/institutional-portfolios`.
  - Confirmed React workbench loads with stored SEC 13F snapshot.
  - Opened `종목 분석 > 종목 상세`, selected visible KO top holding, and confirmed selected security card, `현재 선택한 기관 포트폴리오 기준`, stored price chart, volume strip, chart navigator, and `보유 기관 리스트` DOM.
  - Saved QA screenshot: `institutional-portfolios-security-detail-chart-layout-qa.png` (generated artifact, not for commit).
