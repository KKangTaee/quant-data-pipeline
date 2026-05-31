# Decision Dossier Report V1 Risks

Status: Active
Created: 2026-05-28

## Risks

- Dossier download could be mistaken for investment approval.
- Markdown export could accidentally become another auto-written report artifact.
- Dossier could include too much raw data and recreate the storage sprawl problem.

## Mitigation

- Keep `execution_boundary` explicit: read-only, no auto file write, no live approval, no order instruction, no auto rebalance.
- Use compact evidence rows already stored in Final Review.
- Expose markdown through user-initiated download only.

## Closeout Notes

- No new registry, report file writer, DB schema, user memo field, alert persistence, broker action, or auto rebalance behavior was added.
- If durable dossier files are needed later, they should be an explicit report-export task under storage governance rather than an implicit UI side effect.
