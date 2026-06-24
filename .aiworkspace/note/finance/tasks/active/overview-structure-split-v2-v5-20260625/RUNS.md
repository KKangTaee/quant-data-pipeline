# Overview Structure Split V2-V5 Runs

## V2 Tab Orchestration Split - 2026-06-25

- RED: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_primary_tab_modules_own_tab_orchestration`
  - Result: failed because `market_context.py` still delegated directly to `_legacy._render_overview_market_context_tab()`.
- GREEN focused: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_primary_tab_modules_own_tab_orchestration`
  - Result: passed.
- Compile: `.venv/bin/python -m py_compile app/web/overview/market_context.py app/web/overview/market_movers.py app/web/overview/futures_macro.py app/web/overview/sentiment.py app/web/overview/events.py tests/test_service_contracts.py`
  - Result: passed.
- Overview contract: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests`
  - Result: passed 89 tests.
- Browser QA: Streamlit `http://localhost:8521/?overview_tab=market-context`
  - Result: Market Context rendered; Sentiment and Events tab switches rendered; browser console reported 0 errors. Screenshot: `overview-structure-split-v2-qa.png`.

## V3 Component Surface Split - 2026-06-25

- RED: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_component_surfaces_are_split_by_domain tests.test_service_contracts.OverviewAutomationContractTests.test_overview_active_tabs_use_domain_component_surfaces`
  - Result: failed because `app.web.overview.components.*` modules did not exist and active tabs still used legacy component references.
- GREEN focused: same command
  - Result: passed.
- Compile: `.venv/bin/python -m py_compile app/web/overview/components/__init__.py app/web/overview/components/layout.py app/web/overview/components/market_context.py app/web/overview/components/events.py app/web/overview/page.py app/web/overview/market_context.py app/web/overview/events.py tests/test_service_contracts.py`
  - Result: passed.
- Overview contract: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests`
  - Result: passed 91 tests.
- Browser QA: Streamlit `http://localhost:8521/?overview_tab=market-context`
  - Result: Market Context rendered; Events tab rendered through the component surface; screenshot: `overview-structure-split-v3-qa.png`.

## V4 Service Surface Split - 2026-06-25

- RED: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_service_surfaces_are_split_by_domain tests.test_service_contracts.OverviewAutomationContractTests.test_overview_dashboard_helpers_use_domain_service_surfaces`
  - Result: failed because `app.services.overview.*` modules did not exist and `overview_dashboard_helpers.py` still imported `app.services.overview_market_intelligence` directly.
- GREEN focused: same command
  - Result: passed.
- Compile: `.venv/bin/python -m py_compile app/services/overview/__init__.py app/services/overview/data_health.py app/services/overview/events.py app/services/overview/market_context.py app/services/overview/market_movers.py app/services/overview/sentiment.py app/web/overview_dashboard_helpers.py tests/test_service_contracts.py`
  - Result: passed.
- Overview contract: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests`
  - Result: passed 93 tests.
- Browser QA: Streamlit `http://localhost:8521/?overview_tab=market-context`
  - Result: Market Context rendered; Events rendered after tab switch; current browser console reported 0 errors. Screenshot: `overview-structure-split-v4-qa.png`.
