# Institutional Portfolios Two-Tier Tabs V1 Risks

## Remaining Risks

- This task is UI-only. It does not add new ticker analytics, holding-duration metrics, or data sources.
- Browser automation could not click an offscreen AAPL holding row inside the Streamlit iframe due coordinate translation, so manual/user confirmation may still be useful for the exact holding-row click path. The React source contract continues to cover that drilldown routes to `security`.
