# Notes

## Decision

- The existing Final Review sentiment panel says it is `Context only`, so its large first-read placement conflicts with Final Review's purpose.
- Do not convert CNN / AAII into market timing or rebalance guidance in this task. That requires separate research and look-ahead-safe validation.
- Keep sentiment detail in `Workspace > Overview > Sentiment`. Keep Operations > Portfolio Monitoring's read-only context overlay untouched.

## User-Facing Flow

1. User opens Final Review.
2. Decision Desk shows candidate availability and first candidate to inspect.
3. Candidate Board and investment report become the next visible decision surfaces.
4. Sentiment no longer appears as a Final Review panel or raw CNN / AAII table.
