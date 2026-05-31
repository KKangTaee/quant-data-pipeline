# Symbol Directory Snapshot Ingestion V1 Notes

Status: Active
Created: 2026-05-28

## Source Contract

- Source files:
  - `https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt`
  - `https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt`
- These are current snapshots.
- They are not historical membership or delisting feeds.
- Rows must remain `coverage_status=partial`.

## Implementation Notes

- Source `nasdaqlisted` writes `source=nasdaq_symdir_nasdaqlisted`.
- Source `otherlisted` writes `source=nasdaq_symdir_otherlisted`.
- Both sources use `source_type=current_listing_snapshot`, `event_type=listing_observed`, and `coverage_status=partial`.
- File creation date is used as `event_date` when available; otherwise collection date is used.
- Missing from a current file is not interpreted as delisting.
