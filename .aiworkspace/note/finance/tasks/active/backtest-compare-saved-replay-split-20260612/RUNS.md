# Backtest Compare Saved Replay Split 6A Runs

## 2026-06-12

- `git status --short`
  - Existing local changes before 6A: `.aiworkspace/note/finance/saved/SELECTED_DASHBOARD_PORTFOLIOS.jsonl`, `finance/.DS_Store`, untracked `.aiworkspace/note/finance/run_history/BACKTEST_RUN_HISTORY.jsonl`.
  - Decision: keep generated/user-state artifacts unstaged.
- `.venv/bin/python -m unittest tests.test_service_contracts.BoundaryContractHardeningTests.test_backtest_compare_delegates_saved_replay_to_dedicated_module tests.test_service_contracts.BoundaryContractHardeningTests.test_backtest_compare_saved_replay_module_owns_render_entrypoint -v`
  - First run before implementation: failed as expected because `app.web.backtest_compare_saved_replay` did not exist and `backtest_compare.py` still owned saved replay functions.
  - Post-implementation run: passed.
- `.venv/bin/python -m py_compile app/web/backtest_compare.py app/web/backtest_compare_saved_replay.py app/web/backtest_compare_components.py tests/test_service_contracts.py`
  - Passed.
- `.venv/bin/python -m unittest tests.test_service_contracts -v`
  - Ran 304 tests with one failure outside 6A: `FuturesMacroThermometerContractTests.test_macro_thermometer_inverts_rates_and_fx_pressure` expected `OK` but current service returned `REVIEW`.
  - Isolated the same test and confirmed it fails independently without touching macro thermometer code.
- `.venv/bin/python -m unittest tests.test_service_contracts.BoundaryContractHardeningTests -v`
  - Passed. Streamlit/edgar deprecation warnings only.
- `git diff --check`
  - Passed.
- `.venv/bin/python -m streamlit run app/web/streamlit_app.py --server.port 8501 --server.headless true`
  - Started local UI for Browser QA. Direct `.venv/bin/streamlit` script has a stale interpreter path, so module invocation was used.
- Browser QA on `http://localhost:8501/backtest`
  - Navigated to Backtest Analysis, switched to Portfolio Mix Builder, opened `저장된 Mix`, and confirmed saved Mix table, replay parity snapshot, real-money / guardrail scope, and `Mix 재실행 및 검증` controls render.
  - Screenshot: `.aiworkspace/note/finance/run_artifacts/backtest_compare_saved_replay_6a_qa.png`.
- Final rerun after docs sync:
  - `.venv/bin/python -m py_compile app/web/backtest_compare.py app/web/backtest_compare_saved_replay.py app/web/backtest_compare_components.py tests/test_service_contracts.py`: passed.
  - `.venv/bin/python -m unittest tests.test_service_contracts.BoundaryContractHardeningTests -v`: passed, 15 tests. Third-party `edgar` deprecation warnings and Streamlit cache warning only.
  - `git diff --check`: passed.
