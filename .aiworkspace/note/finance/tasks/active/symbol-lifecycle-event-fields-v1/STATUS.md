# Symbol Lifecycle Event Fields V1 Status

Status: Implementation complete
Created: 2026-05-28

## Checklist

- [x] Schema update
- [x] NYSE listing snapshot writer update
- [x] SEC Form 25 writer update
- [x] Loader update
- [x] Tests update
- [x] Docs sync
- [x] Verification

## Notes

- This task is Phase 8 slice 8-1.
- No workflow JSONL, memo, preset, approval, order, or rebalance behavior should be added.

## Result

- `nyse_symbol_lifecycle` now accepts nullable event semantics through `event_type`, `event_date`, `related_symbol`, and `related_cik`.
- NYSE current listing rows are `event_type=listing_observed` partial evidence.
- SEC Form 25 rows are `event_type=delisting` actual delisting evidence.
- `finance/loaders/universe.py` returns the new event fields in compact lifecycle summaries.
