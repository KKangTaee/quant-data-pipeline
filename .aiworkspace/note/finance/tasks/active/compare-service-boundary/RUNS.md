# Compare Service Boundary Runs

Status: In progress
Created: 2026-05-19

## Commands

| Command | Result | Notes |
| --- | --- | --- |
| `.venv/bin/python -m py_compile app/services/backtest_compare_execution.py app/web/backtest_compare.py` | pass | syntax / import-time compile |
| `rg "import streamlit\|from streamlit\|st\\." app/services/backtest_compare_execution.py` | no hits | service has no Streamlit references |
| `.venv/bin/python -c "from app.services.backtest_compare_execution import execute_strategy_compare; print(callable(execute_strategy_compare))"` | `True` | import smoke |
| fake runner success smoke | `True 2 {'x': 1}` | verifies loop and per-strategy override forwarding |
| fake `BacktestInputError` smoke | `False input Comparison input issue: bad compare input` | verifies input error normalization |
| `.venv/bin/python -c "import sys; import app.services.backtest_compare_execution; print('streamlit' in sys.modules)"` | `False` | service import does not load Streamlit |
| `git diff --check` | pass | no whitespace errors |
| `.venv/bin/python -m py_compile app/services/backtest_compare_catalog.py app/services/backtest_compare_execution.py app/web/backtest_compare.py` | pass | Slice 2 compile check |
| `rg "import streamlit\|from streamlit\|st\\." app/services/backtest_compare_catalog.py app/services/backtest_compare_execution.py` | no hits | services have no direct Streamlit references |
| `.venv/bin/python -c "import sys; import app.services.backtest_compare_catalog; import app.services.backtest_compare_execution; print('streamlit' in sys.modules)"` | `False` | service imports do not load Streamlit |
| invalid strategy smoke for `run_compare_strategy(...)` | `Unsupported compare strategy: Not A Strategy` | service preserves input error path |
| UI `_compare_preset_catalog()` smoke | `True True` | UI wrapper exposes current preset catalog to service |
