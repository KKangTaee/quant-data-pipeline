# Status

Status: Complete
Updated: 2026-06-30

## Summary

Phase 1 source contract freeze completed.

## Changed

- Added `finance/loaders/financial_source_contract.py`.
- Annotated broad fundamentals/factors loaders as `legacy_broad_yfinance`.
- Annotated statement shadow fundamentals/factors loaders as `sec_edgar_statement_shadow`.
- Preserved common filing aliases: `available_at`, `form_type`, `accession_no`.
- Added source contracts to factor strategy evidence rows.
- Passed source contract metadata through Market Movers research snapshot output.
- Updated data flow and table semantics docs.

## Next

Proceed to Phase 2 Market Movers annual EDGAR-first migration.
