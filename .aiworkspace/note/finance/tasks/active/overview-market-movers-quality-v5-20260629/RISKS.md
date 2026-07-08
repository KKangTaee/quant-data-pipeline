# Overview Market Movers Quality V5 Risks

- Coverage trust state is derived from the current snapshot and missing rows; if upstream diagnostics are stale, the trust language can only reflect that stale evidence.
- Raw diagnostics still include lifecycle/profile strings from prior evidence columns. The grouped summary avoids unsupported conclusions, but users may still need to open raw evidence for symbol-level detail.
- Browser QA confirmed the trust strip does not create horizontal overflow at 390px, but very wide raw diagnostics tables still rely on Streamlit's dataframe scrolling when opened.
