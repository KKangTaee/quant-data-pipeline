# SEC Form 25 Ingestion UI V1 Status

## 2026-05-28

- Implementation complete.
- Target surface: `Workspace > Ingestion > Practical Validation Provider Snapshots`.
- Added `Delisting Evidence` tab that schedules `collect_sec_form25_delistings`.
- Added UI copy that Form 25 absence is not active proof and full historical membership remains separate.
- Storage boundary: uses existing DB collector only; no new workflow JSONL / memo / preset / report / approval / order / rebalance feature.
