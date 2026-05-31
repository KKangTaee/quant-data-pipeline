# Computed Snapshot Lifecycle V1 Risks

Status: Active
Created: 2026-05-28

## Open Risks

- Repeated current snapshots are not a full historical listing feed.
- A symbol missing from a later current snapshot may reflect source coverage, ticker change, data issue, or delisting; this task does not infer which one.
- Historical survivorship PASS still requires actual historical listing / delisting evidence, or a future computed source that can defensibly mark `coverage_status=actual`.
