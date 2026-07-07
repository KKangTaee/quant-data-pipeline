# Overview Sentiment React UX Notes

- Current tab entrypoint: `app/web/overview/sentiment.py`.
- Current Streamlit body: `app/web/overview/sentiment_helpers.py`.
- Read model owner: `app/services/overview/sentiment.py`.
- Collection / loader boundary: `finance/data/sentiment.py`, `finance/loaders/sentiment.py`.
- Existing service already provides `analysis`, `driver_groups`, `component_explanations`, `next_checks`, `rows`, `component_rows`, `history_rows`.
- React must render existing service interpretation only. It must not invent new recommendation or trading language.

