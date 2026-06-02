# Futures Monitor UI V2 Risks

## 2026-06-02

- yfinance futures candles can lag exchange time; the command center intentionally reports Fresh / Review / Stale based on stored candle age rather than implying exchange-grade realtime.
- Auto refresh is a Streamlit browser fragment. It reduces full-page rerun feel for the active user but does not replace a scheduled ingestion job.
- The V2 skeleton improves layout and data-state readability, but deeper visual charting upgrades may still require a future dedicated chart interaction pass.
