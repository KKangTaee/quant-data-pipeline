# Runs

## 2026-07-07

- Started task shell.
- `.venv/bin/python -m py_compile app/web/backtest_common.py app/web/backtest_single_forms/strict_factor.py app/web/backtest_result_display.py` passed.
- Focused unittest for new strict post-run readiness contracts passed.
- `.venv/bin/python -m py_compile app/web/backtest_common.py app/web/backtest_single_forms/strict_factor.py app/web/backtest_compare/page.py app/web/backtest_result_display.py` passed.
- `.venv/bin/python -m unittest tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests` passed: 39 tests.
- `git diff --check` passed.
- `.venv/bin/python -m unittest tests.test_service_contracts` passed: 529 tests.
- Browser QA: ran Streamlit on `http://localhost:8524/backtest`, selected Single Strategy `Quality` / `Strict Annual`, and confirmed `Preset -> Universe 기준 -> post-run readiness preview -> form inputs` ordering.
- QA screenshot: `backtest-post-run-factor-readiness-v1-qa.png` generated but not staged.
