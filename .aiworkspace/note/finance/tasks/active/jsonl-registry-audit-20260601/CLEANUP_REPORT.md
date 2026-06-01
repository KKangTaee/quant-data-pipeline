# JSONL Registry Cleanup Report

Status: Complete
Date: 2026-06-01
Archive: `.aiworkspace/note/finance/archive/jsonl-registry-audit-20260601/20260601T152645KST/`

## Summary

Approved cleanup was executed without DB, broker/account, order, live approval, or auto-rebalance actions.

All 13 pre-cleanup JSONL files were copied to the archive before active deletion. The archive manifest is:

```text
.aiworkspace/note/finance/archive/jsonl-registry-audit-20260601/20260601T152645KST/manifest.json
```

## Active JSONL After Cleanup

| Active JSONL | Rows | Reason |
|---|---:|---|
| `registries/FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl` | 4 | Current Final Review V2 selected source for Selected Dashboard |
| `saved/SELECTED_DASHBOARD_PORTFOLIOS.jsonl` | 1 | User-created dashboard portfolio with 4 GRS decision ids |
| `saved/SAVED_PORTFOLIOS.jsonl` | 2 | Legacy saved setup still read by saved replay / overview compatibility |

## Archived And Removed From Active

| JSONL | Rows | Action |
|---|---:|---|
| `registries/CANDIDATE_REVIEW_NOTES.jsonl` | 5 | archived, removed from active |
| `registries/CURRENT_CANDIDATE_REGISTRY.jsonl` | 10 | archived, removed from active |
| `registries/FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl` | 2 | archived, removed from active |
| `registries/PAPER_PORTFOLIO_TRACKING_LEDGER.jsonl` | 1 | archived, removed from active |
| `registries/PORTFOLIO_PROPOSAL_REGISTRY.jsonl` | 4 | archived, removed from active |
| `registries/PORTFOLIO_SELECTION_SOURCES.jsonl` | 1 | archived, removed from active |
| `registries/PRACTICAL_VALIDATION_RESULTS.jsonl` | 2 | archived, removed from active |
| `registries/PRE_LIVE_CANDIDATE_REGISTRY.jsonl` | 5 | archived, removed from active |
| `run_history/BACKTEST_RUN_HISTORY.jsonl` | 62 | archived, removed from active generated history |
| `run_history/WEB_APP_RUN_HISTORY.jsonl` | 10 | archived, removed from active generated history |

## Kept And Also Archived For Rollback

| JSONL | Rows |
|---|---:|
| `registries/FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl` | 4 |
| `saved/SELECTED_DASHBOARD_PORTFOLIOS.jsonl` | 1 |
| `saved/SAVED_PORTFOLIOS.jsonl` | 2 |

## GRS V2 Decision

The 4 GRS rows remain as self-contained `FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl` selected records. No synthetic source/result rows were created.

Current read model remains valid:

| Check | Result |
|---|---:|
| Final Decision V2 rows | 4 |
| Selected rows | 4 |
| Dashboard rows | 4 |
| Dashboard portfolios | 1 |
| Assigned selected references | 4 |
| Missing references | 0 |
| Duplicate references | 0 |
| Handoff route | `HANDOFF_READY` |
| Monitorable rows | 4 |
| Blocked rows | 0 |
| Live approval / order / auto rebalance | `false / false / false` |

## Verification

| Verification | Result |
|---|---|
| Archive manifest coverage | Passed: 13 entries |
| Archive SHA-256 verification | Passed |
| JSONL parse check | Passed for archive + active files |
| Selected Dashboard read model | Passed: selected 4, dashboard 4, assigned 4, missing 0 |
| Focused service contracts | Passed: 6 `unittest` tests |
| `git diff --check` | Passed |
| Browser QA | Not run; no UI or app code changed |

## Remaining Notes

- `PORTFOLIO_SELECTION_SOURCES.jsonl` and `PRACTICAL_VALIDATION_RESULTS.jsonl` are absent from active state after cleanup. The runtime can recreate them on the next Backtest Analysis / Practical Validation save.
- Legacy Candidate Library / Proposal / Paper views may show empty state until new rows are written or archive data is manually restored.
- `SAVED_PORTFOLIOS.jsonl` remains active because current saved replay / overview compatibility code still reads it.
