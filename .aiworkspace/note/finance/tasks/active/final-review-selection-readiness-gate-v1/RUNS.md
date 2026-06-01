# Runs

| Time | Command / Check | Outcome |
|---|---|---|
| 2026-06-01 | Task setup | Opened task and captured gate redesign matrix. |
| 2026-06-01 | `.venv/bin/python -m unittest tests.test_service_contracts.PracticalValidationServiceContractTests tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests` | Passed, 48 tests. |
| 2026-06-01 | `.venv/bin/python -m py_compile app/services/backtest_evidence_read_model.py app/services/backtest_practical_validation_source.py app/web/backtest_final_review_helpers.py` | Passed. |
| 2026-06-01 | `.venv/bin/python -m unittest tests.test_service_contracts` | Passed, 211 tests. |
| 2026-06-01 | `git diff --check` | Passed. |
| 2026-06-01 | Browser QA attempt | Codex Browser MCP was unavailable because the shared Chrome profile was already in use. Python / Node Playwright packages were not installed in this worktree, so screenshot QA was skipped. |
| 2026-06-01 | `curl -I --max-time 5 http://127.0.0.1:8502/backtest` | Passed, HTTP 200. |
