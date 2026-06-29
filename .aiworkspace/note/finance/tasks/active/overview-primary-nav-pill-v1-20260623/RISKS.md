# Overview Primary Nav Pill V1 Risks

## Closed Risks

- Custom HTML nav uses query-param navigation. Browser QA confirmed direct tab selection works on `?overview_tab=market-movers`.
- Streamlit theme changes can affect spacing around the markdown block. Current CSS is scoped to `.ov-primary-nav`.
