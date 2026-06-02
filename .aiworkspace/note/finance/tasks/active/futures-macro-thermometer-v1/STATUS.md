# Futures Macro Thermometer V1 Status

## 2026-06-02

- Started after user requested implementation of a global macro interpretation layer on top of collected futures daily OHLCV.
- Scope classified as futures DB ingestion support plus Overview market intelligence UI.
- Planned structure:
  - keep existing futures 1m monitor and candlestick charts unchanged;
  - add daily futures macro read model in a separate service;
  - add `Macro Thermometer` tab inside `Overview > Futures Monitor`;
  - expose `1d` interval / 1y period ingestion for daily backfill.
- Implemented:
  - `finance/data/futures_market.py` accepts `interval='1d'` so the existing futures OHLCV table can hold daily rows.
  - `app/services/futures_macro_thermometer.py` computes symbol returns, 60D volatility standardized moves, 252D position, six macro scores, scenario summary, evidence, and caution lines.
  - `app/web/overview_dashboard.py` adds `Macro Thermometer` inside `Futures Monitor` and a manual `Refresh Daily Macro OHLCV` action.
  - `app/web/streamlit_app.py` lets Ingestion select longer futures periods and `1d` interval.
  - Service contract tests cover rate / FX inversion, rate-pressure scenario detection, and short-history warnings.
- Daily backfill smoke succeeded for all 16 non-optional core futures symbols with `period=1y`, `interval=1d`.
