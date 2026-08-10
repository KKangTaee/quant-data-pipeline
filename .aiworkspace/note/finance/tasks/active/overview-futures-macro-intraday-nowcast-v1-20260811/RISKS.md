# Overview Futures Macro Intraday Nowcast V1 Risks

Last Updated: 2026-08-11

## Open Risks

- Yahoo continuous futures 5m data may be delayed, missing by symbol or revised; the common cutoff,
  full-family membership and 30-minute freshness gates must fail closed.
- Futures session dates can differ from New York calendar dates around Sunday evening and holidays;
  the existing DST-safe resolver/window contract must remain the authority.
- A synthetic current close can change regime/transition during the session. Every provisional value
  must remain visibly labeled and must not enter immutable forecast history.
- Reusing one 5m collection for both nowcast and post-cutoff finalization requires a narrow handoff;
  it must not weaken the existing 17/17 atomic finalization gate.
- The active React component bundle is generated code that must be rebuilt and verified without
  staging unrelated generated screenshots or run history.

## Deferred

- Intraday forecast probabilities or model retraining
- Exchange-grade settlement/realtime provider migration
- Automatic or scheduled intraday refresh
- A separate persisted intraday snapshot table
