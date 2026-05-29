# Phase 9 Board Open Notes

Status: Active
Created: 2026-05-29

## Findings

- `app/services/backtest_realism_audit.py` already has rows for transaction cost, turnover, liquidity / operability, net policy, rebalance timing, tax/account scope, and execution boundary.
- Existing logic can detect missing cost and assumption-only cost, but Phase 9 needs stronger proof that cost was applied to the net result curve.
- Provider / liquidity evidence already exists in DB-backed provider snapshots, but capacity and selected notional realism still need a clearer contract.

## Decision

Start with source contract review before changing runtime behavior.
The first implementation should be based on what the current runtime can prove, not on optimistic assumptions.
