# Runs

Status: Completed
Last Verified: 2026-06-08

## RED

```bash
.venv/bin/python -m unittest \
  tests.test_reference_contextual_help.ReferenceContextualHelpContractTests.test_contextual_help_renderer_maps_internal_links_to_page_target_keys \
  tests.test_reference_guides_catalog.ReferenceGuidesCatalogContractTests.test_reference_center_catalog_is_streamlit_free_and_task_first
```

Result: expected failure. `_reference_page_target_key` did not exist in `app.web.reference_contextual_help`.

## GREEN

```bash
.venv/bin/python -m unittest tests.test_reference_contextual_help tests.test_reference_guides_catalog
```

Result: passed, 10 tests.

## Closeout Verification

```bash
.venv/bin/python -m py_compile app/web/reference_contextual_help.py app/web/streamlit_app.py tests/test_reference_contextual_help.py tests/test_reference_guides_catalog.py
```

Result: passed.

```bash
.venv/bin/python -m unittest tests.test_reference_contextual_help tests.test_reference_guides_catalog tests.test_reference_glossary_catalog tests.test_service_contracts
```

Result: passed, 309 tests.

```bash
.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py
```

Result: passed. Hard violations: none. Advisories: none.

```bash
git diff --check
curl -fsS http://localhost:8501/_stcore/health
```

Result: passed. Streamlit health returned `ok`.

```bash
rg -n "Status: In Progress" .aiworkspace/note/finance/tasks/active/reference-contextual-links-v4-20260608 .aiworkspace/note/finance/tasks/active/merge-review-fixes-20260608 --glob '!RUNS.md'
```

Result: no matches.

## Browser QA

- Restarted local Streamlit on `http://localhost:8501` after the previous hot-reload shell stopped rendering body content.
- Verified Backtest Analysis Reference help renders and `Guides에서 workflow 확인` navigates to `http://localhost:8501/guides` with the Reference Center body visible.
- Verified Operations Console Reference help renders and `Glossary에서 운영 용어 확인` navigates to `http://localhost:8501/glossary` with Glossary body visible.
- Screenshot artifact: `/Users/taeho/Project/quant-data-pipeline/reference-help-page-link-qa-20260608.png`
