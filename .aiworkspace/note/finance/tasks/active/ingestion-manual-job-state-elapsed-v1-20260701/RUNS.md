# Runs

## 2026-07-01

- RED: `uv run python -m unittest tests.test_service_contracts.BoundaryContractHardeningTests.test_ingestion_collection_section_selector_is_stateful_across_reruns tests.test_service_contracts.BoundaryContractHardeningTests.test_ingestion_running_jobs_preserve_section_and_show_elapsed_time`
  - Result: failed before implementation because the stateful selector and elapsed job-state markers were absent.
- GREEN: `uv run python -m unittest tests.test_service_contracts.BoundaryContractHardeningTests.test_ingestion_collection_section_selector_is_stateful_across_reruns tests.test_service_contracts.BoundaryContractHardeningTests.test_ingestion_running_jobs_preserve_section_and_show_elapsed_time`
  - Result: passed.
- `uv run python -m py_compile app/web/ingestion_console.py app/jobs/ingestion_jobs.py app/jobs/run_history.py`
  - Result: passed.
- `uv run --with pytest python -m pytest tests/test_service_contracts.py -q -k "ingestion or financial_statement or statement_shadow"`
  - Result: passed, 24 selected tests.
- `git diff --check`
  - Result: passed.
- Browser QA: `uv run streamlit run app/web/streamlit_app.py --server.port 8526 --server.headless true`
  - Result: Ingestion page loaded. Manual selector click showed `수동 복구 / 진단` context and `상세 재무제표 수동 수집`; no Traceback.
  - Screenshot artifact: `.aiworkspace/note/finance/run_artifacts/ingestion-manual-section-stateful-20260701.png`

## Notes

- Port 8525 was already occupied during QA, so 8526 was used.
- The Streamlit `/ingestion` direct route showed the app's page-not-found fallback dialog once, then rendered the Ingestion page. The dialog was closed for QA.
