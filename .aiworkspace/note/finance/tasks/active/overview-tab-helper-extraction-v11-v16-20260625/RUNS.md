# Overview Tab Helper Extraction V11-V16 Runs

## V11 Audit / Guard - 2026-06-25

- RED: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_helper_extraction_audit_tracks_target_helper_modules`
  - Result: failed as expected because `HELPER_EXTRACTION_AUDIT.md` did not exist yet.
- GREEN: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_helper_extraction_audit_tracks_target_helper_modules`
  - Result: passed.
- GREEN: `.venv/bin/python -m py_compile app/web/overview/market_context.py app/web/overview/events.py app/web/overview/futures_macro.py app/web/overview/market_movers.py app/web/overview/sentiment.py tests/test_service_contracts.py`
  - Result: passed.
- GREEN: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests`
  - Result: 105 tests passed.
- Browser QA: `http://localhost:8521/?nav=overview`
  - Result: Overview rendered, default Market Context tab visible, console errors 0.
  - Screenshot: `overview-tab-helper-extraction-v11-qa.png` (generated artifact, not committed).

## V12 Market Context Helper Extraction - 2026-06-25

- RED: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_market_context_entrypoint_uses_tab_helper_module`
  - Result: failed as expected because `app/web/overview/market_context_helpers.py` did not exist yet.
- GREEN: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_market_context_entrypoint_uses_tab_helper_module`
  - Result: passed.
- GREEN: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_primary_tab_modules_own_tab_orchestration tests.test_service_contracts.OverviewAutomationContractTests.test_overview_dashboard_renders_macro_context_cockpit_inside_market_context_tab tests.test_service_contracts.OverviewAutomationContractTests.test_overview_dashboard_keeps_deep_tab_guide_out_of_market_context_brief tests.test_service_contracts.OverviewAutomationContractTests.test_overview_market_context_keeps_historical_analog_out_of_default_entry`
  - Result: 4 tests passed.
- GREEN: `.venv/bin/python -m py_compile app/web/overview/market_context.py app/web/overview/market_context_helpers.py tests/test_service_contracts.py`
  - Result: passed.
- GREEN: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests`
  - Result: 106 tests passed.
- Browser QA: `http://localhost:8521/?nav=overview`
  - Result: Overview default Market Context tab rendered, console errors 0.
  - Screenshot: `overview-tab-helper-extraction-v12-market-context-qa.png` (generated artifact, not committed).

## V13 Events Helper Extraction - 2026-06-25

- RED: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_events_entrypoint_uses_tab_helper_module`
  - Result: failed as expected because `app/web/overview/events_helpers.py` did not exist yet.
- GREEN: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_events_entrypoint_uses_tab_helper_module`
  - Result: passed.
- GREEN: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_primary_tab_modules_own_tab_orchestration tests.test_service_contracts.OverviewAutomationContractTests.test_overview_active_tabs_use_domain_component_surfaces tests.test_service_contracts.OverviewAutomationContractTests.test_overview_events_tab_renders_macro_week_lane_before_calendar_filters`
  - Result: 3 tests passed.
- GREEN: `.venv/bin/python -m py_compile app/web/overview/events.py app/web/overview/events_helpers.py tests/test_service_contracts.py`
  - Result: passed.
- GREEN: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests`
  - Result: 107 tests passed.
- Browser QA: `http://localhost:8521/?nav=overview`, switched to `일정 · Events`.
  - Result: Events tab rendered summary lane, macro week lane, detail tabs; console errors 0.
  - Screenshot: `overview-tab-helper-extraction-v13-events-qa.png` (generated artifact, not committed).

## V14 Futures Macro Helper Extraction - 2026-06-25

- RED: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_futures_macro_entrypoint_uses_tab_helper_module`
  - Result: failed as expected because `app/web/overview/futures_macro_helpers.py` did not exist yet.
- GREEN: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_futures_macro_entrypoint_uses_tab_helper_module`
  - Result: passed.
- GREEN: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_primary_tab_modules_own_tab_orchestration tests.test_service_contracts.OverviewAutomationContractTests.test_overview_dashboard_routes_futures_macro_as_primary_tab tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_tab_exposes_daily_refresh_and_cache_reload`
  - Result: 3 tests passed.
- GREEN: `.venv/bin/python -m py_compile app/web/overview/futures_macro.py app/web/overview/futures_macro_helpers.py tests/test_service_contracts.py`
  - Result: passed.
- GREEN: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests`
  - Result: 108 tests passed.
- Browser QA: `http://localhost:8521/?nav=overview`, switched to `선물 매크로 · Futures Macro`.
  - Result: Futures Macro tab rendered action buttons and macro context panel; console errors 0.
  - Screenshot: `overview-tab-helper-extraction-v14-futures-macro-qa.png` (generated artifact, not committed).
