# Risks

- Existing persisted snapshots do not contain active-anchor dates. Legacy inference must be
  labeled as history-window evidence, not an exact confirmation date.
- The refresh remains synchronous; truthful duration feedback improves usability but does not
  remove provider and materialization latency.
- A structural arrow can still be mistaken for a forecast unless the map and transition card
  both repeat the non-forecast boundary.
- Production component build output must be regenerated after source changes.
