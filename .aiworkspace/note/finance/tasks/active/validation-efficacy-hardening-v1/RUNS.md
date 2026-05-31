# Runs

## 2026-05-28

- `.venv/bin/python -m py_compile app/services/backtest_validation_efficacy.py app/services/backtest_practical_validation_diagnostics.py app/services/backtest_evidence_read_model.py app/web/backtest_practical_validation.py app/web/backtest_final_review.py app/web/backtest_final_review_helpers.py`
  - Result: pass.
- `.venv/bin/python -m unittest tests.test_service_contracts.ValidationEfficacyAuditContractTests tests.test_service_contracts.PracticalValidationServiceContractTests tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests`
  - Result: pass, 18 tests.
- `.venv/bin/python -m unittest tests.test_service_contracts`
  - Result: pass, 48 tests.
