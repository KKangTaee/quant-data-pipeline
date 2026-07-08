# Runs

Status: Active
Last Updated: 2026-06-29

## RED

```bash
PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts -k market_movers_redesign_v2_phase3
PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts -k market_mover_chart_workspace_model
```

Result: failed as expected before implementation because the chart workspace model and renderer did not exist.

## Focused GREEN

```bash
PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts -k market_movers_redesign_v2_phase3
PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts -k market_mover_chart_workspace_model
uv run python -m py_compile app/web/overview/market_movers_helpers.py app/web/overview/components/market_movers.py app/web/overview/components/common.py
```

Result: passed.

## Common Verification

```bash
git diff --check
uv run python -m py_compile app/web/overview/market_movers.py app/web/overview/market_movers_helpers.py app/web/overview/components/market_movers.py app/services/overview/market_movers.py app/services/overview/why_it_moved.py
uv run python -m pytest tests/test_service_contracts.py -q -k "market_mover or market_movers or why_it_moved"
PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts -k market_mover
PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts -k why_it_moved
```

Result:

- `git diff --check`: passed.
- `py_compile`: passed.
- `pytest`: failed because `pytest` is not installed in the venv.
- `unittest -k market_mover`: 48 tests passed.
- `unittest -k why_it_moved`: 6 tests passed.

## Browser QA

Server:

```bash
uv run streamlit run app/web/streamlit_app.py --server.port 8525 --server.headless true
```

Result:

- SP500 Daily: chart workspace rendered with title, metric badge, row count, top symbol, and metric range.
- SP500 Weekly: chart workspace remained visible while coverage trust changed to Partial.
- NASDAQ Weekly: workspace did not render for `No Universe`; empty/trust state remained visible.
- Narrow viewport `390x844`: no horizontal overflow; workspace facts collapsed within the viewport.

Screenshot:

```text
.aiworkspace/note/finance/run_artifacts/market-movers-redesign-v2-03-chart-workspace-qa.png
```
