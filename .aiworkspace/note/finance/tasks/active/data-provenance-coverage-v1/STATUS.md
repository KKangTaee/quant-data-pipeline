# Data Provenance Coverage V1 Status

Status: Complete
Last Updated: 2026-05-28

## Completed

- Added provider context schema v2 with compact provenance / freshness summaries.
- Added source mix, coverage status weight, as-of range, collected range, stale symbols, stale weight, and compact symbol rows for ETF provider areas.
- Added macro provenance with source mode, observation range, collected range, stale series, and compact series rows.
- Stale ETF provider snapshot evidence now downgrades otherwise-PASS diagnostics to `REVIEW`.
- Provider Coverage display rows now include `Source Mix`, `Freshness`, and `As Of Range`.
- Practical Validation metrics now carry compact source / freshness fields for Final Review packet interpretation.
- Added focused service contract test coverage.

## Next

1. Use `look-through-exposure-board-v1` to show holdings / exposure coverage more directly.
2. Keep full holdings / exposure / macro rows in DB, not JSONL.
3. Revisit the 45-day ETF provider freshness threshold only after real provider cadence data is reviewed.
