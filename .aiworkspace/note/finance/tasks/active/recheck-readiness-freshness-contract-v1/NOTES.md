# Recheck Readiness / Freshness Contract V1 Notes

Status: Complete
Created: 2026-05-29

## Notes

- The preflight contract intentionally wraps existing readiness and symbol freshness contracts instead of replacing them.
- Final Review embedded replay contract is now the first source, with Current Candidate Registry as fallback.
- Performance Recheck execution uses the same resolver as preflight, avoiding a ready preflight for contracts execution cannot replay.
- `SYMBOL_FRESHNESS_MISSING` maps to preflight `NEEDS_DATA`; `SYMBOL_FRESHNESS_STALE` maps to preflight `REVIEW`.
- No new persistence path was added.
