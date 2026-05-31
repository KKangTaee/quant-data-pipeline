# Final Review Evidence Appendix V1 Runs

## 2026-05-31

- `git status --short`
  - Existing dirty generated / local artifacts were present before this task: run history JSONL, registry JSONL, `.DS_Store`, and prior QA screenshots.
- `.venv/bin/python -m py_compile app/web/backtest_final_review.py app/web/backtest_final_review_helpers.py app/services/backtest_evidence_read_model.py`
  - Passed.
- `.venv/bin/python -m unittest tests.test_service_contracts`
  - Passed: 200 tests.
- `git diff --check`
  - Passed.
- Browser QA on Backtest > Final Review at `http://127.0.0.1:8503/backtest`
  - Confirmed order: Candidate Board -> Decision Cockpit -> Final Decision Record -> Evidence Appendix -> Saved Final Review Decisions.
  - Confirmed appendix copy says it does not rerun Practical Validation.
  - Screenshot saved at `/Users/taeho/Project/quant-data-pipeline-worktrees/main-dev/final-review-evidence-appendix-qa.png`.
