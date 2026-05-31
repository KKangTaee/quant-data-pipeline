# Look-through Exposure Board V1 Runs

Status: Complete
Created: 2026-05-28

## Commands

| Command | Result |
|---|---|
| `git status --short` | Only pre-existing `finance/.DS_Store` modification was present before this task. |
| `rg -n "provider_coverage|Provider Coverage|holdings|exposure" app/web app/services tests/test_service_contracts.py` | Located provider context, Practical Validation / Final Review display, and service contract tests. |
| `sed -n ... docs/ROADMAP.md docs/PROJECT_MAP.md phases/.../TASKS.md` | Confirmed next task is `look-through-exposure-board-v1`. |

## Verification

| Command | Result |
|---|---|
| `.venv/bin/python -m py_compile app/services/backtest_practical_validation_provider_context.py app/services/backtest_practical_validation_diagnostics.py app/services/backtest_evidence_read_model.py app/web/backtest_practical_validation.py app/web/backtest_final_review.py app/web/backtest_final_review_helpers.py tests/test_service_contracts.py` | Passed during implementation. |
| `.venv/bin/python -m unittest tests/test_service_contracts.py` | Passed, 29 tests. Third-party `edgar` deprecation warnings only. |
| `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py` | Passed. No hard violations or advisories. |
| `git diff --check` | Passed. |
| `.venv/bin/python -m streamlit run app/web/streamlit_app.py --server.address 127.0.0.1 --server.port 8502` + Browser smoke | Passed. Root -> Backtest -> Practical Validation -> Final Review navigation loaded with 0 browser console errors. Direct `/backtest` URL showed transient Streamlit `_stcore` relative-path 404 before using normal root navigation. |
