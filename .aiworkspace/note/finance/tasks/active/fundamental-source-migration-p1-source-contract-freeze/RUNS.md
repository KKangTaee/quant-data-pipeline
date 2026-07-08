# Runs

## 2026-06-30 TDD Red

Initial `pytest` attempt:

```bash
uv run python -m pytest tests/test_service_contracts.py -q -k "financial_source_contract or market_mover_research_snapshot_reads_existing_db_loaders"
uv run python -m pytest tests/test_backtest_strategy_evidence_inventory.py -q -k "source_contract"
```

Result: exit 1 before test execution because local `.venv` did not have `pytest` installed.

Red verification was then run with `unittest`:

```bash
uv run python -m unittest tests.test_service_contracts -k "financial_source_contract"
uv run python -m unittest tests.test_service_contracts -k "market_mover_research_snapshot_reads_existing_db_loaders"
uv run python -m unittest tests.test_backtest_strategy_evidence_inventory -k "source_contract"
```

Expected failures:

- `ModuleNotFoundError: No module named 'finance.loaders.financial_source_contract'`
- `KeyError: 'financial_source'`
- `KeyError: 'source_contract'`

## 2026-06-30 Green / Verification

### Compile

```bash
uv run python -m py_compile finance/loaders/fundamentals.py finance/loaders/factors.py app/services/overview/why_it_moved.py
```

Result: exit 0.

### Focused unittest

```bash
uv run python -m unittest tests.test_service_contracts -k "financial_source_contract"
uv run python -m unittest tests.test_service_contracts -k "market_mover_research_snapshot_reads_existing_db_loaders"
uv run python -m unittest tests.test_backtest_strategy_evidence_inventory -k "source_contract"
```

Result: all selected tests passed.

### Guide-style filtered pytest

```bash
uv run --with pytest python -m pytest tests/test_service_contracts.py tests/test_backtest_strategy_evidence_inventory.py -q -k "fundamental or fundamentals or factor or statement or why_it_moved or strategy_evidence or financial_source_contract"
```

Result: exit 0, `13 passed, 482 deselected, 3 warnings`.

Warnings: existing `edgar` deprecation warnings for upcoming v6 parser migration.

### Whitespace

```bash
git diff --check
```

Result: exit 0.
