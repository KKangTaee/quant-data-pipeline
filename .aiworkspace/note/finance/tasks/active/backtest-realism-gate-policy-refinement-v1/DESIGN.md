# Backtest Realism Gate Policy Refinement V1 Design

Status: Active
Created: 2026-05-29

## Existing Behavior

`build_investability_evidence_packet()` already creates a packet check for `Backtest Realism Audit`.
If the route is not `BACKTEST_REALISM_READY`, selected-route is blocked or held through `build_investability_gate_policy()`.

The gap is that policy evidence can remain route-level and generic.
After Phase 9-5, specific rows such as `Cost / slippage sensitivity evidence` should be visible in the gate policy row.

## Refinement

- Keep selected-route severity semantics unchanged.
- Add row-level merge for audit rows whose status is not PASS.
- Map Backtest Realism row-level `REVIEW` to `REVIEW_REQUIRED`.
- Map Backtest Realism row-level `NEEDS_INPUT` / `BLOCKED` to `BLOCK`.
- Preserve read-only behavior; no persistence, no order semantics.

## Expected Contract

| Audit row | Gate group | Severity |
| --- | --- | --- |
| `Cost / slippage sensitivity evidence` REVIEW | `backtest_realism` | `REVIEW_REQUIRED` |
| `Cost / slippage sensitivity evidence` NEEDS_INPUT | `backtest_realism` | `BLOCK` |
| `Liquidity / operability evidence` REVIEW | `backtest_realism` | `REVIEW_REQUIRED` |
| `Liquidity / operability evidence` NEEDS_INPUT / BLOCKED | `backtest_realism` | `BLOCK` |
