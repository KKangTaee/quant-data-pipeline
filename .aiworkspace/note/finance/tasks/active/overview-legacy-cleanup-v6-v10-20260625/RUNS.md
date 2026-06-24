# Overview Legacy Cleanup V6-V10 Runs

## V6 Legacy Usage Audit - 2026-06-25

- RED: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_legacy_cleanup_audit_tracks_active_retained_and_removable_buckets`
  - Result: failed because `LEGACY_USAGE_AUDIT.md` was still a placeholder without active / retained / removable buckets.
- GREEN focused: same command
  - Result: passed.
- Compile: `.venv/bin/python -m py_compile tests/test_service_contracts.py`
  - Result: passed.
- Overview contract: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests`
  - Result: passed 98 tests.
- Browser QA: Streamlit `http://localhost:8521/?overview_tab=market-context`
  - Result: Market Context rendered with current session copy `장 마감 기준 시장 브리프`; Events rendered after tab switch; current browser console reported 0 errors. Screenshot: `overview-legacy-cleanup-v6-qa.png`.

## V7 Navigation Surface Extraction - 2026-06-25

- RED: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_navigation_surface_owns_selector_entrypoints tests.test_service_contracts.OverviewAutomationContractTests.test_overview_page_uses_navigation_surface_instead_of_legacy_selector_body tests.test_service_contracts.OverviewAutomationContractTests.test_overview_dashboard_primary_selector_uses_internal_pill_widget`
  - Result: failed because `app/web/overview/navigation.py` did not exist and `page.py` still called legacy selector helpers.
- GREEN focused: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_navigation_surface_owns_selector_entrypoints tests.test_service_contracts.OverviewAutomationContractTests.test_overview_page_uses_navigation_surface_instead_of_legacy_selector_body tests.test_service_contracts.OverviewAutomationContractTests.test_overview_dashboard_primary_selector_uses_internal_pill_widget tests.test_service_contracts.OverviewAutomationContractTests.test_overview_dashboard_dispatches_only_selected_deep_tab tests.test_service_contracts.OverviewAutomationContractTests.test_overview_dashboard_defaults_unknown_deep_tab_to_market_context tests.test_service_contracts.OverviewAutomationContractTests.test_overview_dashboard_pill_nav_slug_contract`
  - Result: passed 6 tests.
- Compile: `.venv/bin/python -m py_compile app/web/overview/navigation.py app/web/overview/page.py app/web/overview/legacy_dashboard.py tests/test_service_contracts.py`
  - Result: passed.
- Overview contract: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests`
  - Result: passed 100 tests.
- Browser QA: Streamlit `http://localhost:8521/?overview_tab=market-context`
  - Result: Market Context rendered; Futures Macro tab switched through the navigation surface; current browser console reported 0 errors. Screenshot: `overview-legacy-cleanup-v7-qa.png`.

## V8 IA Read Model Service Extraction - 2026-06-25

- RED: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_service_surfaces_are_split_by_domain tests.test_service_contracts.OverviewAutomationContractTests.test_overview_dashboard_helpers_use_domain_service_surfaces tests.test_service_contracts.OverviewAutomationContractTests.test_overview_ia_closeout_body_lives_in_service_surface`
  - Result: failed because `app/services/overview/ia.py` did not exist and `overview_dashboard_helpers.py` still owned the `load_overview_ia_closeout_model` body.
- GREEN focused: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_service_surfaces_are_split_by_domain tests.test_service_contracts.OverviewAutomationContractTests.test_overview_dashboard_helpers_use_domain_service_surfaces tests.test_service_contracts.OverviewAutomationContractTests.test_overview_ia_closeout_body_lives_in_service_surface tests.test_service_contracts.OverviewAutomationContractTests.test_overview_ia_closeout_model_demotes_ops_surfaces_from_primary_tabs`
  - Result: passed 4 tests.
- Compile: `.venv/bin/python -m py_compile app/services/overview/ia.py app/web/overview_dashboard_helpers.py tests/test_service_contracts.py`
  - Result: passed.
- Overview contract: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests`
  - Result: passed 101 tests.
- Browser QA: Streamlit `http://localhost:8521/?overview_tab=market-context`
  - Result: Market Context rendered; Events rendered after tab switch; current browser console reported 0 errors. Screenshot: `overview-legacy-cleanup-v8-qa.png`.
