# Institutional Portfolios Selection Loading V1 Runs

- 2026-07-09: Started local Streamlit on port 8531 for diagnosis.
- 2026-07-09: Opened Institutional Portfolios in in-app browser. Direct `/institutional-portfolios` route displayed underlying workbench plus Streamlit `Page not found` modal; this is a QA navigation artifact to avoid in final verification.
- 2026-07-09: Timed read paths: manager choices 0.020s; watchlist portfolio bundle/payload about 0.010s/0.001s; reverse lookup `AAPL`, `APPLE`, `037833100` about 10.1s each.
- 2026-07-10 KST: After SQL/index optimization, reverse lookup timings measured around `AAPL` 0.294s, `037833100` 0.125s, `APPLE` 0.277s.
- 2026-07-10 KST: `.venv/bin/python -m unittest tests.test_institutional_portfolios` passed, 18 tests.
- 2026-07-10 KST: `.venv/bin/python -m py_compile app/web/institutional_portfolios.py app/services/institutional_portfolios.py finance/loaders/institutional_13f.py finance/loaders/__init__.py finance/data/db/schema.py` passed.
- 2026-07-10 KST: `npm run build` passed for `app/web/streamlit_components/institutional_portfolios_workbench`.
- 2026-07-10 KST: `git diff --check` passed.
- 2026-07-10 KST: Browser QA on `http://localhost:8531` via Workspace nav confirmed no Runtime / Build text, watchlist managers show stored report periods, click loading banner appears, and repeated Baupost / Pershing / Berkshire / Appaloosa selections settle without endless loading.
