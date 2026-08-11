# Overview Futures Macro Intraday Nowcast V1 Status

State: complete
Roadmap: 3/3 implementation stages complete
Last Updated: 2026-08-11

## Current

- Active futures sessions now use latest stored closed 5m data for provisional 1D / 5D / 20D
  current observation.
- Completed-session data remains the only input to forecast validation and immutable history.
- The manual action is now `최신 데이터 갱신`; one 2d/5m collection is reused by
  current observation and eligible daily finalization.
- React separates current observation from the completed-session 5D forecast validation gate and
  exposes sample count, chronological evaluation count, model Brier and baseline Brier.
- Focused regression, production bundle build, actual refresh, DB-only service read and Browser QA
  completed successfully.

## Closeout

- Implementation commits: `61e2700f1`, `638ec9edd`, `61d88c4a6`, `1c83f62c4`.
- Browser QA screenshot: `futures-macro-intraday-nowcast-v1-qa.png` (generated, not committed).
- No DB schema was added. Existing `futures_ohlcv` 5m rows are reused and provisional output is
  render-time only.

## Remaining Roadmap

1. Written specification approval - complete
2. Intraday collection/read-model/React implementation - complete
3. Focused verification, Browser QA, durable documentation and closeout - complete
