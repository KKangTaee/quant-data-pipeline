# Runs

- 2026-05-28: `uv run python -m py_compile app/services/overview_market_intelligence.py app/web/overview_dashboard.py tests/test_service_contracts.py` - PASS.
- 2026-05-28: `uv run python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests` - PASS after refresh diagnostics additions.
- 2026-05-28: Browser smoke on `http://localhost:8501` confirmed Market Movers shows `Stale`, refresh recommendation, and Returnable Coverage diagnostics card.
