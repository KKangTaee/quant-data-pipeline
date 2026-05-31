# Final Review Candidate Board V1 Design

## Current State

`build_final_review_candidate_board_rows` flattens eligible candidates into table rows, but the board does not yet decide display priority. The current `Rank` is input order, not review priority.

## Implementation Direction

- Add a `build_final_review_candidate_board` read model around the existing row builder.
- Keep `build_final_review_candidate_board_rows` for table compatibility, but sort rows by review priority.
- Use the same Decision Cockpit / investability packet data already used by Final Review:
  - `SELECT_READY`
  - `HOLD_OR_RE_REVIEW`
  - `SELECT_BLOCKED`
- Add board-level summary:
  - total candidates
  - select-ready count
  - hold / re-review count
  - blocked count
  - first review candidate and action
- Add compact review queue rows above the full table.

## Sorting Policy

```text
1. SELECT_READY
2. HOLD_OR_RE_REVIEW
3. SELECT_BLOCKED
```

Tie-breakers:

```text
fewer blockers
fewer review-required rows
higher packet score
original order
```

## Non-Goals

- No new validation threshold.
- No source picker eligibility change.
- No registry append.
- No persistence schema change.
- No live approval, broker order, account sync, or auto rebalance.
