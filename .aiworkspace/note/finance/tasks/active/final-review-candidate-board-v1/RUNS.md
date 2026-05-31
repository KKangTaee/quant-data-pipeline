# Final Review Candidate Board V1 Runs

## 2026-05-31

- `.venv/bin/python -m py_compile app/services/backtest_evidence_read_model.py app/web/backtest_final_review.py tests/test_service_contracts.py`
  - Passed.
- `.venv/bin/python -m unittest tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_candidate_board_prioritizes_ready_candidates tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_decision_cockpit_summarizes_selected_route_state tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_decision_cockpit_surfaces_blocked_candidate_board_row`
  - Passed: 3 tests.
- `.venv/bin/python -m unittest tests.test_service_contracts`
  - Passed: 201 tests.
- `git diff --check`
  - Passed.
- Browser QA on Backtest > Final Review
  - Confirmed Candidate Board summary / Review Queue / detail table render.
  - Screenshot saved at `/Users/taeho/Project/quant-data-pipeline-worktrees/main-dev/final-review-candidate-board-v1-qa.png`.
