# Overview Futures Macro Short-Horizon V1 Status

Status: Design review pending
Roadmap: 0/4 implementation stages complete
Last Updated: 2026-07-23

## Completed

- Diagnosed the 40~50 second refresh path as repeated 17-symbol 10-year collection plus full nested outlook materialization.
- Confirmed current stored coverage is 17/17 symbols and family 6/6.
- Confirmed 15 symbols directly feed `SCORE_DEFINITIONS`; DXY is shared with Economic Cycle and silver is raw observation only.
- Confirmed existing active pathway UI exposes five families and omits growth.
- Confirmed the user-approved product direction: recent 1/5/20 observation roles, future 5D validation, core 4 + confirmation 2, and no primary 2D path/future 20D card.
- Recorded the implementation boundary, refresh fast path, error handling, and QA contract in `DESIGN.md`.
- Completed the written-spec placeholder, consistency, ambiguity, and scope review. Corrected the unapproved 60D removal assumption so the ribbon remains secondary history.

## Current

- Spec-only commit and user review gate.
- No product code or production bundle has changed.

## Next

- Commit only this active-task specification.
- Ask the user to review the committed spec before writing the implementation plan.

## Remaining Roadmap

1. Short-horizon UX and payload
2. Routine incremental daily refresh
3. Unchanged-input materialization fast path
4. Verification, Browser QA, and durable docs
