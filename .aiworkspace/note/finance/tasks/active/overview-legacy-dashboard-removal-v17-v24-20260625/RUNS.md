# Overview Legacy Dashboard Removal V17-V24 Runs

## V17 Audit / Guard - 2026-06-25

- RED: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_legacy_dashboard_removal_audit_tracks_phase_targets`
  - Result: failed as expected because `LEGACY_DASHBOARD_REMOVAL_AUDIT.md` did not exist yet.
- GREEN: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_legacy_dashboard_removal_audit_tracks_phase_targets`
  - Result: passed.
- GREEN: `.venv/bin/python -m py_compile tests/test_service_contracts.py`
  - Result: passed.
- GREEN: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests`
  - Result: 111 tests passed.

## V18 Session / Banner Helper Extraction - 2026-06-25

- RED: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_page_uses_session_helper_instead_of_legacy_dashboard`
  - Result: failed as expected because `app/web/overview/session_helpers.py` did not exist yet.
- GREEN: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_page_uses_session_helper_instead_of_legacy_dashboard ...test_snapshot_status_labels_sparse_eod_date`
  - Result: 7 focused session / snapshot tests passed.
- GREEN: `.venv/bin/python -m py_compile app/web/overview/session_helpers.py app/web/overview/page.py app/web/overview/market_context_helpers.py tests/test_service_contracts.py`
  - Result: passed.
- GREEN: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests`
  - Result: 112 tests passed.
- Browser QA: `http://localhost:8521/?nav=overview`
  - Result: Overview / 미국장 session banner / Market Context rendered.
  - Screenshot: `overview-legacy-dashboard-removal-v18-session-qa.png`.
  - Current-page console: 0 errors.

## V19 Market Context Helper Extraction - 2026-06-25

- RED: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_market_context_entrypoint_uses_tab_helper_module`
  - Result: failed as expected because `market_context_helpers.py` still imported `legacy_dashboard`.
- GREEN: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_market_context_entrypoint_uses_tab_helper_module ...test_overview_market_context_copy_uses_korean_summary_first_language`
  - Result: 3 focused Market Context tests passed.
- GREEN: `.venv/bin/python -m py_compile app/web/overview/market_context_helpers.py tests/test_service_contracts.py`
  - Result: passed.
- GREEN: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests`
  - Result: 112 tests passed.
- GREEN: `rg -n "legacy_dashboard|_legacy\\." app/web/overview/market_context_helpers.py app/web/overview/market_context.py`
  - Result: no matches.
- Browser QA: `http://localhost:8521/?nav=overview`
  - Result: Market Context and `필요 자료 보강` expander rendered.
  - Screenshot: `overview-legacy-dashboard-removal-v19-market-context-qa.png`.
  - Current-page console: 0 errors.

## V20 Events Helper Extraction - 2026-06-25

- RED: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_events_entrypoint_uses_tab_helper_module`
  - Result: failed as expected because `events_helpers.py` still imported `legacy_dashboard`.
- GREEN: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_events_entrypoint_uses_tab_helper_module ...test_overview_active_tabs_use_domain_component_surfaces`
  - Result: 3 focused Events / component tests passed.
- GREEN: `.venv/bin/python -m py_compile app/web/overview/events_helpers.py tests/test_service_contracts.py`
  - Result: passed.
- GREEN: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests`
  - Result: 112 tests passed.
- GREEN: `rg -n "legacy_dashboard|_legacy\\." app/web/overview/events_helpers.py app/web/overview/events.py`
  - Result: no matches.
- Browser QA: `http://localhost:8521/?nav=overview`, Events tab.
  - Result: Events summary, warning strip, view filters, and Agenda tab rendered.
  - Screenshot: `overview-legacy-dashboard-removal-v20-events-qa.png`.
  - Current-page console: 0 errors.

## V21 Sentiment Helper Extraction - 2026-06-25

- RED: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_sentiment_entrypoint_uses_tab_helper_module`
  - Result: failed as expected because `sentiment_helpers.py` still imported `legacy_dashboard`.
- GREEN: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_sentiment_entrypoint_uses_tab_helper_module`
  - Result: passed.
- GREEN: `.venv/bin/python -m py_compile app/web/overview/sentiment_helpers.py tests/test_service_contracts.py`
  - Result: passed.
- GREEN: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests`
  - Result: 112 tests passed.
- GREEN: `rg -n "legacy_dashboard|_legacy\\." app/web/overview/sentiment_helpers.py app/web/overview/sentiment.py`
  - Result: no matches.
- Browser QA: `http://localhost:8521/?nav=overview`, Sentiment tab.
  - Result: sentiment analysis panel, 6-step reading flow, status cards, driver cards, learning notes, and detail tabs rendered.
  - Screenshot: `overview-legacy-dashboard-removal-v21-sentiment-qa.png`.
  - Current-page console: 0 errors, 12 warnings.

## V22 Market Movers Helper Extraction - 2026-06-25

- RED: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_market_movers_entrypoint_uses_tab_helper_module`
  - Result: failed as expected because `market_movers_helpers.py` still imported `legacy_dashboard`.
- GREEN: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_market_movers_entrypoint_uses_tab_helper_module`
  - Result: passed.
- GREEN: `.venv/bin/python -m py_compile app/web/overview/market_movers_helpers.py tests/test_service_contracts.py`
  - Result: passed.
- GREEN: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests`
  - Result: 112 tests passed.
- GREEN: `rg -n "legacy_dashboard|_legacy\\." app/web/overview/market_movers_helpers.py app/web/overview/market_movers.py`
  - Result: no matches.
- Browser QA: `http://localhost:8521/?nav=overview`, Market Movers tab.
  - Result: controls, data refresh bar, snapshot meta strip, rank/chart area, table, and Why It Moved section rendered.
  - Screenshot: `overview-legacy-dashboard-removal-v22-market-movers-qa.png`.
  - Current-page console: 0 errors, 12 warnings.

## V23 Futures Macro Helper Extraction - 2026-06-25

- RED: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_futures_macro_entrypoint_uses_tab_helper_module ...test_futures_macro_tab_exposes_daily_refresh_and_cache_reload`
  - Result: failed as expected because `futures_macro_helpers.py` still bridged into `legacy_dashboard`.
- GREEN: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_futures_macro_entrypoint_uses_tab_helper_module ...test_futures_weekly_flow_model_ranks_driver_and_supports`
  - Result: 12 focused Futures Macro / futures helper tests passed.
- GREEN: `.venv/bin/python -m py_compile app/web/overview/futures_macro_helpers.py tests/test_service_contracts.py`
  - Result: passed.
- GREEN: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests`
  - Result: 112 tests passed.
- GREEN: `rg -n "legacy_dashboard|_legacy\\." app/web/overview/futures_macro_helpers.py app/web/overview/futures_macro.py`
  - Result: no matches.
- Browser QA: `http://localhost:8521/?nav=overview`, Futures Macro tab.
  - Result: action buttons, macro brief, weekly flow, score lane, and evidence/raw data disclosure rendered.
  - Screenshot: `overview-legacy-dashboard-removal-v23-futures-macro-qa.png`.
  - Current-page console: 0 errors, 12 warnings.

## V24 Compatibility Wrapper Cleanup / Legacy File Deletion - 2026-06-25

- RED: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_legacy_dashboard_removal_audit_tracks_phase_targets`
  - Result: failed as expected while `app/web/overview/legacy_dashboard.py` still existed.
- GREEN: `.venv/bin/python -m py_compile app/web/overview_dashboard.py app/web/overview/market_context_helpers.py tests/test_service_contracts.py`
  - Result: passed.
- GREEN: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests`
  - Result: 112 tests passed.
- GREEN: `rg -n "from app\\.web\\.overview import legacy_dashboard|import legacy_dashboard|_legacy_dashboard|_legacy\\." app tests`
  - Result: no active app imports; remaining matches are negative contract strings in tests.
- Browser QA: `http://localhost:8521/?nav=overview`, Overview final pass.
  - Result: refreshed the app after deleting `legacy_dashboard.py`; Futures Macro and Market Context rendered with current wrapper imports.
  - Screenshot: `overview-legacy-dashboard-removal-v24-final-qa.png`.
  - Current-page console: 0 errors, 12 warnings.
