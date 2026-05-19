# Practical Validation Replay Service Boundary Risks

## Open Risks

- Actual replay can run DB-backed strategy runtime; tests should cover the plan contract with mocks instead of executing DB replay.
- The moved service module still imports `app.web.runtime.backtest` and curve helpers as transition debt.

## Closed In This Slice

- UI no longer imports the replay helper from `app.web`.
- Replay service import does not load Streamlit.
- Replay plan contract and blocked replay result contract are covered by `unittest` without DB runtime execution.
