# JSONL Write Audit

Status: Complete
Last Audited: 2026-05-28

## Main Workflow Chain

| File | Writer | Reader / Consumer | Classification | Policy |
|---|---|---|---|---|
| `PORTFOLIO_SELECTION_SOURCES.jsonl` | `app/runtime/portfolio_selection_v2.py` | Practical Validation | Main workflow registry | Keep. 후보 source handoff만 저장한다. |
| `PRACTICAL_VALIDATION_RESULTS.jsonl` | `app/runtime/portfolio_selection_v2.py`, `app/services/backtest_practical_validation.py` | Final Review | Main workflow registry | Keep. 12개 diagnostic / compact evidence / blocker만 저장한다. |
| `FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl` | `app/runtime/portfolio_selection_v2.py`, Final Review helpers | Selected Portfolio Dashboard | Main workflow registry | Keep. final decision과 compact packet / gate snapshot만 저장한다. |

## Optional / Explicit Storage

| File | Writer | Reader / Consumer | Classification | Policy |
|---|---|---|---|---|
| `SELECTED_PORTFOLIO_MONITORING_LOG.jsonl` | `app/runtime/portfolio_selection_v2.py` | Selected Portfolio Dashboard | Optional monitoring log | Keep only for explicit user snapshot. No automatic periodic writes. |
| `SAVED_PORTFOLIO_MIXES.jsonl` | `app/runtime/portfolio_selection_v2.py` | Practical Validation / replay paths | Explicit saved setup | Keep as reusable mix setup, not validation evidence. |
| `SAVED_PORTFOLIOS.jsonl` | `app/runtime/portfolio_store.py` | Compare / saved portfolio replay | Legacy explicit saved setup | Preserve. It rewrites rows on update/delete, so do not expand without a migration task. |

## Legacy Compatibility

| File | Writer | Reader / Consumer | Classification | Policy |
|---|---|---|---|---|
| `CURRENT_CANDIDATE_REGISTRY.jsonl` | `app/runtime/candidate_registry.py`, helper scripts | Candidate Library / legacy compare paths | Legacy compatibility registry | Preserve. Do not make it the main source chain again. |
| `CANDIDATE_REVIEW_NOTES.jsonl` | `app/runtime/candidate_registry.py` | Candidate Review | Legacy review note | Freeze expansion. This is closest to memo-sprawl risk. |
| `PRE_LIVE_CANDIDATE_REGISTRY.jsonl` | `app/runtime/candidate_registry.py`, helper scripts | Candidate Library / legacy pre-live paths | Legacy compatibility registry | Preserve for old flow. New selected route should use V2 decision chain. |
| `PORTFOLIO_PROPOSAL_REGISTRY.jsonl` | `app/runtime/portfolio_proposal.py` | Portfolio Proposal | Legacy proposal draft | Preserve for compatibility. Do not add new main-flow dependency. |
| `PAPER_PORTFOLIO_TRACKING_LEDGER.jsonl` | `app/runtime/paper_portfolio_ledger.py` | Portfolio Proposal / paper tracking | Legacy paper ledger | Preserve. Prefer compact paper observation inside Final Review V2 for the current flow. |
| `FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl` | `app/runtime/final_selection_decisions.py` | Legacy Final Review | Legacy final decision | Preserve as V1 history. V2 dashboard should not depend on it. |

## Local Runtime Artifacts

| File / Folder | Writer | Classification | Policy |
|---|---|---|---|
| `BACKTEST_RUN_HISTORY.jsonl` | `app/runtime/history.py` | Local run history | Useful for replay/debug, but not a product decision source. Usually not staged. |
| `WEB_APP_RUN_HISTORY.jsonl` | `app/jobs/run_history.py` | Local operations history | Useful for ops/debug, but not a product decision source. Usually not staged. |
| `.aiworkspace/note/finance/run_artifacts/*` | `app/jobs/result_artifacts.py` | Generated run artifact | Keep local unless user asks for a report/artifact commit. |
| `.aiworkspace/note/finance/backtest_artifacts/*` | `app/runtime/history.py` | Generated backtest artifact | Keep local unless promoted to a human-readable report. |
| `csv/*_failures.csv` | `app/jobs/result_artifacts.py` | Generated failure CSV | Keep local unless explicitly requested. |

## DB-Only Evidence

| Data | Storage Boundary | Reason |
|---|---|---|
| Full provider raw response | DB / ingestion artifact, not workflow JSONL | JSONL registry should not become a raw data warehouse. |
| Full ETF holdings rows | `finance_meta.etf_holdings_snapshot` through ingestion / loader | Look-through evidence needs structured query, freshness, and coverage metadata. |
| ETF exposure snapshots | `finance_meta.etf_exposure_snapshot` through ingestion / loader | Final Review needs compact summary, not full row dumps. |
| Macro time series | `finance_meta.macro_series_observation` through ingestion / loader | Practical Validation should read market context from DB. |
| Price / factor history | `finance_price` / `finance_fundamental` DB groups | Backtest reproducibility depends on source-aware stored data. |

## Immediate Findings

- Main V2 chain is already small enough to keep.
- Most storage sprawl risk now sits in legacy candidate/proposal/paper helpers and saved portfolio compatibility.
- `SAVED_PORTFOLIOS.jsonl` is not append-only because update/delete rewrite the file; treat it as a compatibility exception.
- Run history and run artifacts are useful but should not be used as investability evidence.
- The next implementation should be `data-provenance-coverage-v1`, not another JSONL registry.
