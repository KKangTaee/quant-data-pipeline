# ETF Rerun Matrix Workbench 4B Risks

## Open

- Default runtime runners may fail if local DB price coverage is incomplete; UI captures scenario-level errors and keeps the matrix session-local.
- Provider snapshot collection, durable strategy hub / report, Practical Validation handoff, and Current Candidate promotion remain open follow-up scope.

## Closed

- Browser QA avoided forcing a costly DB rerun and verified panel rendering / boundary copy instead.
- The panel explicitly separates session-only matrix results from Practical Validation, Final Review, Monitoring, and Current Candidate promotion writes.
