# Backtest Real-Money Readiness Efficacy V1 Risks

## Known Risks

- Legacy metadata field names such as `deployment_*`, `probation_*`, and `monitoring_*` remain for compatibility.
- Older persisted run history can still contain historical raw fields.
- This task does not replace Practical Validation's deeper evidence audits.
- Compare / History may still read legacy metadata names internally, but user-facing labels now avoid treating them as separate Backtest validation stages.
