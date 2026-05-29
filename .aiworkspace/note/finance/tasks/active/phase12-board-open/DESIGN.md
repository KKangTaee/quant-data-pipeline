# Phase 12 Board Open Design

Status: Complete
Created: 2026-05-29

## Board Decision

Phase 12 is the selected monitoring / recheck operations phase.

The board starts with source mapping rather than implementation because Selected Portfolio Dashboard already has partial monitoring surfaces:

- Final Review -> dashboard continuity check
- Recheck Readiness
- Symbol Freshness
- Provider Evidence
- Portfolio Monitoring Timeline
- Review Signals
- Recheck Comparison
- optional Actual Allocation / Drift Check
- Decision Dossier

The next task must first decide which evidence is source-of-truth, which evidence is session-only, and which gaps require read-model or policy refinements.

## Initial Task Split

- 12-1 maps existing selected monitoring sources.
- 12-2 handles recheck readiness and symbol freshness operations contract.
- 12-3 handles selected provider evidence staleness and coverage.
- 12-4 handles recheck comparison and review signal policy.
- 12-5 handles optional allocation drift evidence boundary.
- 12-6 handles decision dossier, continuity, and timeline consistency.
- 12-7 closes the phase with integrated QA.

## Storage Boundary

No new JSONL registry, automatic monitoring log append, memo, preset, report artifact, account integration, approval, order, or auto rebalance path is part of board open.
