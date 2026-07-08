# Phase 5. Ingestion Workflow Cleanup Runs

## TDD RED

```bash
uv run python -m unittest tests.test_service_contracts.BoundaryContractHardeningTests.test_ingestion_financial_statement_refresh_is_edgar_first_with_legacy_broad_advanced tests.test_service_contracts.BoundaryContractHardeningTests.test_statement_refresh_action_summary_focuses_on_coverage_freshness_and_next_action
```

Result: failed as expected. EDGAR-first Ingestion labels/order were absent and `_build_statement_refresh_action_summary` did not exist.

## Verification

```bash
uv run python -m unittest tests.test_service_contracts.BoundaryContractHardeningTests.test_ingestion_financial_statement_refresh_is_edgar_first_with_legacy_broad_advanced tests.test_service_contracts.BoundaryContractHardeningTests.test_statement_refresh_action_summary_focuses_on_coverage_freshness_and_next_action
```

Result: passed, 2 tests. EdgarTools emitted deprecation warnings during import.

```bash
uv run python -m py_compile app/jobs/ingestion_jobs.py app/web/ingestion_console.py app/jobs/diagnostics.py app/jobs/run_history.py
```

Result: passed.

```bash
uv run --with pytest python -m pytest tests/test_service_contracts.py -q -k "ingestion or financial_statement or statement_shadow or run_history"
```

Result: passed, 22 tests selected, 474 deselected, 3 edgar deprecation warnings.

```bash
git diff --check
```

Result: passed.

## Browser QA

```text
http://localhost:8525/ingestion
```

Result: passed. EDGAR annual refresh appears before the legacy broad yfinance card; both source-boundary phrases are present after expanding the relevant panels; no visible `Traceback` or `ImportError`.

Generated screenshot: `.aiworkspace/note/finance/run_artifacts/ingestion_edgar_statement_primary_20260630.png`
