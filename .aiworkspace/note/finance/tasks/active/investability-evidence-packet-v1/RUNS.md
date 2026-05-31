# RUNS - Investability Evidence Packet V1

Status: Active
Last Updated: 2026-05-28

## Commands

| Command | Result |
| --- | --- |
| `.venv/bin/python -m py_compile app/services/backtest_evidence_read_model.py app/web/backtest_final_review_helpers.py app/web/backtest_final_review.py tests/test_service_contracts.py` | Passed |
| `.venv/bin/python -m unittest tests/test_service_contracts.py` | Passed, 26 tests |
| `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py` | Passed, hard violations none |
| `git diff --check` | Passed |
| `.venv/bin/python -m streamlit run app/web/streamlit_app.py --server.headless true --server.port 8502 --server.address 127.0.0.1` + Browser smoke | Passed: Backtest > Final Review opened, Investability Evidence Packet section rendered, console had 0 errors. Streamlit showed existing `use_container_width` deprecation warning. |
