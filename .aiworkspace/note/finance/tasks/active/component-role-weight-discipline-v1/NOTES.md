# Component Role / Weight Discipline V1 Notes

Status: Active
Created: 2026-05-29

## Notes

- Existing weighted / saved mix handoff can carry `proposal_role`, `target_weight`, and `weight_reason`.
- Existing validation profile already has `max_weight_review` and profile answers such as `primary_goal`.
- Single-strategy sources may not have explicit role metadata; V1 should show that as source weakness rather than creating a saved role preset.
- V1 separates explicit role metadata from inferred role category. Inference helps display, but missing explicit role source does not become ready.
- No new JSONL registry, user memo, role preset, saved setup, approval, order, or auto rebalance path was added.
