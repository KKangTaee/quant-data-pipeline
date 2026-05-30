# Runs

- `uv lock` - passed; added direct `beautifulsoup4` dependency metadata.
- `uv run python -m py_compile finance/data/market_intelligence.py app/jobs/ingestion_jobs.py app/services/overview_market_intelligence.py app/web/overview_dashboard_helpers.py app/web/overview_dashboard.py app/web/streamlit_app.py tests/test_service_contracts.py` - passed.
- `uv run python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests tests.test_service_contracts.MarketIntelligenceEventCalendarContractTests` - passed, 11 tests.
- `uv run python -m unittest tests.test_service_contracts` - passed, 36 tests.
- `git diff --check` - passed.
- `run_collect_fomc_calendar(years=(2026, 2027))` - passed; wrote 16 rows from the official Fed page.
- `build_market_events_snapshot(today=date(2026, 5, 28), horizon_days=540)` - passed; returned 12 upcoming rows with next event `2026-06-17`.
- Browser smoke at `http://localhost:8501` - passed; Overview Events shows next FOMC date / stored rows and Ingestion shows `Overview Market Event Calendar` with `Collect FOMC Calendar`.
