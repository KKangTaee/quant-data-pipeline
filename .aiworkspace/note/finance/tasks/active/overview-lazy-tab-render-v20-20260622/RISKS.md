# Risks

- Remaining visual tradeoff: top-level deep navigation now uses `st.segmented_control` (or horizontal `st.radio` fallback) instead of native `st.tabs`, so the control looks like a segmented selector rather than Streamlit tab headers.
- Candidate Ops behavior is preserved by loading the same dashboard snapshot inside the selected branch. No Candidate Ops logic was changed.
- This only defers renderer execution; heavy queries inside the selected tab can still take time when that tab is opened.
