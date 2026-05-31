# Allocation Drift Evidence Boundary V1 Risks

Status: Complete
Created: 2026-05-29

## Risks

- Users may still interpret `REBALANCE_NEEDED` as an executable order signal.
- Future changes could add alert persistence or monitoring log auto-write around the session signal button.
- Direct current weight input mode has no value input contract object, so the Dashboard must keep its session-only wording clear.

## Mitigation

- Boundary rows explicitly state storage and execution false fields.
- The Dashboard button label is `Reflect Session Signal`, not save / update / rebalance.
- Tests assert no DB write, registry write, monitoring log auto-write, input persistence, alert persistence, account connection, broker sync, live approval, order instruction, or auto rebalance.
