# Phase 13 Docs / Runbook Alignment V1 Design

Status: Complete
Created: 2026-05-30
Completed: 2026-05-30

## Alignment Principle

Durable docs should describe implemented behavior, not every task detail.
Task-level evidence remains in:

- `phase13-cycle-inventory-v1/INVENTORY.md`
- `phase13-gate-validation-qa-matrix-v1/QA_MATRIX.md`
- `phase13-storage-data-boundary-audit-v1/STORAGE_AUDIT.md`

Docs / runbooks should preserve only the repeatable interpretation:

- Final Decision V2 is the current selected dashboard source.
- legacy Final Decision V1 remains history / compatibility.
- DB-backed full evidence and workflow JSONL compact evidence stay separate.
- selected monitoring read models are read-only unless a user explicitly performs a scoped monitoring snapshot action.
- generated artifacts remain local and unstaged.

## Durable Docs Chosen

Updated durable docs:

- `docs/data/STORAGE_GOVERNANCE.md`
- `docs/data/README.md`
- `docs/flows/README.md`
- `docs/flows/PORTFOLIO_SELECTION_FLOW.md`
- `docs/flows/BACKTEST_UI_FLOW.md`
- `docs/GLOSSARY.md`
- `docs/runbooks/README.md`
- `docs/runbooks/PHASE_CLOSEOUT_QA.md`
- `docs/INDEX.md`
- `docs/ROADMAP.md`

No code behavior changed.
