# Runs

Status: Active
Last Updated: 2026-06-29

## RED

```bash
PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts -k market_movers_redesign_v2_phase2
PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts -k market_mover_board_model
```

Result: failed as expected because `build_market_mover_board_model` and the board renderer did not exist.

## Focused GREEN

```bash
PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts -k market_movers_redesign_v2_phase2
PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts -k market_mover_board_model
uv run python -m py_compile app/web/overview/market_movers_helpers.py app/web/overview/components/market_movers.py
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
- `unittest -k market_mover`: 46 tests passed.
- `unittest -k why_it_moved`: 6 tests passed.

## Browser QA

Server:

```bash
uv run streamlit run app/web/streamlit_app.py --server.port 8525 --server.headless true
```

Result:

- SP500 Daily: board rendered first with 5 tape cells, 20 compact list rows, and `상세 표로 보기`.
- SP500 Weekly: board rendered with 5 tape cells and 20 list rows; EOD refresh flow remained visible.
- NASDAQ: no board rendered for `No Universe`; empty/trust state and `Nasdaq 목록 갱신` remained visible.
- Narrow viewport `390x844`: no horizontal overflow; board, tape, and list rows present.

Screenshot:

```text
.aiworkspace/note/finance/run_artifacts/market-movers-redesign-v2-02-board-qa.png
```
