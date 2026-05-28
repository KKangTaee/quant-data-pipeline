# Runs

- 2026-05-28: `uv run python -m py_compile finance/data/market_intelligence.py finance/data/db/schema.py app/jobs/ingestion_jobs.py app/web/streamlit_app.py app/web/overview_dashboard.py app/services/overview_market_intelligence.py tests/test_service_contracts.py` - PASS.
- 2026-05-28: `uv run python -m unittest tests.test_service_contracts.MarketIntelligenceEventCalendarContractTests tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests` - PASS, 18 tests.
- 2026-05-28: Full `uv run python -m unittest tests.test_service_contracts` - PASS, 43 tests.
- 2026-05-28: Browser smoke confirmed Overview Events validation counts and Ingestion Earnings tab Nasdaq cross-check controls render with 0 console errors.
