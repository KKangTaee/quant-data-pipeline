# Notes

- Worktree was dirty at start with user/local artifacts: saved portfolio JSONL, `.DS_Store`, run history JSONL, and several QA screenshots. These are unrelated and must not be reverted or staged.
- Futures Monitor is context-only. The fix must not create validation gate, monitoring signal, approval, order, or auto rebalance behavior.
- The issue reproduced with a service contract where stored `NQ=F` rows ended at `2026-06-05 21:00 UTC` but current time was `2026-06-06 09:00 UTC`. The old `UTC_TIMESTAMP()`-anchored query returned no rows, causing `MISSING`; the corrected latest-stored-candle query returns rows and marks them `Stale`.
- Browser QA on port 8502 showed `Futures Monitor` rendering Pre-open Core symbols with `Stale` state and live chart section visible on a weekend/closed-market state.
