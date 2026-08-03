# Runs

## 2026-08-04

- Read-only comparison of current month-end and intramonth snapshots.
- Read-only review of `WEB_APP_RUN_HISTORY.jsonl` manual refresh durations and outcomes.
- Source inspection of freshness, refresh orchestration, observed-state domain, Overview service,
  React workbench and related tests.
- TDD RED: anchor provenance assertions failed because the three fields were absent.
- TDD GREEN: `python -m pytest tests/test_economic_cycle_observed_state_v1.py -q` passed 14 tests.
- TDD RED: five service/freshness assertions failed for missing provenance and date fields.
- TDD GREEN: focused service/freshness suite passed 40 tests.
- React RED: six assertions failed for checkpoint, transition, freshness and ribbon contracts.
- React GREEN/build: `npm test -- --run && npm run build` passed 8 tests and emitted the
  production `component_static` bundle.
- Integrated Python verification:
  `.venv/bin/python -m pytest tests/test_economic_cycle_observed_state_v1.py tests/test_economic_cycle_freshness.py tests/test_economic_cycle_service.py tests/test_economic_cycle_refresh.py tests/test_market_context_economic_cycle.py -q`
  passed 89 tests with three third-party `edgar` deprecation warnings.
- Static verification: `py_compile` and `git diff --check` exited successfully.
- Browser QA on a clean temporary Streamlit process verified 6M / 3M / 1M / current labels,
  current contraction, anchor/target explanatory copy, four-color legend, 12 month items,
  visible focus tooltip and the unchanged asset checkpoint section.
- QA screenshot: `economic-cycle-usability-followup-v2-qa.png` (generated artifact, not staged).
- Restarted the existing port 8503 local Streamlit process so the open page loads the new bundle;
  no DB refresh or provider collection was triggered.
- A direct `.venv/bin/pytest` invocation was discarded because its entry-point path did not add
  the repository root to `sys.path`; all recorded verification used `.venv/bin/python -m pytest`.
- Code review found that `source_collected_at` had been over-labeled as a generic last check.
  TDD RED produced two Python failures and one React failure; the corrected
  `last_successful_collection_at` / `마지막 성공 수집` contract passed 40 Python and 8 React tests.
- Review suggestion to restore all monthly points on the map was not applied because it conflicts
  with the approved 6M / 3M / 1M / current-only map; the legend now says `실제 핵심 시점 경로`.
