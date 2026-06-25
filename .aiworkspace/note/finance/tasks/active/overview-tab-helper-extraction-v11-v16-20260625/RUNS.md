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
