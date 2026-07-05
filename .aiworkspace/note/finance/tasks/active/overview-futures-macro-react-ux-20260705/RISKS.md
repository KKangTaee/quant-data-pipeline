# Overview Futures Macro React UX Risks

- Historical validation is useful context, so hiding it completely would reduce evidence quality.
- Fast entry must clearly label validation as not loaded until requested.
- React migration must preserve the no-signal / no-approval boundary.
- Phase 1 leaves validation session-only. Server restart, cache clear, daily refresh, or explicit reload requires the user to load historical validation again.
- Phase 2 Browser QA verified visual React render but could not prove iframe button clicks dispatch through the custom component bridge in this automation environment. Unit tests cover nested/direct event payload parsing and Python dispatch boundaries; Phase 3 or final QA should re-check the click path manually or with a browser method that can deliver iframe events.
- React `component_static` is checked in for Streamlit runtime availability. When editing `src/`, always rerun `npm run build` and stage the new static assets with the source change.
- Phase 5 still needs a deliberate cache/materialization decision; do not add a DB table casually before comparing process cache vs compact materialized summary.
