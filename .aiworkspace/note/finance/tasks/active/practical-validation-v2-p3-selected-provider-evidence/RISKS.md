# Risks

- Provider context is ETF-oriented. Non-ETF selected strategies may correctly show `NEEDS_DATA` rather than pass.
- Local DB availability can vary, so tests should inject provider context and avoid live MySQL.
- Candidate Registry replay contract gaps should be surfaced as blockers, not silently replaced by memo-like user data.
- Live DB provider coverage was not asserted in tests; runtime surfaces loader/DB errors as `SELECTED_PROVIDER_NEEDS_DATA`.
