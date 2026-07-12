# Institutional Portfolios Interactive Security Chart V1 Risks

## Remaining Risks

- Browser automation could not click the candle toggle because the Streamlit iframe was partially above the viewport and the in-app browser translated the click to a negative page coordinate. DOM checks confirmed the button exists; npm build confirmed the candle code compiles.
- The chart uses stored price rows only. If `finance_price.nyse_price_history` lacks OHLCV for a selected symbol, the existing price collection action remains the recovery path.
- The current chart is a lightweight SVG implementation, not a full TradingView-class charting library. If future requirements include zoom wheel, technical indicators, multi-series overlays, or saved chart state, a dedicated chart library should be evaluated.
