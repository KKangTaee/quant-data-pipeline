# Streamlit Ingestion Console Split Runs

## RED

Command:

```bash
.venv/bin/python -m unittest tests.test_service_contracts.BoundaryContractHardeningTests.test_streamlit_shell_delegates_ingestion_console_to_dedicated_module tests.test_service_contracts.BoundaryContractHardeningTests.test_ingestion_console_module_owns_render_entrypoint
```

Result:

- Failed as expected before implementation.
- Failure showed `app.web.ingestion_console` did not exist and `streamlit_app.py` had not yet delegated the Ingestion console.

## GREEN

Command:

```bash
.venv/bin/python -m py_compile app/web/streamlit_app.py app/web/ingestion_console.py tests/test_service_contracts.py
```

Result:

- Passed.

Command:

```bash
.venv/bin/python -m unittest tests.test_service_contracts.BoundaryContractHardeningTests.test_streamlit_shell_delegates_ingestion_console_to_dedicated_module tests.test_service_contracts.BoundaryContractHardeningTests.test_ingestion_console_module_owns_render_entrypoint
```

Result:

- Passed. Existing `edgar` deprecation warnings and Streamlit no-runtime cache warning appeared during import-only test execution.

## Final Verification

Command:

```bash
.venv/bin/python -m unittest tests.test_service_contracts.BoundaryContractHardeningTests
```

Result:

- Passed. 3 tests.

Command:

```bash
.venv/bin/python -m py_compile app/web/streamlit_app.py app/web/ingestion_console.py tests/test_service_contracts.py
```

Result:

- Passed.

Command:

```bash
.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py
```

Result:

- Passed. Hard violations: none. Advisories: none.

Command:

```bash
.venv/bin/python -m unittest tests.test_service_contracts
```

Result:

- Passed. 277 tests. Existing `edgar` deprecation warnings and Streamlit no-runtime cache warnings appeared during import-only test execution.

Command:

```bash
git diff --check
```

Result:

- Passed.

Command:

```bash
curl -fsS http://localhost:8501/_stcore/health
```

Result:

- `ok` after restarting the `qdp8501-master` Streamlit screen session.

## Browser QA

- Route: `http://localhost:8501/ingestion`
- Confirmed: Ingestion title, page caption, Runtime / Build, and `일별 가격 업데이트` panel.
- Confirmed: no Traceback / ModuleNotFoundError / NameError in the visible DOM.
- Fresh direct `/ingestion` tab loaded without Page not found modal.
- Screenshot: `/tmp/ingestion-console-split-clean-qa-20260607.png` generated artifact, not staged.
