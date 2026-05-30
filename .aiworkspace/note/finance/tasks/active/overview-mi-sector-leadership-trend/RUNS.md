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
- `uv run python -m unittest tests.test_service_contracts` - 56 tests pass after adding daily intraday group leadership.
- `uv run python -m py_compile app/services/overview_market_intelligence.py app/web/overview_dashboard.py app/web/overview_dashboard_helpers.py` - pass after daily intraday group leadership.
- DB smoke: `SP500 sector daily` returned `price_mode=Intraday Snapshot`, `snapshot_time_utc=2026-05-29 00:32`, 503 returnable rows, 10 group rows, 640 trend rows, and 150 ticker leader rows.
- Browser smoke: restarted Streamlit and verified Overview > Sector / Industry > Daily shows `Effective Price Time=2026-05-29 00:32`, `Price Mode=Intraday Snapshot`, and `Return Window: Previous Close -> 2026-05-29 00:32`; console errors 0.
- `uv run python -m py_compile app/web/overview_dashboard.py app/web/overview_dashboard_helpers.py tests/test_service_contracts.py` - pass after price-basis label and loading UX update.
- `uv run python -m unittest tests.test_service_contracts.OverviewAutomationContractTests tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests` - 31 tests pass.
- `uv run python -m unittest tests.test_service_contracts` - 78 tests pass.
- Browser smoke: `http://localhost:8501` Overview > Sector / Industry shows `Effective EOD Date`, no old `Effective Price Time`, sparse-date detail present, no persistent completion status, no horizontal overflow, and no app traceback. Streamlit telemetry fetch errors were observed in console but no app-rendering exception appeared.
