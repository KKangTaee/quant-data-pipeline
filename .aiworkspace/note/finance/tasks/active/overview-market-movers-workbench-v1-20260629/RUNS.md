# Runs

| Time | Command / Check | Result |
|---|---|---|
| 2026-06-29 | `uv run python -m pytest tests/test_service_contracts.py -q -k "market_movers_command_strip_model or market_movers_empty_state_model"` | Blocked: current venv has no `pytest` module. |
| 2026-06-29 | `uv run python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_market_movers_command_strip_model_summarizes_active_workbench_context tests.test_service_contracts.OverviewAutomationContractTests.test_market_movers_empty_state_model_guides_no_universe_without_showing_why_it_moved` | RED confirmed: helper imports missing. |
| 2026-06-29 | `uv run python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_market_movers_command_strip_model_summarizes_active_workbench_context tests.test_service_contracts.OverviewAutomationContractTests.test_market_movers_empty_state_model_guides_no_universe_without_showing_why_it_moved` | PASS after implementation. |
| 2026-06-29 | `git diff --check` | PASS. |
| 2026-06-29 | `uv run python -m py_compile app/web/overview/market_movers.py app/web/overview/market_movers_helpers.py app/web/overview/components/market_movers.py app/services/overview/market_movers.py app/services/overview/why_it_moved.py` | PASS. |
| 2026-06-29 | `uv run python -m pytest tests/test_service_contracts.py -q -k "market_mover or market_movers or why_it_moved"` | Blocked: `.venv/bin/python3: No module named pytest`. |
| 2026-06-29 | `PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts -k market_mover` | PASS: 32 tests. |
| 2026-06-29 | `PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts -k why_it_moved` | PASS: 4 tests. |
| 2026-06-29 | `uv run streamlit run app/web/streamlit_app.py --server.port 8525 --server.headless true` | PASS: server started on `http://localhost:8525`. |
| 2026-06-29 | Browser QA | PASS: SP500 daily workbench, SP500 weekly EOD state, NASDAQ daily/weekly empty state, and narrow viewport retained the new command strip / workbench flow. |
