# Runs

- `git status --short`: active task docs와 이전 generated screenshot만 untracked.
- `rg institutional_13f ...docs...`: Institutional Portfolios 코드 / 문서 소유 경계 확인.
- `sed tests/test_institutional_portfolios.py`: 기존 13F parser / service / navigation tests 확인.
- `sed app/services/institutional_portfolios.py`, `finance/loaders/institutional_13f.py`, React TSX/CSS: 현재 payload, loader, UI tab 구조 확인.
- `.venv/bin/python -m unittest tests.test_institutional_portfolios`: 24 tests OK after implementation.
- `.venv/bin/python -m py_compile app/web/institutional_portfolios.py app/services/institutional_portfolios.py finance/loaders/institutional_13f.py finance/loaders/__init__.py finance/data/db/schema.py`: OK.
- `npm run build` in `app/web/streamlit_components/institutional_portfolios_workbench`: OK, updated `component_static`.
- `git diff --check`: OK.
- UI/engine boundary scan: React source has no external fetch; Streamlit UI reads service payload; service uses DB loaders / price loader.
- Local DB migration for QA: added `finance_meta.institutional_13f_holding.ix_report_period_cusip_cik`.
- Browser QA at `http://localhost:8502`: manager workbench rendered; AAPL click showed selected-security detail without stuck loading; chart points rendered; popularity ranking loaded rows for 2026-03-31. Screenshot: `/tmp/institutional-portfolios-ux-detail-ranking-qa.png`.
