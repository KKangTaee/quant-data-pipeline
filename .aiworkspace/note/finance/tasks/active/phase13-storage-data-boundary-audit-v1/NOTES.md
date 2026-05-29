# Phase 13 Storage / Data Boundary Audit V1 Notes

Status: Complete
Created: 2026-05-30

## Findings

- `app/workspace_paths.py` centralizes registry, saved, run history, run artifact, and backtest artifact directories.
- `app/runtime/portfolio_selection_v2.py` is the main V2 workflow JSONL boundary.
- `app/runtime/candidate_registry.py`, `app/runtime/portfolio_store.py`, `app/runtime/history.py`, and `app/jobs/run_history.py` remain legacy / saved setup / generated history surfaces.
- `finance/data/*lifecycle*` collectors write DB rows and expose no registry write side effects.
- Selected Dashboard read models repeatedly expose read-only execution boundaries and service contracts assert them.

## Interpretation

The project is not currently adding a JSONL row for every phase or user comment.
The remaining JSONL writes are either workflow stage handoff, compact validation / decision evidence, saved setup, legacy compatibility, or local generated history.

This task did not change code because the audit found no immediate defect.
