# Overview Primary Tab Soft Remove V1 Notes

## Decisions

- Remove both `Futures Monitor` and `Sector / Industry` from the Overview primary selector.
- Treat this as product simplification, not a data pipeline or service deletion.
- Existing futures and sector calculations are still useful as `Market Context` evidence, but not as separate user-facing destinations for now.

## Boundaries

- No provider / schema / DB changes.
- No registry / saved JSONL writes.
- No live trading, validation, monitoring, broker, or auto-rebalance semantics.
