# Robustness Lab V1 Notes

Status: Active
Created: 2026-05-28

## Findings

- Existing diagnostics already produce `stress_interpretation`, `sensitivity_interpretation`, `rolling_validation`, and `overfit_audit`.
- The missing piece is an operator-facing compact board and downstream evidence expansion, not a new persistence layer.
- `NOT_RUN` must remain visible as an evidence gap, not be treated as pass.
- `runtime_followup_count > 0` is surfaced as REVIEW at the board level even when curve-only sensitivity rows are otherwise PASS.
- The board stays inside `robustness_validation` to avoid top-level duplication and registry sprawl.
