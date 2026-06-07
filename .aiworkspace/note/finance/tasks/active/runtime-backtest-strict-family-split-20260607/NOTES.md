# Notes

Status: Completed
Last Verified: 2026-06-07

## Findings

- `app/runtime/backtest.py` already acted as a compatibility facade after 8A and 8B.
- Strict annual and quarterly wrappers form a coherent family because they share strict price freshness inspection, factor / statement snapshot preflight, dynamic universe handling, rejected slot policy, and real-money hardening metadata.
- Keeping `app.runtime.backtest` as the public import path avoids churn in `app/services/backtest_execution.py`, `app/services/backtest_compare_catalog.py`, `app/web/backtest_common.py`, history helpers, candidate replay, and existing tests.
- 7A Ingestion Console split and 8C runtime strict split are independent. 7B is still a valid next candidate but does not block runtime cleanup.

## Compatibility Notes

- Representative strict facade identity smoke passed for `inspect_strict_annual_price_freshness`, quality strict annual, value strict annual, and quality-value strict annual runners.
- Existing patch points that target `app.runtime.backtest.inspect_strict_annual_price_freshness` still affect ETF facade runners because `backtest.py` imports the strict implementation into its module namespace.
