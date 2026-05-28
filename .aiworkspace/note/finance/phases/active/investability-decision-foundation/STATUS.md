# Investability Decision Foundation Status

Status: Active
Last Updated: 2026-05-28

## Current Status

- Phase opened from `2026-05-investable-workflow-gap-analysis` recommendation and user approval.
- `investability-evidence-packet-v1` has already landed as the first narrow implementation slice.
- Phase 0 is now defining the policy baseline around storage, validation gates, data acquisition, wording, and task order.

## Completed

- Product gap analysis completed under `.aiworkspace/note/finance/researches/active/2026-05-investable-workflow-gap-analysis/`.
- Final Review now has an Investability Evidence Packet and selected-route gate.
- Final decision row stores a compact packet snapshot without adding a new JSONL registry.
- `validation-gate-hardening-v1` implemented a profile-aware gate policy matrix and compact `gate_policy_snapshot`.

## In Progress

- Decide whether the next task should be storage governance audit or data provenance / coverage.

## Next

1. Review whether to start `storage-governance-audit-v1` before data provenance work.
2. Decide structured waiver policy before allowing selected-route override.
3. Use `data-provenance-coverage-v1` before strict look-through board work.

## Current Defaults

- No new JSONL registry by default.
- No user memo storage.
- Critical `NOT_RUN` is not pass.
- Selected route means `실전 검토 통과 후보`, not live approval.
- UI does not fetch provider or macro data directly.
