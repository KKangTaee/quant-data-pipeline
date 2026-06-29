# Overview Futures Macro Tab Split V1 Notes

## Decisions

- `시장 맥락` should remain the default Overview entry, but it should not run futures macro historical validation or historical analog on first load.
- `선물 매크로` becomes a primary Overview tab for futures macro current diagnosis, evidence reading, historical validation, data management, and raw tables.
- This is a user workflow improvement, not an operations diagnostics panel.

## Prior Measurement

- Full cold `load_overview_macro_context_cockpit`: about 15.7s.
- `load_overview_futures_macro_snapshot(include_validation=True)`: about 7.6s.
- `include_validation=False`: about 0.2s.
- `market_movers`: about 2.1s, mostly DB latest-date query.
- `group_leadership`: about 4.5s, including repeated latest-date query.
