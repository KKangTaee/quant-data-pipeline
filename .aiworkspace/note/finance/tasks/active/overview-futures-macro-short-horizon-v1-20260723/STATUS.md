# Overview Futures Macro Short-Horizon V1 Status

Status: Complete
Roadmap: 4/4 implementation stages complete
Last Updated: 2026-07-23

## Completed

- Diagnosed the 40~50 second refresh path as repeated 17-symbol 10-year collection plus full nested outlook materialization.
- Confirmed current stored coverage is 17/17 symbols and family 6/6.
- Confirmed 15 symbols directly feed `SCORE_DEFINITIONS`; DXY is shared with Economic Cycle and silver is raw observation only.
- Confirmed existing active pathway UI exposes five families and omits growth.
- Confirmed the user-approved product direction: recent 1/5/20 observation roles, future 5D validation, core 4 + confirmation 2, and no primary 2D path/future 20D card.
- Recorded the implementation boundary, refresh fast path, error handling, and QA contract in `DESIGN.md`.
- Completed the written-spec placeholder, consistency, ambiguity, and scope review. Corrected the unapproved 60D removal assumption so the ribbon remains secondary history.
- Received user approval for the written specification and request to proceed with development.
- Wrote and self-reviewed `IMPLEMENTATION_PLAN.md` with TDD units for payload/UI, routine refresh, pre-materialization reuse, and integrated QA.
- Implemented the approved short-horizon decision surface, core 4 + confirmation 2 direction alignment, calculation scope, and user-facing `NO_EDGE` explanation.
- Changed routine daily collection from all-symbol ten-year download to one-year overlap plus deficient-symbol bootstrap.
- Added completed-input probing before nested model builders and corrected Yahoo same-date evening bars to remain pending when they can still move.
- Added incompatible-version current replacement and accurate end-to-end refresh duration reporting.
- Actual unchanged-input refresh improved from 64.859 seconds to 12.936 seconds; nested materialization was 0 seconds on the verified fast path.
- Completed actual desktop and 420px Browser QA with no horizontal overflow and no console warning/error.
- Passed the final focused suite (69 tests, 15 subtests), Futures Macro service contracts (26 tests), py_compile, diff check, and Vite production build.

## Current

- All implementation, performance, browser, and documentation completion gates are satisfied.

## Next

- Preserve the branch/worktree until the user selects merge, PR, keep, or discard handling.
- Treat genuinely changed-session nested-model optimization as a separate approved performance task if required.

## Remaining Roadmap

1. Short-horizon UX and payload — complete
2. Routine incremental daily refresh — complete
3. Unchanged-input materialization fast path — complete
4. Verification, Browser QA, and durable docs — complete
