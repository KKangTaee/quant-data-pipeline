# Runs

- 2026-05-28: `uv run python -m py_compile app/services/overview_market_intelligence.py app/web/overview_dashboard.py app/web/streamlit_app.py app/jobs/ingestion_jobs.py finance/data/market_intelligence.py tests/test_service_contracts.py` - PASS.
- 2026-05-28: `uv run python -m unittest tests.test_service_contracts` - PASS, 43 tests.
- 2026-05-28: `uv run python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py` - PASS, hard violations 0 and advisories 0.
- 2026-05-28: `git diff --check` - PASS.
- 2026-05-28: Browser smoke at `http://localhost:8501` - Market Movers, Sector / Industry, and Events production UX rendered; console errors 0. Remaining warnings were benign Vega `fit-x` sizing warnings for fixed/discrete chart layout.
