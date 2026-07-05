# Overview Market Movers Sector React Migration Risks

- The fallback path must remain available when `component_static/index.html` is missing.
- The React detail drawer replaces the visible `st.expander`, so Browser QA must verify the drawer is inside the component iframe.
- Built Vite asset filenames can change; stage only the resulting `component_static` files and avoid local generated screenshots.
- Residual UI risk: the React custom component is an iframe, so its responsive breakpoint is based on iframe width, not the outer browser viewport. In common local QA width it renders 3 columns; wider iframes render 4.
