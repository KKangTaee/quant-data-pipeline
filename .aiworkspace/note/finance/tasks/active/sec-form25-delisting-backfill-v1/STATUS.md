# SEC Form 25 Delisting Backfill V1 Status

## 2026-05-28

- Implementation complete.
- Added `finance/data/sec_delisting.py`.
- Added `run_collect_sec_form25_delistings()` in `app/jobs/ingestion_jobs.py`.
- Added service contract coverage for parser normalization, DB-only collector writes, and job wrapper partial coverage status.
- Target source: SEC EDGAR submissions API and Form 25 / 25-NSE filing metadata.
- Target table: `finance_meta.nyse_symbol_lifecycle`.
- Storage boundary: DB evidence only; no new workflow JSONL, memo, preset, approval, order, or rebalance write.
