# Phase 4. Backtest Strategy Migration Runs

## TDD RED

```bash
uv run python -m unittest tests.test_backtest_strategy_evidence_inventory.BacktestStrategyEvidenceInventoryContractTests.test_strategy_catalog_defaults_prioritize_statement_annual_family tests.test_backtest_strategy_evidence_inventory.BacktestStrategyEvidenceInventoryContractTests.test_backtest_ui_uses_catalog_defaults_for_primary_strategy_surfaces
```

Result: failed as expected. Catalog default constants did not exist and UI code did not use them.

## Verification

```bash
uv run python -m unittest tests.test_backtest_strategy_evidence_inventory.BacktestStrategyEvidenceInventoryContractTests.test_strategy_catalog_defaults_prioritize_statement_annual_family tests.test_backtest_strategy_evidence_inventory.BacktestStrategyEvidenceInventoryContractTests.test_backtest_ui_uses_catalog_defaults_for_primary_strategy_surfaces
```

Result: passed, 2 tests.

```bash
uv run python -m py_compile app/runtime/backtest_strict.py app/runtime/backtest.py app/runtime/candidate_library.py app/services/backtest_strategy_catalog.py app/services/backtest_strategy_evidence_inventory.py app/services/backtest_execution.py app/services/backtest_compare_catalog.py app/web/backtest_common.py app/web/backtest_single_forms.py app/web/backtest_single_strategy.py app/web/backtest_compare.py app/web/backtest_history_helpers.py app/web/backtest_strategy_catalog.py
```

Result: passed.

```bash
uv run --with pytest python -m pytest tests/test_backtest_strategy_evidence_inventory.py tests/test_service_contracts.py -q -k "backtest or strategy_catalog or strategy_evidence or candidate_library or strict_annual"
```

Result: passed, 40 tests selected, 462 deselected, 3 edgar deprecation warnings.

## Browser QA

```text
http://localhost:8525/backtest
```

Result: passed after restarting the local Streamlit process. Single Strategy default was `Quality + Value / Strict Annual`; Portfolio Mix Builder default was `Quality + Value`, `GTAA`, `Equal Weight`.

Generated screenshot: `.aiworkspace/note/finance/run_artifacts/backtest_statement_annual_default_20260630.png`
