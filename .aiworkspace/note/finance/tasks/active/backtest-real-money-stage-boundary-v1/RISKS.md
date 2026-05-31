# Backtest Real-Money Stage Boundary V1 Risks

## Known Risks

- Internal metadata and legacy history rows can still contain old field names such as `probation_*`, `monitoring_*`, and `deployment_*` for compatibility.
- Practical Validation / Final Review / Selected Portfolio Dashboard still own the actual evidence, observation, final decision, and selected monitoring contracts.
- Older persisted run-history rows may include historical raw metadata if viewed in a raw/meta surface; this task only normalizes the user-facing Backtest Analysis interpretation.
