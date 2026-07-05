# Risks

## 2026-07-05 - Initial Risks

- Removing Practical Validation sentiment overlay is safe only because it is context-only on this surface. Do not delete the shared service or alter Final Review / Monitoring sentiment context without separate approval.
- Changing shared Practical Validation visual CSS affects command center, step rail, section headers, cards, and alert panels in the tab. Browser QA is required.
- Generated screenshots and local run history should remain untracked.

## 2026-07-05 - Residual Risk

- `npm audit` reports 2 dependency warnings in the existing React component dependency tree. This task did not change dependency versions.
- The page still has Streamlit native `st.container(border=True)` surfaces around each flow. This pass changed the custom Practical Validation cards and React Fix Queue, not Streamlit's native container style.
