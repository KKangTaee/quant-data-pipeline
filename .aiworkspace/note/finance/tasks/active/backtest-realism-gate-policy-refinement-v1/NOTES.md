# Backtest Realism Gate Policy Refinement V1 Notes

## Findings

- `build_investability_evidence_packet()` already includes Backtest Realism Audit route as a packet check.
- Existing selected-route semantics are broadly correct:
  - `BACKTEST_REALISM_NEEDS_INPUT` / `BLOCKED` blocks selection.
  - `BACKTEST_REALISM_REVIEW` holds selection for review.
- The policy row evidence is too generic for Phase 9 row-level gaps. It should mention the failing Backtest Realism row, such as cost / slippage sensitivity or liquidity capacity.

## Boundary

- Refine read model evidence only.
- Do not add persistence, waiver storage, or live trading behavior.

## Result

- Final Review gate policy still uses the existing selected-route semantics.
- Failing Backtest Realism row criteria now surface in policy evidence.
- `NEEDS_INPUT` status is explicitly treated as a blocker severity when row-level audit evidence is merged.
