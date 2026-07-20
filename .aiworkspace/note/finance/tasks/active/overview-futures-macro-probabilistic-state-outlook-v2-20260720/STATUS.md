# Overview Futures Macro Probabilistic State Outlook V2 Status

Status: Complete — 3/3 stages, 9/9 tasks
Last Updated: 2026-07-20

## Current Progress

- User concern reproduced against the two supplied screenshots and current DB rows.
- 2026-07-17 and 2026-07-20 fixed-cutoff anchors were reconstructed.
- Historical same-date PIT feature stability was confirmed with maximum difference `0.0` through 2026-07-17.
- Root cause was separated into rolling anchor movement, incomplete current candle, sparse three-point rendering, and forecast target semantic mismatch.
- User approved the direction: momentum-only baseline plus PIT macro/event soft conditioning, selected only by chronological validation.
- Written `PLAN.md` and `DESIGN.md` were explicitly approved by the user.
- Detailed TDD tasks, exact file ownership, validation gates, and commit checkpoints are recorded in `IMPLEMENTATION_PLAN.md`.
- Task 1 completed-session resolver is implemented with canonical duplicate collapse and pending-session evidence.
- Task 2 canonical state builder and same-state 5D/20D target are implemented.
- Task 3 DB-only Economic Cycle replay and official event known-at context is implemented.
- Task 4 fixed 16-feature momentum projection and weighted M1/M2 analog ranking are implemented.
- Task 5 nested rolling-origin selection, B0/B1/M1/M2 comparison, separate publication gates, and weighted joint terminal regions are implemented.
- V2 horizon snapshot now uses the same future state `S(t+h)` as the observed map and no longer publishes the sparse median path as its forecast primitive.
- M2 candidates must cover the same inner evaluation origins as M1/baselines; partial macro history cannot win on an easier subset.
- Task 6 adds deterministic final-input fingerprints, immutable forecast identities/history, and atomic latest-good current advancement.
- Pending sessions reuse the prior current snapshot; older final as-of rows cannot replace a newer current row.
- Task 7 V3 Python bridge now enforces separate probability/coordinate/vector publication suppression without recalculating the model.
- Task 8 React surface now renders the full completed-session trail on a fixed domain and only verified ellipse/vector forecast geometry.
- Task 9 fixed-cutoff integration, legacy schema transition, actual DB materialization, responsive Browser QA, and durable documentation sync are complete.
- Actual V2 current is final `2026-07-17`; raw `2026-07-20` is disclosed as pending and excluded from current/forecast inputs.
- Actual 5D/20D publication status is `NO_EDGE` for probability, coordinate, and vector. No conditional numbers or forecast geometry are forced onto the first surface.
- Desktop and 420px QA confirmed full daily trail, fixed axes, separated dated anchors, pending-session notice, and NO_EDGE suppression.

## Roadmap State

- 1차 Data / Target Contract: complete
- 2차 Momentum Baseline / Macro Hybrid Validation: complete (Tasks 3-5)
- 3차 Observed Trail / Probabilistic Outlook UI / QA: complete
- Design gate: approved 2026-07-20
- Implementation execution: complete

## Next Action

No implementation step remains in the approved roadmap. Optional future work is limited to new data/model candidates such as roll-aware prices or wider PIT macro coverage; these require a new version and may not relax the current gate in place.
