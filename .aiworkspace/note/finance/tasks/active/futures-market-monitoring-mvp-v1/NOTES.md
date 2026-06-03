# Futures Market Monitoring MVP V1 Notes

## Implementation Notes

- Keep provider collection out of Streamlit render; use job wrapper / DB / service read model.
- Treat `yfinance` as pilot provider with visible source freshness and failure state.
- Default cadence should be 60s; fast mode must be bounded to selected symbols.
- MVP watch list uses broad, liquid Yahoo futures symbols first: equity index (`ES=F`, `NQ=F`, `YM=F`, `RTY=F`), rates (`ZN=F`, `ZB=F`), commodities (`CL=F`, `GC=F`, `SI=F`, `HG=F`), FX (`6E=F`, `6J=F`, `6B=F`), optional micro / crypto symbols. `DX=F` and `VX=F` remain excluded from the default because research smoke showed weak free-provider availability.
- The Overview monitor intentionally shows missing rows for selected symbols without stored candles. This makes partial watchlist coverage visible instead of silently hiding symbols.
- Provider status is not exchange-grade realtime; the UI should continue to present it as pre-open context / early warning, not as a trading execution feed.
- 2026-06-03 bugfix: yfinance can return empty or extremely sparse `1d / 1m` futures frames for some symbols even when `2d / 1m` has current candles. The collector now performs one bounded 2d retry for symbols that produced no normalized rows or fewer than 120 normalized rows in the initial 1d request. This is a coverage recovery path, not a freshness guarantee; stale warnings still remain when the provider latest candle is delayed.
