# Symbol Directory Snapshot Ingestion V1 Risks

Status: Active
Created: 2026-05-28

## Risks

- Current snapshot rows can be over-interpreted as historical membership.
- Missing current file rows can be over-interpreted as delisting.
- Exchange code semantics in `otherlisted.txt` need careful future mapping if used in UI.

## Mitigation

- Store rows only as `listing_observed` partial evidence.
- Preserve source limitations in collector summary.
- Keep Data Coverage Audit PASS criteria unchanged.

## Remaining Gaps

- Symbol Directory current snapshots do not create historical survivorship PASS evidence.
- Repeated snapshot diff logic is still pending in `computed-snapshot-lifecycle-v1`.
- SEC CIK / exchange cross-check remains pending in `sec-cik-exchange-crosscheck-v1`.
