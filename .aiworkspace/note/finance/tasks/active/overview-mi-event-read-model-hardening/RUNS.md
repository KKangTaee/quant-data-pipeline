# Runs

- 2026-05-28: `uv run python -m py_compile app/services/overview_market_intelligence.py app/web/overview_dashboard.py tests/test_service_contracts.py` - PASS.
- 2026-05-28: `uv run python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests` - PASS, 8 tests.
- 2026-05-28: Full `uv run python -m unittest tests.test_service_contracts` - PASS, 40 tests.
