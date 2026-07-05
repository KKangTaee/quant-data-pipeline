# Overview Market Movers Sector V4 Notes

- Sector breadth is computed from already-loaded mover return rows, so it respects current coverage / period / sector filters.
- The heatmap is not limited by `top_n`; `top_n` still controls exploration mode table length.
- Market-cap share is a size proxy only. It is not a signal or allocation suggestion.
- The fallback table is intentionally inside an expander so the first screen stays user-flow oriented.
- Same-symbol detail pane from 3차 remains below sector context; Why It Moved is not changed in 4차.
- 2026-07-05 follow-up: the lane visual no longer treats zero as the center. Positive and negative lanes both express magnitude from left to right; negative meaning is carried by color and signed return text.
- The detailed breadth table can be absorbed into the sector visual area, but the current renderer is Streamlit markdown HTML, not React. A true React detail drawer would be a separate migration of `render_sector_breadth_market_map` and its dataframe expander contract.
