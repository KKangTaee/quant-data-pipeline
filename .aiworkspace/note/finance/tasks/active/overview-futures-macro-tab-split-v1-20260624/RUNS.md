# Overview Futures Macro Tab Split V1 Runs

## Commands

- RED focused contract run failed before implementation as expected.
- Focused new contract run passed:
  - `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_dashboard_primary_selector_excludes_inactive_tabs tests.test_service_contracts.OverviewAutomationContractTests.test_overview_dashboard_pill_nav_slug_contract tests.test_service_contracts.OverviewAutomationContractTests.test_overview_dashboard_routes_futures_macro_as_primary_tab tests.test_service_contracts.OverviewAutomationContractTests.test_overview_market_context_loader_excludes_futures_macro_by_default tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_overview_macro_context_cockpit_can_omit_futures_macro_for_fast_entry tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_latest_raw_date_query_uses_ordered_latest_row`
  - Result: OK, 6 tests.
- Overview automation contract class passed:
  - `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests`
  - Result: OK, 84 tests.
- Overview market intelligence contract class passed:
  - `.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests`
  - Result: OK, 52 tests.
- Local timing script after split:
  - light Market Context cockpit default before historical analog opt-out: 1.854s.
  - full Market Context cockpit `include_futures_macro=True`: 7.854s.
  - futures macro `include_validation=False`: 0.209s.
  - futures macro `include_validation=True`: 7.574s.
  - light card ids: `movement`, `breadth`, `sentiment`, `events`, `data`.
  - full card ids: `movement`, `breadth`, `futures`, `sentiment`, `events`, `data`.
- Local timing after historical analog default opt-out:
  - light Market Context cockpit default: 0.522s.
  - Market Context cockpit `include_historical_analog=True`: 1.491s.
  - full cockpit `include_futures_macro=True`, `include_historical_analog=True`: 7.732s.
  - futures macro `include_validation=False`: 0.193s.
  - futures macro `include_validation=True`: 7.494s.
- Final static verification:
  - `git diff --check`
  - Result: OK.
  - `.venv/bin/python -m py_compile app/web/overview_dashboard.py app/web/overview_dashboard_helpers.py app/services/overview_market_intelligence.py`
  - Result: OK.
- Final focused contract run:
  - `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests`
  - Result: OK, 136 tests.
- Browser QA:
  - Streamlit run: `.venv/bin/streamlit run app/web/streamlit_app.py --server.port 8507 --server.headless true --server.address 127.0.0.1`.
  - `Market Context` root page rendered the five primary tabs and no longer contained `과거 유사 맥락 기준 선택` or `Macro 조건 후 결과 변화`.
  - `Futures Macro` tab rendered the stored futures daily macro detail panel after validation load.
  - Screenshot artifact: `overview-futures-macro-tab-split-v1-qa.png`.
