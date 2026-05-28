# Phase 8 Investability Data Evidence Expansion Status

Status: Active
Created: 2026-05-28

## Current Status

- [x] Phase 8 scope confirmed with user as the first remaining phase in the 1차 hardening cycle.
- [x] Prior lifecycle work identified as Phase 8 foundation.
- [x] Phase 8 board created.
- [x] `symbol-lifecycle-event-fields-v1` implemented.
- [x] Phase 8 source review completed.
- [x] Symbol directory snapshot ingestion implemented.
- [x] SEC CIK / exchange cross-check implemented.
- [ ] Computed snapshot lifecycle design started.

## Latest Update

2026-05-28:

- Phase 8 starts after completed Phase 0~7 investability foundation work.
- Immediate implementation slice is lifecycle event semantics in DB rows.
- `nyse_symbol_lifecycle` now carries event semantics for listing-observed and delisting rows.
- `historical-membership-source-review-v1` found no free / official complete historical membership source ready for direct ingestion.
- Nasdaq Daily List is strong but subscription / approval based; the next free-source-first implementation is Nasdaq public Symbol Directory current snapshot ingestion.
- `symbol-directory-snapshot-ingestion-v1` added a DB-only collector and job wrapper for Nasdaq public current Symbol Directory files.
- `sec-cik-exchange-crosscheck-v1` added a DB-only SEC current CIK / ticker / exchange cross-check collector and job wrapper.

## Next

- Start `computed-snapshot-lifecycle-v1`.
- Define conservative repeated-snapshot evidence and scoring rules before treating computed lifecycle coverage as stronger than partial current snapshots.
