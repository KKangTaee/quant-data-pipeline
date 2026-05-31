# Symbol Lifecycle Event Fields V1 Notes

Status: Active
Created: 2026-05-28

## Findings

- `nyse_symbol_lifecycle` already supports source category and coverage category.
- It needs event-level semantics before ticker change / merger ingestion is added.
- SEC Form 25 evidence should remain delisting-only evidence.
- NYSE current listing snapshot should remain partial evidence and not historical membership proof.
- The first Phase 8 implementation slice only changes DB row semantics and read path.
  It does not add a new source crawler or loosen Data Coverage Audit PASS criteria.
