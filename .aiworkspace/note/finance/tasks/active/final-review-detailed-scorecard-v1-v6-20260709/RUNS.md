# Runs

Command log for Final Review detailed scorecard V1-V6.

## V1

- `.venv/bin/python -m unittest tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_detailed_scorecard_exposes_weighted_dimensions`
  - RED result: failed with `KeyError: 'dimensions'` before implementation.
  - GREEN result: passed after adding weighted dimensions.
- `.venv/bin/python -m unittest tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_scorecard_maps_gate_to_recommendation_taxonomy tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_scorecard_downgrades_blocked_candidate`
  - Result: passed.
- `.venv/bin/python -m py_compile app/services/backtest_evidence_read_model.py`
  - Result: passed.
- `git diff --check`
  - Result: passed.
