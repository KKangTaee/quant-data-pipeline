# Overview Sentiment React UX Notes

- Current tab entrypoint: `app/web/overview/sentiment.py`.
- Current Streamlit body: `app/web/overview/sentiment_helpers.py`.
- Read model owner: `app/services/overview/sentiment.py`.
- Collection / loader boundary: `finance/data/sentiment.py`, `finance/loaders/sentiment.py`.
- Existing service already provides `analysis`, `driver_groups`, `component_explanations`, `next_checks`, `rows`, `component_rows`, `history_rows`.
- React must render existing service interpretation only. It must not invent new recommendation or trading language.
- Browser QA found Streamlit dark theme made the transparent iframe hard to read; the React workbench now owns a light panel background and white internal cards for stable contrast.
- Graph improvement is implemented inside React using the existing `charts.history` and `charts.components` payload: SVG history line chart plus CNN component bars. Raw rows remain visible in lower evidence tables.
- Follow-up UX review: default next-check cards competed with the evidence flow, so React now hides next-check cards and next-check analysis steps while keeping the service payload unchanged for future context surfaces.
- Follow-up graph review: the history chart should not require raw tables for exact values. React now exposes y-axis labels plus hover tooltip using only existing `charts.history` fields.
- Potential next features should be service-owned before React displays them:
  - Add recent-percentile / range context for CNN score, AAII bearish, and bull-bear spread so users can tell whether the latest reading is ordinary or unusual.
  - Add a divergence read model that distinguishes headline score vs CNN component split vs AAII survey conflict without turning it into a trading signal.
  - Add component-history support if the DB keeps historical CNN component rows; current component bars are latest-only.
  - Add source freshness history / provider issue context for CNN and AAII, especially when official pages block automated requests.
