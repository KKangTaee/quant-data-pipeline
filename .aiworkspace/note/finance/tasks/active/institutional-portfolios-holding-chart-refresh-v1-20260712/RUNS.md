# Institutional Portfolios Holding Chart Refresh V1 Runs

## 2026-07-12

- `.venv/bin/python -m unittest tests.test_institutional_portfolios` initially failed on missing curated symbol resolver and missing price collection event boundary.
- Actual DB check showed Berkshire KO/BAC/CVX/OXY/GOOGL rows lacked `holding_symbol`, while `finance_price.nyse_price_history` already had daily rows for these symbols.
- Actual DB check also showed generic symbol lookup for `KO` could return polluted map rows, so curated symbols now prefer curated CUSIP lookup first.
- `.venv/bin/python -m unittest tests.test_institutional_portfolios` passed after implementation.
- `.venv/bin/python -m py_compile app/services/institutional_portfolios.py app/web/institutional_portfolios.py finance/loaders/institutional_13f.py finance/data/institutional_13f.py` passed.
- `npm run build` passed in `app/web/streamlit_components/institutional_portfolios_workbench/`.
- `git diff --check` passed.
- Browser QA on `http://localhost:8526/institutional-portfolios` confirmed KO selected-security chart renders from stored DB prices and holder list shows 100 latest-filing holders.
