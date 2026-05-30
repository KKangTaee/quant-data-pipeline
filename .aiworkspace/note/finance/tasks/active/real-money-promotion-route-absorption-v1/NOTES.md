# Real-Money Promotion Route Absorption V1 Notes

## Decision

- `Promotion` remains the main Real-Money decision.
- `Shortlist` becomes `Suggested Route` under Promotion.
- The main Real-Money question is: can this backtest result move into Compare / Practical Validation, or should it hold for blocker resolution?

## Implementation Note

`shortlist_status` metadata remains useful because downstream history / compare / saved records can still show compact route state.
The UX change is to stop presenting it as a peer validation item beside Promotion.
