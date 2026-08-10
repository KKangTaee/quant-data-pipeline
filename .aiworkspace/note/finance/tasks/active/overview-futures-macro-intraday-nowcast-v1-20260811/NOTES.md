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
