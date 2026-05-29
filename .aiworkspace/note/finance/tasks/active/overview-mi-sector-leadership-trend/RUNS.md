# Runs

- `uv run python -m py_compile app/services/overview_market_intelligence.py app/web/overview_dashboard.py app/web/overview_dashboard_helpers.py` - pass.
- `uv run python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests` - 14 tests pass.
- `uv run python -m unittest tests.test_service_contracts` - 56 tests pass.
- DB smoke: `SP500 daily` produced 5 ranking rows / 105 trend rows; `TOP1000 weekly` 5 / 65; `TOP2000 monthly` 5 / 30.
- Browser smoke: `http://localhost:8501` Overview > Sector / Industry renders controls and two Vega charts with 0 console errors in a fresh tab.
- `uv run python -m unittest tests.test_service_contracts` - 56 tests pass after Trend 3M / 6M / 1Y and ticker-leader snapshot additions.
- `uv run python -m py_compile app/services/overview_market_intelligence.py app/web/overview_dashboard.py app/web/overview_dashboard_helpers.py` - pass after UI chart additions.
- DB smoke: `SP500 monthly` returned 10 ranking rows / 120 trend rows / 190 ticker leader rows with `trend_window_label=Last 1Y`.
- Browser smoke: restarted Streamlit on `http://localhost:8501`; Overview > Sector / Industry shows Trend Groups multiselect and Positive Group Detail bar/donut charts. Current page console errors: 0.
