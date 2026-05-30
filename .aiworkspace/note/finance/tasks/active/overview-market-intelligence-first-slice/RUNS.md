# Runs

| Time | Command | Result |
| --- | --- | --- |
| 2026-05-28 | Scope lock docs created | Pending implementation verification. |
| 2026-05-28 | `uv run python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests` | PASS, 3 tests. |
| 2026-05-28 | `uv run python -m py_compile app/services/overview_market_intelligence.py app/web/overview_dashboard.py app/web/overview_dashboard_helpers.py tests/test_service_contracts.py` | PASS. |
| 2026-05-28 | local DB smoke for market movers / group leadership service | PASS, effective date `2026-05-18`, raw latest `2026-05-19`. |
| 2026-05-28 | `uv run python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py` | PASS. |
| 2026-05-28 | `git diff --check` | PASS. |
| 2026-05-28 | `uv run python -m unittest tests.test_service_contracts` | PASS, 26 tests. |
| 2026-05-28 | Streamlit browser smoke at `http://localhost:8501/` | PASS: Market Movers, Sector / Industry, Events, and Candidate Ops tabs render. Initial `/overview` path produced Streamlit fallback 404 logs only. |
