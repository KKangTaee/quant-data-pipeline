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
- `storage-governance-audit-v1` classified JSONL write surfaces and added durable storage governance without rewriting registries.
- `data-provenance-coverage-v1` added compact provider / macro provenance and freshness read models without adding storage.
- `look-through-exposure-board-v1` added compact holdings / exposure board rows to Practical Validation and Final Review without adding storage.
- `robustness-lab-v1` added a compact Robustness Lab board for stress / rolling / sensitivity / overfit evidence without adding storage.
- `selected-monitoring-timeline-v1` added a read-only Selected Dashboard Timeline for selection, evidence gate, recheck, drift, and trigger preview signals without adding storage.
- `decision-dossier-report-v1` added a read-only markdown dossier export for saved Final Review rows and Selected Dashboard state without adding storage.

## In Progress

- Prepare phase closeout or structured waiver policy decision.

## Next

1. Decide whether to close out the phase now or open `structured-waiver-policy-v1`.
2. Decide structured waiver policy before allowing selected-route override.
3. Keep storage governance checklist mandatory before adding persistence.

## Current Defaults

- No new JSONL registry by default.
- No user memo storage.
- Main workflow JSONL chain stays limited to source / validation / final decision unless explicitly approved.
- Critical `NOT_RUN` is not pass.
- Selected route means `실전 검토 통과 후보`, not live approval.
- UI does not fetch provider or macro data directly.
- Stale provider snapshot evidence is REVIEW, not PASS.
- Look-through board rows are compact summaries; full holdings / exposure rows stay in DB.
- Robustness Lab rows are compact summaries; raw run history and strategy-specific perturbation artifacts are not stored in JSONL.
- Selected Monitoring Timeline rows are read-only summaries from existing final decision and session-state checks; they are not monitoring log writes.
- Decision Dossier markdown is a user-initiated export string; the UI does not auto-write report files.
