# Notes

- Current Practical Validation result table intentionally formats only `Date`, `Total Balance`, `Total Return`.
- Backtest latest result can have `Next Ticker`, `End Ticker`, `Next Weight`, `Selected Count`, and related rebalance columns, but those are lost when only compact curve records are persisted.
- Existing registry rows must remain untouched; fallback UI is required for old rows.
- New source snapshots carry compact `selection_history` rows only when the source result bundle contains ticker / weight evidence. Full holdings series or raw provider data is not copied into workflow JSONL.
- Mix V1 display keeps component selection histories separate. A portfolio-level monthly union can be derived later if the weighted portfolio builder exposes exact look-through holdings.
