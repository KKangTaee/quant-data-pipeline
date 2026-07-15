# Institutional Portfolios Holding Chart Refresh V1 Risks

- Curated CUSIP seed is intentionally small and service-level. It improves common institutional holdings but is not a complete security master.
- CUSIP-symbol mapping can still be incomplete for less common holdings; unmapped rows should remain explicit rather than guessed.
- Price collection uses existing yfinance-backed OHLCV ingestion, so provider rate limits or no-data responses can still return partial or failed results.
- 13F caveats remain unchanged: delayed quarterly data, no shorts/cash/derivatives/full trading intent, no buy/sell signal.
