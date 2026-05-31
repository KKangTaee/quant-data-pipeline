# Concentration / Overlap / Exposure Contract V1 Design

Status: Complete
Created: 2026-05-29

## Contract

`construction_risk_audit_v1` is a read-only audit contract.

Primary fields:

- `route`
- `route_label`
- `overall_status`
- `source_strength`
- `rows`
- `metrics`
- `limitations`
- `execution_boundary`

## Rows

| Row | Source | Strong PASS Requirement |
| --- | --- | --- |
| Component weight concentration | Practical Validation metrics / concentration diagnostic | active components and max component weight below review line |
| Provider look-through coverage | provider `look_through_board` | holdings and exposure coverage both available and board status `PASS` |
| Top holding concentration | provider holdings compact metrics | holdings coverage available and top holding at or below review line |
| Holdings overlap | provider holdings compact metrics | holdings coverage available and top overlap at or below review line |
| Asset bucket exposure | provider exposure compact metrics | exposure coverage available, no unknown exposure, dominant asset below review line |
| Storage / execution boundary | static boundary | always PASS unless contract changes |

## Route Semantics

| Route | Meaning |
| --- | --- |
| `CONSTRUCTION_RISK_READY` | concentration / overlap / exposure evidence is provider-backed and no immediate review trigger is present |
| `CONSTRUCTION_RISK_REVIEW` | evidence exists but review trigger or partial source strength remains |
| `CONSTRUCTION_RISK_NEEDS_INPUT` | holdings / exposure / provider source is missing or proxy-only |
| `CONSTRUCTION_RISK_BLOCKED` | source contract itself is invalid |

## Boundary

11-2 does not enforce selected-route gate policy. It only creates a gate-ready contract.
Final Review selected-route policy ownership remains 11-5.
