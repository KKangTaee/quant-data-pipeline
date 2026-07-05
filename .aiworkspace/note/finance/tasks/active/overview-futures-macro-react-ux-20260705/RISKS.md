# Overview Futures Macro React UX Risks

- Historical validation is useful context, so hiding it completely would reduce evidence quality.
- Fast entry must clearly label validation as not loaded until requested.
- React migration must preserve the no-signal / no-approval boundary.
- Phase 1 leaves validation session-only. Server restart, cache clear, daily refresh, or explicit reload requires the user to load historical validation again.
- Phase 5 still needs a deliberate cache/materialization decision; do not add a DB table casually before comparing process cache vs compact materialized summary.
