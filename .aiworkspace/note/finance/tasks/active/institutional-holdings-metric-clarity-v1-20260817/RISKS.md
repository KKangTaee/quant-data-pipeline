# Risks

- Data boundary is unchanged: UI uses stored 13F/price data only; this task opens no provider, loader, DB schema, registry, or live-trading path.
- Pre-2023 comparison can still use reported values with absolute-value comparison risk; this task only clarifies read-model meaning and does not revise historical source availability or proxy math.
- Remaining warning: the focused suite imports an external `edgar` package that emits three deprecation warnings; it is unrelated to this change.
- Closed QA issue: formula white-on-light contrast was fixed in `7b8fd606` and verified on a fresh server.
- Operational caution: Browser QA after Python payload changes must use a fresh Streamlit process or explicitly restart the existing one; otherwise module cache can make current React and stale Python contracts look inconsistent.
