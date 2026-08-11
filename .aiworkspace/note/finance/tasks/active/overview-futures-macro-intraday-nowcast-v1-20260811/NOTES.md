# Overview Futures Macro Intraday Nowcast V1 Notes

Last Updated: 2026-08-11

## Confirmed Facts

- The user screenshots were created at 2026-08-11 00:10 KST / 2026-08-10 11:10 ET.
- At that time all 17 latest daily rows resolved to the 2026-08-10 pending session and the
  latest completed session was 2026-08-07.
- The persisted 5D outlook had 120 independent episodes and 325 chronological evaluations.
- Its model Brier score was 0.5582115 versus unconditional baseline 0.5566554, so `NO_EDGE`
  was caused by insufficient predictive improvement, not missing samples.
- Existing finalization reconstructs one completed session from stored exact-window 5m bars and
  advances only with 17/17 atomic coverage.

## Decisions

- Current observation and completed forecast evidence become separate read models.
- Intraday observation uses the latest closed 5m common cutoff across the union of complete-family
  members and recalculates all 1D/5D/20D windows, not only 1D.
- The provisional row never enters completed snapshot/history or publication metrics.
- The future 5D gate remains completed-session based.
- Intraday freshness threshold is 30 minutes.
- Family scores require every member of that family; missing members are not zero-filled or
  carried forward.
- No job diagnostics panel is added to the primary product surface.

## Implemented Contract

- `active_futures_session_date()` resolves the active CME-style trade date independently from the
  mutable Yahoo daily label. Sunday evening resolves to Monday and Monday-Thursday evening resolves
  to the next trade date; settlement gaps and Friday evening return no active session.
- A family is eligible only when every configured member has a closed 5m bar. Eligible families use
  one common cutoff, 6/6 is ready, 4-5 is partial, fewer than 4 or more than 30 minutes stale falls
  back to the latest completed session.
- An unresolved prior pending daily session fails closed instead of mixing two trade dates.
- `다시 읽기` recalculates the DB-only provisional observation but never fetches a provider.
  `최신 데이터 갱신` owns provider collection through the Overview action facade.
- The UI labels the three observation horizons as `지금 새로 생긴 변화`, `현재 단기
  방향`, and `기존 배경과의 관계`; family values use economic labels such as
  `금리 부담 확대/완화` instead of unlabeled score direction.

## Actual Data Result

- The approved refresh wrote 4,267 daily rows and 4,991 5m rows with no failed futures symbols.
- The 2026-08-10 session finalized 17/17 and advanced the completed snapshot to 2026-08-10.
- At 2026-08-10 19:40 ET, the DB-only read model resolved the active 2026-08-11 trade session as
  `INTRADAY_READY` with 6/6 families and 14-minute freshness.
- The completed 5D gate remained `NO_EDGE`: 120 independent episodes and 325 chronological
  evaluations, model Brier 0.5582 versus baseline 0.5567. This is predictive-edge failure, not
  missing-data failure.
