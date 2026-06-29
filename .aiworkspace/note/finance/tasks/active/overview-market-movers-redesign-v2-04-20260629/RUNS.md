# Runs

Status: Active
Last Updated: 2026-06-29

## RED

```bash
PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts -k market_movers_redesign_v2_phase4
PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts -k market_movers_sector_map_model
```

Result: failed as expected before implementation because the sector market map model and renderer did not exist.

## Focused GREEN

```bash
PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts -k market_movers_redesign_v2_phase4
PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts -k market_movers_sector_map_model
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
- `unittest -k market_mover`: 50 tests passed.
- `unittest -k why_it_moved`: 6 tests passed.

## Browser QA

Server:

```bash
uv run streamlit run app/web/streamlit_app.py --server.port 8525 --server.headless true
```

Result:

- SP500 Daily: sector market map rendered with 11 lanes, 5 leader strip items, and context-only boundary text.
- SP500 Weekly: sector market map remained visible with 11 lanes.
- NASDAQ Weekly: no sector map rendered for `No Universe`; empty/trust state remained visible.
- Narrow viewport `390x844`: no horizontal overflow; sector lanes collapsed within the viewport.

Screenshot:

```text
.aiworkspace/note/finance/run_artifacts/market-movers-redesign-v2-04-sector-map-qa.png
```
