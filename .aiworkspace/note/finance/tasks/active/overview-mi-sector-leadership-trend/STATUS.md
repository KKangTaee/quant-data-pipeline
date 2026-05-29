# Status

- Completed: Sector / Industry Leadership now supports S&P 500 / Top 1000 / Top 2000 coverage, Daily / Weekly / Monthly periods, latest group ranking, and DB-backed trend rows.
- Completed: Overview UI replaced the default heatmap view with ranking and trend charts plus a table fallback.
- Completed: Trend horizon expanded to Daily 3M / Weekly 6M / Monthly 1Y, with a Trend Groups multiselect for line-level filtering.
- Completed: Positive-return groups now expose ticker leaders with a Top N bar chart and contribution-style donut chart.
- Completed: Daily Sector / Industry ranking and Positive Group Detail now prefer `market_intraday_snapshot`, so Market Movers daily refresh also feeds this tab; Weekly / Monthly remain EOD DB based.
- Verified: service contract tests, module compile, DB smoke, and browser smoke.
