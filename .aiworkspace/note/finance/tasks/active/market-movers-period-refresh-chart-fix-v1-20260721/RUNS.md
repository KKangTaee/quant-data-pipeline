# Runs

## Tests And Build

- `.venv/bin/python -m pytest tests/test_service_contracts.py -k 'market_movers' -q --tb=short --maxfail=5 -W ignore::DeprecationWarning`
  - result: `89 passed, 768 deselected`
- `.venv/bin/python -m pytest tests/test_overview_market_movers_decision_ui.py -q`
  - result: `27 passed`
- `npm --prefix app/web/streamlit_components/market_movers_workbench run build`
  - result: Vite production build success
- `.venv/bin/python -m py_compile app/services/overview/market_movers.py app/jobs/overview_actions.py`
  - result: success
- `git diff --check`
  - result: clean for implementation commits

## Actual Weekly Refresh

- action: `run_overview_market_movers_eod_history(universe_code='SP500', universe_limit=500, period='weekly', as_of_date='2026-07-20')`
- range: `2026-07-06` through `2026-07-20`
- result: success, 503 requested / 503 processed, 5,533 rows written, 0 failed symbols
- duration: 138.11 seconds
- provider: no missing symbols, no no-data symbols, no rate-limited symbols
- post-refresh browser result: weekly ranking basis `2026-07-20`, `최신 503개 스킵 가능`
- browser manual action result: `마지막 수동 갱신 2026-07-21 08:03:41 KST`

## Browser QA

- latest Streamlit server restarted on port 8530 with `server.runOnSave=true`.
- actual local app opened through the LAN URL because the old 51547 preview tab was unreachable/stale.
- confirmed seven real price-date X-axis ticks and visible positive/negative readout text tones.
- confirmed financial quarter ticks, exact `period_end`, value tooltip, and top-edge tooltip visibility.
- generated screenshot: `market-movers-period-refresh-chart-fix-v1-qa.png` (not staged).
