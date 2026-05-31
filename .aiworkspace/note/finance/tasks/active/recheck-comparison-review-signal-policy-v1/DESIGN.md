# Recheck Comparison Review Signal Policy V1 Design

Status: Active
Created: 2026-05-29

## Design

Review Signals는 user-facing signal board이고, 성과 약화 threshold의 source-of-truth는 Recheck Comparison이다.

Policy source priority:

1. Recheck Operations Preflight route
2. Provider Evidence route
3. Recheck Comparison rows
4. Optional Actual Allocation drift route
5. Final Review stored evidence / triggers as context

## Status Mapping

| Source | Route / Status | Review Signal Status |
|---|---|---|
| Preflight | `RECHECK_PREFLIGHT_READY` | `CLEAR` |
| Preflight | `RECHECK_PREFLIGHT_REVIEW` | `WATCH` |
| Preflight | `RECHECK_PREFLIGHT_NEEDS_DATA` | `NEEDS_INPUT` |
| Preflight | `RECHECK_PREFLIGHT_BLOCKED` | `BREACHED` |
| Provider | `SELECTED_PROVIDER_READY` | `CLEAR` |
| Provider | `SELECTED_PROVIDER_REVIEW` | `WATCH` |
| Provider | `SELECTED_PROVIDER_NEEDS_DATA` | `NEEDS_INPUT` |
| Provider | `SELECTED_PROVIDER_BLOCKED` | `BREACHED` |
| Recheck Comparison row | `PASS` | `CLEAR` |
| Recheck Comparison row | `WATCH` | `WATCH` |
| Recheck Comparison row | `NEEDS_INPUT` | `NEEDS_INPUT` |
| Recheck Comparison row | `BREACHED` | `BREACHED` |
| Drift | not checked | `OPTIONAL` |

## Storage Boundary

- The policy reads existing selected decision, session recheck result, recheck preflight, provider evidence, and optional drift check.
- It does not write DB, registry, monitoring log, user memo, preset, alert record, order, approval, or rebalance instruction.
