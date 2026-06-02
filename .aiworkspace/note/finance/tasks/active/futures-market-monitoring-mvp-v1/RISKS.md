# Futures Market Monitoring MVP V1 Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Free provider data is delayed or incomplete | User may over-trust chart | Show latest candle age, failed symbols, provider label. |
| Fast refresh overloads provider | Data collection fails | Default 60s; bound fast mode to a small symbol set. |
| Futures session semantics are product-specific | UI may mislead | Show provider latest / watch window instead of exchange session truth in MVP. |
| Yahoo symbol availability changes | Default watchlist can show missing rows | Keep missing state visible; refresh instrument list only after provider smoke. |
| Streamlit auto refresh still executes in the browser session | User may expect server-side scheduler | Label as browser-open polling; scheduled/headless collector remains a future step. |
