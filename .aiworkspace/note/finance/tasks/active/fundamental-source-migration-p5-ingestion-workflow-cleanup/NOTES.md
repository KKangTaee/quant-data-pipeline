# Phase 5. Ingestion Workflow Cleanup Notes

- The workflow change is product-facing, not a diagnostic-only panel. The UI now answers which refresh to run first and what to do after a partial result.
- The legacy broad yfinance path remains available because old saved runs and history replay can still need `nyse_fundamentals` / `nyse_factors`.
- The EDGAR card still uses `extended_statement_refresh` internally to avoid breaking run history and scheduled-action compatibility.
- The result summary intentionally avoids treating raw row count as the main success signal; coverage and freshness interpretation are more useful to the operator.
