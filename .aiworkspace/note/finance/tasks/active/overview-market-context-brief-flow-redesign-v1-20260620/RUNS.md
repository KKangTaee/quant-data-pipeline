# Overview Market Context Brief Flow Redesign V1 Runs

| Time | Command | Result |
|---|---|---|
| 2026-06-20 | Read AGENTS / docs / project map / data maps | Pass |
| 2026-06-20 | `uv run --with pytest python -m pytest tests/test_service_contracts.py -q -k "overview_market_context or historical_analog_html or source_confidence"` | RED failed on intended UX contracts, then passed after implementation |
| 2026-06-20 | `uv run --with pytest python -m pytest tests/test_service_contracts.py -q -k "passes_historical_analog_controls"` | RED failed on one-render stale selected-control reflection, then passed after dashboard reload fix |
| 2026-06-20 | `git diff --check` | Pass |
| 2026-06-20 | `uv run python -m py_compile app/services/overview_market_context_analog.py app/services/overview_market_intelligence.py app/web/overview_ui_components.py app/web/overview_dashboard_helpers.py finance/loaders/macro.py finance/loaders/sentiment.py` | Pass |
| 2026-06-20 | `uv run --with pytest python -m pytest tests/test_service_contracts.py -q` | Pass: 365 passed, 3 upstream deprecation warnings |
| 2026-06-20 | `uv run streamlit run app/web/streamlit_app.py --server.port 8525 --server.headless true` + Browser QA | Pass: latest, selected as-of 2026-06-17, 20D, monthly, source ledger, refresh assist, and forbidden copy checked |
