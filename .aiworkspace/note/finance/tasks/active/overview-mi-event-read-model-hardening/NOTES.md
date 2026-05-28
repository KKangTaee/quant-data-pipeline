# Notes

- `market_event_calendar` schema is unchanged. Official / estimate classification is derived from existing `event_type` and `source`.
- `federal_reserve_fomc_calendar` is treated as official.
- `EARNINGS` rows from provider calendar sources are treated as provider estimates unless a future source explicitly marks an official company source.
- Earnings estimate stale threshold is 14 days from `collected_at` to the Overview read date.
