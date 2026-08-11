# Overview Futures Macro Intraday Nowcast V1 Runs

Last Updated: 2026-08-11

| Run | Result |
|---|---|
| Screenshot filesystem timestamp and ET conversion | Confirmed capture during the 2026-08-10 active US session |
| Read-only latest snapshot query | `as_of_date=2026-08-07`, `pending_session=2026-08-10`, 5D `NO_EDGE`, 120 episodes, 325 evaluations |
| Read-only latest daily row resolution | 17/17 rows resolved to `IN_PROGRESS` for 2026-08-10 |
| `.venv/bin/python -m pytest tests/test_overview_futures_macro_refresh.py tests/test_futures_macro_sessions.py tests/test_overview_futures_macro_short_horizon.py -q` | 38 passed, existing edgar deprecation warnings only |
| Intraday service TDD | 7 focused tests passed, including evening reopen and fail-closed prior pending session |
| Refresh/action/payload/React focused suites | 93 passed, 3 existing warnings, 15 React subtests passed |
| React `npm run build` | Production bundle built successfully |
| Approved actual refresh | daily 4,267 rows, intraday 4,991 rows, no failures; 2026-08-10 finalized 17/17 |
| DB-only intraday read after refresh | `INTRADAY_READY`, session 2026-08-11, completed 2026-08-10, 6/6 families, latest common bar 19:40 ET |
| In-app Browser QA | current/validation reference split, 1D/5D/20D semantics, Brier evidence and action labels verified; no console warnings/errors |
| QA screenshot | `futures-macro-intraday-nowcast-v1-qa.png` generated and intentionally left untracked |
| Final Futures Macro regression | 111 passed, 3 existing deprecation warnings, 15 subtests passed |
| Changed service-contract nodes | 11 passed, 3 existing deprecation warnings |
| Python compile + React production build | Passed; Vite built 181 modules |
| Expanded run including full `tests/test_service_contracts.py` | 1,006 passed and 18 failed in pre-existing Backtest/Sentiment/legacy thermometer contracts; none of the owning source files changed in this task |
| Finance refinement hygiene + `git diff --check` | Passed; unrelated registry/run-history/screenshots remained unstaged |
