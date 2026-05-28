# Runs

## 2026-05-28

- `.venv/bin/python -m py_compile app/services/backtest_data_coverage_audit.py finance/loaders/price.py finance/loaders/__init__.py app/services/backtest_practical_validation_diagnostics.py app/services/backtest_evidence_read_model.py app/web/backtest_practical_validation.py app/web/backtest_final_review.py app/web/backtest_final_review_helpers.py`
  - Result: pass.
- `.venv/bin/python -m unittest tests.test_service_contracts.DataCoverageAuditContractTests tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests tests.test_service_contracts.PracticalValidationServiceContractTests`
  - Result: pass, 21 tests.
- `git diff --check`
  - Result: pass.
- `.venv/bin/python -m unittest tests.test_service_contracts`
  - Result: pass, 55 tests.
