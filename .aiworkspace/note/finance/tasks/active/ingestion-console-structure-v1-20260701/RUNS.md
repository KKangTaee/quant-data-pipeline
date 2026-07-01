# Runs

## 2026-07-01

- `.venv/bin/python -m unittest tests.test_service_contracts.BoundaryContractHardeningTests.test_ingestion_collection_section_selector_is_stateful_across_reruns tests.test_service_contracts.BoundaryContractHardeningTests.test_ingestion_running_jobs_preserve_section_and_show_elapsed_time tests.test_service_contracts.BoundaryContractHardeningTests.test_ingestion_ui_removes_legacy_broad_collection_cards_but_keeps_compatibility_actions`
  - Result: PASS, 3 tests.
- `.venv/bin/python -m pytest ...`
  - Result: not available. `.venv` has no `pytest` module, so this task uses `unittest`.
- `.venv/bin/python -m unittest tests.test_service_contracts.BoundaryContractHardeningTests.test_ingestion_console_moves_run_records_into_third_collection_section`
  - Result: RED before implementation. Missing `INGESTION_COLLECTION_RECORDS` / records section function.
- `.venv/bin/python -m unittest tests.test_service_contracts.BoundaryContractHardeningTests.test_ingestion_console_moves_run_records_into_third_collection_section tests.test_service_contracts.BoundaryContractHardeningTests.test_ingestion_collection_section_selector_is_stateful_across_reruns tests.test_service_contracts.BoundaryContractHardeningTests.test_ingestion_running_jobs_preserve_section_and_show_elapsed_time tests.test_service_contracts.BoundaryContractHardeningTests.test_ingestion_ui_removes_legacy_broad_collection_cards_but_keeps_compatibility_actions`
  - Result: PASS, 4 tests.
- `.venv/bin/python -m py_compile app/web/ingestion_console.py app/services/ingestion_diagnostics.py app/jobs/ingestion_jobs.py tests/test_service_contracts.py`
  - Result: PASS.
- `git diff --check`
  - Result: PASS.
- `.venv/bin/python -m unittest tests.test_service_contracts.BoundaryContractHardeningTests.test_ingestion_console_dispatches_collection_sections_to_dedicated_renderers`
  - Result: RED before implementation. Missing dedicated operational/manual/dispatch renderers.
- `.venv/bin/python -m unittest tests.test_service_contracts.BoundaryContractHardeningTests.test_ingestion_console_dispatches_collection_sections_to_dedicated_renderers tests.test_service_contracts.BoundaryContractHardeningTests.test_ingestion_console_moves_run_records_into_third_collection_section tests.test_service_contracts.BoundaryContractHardeningTests.test_ingestion_collection_section_selector_is_stateful_across_reruns tests.test_service_contracts.BoundaryContractHardeningTests.test_ingestion_running_jobs_preserve_section_and_show_elapsed_time tests.test_service_contracts.BoundaryContractHardeningTests.test_ingestion_ui_removes_legacy_broad_collection_cards_but_keeps_compatibility_actions`
  - Result: PASS, 5 tests.
- `.venv/bin/python -m py_compile app/web/ingestion_console.py tests/test_service_contracts.py`
  - Result: PASS.
- `git diff --check`
  - Result: PASS.
