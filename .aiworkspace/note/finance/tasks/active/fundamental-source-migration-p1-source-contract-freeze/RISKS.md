# Risks

## Remaining

- Phase 1 only labels source contracts. Market Movers still uses the broad loader by default until Phase 2.
- Quarterly prototype rows are still exposed but marked non-canonical in strategy evidence. The data correctness gate is Phase 3.
- `pytest` is not installed in the local project environment, so guide-style pytest verification currently uses `uv run --with pytest`.

## Blockers

None for continuing to Phase 2.
