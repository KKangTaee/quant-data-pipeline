# Runs

## 2026-05-28

- `.venv/bin/python -m py_compile app/services/backtest_evidence_read_model.py`
  - Result: pass.
- `.venv/bin/python -m unittest tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests`
  - Result: pass, 12 tests.
- `git diff --check`
  - Result: pass.
- `.venv/bin/python -m unittest tests.test_service_contracts`
  - Result: pass, 53 tests.
