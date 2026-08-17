# Risks

- Data boundary is unchanged: UI uses stored 13F/price data only; this task opens no provider, loader, DB schema, registry, or live-trading path.
- Pre-2023 comparison can still use reported values with absolute-value comparison risk; this task only clarifies read-model meaning and does not revise historical source availability or proxy math.
- Remaining warning: the focused suite imports an external `edgar` package that emits three deprecation warnings; it is unrelated to this change.
