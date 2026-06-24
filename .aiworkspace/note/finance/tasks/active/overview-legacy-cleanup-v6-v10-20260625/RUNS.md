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
