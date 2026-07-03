# Risks

- The repo does not yet have React / Vite scaffold. Phase 1 must add the smallest component structure without forcing a full frontend migration.
- Streamlit custom components still rerun Python when events return, so this pilot improves UI cohesion but does not create a full SPA interaction model.
- Browser QA should avoid broad provider collection unless a phase explicitly requires a small, approved live action check.
- Top filters are intentionally not migrated in this pilot. Moving them to React requires a separate pre-snapshot component because those values determine DB snapshot loading before the workbench payload is built.
- The React component is now a committed static bundle. Any TS/CSS change must be followed by `npm run build` and committed with the updated `component_static/` files.
