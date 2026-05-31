# Component Role / Weight Discipline V1 Design

Status: Complete
Created: 2026-05-29

## Contract

`component_role_weight_audit_v1` is a read-only audit contract.

Primary fields:

- `route`
- `route_label`
- `overall_status`
- `source_strength`
- `rows`
- `metrics`
- `component_rows`
- `limitations`
- `execution_boundary`

## Rows

| Row | Source | Strong PASS Requirement |
| --- | --- | --- |
| Component role source coverage | `selection_source_snapshot.components` role fields | active components have explicit role metadata |
| Profile-aware weight discipline | validation profile threshold and target weights | total 100% and max component weight under profile review line |
| Role concentration discipline | normalized role category weights | no single role category exceeds profile role review line |
| Profile intent role fit | validation profile answers and role categories | defensive / hedged / growth intent has matching role evidence |
| Weight rationale coverage | component `weight_reason` / source construction | multi-component source has compact weight rationale |
| Storage / execution boundary | static boundary | read-only, no memo / preset / approval / order behavior |

## Route Semantics

| Route | Meaning |
| --- | --- |
| `COMPONENT_ROLE_WEIGHT_READY` | role source, profile fit, and weight discipline are present without immediate review trigger |
| `COMPONENT_ROLE_WEIGHT_REVIEW` | evidence exists but role concentration, profile fit, or rationale needs review |
| `COMPONENT_ROLE_WEIGHT_NEEDS_INPUT` | role source or weight rationale evidence is missing |
| `COMPONENT_ROLE_WEIGHT_BLOCKED` | active components or target weight total are invalid |

## Boundary

11-4 does not create role presets or user memo storage and does not enforce selected-route gate policy.
Gate policy ownership remains 11-5.

## Implemented Touch Points

- `app/services/backtest_component_role_weight_audit.py`
- `app/services/backtest_practical_validation_diagnostics.py`
- `app/services/backtest_evidence_read_model.py`
- `app/web/backtest_practical_validation.py`
- `app/web/backtest_final_review.py`
- `app/web/backtest_final_review_helpers.py`
- `tests/test_service_contracts.py`
