# Provider Gap Collection Boundary Risks

## Open Risks

- Provider collectors can write DB snapshots and run history when invoked from the UI; tests must mock those calls.
- `app.jobs.run_history` still points at the legacy `.note/finance/run_history` path in this codebase. This task preserves behavior and does not change run history storage.
- Existing `app.services -> app.web` transitional import debt remains advisory.

## Closed In This Slice

- Streamlit UI no longer imports provider ingestion jobs directly for the Provider Data Gaps button.
- Provider gap plan / run orchestration is covered by service contract tests without performing DB writes.
