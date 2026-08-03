# Risks

- Existing persisted snapshots do not contain active-anchor dates. Legacy inference must be
  labeled as history-window evidence, not an exact confirmation date.
- The refresh remains synchronous; truthful duration feedback improves usability but does not
  remove provider and materialization latency.
- A structural arrow can still be mistaken for a forecast unless the map and transition card
  both repeat the non-forecast boundary.
- Production component build output must be regenerated after source changes.

## Closeout Residual Risks

- Manual freshness refresh remains a synchronous provider collection and materialization path.
  Historical successful runs took roughly 42-97 seconds; this iteration makes the wait and dates
  truthful but does not introduce async execution or reduce provider latency.
- The freshness target remains a business-day calculation target, not a provider-by-provider
  release calendar.
- Legacy anchor fallback dates are bounded by loaded history and are therefore labeled as
  first-seen evidence rather than exact confirmation.
- No remaining implementation or QA blocker was found for this task.
