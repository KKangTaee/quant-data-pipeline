# Construction Risk Gate Policy V1 Design

Status: Complete
Created: 2026-05-29

## Contract

Final Review selected-route gate policy now treats the three construction risk audit routes as critical groups:

| Audit | Gate Group | Ready Route | Non-ready Treatment |
| --- | --- | --- | --- |
| Construction Risk Audit | `construction_risk` | `CONSTRUCTION_RISK_READY` | `NEEDS_INPUT` / `BLOCKED` = blocker, `REVIEW` = review-required |
| Risk Contribution Audit | `risk_contribution` | `RISK_CONTRIBUTION_READY` | `NEEDS_INPUT` / `BLOCKED` = blocker, `REVIEW` = review-required |
| Component Role / Weight Audit | `component_role_weight` | `COMPONENT_ROLE_WEIGHT_READY` | `NEEDS_INPUT` / `BLOCKED` = blocker, `REVIEW` = review-required |

## Implementation

- Added labels, required actions, section mapping, and critical group membership for the three audit groups in `build_investability_gate_policy()`.
- Added investability packet check rows for the three audit routes.
- Passed the three audit payloads into the gate policy snapshot.
- Reused `_merge_audit_rows_into_policy()` so non-PASS row criteria, status, current value, meaning, and next action become gate policy evidence.
- Remapped existing `concentration_overlap_exposure` and `correlation_diversification_risk_contribution` diagnostic findings to the new construction-specific gate groups so they do not duplicate under generic provider / stress groups.

## Storage Boundary

No new storage path was added.

- DB write: no
- JSONL registry write: no
- saved setup / preset write: no
- user memo write: no
- live approval / order / auto rebalance: no
