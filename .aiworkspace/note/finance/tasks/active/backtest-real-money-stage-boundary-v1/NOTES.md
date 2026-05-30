# Backtest Real-Money Stage Boundary V1 Notes

## Decision

- Backtest Analysis owns candidate generation and first-pass candidate readiness only.
- Practical Validation owns actual practical diagnostics.
- Final Review owns final selected-route decision and paper observation criteria.
- Selected Dashboard owns post-selection monitoring / recheck.

## Implementation Note

Existing metadata fields such as `probation_status`, `monitoring_status`, and `deployment_readiness_status` may remain for compatibility, but the Backtest Analysis UI should not present them as if probation, monitoring, or deployment has actually started.
