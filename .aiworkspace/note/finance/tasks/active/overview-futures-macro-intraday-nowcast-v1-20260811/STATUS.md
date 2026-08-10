# Overview Futures Macro Intraday Nowcast V1 Status

State: active
Roadmap: 0/3 implementation stages complete
Last Updated: 2026-08-11

## Current

- User approved the product direction that active futures sessions should use latest stored
  intraday data for provisional 1D / 5D / 20D observation.
- Completed-session data remains the only input to forecast validation and immutable history.
- Written specification is ready for user review in `DESIGN.md`.

## Next

- Receive user review of the written specification.
- After approval, write the TDD implementation plan before changing production code.

## Remaining Roadmap

1. Written specification approval
2. Intraday collection/read-model/React implementation
3. Focused verification, Browser QA, durable documentation and closeout
