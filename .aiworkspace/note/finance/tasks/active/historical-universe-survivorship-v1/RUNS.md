# Runs

## 2026-05-28

- `.venv/bin/python -m py_compile finance/data/db/schema.py finance/data/nyse_db.py finance/loaders/universe.py finance/loaders/__init__.py app/services/backtest_data_coverage_audit.py app/services/backtest_validation_efficacy.py app/services/backtest_evidence_read_model.py`
  - Result: pass.
- `.venv/bin/python -m unittest tests.test_service_contracts.DataCoverageAuditContractTests tests.test_service_contracts.ValidationEfficacyAuditContractTests tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests`
  - Result: pass, 24 tests.
- `git diff --check`
  - Result: pass.
- `.venv/bin/python -m unittest tests.test_service_contracts`
  - Result: pass, 63 tests.
