# Risks

- The repo does not yet have React / Vite scaffold. Phase 1 must add the smallest component structure without forcing a full frontend migration.
- Streamlit custom components still rerun Python when events return, so this pilot improves UI cohesion but does not create a full SPA interaction model.
- Browser QA should avoid broad provider collection unless a phase explicitly requires a small, approved live action check.
