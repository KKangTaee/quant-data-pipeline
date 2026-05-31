# Phase 8 Integrated QA Closeout Runs

Status: Active
Created: 2026-05-29

## Commands

2026-05-29:

```bash
.venv/bin/python -m py_compile finance/data/db/schema.py finance/data/nyse_db.py finance/data/sec_delisting.py finance/data/sec_company_tickers.py finance/data/symbol_directory.py finance/data/computed_lifecycle.py finance/loaders/universe.py app/jobs/ingestion_jobs.py app/services/backtest_data_coverage_audit.py
```

Result: passed.

```bash
.venv/bin/python -m unittest tests.test_service_contracts
```

Result: passed, 79 tests. Warnings were dependency deprecation warnings from `edgar`.

```bash
git diff --check
```

Result: passed.
