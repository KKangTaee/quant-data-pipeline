# GTAA Result Cadence Monthly Valuation Notes

- Existing root cause: `finance/sample.py::get_gtaa3_from_db` chains `.interval(interval)` before `GTAA3Strategy`, so `interval=4` removes non-rebalance monthly rows from the strategy input.
- Secondary root cause: `option=month_end` removes the current partial month; when the requested end date is not a month-end, the latest available common trading day needs to be appended after period filtering.
- Nearby precedent: Global Relative Strength no longer thins period rows before strategy execution; `GlobalRelativeStrengthStrategy(rebalance_interval=...)` owns cadence.
- Desired GTAA row semantics:
  - `Raw Selected Ticker`: current month score-based candidates.
  - `Signal Investable Ticker`: current month candidates after trend/price/liquidity/risk-off signal filters.
  - `Next Ticker`: actual next-period holdings.
  - `Rebalancing`: whether actual holdings were updated on this row.
- The latest common row is limited by the stalest ticker in the requested GTAA universe. In the 2026-06-29 smoke, `SOXX`, `MTUM`, `QUAL`, and `USMV` only had data through `2026-03-16`, so `2026-03-16` is the correct result end until data is refreshed.
