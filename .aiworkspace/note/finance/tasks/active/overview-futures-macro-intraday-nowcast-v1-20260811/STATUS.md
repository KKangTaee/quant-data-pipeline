# Overview Futures Macro Intraday Nowcast V1 Status

State: active
Roadmap: 0/3 implementation stages complete
Last Updated: 2026-08-11

## Current

- User approved the product direction that active futures sessions should use latest stored
  intraday data for provisional 1D / 5D / 20D observation.
- Completed-session data remains the only input to forecast validation and immutable history.
- User approved the written specification and asked implementation to proceed.
- TDD implementation steps are defined in `IMPLEMENTATION_PLAN.md`.

## Next

- Execute Task 1 in `IMPLEMENTATION_PLAN.md`: stored 5m intraday observation service.

## Remaining Roadmap

1. Written specification approval
2. Intraday collection/read-model/React implementation
3. Focused verification, Browser QA, durable documentation and closeout
