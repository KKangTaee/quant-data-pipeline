# Lifecycle Audit Scoring V1 Notes

Status: Active
Created: 2026-05-28

## Findings

- `build_data_coverage_audit()` already reads compact lifecycle rows through `finance.loaders.universe`.
- PASS currently depends on requested-period coverage through lifecycle rows.
- The evidence string needs to distinguish source classes so operator review can tell current snapshot evidence from actual historical evidence.

## Policy

- Current listing snapshots are partial evidence.
- SEC CIK / ticker / exchange cross-check rows are identity evidence.
- Computed snapshot rows are partial observed-window evidence in Phase 8.
- Actual lifecycle coverage requires `coverage_status=actual` and requested-period coverage.
