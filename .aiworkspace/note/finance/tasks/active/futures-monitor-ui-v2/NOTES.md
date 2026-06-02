# Futures Monitor UI V2 Notes

## 2026-06-02

- Benchmark direction used for the V2 skeleton:
  - keep a persistent watchlist / data-feed status surface near the top;
  - show macro interpretation and live chart evidence in the same workspace;
  - keep raw provider evidence available, but lower it under diagnostics.
- No scoring, validation, provider, or DB schema contract changed in this task.
- Streamlit fragment refresh is still browser-open dependent. It is not a backend scheduler and does not collect futures data when no browser session is active.
