# Correlation / Risk Contribution Contract V1 Design

Status: Complete
Created: 2026-05-29

## Contract

`risk_contribution_audit_v1` is a read-only audit contract.

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
| Component return matrix coverage | `curve_evidence.component_curve_rows` and correlation diagnostic metrics | at least two usable component curves and monthly return rows |
| Pairwise correlation | `correlation_diversification_risk_contribution.metrics` | max correlation at or below review line |
| Risk contribution concentration | `correlation_diversification_risk_contribution.metrics` | max risk contribution at or below review line |
| Component dependency | `sensitivity_interpretation` row `Component dependency` | drop-one sensitivity computed without review trigger |
| Storage / execution boundary | static boundary | always PASS unless contract changes |

## Route Semantics

| Route | Meaning |
| --- | --- |
| `RISK_CONTRIBUTION_READY` | correlation / risk contribution / drop-one evidence is computed and no immediate review trigger is present |
| `RISK_CONTRIBUTION_REVIEW` | evidence exists but source strength, correlation, risk contribution, or drop-one dependency needs review |
| `RISK_CONTRIBUTION_NEEDS_INPUT` | component return matrix or dependency evidence is missing |
| `RISK_CONTRIBUTION_BLOCKED` | source contract itself is invalid |

## Boundary

11-3 does not create raw matrix artifacts and does not enforce selected-route gate policy.
Gate policy ownership remains 11-5.

## Implemented Touch Points

- `app/services/backtest_risk_contribution_audit.py`
- `app/services/backtest_practical_validation_diagnostics.py`
- `app/services/backtest_evidence_read_model.py`
- `app/web/backtest_practical_validation.py`
- `app/web/backtest_final_review.py`
- `app/web/backtest_final_review_helpers.py`
- `tests/test_service_contracts.py`
