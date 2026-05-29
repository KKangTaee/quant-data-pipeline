# Runs

- `uv run python -m py_compile app/services/overview_market_intelligence.py app/web/overview_dashboard.py app/web/overview_dashboard_helpers.py` - pass.
- `uv run python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests` - 14 tests pass.
- `uv run python -m unittest tests.test_service_contracts` - 56 tests pass.
- DB smoke: `SP500 daily` produced 5 ranking rows / 105 trend rows; `TOP1000 weekly` 5 / 65; `TOP2000 monthly` 5 / 30.
- Browser smoke: `http://localhost:8501` Overview > Sector / Industry renders controls and two Vega charts with 0 console errors in a fresh tab.
