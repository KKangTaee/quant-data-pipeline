# Status

- 2026-07-08: Started. User approved phased 1-4 implementation for Market Movers EOD refresh scope visibility and execution narrowing.
- 2026-07-08: Completed 1차~4차 in this task.
  - 1차: EOD refresh preflight payload now exposes selected/current/stale/repair/missing counts, range start/end, driver symbols, and range reason before provider fetch.
  - 2차: Market Movers React summary separates screen calculation availability from EOD refresh debt with `계산 가능 · 이력 보강 필요`.
  - 3차: Non-daily `가격 이력 갱신` action carries preflight detail such as `최신 1,000개 스킵 가능` or collection range before click.
  - 4차: Top1000 / Top2000 refresh uses materialized liquidity universe, receives screen effective `as_of_date`, and splits stale/repair collection by start-date batch.
