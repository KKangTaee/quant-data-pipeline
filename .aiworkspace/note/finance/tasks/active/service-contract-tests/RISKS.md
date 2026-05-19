# Service Contract Tests Risks

## Open Risks

- The tests intentionally cover service payload contracts, not full UI behavior.
- `app.services -> app.web` imports remain transition debt and are handled by boundary lint advisories, not by this test as failures.

## Closed In This Slice

- Service handoff persistence paths are tested with mocks, so the test suite does not mutate registry JSONL.
- Fresh-process service imports confirm `streamlit` is not loaded by the current service modules.
