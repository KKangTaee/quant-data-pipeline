# JSONL Registry Audit Dry-Run Report

Status: Read-only dry run
Date: 2026-06-01
Worktree: `/Users/taeho/Project/quant-data-pipeline-worktrees/main-dev`

## Executive Summary

No JSONL registry, saved setup, or run-history file was modified.

Current Selected Dashboard state is valid:

| Check | Result |
|---|---:|
| Final Decision selected rows | 4 |
| Selected Dashboard rows built from current Final Decision | 4 |
| Dashboard portfolio count | 1 |
| Assigned selected decision references | 4 |
| Missing dashboard references | 0 |
| Duplicate dashboard references | 0 |
| Live approval / order / auto rebalance | Disabled |

Recommended policy for the GRS 4 rows: keep them as `FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl` self-contained selected records. The current runtime supports this: Selected Dashboard and recheck readiness can use the embedded Final Decision contract without corresponding source/result registry rows. Do not synthesize `PORTFOLIO_SELECTION_SOURCES` or `PRACTICAL_VALIDATION_RESULTS` rows for GRS unless the strategies are re-run through the current Backtest Analysis -> Practical Validation -> Final Review gates.

## Inventory

| JSONL | Git state | Rows | schema_version | Main ids / status | Current code consumers | Dry-run class |
|---|---:|---:|---|---|---|---|
| `registries/PORTFOLIO_SELECTION_SOURCES.jsonl` | untracked | 1 | `1` | GTAA Clean-6 source `selection_latest_backtest_run_gtaa_clean_6...` | `app/runtime/portfolio_selection_v2.py`, `app/web/backtest_practical_validation.py` | `needs-user-decision` |
| `registries/PRACTICAL_VALIDATION_RESULTS.jsonl` | untracked | 2 | `5` | GTAA Clean-6 validations; both `READY_FOR_FINAL_REVIEW`, but selected-route preflight currently not allowed | `app/runtime/portfolio_selection_v2.py`, `app/web/backtest_practical_validation.py`, `app/web/backtest_final_review.py`, `app/web/backtest_final_review_helpers.py` | `needs-user-decision` |
| `registries/FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl` | tracked clean | 4 | `2` | 4 GRS `SELECT_FOR_PRACTICAL_PORTFOLIO` rows | `app/runtime/portfolio_selection_v2.py`, `app/runtime/final_selected_portfolios.py`, `app/web/backtest_final_review.py`, `app/services/backtest_evidence_read_model.py` | `keep-current` |
| `saved/SELECTED_DASHBOARD_PORTFOLIOS.jsonl` | tracked clean | 1 | `1` | `Final Review 통과 후보 2026-06-01`, 4 assigned GRS ids | `app/runtime/final_selected_portfolios.py`, `app/web/final_selected_portfolio_dashboard.py` | `keep-current` |
| `saved/SAVED_PORTFOLIOS.jsonl` | tracked clean | 2 | `1` | legacy reusable weighted setup | `app/runtime/portfolio_store.py`, `app/web/backtest_compare.py`, `app/web/overview_dashboard_helpers.py` | `keep-current` |
| `registries/FINAL_PORTFOLIO_SELECTION_DECISIONS_V1.jsonl` | archived legacy | 2 | `1` | V1 selected decisions | `app/runtime/final_selection_decisions.py` export only; not Selected Dashboard input | `archive-legacy` |
| `registries/CURRENT_CANDIDATE_REGISTRY.jsonl` | tracked clean | 10 | `1` | 9 active / 1 inactive current-candidate rows | `app/runtime/candidate_registry.py`, Candidate Library / legacy Proposal / selected recheck fallback | `archive-legacy` |
| `registries/CANDIDATE_REVIEW_NOTES.jsonl` | tracked clean | 5 | `1` | 5 active review notes | `app/runtime/candidate_registry.py`, legacy Candidate Review | `archive-legacy` |
| `registries/PRE_LIVE_CANDIDATE_REGISTRY.jsonl` | tracked clean | 5 | `1` | 5 active paper-tracking rows | `app/runtime/candidate_registry.py`, legacy Candidate Library / Proposal | `archive-legacy` |
| `registries/PORTFOLIO_PROPOSAL_REGISTRY.jsonl` | tracked clean | 4 | `1` | 4 revisions of `proposal_20260503_0fb12b` | `app/runtime/portfolio_proposal.py`, legacy Portfolio Proposal | `archive-legacy` |
| `registries/PAPER_PORTFOLIO_TRACKING_LEDGER.jsonl` | tracked clean | 1 | `1` | legacy paper observation row | `app/runtime/paper_portfolio_ledger.py`, legacy paper compatibility | `archive-legacy` |
| `run_history/BACKTEST_RUN_HISTORY.jsonl` | tracked modified | 62 | `2` | local backtest execution history | `app/runtime/history.py`, Operations Backtest History | `delete-generated` |
| `run_history/WEB_APP_RUN_HISTORY.jsonl` | ignored local | 10 | `2` | local ingestion/job execution history | `app/jobs/run_history.py`, Ops Review / Overview ops surfaces | `delete-generated` |

Expected optional files not present:

| JSONL | Status | Action |
|---|---|---|
| `registries/SELECTED_PORTFOLIO_MONITORING_LOG.jsonl` | absent | No action. Optional explicit monitoring log only. |
| `saved/SAVED_PORTFOLIO_MIXES.jsonl` | absent | No action. `SAVED_PORTFOLIOS.jsonl` remains the current compatibility saved setup. |

## Row Classification

| File | Rows / ids | Classification | Reason |
|---|---|---|---|
| `FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl` | `final_selected_grs_liquid_macro_top2_20260601`; `final_selected_grs_macro_top1_ma200_20260601`; `final_selected_grs_qqq_gold_bonds_top2_ma150_20260601`; `final_selected_grs_macro_top3_ma200_20260601` | `keep-current` | Selected Dashboard input. All selected, component count 1, target weight 100%, dashboard status `normal`. |
| `SELECTED_DASHBOARD_PORTFOLIOS.jsonl` | `selected_dashboard_portfolio_final_review_passes_20260601` | `keep-current` | User-created monitoring portfolio. References all 4 GRS decisions and has no missing ids. |
| `SAVED_PORTFOLIOS.jsonl` | `portfolio_e81d1c7966d3`; `portfolio_gtaa_spy_low_mdd_60_ew_growth_sector_gold_40` | `keep-current` | Legacy saved setup remains actively readable for saved replay / overview compatibility. No migration required unless requested separately. |
| `PORTFOLIO_SELECTION_SOURCES.jsonl` | GTAA Clean-6 source row | `needs-user-decision` | Current schema, but untracked and unrelated to the GRS Dashboard state. Keep if preserving audit/replay source; archive if the goal is a minimal selected-dashboard-only active set. |
| `PRACTICAL_VALIDATION_RESULTS.jsonl` line 1 | GTAA validation `_50ce8a39` | `archive-legacy` | Current schema but obsolete for active flow: `final_review_gate.can_save_and_move=false`; selected-route preflight `select_allowed=false`; Final Review hides it. |
| `PRACTICAL_VALIDATION_RESULTS.jsonl` line 2 | GTAA validation `_80b3f2e7` | `needs-user-decision` | Later row has `final_review_gate.can_save_and_move=true`, but current selected-route preflight still returns `select_allowed=false`; Final Review hides it. Archive for minimal active set, keep only if preserving audit trail. |
| `FINAL_PORTFOLIO_SELECTION_DECISIONS_V1.jsonl` | 2 V1 decisions | `archive-legacy` | V1 history. Current Dashboard reads current Final Decision only. Do not migrate unless current selected-route gate is re-run and passes. |
| Legacy candidate / proposal / paper files | all rows in `CURRENT_CANDIDATE_REGISTRY`, `CANDIDATE_REVIEW_NOTES`, `PRE_LIVE_CANDIDATE_REGISTRY`, `PORTFOLIO_PROPOSAL_REGISTRY`, `PAPER_PORTFOLIO_TRACKING_LEDGER` | `archive-legacy` | Compatibility records for Candidate Library / old Proposal / old paper flow. Not current Portfolio Selection current source-of-truth. |
| `run_history/*.jsonl` | all rows | `delete-generated` | Local/generated execution history, not durable decision source. Archive first if the user wants rollback/debug context. |

## Reference Integrity

| Chain | Result |
|---|---|
| GTAA `PRACTICAL_VALIDATION_RESULTS` -> `PORTFOLIO_SELECTION_SOURCES` | Both result rows reference the existing GTAA source row. |
| GRS `FINAL_PORTFOLIO_SELECTION_DECISIONS` -> source/result registries | 4/4 selected GRS rows have missing source/result registry counterparts. |
| GRS `FINAL_PORTFOLIO_SELECTION_DECISIONS` self-contained contract | 4/4 rows have embedded selected components and dashboard-readable evidence. |
| `SELECTED_DASHBOARD_PORTFOLIOS` -> Final Decision | 4/4 assigned ids exist. |

## GRS Chain Decision

Recommendation: treat the GRS 4 Final Decision rows as self-contained selected records.

Rationale:

- Current Selected Dashboard source-of-truth is `FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`.
- `app/runtime/final_selected_portfolios.py` builds dashboard rows directly from Final Decision selected rows.
- Focused contract `test_recheck_readiness_uses_embedded_final_decision_contract_without_registry` passed.
- Creating source/result rows after the fact would be synthetic unless the latest Backtest Analysis and Practical Validation gates are re-run.
- Gate relaxation is explicitly out of scope.

Alternative if a complete current chain is required: re-run each GRS candidate through the current Backtest Analysis -> Practical Validation -> Final Review flow, append fresh `PORTFOLIO_SELECTION_SOURCES` and `PRACTICAL_VALIDATION_RESULTS` rows only if current gates pass, then decide whether to keep the existing Final Decision ids or append new selected decisions. This is a new migration task, not a cleanup rewrite.

## Recommended Cleanup After Approval

Default recommendation for a minimal current active state:

| Action | Files |
|---|---|
| Keep | `FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`; `SELECTED_DASHBOARD_PORTFOLIOS.jsonl`; `SAVED_PORTFOLIOS.jsonl` |
| Archive from active registries | `FINAL_PORTFOLIO_SELECTION_DECISIONS_V1.jsonl`; `CURRENT_CANDIDATE_REGISTRY.jsonl`; `CANDIDATE_REVIEW_NOTES.jsonl`; `PRE_LIVE_CANDIDATE_REGISTRY.jsonl`; `PORTFOLIO_PROPOSAL_REGISTRY.jsonl`; `PAPER_PORTFOLIO_TRACKING_LEDGER.jsonl` |
| Needs decision | `PORTFOLIO_SELECTION_SOURCES.jsonl`; `PRACTICAL_VALIDATION_RESULTS.jsonl` |
| Delete generated after backup | `run_history/BACKTEST_RUN_HISTORY.jsonl`; `run_history/WEB_APP_RUN_HISTORY.jsonl` |
| Do not create | `SELECTED_PORTFOLIO_MONITORING_LOG.jsonl`; `SAVED_PORTFOLIO_MIXES.jsonl` |

For the two untracked GTAA current-workflow files, the stricter "only rows the latest Final Review / Dashboard can actually use" interpretation means archive both files because the Practical Validation rows are not current selected-route eligible. If the user wants to preserve GTAA as a re-validation audit trail, keep them but do not treat them as selected Dashboard input.

## Approval-Time Procedure

If approved, run cleanup in this order:

1. Create timestamped archive backup under `.aiworkspace/note/finance/archive/jsonl-registry-audit-20260601/<timestamp>/`.
2. Copy every existing JSONL there before modifying anything.
3. Write an archive manifest with source path, row count, SHA-256, classification, and action.
4. Deterministically rewrite kept JSONL files:
   - sort by stable id and timestamp where rewrite is needed,
   - normalize JSON with `ensure_ascii=False`,
   - preserve one JSON object per line,
   - do not synthesize GRS source/result rows.
5. Remove archived legacy/generated files from active locations only after backup verification.
6. Re-run parse, integrity, Selected Dashboard read model, focused service contracts, and `git diff --check`.
7. Write a final cleanup report listing keep/archive/delete/rewrite results.

## Verification Results

| Verification | Result |
|---|---|
| JSONL parse check | Passed: 13 files, 109 object rows, 0 invalid rows. |
| Source/result/final decision reference check | Passed with known GRS source/result gap documented. |
| Selected Dashboard read model | Passed: selected rows 4, dashboard rows 4, assigned 4, missing 0. |
| Focused service contracts | Passed: 6 `unittest` tests. |
| `pytest` attempt | Not run: `.venv` has no `pytest` module. |
| `git diff --check` | Passed. |

## Guardrails

- No DB changes.
- No live approval.
- No broker/account connection.
- No order instruction.
- No auto rebalance.
- No Final Review gate relaxation.
