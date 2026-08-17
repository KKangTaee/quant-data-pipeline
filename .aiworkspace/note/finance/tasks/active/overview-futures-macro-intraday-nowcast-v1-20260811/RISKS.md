# Overview Futures Macro Intraday Nowcast V1 Risks

Last Updated: 2026-08-11

## Residual Risks

- Yahoo continuous futures 5m data may be delayed, missing by symbol or revised; the common cutoff,
  full-family membership and 30-minute freshness gates must fail closed.
- The CME-style active-session resolver covers weekday/evening reopen semantics but is not an
  exchange holiday calendar. Holiday sessions with no fresh data fail closed through the freshness
  gate.
- A synthetic current close can change regime/transition during the session. Every provisional value
  must remain visibly labeled and must not enter immutable forecast history.
- The provider is not exchange-grade realtime; a delayed but still sub-30-minute bar can differ from
  a broker feed. The UI therefore keeps the observation explicitly provisional.

## Closed In This Task

- Evening reopen trade-date ambiguity is covered by dedicated regression tests.
- One 5m collection is reused without weakening the 17/17 atomic daily finalization gate.
- The active React production bundle was rebuilt and Browser QA passed without staging generated
  screenshots or unrelated run history.

## Repository Verification Gap

- The task-owned Futures Macro suites and changed contract nodes pass. A wider exploratory run of
  `tests/test_service_contracts.py` still has 18 failures in pre-existing Backtest, Sentiment and
  legacy thermometer contracts whose owning source files were unchanged by this task.

## Deferred

- Intraday forecast probabilities or model retraining
- Exchange-grade settlement/realtime provider migration
- Automatic or scheduled intraday refresh
- A separate persisted intraday snapshot table
