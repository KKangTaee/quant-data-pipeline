# Recheck Readiness / Freshness Contract V1 Design

Status: Complete
Created: 2026-05-29

## Contract

Runtime contract:

- `schema_version`: `selected_recheck_operations_preflight_v1`
- `route`: `RECHECK_PREFLIGHT_READY`, `RECHECK_PREFLIGHT_REVIEW`, `RECHECK_PREFLIGHT_NEEDS_DATA`, `RECHECK_PREFLIGHT_BLOCKED`
- nested evidence:
  - `readiness`: existing `selected_recheck_readiness_v1`
  - `symbol_freshness`: existing `selected_recheck_symbol_freshness_v1`
- `execution_boundary`: read-only, no DB write, no registry write, no monitoring log auto write, no live approval, no order, no auto rebalance

## Replay Contract Source Priority

1. Final Review selected component embedded contract
2. Current Candidate Registry fallback by `registry_id`
3. Blocked if neither source can build a replay payload

The same resolver feeds readiness, symbol freshness symbol resolution, and Performance Recheck execution so preflight does not report ready for a source that execution cannot use.

## Route Mapping

| Input State | Preflight Route |
|---|---|
| readiness blocked or symbol freshness blocked | `RECHECK_PREFLIGHT_BLOCKED` |
| readiness needs data, freshness missing, or freshness needs data | `RECHECK_PREFLIGHT_NEEDS_DATA` |
| readiness review, freshness watch, or freshness stale | `RECHECK_PREFLIGHT_REVIEW` |
| readiness ready and freshness ready | `RECHECK_PREFLIGHT_READY` |

## Storage Boundary

The contract reads selected final decision row, Current Candidate Registry fallback, DB latest market date, and DB price freshness metadata.
It does not collect data, append monitoring logs, create user notes, save presets, write reports, create orders, or rebalance anything.
