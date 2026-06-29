# Overview Nav Internal Lazy Load V1 Risks

## Open Risks

- `st.pills` visual styling depends on Streamlit DOM classes; custom CSS must stay scoped and not rely on fragile unrelated selectors.

## Closed Or Bounded Risks

- Anchor-based tab navigation is removed from the render path. Query-param slug reading remains only as compatibility input and is not rendered as clickable navigation.
- Browser QA confirmed the first-load lazy gate shows `시장 맥락 불러오기` before the heavy Market Context body, and that switching to Market Movers stays in the same browser tab.
- Browser QA found dark-theme inactive tabs were too dim; the CSS now uses Streamlit theme text color for inactive tab readability.
