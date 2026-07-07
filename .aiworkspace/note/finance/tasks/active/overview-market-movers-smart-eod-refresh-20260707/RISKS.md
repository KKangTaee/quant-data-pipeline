# Risks

- Current 1차 only checks latest-date freshness. It does not yet repair bad latest rows or insufficient lookback coverage.
- Delta fetch groups stale symbols by the earliest stale start date, so some stale symbols can receive a few extra rows. This is still much smaller than refreshing the entire universe.
