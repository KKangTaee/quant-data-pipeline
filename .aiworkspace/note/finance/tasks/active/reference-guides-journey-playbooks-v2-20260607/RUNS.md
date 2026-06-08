# Runs

| Date | Command | Result |
|---|---|---|
| 2026-06-07 | `.venv/bin/python -m unittest tests.test_reference_guides_catalog` | RED: failed on missing `steps` and missing `provider_snapshot_missing` playbook. |
| 2026-06-07 | `.venv/bin/python -m unittest tests.test_reference_guides_catalog` | GREEN: 5 tests passed. |
| 2026-06-07 | `.venv/bin/python -m py_compile app/services/reference_guides_catalog.py app/web/reference_guides.py app/web/streamlit_app.py` | Passed. |
| 2026-06-07 | `.venv/bin/python -m unittest tests.test_reference_guides_catalog tests.test_service_contracts` | Final: 293 tests passed. Existing edgar deprecation and Streamlit no-runtime warnings only. |
| 2026-06-07 | `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py` | PASS: hard violations none, advisories none. |
| 2026-06-07 | `git diff --check` | Passed. |
| 2026-06-07 | Browser QA at `http://localhost:8505/guides` | Reference Center rendered. 제품 흐름 tab showed Journey 상세 보기 / 확인 순서 / 자주 막히는 상태. 문제 해결 tab showed check steps and evidence locations. |
| 2026-06-07 | `reference-guides-v2-qa-20260607.png` | Generated QA screenshot saved; not staged by default. |
| 2026-06-07 | `lsof -iTCP:8505 -sTCP:LISTEN -n -P` | Exit 1 / no output after cleanup; QA server not left running. |
