# Overview Market Movers Sector React Migration Notes

- Existing React custom component already supports multiple payload branches: workbench summary and selected-symbol investigation pane.
- Sector breadth map can follow the same branch pattern instead of creating a second custom component bundle.
- Python remains the source of truth for `sector_breadth` data and table rows; React only renders the already-prepared read model.
- The React sector component uses the same left-to-right magnitude convention as the latest HTML polish. Negative sectors use `danger` / red tone and do not render around a central zero marker.
- The detail table is now a React `<details>` drawer inside the same custom component payload. Streamlit `st.expander` is retained only in `_render_market_movers_sector_breadth_fallback`.
- In the browser QA viewport the Streamlit iframe width was below the 1180px breakpoint, so the sector lanes rendered as 3 columns. The CSS default remains 4 columns and narrows to 3 columns at intermediate widths.
- Follow-up root cause: opening a native `<details>` element does not necessarily trigger a React render or the custom component's existing mount-time height sync. The sector detail table rendered inside the iframe, but the parent Streamlit frame stayed at the closed height and clipped the expanded table. The fix attaches a small `Streamlit.setFrameHeight()` resync helper to detail toggle events.
