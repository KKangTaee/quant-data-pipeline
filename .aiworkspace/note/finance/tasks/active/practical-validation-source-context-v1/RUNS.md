# Runs

| Time | Command | Result |
|---|---|---|
| 2026-05-31 | `git status --short` | Dirty tree includes generated run history / registries / QA screenshots / `.DS_Store`; preserve and avoid staging. |
| 2026-05-31 | `.venv/bin/python -m py_compile app/services/backtest_practical_validation_source.py app/services/backtest_practical_validation_replay.py app/web/backtest_candidate_review_helpers.py app/web/backtest_compare.py app/web/backtest_practical_validation.py` | Passed. |
| 2026-05-31 | `.venv/bin/python -m pytest tests/test_service_contracts.py -k "selection_history or selection_source_preserves_cost"` | Not run: local venv does not have `pytest` installed. |
| 2026-05-31 | `.venv/bin/python -m unittest tests.test_service_contracts.PracticalValidationServiceContractTests` | Passed, 17 tests. |
| 2026-05-31 | `git diff --check` | Passed. |
| 2026-05-31 | `.venv/bin/python -m unittest tests.test_service_contracts` | Passed, 210 tests. |
| 2026-05-31 | `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py` | Passed, hard violations none. |
| 2026-05-31 | `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py` | Passed checklist. Generated run history, registries, QA screenshots, and `.DS_Store` remain unstaged candidates. |
| 2026-05-31 | `.venv/bin/python -m streamlit run app/web/streamlit_app.py --server.port 8505 --server.address 127.0.0.1 --server.headless true --browser.gatherUsageStats false` + Browser QA | Passed. Practical Validation Step 1 rendered source strategy, construction, selection evidence cards, component strategy table, Result Table tabs, and browser console errors 0. Screenshot: `practical-validation-source-context-v1-qa.png`. |
