# Overview Tab Helper Extraction V11-V16 Status

## 2026-06-25

- Started V11-V16 after the user approved the one-entrypoint plus one-helper-per-tab direction.
- V11 audit / target helper structure guard completed.
  - Added a contract test for the helper extraction audit.
  - Recorded the active legacy helper call groups and target helper modules in `HELPER_EXTRACTION_AUDIT.md`.
  - QA passed with focused contract test, Overview contract suite, py_compile, and Browser QA.
- V12 Market Context helper extraction completed.
  - Added `app/web/overview/market_context_helpers.py`.
  - Made `app/web/overview/market_context.py` call semantic helper functions instead of importing `legacy_dashboard.py`.
  - QA passed with TDD red/green check, related contract tests, Overview contract suite, py_compile, and Browser QA.
- V13 Events helper extraction completed.
  - Added `app/web/overview/events_helpers.py`.
  - Made `app/web/overview/events.py` call semantic helper functions instead of importing `legacy_dashboard.py`.
  - QA passed with TDD red/green check, related contract tests, Overview contract suite, py_compile, and Events Browser QA.
- V14 Futures Macro helper extraction completed.
  - Added `app/web/overview/futures_macro_helpers.py`.
  - Made `app/web/overview/futures_macro.py` call semantic helper functions instead of importing `legacy_dashboard.py`.
  - QA passed with TDD red/green check, related contract tests, Overview contract suite, py_compile, and Futures Macro Browser QA.
- V15 Market Movers helper extraction completed.
  - Added `app/web/overview/market_movers_helpers.py`.
  - Made `app/web/overview/market_movers.py` call semantic helper functions instead of importing `legacy_dashboard.py`.
  - QA passed with TDD red/green check, related contract tests, Overview contract suite, py_compile, and Market Movers Browser QA.
- Next step: V16 Sentiment helper extraction and final docs/QA.
