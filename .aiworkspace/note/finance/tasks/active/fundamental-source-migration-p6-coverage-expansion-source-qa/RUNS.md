# Phase 6. Coverage Expansion And Source QA Runs

## TDD RED

```bash
uv run python -m unittest tests.test_service_contracts.BoundaryContractHardeningTests.test_ingestion_diagnostics_service_owns_public_entrypoints tests.test_service_contracts.BoundaryContractHardeningTests.test_statement_universe_coverage_qa_groups_missing_reasons_without_live_source_probe tests.test_service_contracts.BoundaryContractHardeningTests.test_ingestion_console_surfaces_statement_universe_coverage_qa_card
```

Result: failed as expected. The universe QA service entrypoint, DB-backed analyzer, and UI card did not exist.

## Verification

```bash
uv run python -m unittest tests.test_service_contracts.BoundaryContractHardeningTests.test_ingestion_diagnostics_service_owns_public_entrypoints tests.test_service_contracts.BoundaryContractHardeningTests.test_statement_universe_coverage_qa_groups_missing_reasons_without_live_source_probe tests.test_service_contracts.BoundaryContractHardeningTests.test_ingestion_console_surfaces_statement_universe_coverage_qa_card
```

Result: passed, 3 tests. EdgarTools emitted deprecation warnings during import.

```bash
uv run python -m py_compile app/jobs/diagnostics.py app/services/ingestion_diagnostics.py app/web/ingestion_console.py finance/data/financial_statements.py finance/data/fundamentals.py finance/data/factors.py finance/loaders/universe.py
```

Result: passed.

```bash
uv run --with pytest python -m pytest tests/test_service_contracts.py -q -k "coverage or financial_statement or statement_shadow or universe"
```

Result: passed, 27 tests selected, 471 deselected, 3 edgar deprecation warnings.

```bash
git diff --check
```

Result: passed.

## DB Smoke

```bash
uv run python - <<'PY'
from app.jobs.diagnostics import inspect_statement_universe_coverage

for universe_code, limit in [('SP500', None), ('TOP1000', 1000), ('TOP2000', 2000), ('NASDAQ', 5000)]:
    result = inspect_statement_universe_coverage(
        universe_code=universe_code,
        universe_limit=limit,
        freq='annual',
        as_of_date='2026-06-30',
    )
    details = result['details']
    coverage = details.get('coverage') or {}
    print(universe_code, result['status'], details.get('universe_count'), coverage.get('shadow_available_count'), coverage.get('shadow_coverage_pct'), details.get('reason_counts'))
PY
```

Result:

- `SP500`: warning, 503 symbols, 473 shadow-ready, 94.04%, reasons `statement_shadow_available=473`, `non_us_issuer_or_foreign_form_expected=22`, `missing_profile_or_universe_metadata=3`, `edgar_unavailable_or_cik_mapping_issue=5`.
- `TOP1000`: warning, 1000 symbols, 953 shadow-ready, 95.3%, reasons `statement_shadow_available=953`, `edgar_unavailable_or_cik_mapping_issue=47`.
- `TOP2000`: warning, 2000 symbols, 953 shadow-ready, 47.65%, reasons `statement_shadow_available=953`, `edgar_unavailable_or_cik_mapping_issue=1047`.
- `NASDAQ`: error, 0 resolved universe symbols in this worktree.

## Browser QA

```text
http://localhost:8525/ingestion
```

Result: passed after restarting stale Streamlit port `8525`. New card was visible under manual diagnostics, expected source-boundary language was present, and no visible `Traceback` or `ImportError` remained.

Generated screenshot: `.aiworkspace/note/finance/run_artifacts/ingestion_statement_universe_coverage_qa_20260630.png`
