# Runs

Commands and outcomes will be appended during verification.

## 2026-05-30

- `.venv/bin/python -m py_compile app/web/backtest_compare.py`
  - Passed.
- `git diff --check`
  - Passed.
- `.venv/bin/python -m pytest tests/test_service_contracts.py`
  - Not run: local venv has no `pytest` module.
- `.venv/bin/python -m unittest tests.test_service_contracts`
  - Passed, 133 tests.
- Browser smoke on `http://127.0.0.1:8502/backtest`
  - Loaded Backtest page, opened `Portfolio Mix Builder`, verified step strip renders as real UI rather than Markdown code.
  - Ran default `Equal Weight + GTAA` component execution.
  - Confirmed post-run UI exposes `요약 / 차트 / 진단 / 상세`, keeps raw component summary behind an expander, and no longer shows the old 9-tab overlay labels.
