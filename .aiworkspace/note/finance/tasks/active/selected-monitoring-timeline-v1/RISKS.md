# Selected Monitoring Timeline V1 Risks

Status: Active
Created: 2026-05-28

## Risks

- Monitoring timeline could be mistaken for live approval or automated operations.
- Timeline could accidentally become another append-only log surface.
- Timeline could duplicate Review Signals without adding clarity.

## Mitigation

- Mark execution boundary as read-only with auto-save disabled.
- Keep timeline row set compact and source-labeled.
- Keep Review Signals for trigger details and Timeline for ordered status history.

## Closeout Notes

- No new registry, DB schema, user memo, alert persistence, broker action, or auto rebalance behavior was added.
- Remaining product risk is semantic: users may still read a selected portfolio as approval, so the dashboard repeats read-only / no-auto-write boundaries.
