# Overview Futures Macro Intraday Nowcast V1 Runs

Last Updated: 2026-08-11

| Run | Result |
|---|---|
| Screenshot filesystem timestamp and ET conversion | Confirmed capture during the 2026-08-10 active US session |
| Read-only latest snapshot query | `as_of_date=2026-08-07`, `pending_session=2026-08-10`, 5D `NO_EDGE`, 120 episodes, 325 evaluations |
| Read-only latest daily row resolution | 17/17 rows resolved to `IN_PROGRESS` for 2026-08-10 |
| `.venv/bin/python -m pytest tests/test_overview_futures_macro_refresh.py tests/test_futures_macro_sessions.py tests/test_overview_futures_macro_short_horizon.py -q` | 38 passed, existing edgar deprecation warnings only |

No production code or DB state was changed during diagnosis and specification.
