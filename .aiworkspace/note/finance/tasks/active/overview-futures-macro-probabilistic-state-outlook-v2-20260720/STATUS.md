# Overview Futures Macro Probabilistic State Outlook V2 Status

Status: Design approved; detailed implementation plan ready
Last Updated: 2026-07-20

## Current Progress

- User concern reproduced against the two supplied screenshots and current DB rows.
- 2026-07-17 and 2026-07-20 fixed-cutoff anchors were reconstructed.
- Historical same-date PIT feature stability was confirmed with maximum difference `0.0` through 2026-07-17.
- Root cause was separated into rolling anchor movement, incomplete current candle, sparse three-point rendering, and forecast target semantic mismatch.
- User approved the direction: momentum-only baseline plus PIT macro/event soft conditioning, selected only by chronological validation.
- Written `PLAN.md` and `DESIGN.md` were explicitly approved by the user.
- Detailed TDD tasks, exact file ownership, validation gates, and commit checkpoints are recorded in `IMPLEMENTATION_PLAN.md`.

## Roadmap State

- 1차 Data / Target Contract: not started
- 2차 Momentum Baseline / Macro Hybrid Validation: not started
- 3차 Observed Trail / Probabilistic Outlook UI / QA: not started
- Design gate: approved 2026-07-20
- Implementation execution: not started

## Next Action

Select the execution mode for `IMPLEMENTATION_PLAN.md`, then begin 1차 Data / Target Contract.
No implementation code or production data has been changed yet.
