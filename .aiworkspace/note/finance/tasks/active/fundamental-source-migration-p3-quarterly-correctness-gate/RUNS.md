# Phase 3. Quarterly Correctness Gate Runs

## TDD RED

```bash
uv run python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_quarterly_statement_policy_filters_unsafe_10k_rows tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_quarterly_statement_policy_clears_unsafe_10k_flow_values tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_statement_fundamentals_shadow_loader_filters_quarterly_10k_rows tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_statement_factors_shadow_loader_joins_form_type_and_filters_quarterly_10k_rows
```

Result: failed as expected. Missing `finance.financial_source_policy`, fundamentals loader returned 10-K quarterly row, and factors loader did not join `nyse_fundamentals_statement`.

## Verification

```bash
uv run python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_quarterly_statement_policy_filters_unsafe_10k_rows tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_quarterly_statement_policy_clears_unsafe_10k_flow_values tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_statement_fundamentals_shadow_loader_filters_quarterly_10k_rows tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_statement_factors_shadow_loader_joins_form_type_and_filters_quarterly_10k_rows
```

Result: passed, 4 tests.

```bash
uv run python -m py_compile finance/financial_source_policy.py finance/data/fundamentals.py finance/loaders/fundamentals.py finance/loaders/factors.py app/runtime/backtest_strict.py
```

Result: passed.

```bash
uv run --with pytest python -m pytest tests/test_service_contracts.py -q -k "financial_source_policy or statement_fundamentals_shadow_loader or statement_factors_shadow_loader or market_mover or fundamental or factor"
```

Result: passed, 69 tests selected, 425 deselected, 3 edgar deprecation warnings.

```bash
git diff --check
```

Result: passed.

```bash
uv run python -m py_compile finance/data/financial_statements.py finance/data/fundamentals.py finance/data/factors.py finance/loaders/financial_statements.py finance/loaders/fundamentals.py finance/loaders/factors.py finance/financial_source_policy.py
```

Result: passed.

```bash
uv run --with pytest python -m pytest tests/test_service_contracts.py -q -k "financial_statement or statement_shadow or quarterly or factor"
```

Result: passed, 5 tests selected, 489 deselected.

```sql
SELECT latest_form_type, COUNT(*) rows_count, COUNT(DISTINCT symbol) symbols
FROM finance_fundamental.nyse_fundamentals_statement
WHERE freq='quarterly'
GROUP BY latest_form_type;
```

Result:

| latest_form_type | rows_count | symbols |
|---|---:|---:|
| 10-K | 14538 | 987 |
| 10-K/A | 91 | 46 |
| 10-Q | 43284 | 984 |
| 10-Q/A | 405 | 125 |
