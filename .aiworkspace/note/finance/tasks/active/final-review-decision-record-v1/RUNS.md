# Final Review Decision Record V1 Runs

| Command | Result |
|---|---|
| `.venv/bin/python -m py_compile app/services/backtest_evidence_read_model.py app/web/backtest_final_review.py tests/test_service_contracts.py` | Passed |
| `.venv/bin/python -m unittest tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_decision_record_guide_blocks_selected_route_when_gate_blocks tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_decision_record_guide_allows_non_select_route_with_evidence_gap tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_candidate_board_prioritizes_ready_candidates` | Passed, 3 tests |
| `.venv/bin/python -m unittest tests.test_service_contracts` | Passed, 203 tests |
| `git diff --check` | Passed |
| `.venv/bin/python -m streamlit run app/web/streamlit_app.py --server.headless true --server.port 8503 --server.address 127.0.0.1` + Browser QA | Passed visible QA. Final Review showed Decision Record Checklist, non-select recordable route guide, and disabled live approval / order boundary. Direct `/backtest` produced existing Streamlit `_stcore` relative-path 404 console errors. |
