# Data Provenance / PIT Evidence Contract Runs

## 2026-06-09

- `git status --short && git rev-parse --show-toplevel && git log --oneline -5`
  - Found pre-existing local/generated changes: saved dashboard JSONL, `.DS_Store`, run history JSONL, multiple QA screenshots.
  - Latest commit: `79af6f93 Robustness 실험 run-set 계약 추가`.
- Read required docs listed in the user request.
- `rg` audit over provenance/source/staleness/PIT terms in `app`, `finance`, `tests`, and durable docs.
  - Confirmed provider/macro/lifecycle loaders already expose source/timing/coverage metadata.
  - Confirmed Practical Validation / Final Review read models have audit rows but no unified provenance contract.
- `.venv/bin/python -m unittest tests.test_service_contracts.DataProvenanceContractTests -v`
  - Expected RED: `app.services.backtest_data_provenance` missing and Final Review packet has no `data_provenance_summary`.
- `.venv/bin/python -m unittest tests.test_service_contracts.DataProvenanceContractTests -v`
  - PASS after implementation: stale provider/current lifecycle evidence stay `Treat As Pass=False`; Final Review packet carries `data_provenance_summary`.
- `.venv/bin/python -m unittest tests.test_service_contracts.DataCoverageAuditContractTests tests.test_service_contracts.BacktestRealismAuditContractTests -v`
  - PASS: adjacent data coverage and realism contracts remain stable.
- `.venv/bin/python -m unittest tests.test_service_contracts -v`
  - Initial failure after implementation: new provenance check turned sparse legacy Final Review packet fixtures into selected-route blockers.
  - Root cause: provenance builder fabricated missing provider/price/lifecycle/run-set rows from non-provenance status stubs.
- `.venv/bin/python -m unittest tests.test_service_contracts.DataProvenanceContractTests tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_investability_packet_ready_contract_is_ui_neutral tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_integrated_investability_gate_all_ready_allows_selected_route tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_integrated_investability_gate_multiple_review_gaps_hold_selected_route -v`
  - PASS after regression fix: explicit provenance rows gate; sparse legacy packet fixtures remain neutral.
- `.venv/bin/python -m py_compile app/services/backtest_data_provenance.py app/services/backtest_practical_validation_diagnostics.py app/services/backtest_evidence_read_model.py app/web/backtest_practical_validation.py app/web/backtest_final_review.py && git diff --check`
  - PASS.
- `.venv/bin/python -m unittest tests.test_service_contracts -v`
  - 295/296 PASS.
  - Remaining failure: `FuturesMacroThermometerContractTests.test_macro_thermometer_inverts_rates_and_fx_pressure` expected `OK` but got `REVIEW`; fixture latest candle is 2026-06-02 while current session date is 2026-06-09, so the service flags stale daily futures data. This is outside this task's touched files.
- Browser QA: `.venv/bin/python -m streamlit run app/web/streamlit_app.py --server.port 8517 --server.headless true --browser.gatherUsageStats false`
  - Direct `.venv/bin/streamlit` failed due a stale shebang pointing at another worktree venv; module execution worked.
  - Browser DOM QA loaded `http://localhost:8517/backtest`, switched to Practical Validation and Final Review successfully.
  - Browser screenshot API timed out on Streamlit capture; fallback Playwright viewport screenshot saved to `/Users/taeho/Project/quant-data-pipeline-worktrees/main-dev/data-provenance-pit-contract-qa-20260609.png`.
- Final focused verification:
  - `.venv/bin/python -m unittest tests.test_service_contracts.DataProvenanceContractTests tests.test_service_contracts.DataCoverageAuditContractTests tests.test_service_contracts.BacktestRealismAuditContractTests tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_investability_packet_ready_contract_is_ui_neutral tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_integrated_investability_gate_all_ready_allows_selected_route tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_integrated_investability_gate_multiple_review_gaps_hold_selected_route -v`
  - `.venv/bin/python -m py_compile app/services/backtest_data_provenance.py app/services/backtest_practical_validation_diagnostics.py app/services/backtest_evidence_read_model.py app/web/backtest_practical_validation.py app/web/backtest_final_review.py`
  - `git diff --check`
  - PASS.
