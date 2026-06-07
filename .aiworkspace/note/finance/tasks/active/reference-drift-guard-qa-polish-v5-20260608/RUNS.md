# Reference Drift Guard / QA Polish V5 Runs

Status: Active
Date: 2026-06-08

## Runs

- `.venv/bin/python -m unittest tests.test_reference_contextual_help`
  - RED result: failed with `ImportError` for missing `build_reference_contextual_help_drift_report`.
- `.venv/bin/python -m unittest tests.test_reference_contextual_help`
  - GREEN result: 4 tests passed after service drift report and copy polish.
- `.venv/bin/python -m unittest tests.test_reference_contextual_help tests.test_reference_glossary_catalog tests.test_reference_guides_catalog`
  - Result: 12 tests passed.
- Browser QA on `http://localhost:8509/selected-portfolio-dashboard`
  - Result: `Reference help - Operations > Portfolio Monitoring` expander opened.
  - Confirmed guide focus text: `제품 흐름 / Operations / Portfolio Monitoring, 문제 해결 / stale scenario`.
  - Confirmed `&gt;` was not present and Guides / Glossary links pointed to `/guides` and `/glossary`.
  - Screenshot artifact: `reference-drift-guard-v5-qa-20260608.png` (generated, not committed).
  - Note: in-app browser screenshot capture timed out twice, so the image artifact was captured with the fallback Playwright QA session after the DOM checks passed.
- `.venv/bin/python -m unittest tests.test_reference_contextual_help tests.test_reference_glossary_catalog tests.test_reference_guides_catalog tests.test_service_contracts`
  - Result: 300 tests passed.
  - Known warnings: edgar deprecation warnings and Streamlit `No runtime found` cache warnings during tests.
- `.venv/bin/python -m py_compile app/services/reference_contextual_help.py app/web/reference_contextual_help.py tests/test_reference_contextual_help.py`
  - Result: passed.
- `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py`
  - Result: PASS, hard violations none, advisories none.
- `git diff --check`
  - Result: passed.
- `lsof -tiTCP:8509 -sTCP:LISTEN || true`
  - Result: no listener after QA server shutdown.
