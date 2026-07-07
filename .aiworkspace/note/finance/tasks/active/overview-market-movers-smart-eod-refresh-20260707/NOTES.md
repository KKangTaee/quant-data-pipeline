# Notes

- Existing collection periods remain unchanged as fallback windows:
  - Weekly: `3mo`
  - Monthly: `1y`
  - Yearly: `3y`
- Smart refresh uses `nyse_price_history` freshness preflight through the loader boundary.
- If freshness preflight fails, the action falls back to the previous full-window behavior and records the fallback reason in result details.
- UI result captions now summarize selected, skipped-current, delta, missing/full-window counts from job details.
