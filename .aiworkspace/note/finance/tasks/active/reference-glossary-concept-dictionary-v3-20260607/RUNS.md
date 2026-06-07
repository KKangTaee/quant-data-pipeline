# Runs

| Date | Command | Result |
|---|---|---|
| 2026-06-07 | `.venv/bin/python -m unittest tests.test_reference_glossary_catalog` | RED: `app.services.reference_glossary_catalog` did not exist. |
| 2026-06-07 | `.venv/bin/python -m unittest tests.test_reference_glossary_catalog tests.test_reference_guides_catalog` | GREEN: 8 tests passed. |
| 2026-06-07 | `.venv/bin/python -m py_compile app/services/reference_glossary_catalog.py app/services/reference_guides_catalog.py app/web/reference_guides.py app/web/streamlit_app.py` | Passed. |
| 2026-06-07 | `.venv/bin/python -m unittest tests.test_reference_glossary_catalog tests.test_reference_guides_catalog tests.test_service_contracts` | Passed: 296 tests. Existing warnings only. |
| 2026-06-07 | `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py` | PASS: boundary files 48, service 33, runtime 15, no hard violations or advisories. |
| 2026-06-07 | `git diff --check` | Passed. |
| 2026-06-07 | Browser QA on `http://localhost:8506/glossary` and `http://localhost:8506/guides` | Passed render check: Glossary shows curated concept metrics/table plus `GLOSSARY.md` sections; Guides shows shared `NOT_RUN` concept rows. Screenshot: `.playwright-mcp/reference-glossary-v3-qa-20260607-core.png`. |
| 2026-06-07 | `lsof -iTCP:8506 -sTCP:LISTEN -n -P` after shutdown | No listener. |
