# RISKS - Validation Gate Hardening V1

Status: Active
Created: 2026-05-28

## Risks

| Risk | Mitigation |
| --- | --- |
| Gate becomes too strict for current provider coverage | Keep non-selected routes saveable and expose route guidance |
| Gate becomes too vague | Store compact policy snapshot with group / severity / recommendation |
| Waiver becomes memo sprawl | Do not implement waiver in V1 |
| UI becomes noisy | Put policy matrix in compact table / expander |
| Existing selected decisions are interpreted differently | Keep saved row rendering backward compatible when snapshot is missing |

## Residual

- Structured waiver is intentionally not implemented. Future waiver work must be structured and should not become a free-form memo field.
- Existing records without `gate_policy_snapshot` remain readable through the older packet / evidence fields.
