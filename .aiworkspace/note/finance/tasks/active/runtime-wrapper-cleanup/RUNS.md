# Runtime Wrapper Cleanup Runs

Status: Active
Created: 2026-05-27

## 2026-05-27

| Command | Result |
| --- | --- |
| `git status --short --untracked-files=all` | Clean before Task 8 |
| `wc -l app/runtime/backtest.py` | `5191` lines |
| `rg -n "^def \|^class \|^[A-Z_]+\\s*=" app/runtime/backtest.py` | Identified public errors, constants, helper families, and `run_*_backtest_from_db` wrappers |
| `rg -n "run_.*_backtest_from_db\|from app\\.runtime\\.backtest\|import app\\.runtime\\.backtest\|app\\.runtime\\.backtest" app tests finance .aiworkspace/note/finance/docs -g '*.py' -g '*.md'` | Identified direct public runtime callers in services, runtime package export, candidate library, web helper modules, tests, and docs |
| `rg -n "build_backtest_result_bundle\|BacktestInputError\|BacktestDataError\|STRICT_BENCHMARK_CONTRACT_CANDIDATE_EQUAL_WEIGHT\|inspect_strict_annual_price_freshness" app tests -g '*.py'` | Confirmed result bundle, error classes, strict benchmark constant, freshness helper, and public wrappers are external compatibility surface |
| `.venv/bin/python -m py_compile app/runtime/backtest_result_bundle.py app/runtime/backtest.py tests/test_service_contracts.py` | PASS |
| `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py` | PASS, hard violations none, advisories none |
| `.venv/bin/python -m unittest tests.test_service_contracts` | PASS, 21 tests |
| `git diff --check && wc -l app/runtime/backtest.py app/runtime/backtest_result_bundle.py` | PASS; `app/runtime/backtest.py` 4995 lines, `app/runtime/backtest_result_bundle.py` 206 lines |
| Browser QA | Not run; helper split keeps public runtime API and does not change visible Streamlit layout / interaction |
