# Notes

## Source Contract Shape

The loader source contract columns are:

- `source`
- `financial_source`
- `financial_source_mode`
- `source_table`
- `source_detail`
- `available_at`
- `form_type`
- `accession_no`

Broad yfinance rows intentionally keep filing aliases empty because those tables do not carry filing metadata. Statement shadow rows map `latest_available_at`, `latest_form_type`, `latest_accession_no`, `fundamental_available_at`, and `fundamental_accession_no` into the common aliases where available.

## Current Interpretation

- `legacy_broad_yfinance`: compatibility / fallback / old run support.
- `sec_edgar_statement_shadow`: EDGAR raw ledger rebuild path and canonical candidate for annual.
- strict quarterly remains non-canonical until Phase 3 blocks or corrects 10-K/FY flow-value mixing.
