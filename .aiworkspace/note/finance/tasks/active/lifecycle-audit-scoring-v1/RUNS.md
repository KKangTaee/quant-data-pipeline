# Lifecycle Audit Scoring V1 Runs

Status: Active
Created: 2026-05-28

## Commands

2026-05-28:

```bash
.venv/bin/python -m py_compile app/services/backtest_data_coverage_audit.py
```

Result: passed.

```bash
.venv/bin/python -m unittest tests.test_service_contracts.DataCoverageAuditContractTests tests.test_service_contracts.ComputedSnapshotLifecycleContractTests
```

Result: passed, 9 tests. Warnings were dependency deprecation warnings from `edgar`.

```bash
.venv/bin/python -m unittest tests.test_service_contracts
```

Result: passed, 79 tests. Warnings were dependency deprecation warnings from `edgar`.

```bash
git diff --check
```

Result: passed.
