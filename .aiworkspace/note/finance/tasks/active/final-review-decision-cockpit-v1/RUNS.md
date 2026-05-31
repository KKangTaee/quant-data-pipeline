# Final Review Decision Cockpit V1 Runs

Status: Active
Created: 2026-05-31

## Runs

- `git status --short`
  - Result: worktree already had generated / local artifacts before this task (`run_history`, registry JSONL, QA PNGs, `.DS_Store`); left untouched.
- `.venv/bin/python -m py_compile app/services/backtest_evidence_read_model.py app/web/backtest_final_review.py app/web/backtest_final_review_helpers.py`
  - Result: pass.
- `.venv/bin/python -m pytest tests/test_service_contracts.py -k 'final_review_decision_cockpit or decision_display_rows_keep_table_contract or final_review_save_evaluation_uses_investability_packet_gate'`
  - Result: not run; venv has no `pytest` module.
- `.venv/bin/python -m unittest tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_decision_cockpit_summarizes_selected_route_state tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_decision_cockpit_surfaces_blocked_candidate_board_row tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_decision_display_rows_keep_table_contract tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_save_evaluation_uses_investability_packet_gate`
  - Result: pass, 4 tests.
- `.venv/bin/python -m streamlit run app/web/streamlit_app.py --server.port 8503 --server.headless true`
  - Result: server started; direct `.venv/bin/streamlit` wrapper failed first because its shebang points at another worktree venv.
- Browser QA on `http://127.0.0.1:8503/backtest`
  - Result: Final Review opened; Candidate Board and Decision Cockpit rendered. Screenshot: `final-review-decision-cockpit-summary-qa.png`.
- `.venv/bin/python -m unittest tests.test_service_contracts`
  - Result: pass, 200 tests. Streamlit emitted one existing `use_container_width` deprecation warning during service tests.
- `git diff --check`
  - Result: pass.
- QA server stop
  - Result: stopped `python -m streamlit` session on port 8503. Server log also emitted existing `use_container_width` deprecation warnings.
