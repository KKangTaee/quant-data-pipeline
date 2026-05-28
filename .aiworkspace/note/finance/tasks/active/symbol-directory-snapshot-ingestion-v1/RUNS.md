# Symbol Directory Snapshot Ingestion V1 Runs

Status: Active
Created: 2026-05-28

## Commands

2026-05-28:

```bash
.venv/bin/python -m py_compile finance/data/symbol_directory.py app/jobs/ingestion_jobs.py
```

Result: passed.

```bash
.venv/bin/python -m unittest tests.test_service_contracts.SymbolDirectorySnapshotCollectorContractTests
```

Result: passed, 4 tests. Warnings were dependency deprecation warnings from `edgar`.

```bash
git diff --check
```

Result: passed.

```bash
.venv/bin/python -m unittest tests.test_service_contracts
```

Result: passed, 71 tests. Warnings were dependency deprecation warnings from `edgar`.
