# Overview Nav Internal Lazy Load V1 Runs

## Commands

- `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_dashboard_primary_selector_uses_internal_pill_widget tests.test_service_contracts.OverviewAutomationContractTests.test_overview_dashboard_pill_nav_slug_contract tests.test_service_contracts.OverviewAutomationContractTests.test_overview_dashboard_defers_default_market_context_until_user_runs_it`
  - Result: RED confirmed. Current code still rendered anchor HTML and did not expose lazy-load gate helpers.
- `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_dashboard_primary_selector_uses_internal_pill_widget`
  - Result: RED confirmed after user supplied underline-tab visual target. Current CSS still had rounded pill/card styling.
- `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_dashboard_primary_selector_uses_internal_pill_widget`
  - Result: GREEN after replacing pill/card CSS with scoped text-tab underline CSS.
- `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_dashboard_primary_selector_uses_internal_pill_widget tests.test_service_contracts.OverviewAutomationContractTests.test_overview_dashboard_pill_nav_slug_contract tests.test_service_contracts.OverviewAutomationContractTests.test_overview_dashboard_defers_default_market_context_until_user_runs_it`
  - Result: GREEN. Internal `st.pills` selector, slug compatibility, and first-load Market Context lazy gate contracts all pass.
- `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_dashboard_primary_selector_uses_internal_pill_widget`
  - Result: RED confirmed for dark-theme inactive-tab readability after Browser QA showed inactive labels were too dim.
- `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_dashboard_primary_selector_uses_internal_pill_widget`
  - Result: GREEN after changing inactive tab color to use Streamlit `var(--text-color)`.
- Browser QA on `http://localhost:8502/`
  - Result: PASS. Fresh entry shows text tabs, no `overview_tab` anchors, no heavy Market Context body, and `시장 맥락 불러오기`.
  - Result: PASS. Clicking `변동 종목 · Market Movers` keeps one browser tab, keeps URL `http://localhost:8502/`, and shows Market Movers content.
  - Screenshots: `overview-nav-text-tabs-v1-gate-qa.png`, `overview-nav-text-tabs-v1-market-movers-qa.png` are local generated artifacts only.
- `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests`
  - Result: GREEN, 82 tests.
- `.venv/bin/python -m py_compile app/web/overview_dashboard.py`
  - Result: PASS.
- `git diff --check`
  - Result: PASS.
