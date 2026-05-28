# Decision Dossier Report V1 Runs

Status: Active
Created: 2026-05-28

## Commands

- `.venv/bin/python -m py_compile app/services/backtest_evidence_read_model.py app/web/backtest_final_review.py app/web/final_selected_portfolio_dashboard.py tests/test_service_contracts.py` - PASS.
- `.venv/bin/python -m unittest tests/test_service_contracts.py` - PASS, 34 tests. Deprecation warnings from `edgar` only.
- `git diff --check` - PASS.
- `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py` - PASS, hard violations none, advisories none.
- `.venv/bin/python -m streamlit run app/web/streamlit_app.py --server.port 8502 --server.headless true` + Browser smoke - PASS.
  - `Operations > Selected Portfolio Dashboard` loaded from top nav with empty selected registry state and no console errors.
  - `Backtest > Final Review` loaded from top nav with current candidate data and no console errors.
  - Current final decision records were 0, so saved-row dossier interaction was covered by service contract tests rather than populated browser data.
  - Terminal showed an existing Streamlit `use_container_width` deprecation warning outside this task's changed code.
