# Structured Waiver Policy V1 Notes

Status: Active
Created: 2026-05-28

## Findings

- Current `build_investability_gate_policy` returns `waiver_supported=False`.
- Current selected route behavior is conservative: blockers / review-required gaps prevent `SELECT_FOR_PRACTICAL_PORTFOLIO`.
- A useful future waiver must be structured, scoped, expiring, and tied to review triggers.
- `BLOCK` severity should not be waiverable because it represents missing or invalid critical evidence.

## Decision

- Keep current implementation as `waiver_supported=False`.
- Future waiver may only consider `REVIEW_REQUIRED`, not `BLOCK`.
- Future waiver must not convert the original gap into `PASS`.
- Default storage target, if implemented, is compact final decision snapshot rather than a new registry.
