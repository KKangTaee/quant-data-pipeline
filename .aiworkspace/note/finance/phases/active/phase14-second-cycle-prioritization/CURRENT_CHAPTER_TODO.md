# Phase 14 Current Chapter TODO

Status: Active
Created: 2026-05-30

## Current Chapter

Next task: `phase14-candidate-prioritization-v1`

## TODO

- Build a ranked candidate matrix from `phase13-residual-risk-carry-forward-v1/CARRY_FORWARD_MATRIX.md`.
- Separate immediately implementable workflow hardening from data-source review and product-research candidates.
- Recommend the first implementation slice and owner skill.
- Keep storage and trading automation boundaries explicit.

## Stop Conditions

- Do not implement code inside candidate prioritization.
- Do not add a new registry, memo, preset, closeout comment store, or monitoring-log auto-write.
- Do not adopt paid / approval-based data sources without explicit user approval.
- Do not implement broker order, live approval, account sync, or auto rebalance.
