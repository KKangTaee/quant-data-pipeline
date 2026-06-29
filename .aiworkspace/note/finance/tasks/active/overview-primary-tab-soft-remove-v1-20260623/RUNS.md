# Overview Primary Tab Soft Remove V1 Runs

## Commands

- `.venv/bin/python -m pytest tests/test_service_contracts.py::OverviewAutomationContractTests::test_overview_dashboard_uses_lazy_selected_deep_tab_rendering tests/test_service_contracts.py::OverviewAutomationContractTests::test_overview_dashboard_primary_selector_excludes_inactive_tabs tests/test_service_contracts.py::OverviewAutomationContractTests::test_overview_dashboard_defaults_unknown_deep_tab_to_market_context -q`
  - Result: failed because local `.venv` does not provide `pytest`.
- `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_dashboard_uses_lazy_selected_deep_tab_rendering tests.test_service_contracts.OverviewAutomationContractTests.test_overview_dashboard_primary_selector_excludes_inactive_tabs tests.test_service_contracts.OverviewAutomationContractTests.test_overview_dashboard_defaults_unknown_deep_tab_to_market_context`
  - Result: RED confirmed. Failures show `Futures Monitor` and `Sector / Industry` still in the Overview selector / renderer and old tab values still resolving to themselves.
- `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_dashboard_uses_lazy_selected_deep_tab_rendering tests.test_service_contracts.OverviewAutomationContractTests.test_overview_dashboard_primary_selector_excludes_inactive_tabs tests.test_service_contracts.OverviewAutomationContractTests.test_overview_dashboard_defaults_unknown_deep_tab_to_market_context`
  - Result: GREEN after removing both labels from `OVERVIEW_DEEP_TAB_OPTIONS` and renderer dispatch.
- `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_dashboard_uses_lazy_selected_deep_tab_rendering tests.test_service_contracts.OverviewAutomationContractTests.test_overview_dashboard_primary_selector_excludes_inactive_tabs tests.test_service_contracts.OverviewAutomationContractTests.test_overview_dashboard_defaults_unknown_deep_tab_to_market_context tests.test_service_contracts.OverviewAutomationContractTests.test_overview_ia_closeout_model_demotes_ops_surfaces_from_primary_tabs`
  - Result: GREEN after aligning the IA closeout model with current primary tabs.
- `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests`
  - Result: PASS, 79 tests.
- `.venv/bin/python -m py_compile app/web/overview_dashboard.py app/web/overview_dashboard_helpers.py`
  - Result: PASS.
- `git diff --check`
  - Result: PASS.
- Browser QA on `http://localhost:8502`
  - Result: PASS. Overview selector shows `Market Context`, `Market Movers`, `Sentiment`, and `Events` only. `Futures Monitor` and `Sector / Industry` are absent from the selector.
  - Screenshot: `/Users/taeho/Project/quant-data-pipeline-worktrees/sub-dev/overview-primary-tab-soft-remove-v1-qa.png` (generated artifact, not for staging).
- Fresh pre-commit verification:
  - `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests`: PASS, 79 tests.
  - `.venv/bin/python -m py_compile app/web/overview_dashboard.py app/web/overview_dashboard_helpers.py`: PASS.
  - `git diff --check`: PASS.
  - Browser selector readback: `["Market Context", "Market Movers", "Sentiment", "Events"]`.
