# Notes

- Initial direction: use DB-only `nyse_price_history` returns and existing universe metadata.
- Trend windows use non-overlapping trading-day offsets:
  - Daily: 63 windows, approximately 3 months.
  - Weekly: 26 windows, approximately 6 months.
  - Monthly: 12 windows, approximately 1 year.
- Trend chart follows the latest Top N groups so users can compare current leaders against recent behavior; the UI defaults to the first 5 groups and lets users toggle visible lines with `Trend Groups`.
- Positive Group Detail is derived from the latest ranking's positive cap-weighted groups. Ticker share is the ticker's positive return divided by the selected group's sum of positive ticker returns, so it is a return-share view rather than a market-cap attribution model.
- Daily mode now uses the same `market_intraday_snapshot` read path as Market Movers when a snapshot exists. Ranking rows and ticker leaders use `Previous Close -> latest quote / snapshot_time`; the trend chart keeps the historical EOD daily windows and appends the current intraday point for the latest selected groups.
- Weekly and Monthly modes remain `nyse_price_history` EOD based because intraday snapshots only represent previous-close daily movement.
