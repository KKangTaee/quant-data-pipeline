# SEC CIK Exchange Crosscheck V1 Status

Status: Implementation complete
Created: 2026-05-28

## Checklist

- [x] Collector implementation
- [x] Ingestion job wrapper
- [x] Contract tests
- [x] Docs sync
- [x] Verification

## Notes

- This is Phase 8 slice 8-4.
- The collector writes DB lifecycle rows only.

## Result

- Added `finance/data/sec_company_tickers.py`.
- Added `run_collect_sec_company_ticker_crosscheck()` job wrapper.
- SEC current CIK / ticker / exchange associations are normalized as partial `listing_observed` lifecycle evidence.
- `related_cik` carries the SEC CIK for identity cross-checking.
- No workflow JSONL, memo, preset, approval, order, or rebalance behavior was added.
