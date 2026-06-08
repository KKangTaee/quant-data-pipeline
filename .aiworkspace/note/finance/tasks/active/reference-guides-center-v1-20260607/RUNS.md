# Runs

| Time | Command | Result |
|---|---|---|
| 2026-06-07 | `git status --short` | Dirty tree confirmed; unrelated artifacts present. |
| 2026-06-07 | `.venv/bin/python -m unittest tests.test_reference_guides_catalog` | RED: `app.services.reference_guides_catalog` did not exist. |
| 2026-06-07 | `.venv/bin/python -m unittest tests.test_reference_guides_catalog` | GREEN: 3 catalog contract tests passed. |
| 2026-06-07 | `.venv/bin/python -m py_compile app/services/reference_guides_catalog.py app/web/reference_guides.py app/web/streamlit_app.py` | Passed. |
| 2026-06-07 | Browser QA at `http://localhost:8504/guides` | Reference Center default view rendered with task cards, read-only boundary, Portfolio Monitoring naming. Portfolio Selection Journey view preserved existing 1~4 guide. |
| 2026-06-07 | Browser narrow viewport QA `390x900` | Main task cards stacked without text overlap in snapshot. |
| 2026-06-07 | `reference-guides-center-v1-qa-20260607.png` | Generated QA screenshot saved; not staged by default. |
| 2026-06-07 | `.venv/bin/python -m unittest tests.test_reference_guides_catalog tests.test_service_contracts` | 291 tests passed. Existing edgar deprecation warnings only. |
| 2026-06-07 | `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py` | PASS, no hard violations or advisories. |
| 2026-06-07 | `git diff --check` | Passed. |
| 2026-06-07 | Final `.venv/bin/python -m unittest tests.test_reference_guides_catalog tests.test_service_contracts` | 291 tests passed. Existing edgar deprecation warnings only. |
| 2026-06-07 | Final `.venv/bin/python -m py_compile app/services/reference_guides_catalog.py app/web/reference_guides.py app/web/streamlit_app.py` | Passed. |
| 2026-06-07 | Final `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py && git diff --check` | PASS, no violations/advisories and no whitespace errors. |
| 2026-06-07 | `lsof -iTCP:8504 -sTCP:LISTEN -n -P` | No listener remained after temporary QA server shutdown. |
