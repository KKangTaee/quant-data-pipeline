# GTAA Result Cadence Monthly Valuation Risks

- Changing row cadence will change historical GTAA metrics because non-rebalance valuation rows now affect monthly return path and summary period end.
- Selection history and real-money turnover helpers must keep reading `Next Ticker` as actual holdings, not monthly signal candidates.
- Guardrail signals on non-rebalance months are visible as signal evidence but should not silently force an actual holdings switch unless cadence says rebalance.
- Latest common row semantics depend on current DB coverage. If one ETF is stale, the strategy result correctly stops at that stale common date; users may still need a separate price refresh workflow to move the endpoint forward.
