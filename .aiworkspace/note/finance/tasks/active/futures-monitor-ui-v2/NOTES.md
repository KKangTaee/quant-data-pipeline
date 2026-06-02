# Futures Monitor UI V2 Notes

## 2026-06-02

- Benchmark direction used for the V2 skeleton:
  - keep a persistent watchlist / data-feed status surface near the top;
  - show macro interpretation and live chart evidence in the same workspace;
  - keep raw provider evidence available, but lower it under diagnostics.
- No scoring, validation, provider, or DB schema contract changed in this task.
- Streamlit fragment refresh is still browser-open dependent. It is not a backend scheduler and does not collect futures data when no browser session is active.
- V2.1 kept the same service read model and focused only on render density:
  - controls are selection-first with collection controls in `Data Actions`;
  - mini chart cards use chips instead of `st.metric` to avoid numeric truncation;
  - macro reliability information is a compact signal strip, not a large generic KPI grid.
