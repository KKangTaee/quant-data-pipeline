# Phase 8 Investability Data Evidence Expansion Status

Status: Active
Created: 2026-05-28

## Current Status

- [x] Phase 8 scope confirmed with user as the first remaining phase in the 1차 hardening cycle.
- [x] Prior lifecycle work identified as Phase 8 foundation.
- [x] Phase 8 board created.
- [x] `symbol-lifecycle-event-fields-v1` implemented.
- [ ] Phase 8 source review started.

## Latest Update

2026-05-28:

- Phase 8 starts after completed Phase 0~7 investability foundation work.
- Immediate implementation slice is lifecycle event semantics in DB rows.
- `nyse_symbol_lifecycle` now carries event semantics for listing-observed and delisting rows.

## Next

- Start `historical-membership-source-review-v1`.
- Decide the first free / official source for ticker actions or historical membership evidence.
