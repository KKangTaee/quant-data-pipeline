# Runs

Status: Active
Last Updated: 2026-06-29

## RED

```bash
PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts -k market_movers_redesign_v2_phase6
PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts -k market_movers_data_trust_strip_model
PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts -k market_movers_empty_state_model_guides_no_universe
```

Result: failed as expected before implementation because compact data trust strip and empty trust hint did not exist.

## Focused GREEN

```bash
PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts -k market_movers_redesign_v2_phase6
PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts -k market_movers_data_trust_strip_model
PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts -k market_movers_empty_state_model_guides_no_universe
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
- `unittest -k market_mover`: 54 tests passed.
- `unittest -k why_it_moved`: 6 tests passed.

## Browser QA

Server:

```bash
uv run streamlit run app/web/streamlit_app.py --server.port 8525 --server.headless true
```

Result:

- SP500 Daily: compact trust strip rendered with 3 chips; grouped diagnostics remained in `Coverage trust detail`.
- SP500 Weekly: compact trust strip remained visible with Partial/Missing context.
- NASDAQ Weekly: No Universe empty state showed trust hint and `Nasdaq 목록 갱신` action.
- Narrow viewport `390x844`: no horizontal overflow; trust strip stayed within the viewport.

Screenshot:

```text
.aiworkspace/note/finance/run_artifacts/market-movers-redesign-v2-06-data-trust-qa.png
```
