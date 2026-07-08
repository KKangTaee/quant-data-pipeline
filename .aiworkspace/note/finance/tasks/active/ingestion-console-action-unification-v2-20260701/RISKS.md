# Risks

## 2026-07-01

- Streamlit synchronous execution cannot update a wall-clock timer every second during a blocking provider call. The realistic target is event-driven progress updates plus elapsed time whenever callbacks fire.
- Broad yfinance fundamentals / factors are legacy compatibility paths. Removing dispatch or run-history labels may break older saved/history replay flows.
- Live provider smoke runs can be slow or rate-limited; automated QA should focus on service contracts and UI structure, with Browser QA avoiding large live collection.
