# Phase 13 Current Chapter TODO

Status: Active
Created: 2026-05-29

## Current Chapter

Next task: `phase13-residual-risk-carry-forward-v1`

## TODO

- Triage residual risks from Phase 8~12 and Phase 13 13-1~13-4.
- Separate current product limitations, second-cycle candidates, and explicit out-of-scope broker-grade / production operations items.
- Use `phase13-cycle-inventory-v1/INVENTORY.md`, `phase13-gate-validation-qa-matrix-v1/QA_MATRIX.md`, `phase13-storage-data-boundary-audit-v1/STORAGE_AUDIT.md`, and `phase13-docs-runbook-alignment-v1/DOC_ALIGNMENT.md`.
- Do not convert residual risk triage into implementation.
- Do not introduce new storage or trading automation.

## Stop Conditions

- Do not implement account integration, order draft, approval, auto rebalance, or automatic monitoring log append.
- Do not add a new JSONL registry for notes, presets, or closeout comments.
- Do not mark unresolved broker-grade or production operations features as complete.
