# Overview Market Movers Detail V3 Notes

- The detail panel remains context-only. It does not classify catalysts or recommend trades.
- `fetch_market_mover_compact_metadata` is only called after the user presses `간단 메타데이터 조회`; normal page render does not fetch news or SEC metadata.
- Metadata lookup output remains in Streamlit session state keyed by selected symbol/context. It is not persisted.
- External search links are still clickable starting points; opening them is a user action outside the app.
- Sector peer context is intentionally compact and based on currently displayed rows. Full sector breadth/heatmap remains 4차.
