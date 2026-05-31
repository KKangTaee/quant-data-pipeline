# Decision Dossier Continuity Operations V1 Risks

Status: Complete
Created: 2026-05-29

## Risks

- A timeline object without a source contract should not be treated as durable proof that the selected decision row matches the dossier.
- Session-state performance recheck / drift / alert evidence can still be mistaken for saved monitoring history if UI labels drift.
- Legacy final decision registry naming can confuse future source-contract readers.

## Mitigation

- Continuity blocks missing or mismatched timeline source contracts.
- Decision Dossier marks timeline contract presence and consistency in markdown.
- Dashboard source contract tables explicitly show disabled registry write, monitoring log auto-write, report auto-write, order, and auto rebalance behavior.
