# Overview Futures Macro React UX Risks

- Historical validation is useful context, so hiding it completely would reduce evidence quality.
- Fast entry must clearly label validation as not loaded until requested.
- React migration must preserve the no-signal / no-approval boundary.
- Phase 1 leaves validation session-only. Server restart, cache clear, daily refresh, or explicit reload requires the user to load historical validation again.
- Phase 2 Browser QA verified visual React render but could not prove iframe button clicks dispatch through the custom component bridge in this automation environment. Phase 3 also could not capture a new Browser screenshot because the Codex In-app Browser tab API timed out while listing / reading tabs. Unit tests cover nested/direct event payload parsing and Python dispatch boundaries; final QA should re-check iframe visual rendering and click dispatch manually or with a browser method that can deliver iframe events.
- React `component_static` is checked in for Streamlit runtime availability. When editing `src/`, always rerun `npm run build` and stage the new static assets with the source change.
- 1W / 1M flow is computed from already stored 1D candles (`5D %` / `20D %`). It is context only and should not be reframed as a trading signal or validation gate.
- Phase 4 mixed subtypes are interpretation labels, not directional validation labels. Historical validation should continue to report mixed states as occurrence / N/A hit-rate rather than forcing risk-on or risk-off samples.
- Phase 5 chose process cache, not DB materialization. If another workflow later needs validation summaries across app restarts or across machines, revisit compact persisted summary design with explicit retention and source-of-truth semantics.
- Final Browser QA could verify the current-code iframe render and visible state, but iframe button click dispatch still needs manual or alternate automation confirmation if that specific bridge behavior is questioned. Unit tests cover nested/direct event payload handling and Python action dispatch boundary.
