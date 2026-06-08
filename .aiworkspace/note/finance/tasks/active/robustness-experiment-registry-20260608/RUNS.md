# Robustness Experiment Registry Runs

## 2026-06-08

- Read requested docs and prior task statuses.
- Inspected existing robustness / temporal / validation efficacy / realism / Final Review read model code.
- Confirmed dirty worktree has unrelated saved JSONL, `.DS_Store`, run history, and QA screenshots; these should remain unstaged.
- RED: `.venv/bin/python -m unittest tests.test_service_contracts.RobustnessExperimentRunSetContractTests -v`
  - Result: failed with `ModuleNotFoundError: No module named 'app.services.backtest_robustness_run_set'`.
- GREEN focused: `.venv/bin/python -m unittest tests.test_service_contracts.RobustnessExperimentRunSetContractTests tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_investability_packet_carries_robustness_run_set_snapshot -v`
  - Result: 3 tests passed.
- Compile: `.venv/bin/python -m py_compile app/services/backtest_robustness_run_set.py app/services/backtest_practical_validation_diagnostics.py app/services/backtest_evidence_read_model.py app/web/backtest_practical_validation.py app/web/backtest_final_review.py app/web/backtest_final_review_helpers.py`
  - Result: passed.
- Full service contracts: `.venv/bin/python -m unittest tests.test_service_contracts -v`
  - Result: 294 tests passed.
- Hygiene: `git diff --check`
  - Result: passed.
- Browser QA:
  - Started Streamlit with `.venv/bin/python -m streamlit run app/web/streamlit_app.py --server.port 8503 --server.headless true`.
  - Opened `http://localhost:8503/backtest`, switched to `Final Review`, confirmed the page rendered without console errors.
  - Screenshot: `robustness-run-set-v1-browser-qa-20260608.png`.
