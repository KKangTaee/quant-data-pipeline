# Construction Risk Source Map V1 Notes

Status: Complete
Created: 2026-05-29

## Observations

- `build_practical_validation_result()` already computes `concentration_overlap_exposure` and `correlation_diversification_risk_contribution`.
- Provider look-through board already emits holdings coverage, exposure coverage, top holding weight, top overlap weight, dominant asset bucket, and unknown exposure.
- Holdings overlap currently stores only compact top rows in validation context. Full holdings stay in DB, which matches the storage boundary.
- `_correlation_risk_evidence()` computes a useful proxy, but it is not a full covariance / marginal contribution model.
- `_sensitivity_rows()` already computes drop-one and +5%p weight tilt scenarios when component curves are available.
- `build_investability_gate_policy()` currently routes `concentration_overlap_exposure` to `provider_coverage` and `correlation_diversification_risk_contribution` to `stress_robustness`.
- There is no explicit `construction_risk` gate group yet.

## Decision

11-2 should not start by adding a provider collector.

It should first create a compact construction risk read model that reuses:

- active component weights
- proxy exposure summary
- provider look-through board
- provider holdings / exposure coverage status
- top holding / overlap / unknown exposure metrics

Provider data gaps should remain visible as `REVIEW` or `NEEDS_INPUT`.
