# Computed Snapshot Lifecycle V1 Notes

Status: Active
Created: 2026-05-28

## Findings

- Existing current snapshot collectors already UPSERT one row per `(symbol, kind, source)` and preserve `first_seen_date` / `last_seen_date`.
- This means repeated collection can create a wider observed window without storing every raw snapshot.
- The observed window is evidence of repeated active observation, not complete membership proof for dates between observations.

## Policy

- Computed rows can summarize observation range and source agreement.
- Computed rows must not infer delisting from missing rows.
- In Phase 8-5, computed rows remain `coverage_status=partial`.
- Data Coverage Audit should only treat computed rows as PASS candidates if the row is explicitly `coverage_status=actual`.
