# Final Review Saved Decision Review V1 Runs

| Command | Result |
|---|---|
| `.venv/bin/python -m py_compile app/services/backtest_evidence_read_model.py app/web/backtest_final_review.py tests/test_service_contracts.py` | Passed |
| `.venv/bin/python -m unittest tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_saved_final_review_decision_review_summarizes_and_sorts_records tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_decision_display_rows_keep_table_contract` | Passed, 2 tests |
| `.venv/bin/python -m unittest tests.test_service_contracts` | Passed, 204 tests |
| `git diff --check` | Passed |
| `.venv/bin/python -m streamlit run app/web/streamlit_app.py --server.headless true --server.port 8503 --server.address 127.0.0.1` + Browser QA | Passed visible QA. Final Review loaded and saved decision empty state rendered. Local data had 0 final decision rows, so populated ledger behavior is covered by service contract tests. |
