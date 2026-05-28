# SEC Form 25 Delisting Backfill V1 Runs

## 2026-05-28

| Command | Result |
|---|---|
| `.venv/bin/python -m py_compile finance/data/sec_delisting.py app/jobs/ingestion_jobs.py` | PASS |
| `.venv/bin/python -m unittest tests.test_service_contracts.SecForm25DelistingCollectorContractTests` | PASS, 3 tests |
| `.venv/bin/python -m unittest tests.test_service_contracts` | PASS, 66 tests |
