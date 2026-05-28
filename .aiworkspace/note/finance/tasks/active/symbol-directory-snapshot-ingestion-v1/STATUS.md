# Symbol Directory Snapshot Ingestion V1 Status

Status: Implementation complete
Created: 2026-05-28

## Checklist

- [x] Collector implementation
- [x] Ingestion job wrapper
- [x] Contract tests
- [x] Docs sync
- [x] Verification

## Notes

- This is Phase 8 slice 8-3.
- The collector writes DB lifecycle rows only.

## Result

- Added `finance/data/symbol_directory.py`.
- Added `run_collect_symbol_directory_snapshots()` job wrapper.
- Nasdaq `nasdaqlisted.txt` / `otherlisted.txt` rows are normalized as partial `listing_observed` lifecycle evidence.
- Test issues are skipped by default.
- No workflow JSONL, memo, preset, approval, order, or rebalance behavior was added.
