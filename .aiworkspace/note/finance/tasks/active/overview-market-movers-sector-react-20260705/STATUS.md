# Overview Market Movers Sector React Migration Status

## 2026-07-05

- Scope: migrate the Market Movers sector breadth map and detail table into the existing React custom component.
- Boundary: no DB/provider/schema changes, no new refresh actions, no trading or validation semantics.
- Contract / implementation status: complete.
- React migration result: `섹터 / 시장 확산 맥락` now renders through the existing `market_movers_workbench` custom component when the built bundle is available. The old HTML map + Streamlit `st.expander` remains only as the component-unavailable fallback.
- Browser QA confirmed one React sector component iframe, 11 sector lanes, one React detail drawer, zero legacy `.ov-sector-breadth-map` nodes in the main page, and 3 negative lanes with red `#dc2626` bars.
