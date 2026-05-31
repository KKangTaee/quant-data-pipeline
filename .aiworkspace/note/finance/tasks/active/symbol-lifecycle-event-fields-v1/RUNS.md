# Symbol Lifecycle Event Fields V1 Runs

Status: Active
Created: 2026-05-28

## Commands

2026-05-28:

```bash
.venv/bin/python -m py_compile finance/data/db/schema.py finance/data/nyse_db.py finance/data/sec_delisting.py finance/loaders/universe.py app/services/backtest_data_coverage_audit.py
```

Result: passed.

```bash
.venv/bin/python -m unittest tests.test_service_contracts.SecForm25DelistingCollectorContractTests tests.test_service_contracts.DataCoverageAuditContractTests
```

Result: passed, 8 tests. Warnings were dependency deprecation warnings from `edgar`.

```bash
git diff --check
```

Result: passed.

```bash
.venv/bin/python -m unittest tests.test_service_contracts
```

Result: passed, 67 tests. Warnings were dependency deprecation warnings from `edgar`.
