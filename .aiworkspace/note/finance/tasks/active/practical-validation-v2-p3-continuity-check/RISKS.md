# Practical Validation V2 P3 Continuity Check Risks

Status: Active
Last Updated: 2026-05-28

## Storage sprawl

Continuity QA must not create another JSONL registry or auto-write monitoring rows.

Mitigation:

- Keep the implementation as a read model over existing final decision rows and session-state timeline.

## False approval signal

A continuity check can be misread as live approval.

Mitigation:

- Keep execution boundary fields and UI copy explicit: no live approval, no order, no auto rebalance.

## Historical row compatibility

Older selected rows may not have the newest investability packet fields.

Mitigation:

- Treat missing packet evidence as `REVIEW` / `NEEDS_INPUT` instead of crashing.
