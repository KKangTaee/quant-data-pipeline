# Backtest Boundary Refactor V1 Runs

Command log for staged QA.

## 1차

- RED: `.venv/bin/python -m unittest tests.test_backtest_refactor_boundaries -v`
  - Expected failure: missing `app.web.backtest_state`, missing `app.web.backtest_formatters`, and `backtest_page.py` still importing from `backtest_common.py`.
- GREEN QA: `.venv/bin/python -m unittest tests.test_backtest_refactor_boundaries -v`
  - Result: PASS.
- Compile: `.venv/bin/python -m py_compile app/web/backtest_page.py app/web/backtest_state.py app/web/backtest_formatters.py app/web/backtest_common.py`
  - Result: PASS.
- Diff check: `git diff --check`
  - Result: PASS.
