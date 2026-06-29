# Overview Market Context UX V3 Risks

## Residual Risks

- Direct `/overview` first-load still shows Streamlit's `Page not found` modal before/alongside the app fallback. The normal navigation path is root `/` and top navigation `Overview`, which renders without the modal. Fixing this likely needs a broader Streamlit routing strategy or an accepted URL policy, not a Market Context copy/layout patch.
- The new card hierarchy intentionally pushes source details into supporting/collapsible areas. Users who relied on all source caveats being visible immediately may need to open `자료 기준 / 출처 상태`.
- Some source names and product tab labels remain English by design because they are canonical UI names or source names.
