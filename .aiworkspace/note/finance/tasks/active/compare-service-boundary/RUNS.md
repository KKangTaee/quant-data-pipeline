# Compare Service Boundary Runs

Status: Implementation complete
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
| `.venv/bin/python -m py_compile app/services/backtest_result_read_model.py app/services/backtest_weighted_portfolio.py app/services/backtest_compare_catalog.py app/services/backtest_compare_execution.py app/web/backtest_compare.py app/web/backtest_result_display.py` | pass | Slice 3 compile check |
| `rg "import streamlit\|from streamlit\|st\\." app/services/backtest_result_read_model.py app/services/backtest_weighted_portfolio.py app/services/backtest_compare_catalog.py app/services/backtest_compare_execution.py` | no hits | services have no direct Streamlit references |
| `.venv/bin/python -c "import sys; import app.services.backtest_result_read_model; import app.services.backtest_weighted_portfolio; print('streamlit' in sys.modules)"` | `False` | weighted portfolio service imports do not load Streamlit |
| in-memory `build_weighted_portfolio_bundle(...)` smoke | `Weighted Portfolio 4 [0.6, 0.4] 2` | verifies weighted result rows, normalized weights, and data trust rows |
| `app.web.backtest_result_display._build_strategy_data_trust_rows(...)` smoke | `A - 눈에 띄는 데이터 이슈 없음` | display wrapper delegates to read model |
| `.venv/bin/python -m py_compile app/services/backtest_saved_portfolio_replay.py app/services/backtest_weighted_portfolio.py app/services/backtest_result_read_model.py app/web/backtest_compare.py` | pass | Slice 4 compile check |
| `rg "import streamlit\|from streamlit\|st\\." app/services/backtest_saved_portfolio_replay.py app/services/backtest_weighted_portfolio.py app/services/backtest_result_read_model.py app/services/backtest_compare_catalog.py app/services/backtest_compare_execution.py` | no hits | services have no direct Streamlit references |
| `.venv/bin/python -c "import sys; import app.services.backtest_saved_portfolio_replay; print('streamlit' in sys.modules)"` | `False` | saved replay service import does not load Streamlit |
| fake `replay_saved_portfolio_record(...)` smoke | `2 Saved Portfolio: Test Mix [60.0, 40.0] saved_portfolio portfolio_test` | verifies component replay, weighted bundle, source context, and history context assembly |
| `git diff --check` | pass | no whitespace errors |
