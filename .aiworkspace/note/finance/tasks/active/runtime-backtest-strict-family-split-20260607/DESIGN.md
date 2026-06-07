# Design

Status: Completed
Last Verified: 2026-06-07

## Module Boundary

`app/runtime/backtest.py` remains the public runtime compatibility facade.

It still owns the price-only ETF wrapper family:

- `run_equal_weight_backtest_from_db`
- `run_gtaa_backtest_from_db`
- `run_global_relative_strength_backtest_from_db`
- `run_risk_parity_trend_backtest_from_db`
- `run_dual_momentum_backtest_from_db`

Strict factor / fundamental wrapper implementation moved to `app/runtime/backtest_strict.py`:

- `inspect_strict_annual_price_freshness`
- `run_quality_snapshot_backtest_from_db`
- `run_quality_snapshot_strict_annual_backtest_from_db`
- `run_statement_quality_prototype_backtest_from_db`
- `run_value_snapshot_strict_annual_backtest_from_db`
- `run_value_snapshot_strict_quarterly_prototype_backtest_from_db`
- `run_quality_value_snapshot_strict_annual_backtest_from_db`
- `run_quality_value_snapshot_strict_quarterly_prototype_backtest_from_db`
- `run_quality_snapshot_strict_quarterly_prototype_backtest_from_db`

## Compatibility Contract

Existing callers can continue importing from `app.runtime.backtest`.

```python
from app.runtime.backtest import run_quality_snapshot_strict_annual_backtest_from_db
```

The facade imports the function from `app.runtime.backtest_strict` and re-exports it.
The focused test asserts identity between the facade export and the strict module implementation.

## Cycle Avoidance

`app/runtime/backtest_strict.py` does not top-level import `app.runtime.backtest`.
It uses local lazy error factories for `BacktestInputError` and `BacktestDataError` so the facade can import strict exports without circular initialization.

## 7B Relationship

The user noticed 7차 may not be fully complete.
That is correct: 7A physical Ingestion Console split is complete, but Ingestion diagnostic facade extraction remains a separate candidate.
8C is independent because it only changes `app/runtime/backtest*.py` and service contract docs/tests, not `app/web/ingestion_console.py` diagnostics.
