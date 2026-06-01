# Risks

- Streamlit still limits exact card grid control compared with a dedicated frontend, so the polish should use stable dimensions and restrained HTML rather than fragile DOM hacks.
- Browser QA must verify no text overflow or duplicated widget key errors.
- The in-app browser QA used the current dirty saved setup, including a test portfolio. The implementation does not rewrite or normalize that saved file.
- Full SaaS-grade interactions such as drawers, drag sorting, and richer modal behavior remain better suited to a future React-style front end, but were intentionally out of scope for this Streamlit polish slice.
