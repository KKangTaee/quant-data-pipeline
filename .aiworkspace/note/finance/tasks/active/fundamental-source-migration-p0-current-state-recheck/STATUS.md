# Status

Status: Complete
Updated: 2026-06-30

## Summary

Phase 0 current-state recheck completed. Local DB coverage and code usage still match the research direction closely enough to continue with the planned migration order.

## Findings

- Current branch is `codex/sub-dev`.
- Pre-existing local/generated changes are present and intentionally excluded from commits: `finance/.DS_Store`, `.aiworkspace/note/finance/run_history/BACKTEST_RUN_HISTORY.jsonl`, `.superpowers/`.
- Market Movers still defaults to broad `load_fundamental_snapshot` in `app/services/overview/why_it_moved.py`.
- Strict annual statement paths are present, while quarterly prototype paths are still exposed.
- Local quarterly statement shadow still includes `10-K` and `10-K/A` rows, so Phase 3 quarterly correctness gate remains necessary.

## Next

Proceed to Phase 1 source contract freeze.
