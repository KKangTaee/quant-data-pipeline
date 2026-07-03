# Runs

## Phase 0 - 2026-07-03

- RED: `uv run python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_movers_react_pilot_contract_defines_payload_and_actions`
  - Result: failed as expected with missing `build_market_movers_react_workbench_payload` import.
- GREEN: `uv run python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_movers_react_pilot_contract_defines_payload_and_actions`
  - Result: passed.
- `uv run python -m py_compile app/web/overview/market_movers_helpers.py`
  - Result: passed.
- `git diff --check`
  - Result: passed.

## Phase 1 - 2026-07-03

- RED: `uv run python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_movers_react_component_scaffold_keeps_streamlit_fallback`
  - Result: failed as expected with missing `app.web.overview.market_movers_react_component`.
- GREEN: `uv run python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_movers_react_component_scaffold_keeps_streamlit_fallback`
  - Result: passed.
- `uv run python -m py_compile app/web/overview/market_movers_react_component.py app/web/overview/market_movers_helpers.py`
  - Result: passed.
- `git diff --check`
  - Result: passed.
