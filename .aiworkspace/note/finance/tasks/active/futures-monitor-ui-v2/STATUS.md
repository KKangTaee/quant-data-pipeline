# Futures Monitor UI V2 Status

## 2026-06-02

- User approved implementing the Futures Monitor UI redesign guide in order.
- Working scope is V2 skeleton first:
  - command center and data feed visual treatment;
  - Macro Thermometer plus Candles in one workspace;
  - Shock Board / Provider Run moved to diagnostics;
  - refresh UX reduced so data collection does not feel like a full-page prototype rerun.
- Existing dirty artifacts observed and left untouched: `finance/.DS_Store`, prior futures QA screenshots.
- Implemented V2 layout skeleton:
  - top Futures Workspace / Market Pulse / Data Feed command center;
  - Macro Context and Live Futures Charts rendered side-by-side;
  - Shock Board / Provider Run / selected candle rows moved under diagnostics expander;
  - manual 1m futures refresh now reloads the snapshot in-place instead of forcing an immediate `st.rerun()`;
  - auto refresh updates the Futures workspace via Streamlit fragment.
- Browser QA confirmed the new body no longer exposes `Shock Board`, `Candles`, or `Provider Run` as peer tabs.
- Implemented V2.1 visual follow-up from user screenshot review:
  - compressed the top controls into one row and moved refresh controls into `Data Actions`;
  - replaced large mini-chart `st.metric` blocks with compact 60m / 15m / Age chips;
  - increased mini-chart height and card framing so chart evidence is no longer subordinate to large numbers;
  - changed Macro Context from large generic cards to scenario / confidence / validation / history signal strips plus score chips.
- Browser QA caught and fixed raw HTML leakage in signal and score strips before closeout.
