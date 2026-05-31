# Phase 13 Storage / Data Boundary Audit V1

Status: Complete
Created: 2026-05-30

## Summary

Audit result: `QA_PASS`

Phase 13 13-3 found no storage boundary drift that requires an immediate code change.
The current codebase still separates DB-backed evidence, workflow JSONL compact evidence, saved reusable setup, generated run artifacts, and read-only selected monitoring surfaces.

## Boundary Matrix

| Surface | Current owner | Allowed role | Audit result |
| --- | --- | --- | --- |
| DB-backed lifecycle / survivorship evidence | `finance/data/sec_delisting.py`, `finance/data/symbol_directory.py`, `finance/data/sec_company_tickers.py`, `finance/data/computed_lifecycle.py` | Persist structured evidence to `finance_meta.nyse_symbol_lifecycle` | Pass. Collectors report `db_write: True`, `registry_write: False`, and tests assert no JSONL / memo / preset side effects. |
| ETF provider / macro ingestion | `finance/data/etf_provider.py`, `finance/data/macro.py`, ingestion jobs / loaders | Persist or read provider / macro evidence through DB / loader paths | Pass. Practical Validation uses ingestion jobs and DB loaders rather than UI direct provider fetch as the canonical path. |
| Portfolio selection source registry | `app/runtime/portfolio_selection_v2.py` | Compact source handoff into Practical Validation | Pass. `PORTFOLIO_SELECTION_SOURCES.jsonl` is workflow handoff evidence, not user memo storage. |
| Practical Validation result registry | `app/runtime/portfolio_selection_v2.py`, `app/services/backtest_practical_validation.py` | Compact validation result for Final Review handoff | Pass. `PRACTICAL_VALIDATION_RESULTS.jsonl` persists structured validation evidence and explicitly avoids final operator memo semantics. |
| Final Review V2 decision registry | `app/runtime/portfolio_selection_v2.py`, `app/web/backtest_final_review.py` | Compact final decision packet and selected dashboard source | Pass. It is decision evidence, not live approval / broker order / auto rebalance. |
| Selected portfolio monitoring log | `app/runtime/portfolio_selection_v2.py` | Explicit selected monitoring snapshot only | Pass with boundary note. Runtime defines `SELECTED_PORTFOLIO_MONITORING_LOG.jsonl`, but Selected Dashboard read models assert `monitoring_log_auto_write: False`; no automatic append path was found in Phase 13 audit. |
| Saved portfolio setup | `app/runtime/portfolio_store.py`, `app/runtime/portfolio_selection_v2.py` | Reusable setup selected by user | Pass with boundary note. `SAVED_PORTFOLIOS.jsonl` and runtime-defined `SAVED_PORTFOLIO_MIXES.jsonl` are setup storage, not validation, approval, or monitoring evidence. |
| Legacy workflow registries | `app/runtime/candidate_registry.py`, legacy runtime modules | Compatibility / existing workflow state | Pass with caution. Legacy files remain preserved; Phase 13 did not assign them new responsibilities or add new memo / preset storage. |
| Backtest run history and dynamic universe artifacts | `app/runtime/history.py` | Local run history and generated artifact for replay / debugging | Pass. These are generated / local artifacts and were not modified by this task. |
| Web app run history | `app/jobs/run_history.py` | Local ingestion / job execution history | Pass. This remains run history rather than validation evidence or user memo. |
| Reports | `.aiworkspace/note/finance/reports/backtests/` | Human-readable reports | Pass. Reports remain separate from DB / registry source-of-truth. |
| Playwright output | `.playwright-mcp/` | Local browser verification output | Pass. Existing generated output was not modified by this task. |
| Selected Dashboard read models | `app/runtime/final_selected_portfolios.py` | Read-only continuity / recheck / provider / signal / dossier evidence | Pass. Service contracts assert no DB write, registry write, monitoring log auto-write, live approval, order instruction, or auto rebalance for these surfaces. |

## Local Artifact Check

The local artifact check found no task-created changes under:

- `.aiworkspace/note/finance/registries/`
- `.aiworkspace/note/finance/saved/`
- `.aiworkspace/note/finance/run_history/`
- `.aiworkspace/note/finance/run_artifacts/`
- `.playwright-mcp/`

Only the pre-existing `finance/.DS_Store` working tree change remained outside this task and was left untouched.

## Notes

- Some V2 registry paths are runtime-defined and may not exist locally until the first write. That absence is not drift.
- `CANDIDATE_REVIEW_NOTES.jsonl` is a legacy registry, not a new Phase 13 storage expansion.
- `run_history/*.jsonl`, `run_artifacts/`, and `.playwright-mcp/` should stay uncommitted unless a user explicitly asks to preserve generated output.
- 13-4 should align docs / runbooks so future readers understand runtime-defined JSONL paths versus present local files.

## Follow-Up

Next task: `phase13-docs-runbook-alignment-v1`

Recommended focus:

- make docs / runbooks point to the 13-1 inventory, 13-2 QA matrix, and this storage audit;
- clarify DB-backed evidence versus workflow JSONL compact evidence in durable docs;
- keep residual broker-grade and production operations items for 13-5 rather than marking them complete.
