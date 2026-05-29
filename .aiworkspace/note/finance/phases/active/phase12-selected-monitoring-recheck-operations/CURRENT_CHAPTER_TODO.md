# Phase 12 Current Chapter TODO

Status: Active
Created: 2026-05-29

## Current Chapter

Next task: `allocation-drift-evidence-boundary-v1`

## TODO

- Confirm current value / shares x price / current weight inputs remain optional read-only drift evidence.
- Ensure drift alert preview cannot be read as broker order, approval, or auto rebalance guidance.
- Keep Update Review Signals as session-state reflection, not durable monitoring log append.
- Add focused contract tests for drift aligned / watch / rebalance / incomplete input boundary.

## Stop Conditions

- Do not implement account integration, order draft, approval, auto rebalance, or automatic monitoring log append.
- Do not add a new JSONL registry for monitoring notes or presets.
- Do not let Actual Allocation input imply account integration, order draft, approval, or auto rebalance.
