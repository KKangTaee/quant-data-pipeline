# Runs

## 2026-06-07

- RED: `.venv/bin/python -m unittest tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests.test_operations_overview_model_adds_evidence_health_strip tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests.test_operations_overview_source_renders_evidence_health_before_queue` failed because `evidence_health` and `_render_evidence_health_strip(model)` did not exist.
- GREEN: same focused command passed after adding the read model and renderer.
- Regression: Operations overview/navigation focused unittest set passed: 10 tests, OK.
- Static verification: `.venv/bin/python -m py_compile app/web/operations_overview.py tests/test_service_contracts.py` and `git diff --check` passed.
- Verification gap: `.venv/bin/python scripts/check_ui_engine_boundary.py` and `.venv/bin/python scripts/check_finance_refinement_hygiene.py` could not run because those scripts are not present in this worktree.
- Browser QA: Streamlit served on `http://localhost:8507/operations`; DOM check confirmed Portfolio Monitoring Status -> Evidence Health -> Today's Operations Queue ordering and no archive/development-history copy.
- Browser QA screenshot: `operations-evidence-health-strip-qa.png`. In-app Browser screenshot capture timed out, so Playwright fallback captured the QA image after the same page rendered `Evidence Health`.
- Final verification: Operations focused unittest set passed again: 10 tests, OK. `py_compile` and `git diff --check` also passed.
- Final Browser QA: `http://localhost:8507/operations` rendered `Evidence Health`; DOM check confirmed Portfolio Monitoring Status before Evidence Health before Today's Operations Queue, with Selected Evidence and System Run Health present and archive/development-history copy absent.
