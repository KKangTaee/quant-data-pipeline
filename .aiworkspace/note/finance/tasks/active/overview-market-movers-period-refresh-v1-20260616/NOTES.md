# Notes

- Daily movers use `market_intraday_snapshot` and keep browser-session auto refresh.
- Weekly / Monthly / Yearly movers use stored EOD `finance_price.nyse_price_history`.
- Overview UI must not directly fetch providers. The UI calls `app/jobs/overview_actions.py`, which wraps ingestion jobs.
- Non-daily refresh is a user action path, not a diagnostic panel.
- Existing generated screenshots and `.DS_Store` changes were present before this task and must not be staged.
- Period-to-provider windows are explicit in the Overview action facade: Weekly -> `3mo`, Monthly -> `1y`, Yearly -> `3y`.
- Top1000 / Top2000 reuse the market-cap ranked asset profile universe and show a runtime-cost warning in the UI.
