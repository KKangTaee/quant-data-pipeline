# Notes

- Initial direction: use DB-only `nyse_price_history` returns and existing universe metadata.
- Trend windows use non-overlapping trading-day offsets:
  - Daily: 21 windows, approximately 1 month.
  - Weekly: 13 windows, approximately 3 months.
  - Monthly: 6 windows, approximately 6 months.
- Trend chart follows the latest Top N groups so users can compare current leaders against recent behavior.
