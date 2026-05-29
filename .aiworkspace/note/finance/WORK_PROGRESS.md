# Finance Work Progress

## Purpose
This file is the current, concise implementation log for `finance` package work.

Keep here:
- current active workstream
- recent major milestones
- durable handoff notes

Detailed historical logs were archived on `2026-04-13`.

## Active Pointers

- current phase board:
  - [PHASE34_CURRENT_CHAPTER_TODO.md](/Users/taeho/Project/quant-data-pipeline/.aiworkspace/note/finance/phases/phase34/PHASE34_CURRENT_CHAPTER_TODO.md)
- current candidate summary:
  - [CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md](/Users/taeho/Project/quant-data-pipeline/.aiworkspace/note/finance/backtest_reports/strategies/CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md)
- historical full archive:
  - [WORK_PROGRESS_ARCHIVE_20260413.md](/Users/taeho/Project/quant-data-pipeline/.aiworkspace/note/finance/archive/WORK_PROGRESS_ARCHIVE_20260413.md)

## Entries

### 2026-05-28
- Completed `.aiworkspace/note/finance/tasks/active/overview-mi-market-movers-ops-hardening/`.
- Added Market Movers daily snapshot coverage %, richer refresh-state fields, and DB-only status auto-check for SP500 / TOP1000 / TOP2000.
- Moved the Market Movers refresh bar into the timed DB reload fragment so stale / due guidance can update without automatic provider collection.
- Completed `.aiworkspace/note/finance/tasks/active/overview-mi-events-calendar-ux/`.
- Added Events `Days Until`, `Importance`, and `Focus` read-model fields, plus Focus / Calendar / Table tabs with an Importance filter.
- Events calendar now stacks counts by event type so FOMC, Macro, and Earnings rows are distinguishable at a glance.
- Completed `.aiworkspace/note/finance/tasks/active/overview-mi-earnings-quality-hardening/`.
- Added earnings symbol diagnostics for missing / outside-window / provider-error cases, surfaced diagnostics in Ingestion and Overview refresh results, and added Events `Quality Action` read-model guidance.
- Completed `.aiworkspace/note/finance/tasks/active/overview-mi-bls-ics-import/`.
- Added official BLS `.ics` file import fallback for Macro Calendar so CPI / PPI / Employment Situation rows can be stored when backend BLS requests return HTTP 403.
- Ingestion Macro tab now exposes `.ics` upload/import; Data Health treats `import_bls_macro_calendar_ics` as a Macro Calendar refresh path.
- Completed 4차 production UX for `.aiworkspace/note/finance/phases/active/overview-market-intelligence-productionization/`.
- Added Market Movers Rank / Sector Pulse tabs, Sector / Industry Heatmap / Table tabs, and Events Calendar / Table views with window/source/validation filters.
- Updated runbook, phase acceptance notes, roadmap, and task handoff docs. Remaining future candidates are macro calendar sources, official earnings IR parsing, and scheduled refresh automation.
- Opened `.aiworkspace/note/finance/phases/active/overview-market-intelligence-productionization/`.
- Recommended formalization path: 1차 prototype complete, 2차 production baseline, 3차 earnings/events production, 4차 UX/automation polish.
- Next implementation task is `Task 2-01 Refresh State And Diagnostics Baseline`.
- Completed phase closeout under `.aiworkspace/note/finance/tasks/active/overview-market-intelligence-closeout/`.
- Added `.aiworkspace/note/finance/docs/runbooks/OVERVIEW_MARKET_INTELLIGENCE.md` for Market Movers, FOMC, and earnings prototype refresh operations.
- Updated phase plan/design/integration wording so Events is no longer described as a placeholder; closeout QA passed.
- Completed Task 6 under `.aiworkspace/note/finance/tasks/active/overview-earnings-prototype/`.
- Added bounded yfinance earnings calendar collection into `market_event_calendar` as `EARNINGS`, wired Ingestion prototype controls and Overview Events filter/refresh.
- Local smoke wrote 3 earnings rows for `AAPL`, `MSFT`, `NVDA`; service contract tests passed.
- Completed Task 5 under `.aiworkspace/note/finance/tasks/active/overview-fomc-collector/`.
- Added Fed official FOMC calendar collection into `finance.data.market_intelligence`, wrapped it as `collect_fomc_calendar`, and wired Ingestion / Overview Events to `market_event_calendar`.
- Local smoke wrote 16 FOMC rows for 2026/2027; service contract tests passed.
- Next overview-market-intelligence item is production hardening / UX follow-up for Events or broader event sources.

### 2026-05-27
- Completed Task 7-04 under `.aiworkspace/note/finance/tasks/active/practical-validation-diagnostics-split/`.
- Moved `source_components_dataframe` into `app/services/backtest_practical_validation_source.py` and pinned diagnostics compatibility exports with `__all__`.
- Task 7 `practical-validation-diagnostics-split` is complete; next cleanup slice is Task 8 runtime wrapper cleanup.
- Completed Task 7-03 under `.aiworkspace/note/finance/tasks/active/practical-validation-diagnostics-split/`.
- Added `app/services/backtest_practical_validation_stress_sensitivity.py` for rolling validation, stress windows, baseline challenge, sensitivity interpretation, correlation risk, market context, and overfit audit helpers.
- Diagnostics service now focuses more on component context assembly and the 12 diagnostic result orchestration.
- Followed by Task 7-04 orchestration import / public contract cleanup.
- Completed Task 7-02 under `.aiworkspace/note/finance/tasks/active/practical-validation-diagnostics-split/`.
- Added `app/services/backtest_practical_validation_curve_context.py` for compact curve snapshots, curve normalize, DB price proxy, component curve combination, and monthly/window helpers.
- Compare and Candidate Review now import compact curve snapshot helpers directly from the curve context service helper.
- Followed by Task 7-03 stress / sensitivity helper extraction.
- Completed Task 7-01 under `.aiworkspace/note/finance/tasks/active/practical-validation-diagnostics-split/`.
- Added `app/services/backtest_practical_validation_source.py` for validation profile and Clean V2 selection source builders.
- Diagnostics service remains the public compatibility surface, while direct Compare / Candidate Review / Practical Validation service imports now use the source helper module.
- Followed by Task 7-02 curve context helper extraction.
- Completed `.aiworkspace/note/finance/tasks/active/practical-validation-helper-boundary/`.
- Moved Practical Validation curve helper to `app/services/backtest_practical_validation_curve.py`.
- Moved provider context adapter to `app/services/backtest_practical_validation_provider_context.py`.
- Boundary lint now reports no `app.services/app.runtime -> app.web` advisories; next cleanup task is diagnostics service split.
- Opened `.aiworkspace/note/finance/phases/active/ui-engine-boundary-cleanup/`.
- Completed Task 0 audit at `.aiworkspace/note/finance/tasks/active/ui-engine-boundary-cleanup-audit/`.
- Task 0 originally found 3 Practical Validation helper advisories; Task 6 resolved them.
- Next task is `7. practical-validation-diagnostics-split`.

### 2026-05-20
- Completed `.aiworkspace/note/finance/tasks/active/runtime-package-boundary/`.
- `5-01`: moved `app/web/runtime` to `app/runtime` and updated repo imports to `app.runtime`.
- `5-02`: moved Candidate Library replay helper to `app/runtime/candidate_library.py`.
- Boundary lint now scans both `app/services` and `app/runtime`; remaining advisories are Practical Validation web helper dependencies.
- Completed `.aiworkspace/note/finance/tasks/active/practical-validation-diagnostics-service-boundary/`.
- Moved the large Practical Validation diagnostic builder from `app/web` to `app/services/backtest_practical_validation_diagnostics.py`.
- Practical Validation service, Compare, and Candidate Review now import diagnostic/source/compact curve helpers from the service boundary.
- Added diagnostics service contract coverage to `tests/test_service_contracts.py`.
- Added `.aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py` as a repo-local UI-engine boundary lint helper.
- The helper hard-fails on Streamlit usage in `app/services` / `app/runtime` and staged generated / registry / saved artifacts, while reporting current `app.services/app.runtime -> app.web` imports as advisory transition debt.
- Completed `.aiworkspace/note/finance/tasks/active/evidence-read-model-boundary/`.
- Added `app/services/backtest_evidence_read_model.py` so Final Review saved decision rows and Selected Dashboard evidence rows share a Streamlit-free read model.
- `ui-engine-boundary-foundation` implementation slices are now complete; next decision is phase closeout QA or a follow-up boundary phase.
- Completed `.aiworkspace/note/finance/tasks/active/practical-validation-service-boundary/`.
- Added `app/services/backtest_practical_validation.py` as the Streamlit-free Practical Validation source/result append and handoff contract boundary.
- `app/web/backtest_practical_validation_helpers.py` no longer imports Streamlit; UI modules apply service handoff contracts to session state.
- Next implementation slice in the phase: `evidence-read-model-boundary`.

### 2026-05-19
- Opened the active phase `.aiworkspace/note/finance/phases/active/ui-engine-boundary-foundation/`.
- Created the first audit task at `.aiworkspace/note/finance/tasks/active/ui-engine-boundary-audit/`.
- Durable direction: keep Streamlit for now and introduce `app/services` as the UI-engine boundary.
- Completed the first implementation task `.aiworkspace/note/finance/tasks/active/backtest-execution-service-boundary/` by moving Single Backtest dispatch / error normalization to `app/services/backtest_execution.py`.
- Started `.aiworkspace/note/finance/tasks/active/compare-service-boundary/` and moved manual compare execution loop / error normalization to `app/services/backtest_compare_execution.py`.
- Moved the compare strategy runner catalog / defaults to `app/services/backtest_compare_catalog.py`; UI now injects current preset dictionaries as `ComparePresetCatalog`.
- Moved weighted portfolio bundle construction to `app/services/backtest_weighted_portfolio.py` and data-only result helper logic to `app/services/backtest_result_read_model.py`.
- Moved saved portfolio replay execution / data assembly to `app/services/backtest_saved_portfolio_replay.py`; UI keeps session state, history append, notices, and render side effects.
- Next implementation slice: start `practical-validation-service-boundary`.

### 2026-05-13
- Renamed the product direction research workspace from `.aiworkspace/note/finance/research/` to `.aiworkspace/note/finance/researches/`.
- Updated AGENTS, durable docs, active task notes, and product research skills to use `researches/active/<research-id>/`.
- Synced the global finance skill mirrors after the path rename.

### 2026-05-13
- Set `.aiworkspace/note/finance/researches/` as the canonical workspace for product direction research output.
- Added `researches/README.md` plus `active/` and `done/` folders for audit, benchmark, feature candidate, recommendation, source, and risk notes.
- Updated AGENTS, docs index/project map/roadmap, and the product research skills so actual research outputs go to `researches/active/<research-id>/`.
- `tasks/active/` remains for execution records such as skill/workflow changes.

### 2026-05-13
- Completed Product Research Skill Stage 1 for future finance roadmap research.
- Added the active task at `.aiworkspace/note/finance/tasks/active/product-research-skill-stage1/`.
- New validated stage-1 skills are `finance-product-audit`, `finance-benchmark-research`, and `finance-feature-opportunity`.
- The intent is to validate the research workflow before later packaging a dedicated product-research plugin.

### 2026-05-13
- Renamed finance worktrees / branches to the new role names:
  - `candidate-search` -> `research` / `codex/research`
  - `phase` -> `main-dev` / `codex/main-dev`
  - `ux-ui-polishing` -> `sub-dev` / `codex/sub-dev`
- Updated active workspace guidance and skill-system notes so future routing uses `main-dev`, `research`, and `sub-dev`.

### 2026-05-13
- Migrated legacy `code_analysis/` into the new document system.
- Moved current-state developer flow docs into:
  - `.aiworkspace/note/finance/docs/architecture/`
  - `.aiworkspace/note/finance/docs/flows/`
  - `.aiworkspace/note/finance/docs/runbooks/`
- Moved Practical Validation V2 planning docs into `.aiworkspace/note/finance/tasks/active/practical-validation-v2/`.
- Rewrote the old portfolio selection redesign guide as the current-state `PORTFOLIO_SELECTION_FLOW.md`.
- Removed the old `.aiworkspace/note/finance/code_analysis/` folder and updated active references to the new paths.

### 2026-05-11
- Updated finance document-writing guidance for future phase / planning documents.
- Updated:
  - `AGENTS.md`
  - `.aiworkspace/note/finance/PHASE_PLAN_TEMPLATE.md`
  - `.aiworkspace/note/finance/docs/runbooks/AUTOMATION_SCRIPTS.md`
  - `.aiworkspace/plugins/quant-finance-workflow/scripts/bootstrap_finance_phase_bundle.py`
  - local finance phase/doc-sync skill guidance
- Durable decision:
  - New or substantially rewritten plan documents should use `이걸 하는 이유?` as the plain-language purpose/value section.
  - Separate plain-summary and end-benefit sections are no longer required.

### 2026-05-11
- Updated Practical Validation V2 P2 provider connector planning after source / ingestion direction review.
- Updated:
  - `.aiworkspace/note/finance/tasks/active/practical-validation-v2/PROVIDER_CONNECTORS.md`
  - `.aiworkspace/note/finance/tasks/active/practical-validation-v2/CONNECTOR_AND_STRESS_PLAN.md`
- Durable decision:
  - P2 development starts with provider data collection through `finance/data/*` ingestion and MySQL persistence.
  - Practical Validation / Dashboard must read provider data through loaders, not remote-fetch from the UI.
  - Official issuer / FRED sources are preferred; `yfinance`, `nyse_asset_profile`, and price-history ADV remain bridge / fallback evidence.

### 2026-05-11
- Reframed Practical Validation V2 P2 around diagnostic normalization rather than provider collection as the end goal.
- Updated:
  - `.aiworkspace/note/finance/tasks/active/practical-validation-v2/IMPLEMENTATION_PLAN.md`
  - `.aiworkspace/note/finance/tasks/active/practical-validation-v2/CONNECTOR_AND_STRESS_PLAN.md`
  - `.aiworkspace/note/finance/tasks/active/practical-validation-v2/PROVIDER_CONNECTORS.md`
- Durable decision:
  - P2 means normalizing the incomplete Practical Validation diagnostics among the 12 patterns.
  - Provider / holdings / macro ingestion is the implementation method, not the product goal.
  - P2 target diagnostics are primarily 2, 3, 5, 6, 7, 9, 10, and 11.

### 2026-05-11
- Completed Practical Validation V2 P2-0 target diagnostic contract.
- Updated:
  - `.aiworkspace/note/finance/tasks/active/practical-validation-v2/CONNECTOR_AND_STRESS_PLAN.md`
  - `.aiworkspace/note/finance/tasks/active/practical-validation-v2/PROVIDER_CONNECTORS.md`
  - `.aiworkspace/note/finance/tasks/active/practical-validation-v2/IMPLEMENTATION_PLAN.md`
- Durable decision:
  - P2-0 fixed the target diagnostics as 2, 3, 5, 6, 7, 9, 10, and 11.
  - Each target diagnostic now has an actual-data requirement, bridge/proxy fallback, `NOT_RUN` / `REVIEW` condition, and compact evidence boundary.
  - Next work is P2-1: schema / ingestion field contract based on the P2-0 diagnostic contract.

### 2026-05-10
- Clarified `NOT_RUN` handling for Final Review route in Practical Validation docs.
- Updated:
  - `.aiworkspace/note/finance/researches/PRACTICAL_VALIDATION_INVESTMENT_DIAGNOSTICS_RESEARCH.md`
  - `.aiworkspace/note/finance/tasks/active/practical-validation-v2/DESIGN.md`
  - `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Durable decision:
  - `NOT_RUN` is not a pass. It means the diagnostic was not executed because data or implementation is missing.
  - Final Review can still receive candidates with some `NOT_RUN` domains, but critical `NOT_RUN` domains must be explicitly acknowledged.
  - Missing core prices or similarly dangerous gaps should be treated as `BLOCKED`, not soft `NOT_RUN`.

### 2026-05-10
- Clarified proxy classification and holdings look-through wording in Practical Validation design docs.
- Updated:
  - `.aiworkspace/note/finance/researches/PRACTICAL_VALIDATION_INVESTMENT_DIAGNOSTICS_RESEARCH.md`
  - `.aiworkspace/note/finance/tasks/active/practical-validation-v2/DESIGN.md`
  - `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Durable decision:
  - Proxy classification means using ticker-level category proxies when holdings data is unavailable.
  - Holdings look-through means checking ETF internal constituents and top holding overlap.
  - Missing holdings coverage should be shown as `NOT_RUN`, not as pass.

### 2026-05-10
- Changed Practical Validation design-question status tables to a single checklist table.
- Updated:
  - `.aiworkspace/note/finance/researches/PRACTICAL_VALIDATION_INVESTMENT_DIAGNOSTICS_RESEARCH.md`
  - `.aiworkspace/note/finance/tasks/active/practical-validation-v2/DESIGN.md`
  - `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Durable decision:
  - Use one table with `확인 여부`, `질문`, and `결정 / 기본 방향` columns instead of splitting design questions into completed and remaining sections.
  - Mark confirmed items as `O` and implementation-time choices as `X`.

### 2026-05-10
- Refreshed Practical Validation open design questions.
- Updated:
  - `.aiworkspace/note/finance/researches/PRACTICAL_VALIDATION_INVESTMENT_DIAGNOSTICS_RESEARCH.md`
  - `.aiworkspace/note/finance/tasks/active/practical-validation-v2/DESIGN.md`
  - `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Durable decision:
  - Practical Validation design questions are now split into `결정 완료` and `남은 구현 선택`.
  - Remaining implementation choices are rolling window defaults, cost assumptions, baseline proxy set, sensitivity perturbation grid, stress window defaults, and future sentiment connector timing.

### 2026-05-10
- Finalized Korean-facing Validation Profile wording for Practical Validation design.
- Updated:
  - `.aiworkspace/note/finance/researches/PRACTICAL_VALIDATION_INVESTMENT_DIAGNOSTICS_RESEARCH.md`
  - `.aiworkspace/note/finance/tasks/active/practical-validation-v2/DESIGN.md`
  - `.aiworkspace/note/finance/FINANCE_TERM_GLOSSARY.md`
  - `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Durable decision:
  - User-facing profile labels should be Korean: 방어형, 균형형, 성장형, 전술 / 헤지형, 사용자 지정.
  - Internal ids remain English for code / JSON stability.
  - The 5 profile questions are portfolio purpose, tolerated drawdown, expected holding period, product / complexity allowance, and desired improvement versus simple alternatives.
  - Invariant hard blockers mean validation failures that cannot be waived by an aggressive profile.

### 2026-05-10
- Clarified Practical Validation terminology and future sentiment connector scope.
- Updated:
  - `.aiworkspace/note/finance/researches/PRACTICAL_VALIDATION_INVESTMENT_DIAGNOSTICS_RESEARCH.md`
  - `.aiworkspace/note/finance/tasks/active/practical-validation-v2/DESIGN.md`
  - `.aiworkspace/note/finance/FINANCE_TERM_GLOSSARY.md`
  - `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Durable decision:
  - Sentiment Overlay remains a required future Practical Validation module, but the first implementation can keep it as `NOT_RUN` / future connector until the core validation flow is stable.
  - Future sentiment work should start with FRED-based VIX / Credit Spread / Yield Curve snapshots and keep Fear & Greed optional.
  - Asset Allocation Profile means the expected asset exposure character used to interpret equity, bond, cash, gold, commodity, inverse, and leveraged allocation fit.

### 2026-05-10
- Refined the Practical Validation diagnostics design with Validation Profile behavior.
- Updated:
  - `.aiworkspace/note/finance/researches/PRACTICAL_VALIDATION_INVESTMENT_DIAGNOSTICS_RESEARCH.md`
  - `.aiworkspace/note/finance/tasks/active/practical-validation-v2/DESIGN.md`
  - `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Durable decision:
  - Practical Validation should ask 3~5 questions to create a Validation Profile, then use that profile to adjust thresholds, domain weights, blocker / review interpretation, and user-intent mismatch warnings.
  - The profile should not skip diagnostic domains. Available domains should still be attempted, while invariant hard blockers such as Data Trust failure, weight total error, missing core prices, execution boundary violations, and large leveraged / inverse mismatch remain strict.
- Current status:
  - Product code was not changed. This is a document-only design refinement before implementation.

### 2026-05-10
- Documented the Practical Validation investment diagnostics direction.
- Created:
  - `.aiworkspace/note/finance/researches/PRACTICAL_VALIDATION_INVESTMENT_DIAGNOSTICS_RESEARCH.md`
- Updated:
  - `.aiworkspace/note/finance/tasks/active/practical-validation-v2/DESIGN.md`
  - `.aiworkspace/note/finance/researches/README.md`
  - `.aiworkspace/note/finance/FINANCE_DOC_INDEX.md`
  - `.aiworkspace/note/finance/docs/architecture/README.md`
  - `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Durable decision:
  - Practical Validation should not be only an upstream evidence summary. It should use upstream evidence as input, then run portfolio-level practical diagnostics such as asset allocation fit, concentration / overlap, correlation / risk contribution, macro / sentiment context, stress / scenario, alternative portfolio challenge, leveraged / inverse suitability, ETF operability, and robustness / overfit review.
- Current status:
  - Product code was not changed. This is a research and development guide update for the next implementation unit.

### 2026-05-03
- Opened Phase 34 `Final Portfolio Selection Decision Pack`.
- Created:
  - `.aiworkspace/note/finance/phases/phase34/PHASE34_FINAL_PORTFOLIO_SELECTION_DECISION_PACK_PLAN.md`
  - `.aiworkspace/note/finance/phases/phase34/PHASE34_CURRENT_CHAPTER_TODO.md`
  - `.aiworkspace/note/finance/phases/phase34/PHASE34_FINAL_DECISION_CONTRACT_FIRST_WORK_UNIT.md`
  - `.aiworkspace/note/finance/phases/phase34/PHASE34_TEST_CHECKLIST.md`
  - `.aiworkspace/note/finance/phases/phase34/PHASE34_COMPLETION_SUMMARY.md`
  - `.aiworkspace/note/finance/phases/phase34/PHASE34_NEXT_PHASE_PREPARATION.md`
- Synced:
  - roadmap, document index, work log, question log, and comprehensive analysis current-state references
- Current status:
  - Phase 34 is `active` / `not_ready_for_qa`
  - first work unit, final decision contract and storage boundary, is completed
  - next work unit is decision evidence pack calculation criteria
- Durable takeaway:
  - Phase 34 is not live approval or order execution. It will read Phase 33 paper ledger records and create a final selection / hold / reject / re-review decision pack.

### 2026-05-03
- Closed Phase 33 after the user confirmed the checklist was complete.
- Updated:
  - marked Phase 33 as `complete` / `manual_qa_completed`
  - preserved the user's checked `PHASE33_TEST_CHECKLIST.md`
  - synced Phase33 TODO, completion summary, next-phase preparation, roadmap, doc index, comprehensive analysis, work log, and question log
- Durable takeaway:
  - Phase 33 is closed. Phase 34 can start as the Final Portfolio Selection Decision Pack phase, reading the saved Paper Portfolio Tracking Ledger but still staying separate from live approval or order execution.

### 2026-05-03
- Completed Phase 33 implementation units 1~4 and moved the phase to manual QA handoff.
- Implemented:
  - `app/web/runtime/paper_portfolio_ledger.py` append / load helper for `.aiworkspace/note/finance/registries/PAPER_PORTFOLIO_TRACKING_LEDGER.jsonl`
  - `Backtest > Portfolio Proposal` Paper Tracking Ledger Draft / Save controls under Validation Pack
  - saved Paper Tracking Ledger review surface with source, target weights, benchmark, cadence, triggers, raw JSON
  - Phase34 handoff route calculation for saved ledger records
- Synced:
  - Phase33 TODO, checklist, completion summary, next-phase preparation, work-unit docs
  - README, AGENTS, script map, Backtest UI flow, operations guide, glossary, roadmap, doc index, comprehensive analysis
- Validation:
  - focused py_compile passed
  - paper ledger helper smoke passed
- Current status:
  - Phase 33 is `implementation_complete` / `manual_qa_pending`
  - user manual QA should use `PHASE33_TEST_CHECKLIST.md`
- Durable takeaway:
  - Phase 33 creates an explicit paper tracking ledger record, but it is still not paper PnL automation, final selection, live approval, or order execution.

### 2026-05-03
- Closed Phase 32 after the user confirmed the checklist was complete.
- Updated:
  - marked Phase 32 as `complete` / `manual_qa_completed`
  - synced Phase 32 TODO, checklist, completion summary, next-phase preparation, roadmap, doc index, work log, question log, README, and comprehensive analysis
  - kept the Phase 32 Robustness / Stress surface as read-only validation and handoff, not proposal save, paper ledger save, live approval, or final selection
- Durable takeaway:
  - Phase 32 is closed, and Phase 33 can begin as the paper tracking ledger phase.

### 2026-05-03
- Opened Phase 33 `Paper Portfolio Tracking Ledger`.
- Created:
  - `.aiworkspace/note/finance/phases/phase33/PHASE33_PAPER_PORTFOLIO_TRACKING_LEDGER_PLAN.md`
  - `.aiworkspace/note/finance/phases/phase33/PHASE33_CURRENT_CHAPTER_TODO.md`
  - `.aiworkspace/note/finance/phases/phase33/PHASE33_LEDGER_CONTRACT_FIRST_WORK_UNIT.md`
  - `.aiworkspace/note/finance/phases/phase33/PHASE33_TEST_CHECKLIST.md`
  - `.aiworkspace/note/finance/phases/phase33/PHASE33_COMPLETION_SUMMARY.md`
  - `.aiworkspace/note/finance/phases/phase33/PHASE33_NEXT_PHASE_PREPARATION.md`
- Synced:
  - roadmap, document index, work log, question log, and comprehensive analysis current-state references
- Current status:
  - Phase 33 is `active` / `not_ready_for_qa`
  - first work unit is paper ledger row contract and storage boundary
- Durable takeaway:
  - Phase 33 is not final selection or live approval. It starts the append-only paper tracking ledger needed before Phase 34 final selection decision work.

### 2026-04-20
- Reorganized section 3 of `FINANCE_COMPREHENSIVE_ANALYSIS.md` so current architecture and phase history are separated.
- Changed:
  - renamed section 3 to `현재 시스템 구조와 phase별 구현 히스토리`
  - added `3-1. 현재 시스템 구조` as the current architecture reading path
  - added `3-2. Phase별 구현 히스토리` as a grouped phase timeline from Phase 1~25
  - moved the previous mixed chronological narrative under `3-3. 상세 구현 메모`
  - changed the old `Phase 14 Practical Closeout` UI status sentence to read as a historical note rather than current state
- Durable takeaway:
  - The comprehensive analysis now keeps deep implementation notes but no longer asks users to read mixed phase history as the current architecture explanation.

### 2026-04-20
- Added a user-facing entry layer to `FINANCE_COMPREHENSIVE_ANALYSIS.md` without removing the deep technical context.
- Changed:
  - clarified the document's three roles: readable system map, agent deep reference, and durable implementation context
  - added a quick reading guide by purpose
  - added a one-page current system summary across data collection, persistence, loader/runtime, strategy engine, web UI, and review/pre-live layers
  - added reading rules so older implementation notes are preserved as history while current state is checked against roadmap/work logs
- Durable takeaway:
  - `FINANCE_COMPREHENSIVE_ANALYSIS.md` remains the deep system reference, but it now has a clearer human-readable entry point.

### 2026-04-20
- Refined the `FINANCE_DOC_INDEX.md` earlier-phase section after user feedback.
- Changed:
  - replaced the single long `Earlier Phase Detail` table with one subsection per phase for Phase 1~18
  - added managed documents where relevant, including plan, TODO, work unit, checklist, completion, next-phase prep, decisions, gates, and validation notes
  - kept the scope controlled by listing representative managed documents instead of every historical file
- Durable takeaway:
  - Both recent and earlier phases are now navigable by phase, while the index still avoids becoming a full archive dump.

### 2026-04-20
- Reorganized `FINANCE_DOC_INDEX.md` as a navigation-first finance document map.
- Changed:
  - reduced the index from a long explanatory list into a shorter phase-oriented guide
  - added a "지금 먼저 볼 문서" section for Phase 25 active work
  - split top-level docs, operating files, backtest reports, recent phases, earlier phases, support track, data/runtime references, research references, and archives
  - moved detailed backtest result lookup guidance toward `backtest_reports/BACKTEST_REPORT_INDEX.md`
- Durable takeaway:
  - `FINANCE_DOC_INDEX.md` should now act as a document map, not another long explanation document.

### 2026-04-20
- Closed `Phase 24` and opened `Phase 25`.
- Changed:
  - accepted the completed `PHASE24_TEST_CHECKLIST.md` manual QA state
  - marked `PHASE24_CURRENT_CHAPTER_TODO.md`, `PHASE24_COMPLETION_SUMMARY.md`, and `PHASE24_NEXT_PHASE_PREPARATION.md` as Phase 24 closeout / Phase 25 handoff documents
  - bootstrapped the Phase 25 document bundle
  - rewrote the Phase 25 plan, TODO, checklist, completion draft, next-phase draft, and first work-unit note around `Pre-Live Operating System And Deployment Readiness`
  - fixed the Phase 25 boundary as `Real-Money 검증 신호 = per-run diagnostic signal` and `Pre-Live 운영 점검 = paper / watchlist / hold / re-review operating process`
  - synced `MASTER_PHASE_ROADMAP.md`, `FINANCE_DOC_INDEX.md`, and durable analysis logs
- Durable takeaway:
  - Phase 24 is closed as a completed new-strategy implementation bridge, and Phase 25 is now active as a pre-live operating-system development phase, not a live trading or investment approval phase.

### 2026-04-20
- Clarified the Phase 25 boundary between existing Real-Money validation and future pre-live operation workflow.
- Decision:
  - `Real-Money 검증 신호` = per-backtest diagnostic surface for transaction cost, benchmark, drawdown, liquidity, ETF operability, promotion status
  - `Pre-Live 운영 점검` = Phase 25 workflow for paper tracking, watchlist, hold/review decisions, monitoring notes, and re-collection/re-validation actions
- Updated:
  - `Reference > Guides > 테스트에서 상용화 후보 검토까지 사용하는 흐름`
  - `FINANCE_TERM_GLOSSARY.md`
  - `PHASE24_NEXT_PHASE_PREPARATION.md`
  - `FINANCE_COMPREHENSIVE_ANALYSIS.md`
  - `QUESTION_AND_ANALYSIS_LOG.md`

### 2026-04-20
- Corrected the `Global Relative Strength` malformed price-row handling policy after user QA feedback.
- Decision:
  - do not silently remove or repair a malformed price row to extend the backtest result window
  - keep the conservative common rebalance-date behavior so `IWM`'s `2026-03-17` missing close naturally limits the run to the last clean common rebalance date
  - surface the issue through `malformed_price_rows` metadata and a Korean warning so the operator can inspect or re-collect the source price row
- Validation expectation:
  - the same `2016-01-01 -> 2026-04-20` default run should end at `2026-02-27` until the malformed `IWM` source row is fixed or re-collected
- Documentation hygiene:
  - reviewed index impact; no new durable document was added, so `FINANCE_DOC_INDEX.md` did not need a structural update

### 2026-04-20
- Fixed a follow-up Phase 24 QA issue where `Global Relative Strength` stopped at `2026-02-27` even when the selected end date was `2026-04-20`.
- Root cause:
  - `IWM` had one DB row on `2026-03-17` with empty OHLC values
  - `add_ma` treated that empty `Close` inside the rolling window as invalid and dropped all later MA rows until the rolling window recovered
  - month-end alignment therefore lost March/April common dates and the result stopped at February
- Implemented:
  - `add_ma` now removes rows with missing price values before calculating moving averages
  - Global Relative Strength now records those removed malformed rows in `malformed_price_rows` metadata and result warnings
  - real-money warning strings shown under "이번 실행에서 같이 봐야 할 주의사항" were translated to Korean-oriented copy
- Validation:
  - `.venv` default `Global Relative Strength` runtime smoke for `2016-01-01 -> 2026-04-20` now ends at `2026-04-17`, the latest available DB trading date
  - the same smoke surfaces `IWM 1건(2026-03-17)` as a malformed price-row warning
  - `.venv/bin/python -m py_compile finance/transform.py app/web/runtime/backtest.py finance/sample.py`
- Documentation hygiene:
  - reviewed index impact; no new durable document was added, so `FINANCE_DOC_INDEX.md` did not need a structural update

### 2026-04-20
- Fixed a Phase 24 QA issue in `Global Relative Strength` single-strategy execution.
- Root cause:
  - default preset included `EEM`, but the current DB only had recent `EEM` price rows
  - after `MA200` and 12-month relative-strength warmup, `EEM` became an empty transformed series
  - strict date intersection then failed with `공통 Date가 없습니다.`
- Implemented:
  - DB-backed Global Relative Strength now excludes risky tickers that have insufficient transformed price history
  - excluded tickers are preserved in result metadata as `excluded_tickers`
  - UI/runtime warnings explain that the ticker was excluded and that DB price data should be refreshed before interpreting the result
- Validation:
  - `.venv` default preset runtime smoke now succeeds with `EEM` excluded
  - compact custom universe runtime smoke still succeeds with no excluded tickers
  - `.venv/bin/python -m py_compile finance/sample.py app/web/runtime/backtest.py`

### 2026-04-20
- Continued Phase 24 with the UI / replay integration pass for `Global Relative Strength`.
- Implemented:
  - strategy catalog registration for single and compare strategy selectors
  - `Backtest > Single Strategy` form with universe, cash ticker, top, interval, score horizons, trend filter, and ETF real-money contract inputs
  - `Compare & Portfolio Builder` strategy-specific box and compare runner override support
  - history payload / load-into-form / run-again roundtrip for `cash_ticker`, cadence, score, and trend settings
  - saved portfolio replay override preservation for the new strategy
- Validation:
  - `python3 -m py_compile app/web/backtest_strategy_catalog.py app/web/runtime/backtest.py app/web/runtime/history.py app/web/pages/backtest.py`
  - `.venv` catalog/history smoke
  - `.venv` DB-backed runtime smoke
  - `.venv` compare runner smoke
- Status:
  - Phase 24 is now `practical_closeout / manual_validation_pending`.
  - Next step is user QA via `PHASE24_TEST_CHECKLIST.md`.
- Guidance sync:
  - refreshed `finance-strategy-implementation` skill guidance so future user-facing strategy additions include catalog / single UI / compare / history / saved replay handoff checks.

### 2026-04-19
- Continued Phase 23 implementation with the first quarterly contract parity pass.
- Implemented:
  - quarterly single-strategy UI now shows `Portfolio Handling & Defensive Rules`
  - quarterly payloads now carry weighting, rejected-slot handling, risk-off, and defensive ticker contract values
  - quarterly compare forms now expose the same portfolio handling contract controls
  - quarterly history load-into-form restores the same contract values
  - quarterly runtime wrappers accept and pass these contracts to the DB-backed strict statement shadow execution path
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py app/web/runtime/backtest.py finance/sample.py`
  - `.venv` import/signature smoke for the three quarterly strict prototype runners

### 2026-04-19
- Opened `Phase 23 Quarterly And Alternate Cadence Productionization`.
- Created and rewrote the Phase 23 plan / TODO / checklist / completion / next-phase documents so the phase is clearly framed as product development, not investment analysis.
- Added the first work-unit document:
  - `.aiworkspace/note/finance/phases/phase23/PHASE23_QUARTERLY_PRODUCTIONIZATION_FRAME_FIRST_WORK_UNIT.md`
- Current reading:
  - quarterly strict family already has execution paths
  - Phase 23 will harden UI, payload, compare/history/replay, and representative validation before Phase 24 new strategy expansion

### 2026-04-18
- Started a user-requested GTAA investable portfolio search outside the current presets.
- Used sub-agents for:
  - GTAA runtime / promotion metadata path discovery
  - conservative ETF universe exploration
  - offensive ETF universe exploration
- Re-ran the strongest ideas in the main environment with `.venv/bin/python` and current DB-backed `run_gtaa_backtest_from_db`.
- Result:
  - compact ETF sleeves produced `real_money_candidate` GTAA candidates without relaxing ETF AUM/spread gates
  - broader high-CAGR universes were rejected because current ETF operability/profile coverage pushed them back to `hold`
  - saved the durable report at `.aiworkspace/note/finance/backtest_reports/strategies/GTAA_REAL_MONEY_CANDIDATE_SEARCH_20260418.md`
  - appended the result to the GTAA strategy log and candidate registry

### 2026-04-16
- Split the roadmap tail into two clearer roles:
  - `현재 위치` now behaves like a status board
  - `지금부터의 큰 흐름` now behaves like a next-step guide
- Removed:
  - duplicated reading-order guidance that overlapped between the two sections
- Result:
  - the roadmap reads more like a single coherent document and less like two overlapping summaries

### 2026-04-16
- Reworked the roadmap summary section that used to read as a special `Phase 18~25 Draft Big Picture`.
- Changed it into:
  - `다음 단계 한눈에 보기 (Phase 18 ~ 25)`
  - a quick-reading summary that clearly says it does not replace the actual phase descriptions above
- Result:
  - the roadmap now feels less like it has a second special roadmap embedded inside it
  - `Phase 18 ~ 25` is easier to read as a continuation of the same master roadmap

### 2026-04-16
- Clarified roadmap semantics after user review:
  - `Phase 18` is still in-progress from a backlog perspective
  - `Phase 19` and `Phase 20` are fully manual-validation completed
  - `Phase 5 first chapter` was a historical chapter label, not a hidden active second chapter
  - `support track` remains a parallel tooling lane, not a main finance phase
- Updated the roadmap so these distinctions read more directly.

### 2026-04-16
- Refreshed `MASTER_PHASE_ROADMAP.md` after the user pointed out that the reading order had become awkward.
- Reordered:
  - `Phase 6` and `Phase 16` back into their natural chronological positions
  - `현재 위치` / `Phase 18~25 Draft Big Picture` / `앞으로의 운영 방식` into a cleaner tail structure
- Synced:
  - `Phase 19` status now reads as `phase complete / manual_validation_completed`
  - active pointer now follows `Phase 21` as the next main phase board
- Result:
  - the roadmap now reads as a real phase sequence again instead of a mix of historical notes and later inserts

### 2026-04-16
- Rebased the roadmap after the user pointed out that the old `Phase 21` was not really product work.
- Applied:
  - previous `Research Automation And Experiment Persistence` work is now treated as a support track, not a main finance phase
  - the main roadmap was redesigned so the new `Phase 21` is `Integrated Deep Backtest Validation`
  - new `Phase 21` plan / TODO / checklist / next-phase docs now reflect deep validation instead of agent/plugin setup
- Result:
  - the project phase sequence is back on the product path:
    validation -> portfolio-level construction -> quarterly productionization -> new strategy expansion -> pre-live readiness

### 2026-04-16
- Reviewed Phase 21 QA documents after Phase 20 workflow naming/validation changes.
- Outcome:
  - `PHASE21_TEST_CHECKLIST.md` itself did not need major target changes because it validates scripts, registry, and docs rather than Phase 20 UI buttons
  - added one explicit note so future QA readers know the Phase 20 button rename is not the core Phase 21 test target
  - updated `PHASE21_NEXT_PHASE_PREPARATION.md` so it no longer assumes Phase 20 operator workflow is still the main open question

### 2026-04-16
- User-facing Phase 20 checklist confirmation is now complete.
- Closed:
  - `PHASE20_CURRENT_CHAPTER_TODO.md` -> `phase complete / manual_validation_completed`
  - `PHASE20_COMPLETION_SUMMARY.md` -> reflects checklist completion
  - `PHASE20_CANDIDATE_CONSOLIDATION_AND_OPERATOR_WORKFLOW_HARDENING_PLAN.md` -> status synced to completion
- Meaning:
  - current candidate -> compare -> weighted -> saved -> replay/load-back workflow is now considered closed at the manual validation level

### 2026-04-16
- Phase 20 saved-portfolio QA exposed one real replay bug and one lingering UX gap.
- Fixed:
  - `Replay Saved Portfolio` could fail when stored compare overrides still contained legacy keys such as `factor_freq`
    that the current strict-annual runtime wrappers no longer accept
  - compare replay now filters unsupported kwargs against the current runner signature before execution
- Clarified:
  - `Save This Weighted Portfolio` now explains what `Portfolio Name` and `Description` are for
  - `Portfolio Name` starts from the current source label or strategy combination so the saved name reads less like an empty form
  - the saved-portfolio re-entry button now reads as `Load Saved Setup Into Compare`
    so it feels more like "restore settings" than "edit this record in place"

### 2026-04-15
- Applied a Phase 20 QA-driven UX clarification pass to `Current Candidate Re-entry`.
- Added:
  - clearer explanation that current candidate re-entry fills the compare form rather than running compare immediately
  - clearer explanation for `Load Current Anchors` and `Load Lower-MDD Near Misses`
  - registry-source explanation that the list is curated from `CURRENT_CANDIDATE_REGISTRY.jsonl`, not auto-filled by every run
  - a `What Changed In Compare` summary card that shows selected strategies, period, and key overrides after load

### 2026-04-15
- Fixed a strict-annual shadow sample parity bug found during manual backtest validation.
- Cause:
  - strict annual runtime wrappers started passing `rejected_slot_handling_mode`
    to the shadow DB sample entrypoints,
    but the three shadow helpers in `finance/sample.py`
    still only accepted the older boolean pair.
- Applied the fix to:
  - quality strict annual shadow path
  - value strict annual shadow path
  - quality+value strict annual shadow path
- Result:
  - the shadow sample entrypoints now accept the explicit rejected-slot handling contract
    and normalize it back into legacy flags before execution.

### 2026-04-15
- Continued Phase 20 through practical closeout.
- Added the second operator-workflow hardening unit:
  - compare source context now carries into weighted portfolio and saved portfolio flows
  - `Current Compare Bundle` summary now explains what the current compare run came from
  - saved portfolio actions and detail tabs were renamed/expanded to make next actions clearer
- Synced:
  - Phase 20 closeout docs
  - roadmap / doc index
  - finance analysis
  - current candidate registry guide
- Current reading:
  - Phase 20 is now `practical closeout / manual_validation_pending`
  - main remaining step is the user-facing checklist

### 2026-04-13
- Compressed the root work log into a concise active-context version.
- Moved the previous full log to:
  - `.aiworkspace/note/finance/archive/WORK_PROGRESS_ARCHIVE_20260413.md`
- Added a one-page current-candidate summary and code-flow/operator docs so future backtest refinement work can restart faster.

### 2026-04-13
- Continued Phase 16 as a downside-focused practical refinement track for both `Value` and `Quality + Value`.
- Confirmed `Value` current best practical point still remains:
  - `Top N = 14 + psr`
  - `CAGR = 28.13%`
  - `MDD = -24.55%`
  - `real_money_candidate / paper_probation / review_required`
- Confirmed the most useful lower-MDD `Value` near-miss:
  - `+ pfcr`
  - `CAGR = 27.22%`
  - `MDD = -21.16%`
  - but `production_candidate / watchlist`

### 2026-04-13
- Confirmed new `Quality + Value` current strongest practical point:
  - `net_margin -> operating_margin`
  - `ocf_yield -> pcr`
  - `operating_income_yield -> por`
  - `Top N = 10`
  - `Candidate Universe Equal-Weight`
  - `CAGR = 31.82%`
  - `MDD = -26.63%`
  - `real_money_candidate / small_capital_trial / review_required`

### 2026-04-13
- Added repo-local Codex workflow support artifacts:
  - current candidate summary
  - backtest refinement code-flow guide
  - runtime artifact hygiene guide
  - repo-local plugin scaffold:
    - `.aiworkspace/plugins/quant-finance-workflow`
  - repo-local skill draft:
    - `finance-backtest-candidate-refinement`
  - first practical plugin script:
    - `.aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py`

### 2026-04-13
- Promoted the finance refinement hygiene script into an explicit operating rule.
- Synced:
  - `AGENTS.md`
  - `operations/RUNTIME_ARTIFACT_HYGIENE.md`
- Default usage points are now:
  - after meaningful refinement/doc-sync units
  - before commit
  - before phase closeout

### 2026-04-13
- Closed Phase 16 as a bounded downside-refinement phase.
- `Value`:
  - current best practical point remains `Top N = 14 + psr`
  - `28.13% / -24.55% / real_money_candidate / paper_probation / review_required`
  - lower-MDD near-miss `+ pfcr` improved `MDD` to `-21.16%` but only reached `production_candidate / watchlist`
- `Quality + Value`:
  - current strongest practical point remains
    `operating_margin + pcr + por + per + Top N 10 + Candidate Universe Equal-Weight`
  - `31.82% / -26.63% / real_money_candidate / small_capital_trial / review_required`
  - lower-MDD alternatives existed, but all weakened gate quality
- Synced:
  - Phase 16 closeout docs
  - strategy hubs / backtest logs
  - roadmap / doc indexes

### 2026-04-14
- Clarified compare / weighted portfolio / saved portfolio workflow semantics.
- Current reading:
  - `Compare` = research surface for side-by-side strategy inspection
  - `Weighted Portfolio` = monthly composite of compared strategies
  - `Saved Portfolio` = replayable research artifact for compare -> builder -> rerun
- Durable note:
  - weighted bundles do not create new real-money / promotion / shortlist / deployment semantics on their own
  - Phase 17 should document them as operator bridges, not as independent candidate gates

### 2026-04-14
- Opened Phase 17 as a structural downside-improvement phase.
- Synced:
  - phase kickoff plan
  - current board
  - structural lever inventory first pass
  - candidate consolidation fit review first pass
  - code-flow guide
  - repo-local refinement skill reference
- Current reading:
  - immediate main track:
    - strict annual structural downside levers
  - secondary/supporting track:
    - weighted portfolio / saved portfolio as operator bridge
- Current first-slice recommendation:
  - `partial cash retention` before broader defensive-sleeve or weighting redesign

### 2026-04-14
- Clarified near-term development order before Phase 17 implementation.
- Current order:
  - first:
    - existing core strategy structural refinement
  - second:
    - candidate consolidation / operator bridge cleanup
  - later:
    - new strategy or wider expansion work
- Durable takeaway:
  - new strategy work is still planned,
    but it is intentionally behind the current `Value / Quality + Value` structural downside-improvement track

### 2026-04-14
- Implemented the first Phase 17 structural lever slice:
  - strict annual `partial cash retention`
- Wired through:
  - `finance.strategy.quality_snapshot_equal_weight(...)`
  - strict annual DB-backed sample/runtime wrappers
  - strict annual single / compare forms
  - selection interpretation / warnings / input params
- Current rule:
  - applies only when `Trend Filter` partially rejects raw selected names
  - does not replace full-cash `market regime` / guardrail risk-off behavior
- Verification:
  - `py_compile` passed
  - synthetic smoke confirmed
    - `off` = survivor reweighting
    - `on` = rejected slots retained as cash
  - representative DB-backed rerun is still gated by local shadow-factor data availability

### 2026-04-14
- Ran the first Phase 17 representative rerun on real current anchors.
- Cases:
  - `Value` current practical anchor:
    - `Top N = 14 + psr`
    - `Trend Filter = on`
    - `cash retention off/on`
  - `Quality + Value` strongest practical point:
    - strongest factor set
    - `Trend Filter = on`
    - `cash retention off/on`
- Result:
  - `partial cash retention` worked and materially lowered `MDD` in both families
  - but both cases still stayed `hold / blocked`
  - main pattern:
    - downside improved strongly
    - cash share rose materially
    - return drag remained too large for practical gate rescue
- Updated:
  - Phase 17 representative rerun report
  - strategy hubs
  - strategy backtest logs
  - current candidate summary
- Next priority:
  - `defensive sleeve risk-off` over another cash-only follow-up

### 2026-04-14
- Implemented the second Phase 17 structural lever slice:
  - strict annual `defensive sleeve risk-off`
- Wired through:
  - `finance.strategy.quality_snapshot_equal_weight(...)`
  - strict annual DB-backed sample/runtime wrappers
  - strict annual single / compare forms
  - warning / meta / interpretation surface
- Important correction:
  - defensive sleeve ticker was separated from strict annual candidate-universe filtering
  - this removed the false `Liquidity Excluded Count` inflation that appeared in the first rerun
- Representative rerun result after the correction:
  - `Value` current anchor:
    - gate unchanged
    - `MDD` slightly worse
  - `Quality + Value` current strongest point:
    - gate unchanged
    - `MDD` slightly worse
- Durable takeaway:
  - `defensive sleeve risk-off` is now implemented and verifiable
  - but it did not produce a same-gate lower-MDD rescue on the current anchors
  - next structural lever priority moves to `concentration-aware weighting`

### 2026-04-14
- Reviewed strict annual reuse points for `concentration-aware weighting`.
- Key finding:
  - no existing rank-based taper/capped position-weight contract was found in the strict annual family
  - the safest first slice remains the `quality_snapshot_equal_weight(...)` rebalancing block after top-N selection
- Reusable runtime contract:
  - keep `strategy_key` / `snapshot_mode` / `snapshot_source` / `factor_freq` / `universe_contract` / dynamic universe fields aligned with the current strict annual wrappers

### 2026-04-14
- Implemented the third Phase 17 structural lever slice:
  - strict annual `concentration-aware weighting`
- Wired through:
  - `finance.strategy.quality_snapshot_equal_weight(...)`
  - strict annual DB-backed sample/runtime wrappers
  - strict annual single / compare forms
  - warning / meta / interpretation surface
- Current contract:
  - `equal_weight`
  - `rank_tapered`
- Representative rerun result:
  - `Value` current anchor:
    - gate unchanged

### 2026-04-15
- Started the first real Phase 20 implementation unit.
- Added a `Current Candidate Re-entry` surface inside `Compare & Portfolio Builder`.
- Current anchors and lower-MDD near-misses can now be sent back into compare without manually rebuilding the full strict annual contract.
- Synced:
  - Phase 20 first work-unit document
  - phase TODO board
  - roadmap / doc index
  - finance comprehensive analysis
- Validation:
  - `py_compile`
  - `.venv` import smoke
  - current candidate registry helper smoke
    - `MDD` worse
    - `Rolling Review` also weakened
  - `Quality + Value` current strongest point:
    - gate unchanged
    - `CAGR` higher
    - but `MDD` worse
- Durable takeaway:
  - `concentration-aware weighting` is now implemented and verifiable
  - but it did not produce a same-gate lower-MDD rescue on the current anchors
  - next active question moves to
    Phase 17 closeout vs next structural lever reprioritization

### 2026-04-14
- Closed Phase 17 as a structural downside-improvement phase.
- Practical closeout reading:
  - `partial cash retention`
  - `defensive sleeve risk-off`
  - `concentration-aware weighting`
  first three slices are now implemented and representative-rerun verified
- Common conclusion:
  - no same-gate lower-MDD exact rescue was found for
    current `Value` / `Quality + Value` anchors
  - current practical anchors remain unchanged
- Synced:
  - Phase 17 completion summary
  - next-phase preparation
  - manual test checklist
  - roadmap / finance doc index
- Follow-up review:
  - examined a possible first slice for filling trend-rejected raw top-N slots with next-ranked eligible names
  - safest candidate insertion point is still the strict annual rebalancing block in `finance/strategy.py`
  - this redesign should be treated as a separate interpretation lane from `partial cash retention` and `rank_tapered`, not as a cosmetic tweak to either one

### 2026-04-14
- Opened Phase 18 as `Larger Structural Redesign`.
- Implemented first slice:
  - strict annual `Fill Rejected Slots With Next Ranked Names`
- Wired through:
  - `finance.strategy.quality_snapshot_equal_weight(...)`
  - strict annual DB-backed sample/runtime wrappers
  - strict annual single / compare forms
  - history / rerun / interpretation surface
- New durable result/meta fields:
  - `Rejected Slot Fill Enabled`
  - `Rejected Slot Fill Active`
  - `Rejected Slot Fill Ticker`
  - `Rejected Slot Fill Count`
  - `rejected_slot_fill_enabled`
- Representative rerun first pass:
  - `Value` trend-on probe:
    - cash drag와 downside 개선 방향은 확인됐지만
      still `hold / blocked`
    - meaningful redesign reference로는 남지만
      current practical anchor replacement는 아니었다
  - `Quality + Value` trend-on probe:
    - `CAGR`, `MDD`, cash share improved
    - but still `hold / blocked`
- Durable takeaway:
  - next-ranked eligible fill is a meaningful larger-redesign lane
  - first pass does not replace the current practical anchors
  - next follow-up should stay in Phase 18 rather than reopening bounded tweak work

### 2026-04-14
- Re-ran Phase 18 `next-ranked eligible fill` around the actual `Value` practical anchor.
- Scope:
  - `base + psr`, `Top N = 12~16`
  - `base + psr + pfcr`, `Top N = 12~16`
  - `Trend Filter = on`, `rejected_slot_fill_enabled = on`
- Result:
  - no same-gate lower-MDD rescue was found
  - all anchor-near candidates remained `hold / blocked`
  - best lower-MDD near-miss was:
    - `base + psr + pfcr`, `Top N = 13`
    - `24.47% / -24.89% / hold / blocked`
- Durable takeaway:
  - Phase 18 first slice should be kept as a meaningful redesign reference,
    not as a rescued replacement candidate
  - next work should shift to Phase 18 second-slice prioritization

### 2026-04-14
- User direction changed Phase 18 from rerun-first to implementation-first.
- Current rule:
  - broader deep backtest / wider rescue search is paused
  - new implementation slices should be followed only by
    compile / import smoke and minimal representative validation
- Synced:
  - Phase 18 plan
  - current board
  - roadmap
  - finance doc index
- Durable takeaway:
  - next active work is not another broad rerun cycle
  - it is selecting and implementing the Phase 18 second slice first

### 2026-04-14
- Rebased the upper roadmap from current `Phase 18` status through a new `Phase 25` draft.
- Current reading:
  - `Phase 18~21`
    - implementation / operator / automation backlog
  - `Phase 22`
    - integrated deep backtest validation restart
  - `Phase 23~25`
    - portfolio candidate / new strategy / pre-live operator workflow expansion
- Synced:
  - master roadmap
  - roadmap rebase draft
  - finance doc index
- Durable takeaway:
  - current discussion point is no longer just the next slice,
    but whether this `Phase 19~25` sequence matches the user's desired long-term direction

### 2026-04-14
- Rewrote the `Phase 19~25` roadmap explanation in plainer language.
- Focus:
  - what each future phase means
  - why it should happen
  - why the proposed order is natural
- Synced:
  - `MASTER_PHASE_ROADMAP.md`
  - `support_tracks/ROADMAP_REBASE_PHASE18_TO_PHASE25_20260414.md`
- Durable takeaway:
  - the roadmap now reads less like a phase title list
    and more like an execution narrative the user can review before deciding direction

### 2026-04-14
- Started `Phase 19` in implementation-first mode.
- First slice:
  - strict annual `Rejected Slot Handling Contract`
  - replaces the operator-facing two-checkbox reading with one explicit handling mode
- Implemented:
  - new explicit mode constants/helpers in `finance.sample`
  - runtime compatibility bridge in `app/web/runtime/backtest.py`
  - single / compare / history / prefill sync in `app/web/pages/backtest.py`
- Validation:
  - `python3 -m py_compile finance/sample.py app/web/runtime/backtest.py app/web/pages/backtest.py`
  - `.venv/bin/python` import smoke for the same modules
- Synced:
  - phase19 kickoff docs
  - roadmap
  - finance doc index
  - finance comprehensive analysis
- Durable takeaway:
  - Phase 19 first slice favors contract clarity and legacy compatibility over broad rerun coverage

### 2026-04-14
- Completed `Phase 19` second slice for history / interpretation cleanup.
- Changed:
  - strict annual selection history now preserves rejected-slot fill / cash-retention execution details for interpretation
  - interpretation summary now shows `Rejected Slot Handling`, `Filled Events`, `Cash-Retained Events`
  - history table hides internal booleans and shows operator-facing contract language instead
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python` import smoke for `app.web.pages.backtest`
- Synced:
  - phase19 TODO/doc
  - finance comprehensive analysis
  - finance doc index
- Durable takeaway:
  - Phase 19 now covers not only form/runtime contract clarity but also history/interpretation readability for the same handling semantics

### 2026-04-14
- Completed `Phase 19` third slice for risk-off / weighting interpretation cleanup.
- Changed:
  - strict annual selection history now shows `Weighting Contract`, `Risk-Off Contract`, `Risk-Off Reasons`
  - interpretation summary now shows `Weighting Contract`, `Risk-Off Contract`, `Defensive Sleeve Activations`
  - row-level interpretation now distinguishes
    - full cash risk-off
    - defensive sleeve rotation
    - final weighting contract
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python` import smoke for `app.web.pages.backtest`
- Synced:
  - phase19 TODO/doc
  - finance comprehensive analysis
  - finance doc index
- Durable takeaway:
  - Phase 19 interpretation cleanup now covers the three main structural contract lanes:
    rejected-slot handling, weighting, and risk-off

### 2026-04-14
- Closed out `Phase 19` at practical closeout / manual_validation_pending.
- Added:
  - `PHASE19_COMPLETION_SUMMARY.md`
  - `PHASE19_NEXT_PHASE_PREPARATION.md`
  - `PHASE19_TEST_CHECKLIST.md`
- Synced:
  - `PHASE19_CURRENT_CHAPTER_TODO.md`
  - `MASTER_PHASE_ROADMAP.md`
  - `FINANCE_DOC_INDEX.md`
- Durable takeaway:
  - Phase 19 is now handed off as a documentation/contract stabilization phase with manual UI validation still pending

### 2026-04-14
- Rewrote the `Phase 19` kickoff plan in much plainer language.
- Focus:
  - what this phase is doing
  - why it is needed before deep backtest resumes
  - what difficult terms like `contract`, `slice`, `payload`, `minimal validation` mean
- Synced:
  - `PHASE19_STRUCTURAL_CONTRACT_EXPANSION_PLAN.md`
  - `FINANCE_TERM_GLOSSARY.md`
- Durable takeaway:
  - the Phase 19 plan now reads as an operator-facing explanation, not just an internal engineering memo

### 2026-04-14
- Updated future phase-plan writing guidance.
- Changed:
  - `AGENTS.md` now requires new or heavily rewritten phase plan docs to include
    - `쉽게 말하면`
    - `왜 필요한가`
    - `이 phase가 끝나면 좋은 점`
  - `Phase 19` kickoff doc now explains the current priority-item jargon inline
- Durable takeaway:
  - future phase plans should be readable as orientation documents, not just compressed planning notes

### 2026-04-14
- Finalized the `Phase 19` kickoff document into a template-style operator-friendly plan.
- Added:
  - `.aiworkspace/note/finance/PHASE_PLAN_TEMPLATE.md`
- Synced:
  - `AGENTS.md`
  - `FINANCE_DOC_INDEX.md`
  - `PHASE19_CURRENT_CHAPTER_TODO.md`
- Durable takeaway:
  - future phase plan documents now have a reusable default shape instead of being rewritten ad hoc each time

### 2026-04-14
- Tightened `Phase 19` strict annual contract UX based on checklist feedback.
- Changed:
  - `Weighting Contract`, `Risk-Off Contract`, `Rejected Slot Handling Contract` now use clearer section titles and labels in strict annual single/compare forms
  - each contract now shows a plain-language "current selection" explanation
  - `Defensive Sleeve Tickers` now explains that it is only used for `Defensive Sleeve Preference` during full risk-off
- Synced:
  - `PHASE19_TEST_CHECKLIST.md`
  - `PHASE19_CURRENT_CHAPTER_TODO.md`
  - `FINANCE_TERM_GLOSSARY.md`
  - `FINANCE_COMPREHENSIVE_ANALYSIS.md`
  - `FINANCE_DOC_INDEX.md`
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python` import smoke for `app.web.pages.backtest`
  - finance refinement hygiene script
- Durable takeaway:
  - Phase 19 contract language is now easier to find and read from the form itself, not only from history or docs

### 2026-04-14
- Standardized future phase test checklist workflow.
- Changed:
  - `AGENTS.md` now requires user-facing phase test checklists to prefer Markdown task checkboxes like `[ ]`
  - new `.aiworkspace/note/finance/PHASE_TEST_CHECKLIST_TEMPLATE.md` added as the default checklist template
  - active `PHASE19_TEST_CHECKLIST.md` converted to checkbox-style verification items
- Durable takeaway:
  - future phase handoffs now have a clearer "user checks items directly, then we move on" workflow

### 2026-04-14
- Refined strict annual contract help text based on live Phase 19 checklist feedback.
- Changed:
  - `Rejected Slot Handling Contract` tooltip now explains each option as separate bullet-style items instead of one long sentence
  - `Risk-Off Contract` tooltip now explains what `portfolio-wide risk-off` means in plain Korean
  - overlay contract intro now states that `Weighting Contract`, `Rejected Slot Handling Contract`, and `Risk-Off Contract` are always-on handling rules, not enable/disable toggles
- Synced:
  - `PHASE19_TEST_CHECKLIST.md`
  - `FINANCE_TERM_GLOSSARY.md`
  - `FINANCE_COMPREHENSIVE_ANALYSIS.md`
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python` import smoke for `app.web.pages.backtest`
  - finance refinement hygiene script
- Durable takeaway:
  - contract UI now answers both "what does this option mean?" and "is this always active?" directly from the form

### 2026-04-14
- Reorganized strict annual advanced inputs into separate overlay and handling sections.
- Changed:
  - single / compare strict annual forms now split
    - `Overlay`
    - `Portfolio Handling & Defensive Rules`
  - `Trend Filter` / `Market Regime` stay in `Overlay`
  - `Rejected Slot Handling Contract` / `Weighting Contract` / `Risk-Off Contract` / `Defensive Sleeve Tickers` move into `Portfolio Handling & Defensive Rules`
- Durable takeaway:
  - overlay trigger logic and post-overlay portfolio handling are now easier to distinguish from the form structure itself

### 2026-04-14
- Simplified strict annual handling-contract captions after live UX feedback.
- Changed:
  - removed repetitive `위치:` phrasing from contract captions
  - rewrote `Rejected Slot Handling Contract`, `Risk-Off Contract`, `Weighting Contract` captions around
    - what situation each contract handles
    - easy plain-language summary
    - how it differs from neighboring contracts
  - portfolio handling intro now uses bullet-style role summary instead of compressed inline prose
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python` import smoke for `app.web.pages.backtest`
- Durable takeaway:
  - the form now explains contract purpose directly, without relying on repeated location hints

### 2026-04-14
- Clarified strict annual `Risk-Off Contract` wording after additional UX feedback.
- Changed:
  - replaced vague `보수 모드` / `full risk-off` phrasing in strict annual form help with
    - "factor 포트폴리오 전체를 멈추고 현금 또는 방어 ETF로 전환"
    - "포트폴리오 전체를 쉬어야 할 때"
  - aligned `Risk-Off Contract`, `Defensive Sleeve Tickers`, overlay intro, and interpretation summary around the same plain-language meaning
  - synced glossary/comprehensive analysis wording to the same concept
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python` import smoke for `app.web.pages.backtest`
  - finance refinement hygiene script
- Durable takeaway:
  - users can now read `Risk-Off Contract` as a portfolio-wide transition rule without having to infer what `보수 모드` means

### 2026-04-14
- Tightened History / Selection History UX after Phase 19 checklist confusion.
- Changed:
  - `Backtest > History` now explains that a `history run` means one saved backtest record
  - selected history record drilldown now uses clearer labels like `Selected History Run`, `Saved Run Summary`, `Saved Input & Context`
  - strict annual history drilldown now explicitly says detailed `Selection History` / `Interpretation Summary` are checked after `Run Again` or `Load Into Form`
  - latest result selection tabs now read
    - `Selection History Table`
    - `Interpretation Summary`
    - `Selection Frequency`
  - `Selection History Table` now states that the `Interpretation` column is the row-level explanation
  - `Interpretation Summary` now states which contract / event fields should be checked first
- Synced:
  - `FINANCE_TERM_GLOSSARY.md`
  - `FINANCE_COMPREHENSIVE_ANALYSIS.md`
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python` import smoke for `app.web.pages.backtest`
  - finance refinement hygiene script
- Durable takeaway:
  - users can now find the correct history surface faster and distinguish saved-record review from live selection-history drilldown

### 2026-04-14
- Fixed confusing `History` action flow for strict annual records.
- Changed:
  - `Run Again` from `Backtest > History` now reruns immediately, then moves the UI to `Single Strategy` so the refreshed `Latest Backtest Run` is visible right away
  - `Load Into Form` still moves to `Single Strategy`, but now clearly says it only loads inputs and does not refresh results until the user runs the form
  - added `Back To History` shortcut after `Load Into Form` so the user is not left without an obvious way back
  - updated history warning copy to reference `Selection History Table` / `Interpretation Summary` with current labels
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python` import smoke for `app.web.pages.backtest`
  - finance refinement hygiene script
- Durable takeaway:
  - history actions now better match user expectation: rerun shows refreshed results, while load-into-form is explicitly framed as input prefill only

### 2026-04-15
- Refined Phase 19 closeout docs to better match the user's actual checklist progress and reading flow.
- Changed:
  - `PHASE19_CURRENT_CHAPTER_TODO.md` now marks manual UI validation as `in_progress` instead of `pending`
  - `PHASE19_COMPLETION_SUMMARY.md` now explains completed work in plainer language under `쉽게 말하면`
  - `PHASE_PLAN_TEMPLATE.md` now uses `작업 단위` language instead of `slice`
  - `AGENTS.md` now explicitly prefers plain-language work-unit labels in future phase plan documents
  - `PHASE19_STRUCTURAL_CONTRACT_EXPANSION_PLAN.md` was aligned to the same `작업 단위` wording
- Validation:
  - finance refinement hygiene script
- Durable takeaway:
  - phase plan and closeout docs now better match user-facing review flow and avoid internal jargon where it is not helpful

### 2026-04-15
- Phase 19 manual checklist gate is now treated as completed.
- Changed:
  - `PHASE19_CURRENT_CHAPTER_TODO.md` now marks manual UI validation actual run as `completed`
  - `PHASE19_COMPLETION_SUMMARY.md` now reflects `manual_validation_completed`
- Durable takeaway:
  - Phase 19 can now be treated as fully closed from a user-verification standpoint, and the next phase discussion can proceed without leaving the validation gate ambiguous

### 2026-04-15
- Opened Phase 20 as the next active workstream after Phase 19 closeout.
- Changed:
  - created `PHASE20_CANDIDATE_CONSOLIDATION_AND_OPERATOR_WORKFLOW_HARDENING_PLAN.md`
  - created `PHASE20_CURRENT_CHAPTER_TODO.md`
  - created `PHASE20_OPERATOR_WORKFLOW_INVENTORY_FIRST_PASS.md`
  - updated `MASTER_PHASE_ROADMAP.md` phase20 status to `in_progress`
  - synced `FINANCE_DOC_INDEX.md`
- Durable takeaway:
  - the project is now treating candidate reuse, compare-to-portfolio flow, and saved-portfolio re-entry as the main active operator workflow problem

### 2026-04-15
- Completed a practical Phase 21 automation/persistence baseline in one work unit.
- Changed:
  - added `bootstrap_finance_phase_bundle.py` to open a new phase document bundle from the repo templates
  - added `manage_current_candidate_registry.py` and seeded `.aiworkspace/note/finance/registries/CURRENT_CANDIDATE_REGISTRY.jsonl`
  - updated `check_finance_refinement_hygiene.py` so candidate-facing doc work can also review the machine-readable candidate registry
  - created `PHASE21` kickoff, work-unit, closeout, next-phase, and checklist documents
  - synced `AGENTS.md`, plugin/skill docs, roadmap, doc index, registry guide, runtime artifact guidance, and finance comprehensive analysis
- Validation:
  - `python3 -m py_compile .aiworkspace/plugins/quant-finance-workflow/scripts/bootstrap_finance_phase_bundle.py .aiworkspace/plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py`
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py validate`
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/bootstrap_finance_phase_bundle.py --phase 99 --title "Automation Smoke Example" --dry-run`
  - finance refinement hygiene script
- Durable takeaway:
  - the repo now has a reusable automation baseline for phase kickoff and current-candidate persistence, which lowers repeated setup cost before later deep validation phases

### 2026-04-15
- Phase 20 QA feedback led to another compare-surface UX cleanup.
- Changed:
  - moved current candidate re-entry out of the space between the compare title and the main `Strategies` control
  - kept strategy selection as the first visible compare action
  - reorganized the current candidate helper into a secondary expander with a smaller `What This Does` explanation block
  - synced `FINANCE_COMPREHENSIVE_ANALYSIS.md`
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python -c "import importlib; import app.web.pages.backtest"`
  - finance refinement hygiene script
- Durable takeaway:
  - compare now reads as a primary strategy-selection surface first, while current candidate re-entry behaves like a supporting shortcut instead of competing for top-of-screen attention

### 2026-04-15
- Phase 20 QA also surfaced excessive divider usage inside `Compare & Portfolio Builder`.
- Changed:
  - removed top-level dividers between compare results, weighted portfolio builder, and saved portfolios
  - clarified in the saved-portfolio caption that this area is the next step after compare and weighted builder, not a separate top-level workflow
  - synced `FINANCE_COMPREHENSIVE_ANALYSIS.md`
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python -c "import app.web.pages.backtest"`
  - finance refinement hygiene script
- Durable takeaway:
  - the compare page now relies on section headings instead of repeated horizontal lines, and saved portfolios remains in the same tab because it still behaves like the final step of the same operator workflow

### 2026-04-15
- Phase 20 QA found that current candidate re-entry button labels still read too much like internal jargon.
- Changed:
  - renamed `Load Current Anchors` to `Load Recommended Candidates`
  - renamed `Load Lower-MDD Near Misses` to `Load Lower-MDD Alternatives`
  - renamed the custom picker expander to `Pick Specific Candidates Manually`
  - added one-line explanations under each quick action so users can tell why there are two buttons and when to use each
  - synced `FINANCE_COMPREHENSIVE_ANALYSIS.md`
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python -c "import app.web.pages.backtest"`
  - finance refinement hygiene script
- Durable takeaway:
  - current candidate re-entry now explains “대표 후보 불러오기 / 더 낮은 MDD 대안 불러오기 / 직접 선택” in plain language instead of forcing users to decode internal portfolio-search terms

### 2026-04-15
- Phase 20 QA still found the current candidate re-entry block hard to scan as one mixed section.
- Changed:
  - split the surface into `Quick Bundles` and `Pick Manually` tabs
  - kept the two quick-load buttons together in the first tab
  - moved the candidate table and manual picker into the second tab
  - added an explicit note that this list does not auto-populate from new backtest runs or Markdown docs; it reads active rows from `CURRENT_CANDIDATE_REGISTRY.jsonl`
  - synced `FINANCE_COMPREHENSIVE_ANALYSIS.md`
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python -c "import app.web.pages.backtest"`
  - finance refinement hygiene script
- Durable takeaway:
  - current candidate re-entry now reads as two clearer modes: quick bundle load vs manual pick, and the registry source rule is visible in the UI instead of only in supporting docs

### 2026-04-15
- Phase 20 QA then pointed out that the post-load `What Changed In Compare` card still felt too abstract.
- Changed:
  - changed the card title/phrasing so it reads as a form-update guide instead of an internal status block
  - replaced `Source`, `Label`, `Period` wording with more direct phrases about how the bundle was loaded and what period was auto-filled
  - added a short “where to check” section and a clearer next-step instruction
  - synced `FINANCE_COMPREHENSIVE_ANALYSIS.md`
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python -c "import app.web.pages.backtest"`
  - finance refinement hygiene script
- Durable takeaway:
  - the compare prefill confirmation card now explains the loaded bundle in task-oriented language instead of assuming the user already understands source/label terminology

### 2026-04-15
- Phase 20 QA also asked whether the compare prefill summary was drifting from the actual candidate settings.
- Changed:
  - checked the current-candidate registry -> compare prefill override mapping for top N, benchmark, trend filter, market regime, weighting, risk-off, and universe contract
  - confirmed the current code maps those core fields consistently for the active candidate rows
  - expanded the `Compare Form Updated` table to show `Weighting Contract` and `Risk-Off Contract` alongside `Trend Filter` and `Market Regime`
  - synced `FINANCE_COMPREHENSIVE_ANALYSIS.md`
- Validation:
  - `.venv/bin/python` registry-to-prefill smoke check for current candidate rows
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python -c "import app.web.pages.backtest"`
  - finance refinement hygiene script
- Durable takeaway:
  - the current candidate compare prefill path does not appear to be silently loosening key strict-annual settings, and the confirmation table now exposes more of the actual loaded contract

### 2026-04-15
- Phase 20 QA then pointed out that compare `Strategy-Specific Advanced Inputs` still split family selection from the actual selected snapshot settings.
- Changed:
  - turned `Quality Family`, `Value Family`, `Quality + Value Family` into `Quality`, `Value`, `Quality + Value`
  - kept the variant selector at the top of each family section
  - rendered the selected variant's actual settings directly inside the same family expander instead of in a separate snapshot expander lower in the form
  - synced `FINANCE_COMPREHENSIVE_ANALYSIS.md`
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python -c "import app.web.pages.backtest"`
  - finance refinement hygiene script
- Durable takeaway:
  - compare advanced inputs now read more like GTAA and other strategies: choose the family variant once, then adjust that variant immediately in the same section

### 2026-04-15
- Phase 20 QA also asked for a clearer explanation of `Candidate Universe Equal-Weight` inside strict annual `Benchmark Contract`.
- Changed:
  - rewrote the `Benchmark Contract` tooltip in plain language so the two options read as
    "compare to one benchmark ETF" vs "compare to a simple equal-weight portfolio built from the same candidate universe"
  - expanded the selected-state caption for `Candidate Universe Equal-Weight` so the user can understand the meaning without opening glossary docs
  - added a dedicated glossary entry for `Candidate Universe Equal-Weight`
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python -c "import app.web.pages.backtest"`
  - finance refinement hygiene script
- Durable takeaway:
  - strict annual benchmark choice is now easier to read as an operator decision: external ETF reference vs simple equal-weight baseline from the same candidate pool

### 2026-04-15
- Phase 20 QA then found that `Candidate Universe Equal-Weight / SPY` still looked like a single mixed benchmark label in compare summaries.
- Changed:
  - split compare prefill summary output into `Benchmark Contract` and `Benchmark Ticker / Reference`
  - changed current candidate registry contract summary so equal-weight cases read as
    `Benchmark Candidate Equal-Weight | Reference Ticker SPY`
    instead of an ambiguous slash-joined label
  - added an explanatory caption in the compare update card when equal-weight benchmark contract is active
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - finance refinement hygiene script
- Durable takeaway:
  - the UI now shows that equal-weight benchmark and SPY are not the same object: one is the benchmark contract, the other can remain a separate reference ticker

### 2026-04-15
- Phase 20 QA asked to make the strict-annual input field itself reflect that distinction too.
- Changed:
  - initially tried contract-dependent field naming, but this was not reliable inside the current submit-based Streamlit form
  - switched to a more robust fixed label: `Benchmark / Guardrail / Reference Ticker`
  - added a plain-language caption explaining how to read the field under each benchmark contract
  - kept prefill summary lines using `Reference Ticker` wording for equal-weight cases
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python -c "import app.web.pages.backtest"`
  - finance refinement hygiene script
- Durable takeaway:
  - in the current form architecture, a stable neutral field label plus contract-dependent explanation is less confusing than trying to live-swap the field name

### 2026-04-15
- Phase 20 QA then confirmed that the neutral single-field approach still felt indirect in practice.
- Changed:
  - separated strict-annual `Real-Money Contract` into two explicit inputs:
    - `Benchmark Ticker`
    - `Guardrail / Reference Ticker`
  - kept `Comparison Baseline` and `Guardrail / Reference` as separate concepts in the form so the user can read
    "what do we compare against?" and "what does the guardrail watch?" independently
  - propagated the same split through single strategy, compare prefill, history/meta, runtime bundle input params, and shadow sample entrypoints
  - updated compare summary copy so equal-weight benchmark rows explain the split using the new two-column wording
- Validation:
  - `python3 -m py_compile finance/sample.py app/web/runtime/backtest.py app/web/pages/backtest.py`
  - `.venv/bin/python -c "import finance.sample; import app.web.runtime.backtest; import app.web.pages.backtest"`
- Reviewed:
  - `FINANCE_DOC_INDEX.md`는 새 durable 문서가 추가된 턴이 아니라서 이번 작업 단위에서는 별도 갱신이 필요하지 않다고 판단
- Durable takeaway:
  - the final UX model is no longer "one ticker field with two meanings"; benchmark baseline and guardrail reference are now first-class separate inputs

### 2026-04-15
- Phase 20 QA then asked for one more UX pass: when `Ticker Benchmark` is chosen, `Guardrail / Reference Ticker` should feel optional, and when `Candidate Universe Equal-Weight` is chosen, `Benchmark Ticker` should stop looking required.
- Changed:
  - `Ticker Benchmark` mode now shows:
    - `Benchmark Ticker`
    - `Guardrail / Reference Ticker (Optional)`
    with copy that says leaving the guardrail field blank means "same as benchmark"
  - `Candidate Universe Equal-Weight` mode now hides the benchmark ticker input and explains that the benchmark curve is auto-built from the candidate universe
  - compare/prefill/history summaries now display `Same as Benchmark Ticker` when no separate guardrail ticker was explicitly set
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python -c "import app.web.pages.backtest"`
- Durable takeaway:
  - the operator now reads benchmark baseline and guardrail reference as separate decisions, with the optional/same-as-benchmark case made explicit in the UI

### 2026-04-15
- Phase 20 QA then reported that trying to make fields hide/show based on `Benchmark Contract` still felt awkward in practice.
- Changed:
  - confirmed the root cause was the current `st.form` structure: changing a widget inside the form does not immediately rerun the section
  - removed the experimental layout-refresh button approach
  - returned to a simpler UX where `Benchmark Contract`, `Benchmark Ticker`, and `Guardrail / Reference Ticker (Optional)` are always visible together
  - rewrote the captions so the user can understand:
    - `Ticker Benchmark`: benchmark ticker is the direct comparison baseline
    - `Candidate Universe Equal-Weight`: benchmark ticker is not used for the equal-weight baseline itself
    - `Guardrail / Reference Ticker (Optional)`: tied to underperformance / drawdown guardrails regardless of benchmark contract
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python -c "import app.web.pages.backtest"`
- Durable takeaway:
  - within the current form architecture, "always visible + clearer explanation" is less frustrating than contract-dependent hide/show

### 2026-04-15
- Phase 20 QA then pushed one step further: `Guardrail / Reference Ticker` should not live in `Real-Money Contract` at all because it conceptually belongs to guardrails, not benchmark comparison.
- Changed:
  - moved `Guardrail / Reference Ticker (Optional)` out of `Real-Money Contract` and into the `Guardrails` expander
  - kept `Benchmark Contract` and `Benchmark Ticker` inside `Real-Money Contract`
  - updated the copy so the screen now reads as:
    - `Real-Money Contract` = comparison baseline
    - `Guardrails` = underperformance / drawdown stop rules plus their reference ticker
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python -c "import app.web.pages.backtest"`
- Durable takeaway:
  - the benchmark baseline and the guardrail reference now live in the same places as their actual behavioral meaning, which is much easier to understand in the UI

### 2026-04-15
- Phase 20 QA then pointed out that `Compare Form Updated` should hide values that are not actually used by the loaded contract.
- Changed:
  - when `Benchmark Contract = Candidate Universe Equal-Weight`, the compare summary now leaves `Benchmark Ticker` blank
  - when both underperformance and drawdown guardrails are off, the compare summary now leaves `Guardrail / Reference Ticker` blank
  - kept `Same as Benchmark Ticker` only for cases where a guardrail is on but no separate reference ticker was explicitly entered
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python -c "import app.web.pages.backtest"`
- Durable takeaway:
  - the compare summary is now closer to a true "active settings" view: unused values stay empty instead of looking meaningful

### 2026-04-15
- Phase 20 QA then hit a follow-up compare strict-annual runtime error after the `Guardrail / Reference Ticker` field was moved into `Guardrails`.
- Changed:
  - removed one stale `guardrail_reference_ticker` assignment that still lived in the compare `Quality Snapshot (Strict Annual)` path
  - kept the compare strict-annual guardrail reference flow fully inside the `Guardrails` expander, matching the single-strategy path
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python -c "import app.web.pages.backtest"`
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py`
- Durable takeaway:
  - the compare strict-annual UI now uses the same guardrail-reference ownership model as the single-strategy UI, so the late `NameError` regression is removed.

### 2026-04-16
- Phase 20 QA then pointed out that the information block above `Weighted Portfolio Builder` still read like an internal context card instead of an operator-friendly "what am I combining?" view.
- Changed:
  - rewrote the builder intro copy in plain language so the section reads as "compare에서 본 전략을 어떤 비중으로 섞는 단계"
  - replaced the old `Current Compare Bundle` style card with a clearer `What You Are Combining` summary
  - the summary now shows:
    - where this compare result came from
    - which period is being combined
    - how many strategies are in scope
    - a compact strategy table with `Strategy / Period / CAGR / MDD / Promotion`
  - kept saved-portfolio re-entry weights visible only when they actually exist, as context rather than as the main headline
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python -c "import app.web.pages.backtest"`
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py`
- Durable takeaway:
  - weighted-builder context now starts from "what we are combining" instead of "what internal compare bundle object exists," which is easier to read during QA and normal operator use.

### 2026-04-16
- Phase 20 QA then requested that divider placement in `Compare & Portfolio Builder` match the visual grouping more naturally.
- Changed:
  - removed the divider directly under `Quick Re-entry From Current Candidates`
  - added a divider between `Strategy Comparison` and `Weighted Portfolio Builder`
  - added a divider between `Weighted Portfolio Builder` and `Saved Portfolios`
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python -c "import app.web.pages.backtest"`
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py`
- Durable takeaway:
  - dividers now separate the three main operator stages instead of splitting the compare entry tools from the compare form.

### 2026-04-16
- Phase 20 QA then showed that the checklist itself had started lagging behind the renamed UI labels.
- Changed:
  - updated `PHASE20_TEST_CHECKLIST.md` to use current on-screen names first
  - added an old-name -> current-UI-name mapping block
  - made each section more explicit about where the tester should look on screen
  - aligned the weighted/saved divider checks with the current layout
- Durable takeaway:
  - once UI wording starts changing during QA, the checklist should follow the current labels quickly or it stops being a good test guide.

### 2026-04-16
- Closed `Phase 18` as `practical_closeout / manual_validation_pending` instead of keeping the remaining structural backlog open as an active blocker.
- Changed:
  - created `PHASE18_COMPLETION_SUMMARY.md`
  - created `PHASE18_NEXT_PHASE_PREPARATION.md`
  - created `PHASE18_TEST_CHECKLIST.md`
  - updated `PHASE18_CURRENT_CHAPTER_TODO.md` so the remaining second-slice idea is now treated as deferred backlog rather than current active work
  - updated `PHASE18_LARGER_STRUCTURAL_REDESIGN_PLAN.md` so the current phase reading points toward closeout and handoff
- Durable takeaway:
  - `Phase 18` already produced meaningful redesign evidence, but not anchor replacement evidence, so the right next step is closeout plus handoff rather than one more structural slice.

### 2026-04-16
- Started the new main `Phase 21` reading as `in_progress` and aligned the top-level roadmap/doc index to that state.
- Changed:
  - updated `PHASE21_INTEGRATED_DEEP_BACKTEST_VALIDATION_PLAN.md` to explicitly treat `Phase 18` remaining structural ideas as future options
  - updated `PHASE21_CURRENT_CHAPTER_TODO.md` to reflect kickoff progress and the `Phase 18` closeout decision
  - synced `MASTER_PHASE_ROADMAP.md` and `FINANCE_DOC_INDEX.md` so they now read as:
    - `Phase 18` = practical closeout / manual validation pending
    - `Phase 21` = in progress
- Durable takeaway:
  - the main track is now clearer: we are not opening more structural redesign first, we are validating the current annual-strict candidates and portfolio bridge in one shared frame.

### 2026-04-16
- Continued `Phase 21` with the first real work unit: validation frame definition.
- Changed:
  - created `PHASE21_VALIDATION_FRAME_DEFINITION_FIRST_WORK_UNIT.md`
  - fixed the common rerun frame to:
    - `2016-01-01 ~ 2026-04-01`
    - `US Statement Coverage 100`
    - `Historical Dynamic PIT Universe`
  - fixed the family rerun packs to the current registry-backed candidates:
    - `Value` current anchor / lower-MDD near-miss
    - `Quality` current anchor / cleaner alternative
    - `Quality + Value` current anchor / lower-MDD weaker-gate alternative
  - fixed the representative bridge frame to:
    - `Load Recommended Candidates`
    - near-equal weighted bundle
    - representative saved portfolio replay
  - fixed phase21 report and strategy-log naming rules before actual reruns
- Durable takeaway:
  - `Phase 21` is now in a true execution-ready state: the next step is no longer "define the frame" but "run the pack."

### 2026-04-16
- Ran the first actual `Phase 21` rerun pack for `Value`.
- Changed:
  - reran:
    - current anchor `Top N = 14 + psr`
    - lower-MDD alternative `Top N = 14 + psr + pfcr`
  - confirmed in the shared `Phase 21` frame that:
    - current anchor stays `real_money_candidate / paper_probation / review_required`
    - lower-MDD alternative still remains `production_candidate / watchlist / review_required`
  - created `backtest_reports/phase21/PHASE21_VALUE_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md`
  - created `backtest_reports/phase21/README.md`
  - synced `VALUE_STRICT_ANNUAL.md`, `VALUE_STRICT_ANNUAL_BACKTEST_LOG.md`, `CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md`, phase21 TODO, and the report indexes
- Durable takeaway:
  - `Value` does not need a candidate replacement right now; the current anchor remains the practical reference point even in the integrated validation frame.

### 2026-04-16
- Ran the second actual `Phase 21` rerun pack for `Quality`.
- Changed:
  - reran:
    - current anchor `capital_discipline + LQD + trend on + regime off + Top N 12`
    - cleaner alternative `capital_discipline + SPY + trend on + regime off + Top N 12`
  - confirmed in the shared `Phase 21` frame that:
    - current anchor still remains the practical reference point
    - cleaner alternative still remains a comparison-only surface rather than a replacement
  - created `backtest_reports/phase21/PHASE21_QUALITY_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md`
  - synced `QUALITY_STRICT_ANNUAL.md`, `QUALITY_STRICT_ANNUAL_BACKTEST_LOG.md`, `CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md`, phase21 TODO, and the report indexes
- Durable takeaway:
  - `Quality` also does not need a candidate replacement right now; the `LQD` anchor remains the practical point, and the `SPY` version remains useful mainly as a cleaner comparison surface.

### 2026-04-17
- Ran the third actual `Phase 21` rerun pack for `Quality + Value`.
- Changed:
  - reran:
    - current strongest point `operating_margin + pcr + por + per + Top N 10`
    - lower-MDD alternative with the same factor set and `Top N 9`
  - confirmed in the shared `Phase 21` frame that:
    - current strongest point remains `real_money_candidate / small_capital_trial / review_required`
    - `Top N 9` has stronger raw metrics but still drops to `production_candidate / watchlist / review_required`
  - created `backtest_reports/phase21/PHASE21_QUALITY_VALUE_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md`
  - synced `QUALITY_VALUE_STRICT_ANNUAL.md`, `QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md`, `CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md`, phase21 TODO, and the report indexes
- Durable takeaway:
  - `Quality + Value` remains the strongest blended representative anchor, but the very attractive `Top N 9` alternative still needs weaker-gate handling before it can replace the anchor.

### 2026-04-17
- Ran the `Phase 21` representative portfolio bridge validation.
- Changed:
  - rebuilt the `Load Recommended Candidates` source bundle from:
    - `Value` current anchor
    - `Quality` current anchor
    - `Quality + Value` current anchor
  - built the representative weighted portfolio with:
    - `33 / 33 / 34`
    - `Date Alignment = intersection`
  - validated saved portfolio replay by reconstructing the saved compare context and portfolio context
  - created `backtest_reports/phase21/PHASE21_PORTFOLIO_BRIDGE_VALIDATION_FIRST_PASS.md`
  - updated Phase 21 completion / next-phase docs and candidate summary
- Durable takeaway:
  - the portfolio bridge is reproducible and meaningful enough for Phase 22 portfolio-level candidate construction, but portfolio-level promotion semantics still need to be designed before treating it as a production candidate.

### 2026-04-17
- Refined `Phase 21` QA wording after checklist review.
- Changed:
  - added `Validation Frame` to the shared finance glossary
  - rewrote the Phase 21 plan wording around deferred Phase 18 structural backlog, current anchors, and lower-MDD rescue candidates in plainer language
  - updated the Phase 21 checklist so validation frame verification points directly to the glossary
- Durable takeaway:
  - Phase 21 manual QA should now read as a user-facing validation guide rather than an internal shorthand memo.

### 2026-04-17
- Clarified where to verify `Phase 21` family-level integrated rerun results during manual QA.
- Changed:
  - expanded `PHASE21_TEST_CHECKLIST.md` section 2 with direct links to the phase21 archive, the three family rerun reports, and the strategy hub / backtest log documents
  - recorded the clarification in the Phase 21 TODO board
- Durable takeaway:
  - family-level rerun QA should start from `.aiworkspace/note/finance/backtest_reports/phase21/README.md`, then inspect the `Value`, `Quality`, and `Quality + Value` rerun reports.

### 2026-04-17
- Refined `Phase 21` manual QA decision guidance and annual strict backtest log readability.
- Changed:
  - added 유지 / 교체 / 보류 판단 기준 to `PHASE21_TEST_CHECKLIST.md`
  - standardized the three annual strict backtest logs to read newest-first and end with a compact recent decision summary table
  - moved misplaced `2026-04-14` concentration-aware weighting entries in `Value` and `Quality + Value` logs back into date order
  - updated the shared backtest log template and indexes so future logs follow the same pattern
- Durable takeaway:
  - manual QA should use report interpretation plus gate status, not raw CAGR/MDD alone, when checking whether a candidate is maintained, replaced, or deferred.

### 2026-04-17
- Clarified `Phase 21` portfolio bridge validation locations during manual QA.
- Changed:
  - updated `PHASE21_TEST_CHECKLIST.md` section 3 to point to `PHASE21_PORTFOLIO_BRIDGE_VALIDATION_FIRST_PASS.md` as the official rerun report
  - separated the document report from the UI verification path:
    - `Weighted Portfolio Builder`
    - `Weighted Portfolio Result`
    - `Saved Portfolios`
    - `Replay Saved Portfolio`
  - recorded the clarification in the Phase 21 TODO board
- Durable takeaway:
  - `weighted portfolio / saved portfolio rerun report` should be read as the Phase 21 Markdown report, while the Streamlit UI is the optional replay/visual verification path.

### 2026-04-17
- Rewrote the `Phase 21` portfolio bridge validation report for readability.
- Changed:
  - restructured `PHASE21_PORTFOLIO_BRIDGE_VALIDATION_FIRST_PASS.md` around:
    - what the document is
    - the conclusion first
    - plain-language terms
    - why the three annual strict strategies were used
    - validation flow
    - weighted / saved replay results
    - what the result does and does not prove
    - Phase 22 questions
  - clarified that `FIRST_PASS` means first validation, not final portfolio recommendation
  - synced the Phase 21 archive README, report index, finance doc index, and TODO board
- Durable takeaway:
  - the portfolio bridge report should now read as a workflow validation report rather than an AI-looking result dump.

### 2026-04-17
- Aligned the `Phase 21` manual checklist with the rewritten portfolio bridge report.
- Changed:
  - updated `PHASE21_TEST_CHECKLIST.md` section 3 so QA follows the new report flow:
    - conclusion first
    - why the three strategies were grouped
    - validation flow
    - what the result does and does not prove
    - Phase 22 questions
  - recorded the checklist alignment in the Phase 21 TODO board
- Durable takeaway:
  - portfolio bridge QA now checks whether the report is clearly framed as workflow validation, not as final portfolio winner selection.

### 2026-04-17
- Reorganized the full `Phase 21` test checklist for readability.
- Changed:
  - rewrote `PHASE21_TEST_CHECKLIST.md` around a consistent structure:
    - what to verify
    - where to verify it
    - concrete checkbox items
  - converted scattered location notes into tables for validation frame, family reruns, portfolio bridge, and closeout
  - kept existing user QA checkmarks while making section 3 less noisy and easier to follow
  - synced the Phase 21 TODO board and finance doc index
- Durable takeaway:
  - Phase 21 QA should now be executable from top to bottom without asking where each evidence item lives.

### 2026-04-17
- Closed `Phase 21` after user checklist completion and opened `Phase 22`.
- Changed:
  - marked `PHASE21_CURRENT_CHAPTER_TODO.md` and `PHASE21_COMPLETION_SUMMARY.md` as `phase_complete / manual_validation_completed`
  - created the `Phase 22 Portfolio-Level Candidate Construction` phase bundle with the repo-local bootstrap helper
  - rewrote the Phase 22 plan from template text into a plain-language kickoff document
  - created `PHASE22_PORTFOLIO_LEVEL_CANDIDATE_SEMANTICS_FIRST_WORK_UNIT.md`
  - added `Portfolio-Level Candidate`, `Portfolio Bridge`, `Saved Portfolio Replay`, and `Date Alignment` to the shared glossary
  - synced `MASTER_PHASE_ROADMAP.md` and `FINANCE_DOC_INDEX.md`
- Durable takeaway:
  - Phase 22 is now active, and the immediate next work is to turn the Phase 21 `33 / 33 / 34` portfolio bridge into a controlled baseline portfolio candidate pack rather than treating it as a final winner.

### 2026-04-17
- Completed the first `Phase 22` baseline portfolio candidate pack report.
- Changed:
  - created `backtest_reports/phase22/README.md`
  - created `backtest_reports/phase22/PHASE22_BASELINE_PORTFOLIO_CANDIDATE_PACK_FIRST_PASS.md`
  - clarified that the `Phase 21` `33 / 33 / 34` label is a near-equal shorthand, while the saved definition is `[33.33, 33.33, 33.33]` normalized to equal thirds
  - fixed the baseline portfolio status as `baseline_candidate / portfolio_watchlist / not_deployment_ready`
  - reviewed `CURRENT_CANDIDATE_REGISTRY.jsonl`; validation passes, but no append was made because portfolio-level candidate registry semantics are not defined yet
  - synced Phase 22 TODO/checklist, roadmap, finance doc index, backtest report index, and current practical candidate summary
- Durable takeaway:
  - `phase22_annual_strict_equal_third_baseline_v1` is now the first portfolio-level baseline candidate pack, but not a final portfolio winner.

### 2026-04-17
- Completed the second `Phase 22` benchmark / guardrail / weight-scope work unit.
- Changed:
  - created `PHASE22_PORTFOLIO_BENCHMARK_GUARDRAIL_AND_WEIGHT_SCOPE_SECOND_WORK_UNIT.md`
  - set the primary portfolio benchmark to `phase22_annual_strict_equal_third_baseline_v1`
  - kept `SPY` as market context rather than the Phase 22 primary gate
  - clarified that component benchmarks remain component-level quality checks, not portfolio-level benchmarks
  - defined portfolio-level guardrail as report-level warning, not an actual trading rule
  - narrowed next weight alternatives to `25 / 25 / 50` and `40 / 40 / 20`
  - added `Portfolio-Level Benchmark`, `Portfolio-Level Guardrail`, and `Weight Alternative` to the glossary
  - synced Phase 22 TODO/checklist, roadmap, finance doc index, and backtest report index
- Durable takeaway:
  - the next actual validation step is no longer open-ended; rerun only the two scoped weight alternatives against the equal-third baseline.

### 2026-04-17
- Completed the `Phase 22` weight alternative first-pass rerun.
- Changed:
  - reran the saved portfolio compare context for `Value / Quality / Quality + Value` strict annual anchors
  - compared official equal-third baseline `[33.33, 33.33, 33.33]` against `25 / 25 / 50` and `40 / 40 / 20`
  - created `PHASE22_WEIGHT_ALTERNATIVE_RERUN_FIRST_PASS.md`
  - reconciled the earlier `33 / 33 / 34` Phase 21 near-equal metric with the Phase 22 official equal-third baseline metric
  - updated the Phase 22 TODO, checklist, completion summary, next-phase prep, roadmap, finance doc index, and backtest report index
- Durable takeaway:
  - `25 / 25 / 50` improves raw return but creates `Quality + Value` concentration, while `40 / 40 / 20` lowers drawdown only slightly while giving up CAGR; equal-third remains the Phase 22 primary portfolio baseline.

### 2026-04-17
- Prepared `Phase 22` for manual validation.
- Changed:
  - marked the Phase 22 TODO board as `manual_validation_ready`
  - finalized the Phase 22 checklist around portfolio candidate semantics, baseline report, saved replay, benchmark / guardrail policy, and weight alternative rerun
  - synced the completion summary, next-phase preparation, roadmap, and finance doc index with the manual QA handoff state
- Durable takeaway:
  - Phase 22 implementation/reporting work is ready for user checklist QA; the next decision is closeout vs one more diversified-component portfolio check.

### 2026-04-18
- Polished the `Phase 22` plan and checklist entry point during manual QA.
- Changed:
  - rewrote `PHASE22_PORTFOLIO_LEVEL_CANDIDATE_CONSTRUCTION_PLAN.md` around purpose, necessity, minimum candidate conditions, actual execution order, and checklist usage
  - removed the duplicated feel between `목적` and `쉽게 말하면` by combining the explanation into `목적: 쉽게 말하면`
  - updated `PHASE22_TEST_CHECKLIST.md` section 1 so the user can see exactly which document sections to read and what each checkbox means
  - synced the Phase 22 TODO board and finance doc index
- Durable takeaway:
  - Phase 22 QA should now start from a clearer orientation document, not a phase memo that expects prior chat context.

### 2026-04-18
- Clarified the `Phase 22` development-validation boundary during manual QA.
- Changed:
  - updated the Phase 22 plan to state that the phase is not selecting a live investment portfolio
  - clarified that `Value / Quality / Quality + Value` are representative fixtures for portfolio workflow validation, not a final recommended allocation
  - clarified that the equal-third baseline is a development-validation comparison baseline, not an investment benchmark
  - updated the Phase 22 baseline report and checklist with the same boundary
- Durable takeaway:
  - Phase 22 should be read as portfolio-construction workflow validation for the quant program, not as final portfolio research or live-deployment approval.

### 2026-04-18
- Refreshed the master roadmap after the user identified phase drift risk.
- Changed:
  - added a product development direction section to `MASTER_PHASE_ROADMAP.md`
  - fixed the default roadmap stance as development-first, not investment-analysis-first
  - clarified that user-requested backtests / analysis can still be run during QA, but should be recorded as explicit analysis rather than phase direction drift
  - realigned `Phase 23~25` toward quarterly / alternate cadence productionization, new strategy implementation bridge, and validation / pre-live scaffolding
  - synced Phase 22 next-phase prep, completion summary, TODO, checklist, doc index, and glossary terms
- Durable takeaway:
  - After Phase 22 QA, the default next move is to close the portfolio workflow development-validation phase and return to core product implementation, starting with quarterly / alternate cadence productionization.

### 2026-04-19
- Closed `Phase 22` after user checklist completion.
- Changed:
  - accepted the completed `PHASE22_TEST_CHECKLIST.md` manual QA state
  - marked `PHASE22_CURRENT_CHAPTER_TODO.md` and `PHASE22_COMPLETION_SUMMARY.md` as `phase complete / manual_validation_completed`
  - refreshed `PHASE22_NEXT_PHASE_PREPARATION.md` so it reads as a Phase 23 handoff rather than a pending QA draft
  - synced `MASTER_PHASE_ROADMAP.md` and `FINANCE_DOC_INDEX.md`
- Durable takeaway:
  - Phase 22 is now closed as portfolio workflow development validation, not as investment portfolio approval. The next default main phase is `Phase 23 Quarterly And Alternate Cadence Productionization`.

### 2026-04-19
- Advanced `Phase 23` representative quarterly smoke validation.
- Changed:
  - ran DB-backed smoke runs for `Quality / Value / Quality + Value` strict quarterly prototypes with `AAPL / MSFT / GOOG`, 2021-01-01~2024-12-31, and non-default portfolio handling contracts
  - found that common result bundle meta did not preserve `weighting_mode`, `rejected_slot_handling_mode`, `rejected_slot_fill_enabled`, and `partial_cash_retention_enabled`
  - fixed `build_backtest_result_bundle()` so portfolio handling contract meta is preserved for history / load-into-form workflows
  - created `PHASE23_QUARTERLY_CONTRACT_SMOKE_VALIDATION_FIRST_PASS.md`
  - synced Phase 23 TODO, completion summary, checklist, finance analysis, and backtest report index
- Durable takeaway:
  - quarterly strict family now passes DB-backed smoke validation for portfolio handling contract delivery and meta preservation; remaining Phase 23 validation is UI-level history / saved replay confirmation.

### 2026-04-19
- Prepared `Phase 23` for manual validation.
- Changed:
  - added quarterly portfolio handling contract fields to persisted backtest history records
  - updated history payload rebuild so `Run Again` and `Load Into Form` preserve `weighting_mode`, `rejected_slot_handling_mode`, and related flags
  - updated saved portfolio strategy overrides so `Replay Saved Portfolio` preserves quarterly rejected-slot handling semantics
  - verified result bundle meta -> history record -> history payload -> saved portfolio override roundtrip with a representative quarterly smoke bundle
  - created `PHASE23_HISTORY_AND_SAVED_REPLAY_CONTRACT_ROUNDTRIP_THIRD_WORK_UNIT.md`
  - synced Phase 23 TODO, checklist, completion summary, next-phase prep, roadmap, finance analysis, and doc index
- Durable takeaway:
  - Phase 23 code-level work is now manual-validation-ready; the remaining gate is user UI QA through `PHASE23_TEST_CHECKLIST.md`.

### 2026-04-19
- Refined `Phase 23` compare QA UX after user checklist feedback.
- Changed:
  - confirmed the Compare variant refresh issue came from `Variant` selectboxes living inside `st.form()`
  - moved `Quality / Value / Quality + Value` compare variant selectors outside the form into a dedicated `Strategy Variants` section
  - kept `Advanced Inputs > Strategy-Specific Advanced Inputs` as the detailed settings area for the currently selected variant
  - avoided the previously rejected Apply/Refresh button pattern
  - rewrote unclear Phase 23 checklist items around concrete screen locations: `Data Requirements`, `Statement Shadow Coverage Preview`, `Universe Contract`, and `Strategy Variants`
  - created `PHASE23_COMPARE_VARIANT_IMMEDIATE_REFRESH_FOURTH_WORK_UNIT.md`
- Durable takeaway:
  - Annual / Quarterly changes in Compare should now immediately refresh the lower advanced option UI without extra buttons, and the checklist is more directly testable.

### 2026-04-19
- Flattened the `Phase 23` compare input layout after follow-up UX feedback.
- Changed:
  - removed the compare `st.form()` wrapper and `Advanced Inputs` expander from the compare configuration area
  - moved `Start Date`, `End Date`, `Timeframe`, and `Option` into a shared `Compare Period & Shared Inputs` section
  - moved Annual / Quarterly variant selectors into each `Quality / Value / Quality + Value` strategy box
  - replaced strategy-level expanders with border boxes while keeping lower `Overlay`, `Portfolio Handling`, real-money, and guardrail expanders intact
  - kept a single `Run Strategy Comparison` action button and avoided the rejected Apply / Refresh pattern
  - synced the Phase 23 checklist, fourth work-unit note, TODO board, completion summary, next-phase prep, roadmap, doc index, finance analysis, and question log
- Durable takeaway:
  - Compare QA should now read as common execution inputs first, then one visible box per selected strategy, with variant selection and settings in the same box.

### 2026-04-19
- Tightened `Phase 23` compare/history QA details after checklist feedback.
- Changed:
  - wrapped strict quarterly compare `Trend Filter` and `Market Regime` inputs inside the same `Overlay` expander used by annual strict compare paths
  - kept `Portfolio Handling & Defensive Rules` as the adjacent lower expander for quarterly rejected-slot, weighting, and risk-off settings
  - changed `Back To History` after `Load Into Form` to use a panel-switch callback so the History panel is requested before the radio widget renders
  - rewrote Phase 23 checklist section 3 to explain where to verify saved compare context, saved portfolio context, history run, load-into-form, run-again, and replay saved portfolio
- Durable takeaway:
  - Quarterly compare QA now has the same top-level section rhythm as annual strict, and the checklist distinguishes history rerun from saved portfolio replay.

### 2026-04-19
- Refined the finance phase checklist writing rule after Phase 23 QA feedback.
- Changed:
  - removed the standalone `용어 기준` block from `PHASE23_TEST_CHECKLIST.md`
  - moved the relevant screen paths directly into each section 3 checkbox
  - updated `PHASE_TEST_CHECKLIST_TEMPLATE.md` so future checklists avoid separate glossary-like blocks and instead write exact UI paths inside checklist items
  - updated `FINANCE_DOC_INDEX.md` so the checklist-template entry mentions the same location-first rule
  - synced `PHASE23_CURRENT_CHAPTER_TODO.md` with the checklist wording cleanup
- Durable takeaway:
  - Future finance checklists should be action/location-first: each checkbox should say where to go and what to verify.

### 2026-04-20
- Closed `Phase 23` and opened `Phase 24`.
- Changed:
  - accepted the user's Phase 23 completion signal and marked the remaining checklist item complete
  - updated `PHASE23_CURRENT_CHAPTER_TODO.md`, `PHASE23_COMPLETION_SUMMARY.md`, and `PHASE23_NEXT_PHASE_PREPARATION.md` to `phase complete / manual_validation_completed`
  - bootstrapped `phase24` docs from the finance phase bundle helper
  - rewrote the Phase 24 plan, TODO, checklist, completion draft, next-phase draft, and first work-unit note for the new strategy expansion / research-to-implementation bridge
  - selected `Global Relative-Strength Allocation With Trend Safety Net` as the first implementation candidate because it is price-only, ETF-based, monthly, and compatible with the current DB-backed strategy infrastructure
  - synced `MASTER_PHASE_ROADMAP.md` and `FINANCE_DOC_INDEX.md`
- Durable takeaway:
  - Phase 24 is now active as a development phase for adding a new strategy family, not as an investment-performance analysis phase.

### 2026-04-20
- Ran a user-requested `GTAA` expanded-universe follow-up.
- Changed:
  - re-tested the existing compact `SPY / QQQ / GLD / IEF` `Top = 2` candidate through the latest DB date `2026-04-17`
  - added `TLT` to form a clean 6 ETF core: `SPY / QQQ / GLD / IEF / LQD / TLT`
  - found a new expanded `Top = 1`, `Interval = 8`, `1M / 3M / 6M` candidate with `21.50% CAGR`, `-6.49% MDD`, and `real_money_candidate / paper_probation / paper_only`
  - confirmed the same 6 ETF core with `Top = 2`, `Interval = 4`, `1M / 3M / 6M` remains `production_candidate / watchlist / watchlist_only`
  - documented the result in `GTAA_EXPANDED_UNIVERSE_FOLLOWUP_20260420.md` and synced the GTAA strategy hub, backtest log, report index, current candidate summary, and candidate registry
- Durable takeaway:
  - ticker breadth improved the aggressive GTAA paper candidate, but the balanced 2-holding representative remains the compact `SPY / QQQ / GLD / IEF` candidate until expanded `Top = 2` validation improves.

### 2026-04-20
- Advanced `Phase 24` first new strategy implementation.
- Changed:
  - added `Global Relative Strength` core simulation in `finance.strategy`
  - added DB-backed helper/defaults in `finance.sample`
  - added web runtime wrapper `run_global_relative_strength_backtest_from_db`
  - verified targeted `py_compile`, synthetic strategy smoke, runtime import smoke, and DB-backed smoke run
  - created `PHASE24_GLOBAL_RELATIVE_STRENGTH_CORE_RUNTIME_SMOKE_VALIDATION.md`
  - synced Phase 24 TODO, completion draft, next-phase prep, roadmap, doc index, backtest report index, and finance analysis
- Durable takeaway:
  - `Global Relative Strength` is now implemented at core/runtime level, but it is not yet exposed in `Backtest` UI, compare, history, or saved replay.

### 2026-04-20
- Reorganized the `FINANCE_COMPREHENSIVE_ANALYSIS.md` detailed implementation memo governance.
- Changed:
  - clarified that `3-3. 상세 구현 메모` is a legacy archive, not the current source of truth
  - added a management policy for where future current-state, phase, backtest, glossary, candidate, and workflow records should live
  - added a short future-record template with date, phase, category, affected area, source, and re-review condition
  - added a topic index so the long legacy memo can be searched without treating every old note as current behavior
- Durable takeaway:
  - Future finance implementation notes should not be appended indefinitely to `3-3`; new details should be routed to the correct canonical document and only summarized in the comprehensive analysis when they affect current system behavior.

### 2026-04-20
- Established the first finance code analysis documentation system.
- Changed:
  - created `.aiworkspace/note/finance/docs/architecture/` as the developer-facing place for durable code flow documents
  - added flow docs for backtest runtime, data/DB pipeline, web backtest UI, strategy implementation, and automation scripts
  - updated `FINANCE_COMPREHENSIVE_ANALYSIS.md` so it remains the high-level map and points detailed code flow readers to `docs/architecture/`
  - updated `FINANCE_DOC_INDEX.md`, `AGENTS.md`, and the active `finance-doc-sync` skill guidance to include the new code analysis update rule
- Durable takeaway:
  - Future code changes should update `docs/architecture/` only when the durable code flow changes; small copy edits, one-off results, and phase status updates should stay out of those developer flow documents.

### 2026-04-20
- Slimmed `FINANCE_COMPREHENSIVE_ANALYSIS.md` now that `docs/architecture/` exists.
- Changed:
  - reduced section 4 from detailed file-by-file code notes to a concise system layer table
  - reduced section 12 from long strategy/contract implementation history to a compact code entrypoint map
  - reduced section 18 to a short automation baseline table
  - moved durable strategy contract and runtime interpretation details into `docs/architecture/STRATEGY_IMPLEMENTATION_FLOW.md` and `docs/architecture/BACKTEST_RUNTIME_FLOW.md`
- Durable takeaway:
  - `FINANCE_COMPREHENSIVE_ANALYSIS.md` should now stay as the high-level map, while detailed developer flow should live under `.aiworkspace/note/finance/docs/architecture/`.

### 2026-04-20
- Established the first finance data architecture documentation system.
- Changed:
  - created `.aiworkspace/note/finance/data_architecture/` as the place for data flow, DB schema map, table semantics, and PIT/data-quality notes
  - moved the detailed meaning of sections 5~7 out of `FINANCE_COMPREHENSIVE_ANALYSIS.md` into dedicated data architecture documents
  - reduced `FINANCE_COMPREHENSIVE_ANALYSIS.md` sections 5~7 to high-level flow, DB, and table-semantics summaries
  - updated `FINANCE_DOC_INDEX.md`, `AGENTS.md`, and the active `finance-doc-sync` skill guidance to include the new data architecture update rule
- Durable takeaway:
  - Future DB/table/source-of-truth or PIT/data-quality meaning changes should update `data_architecture/`, while the comprehensive analysis should keep only the top-level data map.

### 2026-04-20
- Refreshed `FINANCE_COMPREHENSIVE_ANALYSIS.md` sections 8~18 using the current finance documentation set.
- Changed:
  - updated sections 8~9 from older ETF/sample-strategy framing to the current product / strategy / portfolio / pre-live layer view
  - condensed sections 10~11 into current limitation and data-quality summaries that point to `data_architecture/`
  - rewrote section 12 as a code entrypoint map that points to `docs/architecture/`
  - updated sections 13~18 to reflect the current development boundary, Phase 25 pre-live direction, future data priorities, and automation / persistence baseline
- Durable takeaway:
  - `FINANCE_COMPREHENSIVE_ANALYSIS.md` now acts as a high-level orientation map for the current product, while detailed code, DB, phase, and result records are delegated to their canonical sub-documents.

### 2026-04-20
- Tightened the update policy for `FINANCE_COMPREHENSIVE_ANALYSIS.md`.
- Changed:
  - updated `AGENTS.md` so `FINANCE_COMPREHENSIVE_ANALYSIS.md` is reviewed after finance changes but updated only when the high-level current-state map changes
  - updated `FINANCE_COMPREHENSIVE_ANALYSIS.md` and `FINANCE_DOC_INDEX.md` to state that one-off results, phase progress, detailed call flows, and table-level semantics belong in the specialized docs
  - updated the active `finance-doc-sync` skill with the same rule
- Durable takeaway:
  - `FINANCE_COMPREHENSIVE_ANALYSIS.md` should show the big picture of the current system, not absorb every implementation detail or experiment record.

### 2026-04-20
- Split the legacy detailed implementation memo out of `FINANCE_COMPREHENSIVE_ANALYSIS.md`.
- Changed:
  - moved the long former `3-3. 상세 구현 메모` into `.aiworkspace/note/finance/archive/FINANCE_COMPREHENSIVE_ANALYSIS_LEGACY_IMPLEMENTATION_NOTES_20260420.md`
  - replaced the root `3-3` section with a short archive pointer and future record-routing rule
  - updated `FINANCE_DOC_INDEX.md` and `.aiworkspace/note/finance/archive/README.md` so the archive is discoverable
- Durable takeaway:
  - `FINANCE_COMPREHENSIVE_ANALYSIS.md` is now much closer to a current-state map, while legacy implementation history remains preserved but out of the main reading path.

### 2026-04-20
- Clarified the finance product goal versus current phase boundary.
- Changed:
  - updated `FINANCE_COMPREHENSIVE_ANALYSIS.md` so the project goal is not described as merely data collection and backtesting
  - clarified that the long-term target is an evidence-based investment candidate recommendation and portfolio construction proposal program
  - updated `MASTER_PHASE_ROADMAP.md`, `AGENTS.md`, and the active `finance-doc-sync` skill to separate final product target from near-term development / validation phase execution
- Durable takeaway:
  - Strong backtest results are not automatic live recommendations, but the product being built is intended to support investment candidate and portfolio proposal workflows after sufficient validation.

### 2026-04-21
- Organized loose root finance Markdown documents into purpose-specific folders.
- Changed:
  - moved operations / runtime / registry / ingestion reference docs under `.aiworkspace/note/finance/operations/`
  - moved daily market update notes under `.aiworkspace/note/finance/operations/daily_market_update/`
  - moved research reference docs under `.aiworkspace/note/finance/researches/`
  - moved support-track discussion docs under `.aiworkspace/note/finance/support_tracks/`
  - moved the legacy backtest refinement flow guide under `.aiworkspace/note/finance/docs/architecture/`
  - updated `FINANCE_DOC_INDEX.md`, active links, and added folder README files
- Durable takeaway:
  - `.aiworkspace/note/finance/` root should now stay focused on top-level maps, active logs, glossary, and templates.

### 2026-04-21
- Standardized phase status terminology for finance roadmap/index documents.
- Changed:
  - added a `Phase 상태값 읽는 법` section to `FINANCE_DOC_INDEX.md`
  - initially normalized recent phase status labels to underscore-based canonical values such as `phase_complete / manual_validation_completed`
  - aligned the `MASTER_PHASE_ROADMAP.md` current-position status summary with the same labels
  - added `Phase Status` to `FINANCE_TERM_GLOSSARY.md`
  - updated `AGENTS.md` and the active `finance-doc-sync` skill so future phase indexes use the same status vocabulary
- Durable takeaway:
  - This was immediately refined into the split-column progress / validation model below, because that is easier to read than one combined status string.

### 2026-04-21
- Refined the phase status model to split progress status from validation status.
- Changed:
  - updated `FINANCE_DOC_INDEX.md` so the phase quick map now has separate `진행 상태`, `검증 상태`, and `다음 확인` columns
  - updated `MASTER_PHASE_ROADMAP.md` current-position summary to the same split-column model
  - updated `FINANCE_TERM_GLOSSARY.md`, `AGENTS.md`, and the active `finance-doc-sync` skill to prefer split phase status labels
  - clarified that `first_chapter_completed` is legacy partial-completion wording, not a signal to introduce a formal chapter hierarchy
- Durable takeaway:
  - Future phase management should stay phase-based, not chapter-based, and should separate work progress from QA/validation status.

### 2026-04-21
- Advanced Phase 25 from boundary definition into Pre-Live candidate record persistence.
- Changed:
  - added `.aiworkspace/plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py`
  - defined `.aiworkspace/note/finance/registries/PRE_LIVE_CANDIDATE_REGISTRY.jsonl` as the append-only Pre-Live operating-state registry
  - added `.aiworkspace/note/finance/operations/PRE_LIVE_CANDIDATE_REGISTRY_GUIDE.md`
  - added `PHASE25_PRE_LIVE_CANDIDATE_RECORD_CONTRACT_SECOND_WORK_UNIT.md`
  - updated Phase 25 plan, TODO, checklist, completion draft, next-phase draft, roadmap, doc index, comprehensive analysis, automation guide, AGENTS, and active finance-doc-sync guidance
- Validation:
  - `py_compile` passed for the new pre-live registry helper and hygiene helper
  - `manage_pre_live_candidate_registry.py validate` passes with an empty registry
  - `manage_current_candidate_registry.py validate` still passes for existing current candidate records
- Durable takeaway:
  - `CURRENT_CANDIDATE_REGISTRY.jsonl` defines the candidate; `PRE_LIVE_CANDIDATE_REGISTRY.jsonl` records how that candidate is handled before live use.

### 2026-04-21
- Advanced Phase 25 into the operator review workflow work unit.
- Changed:
  - added `PHASE25_OPERATOR_REVIEW_WORKFLOW_THIRD_WORK_UNIT.md`
  - extended `manage_pre_live_candidate_registry.py` with `draft-from-current <registry_id>`
  - mapped current candidate Real-Money signals into default Pre-Live statuses:
    `paper_probation -> paper_tracking`, `watchlist -> watchlist`, blockers -> `hold`, reject/fail signals -> `reject`, otherwise `re_review`
  - kept the workflow safe by making draft output the default and requiring `--append` for actual registry writes
  - updated Phase 25 TODO, checklist, completion draft, next-phase draft, operations guide, automation guide, doc index, comprehensive analysis, AGENTS, and active finance-doc-sync guidance
- Validation:
  - `py_compile` passed for `manage_pre_live_candidate_registry.py`
  - `draft-from-current value_current_anchor_top14_psr` outputs a valid `paper_tracking` draft
  - `draft-from-current value_lower_mdd_near_miss_pfcr` outputs a valid `watchlist` draft
- Durable takeaway:
  - Phase 25 now has a helper/report-based entry point for converting current candidates into Pre-Live operating drafts, without automatically approving or saving anything.

### 2026-04-21
- Added the Phase 25 Pre-Live Review UI entry point.
- Changed:
  - added `Pre-Live Review` as a fourth Backtest panel
  - added a current-candidate-to-Pre-Live review UI in `app/web/pages/backtest.py`
  - users can select a current candidate, review Real-Money signals, choose a Pre-Live status, edit operator reason / next action / review date, inspect the JSON draft, and save explicitly
  - saved active records are shown in the same panel's `Pre-Live Registry` tab
  - added `PHASE25_PRE_LIVE_REVIEW_UI_FOURTH_WORK_UNIT.md`
  - updated Phase 25 TODO, checklist, completion/next docs, roadmap, doc index, comprehensive analysis, Pre-Live guide, and web UI flow docs
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py` passed
  - `.venv/bin/python` import of `app.web.pages.backtest` passed
- Durable takeaway:
  - Phase 25 implementation is now ready for user manual QA. The UI still does not enable live trading; it only records pre-live operating state.

### 2026-04-21
- Clarified the Phase 25 Real-Money vs Pre-Live boundary after user QA feedback.
- Changed:
  - updated the first Phase 25 work-unit document so Pre-Live is not described as status labels only
  - defined the Pre-Live "next action record" as an action package:
    `operator_reason`, `next_action`, `review_date`, `tracking_plan.cadence`, `tracking_plan.stop_condition`, `tracking_plan.success_condition`, and supporting docs
  - updated the Phase 25 plan, Pre-Live registry guide, glossary, and checklist to say that status alone is not the distinguishing feature
- Durable takeaway:
  - `pre_live_status` can resemble Real-Money promotion / shortlist labels. The actual Pre-Live distinction is the recorded operating plan for what to check next, when to review, and when to stop or advance.

### 2026-04-21
- Closed Phase 25 after user manual QA completion.
- Changed:
  - updated Phase 25 TODO, completion summary, next-phase preparation, and checklist to `complete / manual_qa_completed`
  - synced `MASTER_PHASE_ROADMAP.md`, `FINANCE_DOC_INDEX.md`, and `FINANCE_COMPREHENSIVE_ANALYSIS.md`
  - recorded that no additional `AGENTS.md` or skill guidance change was needed at closeout because Pre-Live registry and QA closeout rules were already reflected
- Validation:
  - Phase 25 checklist was completed by the user before closeout
- Durable takeaway:
  - Phase 25 is closed as a Pre-Live operating-record workflow, not as live trading or automatic investment approval.

### 2026-04-21
- Opened Phase 26 and documented the Phase 26~30 roadmap direction.
- Changed:
  - created the Phase 26 document bundle for `Foundation Stabilization And Backlog Rebase`
  - added the first Phase 26 work-unit document for phase status and backlog rebase
  - updated `MASTER_PHASE_ROADMAP.md` with Phase 26~30:
    Phase 26 foundation stabilization, Phase 27 data integrity, Phase 28 strategy family parity, Phase 29 candidate review workflow, Phase 30 portfolio proposal / pre-live monitoring
  - updated `FINANCE_DOC_INDEX.md`, `FINANCE_COMPREHENSIVE_ANALYSIS.md`, and `FINANCE_TERM_GLOSSARY.md`
- Durable takeaway:
  - Live Readiness / Final Approval is intentionally deferred until after Phase 30. Phase 26 starts by stabilizing backlog and foundation gaps before new product expansion.

### 2026-04-21
- Completed Phase 26 implementation handoff.
- Changed:
  - added `PHASE26_BACKLOG_REBASE_AND_FOUNDATION_GAP_MAP.md`
  - reclassified Phase 8, 9, 12~15, and 18 as `complete / superseded_by_later_phase`
  - separated Phase 27 data integrity, Phase 28 strategy parity, Phase 29 candidate review, and Phase 30 portfolio proposal inputs
  - updated roadmap, doc index, glossary, comprehensive analysis, AGENTS, and active finance-doc-sync guidance for the new validation label
  - finalized the Phase 26 checklist for user QA
- Validation:
  - documentation consistency and hygiene checks are the relevant checks for this document-only phase
- Durable takeaway:
  - No old pending phase is an immediate blocker before Phase 27. Old pending checklists are now historical references or later-phase inputs, not active QA gates.

### 2026-04-22
- Clarified Phase 26 QA wording and next-phase handoff format.
- Changed:
  - replaced the ambiguous Phase 26 term `input` with user-facing wording: `다룰 주제`
  - added a short plain-language Phase 18 explanation to `PHASE26_BACKLOG_REBASE_AND_FOUNDATION_GAP_MAP.md`
  - expanded `PHASE26_NEXT_PHASE_PREPARATION.md` with a `다음 phase에서 실제로 할 작업` section for Phase 27
  - updated the phase bundle helper, checklist template, and `AGENTS.md` so future next-phase handoff docs explain both why the next phase is natural and what work it will actually do
- Durable takeaway:
  - Future next-phase preparation docs should not stop at "why next"; they should also show the concrete work the user should expect in the next phase.

### 2026-04-22
- Closed Phase 26 after user manual QA completion.
- Changed:
  - marked `PHASE26_TEST_CHECKLIST.md` final closeout items as completed
  - updated Phase 26 TODO, completion summary, next-phase preparation, roadmap, doc index, and comprehensive analysis to `complete / manual_qa_completed`
- Validation:
  - Phase 26 checklist was completed by the user before closeout
- Durable takeaway:
  - Phase 26 is closed. Phase 27 can now open as the data integrity / backtest trust layer.

### 2026-04-22
- Opened Phase 27 and implemented the first data-trust visibility unit.
- Changed:
  - created the Phase 27 document bundle for `Data Integrity And Backtest Trust Layer`
  - added `Data Trust Summary` to the latest Backtest result view
  - added requested vs actual result end, result row count, excluded ticker, malformed price row, and price freshness summary metadata to backtest result bundles
  - connected Global Relative Strength to the same price-freshness preflight used by strict annual workflows, with Korean warning copy for stale / mismatched ticker data
  - updated roadmap, document index, comprehensive analysis, code-flow notes, and data-quality notes for the new Phase 27 trust-layer behavior
- Validation:
  - `python3 -m py_compile app/web/runtime/backtest.py app/web/pages/backtest.py` passed
  - `.venv/bin/python` import of `app.web.runtime.backtest` and `app.web.pages.backtest` passed
  - `git diff --check` passed
- Durable takeaway:
  - Phase 27 starts by making backtest data boundaries visible before deeper strategy work: users should see when the requested end date, actual result end date, stale ticker data, excluded tickers, or malformed rows affect the interpretation of a run.

### 2026-04-22
- Closed Phase 27 after user manual QA completion.
- Changed:
  - marked Phase 27 TODO, completion summary, next-phase preparation, and checklist as `complete / manual_qa_completed`
  - synced `MASTER_PHASE_ROADMAP.md`, `FINANCE_DOC_INDEX.md`, and `FINANCE_COMPREHENSIVE_ANALYSIS.md`
  - kept Phase 28 handoff focused on strategy family parity, cadence completion, and family-level UX / metadata consistency
- Validation:
  - Phase 27 checklist was completed by the user before closeout
- Durable takeaway:
  - Phase 27 is closed. `Data Trust Summary`, `price_freshness`, excluded ticker details, and result-window metadata are now the baseline trust-layer concepts for later strategy family parity work.

### 2026-04-22
- Opened Phase 28 and implemented the first strategy-family parity visibility unit.
- Changed:
  - created the Phase 28 document bundle for `Strategy Family Parity And Cadence Completion`
  - added `Strategy Capability Snapshot` to `Backtest > Single Strategy`
  - added the same capability snapshot inside selected strategy boxes in `Compare & Portfolio Builder`
  - documented annual strict, quarterly prototype, Global Relative Strength, GTAA, and ETF strategy support differences
  - updated roadmap, document index, comprehensive analysis, web UI flow docs, and Phase 28 checklist draft
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py` passed
  - `.venv` candidate review note helper smoke passed
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py validate` passed
  - finance refinement hygiene check passed
  - `git diff --check` passed
- Durable takeaway:
  - Phase 28 starts by making strategy family differences visible before adding or equalizing more functionality. The current focus is "what does this strategy currently support?" rather than new strategy discovery.

### 2026-04-22
- Implemented Phase 28 history replay / load parity visibility.
- Changed:
  - added `History Replay / Load Parity Snapshot` under `Backtest > History > Selected History Run`
  - expanded new backtest history records with result-window, price freshness, excluded ticker, malformed price row, and guardrail reference metadata
  - documented the second Phase 28 work unit and synced roadmap, index, comprehensive analysis, and code-flow notes
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py app/web/runtime/history.py` passed
- Durable takeaway:
  - Phase 28 now lets users inspect whether a saved history run contains the key settings needed for `Load Into Form` or `Run Again` before pressing either action.

### 2026-04-22
- Implemented Phase 28 saved portfolio replay / load parity visibility.
- Changed:
  - added `Saved Portfolio Replay / Load Parity Snapshot` under `Backtest > Compare & Portfolio Builder > Saved Portfolios`
  - added a compact `Strategy Override Summary` for saved portfolio records
  - preserved `weights_percent` in saved portfolio replay history context
  - documented the third Phase 28 work unit and synced roadmap, index, comprehensive analysis, and code-flow notes
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py` passed
  - `.venv` saved portfolio parity helper smoke passed
- Durable takeaway:
  - Saved Portfolio is now easier to inspect before replay: users can see whether compare inputs, strategy overrides, weights, and date alignment are present before loading or rerunning.

### 2026-04-22
- Extended Phase 28 Data Trust visibility into compare, weighted portfolio, and saved replay flows.
- Changed:
  - added a `Data Trust` tab to `Strategy Comparison`
  - added a `Component Data Trust` tab to `Weighted Portfolio Result`
  - persisted strategy/component data trust rows in compare and weighted portfolio history context
  - documented the fourth Phase 28 work unit and synced roadmap, index, comprehensive analysis, and code-flow notes
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py` passed
  - `.venv` strategy data trust helper smoke passed
- Durable takeaway:
  - Compare and weighted portfolio results now expose the component data conditions behind the result, so users can distinguish performance differences from date-window or data-quality differences.

### 2026-04-23
- Completed Phase 28 Real-Money / Guardrail parity visibility.
- Changed:
  - added a `Real-Money / Guardrail` tab to Strategy Comparison
  - added `History Real-Money / Guardrail Scope` under selected history records
  - added `Saved Portfolio Real-Money / Guardrail Scope` under saved portfolio replay/load parity
  - documented the fifth Phase 28 work unit and moved Phase 28 to implementation complete / manual QA pending
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py` passed
  - `.venv` Real-Money / Guardrail parity helper smoke passed
  - `git diff --check` passed
  - finance refinement hygiene check passed
- Durable takeaway:
  - Phase 28 does not force annual strict Real-Money / Guardrail behavior onto quarterly prototype or ETF strategies. It now shows each strategy family's intended validation scope before compare, history replay, or saved portfolio replay.

### 2026-04-23
- Fixed Saved Portfolio name suggestion refresh during Phase 28 QA.
- Changed:
  - `Save This Weighted Portfolio` now derives the default portfolio name from the latest weighted portfolio strategy names and weights
  - the `Portfolio Name` input resets when the weighted portfolio strategy / weight / date alignment signature changes
  - manual name edits are preserved while the same weighted portfolio result is still active
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py` passed
  - `.venv` weighted portfolio name suggestion helper smoke passed
  - `git diff --check` passed
- Durable takeaway:
  - Saving a new weighted portfolio after rebuilding with different strategies should no longer retain the previous portfolio name by accident.

### 2026-04-23
- Closed Phase 28 after user manual QA completion.
- Changed:
  - marked the remaining Phase 28 checklist items as completed based on the user's QA completion confirmation
  - moved Phase 28 status to `complete` / `manual_qa_completed`
  - synced Phase 28 closeout summary, next-phase handoff, master roadmap, document index, and comprehensive analysis
- Validation:
  - finance refinement hygiene check passed
  - `git diff --check` passed
- Durable takeaway:
  - Phase 28 is closed. The next planned development phase is Phase 29 `Candidate Review And Recommendation Workflow`.

### 2026-04-23
- Opened Phase 29 and implemented the first Candidate Review workflow unit.
- Changed:
  - bootstrapped the Phase 29 document bundle for `Candidate Review And Recommendation Workflow`
  - added `Backtest > Candidate Review` as a dedicated panel
  - added a candidate review board for active `CURRENT_CANDIDATE_REGISTRY.jsonl` rows
  - added candidate detail inspection, suggested next step, and Pre-Live Review handoff
  - reused current candidate compare re-entry inside Candidate Review
  - synced roadmap, document index, comprehensive analysis, web UI flow docs, glossary, and README
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py` passed
  - `.venv` import smoke for candidate review helper columns passed
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py validate` passed
  - finance refinement hygiene check passed after root log sync
  - `git diff --check` passed
- Durable takeaway:
  - Phase 29 starts by making current candidates readable as review objects before sending them to compare or Pre-Live. This is a candidate review workflow, not live approval.

### 2026-04-23
- Implemented Phase 29 result-to-candidate-review handoff.
- Changed:
  - added `Candidate Review Handoff` under `Latest Backtest Run`
  - added `Review As Candidate Draft` to selected history run actions
  - added `Candidate Intake Draft` tab under `Backtest > Candidate Review`
  - candidate drafts now show suggested record type, result snapshot, Real-Money signal, data trust snapshot, and settings snapshot
  - documented the second Phase 29 work unit and synced roadmap, index, glossary, web UI flow, current candidate registry guide, and README
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py` passed
  - `.venv` helper smoke passed
- Durable takeaway:
  - Latest/history results can now be reviewed as candidate drafts without automatically writing to `CURRENT_CANDIDATE_REGISTRY.jsonl`.

### 2026-04-23
- Implemented Phase 29 Candidate Review Note workflow.
- Changed:
  - added `.aiworkspace/note/finance/registries/CANDIDATE_REVIEW_NOTES.jsonl` as the append-only target for operator candidate review decisions
  - added `Save As Candidate Review Note` under `Backtest > Candidate Review > Candidate Intake Draft`
  - added `Review Notes` tab to inspect saved candidate review notes
  - kept Candidate Review Note separate from `CURRENT_CANDIDATE_REGISTRY.jsonl`, Pre-Live approval, and investment recommendation
  - synced Phase 29 docs, roadmap, doc index, glossary, operations guide, web UI flow docs, comprehensive analysis, and README
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py` passed
  - `.venv` review note -> registry draft helper smoke passed
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py validate` passed
  - finance refinement hygiene check passed
  - `git diff --check` passed
- Durable takeaway:
  - Candidate Intake Drafts now have a safe persistence step for human review decisions without automatically promoting the draft into the current candidate registry.

### 2026-04-23
- Implemented Phase 29 Review Note to Current Candidate Registry Draft workflow.
- Changed:
  - added `Prepare Current Candidate Registry Row` under `Backtest > Candidate Review > Review Notes`
  - selected review notes can now generate editable current candidate registry row previews
  - added explicit `Append To Current Candidate Registry` action
  - disabled registry append for `Reject For Now` review notes
  - synced Phase 29 fourth work-unit docs, checklist, roadmap, doc index, glossary, guides, web UI flow docs, comprehensive analysis, and README
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py` passed
- Durable takeaway:
  - Review notes can be promoted into candidate registry rows only through an explicit preview-and-append step. This remains candidate persistence, not investment approval or live trading readiness.

### 2026-04-23
- Moved Phase 29 into implementation handoff state.
- Changed:
  - updated Phase 29 progress status to `implementation_complete`
  - kept validation status at `manual_qa_pending`
  - synced Phase 29 TODO, completion summary, next-phase preparation, checklist, master roadmap, and document index
- Durable takeaway:
  - Phase 29 implementation is complete. The next gate is user checklist QA, not Phase 30 development yet.

### 2026-04-23
- Clarified Candidate Board sample-candidate boundary for Phase 29 QA.
- Changed:
  - documented that existing Candidate Board rows are sample / seed registry candidates for workflow QA, not automatic Single Strategy selections
  - added future development note for Candidate Board maturation into a real candidate lifecycle board
  - updated Phase 29 checklist so the user can QA with the correct sample-data interpretation
- Durable takeaway:
  - Candidate Board needs later-phase refinement, especially source distinction, sample/archive handling, and safe non-automatic candidate recommendation flow.

### 2026-04-23
- Fixed Phase 29 Candidate Review -> Compare prefill for GTAA sample candidates.
- Changed:
  - added a GTAA registry `contract` -> compare override fallback for current candidate rows without explicit `compare_prefill`
  - normalized registry risk-off wording such as `cash_only_or_defensive_bond_preference` into the executable GTAA mode `defensive_bond_preference`
  - updated Phase 29 checklist / TODO / handoff docs and the Backtest UI flow code analysis note
  - reviewed `FINANCE_DOC_INDEX.md`; no index update was needed because no new document was introduced
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py` passed
  - `.venv` smoke confirmed both GTAA recommended and lower-MDD registry rows now produce compare prefill payloads
- Durable takeaway:
  - The previous warning was not a user-actionable issue. GTAA seed candidates now have a usable Compare re-entry path through their stored registry contract.

### 2026-04-28
- Closed Phase 29 after user manual QA completion.
- Changed:
  - marked remaining Phase 29 checklist items as completed based on user QA completion confirmation
  - moved Phase 29 status to `complete` / `manual_qa_completed`
  - synced Phase 29 TODO, completion summary, next-phase preparation, master roadmap, doc index, and comprehensive analysis
  - recorded that Phase 30 should start with product-flow reorientation and `backtest.py` module-boundary planning before new portfolio proposal implementation
- Validation:
  - `git diff --check` passed
- Durable takeaway:
  - Phase 29 is closed. The next step is not immediate feature expansion; it is to make the post-Phase-29 operating flow understandable and plan a gradual Backtest UI refactor boundary.

### 2026-04-28
- Opened Phase 30 and completed the first product-flow / refactor-boundary work unit.
- Changed:
  - bootstrapped the Phase 30 document bundle for `Portfolio Proposal And Pre-Live Monitoring Surface`
  - updated the main Guide's `테스트에서 상용화 후보 검토까지 사용하는 흐름` to the post-Phase-29 flow:
    Data Trust -> Single Strategy -> Real-Money Signal -> Compare -> Candidate Draft -> Candidate Review Note -> Current Candidate Registry -> Candidate Board / Pre-Live -> Portfolio Proposal -> Live Readiness
  - documented the `backtest.py` refactor boundary in `BACKTEST_UI_FLOW.md` and the Phase 30 first work-unit note
  - synced Phase 30 status in roadmap, document index, comprehensive analysis, TODO, completion summary, and checklist draft
- Validation:
  - `python3 -m py_compile app/web/streamlit_app.py app/web/pages/backtest.py` passed
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py` passed after root logs were reviewed and updated
  - `git diff --check` passed
- Durable takeaway:
  - Phase 30 is active, but not yet in Portfolio Proposal implementation. The first completed unit makes the user flow understandable again and sets a conservative boundary for future `backtest.py` module extraction.

### 2026-04-28
- Completed the second Phase 30 work unit: Portfolio Proposal contract definition.
- Changed:
  - added `.aiworkspace/note/finance/phases/phase30/PHASE30_PORTFOLIO_PROPOSAL_CONTRACT_SECOND_WORK_UNIT.md`
  - defined the minimum proposal row contract: objective, component candidates, proposal roles, target weights, risk constraints, evidence snapshot, open blockers, and operator decision
  - proposed `.aiworkspace/note/finance/registries/PORTFOLIO_PROPOSAL_REGISTRY.jsonl` as a future append-only storage location without creating the file or implementing append behavior yet
  - updated Phase 30 TODO, checklist, completion summary, roadmap, doc index, glossary, web UI flow docs, and comprehensive analysis
- Validation:
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py` passed
  - `git diff --check` passed
  - Playwright browser smoke confirmed the `Pre-Live Feedback` tab renders under `Backtest > Portfolio Proposal`
- Durable takeaway:
  - Phase 30 can now move toward either Proposal UI / persistence or a small Backtest UI module split with a clearer definition of what a Portfolio Proposal is.

### 2026-04-28
- Completed the third Phase 30 work unit: registry JSONL I/O helper split.
- Changed:
  - added `app/web/runtime/candidate_registry.py`
  - moved current candidate registry, candidate review note, and pre-live registry JSONL read / append helpers out of `app/web/pages/backtest.py`
  - exported the helper functions and registry path constants from `app/web/runtime/__init__.py`
  - kept Candidate Review UI, Pre-Live UI, compare prefill behavior, row schemas, file paths, append-only behavior, and Streamlit session state keys unchanged
  - synced Phase 30 TODO, checklist, completion summary, plan, roadmap, doc index, comprehensive analysis, and web UI flow docs
- Validation:
  - `python3 -m py_compile app/web/runtime/candidate_registry.py app/web/runtime/__init__.py app/web/pages/backtest.py` passed
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py validate` passed
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py validate` passed
  - `.venv/bin/python` import smoke for current candidate / pre-live / review note loaders passed
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py` passed
  - `git diff --check` passed
- Durable takeaway:
  - This is the first actual `backtest.py` code split in Phase 30, but it is intentionally narrow: registry I/O only. Candidate Review / Pre-Live display logic remains in `backtest.py` for later targeted refactors.

### 2026-04-28
- Completed the fourth Phase 30 work unit: Portfolio Proposal Draft UI / persistence.
- Changed:
  - added `app/web/runtime/portfolio_proposal.py`
  - exported proposal registry helpers from `app/web/runtime/__init__.py`
  - added `Backtest > Portfolio Proposal` with `Create Proposal Draft` and `Proposal Registry` tabs
  - allowed current candidates to be grouped into a proposal draft with objective, proposal type, status, candidate roles, target weights, weight reasons, blocker checks, and operator decision
  - added `.aiworkspace/note/finance/operations/PORTFOLIO_PROPOSAL_REGISTRY_GUIDE.md`
  - synced Phase 30 TODO, checklist, completion summary, plan, next-phase prep, roadmap, doc index, glossary, comprehensive analysis, web UI flow docs, and README
- Validation:
  - `python3 -m py_compile app/web/runtime/portfolio_proposal.py app/web/runtime/__init__.py app/web/pages/backtest.py` passed
  - `.venv/bin/python` import smoke for proposal registry path / append helper / loader passed
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py validate` passed
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py validate` passed
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py` passed
  - `git diff --check` passed
- Durable takeaway:
  - Phase 30 now has the first implemented Portfolio Proposal draft surface. It remains proposal-draft persistence only, not live approval, optimizer output, or order instruction.

### 2026-04-28
- Completed the fifth Phase 30 work unit: Portfolio Proposal Monitoring Review.
- Changed:
  - added `Backtest > Portfolio Proposal > Monitoring Review`
  - added monitoring summary rows for saved proposal drafts
  - added selected proposal detail review with objective, construction, component monitoring, blockers, review gaps, operator decision, and JSON inspect
  - defined `blocked`, `needs_review`, and `review_ready` as monitoring summary states, not live approval states
  - synced Phase 30 TODO, checklist, completion summary, plan, next-phase prep, roadmap, doc index, glossary, comprehensive analysis, web UI flow docs, operations guide, and README
- Validation:
  - `python3 -m py_compile app/web/runtime/portfolio_proposal.py app/web/runtime/__init__.py app/web/pages/backtest.py` passed
  - `.venv/bin/python` smoke for proposal monitoring helper functions passed
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py validate` passed
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py validate` passed
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py` passed
  - `git diff --check` passed
- Durable takeaway:
  - Phase 30 proposal drafts can now be saved and then reviewed as monitoring objects. This still does not approve live trading, create orders, or optimize portfolio weights.

### 2026-04-28
- Completed the sixth Phase 30 work unit: Portfolio Proposal Pre-Live Feedback.
- Changed:
  - added `Backtest > Portfolio Proposal > Pre-Live Feedback`
  - compared proposal saved Pre-Live snapshots with current active Pre-Live registry records
  - added component-level saved/current Pre-Live status, status drift, review overdue, tracking cadence, and current next action readouts
  - added feedback gap detection for missing active Pre-Live records, status drift, hold/reject/re-review with active weight, and overdue review dates
  - synced Phase 30 TODO, checklist, completion summary, plan, next-phase prep, roadmap, doc index, glossary, comprehensive analysis, web UI flow docs, operations guide, and README
- Validation:
  - `python3 -m py_compile app/web/runtime/portfolio_proposal.py app/web/runtime/__init__.py app/web/pages/backtest.py` passed
  - `.venv/bin/python` smoke for Pre-Live feedback helper functions passed
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py validate` passed
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py validate` passed
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py` passed
  - `git diff --check` passed
- Durable takeaway:
  - Portfolio Proposal can now be checked against the current Pre-Live operating state without mutating proposal rows or Pre-Live records.

### 2026-04-28
- Completed the seventh Phase 30 work unit: Portfolio Proposal Paper Tracking Feedback.
- Changed:
  - added `Backtest > Portfolio Proposal > Paper Tracking Feedback`
  - compared proposal saved evidence snapshots with current active Pre-Live `result_snapshot` metrics
  - added component-level saved/current CAGR, saved/current MDD, delta, performance signal, tracking cadence, stop condition, and success condition readouts
  - added feedback gap detection for missing active Pre-Live records, non-`paper_tracking` status, missing saved/current metrics, CAGR / MDD deterioration, and missing tracking cadence
  - moved Phase 30 to `implementation_complete` / `manual_qa_pending`
  - synced Phase 30 TODO, checklist, completion summary, plan, next-phase prep, roadmap, doc index, glossary, comprehensive analysis, web UI flow docs, operations guide, and README
- Validation:
  - `python3 -m py_compile app/web/runtime/portfolio_proposal.py app/web/runtime/__init__.py app/web/pages/backtest.py` passed
  - `.venv/bin/python` smoke for Paper Tracking Feedback helper functions passed
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py validate` passed
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py validate` passed
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py` passed
  - `git diff --check` passed
  - Playwright browser smoke confirmed `Backtest > Portfolio Proposal > Paper Tracking Feedback` renders; existing Streamlit subpath `_stcore` 404 console messages were observed
- Durable takeaway:
  - Phase 30 product functionality is now ready for user manual QA. Additional `backtest.py` module splitting is intentionally deferred to a separate special refactor task.

### 2026-04-28
- Refined the Reference guide's `테스트에서 상용화 후보 검토까지 사용하는 흐름` after user direction.
- Changed:
  - kept the guide as an 11-step product/user flow instead of expanding Phase 30 into many implementation steps
  - updated step 11 from future-oriented `Phase 30 이후` wording to the implemented `Backtest > Portfolio Proposal` path
  - framed Monitoring Review, Pre-Live Feedback, and Paper Tracking Feedback as checks inside the Portfolio Proposal step, not separate major workflow steps
- Durable takeaway:
  - The guide now reflects Phase 30 at the correct level of abstraction: a portfolio proposal review step before future Live Readiness / Final Approval, not a list of Phase 30 work-unit details.

### 2026-04-28
- Started Phase 30 manual walkthrough support for the 1~11 guide flow.
- Verified current candidate registry and reran the GTAA Balanced Top-2 candidate through `run_gtaa_backtest_from_db`.
- Selected `gtaa_real_money_balanced_top2_ief_20260418` as the first practice portfolio candidate because current runtime shows `Promotion=real_money_candidate`, `Shortlist=paper_probation`, `Probation=paper_tracking`, `Deployment=paper_only`, `Validation=normal`, `ETF Operability=normal`, and no blockers.
- No code changes were made; this was an operator-flow analysis and QA handoff step.

### 2026-04-28
- Added a user-facing Guide section for reading GTAA Risk-Off candidates.
- Changed:
  - added `Reference > Guides > GTAA Risk-Off 후보군 보는 법`
  - explained that `Defensive Tickers` do not expand the GTAA universe by themselves
  - documented that only the intersection of GTAA Tickers and Defensive Tickers can become usable defensive fallback candidates
  - added the current GTAA Balanced Top-2 example where `IEF` is the only usable defensive fallback candidate
  - updated the Phase 30 checklist so this Guide section is included in manual QA
- Durable takeaway:
  - The walkthrough now has an explicit explanation for why `TLT / LQD / BIL` are not active fallback candidates unless they are also included in the GTAA universe.

### 2026-04-28
- Added an explicit Guide rule for passing from step 4 to step 5 in the 1~11 workflow.
- Changed:
  - added `4단계에서 5단계로 넘어가는 최소 기준` under `Reference > Guides > 테스트에서 상용화 후보 검토까지 사용하는 흐름`
  - documented the minimum Compare-entry criteria as `Promotion Decision != hold`, `Deployment != blocked`, and no unresolved core blocker
  - clarified that this is a Compare-entry criterion, not live trading approval
  - synced the Phase 30 checklist, current TODO, doc index, work log, and question log
- Durable takeaway:
  - Operators can now decide whether a candidate has cleared Hold resolution and can move to Compare without treating the signal as final investment approval.

### 2026-04-28
- Added a Real-Money next-step readiness surface for the 1~11 workflow.
- Changed:
  - added `5단계 Compare 진입 평가` to `Real-Money > 현재 판단`
  - scored Compare-entry readiness out of 10 from Promotion Decision, Deployment Readiness, and Core Blocker status
  - displayed the verdict, next action, progress bar, blocking reasons, review reasons, and score calculation table
  - synced Phase 30 checklist, current TODO, web backtest UI flow, work log, and question log
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py app/web/streamlit_app.py` passed
  - GTAA Balanced Top-2 smoke evaluation returned `8.5 / 10` and `5단계 Compare 진행 가능`
- Durable takeaway:
  - Real-Money now gives an explicit Compare-entry signal before the operator digs into detailed checklist rows.

### 2026-04-29
- Clarified the Real-Money Compare-entry readiness score threshold.
- Changed:
  - added UI copy explaining that `8.0 / 10` is a clean Compare-entry pass
  - clarified that below `8.0 / 10` can still proceed conditionally when the three core criteria pass
  - synced the web backtest UI flow and question log
- Durable takeaway:
  - The score now reads as an operator aid, while the actual stop/go gate remains Promotion non-hold, Deployment non-blocked, and no core blocker.

### 2026-04-29
- Reorganized the Reference guide layout after manual QA feedback.
- Changed:
  - moved `4단계에서 5단계로 넘어가는 최소 기준` out of `테스트에서 상용화 후보 검토까지 사용하는 흐름`
  - added a separate `Reference > Guides > 단계 통과 기준` section for stop/go criteria
  - kept the 1~11 workflow section as a pure step-by-step guide that starts directly at 1단계
  - synced the Phase 30 checklist, current TODO, doc index, work log, and question log
- Durable takeaway:
  - Stage flow guidance and stage pass criteria are now separated, so operators can read the workflow first and consult criteria only when deciding whether to move forward.

### 2026-04-29
- Corrected the documentation scope for the 1~11 walkthrough support session.
- Changed:
  - removed session-specific GTAA Risk-Off, 4->5 pass, and Real-Money readiness checklist items from the Phase 30 QA checklist / TODO
  - created `.aiworkspace/note/finance/operations/BACKTEST_1_TO_11_WALKTHROUGH_SESSION.md` as the separate home for practice questions, candidate examples, and walkthrough-specific UI notes
  - updated the finance doc index and operations README so the walkthrough session is discoverable outside the phase docs
- Durable takeaway:
  - Phase documents should not absorb ad hoc practice-session guidance unless the user explicitly asks to change that phase's QA scope.

### 2026-04-29
- Clarified the correct step-5 Compare path for a new strategy in the walkthrough session.
- Changed:
  - documented that `Candidate Review > Send To Compare` and `Load Recommended Candidates` are registry quick re-entry tools, not the first path for a new unregistered strategy
  - added the direct `Backtest > Compare & Portfolio Builder` path for recreating the single-run contract in Compare
  - noted the current same-family compare limitation and the need to use benchmark / alternative family comparisons first
- Durable takeaway:
  - Step 5 starts from the tested strategy contract itself; registry shortcuts are only for candidates that already exist in current candidate registry.

### 2026-04-29
- Added a Compare-to-Candidate-Draft readiness surface for the 1~11 walkthrough.
- Changed:
  - added `6단계 Candidate Draft 진입 평가` to Compare results
  - scored the selected compare candidate out of 10 from Compare Run, Data Trust, Real-Money Gate, and Relative Evidence
  - added a direct `Send Selected Strategy To Candidate Draft` button for pass / conditional pass cases
  - documented the GTAA Balanced Top-2 compare test setup in the walkthrough session
  - synced the web backtest UI flow, work log, and question log without touching Phase 30 QA docs
- Durable takeaway:
  - Step 5 now has a visible stop/go signal for entering step 6, mirroring the earlier 4->5 readiness box.

### 2026-04-29
- Ran a runtime smoke for the walkthrough's step-5 Compare setup.
- Result:
  - compared GTAA Balanced Top-2, Equal Weight same universe, Global Relative Strength same universe, and Risk Parity Trend default universe
  - GTAA Balanced Top-2 remained the strongest candidate in the smoke run with CAGR 17.88% and MDD -8.39%
  - the new Candidate Draft readiness evaluation returned `9.0 / 10` and `6단계 Candidate Draft 조건부 진행 가능`
- Durable takeaway:
  - The walkthrough now has a concrete compare set and expected smoke result for the user's manual test.

### 2026-04-29
- Reorganized the Reference Guides page for the 1~11 walkthrough support session.
- Changed:
  - grouped Real-Money promotion, Real-Money Contract, and GTAA Risk-Off explanations under `핵심 개념 가이드`
  - made each 1~11 workflow step an expander under `1~11 단계 실행 흐름`
  - made 4->5 and 5->6 pass criteria expanders under `단계 통과 기준`
  - refreshed the `지금 먼저 보면 좋은 문서` and file path list to point at current operations / code analysis / registry docs instead of older Phase 12/13 checklists
  - synced the walkthrough operations note and web backtest UI flow doc without touching Phase 30 QA docs
- Validation:
  - `.venv/bin/python -m py_compile app/web/streamlit_app.py` passed
- Durable takeaway:
  - Guides now separates core concepts, ordered workflow, stop/go criteria, and reference files so the walkthrough can be followed without mixing practice notes into phase QA docs.

### 2026-04-29
- Clarified interval / rebalance interval semantics after walkthrough feedback.
- Changed:
  - added a Guides expander explaining that `option=month_end` makes interval values row cadence, not week counts
  - clarified `1 = monthly / roughly 4 weeks`, `4 = every fourth month-end row`, and `12 = annual`
  - updated Equal Weight input help text in single and compare forms
  - updated the walkthrough note to explain why the GTAA smoke used `Rebalance Interval = 4` and when Equal Weight should use `1`
- Durable takeaway:
  - Operators should use `Rebalance Interval = 1` for a literal monthly / roughly 4-week Equal Weight benchmark under `month_end`; `4` only matches the existing GTAA candidate's slower cadence.

### 2026-04-29
- Split Compare Candidate Draft score from Data Trust gate warnings.
- Changed:
  - removed the hard `6.4 / 10` score cap from the `6단계 Candidate Draft 진입 평가`
  - changed short actual-end / requested-end mismatches into `Data Trust WARNING` instead of a score-capping blocker
  - added a visible `Data Trust` gate metric beside `Draft Score`
  - kept true blocking cases, such as price freshness error or a result period gap over 31 days, as `Data Trust BLOCKED`
  - synced the walkthrough note, web backtest UI flow doc, and Guides pass-criteria copy
- Durable takeaway:
  - Draft Score now reflects compare evidence, while Data Trust tells the operator whether the evidence is clean, warning-level, or blocked.

### 2026-04-29
- Added comparator-selection guidance for the 1~11 walkthrough.
- Changed:
  - added `Reference > Guides > Compare 대상 선정법`
  - documented meaningful comparator roles: naive baseline, market benchmark, adjacent alternative, risk baseline, and existing strong candidate
  - clarified in the walkthrough that Compare is only useful when the comparator set can explain whether the candidate deserves to remain
  - synced the web backtest UI flow doc and question log
- Durable takeaway:
  - Step 5 is not just "run any comparison"; it is the step where the operator chooses defensible comparator roles and checks whether the candidate still has a reason to proceed.

### 2026-04-29
- Added a concrete comparator-selection example for the GTAA walkthrough.
- Changed:
  - added a `GTAA Balanced Top-2` scenario table under `Reference > Guides > Compare 대상 선정법`
  - mirrored the same example in `.aiworkspace/note/finance/operations/BACKTEST_1_TO_11_WALKTHROUGH_SESSION.md`
  - clarified what each comparator tests and what a pass interpretation would look like
- Durable takeaway:
  - Operators now have both comparator categories and a concrete GTAA example for deciding what "meaningful Compare" means before moving to Candidate Draft.

### 2026-04-29
- Combined Candidate Draft intake and Review Note save into one user-facing step.
- Changed:
  - updated `Candidate Review > Candidate Intake Draft` copy to present step 6 as `Candidate Intake & Review Note 저장`
  - added a `6단계 Intake 저장 준비` readiness box that checks candidate identity/source, result snapshot, Data Trust, Real-Money signal, settings snapshot, and operator reason / next action
  - disabled `Save Candidate Review Note` until the intake readiness check passes
  - redefined Guides steps so step 7 is now Review Notes registry-candidate decision and step 8 remains explicit current candidate registry append
  - synced the walkthrough session note and web backtest UI flow doc without touching Phase 30 QA docs
- Durable takeaway:
  - Candidate Draft 확인과 Review Note 저장은 one-step intake workflow이고, registry append는 still a separate explicit decision.

### 2026-04-29
- Added step-7 registry scope gating for saved Candidate Review Notes.
- Changed:
  - added `7단계 Registry 후보 범위 판단` in `Backtest > Candidate Review > Review Notes`
  - classified saved Review Notes into Current Candidate / Near Miss / Scenario / Stop before registry append
  - disabled append when the selected Record Type does not match the step-7 scope
  - preserved compare readiness evidence in Candidate Review Notes and copied it into registry review context
  - synced Guides, walkthrough session notes, and web backtest UI flow without touching Phase 30 QA docs
- Durable takeaway:
  - Step 7 now decides how far a saved Review Note can travel; only a matched scope proceeds to explicit step-8 registry append.

### 2026-04-29
- Merged the previous step-7 scope decision and step-8 registry append into one user-facing step.
- Changed:
  - updated Guides so step 7 is `Current Candidate Registry에 남길 범위 결정 및 저장`
  - removed the separate step that treated `Append To Current Candidate Registry` as its own user-facing stage
  - renumbered Candidate Board / Pre-Live / Portfolio Proposal to follow the merged registry step
  - updated Candidate Review copy so append is presented as the save action inside step 7
  - synced walkthrough and web backtest UI flow docs without touching Phase 30 QA docs
- Durable takeaway:
  - Button-level persistence actions should stay inside the broader decision step instead of becoming standalone workflow stages.

### 2026-04-29
- Added duplicate-safe registry append and step-8 Candidate Board operating readiness.
- Changed:
  - confirmed repeated `Append To Current Candidate Registry` clicks were appending duplicate revisions for the same Review Note while the Board showed only the latest `registry_id` row
  - added a Review Notes duplicate guard that disables append for an already saved Review Note unless the operator explicitly checks a new-revision override
  - added `8단계 Candidate Board 운영 판단` with `PRE_LIVE_READY`, `COMPARE_REVIEW_READY`, and `BOARD_HOLD` routes
  - added route actions to open a ready current candidate in Pre-Live Review or open the Compare picker for near-miss / scenario candidates
  - synced Guides, walkthrough session notes, and web backtest UI flow docs without touching Phase 30 QA docs
- Durable takeaway:
  - Step 8 is a route-reading step: only `PRE_LIVE_READY` moves to Pre-Live; compare-ready alternatives return to Compare instead of being treated as failures.

### 2026-04-29
- Merged the former 6 / 7 / 8 user-facing steps into one Candidate Packaging step.
- Changed:
  - reframed Candidate Review as `6단계 Candidate Packaging` instead of separate Draft / Registry / Board workflow steps
  - updated Compare handoff copy to `Send Selected Strategy To Candidate Packaging`
  - renamed the intake, registry, and board readiness boxes to `Candidate Packaging 저장 준비`, `Registry 후보 범위 판단`, and `Candidate Packaging 종합 판단`
  - reduced Guides from 1~10 to 1~8 steps: 6 Candidate Packaging, 7 Pre-Live Review, 8 Portfolio Proposal
  - synced the walkthrough session note and web backtest UI flow doc without touching Phase 30 QA docs
- Durable takeaway:
  - Candidate Packaging is not a new quant validation layer; it is one packaging gate that turns a compared candidate into a machine-readable, Pre-Live-ready operating candidate.

### 2026-04-29
- Refactored the Candidate Review UX into one sequential Candidate Packaging flow.
- Changed:
  - removed the primary `Candidate Board / Candidate Intake Draft / Review Notes / Inspect Candidate / Send To Compare` tab workflow from `Backtest > Candidate Review`
  - rebuilt the screen as `1. Draft 확인 / Review Note 저장`, `2. Registry 저장`, `3. Pre-Live 진입 평가`
  - kept the existing manual save buttons and readiness gates, but placed them in the order a user actually follows after step-5 Compare
  - moved saved board and compare re-entry into lower auxiliary expanders
  - synced Guides, walkthrough notes, and the web backtest UI flow doc without touching Phase 30 QA docs
- Durable takeaway:
  - Candidate Review is now a single operator flow, not a collection of tabs that force the user to discover the workflow order.

### 2026-04-29
- Improved the handoff from Candidate Packaging registry save to Pre-Live route evaluation.
- Changed:
  - added `registry_id` to current candidate selection labels so repeated GTAA / same-title candidates can be distinguished
  - after `Append To Current Candidate Registry`, stored the appended row's `registry_id` and `revision_id` in session state
  - auto-selected the just-appended row in `3. Pre-Live 진입 평가`
  - added a visible "방금 저장한 후보" summary card with Registry ID, Revision ID, Source Review Note, and Recorded At
  - synced the walkthrough session note and web backtest UI flow doc
- Durable takeaway:
  - The operator no longer has to guess which candidate in the Packaging selectbox came from the immediately preceding registry append.

### 2026-04-29
- Extracted the Candidate Review render flow from `backtest.py`.
- Changed:
  - added `app/web/pages/backtest_candidate_review.py`
  - moved the `Candidate Review` / `Candidate Packaging` screen render logic into the new module
  - kept `_render_candidate_review_workspace()` in `backtest.py` as a thin wrapper so panel routing remains unchanged
  - left shared helpers and registry conversion helpers in `backtest.py` for this first behavior-preserving split
  - synced the web backtest UI flow document
- Durable takeaway:
  - Candidate Review can now be edited from a focused module before adding more Pre-Live workflow work.

### 2026-04-29
- Split Candidate Review render code from Candidate Review helper logic.
- Changed:
  - added `app/web/pages/backtest_candidate_review_helpers.py`
  - moved Candidate Review readiness evaluation, Review Note conversion, registry row conversion, and display helper functions out of `backtest.py`
  - changed `app/web/pages/backtest_candidate_review.py` to import helper logic directly instead of aliasing helper functions from `backtest.py`
  - kept cross-panel handoff functions such as current-candidate compare prefill in `backtest.py` for now
  - synced README, comprehensive analysis, and web backtest UI flow docs
- Verification:
  - `.venv/bin/python -m py_compile app/web/pages/backtest.py app/web/pages/backtest_candidate_review.py app/web/pages/backtest_candidate_review_helpers.py` passed
  - Streamlit smoke checked `Backtest > Candidate Review` on localhost and confirmed the Candidate Packaging screen renders
- Durable takeaway:
  - Candidate Review now has a clearer two-file boundary: render in `backtest_candidate_review.py`, 판단 / 변환 / scoring helper in `backtest_candidate_review_helpers.py`.

### 2026-04-29
- Added repository guidance for script responsibility mapping and function-purpose comments.
- Changed:
  - updated `AGENTS.md` so agents check `.aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md` and the matching code analysis flow doc before finance code edits
  - added `.aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md` as the quick script responsibility map
  - updated `docs/architecture/README.md` and `FINANCE_DOC_INDEX.md` to point future code work to the new map
  - added a function documentation rule for new non-trivial domain / workflow / persistence / scoring helpers
- Durable takeaway:
  - Future finance code changes should keep script responsibility documentation current when modules are added, moved, split, or materially repurposed.

### 2026-04-30
- Refactored the Pre-Live Review UX into a sequential step-7 operating check.
- Changed:
  - removed the primary `Create From Current Candidate / Pre-Live Registry` tab workflow from `Backtest > Pre-Live Review`
  - rebuilt the screen as `1. 운영 후보 확인`, `2. 운영 상태 / 추적 계획 결정`, `3. Portfolio Proposal 진입 평가`, `4. 저장 및 다음 단계`
  - added a 10-point Portfolio Proposal readiness evaluation with route labels such as `PORTFOLIO_PROPOSAL_READY`, `WATCHLIST_ONLY`, `PRE_LIVE_HOLD`, `REJECTED`, and `SCHEDULED_REVIEW`
  - preserved direct Pre-Live entry while auto-selecting candidates opened from Candidate Packaging
  - moved saved Pre-Live registry inspection into a lower auxiliary expander
  - moved Candidate Review render/helper modules outside `app/web/pages/` to avoid Streamlit exposing them as standalone pages
- Verification:
  - `.venv/bin/python -m py_compile app/web/pages/backtest.py app/web/backtest_candidate_review.py app/web/backtest_candidate_review_helpers.py app/web/streamlit_app.py` passed
  - Streamlit smoke checked `Backtest > Pre-Live Review` and confirmed the sequential step-7 screen renders with the new readiness box
- Durable takeaway:
  - Pre-Live Review is now an operating-state decision step, not a tabbed persistence utility.

### 2026-04-30
- Clarified candidate-specific Pre-Live status recommendation vs operator final decision.
- Changed:
  - renamed the step-7 status metric to `System Suggested Status`
  - renamed the saved selectbox to `Operator Final Status`
  - added a visible recommendation reason derived from the selected current candidate's Real-Money signal and blockers
  - added a warning when the operator intentionally chooses a final status different from the system suggestion
  - synced the web backtest UI flow document
- Durable takeaway:
  - Pre-Live status is still operator-controlled, but the UI now makes the candidate-specific system recommendation and the saved human decision visibly separate.

### 2026-04-30
- Extracted the Pre-Live Review render flow and helper logic from `backtest.py`.
- Changed:
  - added `app/web/backtest_pre_live_review.py` for the `Backtest > Pre-Live Review` sequential step-7 UI
  - added `app/web/backtest_pre_live_review_helpers.py` for status suggestion, draft conversion, readiness scoring, and registry display helpers
  - kept `backtest.py` as the Backtest panel router with a thin Pre-Live wrapper
  - preserved the existing Pre-Live registry runtime helper and session-state keys
  - synced README, comprehensive analysis, script structure map, and web backtest UI flow docs
- Durable takeaway:
  - Candidate Review and Pre-Live Review now follow the same render/helper module split pattern, lowering the cost of future 7단계 workflow edits.

### 2026-04-30
- Improved Pre-Live Review summary readability on narrow screens.
- Changed:
  - replaced long-string `st.metric` blocks in Pre-Live Review with wrapping status cards
  - applied the card layout to the top summary and the step-2 Promotion / Shortlist / Deployment / System Suggested Status signals
  - kept the underlying Pre-Live scoring, draft, registry, and session-state behavior unchanged
- Durable takeaway:
  - Long candidate status strings no longer collapse into ellipses in the main Pre-Live Review signal summary.

### 2026-04-30
- Improved long route/readiness labels in Candidate Review and Pre-Live Review.
- Changed:
  - added `app/web/backtest_ui_components.py` with shared wrapping status cards and a route/readiness panel
  - replaced `st.metric` route summaries in `Candidate Review > Pre-Live 진입 평가` and `Pre-Live Review > Portfolio Proposal 진입 평가`
  - preserved the existing progress bars, criteria tables, route decisions, and button gating
  - synced README, comprehensive analysis, script structure map, and web backtest UI flow docs
- Durable takeaway:
  - Route labels such as `PORTFOLIO_PROPOSAL_READY` and `PRE_LIVE_READY` now wrap inside a decision panel instead of being truncated.

### 2026-04-30
- Cleaned up the Backtest page shell and navigation.
- Changed:
  - removed the duplicate in-page `Backtest` heading under the top-level Backtest page title
  - changed the visible Backtest navigation from a six-item radio list to a Streamlit segmented workflow selector
  - kept the main workflow focused on `Single Strategy -> Compare & Portfolio Builder -> Candidate Review -> Pre-Live Review -> Portfolio Proposal`
  - moved `History` out of the main workflow navigation and exposed it as a `Run History` utility button while preserving existing History behavior and handoff routes
  - synced README, comprehensive analysis, script structure map, and web backtest UI flow docs
- Verification:
  - `.venv/bin/python -m py_compile app/web/pages/backtest.py app/web/streamlit_app.py app/web/backtest_ui_components.py app/web/backtest_candidate_review.py app/web/backtest_pre_live_review.py` passed
  - Streamlit smoke checked `/backtest`, confirmed the duplicate title is gone, the segmented workflow renders, `Run History` opens the history surface, and selecting a workflow panel returns to that panel
- Durable takeaway:
  - History remains available for replay and candidate handoff, but it is no longer presented as a core step in the candidate review workflow.

### 2026-04-30
- Moved Backtest run history into the Operations navigation.
- Changed:
  - added `app/web/backtest_history.py` as the `Operations > Backtest Run History` page shell
  - added a new `Backtest Run History` page under the `Operations` top navigation group
  - removed the visible `Run History` button and hidden History panel route from the Backtest workflow selector
  - kept the Backtest workflow focused on `Single Strategy -> Compare & Portfolio Builder -> Candidate Review -> Pre-Live Review -> Portfolio Proposal`
  - preserved history actions: `Load Into Form`, `Run Again`, and `Review As Candidate Draft` now switch back into the Backtest workflow after preparing the relevant session state
  - updated Candidate Review copy to point to `Operations > Backtest Run History`
  - synced README, comprehensive analysis, script structure map, and web backtest UI flow docs
- Verification:
  - `.venv/bin/python -m py_compile app/web/streamlit_app.py app/web/backtest_history.py app/web/pages/backtest.py app/web/backtest_candidate_review.py` passed
  - Streamlit smoke checked the top navigation: `Operations > Backtest Run History` renders the persistent backtest history surface, and `Backtest` no longer shows a Run History utility button
- Durable takeaway:
  - Backtest is now visually reserved for candidate-building workflow, while persisted backtest history is treated as an Operations audit / replay surface.

### 2026-04-30
- Completed the second Backtest Run History module split.
- Changed:
  - moved the persistent history inspector, selected-record detail view, replay parity snapshot, and History action buttons into `app/web/backtest_history.py`
  - added `app/web/backtest_history_helpers.py` for history table rows, replay payload reconstruction, field parity summaries, and Real-Money / Guardrail scope helper tables
  - removed the moved history render/helper bodies from `app/web/pages/backtest.py`
  - kept actual backtest rerun execution delegated to `backtest.py` so History does not own strategy runtime behavior
  - synced script structure and web backtest UI flow docs
- Verification:
  - `python3 -m py_compile app/web/backtest_history.py app/web/backtest_history_helpers.py app/web/pages/backtest.py app/web/streamlit_app.py` passed
  - `uv run python` import smoke confirmed `backtest_history_helpers`, `backtest_history`, and the Backtest parity renderer import load correctly
- Durable takeaway:
  - `backtest.py` is now shorter by the History inspector/replay helper block, and future Run History edits should start in `app/web/backtest_history.py` or `app/web/backtest_history_helpers.py`.

### 2026-04-30
- Merged the standalone Pre-Live Review workflow into Candidate Review.
- Changed:
  - removed the `Pre-Live Review` Backtest panel from the main workflow navigation
  - moved Pre-Live status suggestion, draft generation, readiness scoring, and registry display helper logic into `app/web/backtest_candidate_review_helpers.py`
  - deleted the standalone `app/web/backtest_pre_live_review.py` and `app/web/backtest_pre_live_review_helpers.py` scripts
  - expanded `Backtest > Candidate Review > 3. 운영 상태 저장 및 Portfolio Proposal 진입 평가` so a ready current candidate can save a Pre-Live operating record and then open Portfolio Proposal from the same screen
  - kept `PRE_LIVE_CANDIDATE_REGISTRY.jsonl` and runtime append/load semantics intact because Portfolio Proposal still reads those operating records
  - synced README, comprehensive analysis, script structure map, web backtest UI flow, and Guides copy
- Verification:
  - `.venv/bin/python -m py_compile app/web/backtest_candidate_review.py app/web/backtest_candidate_review_helpers.py app/web/pages/backtest.py app/web/streamlit_app.py` passed
- Durable takeaway:
  - Pre-Live remains an operating-record concept, but it is no longer a separate Backtest tab or script pair. Future UI edits for this step should start in Candidate Review.

### 2026-04-30
- Improved Candidate Review orientation without adding long explanatory copy.
- Changed:
  - added shared Backtest UI components for an artifact pipeline and input/action/output step summaries
  - replaced the Candidate Packaging flow table with a five-card artifact chain: Draft, Review Note, Current Candidate, Pre-Live Record, Proposal Ready
  - added compact input/action/output cards to the three Candidate Review sections
  - changed `Registry 후보 범위 판단` from metric columns to the same wrapping route/readiness panel style used by Candidate Packaging and Portfolio Proposal readiness
  - synced the script structure map and web backtest UI flow docs
- Verification:
  - `.venv/bin/python -m py_compile app/web/backtest_candidate_review.py app/web/backtest_ui_components.py app/web/pages/backtest.py app/web/streamlit_app.py` passed
  - Streamlit smoke checked `Backtest > Candidate Review`; the artifact pipeline, step summaries, and Registry scope panel render correctly
- Durable takeaway:
  - Candidate Review now explains its workflow through compact visual structure rather than large instructional text blocks.

### 2026-04-30
- Refined Candidate Review after visual review feedback.
- Changed:
  - removed the per-section Input / Action / Output card grids because they made the page feel busier
  - replaced them with thin `왜 / 결과` brief strips
  - simplified `2. Registry 저장` by keeping the Scope route panel visible and moving detailed criteria / previous registry rows into collapsed expanders
  - reduced visible Registry row inputs to ID, record type, title, notes, and the next-step selection label; moved advanced strategy identity fields into a collapsed section
  - changed Registry metadata and Pre-Live signal summaries from large cards to compact badge strips
  - trimmed `3. 운영 상태 저장 및 Portfolio Proposal 진입 평가` so Candidate Review shows only the selected candidate's core state, operating decision, and proposal route by default, with recent-candidate identity details hidden behind an expander
  - added a Streamlit copy-shortcut guard so normal Cmd/Ctrl+C does not bubble into Streamlit's clear-cache shortcut handler
- Verification:
  - `.venv/bin/python -m py_compile app/web/backtest_candidate_review.py app/web/backtest_ui_components.py app/web/streamlit_app.py app/web/pages/backtest.py` passed
  - Streamlit smoke checked `Backtest > Candidate Review`; artifact pipeline remains, step guidance is shown as `왜 / 결과`, Registry advanced identity fields and detailed criteria are collapsed, and Cmd/Ctrl+C no longer opens the clear-cache modal
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py` passed
- Durable takeaway:
  - Candidate Review should keep the artifact pipeline, but per-section guidance should stay thin and action-centered.

### 2026-04-30
- Simplified Candidate Review step 3 into candidate confirmation plus operating-record save.
- Changed:
  - renamed step 3 to `운영 기록 저장 및 Portfolio Proposal 이동`
  - replaced the visible `Candidate Packaging 종합 판단` panel with a compact `선택 후보 확인` block
  - merged the separate `Pre-Live 운영 상태 / 추적 계획 저장` and `Portfolio Proposal 진입 평가` blocks into `운영 기록 저장 및 다음 단계 판단`
  - changed the default view to show `Save Record`, `Next Route`, `Proposal`, and `Blockers` as compact badges above the save/open buttons
  - moved detailed route criteria into collapsed expanders
  - synced Guides copy and web backtest UI flow docs
- Verification:
  - `.venv/bin/python -m py_compile app/web/backtest_candidate_review.py app/web/backtest_ui_components.py app/web/pages/backtest.py app/web/streamlit_app.py` passed
  - Streamlit smoke checked `Backtest > Candidate Review`; step 3 now renders as `선택 후보 확인` plus `운영 기록 저장 및 다음 단계 판단`, and the old separate Proposal readiness panel is gone
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py` passed
- Durable takeaway:
  - Step 3 should read as `select candidate -> save operating record -> open Proposal if the saved record qualifies`, not as a second full Candidate Packaging evaluation.

### 2026-04-30
- Restored the shared route/readiness judgment pattern inside Candidate Review step 3.
- Changed:
  - added the common route/readiness panel back to `운영 기록 저장 및 다음 단계 판단` so the next-step judgment remains visually consistent with `저장 범위 판단`
  - kept the Promotion / Shortlist / Deployment / Suggested badges as the candidate signal summary
  - moved `운영 기록 / 다음 단계 판단 기준`, `Pre-Live Record JSON Preview`, and `Selected Candidate Detail` into one collapsed `상세 보기` area with tabs
  - moved the `Save Pre-Live Record` and `Open Portfolio Proposal` buttons into a bordered `저장 및 이동` action block before the details
  - synced the web backtest UI flow doc
- Verification:
  - `.venv/bin/python -m py_compile app/web/backtest_candidate_review.py app/web/backtest_ui_components.py app/web/pages/backtest.py app/web/streamlit_app.py` passed
- Durable takeaway:
  - Candidate Review step 3 should preserve a common next-step judgment panel, but keep secondary details behind one collapsed area so the save/open actions are easy to find.

### 2026-04-30
- Repositioned Candidate Review step 3 next-step judgment above the operating-record inputs.
- Changed:
  - widened and rebalanced the shared route/readiness panel so long route labels break at underscores instead of mid-word
  - moved `다음 단계 진행 판단` above `운영 상태 / 추적 계획 입력` while keeping it driven by the current input values
  - kept the panel in the same bordered format as `저장 범위 판단`, including progress and success/warning/error status
  - left Save / Open buttons before the collapsed detail area
- Verification:
  - `.venv/bin/python -m py_compile app/web/backtest_candidate_review.py app/web/backtest_ui_components.py app/web/pages/backtest.py app/web/streamlit_app.py` passed
  - Streamlit smoke checked `Backtest > Candidate Review` on port `8512`; `다음 단계 진행 판단` now appears above `운영 상태 / 추적 계획 입력`, Save/Open actions remain before `상세 보기`, and route/readiness cards do not horizontally overflow at 900px / 600px viewport widths
  - `git diff --check` passed
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py` passed
- Durable takeaway:
  - Candidate Review should show the pass/fail route judgment before the operator writes or saves the operating record, because the judgment explains why saving is available.

### 2026-04-30
- Reworked Backtest > Portfolio Proposal into a single construction-draft flow toward future Live Readiness.
- Changed:
  - split Portfolio Proposal render logic into `app/web/backtest_portfolio_proposal.py`
  - split proposal row creation, readiness scoring, monitoring, Pre-Live feedback, and paper tracking feedback helpers into `app/web/backtest_portfolio_proposal_helpers.py`
  - reduced `app/web/pages/backtest.py` to a Portfolio Proposal wrapper call for this panel
  - replaced the old five-tab proposal surface with `1. Proposal 후보 확인`, `2. 목적 / 역할 / 비중 설계`, `3. Proposal 저장 및 다음 단계 판단`
  - added a Live Readiness route/readiness panel with `LIVE_READINESS_CANDIDATE_READY`, `PROPOSAL_DRAFT_READY`, and `PROPOSAL_BLOCKED` routes
  - moved saved proposal monitoring / Pre-Live feedback / paper tracking feedback into one collapsed support area
  - refreshed Reference > Guides copy for the new Portfolio Proposal / Live Readiness boundary
  - updated the walkthrough session note so 6단계 Candidate Packaging and 7단계 Portfolio Proposal match the implemented flow
  - fixed shared status cards so numeric `0` displays as `0` instead of `-`
- Verification:
  - `.venv/bin/python -m py_compile app/web/backtest_portfolio_proposal.py app/web/backtest_portfolio_proposal_helpers.py app/web/backtest_ui_components.py app/web/pages/backtest.py app/web/streamlit_app.py` passed
  - Streamlit smoke checked `Backtest > Portfolio Proposal` on port `8513`; the new three-step flow rendered, selecting `GTAA review candidate` produced `LIVE_READINESS_CANDIDATE_READY`, and `Save Portfolio Proposal Draft` became enabled
  - `git diff --check` passed
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py` passed
- Durable takeaway:
  - Portfolio Proposal should remain a Backtest tab, but it should read as one lightweight construction-draft step between Candidate Review and future Live Readiness, not as several separate record-review stages.

### 2026-04-30
- Split Backtest > Portfolio Proposal into single-candidate direct readiness and multi-candidate construction paths.
- Changed:
  - added a `단일 후보 직행 평가` mode for one selected current candidate
  - added direct readiness scoring with `LIVE_READINESS_DIRECT_READY`, `LIVE_READINESS_DIRECT_REVIEW_REQUIRED`, and `LIVE_READINESS_DIRECT_BLOCKED`
  - made direct mode use implicit role `core_anchor`, target weight `100%`, and capital scope `paper_only` without writing a new proposal draft
  - kept `포트폴리오 초안 작성` for two or more candidates, where role / target weight / reason are real proposal inputs
  - clarified that `Proposal Components` is construction selection, not strategy comparison
  - synced Guides, Portfolio Proposal registry guide, web Backtest UI flow, walkthrough note, and the high-level finance map
- Verification:
  - `python3 -m py_compile app/web/backtest_portfolio_proposal.py app/web/backtest_portfolio_proposal_helpers.py` passed
  - `python3 -m py_compile app/web/backtest_portfolio_proposal.py app/web/backtest_portfolio_proposal_helpers.py app/web/pages/backtest.py app/web/streamlit_app.py` passed
  - Streamlit smoke checked `Backtest > Portfolio Proposal` on port `8514`; selecting `GTAA review candidate` opened `단일 후보 직행 평가`, showed `Proposal Draft=저장 불필요`, and rendered `LIVE_READINESS_DIRECT_READY`
  - `git diff --check` passed
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py` passed
- Durable takeaway:
  - Portfolio Proposal should not force a save loop for a single candidate; proposal draft persistence is mainly for multi-candidate construction or intentionally documented allocation proposals.

### 2026-04-30
- Reworked Workspace > Overview into a registry-backed quant dashboard.
- Changed:
  - added `app/web/overview_dashboard.py` for Overview rendering
  - added `app/web/overview_dashboard_helpers.py` for current candidate, Pre-Live, proposal, history, saved portfolio aggregation
  - replaced the old static start guide with KPI cards, review-priority Top 3 candidates, candidate funnel chart, next actions, recent activity, and collapsed system snapshot
  - moved runtime/build details into the `System Snapshot` expander instead of the top of the page
  - updated README, script structure map, web Backtest UI flow, and high-level finance map for the new Overview modules
- Verification:
  - `.venv/bin/python -m py_compile app/web/overview_dashboard.py app/web/overview_dashboard_helpers.py app/web/streamlit_app.py` passed
  - `.venv/bin/python` snapshot load returned 12 current candidates, 2 paper tracking records, 30 recent runs, and a Top 3 candidate list
  - Streamlit smoke checked `Workspace > Overview` on port `8515`; KPI cards, Top 3 candidate cards, funnel chart, next actions, recent activity, and collapsed system snapshot rendered
- Durable takeaway:
  - Overview should behave like the front dashboard for the quant workflow, showing current candidates and next actions rather than acting as a static start guide.

### 2026-04-30
- Split the remaining large Backtest page shell into workflow modules.
- Changed:
  - reduced `app/web/pages/backtest.py` to a thin Backtest page shell and workflow panel dispatcher
  - added `app/web/backtest_common.py` for shared presets, session state, panel routing, strategy input widgets, real-money / guardrail inputs, and status label helpers
  - added `app/web/backtest_single_strategy.py`, `app/web/backtest_single_forms.py`, and `app/web/backtest_single_runner.py` for Single Strategy orchestration, strategy-specific forms, and DB-backed run dispatch
  - added `app/web/backtest_compare.py` for Compare & Portfolio Builder, weighted portfolio builder, saved portfolio load / replay, and current-candidate compare prefill
  - added `app/web/backtest_result_display.py` for latest result / compare result / data trust / real-money detail / selection history display helpers
  - updated `streamlit_app.py`, `backtest_history.py`, and `backtest_candidate_review.py` to import the new module boundaries instead of reaching through the page shell
  - synced the script structure map, web Backtest UI flow, and high-level finance map
- Verification:
  - `.venv/bin/python -m py_compile app/web/pages/backtest.py app/web/backtest_common.py app/web/backtest_single_strategy.py app/web/backtest_single_forms.py app/web/backtest_single_runner.py app/web/backtest_compare.py app/web/backtest_result_display.py app/web/backtest_history.py app/web/backtest_candidate_review.py app/web/streamlit_app.py` passed
  - `.venv/bin/python` import smoke passed for the Backtest shell and new Backtest modules
  - Streamlit smoke checked `Workspace > Overview` and `Backtest` on port `8516`; `Single Strategy`, `Compare & Portfolio Builder`, `Candidate Review`, and `Portfolio Proposal` rendered after the split
- Durable takeaway:
  - `app/web/pages/backtest.py` should stay a page shell. Future Single / Compare / result display work should land in the matching `app/web/backtest_*.py` module instead of growing the page entry again.

### 2026-04-30
- Archived the existing local finance runtime JSONL records and started a fresh candidate registry run.
- Found and saved a GTAA candidate that reaches the current 7-step workflow boundary:
  - `GTAA Clean-6 AOR Top-1`
  - universe `SPY, QQQ, GLD, IEF, LQD, TLT`
  - `top=1`, `interval=2`, `score=3M/12M`, `trend=MA200`, `risk_off=cash_only`
  - formal benchmark `AOR`
  - `CAGR=15.3395%`, `MDD=-13.9675%`, `Promotion=real_money_candidate`
- Persisted:
  - `BACKTEST_RUN_HISTORY.jsonl`
  - `CANDIDATE_REVIEW_NOTES.jsonl`
  - `CURRENT_CANDIDATE_REGISTRY.jsonl`
  - `PRE_LIVE_CANDIDATE_REGISTRY.jsonl`
- Verification:
  - `manage_current_candidate_registry.py validate` passed with 1 registry row
  - `manage_pre_live_candidate_registry.py validate` passed with 1 pre-live row
  - Portfolio Proposal direct readiness evaluated as `LIVE_READINESS_DIRECT_READY`, score `10.0`, blockers `0`
- Durable takeaway:
  - For this GTAA candidate, `AOR` is the appropriate formal multi-asset benchmark for the current gate. `SPY` remains useful as a reference, but using `SPY` as the formal promotion benchmark turns the same candidate into `hold` because of rolling worst-excess validation caution.

### 2026-05-01
- Found and saved a second GTAA candidate under the user's follow-up constraints:
  - universe size 6~15, selected universe `SPY, QQQ, GLD, IEF, LQD, TLT`
  - `top=2`, `interval=3`, `score=1M/3M/6M`, `trend=MA200`, `risk_off=cash_only`
  - formal benchmark `AOR`
  - `CAGR=12.8073%`, `MDD=-11.5626%`, `Sharpe=2.0147`
  - `Promotion=real_money_candidate`, `ETF Operability=normal`, `Validation=normal`
- Persisted:
  - review note `candidate_review_note_a152594509dd`
  - current candidate `gtaa_current_candidate_clean6_aor_top2_i3_1m3m6m`
  - Pre-Live record `pre_live_gtaa_current_candidate_clean6_aor_top2_i3_1m3m6m`
- Verification:
  - `manage_current_candidate_registry.py validate` passed with 2 registry rows
  - `manage_pre_live_candidate_registry.py validate` passed with 2 pre-live rows
- Durable takeaway:
  - The top-2 interval-3 candidate is less aggressive than the top-1 candidate, but it is a cleaner second practice candidate because drawdown is lower and Sharpe is higher while still passing the same AOR-based Real-Money gate.

### 2026-05-01
- Searched for a higher-CAGR GTAA candidate under the same top/interval/universe constraints.
- Selected and saved:
  - `GTAA Clean-6 AOR Top-2 High CAGR`
  - universe `SPY, QQQ, GLD, IEF, LQD, TLT`
  - `top=2`, `interval=2`, `score=1M/12M`, `trend=MA150`, `risk_off=cash_only`
  - formal benchmark `AOR`
  - `CAGR=15.2174%`, `MDD=-8.8783%`, `Sharpe=1.9630`
  - `Promotion=real_money_candidate`, `ETF Operability=normal`, `Validation=normal`
- Persisted:
  - review note `candidate_review_note_d12013649150`
  - current candidate `gtaa_current_candidate_clean6_aor_top2_i2_1m12m_ma150`
  - Pre-Live record `pre_live_gtaa_current_candidate_clean6_aor_top2_i2_1m12m_ma150`
- Verification:
  - `manage_current_candidate_registry.py validate` passed with 3 registry rows
  - `manage_pre_live_candidate_registry.py validate` passed with 3 pre-live rows
- Durable takeaway:
  - The high-CAGR top-2 candidate meets the user's tightened target better than the interval-3 candidate: CAGR is above 15% while MDD is below 9%.

### 2026-05-01
- Added an Operations-owned Candidate Library for saved candidate replay.
- Changed:
  - added `app/web/backtest_candidate_library.py` to inspect saved current candidates and matched Pre-Live records
  - added `app/web/backtest_candidate_library_helpers.py` to join registry rows, build candidate tables, reconstruct ETF replay payloads, and re-run saved contracts
  - added `Operations > Candidate Library` to the Streamlit navigation
  - updated Backtest guidance to point run history to `Backtest Run History` and saved candidate replay to `Candidate Library`
  - clarified the Compare-side saved portfolio area as `Saved Weighted Portfolios`, separate from saved candidate replay
  - synced README, script structure map, web Backtest UI flow, and high-level finance map
- Verification:
  - `.venv/bin/python -m compileall app/web/backtest_candidate_library.py app/web/backtest_candidate_library_helpers.py app/web/streamlit_app.py app/web/pages/backtest.py app/web/backtest_compare.py` passed
  - Candidate Library helper load returned 3 current candidates and built a GTAA replay payload from the saved registry contract
  - GTAA candidate replay reproduced the stored candidate snapshot: `rows=63`, `End Balance=42653.22`, `CAGR=15.3395%`, `MDD=-13.9675%`
  - Streamlit smoke checked `Operations > Candidate Library` on port `8517`; candidate table, snapshot cards, replay button, rebuilt Data Trust / Summary tabs rendered without console errors after adding the missing shared compare chart helper to `backtest_result_display.py`
- Durable takeaway:
  - Saved candidates and saved weighted portfolios are different artifact types. Candidate Library is a 보관함 / 재검토 tool for current candidates, while Compare keeps weighted portfolio outputs created by the portfolio builder.

### 2026-05-01
- Searched `Quality Snapshot (Strict Annual)` for a candidate that can be used in the current 7-step practice workflow.
- Search frame:
  - `US Statement Coverage 100 / 300 / 500`
  - `Historical Dynamic PIT Universe`
  - `topN 3~10`
  - target `CAGR >= 20%`, `MDD >= -15%`
- Selected candidate:
  - `US Statement Coverage 100`, `topN=8`, `AOR` formal benchmark
  - factors `roe, roa, net_margin, asset_turnover, current_ratio`
  - `Trend Filter MA250`, `retain_unfilled_as_cash`, `cash_only`
  - underperformance guardrail `3M / -5%`
  - drawdown guardrail `12M / -12% strategy threshold / 5% gap threshold`
  - `CAGR=20.02%`, `MDD=-13.42%`, `Sharpe=1.3957`
  - `Promotion=real_money_candidate`, `Shortlist=paper_probation`, `Deployment=review_required`
- Coverage 300 / 500 did not produce exact hits in the bounded search.
- Durable takeaway:
  - This Quality candidate is a valid 7-step practice candidate when the formal benchmark is `AOR`.
  - It has not been appended to review/current/pre-live registries yet; saving should be done after the user confirms they want to persist this candidate.

### 2026-05-01
- Re-searched `Quality Snapshot (Strict Annual)` for a cleaner GTAA-like deployment path after the user asked whether the previous `review_required` candidate could be improved into a registry-ready candidate.
- Finding:
  - The earlier `CAGR 20% / MDD -13%` Quality candidate remains `review_required` because guardrail trigger / monitoring review signals stay active.
  - A clean `paper_only` candidate was found, but CAGR drops below the original 20% requirement.
- Clean paper-only candidate:
  - `US Statement Coverage 100`, `Historical Dynamic PIT`
  - factors `roe, roa, cash_ratio, debt_to_assets`
  - `topN=10`, `Trend MA250`, `retain_unfilled_as_cash`, `cash_only`, benchmark `AOR`
  - `CAGR=14.38%`, `MDD=-14.56%`, `Sharpe=1.2490`
  - `Promotion=real_money_candidate`, `Shortlist=paper_probation`, `Deployment=paper_only`
- Durable takeaway:
  - There are two Quality practice choices:
    - higher-return `review_required` candidate: closer to the user's numeric return target
    - lower-return `paper_only` candidate: cleaner registry / Pre-Live practice path

### 2026-05-01
- Improved the Real-Money detail surface used by Candidate Library replay results.
- Changed:
  - replaced truncation-prone `st.metric` rows in the Real-Money overview with wrapping status cards
  - applied the same card layout to Promotion, Shortlist, Probation / Monitoring, and Deployment Readiness sub-sections
  - kept the existing checklist/detail tables, but moved long status and next-step strings into card values/details so narrower browser widths do not collapse them into `...`
- Verification:
  - `.venv/bin/python -m compileall app/web/backtest_result_display.py app/web/backtest_candidate_library.py app/web/backtest_ui_components.py` passed
  - direct import check for `app.web.backtest_result_display._render_real_money_details` passed

### 2026-05-01
- Searched `Quality + Value Snapshot (Strict Annual)` for a practice candidate under the user's expanded constraints.
- Search frame:
  - `US Statement Coverage 100 / 300 / 500 / 1000` considered through local reruns and sub-agent sweeps
  - `Historical Dynamic PIT Universe`
  - `topN 3~10`
  - target `CAGR >= 25%`, `MDD >= -20%`
  - factor sets with at least 3 factors, mixing quality and value factors
- Selected candidate:
  - `US Statement Coverage 100`, `topN=10`, ticker benchmark `SPY`
  - quality factors `roe, roa, operating_margin, asset_turnover, current_ratio`
  - value factors `book_to_market, earnings_yield, sales_yield, pcr, por`
  - `reweight_survivors`, `cash_only`, trend / market regime off
  - underperformance guardrail `12M / -5%`
  - drawdown guardrail `12M / -15% strategy threshold / 3% gap threshold`
  - `CAGR=29.25%`, `MDD=-18.64%`, `Sharpe=1.5222`
  - `Promotion=real_money_candidate`, `Shortlist=paper_probation`, `Deployment=review_required`
- Durable takeaway:
  - This Quality + Value candidate meets the user's CAGR/MDD target and can be used as a Candidate Review / Portfolio Proposal practice candidate.
  - A Coverage 500 exact-performance hit was rejected as a workflow candidate because full runtime marked it `hold / blocked` due to liquidity / validation caution.

### 2026-05-01
- Registered the selected `Quality + Value Snapshot (Strict Annual)` practice candidate through the machine-readable workflow artifacts.
- Saved records:
  - `CANDIDATE_REVIEW_NOTES.jsonl`: `candidate_review_note_qv_cov100_top10_spy_mdd20`
  - `CURRENT_CANDIDATE_REGISTRY.jsonl`: `quality_value_current_candidate_cov100_top10_spy_mdd20`
  - `PRE_LIVE_CANDIDATE_REGISTRY.jsonl`: `pre_live_quality_value_current_candidate_cov100_top10_spy_mdd20`
- Verification:
  - reran full runtime before append: `CAGR=29.2522%`, `MDD=-18.6392%`, `Sharpe=1.5222`
  - gate: `real_money_candidate / paper_probation / review_required`
  - `manage_current_candidate_registry.py validate` passed with 4 rows
  - `manage_pre_live_candidate_registry.py validate` passed with 4 rows
  - Candidate Library helper loaded the candidate with `paper_tracking` Pre-Live status
- Note:
  - Candidate Library lists the candidate now. Strict annual equity replay support was added on 2026-05-02.

### 2026-05-01
- Rechecked the `review_required` issue after the user asked for a cleaner candidate with `Promotion=real_money_candidate`, `Shortlist=paper_probation`, and `Deployment=paper_only`.
- Finding:
  - `Quality + Value` variants could keep stronger CAGR, but no exact `paper_only` deployment candidate was found before stopping the bounded/sub-agent sweep.
  - The clean exact hit was the lower-return `Quality Snapshot (Strict Annual)` candidate.
- Registered records:
  - `CANDIDATE_REVIEW_NOTES.jsonl`: `candidate_review_note_quality_cov100_top10_aor_ma250_paper_only`
  - `CURRENT_CANDIDATE_REGISTRY.jsonl`: `quality_current_candidate_cov100_top10_aor_ma250_paper_only`
  - `PRE_LIVE_CANDIDATE_REGISTRY.jsonl`: `pre_live_quality_current_candidate_cov100_top10_aor_ma250_paper_only`
- Verification:
  - candidate result: `CAGR=14.38%`, `MDD=-14.56%`, `Sharpe=1.2490`
  - gate: `real_money_candidate / paper_probation / paper_only`
  - `manage_current_candidate_registry.py validate` passed with 5 rows
  - `manage_pre_live_candidate_registry.py validate` passed with 5 rows
  - Candidate Library helper loaded the candidate with `paper_tracking` Pre-Live status

### 2026-05-02
- Fixed Candidate Library replay for saved strict annual equity candidates after the user hit the ETF-only replay warning on `Quality + Value Coverage 100 Top-10`.
- Changed:
  - extended `app/web/backtest_candidate_library_helpers.py` replay support from ETF-only families to `quality_snapshot_strict_annual`, `value_snapshot_strict_annual`, and `quality_value_snapshot_strict_annual`
  - restored strict annual contract fields from current candidate registry rows, including factors, topN, dynamic PIT universe, trend / market regime, guardrails, benchmark, liquidity filters, and promotion thresholds
- Verification:
  - `.venv/bin/python -m compileall app/web/backtest_candidate_library_helpers.py app/web/backtest_candidate_library.py` passed
  - Candidate Library replay helper rebuilt `quality_current_candidate_cov100_top10_aor_ma250_paper_only` with 124 result rows and gate `real_money_candidate / paper_probation / paper_only`
  - Candidate Library replay helper rebuilt `quality_value_current_candidate_cov100_top10_spy_mdd20` with 124 result rows and gate `real_money_candidate / paper_probation / review_required`

### 2026-05-02
- Checked the saved `Quality + Value Coverage 100 Top-10` Candidate Library replay after the user could not see `2026-03-31` in the Result Table.
- Finding:
  - backend replay result contains `2026-03-31`; final four result dates are `2026-01-30`, `2026-02-27`, `2026-03-31`, `2026-04-01`
  - the extra `2026-04-01` row is the requested end-date valuation row, while `2026-03-31` is the normal March month-end row
- Changed:
  - translated strict annual runtime warnings for dynamic PIT universe, history/liquidity filters, trend/market regime/risk-off, and underperformance/drawdown guardrails into Korean
- Verification:
  - `.venv/bin/python -m compileall app/web/runtime/backtest.py` passed
  - Candidate Library replay warnings for `quality_value_current_candidate_cov100_top10_spy_mdd20` are now displayed in Korean

### 2026-05-02
- Reorganized finance phase documents under a single phase parent folder after the user pointed out `.aiworkspace/note/finance` root document fragmentation.
- Changed:
  - moved root-level numbered phase folders into `.aiworkspace/note/finance/phases/phase1` through `.aiworkspace/note/finance/phases/phase30`
  - added `.aiworkspace/note/finance/phases/README.md` as the phase document landing page
  - updated phase links and workflow references in roadmap / doc index / analysis / code-analysis / operation docs
  - updated `bootstrap_finance_phase_bundle.py` to create future phase bundles under `.aiworkspace/note/finance/phases/phase<N>/`
  - updated `check_finance_refinement_hygiene.py` phase-doc classification for the new path
- Verification:
  - no numbered phase directories remain directly under `.aiworkspace/note/finance`
  - old `.aiworkspace/note/finance/phaseN` references are removed from active docs and scripts

### 2026-05-02
- Reorganized finance JSONL files into purpose-specific folders after the user asked whether registry and history files should also be folder-managed.
- Changed:
  - moved durable registry files under `.aiworkspace/note/finance/registries/`
  - moved local run history under `.aiworkspace/note/finance/run_history/`
  - moved saved portfolio setup storage under `.aiworkspace/note/finance/saved/`
  - updated Streamlit runtime path constants, registry helper scripts, hygiene helper classification, UI path copy, and durable operations docs
  - added README files for `registries/`, `run_history/`, and `saved/`
- Decision:
  - registries are durable app-readable operating data
  - run history remains generated / local execution state
  - saved portfolio JSONL is reusable setup storage, not a candidate approval registry

### 2026-05-03
- Opened Phase 31 preparation after the user approved the Phase 31~35 direction toward final real-money portfolio candidate selection.
- Created the Phase 31 document bundle under `.aiworkspace/note/finance/phases/phase31/`.
- Defined Phase 31 as `Portfolio Risk And Live Readiness Validation`, not as a duplicate Live Readiness decision-record phase.
- Added the first work-unit document for `Portfolio Risk Input And Validation Contract`.
- Decision:
  - Phase 31 should read existing current candidate, Pre-Live, and Portfolio Proposal registries first.
  - It should start as a read-only validation pack and avoid creating a new approval registry unless a later phase clearly needs one.
  - Phase 30 remains `implementation_complete / manual_qa_pending`; Phase 31 opens as `active / not_ready_for_qa`.

### 2026-05-03
- Completed Phase 31 implementation for `Portfolio Risk And Live Readiness Validation`.
- Changed:
  - added Phase 31 validation helpers in `app/web/backtest_portfolio_proposal_helpers.py`
  - normalized direct single-candidate and proposal draft inputs into one validation input shape
  - added validation result fields for route, score, blockers, paper tracking gaps, review gaps, component rows, checks, and Phase 32 handoff summary
  - rendered Validation Pack surfaces in `Backtest > Portfolio Proposal` for direct single-candidate review, in-progress proposal drafts, and saved proposal review
  - kept the feature read-only: no new approval registry, no live approval, no optimizer
- Documentation:
  - synced Phase 31 TODO, completion summary, checklist, next phase preparation, roadmap, doc index, README, comprehensive analysis, and Backtest UI flow docs
- Verification:
  - `.venv/bin/python -m py_compile app/web/streamlit_app.py app/web/pages/backtest.py app/web/backtest_portfolio_proposal.py app/web/backtest_portfolio_proposal_helpers.py` passed
  - helper smoke confirmed one direct candidate can route to `READY_FOR_ROBUSTNESS_REVIEW`
  - helper smoke confirmed a two-candidate proposal with overlap routes to `NEEDS_PORTFOLIO_RISK_REVIEW`
- Status:
  - Phase 31 is now `implementation_complete / manual_qa_pending`
  - user QA should use `.aiworkspace/note/finance/phases/phase31/PHASE31_TEST_CHECKLIST.md`

### 2026-05-03
- Refined Phase 31 QA feedback around in-progress Portfolio Proposal validation.
- Changed:
  - removed duplicate weight-sum reporting from `Blocking Scope`, so a 100% target-weight issue is surfaced as `Portfolio Construction` with an actionable correction
  - added `blocking_guidance` messages such as target weight must sum to 100% and active proposals need at least one `core_anchor`
  - added a `Proposal Role / Target Weight 사용법` expander inside `Backtest > Portfolio Proposal`
  - clarified the Phase 31 checklist item for "Validation Pack does not auto-save or approve"
  - added Proposal Role usage notes to the glossary and Backtest UI flow document
- Decision:
  - `PROPOSAL_BLOCKED` for GTAA + Quality is normal when target weights do not sum to 100% or no active `core_anchor` remains.
  - The issue was not the validation logic but the lack of actionable UI guidance.

### 2026-05-03
- Fixed Phase 31 Portfolio Proposal save feedback after the user reported no visible reaction from `Save Portfolio Proposal Draft`.
- Finding:
  - the proposal draft was being appended to `.aiworkspace/note/finance/registries/PORTFOLIO_PROPOSAL_REGISTRY.jsonl`
  - the success message disappeared because the UI called `st.rerun()` immediately after `st.success`
  - repeated clicks could append the same Proposal ID multiple times
- Changed:
  - moved the save success message into session state so it remains visible after rerun
  - reset the Proposal ID after a successful save so the next draft gets a fresh default id
  - added duplicate Proposal ID blocking with an explicit "change Proposal ID" instruction

### 2026-05-03
- Refined Phase 31 Portfolio Proposal UX after the user noted saved proposal feedback looked awkward in the single-candidate direct path.
- Changed:
  - removed the saved proposal feedback section from the single-candidate direct path
  - kept single-candidate review focused on direct Live Readiness readiness plus Portfolio Risk / Validation Pack
  - moved saved proposal validation / monitoring / feedback into the multi-candidate proposal draft path as `4. 저장된 Portfolio Proposal 확인`
  - updated the save success copy to point to the new saved proposal section
- Decision:
  - single candidates should proceed as direct next-stage inputs without proposal draft save/list UX
  - saved proposal lists belong to the portfolio construction flow where two or more candidates are being composed

### 2026-05-03
- Refined the Phase 31 manual QA checklist after the saved proposal UX move.
- Changed:
  - preserved the user's existing checked QA items
  - replaced the stale `보조 도구: Saved Proposals / Feedback` verification path with `4. 저장된 Portfolio Proposal 확인`
  - added checks that saved proposal lists appear only in the multi-candidate proposal construction flow
  - added a QA reset note for deleting `.aiworkspace/note/finance/registries/PORTFOLIO_PROPOSAL_REGISTRY.jsonl`

### 2026-05-03
- Renamed the Phase 31 validation expander label after the user pointed out that `Phase 32 handoff` sounded like an internal phase term.
- Changed:
  - UI label changed from `Validation 기준 / Phase 32 handoff` to `검증 기준 / 다음 단계 안내`
  - caption now describes this as a read-only check for the next robustness validation step
  - Phase 31 checklist and Backtest UI flow notes now use the same user-facing wording

### 2026-05-03
- Clarified the Phase 31 manual QA checklist after the user found the `다음 단계 안내 확인` section hard to verify.
- Changed:
  - explained that QA does not need to force all four validation routes
  - added concrete checks for `Validation Route`, `Next Action`, and the `검증 기준 / 다음 단계 안내` expander
  - added route interpretation tables to the checklist and next-phase preparation document

### 2026-05-03
- Closed Phase 31 after the user confirmed Phase 31 closeout.
- Changed:
  - marked remaining Phase 31 checklist items as completed based on the user's QA completion signal
  - moved Phase 31 status to `complete` / `manual_qa_completed`
  - synced Phase 31 TODO, completion summary, next-phase preparation, roadmap, doc index, README, and comprehensive analysis
  - kept Phase 30 as `implementation_complete` / `manual_qa_pending`
- Next direction:
  - Phase 32 can open as `Robustness And Stress Validation Pack` when the user approves the next phase start.
- Hygiene:
  - `check_finance_refinement_hygiene.py` was run.
  - Current candidate registry changes were not needed because Phase 31 closeout changed docs / QA status only, not candidate rows.

### 2026-05-03
- Created narrower local Codex skills after the user approved splitting `finance-doc-sync`.
- Changed:
  - added `/Users/taeho/.codex/skills/finance-backtest-web-workflow/SKILL.md`
  - added `/Users/taeho/.codex/skills/finance-phase-management/SKILL.md`
  - narrowed `/Users/taeho/.codex/skills/finance-doc-sync/SKILL.md` so it is treated as final documentation alignment, not the primary implementation skill
  - updated `AGENTS.md` and support track docs with the intended skill usage order
- Decision:
  - Phase32 Backtest UI work should start with `finance-backtest-web-workflow` or `finance-phase-management`, then use `finance-doc-sync` for final alignment.
- Hygiene:
  - `check_finance_refinement_hygiene.py` was run.
  - Current candidate registry changes were not needed because this was skill / workflow guidance work, not candidate data work.

### 2026-05-03
- Opened Phase 32 `Robustness And Stress Validation Pack` after the user approved moving on from Phase 31.
- Changed:
  - created `.aiworkspace/note/finance/phases/phase32/` plan / TODO / checklist / summary / next-phase preparation documents
  - added `Robustness / Stress Validation Preview` under `Backtest > Portfolio Proposal` Validation Pack
  - expanded validation input rows with period, contract, benchmark, CAGR / MDD, and compare evidence snapshots
  - added robustness route / score / blockers / input gaps / suggested sweeps for single candidate, in-progress proposal, and saved proposal validation
  - updated roadmap, doc index, Backtest UI flow docs, glossary, README, and comprehensive analysis for Phase 32 active status
- Decision:
  - Phase 32 first work unit is a read-only robustness input preview.
  - It does not run period split backtests, parameter sensitivity sweeps, live approval, or final portfolio selection yet.
- Hygiene:
  - py_compile, helper smoke, diff check, and finance refinement hygiene checks were run.
  - current candidate and Pre-Live registry validation passed; no registry row edits were needed.
  - Existing unrelated strategy logs, `uv.lock`, archived reset files, phase12 temp CSVs, and generated proposal registry artifact were left unstaged.

### 2026-05-03
- Completed Phase 32 implementation work units 2 through 4 after the user asked to continue through checklist handoff.
- Changed:
  - added `phase32_stress_summary_v1` stress / sensitivity result contract
  - added `Stress / Sensitivity Summary` table to the Portfolio Proposal Validation Pack
  - added Phase33 paper ledger handoff route / score / requirements
  - updated saved proposal validation summary rows with `Phase33 Handoff`
  - created Phase32 second / third / fourth work-unit documents
  - moved Phase32 to `implementation_complete` / `manual_qa_pending`
- Decision:
  - Phase32 remains read-only and does not execute period split backtests, benchmark sensitivity runners, parameter sweeps, paper ledger persistence, live approval, or final selection.
  - `Result Status = NOT_RUN` means the stress result contract is ready but no actual stress runner has filled results yet.
- Hygiene:
  - py_compile, saved proposal helper smoke, registry validation, diff check, Streamlit server health check, and finance refinement hygiene checks were run.

### 2026-05-03
- Closed Phase 32 after the user confirmed the checklist was complete.
- Changed:
  - preserved the user's checked Phase32 checklist items
  - moved Phase32 status to `complete` / `manual_qa_completed`
  - synced Phase32 TODO, completion summary, next phase preparation, roadmap, doc index, and comprehensive analysis
- Next direction:
  - Phase33 `Paper Portfolio Tracking Ledger` can open when the user approves the next phase start.
  - Phase30 remains `implementation_complete` / `manual_qa_pending` and is not changed by Phase32 closeout.
- Hygiene:
  - `check_finance_refinement_hygiene.py` was run.
  - Current candidate / Pre-Live registry validation passed; no registry row edits were needed.
### 2026-05-03
- Completed Phase 34 implementation work units 1 through 4 after the user asked to finish the phase through checklist handoff.
- Changed:
  - added `app/web/runtime/final_selection_decisions.py` and runtime exports for `.aiworkspace/note/finance/registries/FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`
  - added Final Selection Decision evidence, save-readiness, row-building, display, and Phase35 handoff helpers
  - added `Final Selection Decision Pack`, `Save Final Selection Decision`, and saved final decision review under `Backtest > Portfolio Proposal`
  - created Phase34 second / third / fourth work-unit documents and updated checklist, completion summary, next-phase preparation, roadmap, doc index, operations guides, README, code-analysis docs, and comprehensive analysis
- Decision:
  - Phase34 final decision records are append-only selection / hold / reject / re-review judgments.
  - They are not live approval, broker orders, or automatic trading instructions.
  - Phase35 should read selected final decisions as input for a post-selection operating guide.
- Hygiene:
  - py_compile and helper smoke were run during implementation.
  - Existing unrelated strategy logs, `uv.lock`, archived reset files, phase12 temp CSVs, generated registries, and run history artifacts were left unstaged.

### 2026-05-03
- Reworked Phase 34 after the user challenged the repeated save-button flow.
- Changed:
  - split final validation / observation / judgment into a new `Backtest > Final Review` panel
  - kept `Backtest > Portfolio Proposal` focused on single-candidate direct readiness, multi-candidate proposal draft save, and saved proposal feedback
  - added `app/web/backtest_final_review.py` and `app/web/backtest_final_review_helpers.py`
  - removed the old Paper Ledger / Final Selection save surfaces from the active Portfolio Proposal flow
  - changed the user-facing final save action to `최종 검토 결과 기록`
  - moved paper observation criteria into the final review record instead of requiring a separate main-flow Paper Ledger save
  - rebuilt the Phase34 checklist around Portfolio Proposal boundary, Final Review source selection, validation / observation, final record, and Phase35 handoff
  - synced README, AGENTS, code analysis docs, operations guides, roadmap, doc index, glossary, comprehensive analysis, and Phase34 docs
- Decision:
  - Paper Portfolio Tracking Ledger remains as a compatibility / operating artifact.
  - The main Phase34 user flow is now `Portfolio Proposal draft -> Final Review -> 최종 검토 결과 기록`.
  - Final Review records remain append-only final select / hold / reject / re-review judgments, not live approval or orders.

### 2026-05-04
- Closed Phase 34 after the user confirmed `PHASE34_TEST_CHECKLIST.md` was complete.
- Changed:
  - preserved the user's checked Phase34 checklist items
  - moved Phase34 status to `complete` / `manual_qa_completed`
  - opened Phase35 `Post-Selection Operating Guide` as `active` / `not_ready_for_qa`
  - created the Phase35 plan / TODO / completion summary / next-phase preparation / checklist placeholder bundle under `.aiworkspace/note/finance/phases/phase35/`
  - synced roadmap, doc index, comprehensive analysis, glossary, phase docs, and durable logs
- Decision:
  - Phase35 starts from Phase34 `SELECT_FOR_PRACTICAL_PORTFOLIO` final review records.
  - Phase35 will turn selected records into rebalance / stop / reduce / re-review operating guidance.
  - Phase35 is not live approval, broker order, auto-trading, or an optimizer.
- Hygiene:
  - This was a documentation / phase-management closeout and kickoff unit.
  - Existing unrelated strategy logs, `uv.lock`, generated registries, run history artifacts, archived reset files, and phase12 temp CSVs were left unstaged.

### 2026-05-04
- Completed Phase 35 implementation work units 1 through 4 after the user asked to proceed through checklist handoff.
- Changed:
  - added `Backtest > Post-Selection Guide` as the final workflow panel
  - added `app/web/backtest_post_selection_guide.py` and helper logic for selected final decision input, readiness, operating policy, guide row creation, and saved guide review
  - added `app/web/runtime/post_selection_guides.py` and `.aiworkspace/note/finance/registries/POST_SELECTION_OPERATING_GUIDES.jsonl` as the append-only operating guide registry path
  - connected Final Review to Post-Selection Guide with a navigation button
  - updated Phase35 work-unit docs, checklist, roadmap, doc index, comprehensive analysis, README, AGENTS, code analysis docs, operations guide, glossary, and active skill guidance
- Decision:
  - Phase35 stores operating rules separately from final decisions so selection judgment and operating policy do not overwrite each other.
  - The user-facing action is one clear `운영 가이드 기록` button.
  - Post-Selection Guide remains disabled for live approval, broker order, and auto-trading.
- Hygiene:
  - py_compile and selected final decision input smoke were run.
  - Existing unrelated strategy logs, `uv.lock`, generated registries, run history artifacts, archived reset files, and phase12 temp CSVs were left unstaged.

### 2026-05-04
- Reworked Phase 35 after the user challenged the repeated save-button pattern.
- Changed:
  - removed the active `운영 가이드 기록` append-only save flow from `Backtest > Post-Selection Guide`
  - removed `app/web/runtime/post_selection_guides.py` and runtime exports for a separate post-selection operating guide registry
  - changed Post-Selection Guide into a no-extra-save final investment guide surface that reads Final Review decision records
  - added plain-language final verdict mapping: 투자 가능 후보 / 투자하면 안 됨 / 내용 부족 / 재검토 필요
  - changed Phase35 readiness routes to `FINAL_INVESTMENT_GUIDE_READY`, `FINAL_INVESTMENT_GUIDE_NEEDS_INPUT`, and `FINAL_INVESTMENT_GUIDE_BLOCKED`
  - updated the Phase35 checklist and durable docs so Final Review remains the source of truth and Phase35 is a read / preview surface
- Decision:
  - Phase35 should not create another required registry after Final Review.
  - Final Review's final selection decision remains the durable judgment.
  - Post-Selection Guide confirms final investment readiness and operating-before-live rules without creating live approval, broker orders, or auto-trading.

### 2026-05-04
- Simplified Phase35 again after the user concluded the separate Post-Selection Guide step was still too heavy for the current product stage.
- Changed:
  - removed the active Post-Selection Guide panel from Backtest workflow navigation
  - deleted `app/web/backtest_post_selection_guide.py` and `app/web/backtest_post_selection_guide_helpers.py`
  - kept `Backtest > Final Review` as the final active portfolio-selection panel
  - added saved final decision investment verdict display so final records read as 투자 가능 후보 / 내용 부족 / 투자하면 안 됨 / 재검토 필요
  - replaced Post-Selection navigation from Final Review with a disabled `Live Approval / Order` boundary action
  - rewrote Phase35 TODO, plan, work-unit docs, completion summary, next preparation, and checklist around `Portfolio Proposal -> Final Review -> 최종 판단 완료`
  - synced README, AGENTS, code-analysis docs, operations guides, roadmap, index, glossary, and comprehensive analysis to the simplified flow
- Decision:
  - The active user workflow ends at Final Review.
  - `FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl` is the final judgment source of truth.
  - No separate post-selection registry or active post-selection panel should be added unless the user explicitly reopens that design.

### 2026-05-04
- Fixed a Final Review saved-record display issue after the user noticed legacy Phase35 operating-guide wording in `기록된 최종 검토 결과 확인`.
- Changed:
  - added a Final Review status display translation layer for saved final decision rows
  - mapped existing selected / hold / reject / re-review records to current Final Review end-state wording
  - stopped showing legacy `Phase 35 운영 가이드 작성 가능` verdict / next action text in the route panel
  - updated the Phase35 checklist to include this regression check
- Decision:
  - Existing final decision JSON rows are not rewritten.
  - Legacy `phase35_handoff` data can remain in raw JSON for compatibility, but the UI should explain the record as Final Review completion.

### 2026-05-04
- Updated `Reference > Guides` after the user asked to align the guide with the current final-candidate workflow.
- Changed:
  - expanded the guide execution flow from the stale 1~7 / 1~8 framing to the current 1~10 flow
  - added a core concept guide for `Portfolio Proposal -> Final Review -> 최종 판단 완료`
  - updated stage pass criteria for 7->8, 8->9, 9->10, and final decision interpretation
  - refreshed the guide's document / file list with proposal, paper ledger, and final decision guide / registry paths
  - synced `BACKTEST_UI_FLOW.md`, the historical walkthrough note, and `FINANCE_DOC_INDEX.md` so they no longer imply a separate active Live Readiness / Post-Selection step
- Decision:
  - `Backtest > Final Review > 기록된 최종 검토 결과 확인` is the current final check for whether a portfolio was selected as a practical candidate.
  - Portfolio Proposal UI may still contain legacy `Live Readiness` route labels, but the current user-facing interpretation is Final Review input readiness.
  - `SELECT_FOR_PRACTICAL_PORTFOLIO` means selected as a practical candidate, not live approval, broker order, or auto-trading.

### 2026-05-04
- Improved `Reference > Guides > 문서와 파일 > 주요 파일 경로` after the user asked for clearer JSONL explanations.
- Changed:
  - split the file-path section into tabs for candidate review records, runtime / reusable records, and the full path list
  - added a visual JSONL storage map that explains what each registry stores, where it is created, and how to read it
  - clarified the difference between candidate notes, current candidate registry, Pre-Live records, proposal drafts, paper ledger compatibility rows, final selection decisions, run history, and saved portfolios
- Decision:
  - JSONL files should not be presented as bare paths in the guide.
  - The guide should make clear that only `FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl` is the final candidate-selection judgment source, while run history and saved portfolios are replay / reuse records.

### 2026-05-04
- Lightened repeated operator judgment UX after the user approved the proposed improvement direction.
- Changed:
  - changed Candidate Review Pre-Live input from `Operator Final Status` framing to `추천 운영 상태 확인` / `운영 상태 확인`
  - moved Candidate Review operating memo, next action, and review date into an optional expander with defaults
  - changed Portfolio Proposal `Operator Decision` framing to `Proposal 저장 상태`
  - moved Portfolio Proposal memo and next review date into an optional expander with defaults
  - added a Final Review notice that only the Final Review `최종 판단` is the main practical-candidate decision surface
  - moved Final Review decision id, operating constraints, and next action into an advanced expander
  - updated Phase35 TODO / checklist / completion summary and Backtest UI flow docs
- Decision:
  - The registry contracts remain unchanged.
  - Intermediate records stay useful as preparation / operating notes, but they should not feel like repeated final decisions.

### 2026-05-04
- Fixed a Final Review dataframe serialization warning reported by the user.
- Changed:
  - converted mixed numeric / string `Current` values in the inline paper observation checks to strings before rendering
- Decision:
  - The warning was not a final review logic failure, but it was a real UI hygiene issue because Streamlit logged an Arrow conversion traceback on each Final Review visit.

### 2026-05-04
- Captured the Phase35-after product gap after the user asked to save the discussion as a Markdown note.
- Changed:
  - added `.aiworkspace/note/finance/operations/FINAL_SELECTED_PORTFOLIO_OPERATIONS_DASHBOARD_GAP_20260504.md`
  - registered the note in `.aiworkspace/note/finance/operations/README.md` and `.aiworkspace/note/finance/FINANCE_DOC_INDEX.md`
- Decision:
  - The next most natural product direction is a final-selected portfolio operations dashboard, not another candidate-selection save/review step.

### 2026-05-05
- Improved `Backtest > Compare & Portfolio Builder` after the user asked to make GTAA / Equal Weight mix creation and saved portfolio reuse easier to understand.
- Changed:
  - split the Compare workspace into `전략 비교` and `저장 Mix 다시 열기` tabs
  - kept compare execution, weighted portfolio construction, result review, and save CTA in the `전략 비교` tab
  - moved saved portfolio list / load / replay / delete into the `저장 Mix 다시 열기` tab
  - added quick allocation buttons for `GTAA 70 / EW 30` and `GTAA 50 / EW 50`
  - renamed save/replay UI wording toward `Portfolio Mix` so saved setups are not confused with candidate registries
- Decision:
  - `.aiworkspace/note/finance/saved/SAVED_PORTFOLIOS.jsonl` remains the persistence location because these rows are reusable replay setups, not append-only candidate / proposal / final-decision registry rows.

### 2026-05-05
- Added Equal Weight Real-Money first-pass support after the user noticed its Compare 진입 평가 lacked a proper Real-Money judgment.
- Changed:
  - added Equal Weight runtime Real-Money hardening with cost-adjusted result, benchmark overlay, price freshness, ETF operability policy, promotion / shortlist / deployment metadata
  - added Equal Weight Real-Money Contract inputs in Single Strategy and Compare strategy boxes
  - preserved Equal Weight Real-Money fields in saved Portfolio Mix overrides and Candidate Library replay payloads
  - updated Backtest UI / runtime flow docs and the finance comprehensive map to reflect the new Equal Weight boundary
- Verification:
  - `py_compile` passed for the touched Backtest UI/runtime modules
  - DB-backed Equal Weight smoke confirmed `real_money_hardening`, `promotion_decision`, `shortlist_status`, and `deployment_readiness_status` are now emitted
- Note:
  - the tested Equal Weight baskets currently report `etf_operability_status=caution` because asset profile coverage is partial, so they may still be `hold/blocked`; that is now an explicit gate result rather than a missing judgment.

### 2026-05-05
- 정리 / 검증:
  - user request에 따라 `Equal Weight Dividend Growth 4 (DGRW/SCHD/TDIV/VIG)` current candidate에 `inactive` tombstone row를 append해 Candidate Library 최신 active view에서 제외했다.
  - Equal Weight ETF Real-Money gate 검증을 위해 주요 ETF 후보군의 `nyse_asset_profile` AUM / bid / ask metadata를 yfinance 기반 idempotent UPSERT로 보강했다.
  - `Equal Weight Growth/Commodity 4 (QQQ/SOXX/XLE/IAU)`는 보강 후 `real_money_candidate / paper_probation / paper_only`, CAGR 19.96%, MDD -19.71%, SPY CAGR 13.67%, SPY MDD -24.80%로 runtime 재검증을 통과했다.
- 후보 탐색:
  - 배당 ETF 포함 Equal Weight 후보군을 3~5개 symbol, SPY 초과 CAGR, MDD 20% 이하 기준으로 재탐색했다.
  - 가장 깔끔한 후보는 `IAU / QQQ / SOXX / VIG / XLE`, annual rebalance였다. Runtime 기준 CAGR 18.31%, MDD -19.27%, `real_money_candidate / paper_probation / paper_only`를 만족한다.
  - SCHD 포함 후보는 성과상 SPY를 초과하는 조합이 있었지만, 현재 rolling validation에서 `hold/blocked` 또는 `watchlist_only`로 남아 10단계 실습 후보로는 VIG 포함 5종 후보가 더 깨끗하다.
  - user request에 따라 `Equal Weight Dividend+Growth Balanced 5 (IAU/QQQ/SOXX/VIG/XLE)`를 Current Candidate Registry에 active row로 append해 Candidate Library에 노출했다.

### 2026-05-05
- GTAA SPY benchmark 후보 탐색:
  - user request에 따라 `SPY`를 formal benchmark로 두고 `top=2~4`, universe 6~12개, `interval<=3` 조건의 GTAA 후보를 병렬 탐색했다.
  - 가장 깔끔한 후보는 `QQQ / SOXX / MTUM / QUAL / USMV / IAU / IEF / TLT`, `top=2`, `interval=3`, `1M/6M/12M`, `MA250`, `cash_only`였다.
  - Runtime 재검증 결과 `CAGR=18.97%`, `MDD=-18.10%`, `SPY CAGR=13.36%`, `SPY MDD=-15.90%`, `Promotion=real_money_candidate`, `Shortlist=paper_probation`, `Deployment=paper_only`, `Validation=normal`을 만족했다.
  - 더 높은 CAGR 후보(`SPY/QQQ/SOXX/XLE/XLU/XLV/IEF/IAU`)도 있었지만 `Deployment=review_required`로 남아 10단계 실습 후보로는 위 후보가 더 깨끗하다.
  - 결과를 `GTAA_BACKTEST_LOG.md`에 append했다. Candidate Library 등록은 아직 하지 않았다.

### 2026-05-05
- GTAA SPY benchmark 저MDD 후보 재탐색:
  - user request에 따라 수익률을 조금 낮추더라도 `MDD<=15%`, `CAGR>=16~17%`, `top=2~4`, `interval<=3`, 10단계 통과 조건을 만족하는 후보를 추가 탐색했다.
  - 대표 후보는 `QQQ / SOXX / MTUM / QUAL / USMV / IAU / IEF / TLT`, `top=3`, `interval=3`, `1M/6M`, `MA250`, `cash_only`, `Benchmark=SPY`였다.
  - Runtime 재검증 결과 `CAGR=19.35%`, `MDD=-11.03%`, `SPY CAGR=13.36%`, `SPY MDD=-15.90%`, `Promotion=real_money_candidate`, `Shortlist=paper_probation`, `Deployment=paper_only`, `Validation=normal`을 만족했다.
  - 결과를 `GTAA_BACKTEST_LOG.md`에 append했다. Candidate Library 등록은 아직 하지 않았다.

### 2026-05-05
- GTAA SPY Low-MDD 후보 Candidate Library 등록:
  - user request에 따라 `GTAA SPY Low-MDD Style Top-3` 후보를 `.aiworkspace/note/finance/registries/CURRENT_CANDIDATE_REGISTRY.jsonl`에 active current candidate row로 append했다.
  - `registry_id=gtaa_current_candidate_spy_low_mdd_style_top3_i3_1m6m_ma250`.
  - Registry validation 결과 required field 누락 없이 통과했다.

### 2026-05-05
- Equal Weight + GTAA mix 후보 탐색:
  - user request에 따라 `GTAA SPY Low-MDD Style Top-3`와 함께 쓸 Equal Weight 후보를 symbol 3~5개, interval 6~12개월, benchmark `SPY`, 10단계 통과, MDD 15% 근처 조건으로 탐색했다.
  - 엄격히 Equal Weight 단독 `MDD<=15%`와 `Promotion=real_money_candidate / Deployment=paper_only / Validation=normal`을 동시에 만족하는 후보는 찾지 못했다.
  - 대표 실사용 후보는 `QQQ / SOXX / XLE / XLU / GLD`, annual rebalance다. 단독 기준 `CAGR=17.55%`, `MDD=-18.98%`, `Promotion=real_money_candidate`, `Deployment=paper_only`, `Validation=normal`.
  - `GTAA 70 / EW 30` mix는 `CAGR=18.74%`, `MDD=-10.30%`, `Sharpe=2.51`; `GTAA 60 / EW 40` mix는 `CAGR=18.52%`, `MDD=-10.04%`, `Sharpe=2.54`.
  - 결과를 `EQUAL_WEIGHT.md`와 `EQUAL_WEIGHT_BACKTEST_LOG.md`에 기록했다.

### 2026-05-06
- Portfolio Mix 저장:
  - user request에 따라 `GTAA SPY Low-MDD Style Top-3 60% + Equal Weight Growth/Sector/Gold 5 40%` mix를 `.aiworkspace/note/finance/saved/SAVED_PORTFOLIOS.jsonl`에 저장했다.
  - `portfolio_id=portfolio_gtaa_spy_low_mdd_60_ew_growth_sector_gold_40`.
  - 저장 row는 `Compare & Portfolio Builder > 저장 Mix 다시 열기`에서 다시 불러와 replay할 수 있는 reusable setup이다.

### 2026-05-06
- Compare 결과 노출 흐름 수정:
  - user report에 따라 `Run Strategy Comparison` 또는 `Replay Saved Mix` 후 5단계 Compare 결과가 눈에 보이지 않는 문제를 확인했다.
  - 원인은 saved mix replay 후에도 사용자가 `저장 Mix 다시 열기` 영역에 머물 수 있고, compare 결과가 `전략 비교` 영역 안쪽에 렌더링되어 결과가 숨은 것처럼 보이는 UX였다.
  - `Compare & Portfolio Builder` 내부 전환을 상태 기반 선택 UI로 바꾸고, replay / load / 새 compare 실행 후에는 `전략 비교` 화면으로 돌아오게 했다.
  - 최신 compare 결과는 `전략 비교` 화면 상단의 `5단계 Compare 결과` 박스에 먼저 렌더링하도록 이동했다.
  - 후속 bugfix: Streamlit widget key를 생성 후 직접 수정해 발생한 `backtest_compare_workspace_mode cannot be modified` 오류를 막기 위해, 화면 전환은 `backtest_compare_workspace_mode_request` pending flag로 요청하고 다음 rerun에서 widget 생성 전 적용하도록 변경했다.

### 2026-05-06
- Compare 단계 표현 변경 롤백 및 작업 규칙 보강:
  - user request에 따라 직전 `Compare 통과 판단 단계 표현 정리` 커밋을 revert했다. `Replay Saved Mix` 화면 전환 오류 수정은 유지했다.
  - user feedback을 반영해 단순 label 변경으로 UX / 단계 혼란을 해결하려 하지 말고, 먼저 흐름 구조와 stage ownership을 설명한 뒤 `진행할까요?` 확인을 받도록 `AGENTS.md`에 지침을 추가했다.
  - 향후 Compare / Candidate Review 단계 개편은 5단계 확인 위치와 6단계 handoff가 자연스럽게 이어지는 화면 구조를 먼저 제안한 뒤 진행한다.

### 2026-05-06
- Compare 5단계 / 6단계 handoff UX 개편:
  - user confirmation 후 `5단계 Compare 결과` 안에서 6단계 평가가 섞여 보이던 구조를 개선했다.
  - Compare 결과 상단에 `5단계 Compare 검증 보드`를 두고 PASS / CONDITIONAL / FAIL, Readiness, Data Trust, 4개 검증 기준을 명시적으로 보여주도록 변경했다.
  - `Send Selected Strategy To Candidate Review` 버튼은 `다음 행동` 영역으로 분리해, 버튼을 누른 뒤부터 6단계 Candidate Review가 시작된다는 경계를 화면에 남겼다.
  - `Replay Saved Mix`는 `저장 Mix Replay 결과`와 `구성 전략 Compare 검증`을 나누어 표시해 mix 자체 결과와 개별 전략 handoff 검증을 구분하게 했다.
  - `Reference > Guides`와 `BACKTEST_UI_FLOW.md`의 5단계 / 6단계 설명을 같은 흐름으로 갱신했다.

### 2026-05-06
- Saved Mix replay UX 후속 개편:
  - user confirmation 후 `Replay Saved Mix`가 더 이상 `전략 비교` 화면으로 강제 이동하지 않도록 변경했다.
  - `저장 Mix 다시 열기` 화면 안에서 replay 결과, `Portfolio Mix 검증 보드`, weighted portfolio 상세 결과를 바로 확인하게 했다.
  - mix 검증 보드는 `Saved Mix Replay`, `Mix Data Trust`, `Component Real-Money`, `Workflow Registry`를 따로 보여주며, saved mix setup과 5~10단계 workflow registry 기록을 구분한다.
  - `portfolio_gtaa_spy_low_mdd_60_ew_growth_sector_gold_40` 같은 saved setup은 replay 성과가 있어도 proposal / final review registry에 기록되지 않았으면 `Workflow Registry=NOT RECORDED`로 표시된다.
  - `Reference > Guides`와 `BACKTEST_UI_FLOW.md`를 같은 경계로 갱신했다.

### 2026-05-06
- Saved Mix -> Portfolio Proposal handoff 정리:
  - user confirmation 후 `저장 Mix 다시 열기 > Portfolio Mix 검증 보드`에서 workflow 기록이 없는 saved mix를 바로 `Portfolio Proposal` 초안으로 보낼 수 있게 했다.
  - 이 경로는 단일 후보를 만드는 `Candidate Review`가 아니라, 이미 비중이 정해진 portfolio mix를 proposal draft로 남기는 경로임을 UI와 Guides에 명시했다.
  - Portfolio Proposal은 saved mix prefill이 있을 때 전용 작성 화면을 먼저 보여주고, 저장 시 `.aiworkspace/note/finance/saved/SAVED_PORTFOLIOS.jsonl`의 setup과 `.aiworkspace/note/finance/registries/PORTFOLIO_PROPOSAL_REGISTRY.jsonl` workflow 기록을 연결한다.
  - Final Review에서 saved mix proposal을 읽을 때 component contract / benchmark / universe / compare evidence가 빠지지 않도록 proposal evidence snapshot을 보강했다.

### 2026-05-06
- Phase36 시작:
  - user confirmation에 따라 `Final-Selected Portfolio Monitoring And Rebalance Operations` phase를 열었다.
  - Phase36의 첫 구현 목표는 `FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`을 새로 쓰는 것이 아니라, Final Review에서 이미 `SELECT_FOR_PRACTICAL_PORTFOLIO`로 선정된 row를 읽어 `Operations > Selected Portfolio Dashboard`에서 운영 대상으로 보여주는 것이다.
  - 이번 작업에서는 current price / account holding 기반 drift 계산과 주문 초안은 제외하고, 최종 선정 포트폴리오 목록 / 상태 / target allocation / evidence / disabled execution boundary를 먼저 구현한다.

### 2026-05-06
- Phase36 first pass 구현 완료:
  - `app/web/runtime/final_selected_portfolios.py` read model을 추가해 Final Review selected decision row를 dashboard row와 status summary로 변환했다.
  - `Operations > Selected Portfolio Dashboard` page를 추가해 summary cards, selected portfolio table, status / source / benchmark filters, target allocation, evidence checks, operator next action, disabled execution boundary를 표시한다.
  - Phase36 plan / TODO / first work unit / checklist / completion / next-phase preparation과 roadmap / index / code analysis / comprehensive map / README / Guides를 동기화했다.
  - Verification: `PYTHONPYCACHEPREFIX=/tmp/codex_pycache python3 -m py_compile ...`, runtime helper smoke, `git diff --check`, `check_finance_refinement_hygiene.py` 통과.
  - 남은 gate는 사용자 manual QA다.

### 2026-05-06
- Phase36 current weight / drift check 구현:
  - user request에 따라 Phase36 QA를 마지막으로 미루고 다음 작업을 계속 진행했다.
  - `build_selected_portfolio_drift_check` helper를 추가해 component별 target weight와 operator가 입력한 current weight를 비교한다.
  - `Operations > Selected Portfolio Dashboard` 상세에 `Current Weight / Drift Check`를 추가했다.
  - `Rebalance threshold`, `Watch threshold`, `Total tolerance`를 입력받고 `DRIFT_ALIGNED`, `DRIFT_WATCH`, `REBALANCE_NEEDED`, `DRIFT_INPUT_INCOMPLETE`로 read-only 판정한다.
  - 실제 DB current price 조회, account holding 연결, broker order, auto rebalance는 계속 제외했다.

### 2026-05-06
- Phase36 value / holding input drift check 확장:
  - `finance/loaders/price.py`에 symbol별 latest price 조회 helper를 추가했다.
  - `build_selected_portfolio_current_weight_inputs` helper를 추가해 current value 또는 shares x price 입력을 current weight로 변환한다.
  - `Operations > Selected Portfolio Dashboard`의 drift check 입력 모드를 current weight 직접 입력, current value 입력, shares x price 입력으로 확장했다.
  - shares x price 입력에서는 DB latest close를 보조로 불러올 수 있지만, 값은 저장하지 않고 account holding 자동 연결 / 주문 생성도 하지 않는다.
  - Phase36 문서, roadmap / index / code analysis / comprehensive map / README를 value / holding input 기준으로 동기화했다.

### 2026-05-06
- Phase36 drift alert / review trigger preview 추가:
  - `build_selected_portfolio_drift_alert_preview` helper를 추가해 drift check 결과를 운영 경고 없음 / 관찰 경고 / 리밸런싱 검토 경고 / 입력 확인 경고로 변환했다.
  - `Operations > Selected Portfolio Dashboard` 상세에서 Final Review review trigger와 drift alert row를 함께 보여준다.
  - 이 preview는 alert registry를 저장하지 않고, live approval / broker order / auto rebalance도 계속 disabled로 둔다.
  - Phase36 checklist / completion / next phase preparation과 roadmap / index / code analysis / comprehensive map / README를 alert preview 기준으로 동기화했다.

### 2026-05-06
- Guides 포트폴리오 플로우 맵 UX polish 시작:
  - user request에 따라 `Reference > Guides`의 1~10 단계 실행 흐름을 선형 텍스트만으로 읽기 어렵다는 문제를 확인했다.
  - 단일 후보, 다중 후보 portfolio proposal, saved mix, 재검토 / blocker 경로를 시각적 flow map으로 분리해 보여주는 Guide 보강을 진행한다.
  - 변경 범위는 `app/web/streamlit_app.py`와 Backtest UI flow 문서 동기화로 제한하고, core finance 로직과 JSONL runtime artifact는 수정하지 않는다.
- 구현:
  - `Reference > Guides`의 `1~10 단계 실행 흐름` 앞에 `포트폴리오 플로우 맵`을 추가했다.
  - 경로 선택은 단일 후보, 여러 후보 포트폴리오, 저장 Mix, 재검토 / 막힘 경로로 나누고, 각 경로를 카드형 순서도 / 사용 상황 / 생략되는 단계 / 생성 또는 참조 기록 표로 보여준다.
  - `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md`의 Guides 묶음 설명을 다섯 묶음 기준으로 동기화했다.
- 검증:
  - `py_compile`로 `app/web/streamlit_app.py`, `app/web/pages/backtest.py`, `app/web/backtest_*.py`를 확인했다.
  - worktree Streamlit 서버를 `127.0.0.1:8502`에 띄우고 `Reference > Guides`에서 플로우 맵 렌더링과 경로 선택 동작을 확인했다.
  - `git diff --check`와 finance refinement hygiene helper를 통과했다.

### 2026-05-06
- Guides 제품형 UX 개편:
  - user feedback에 따라 `Reference > Guides`가 실습 문서 목록처럼 보이고, flow map도 카드 나열에 가까운 문제를 확인했다.
  - Guide 렌더링을 `app/web/reference_guides.py`로 분리하고, `streamlit_app.py`는 page shell / navigation 중심 책임을 유지하게 했다.
  - 첫 화면을 `Portfolio Selection Guide` hero, 경로 선택, route summary, GraphViz 기반 `Portfolio Flow`, `Decision Gates`, `Reference Drawer`, 접힘 `System status` 구조로 개편했다.
  - Runtime / Build는 사용자의 첫 guide 경험에서 제외하고 하단 `System status`로 낮췄다.
  - 외부 dependency는 추가하지 않았고, GraphViz 렌더링 실패 시 compact visual fallback을 사용하도록 했다.
  - 검증: `py_compile`, `git diff --check`, finance refinement hygiene helper를 통과했고, `127.0.0.1:8502/guides`에서 GraphViz flowchart 렌더링과 route selector 동작을 확인했다.

### 2026-05-06
- Guides 단계 해석 보강:
  - user feedback에 따라 GraphViz flowchart는 좋아졌지만 노드 내용이 얕고, 기존 1~10 단계 위치감이 약해진 문제를 확인했다.
  - `Reference > Guides`에 선택 경로별 핵심 checkpoint 카드와 `전체 1~10 단계` compact timeline을 추가했다.
  - timeline은 단일 후보, 여러 후보 포트폴리오, 저장 Mix, 막힘 해결 경로에 따라 `필수`, `반복`, `직행`, `선행`, `생략`, `보류` 같은 상태 라벨을 다르게 보여준다.
  - GraphViz node 문구도 `Run + Data Trust`, `Review + Registry`, `Validation + Decision`처럼 조금 더 정보성 있게 보강하되, 긴 설명은 timeline / checkpoint 패널로 분리했다.

### 2026-05-06
- Guides 경로 라벨 / 배치 polish:
  - user feedback에 따라 `저장 Mix`, `막힘 해결`, `이 경로의 핵심 단계`, `현재 경로 / 다음 행동` 카드가 무엇을 의미하는지 애매한 문제를 확인했다.
  - Guide 선택지를 `단일 후보`, `여러 후보 묶음`, `저장된 비중 조합`, `보류 / 재검토`로 정리했다.
  - `전체 1~10 단계에서 현재 위치`를 선택 버튼 바로 아래로 올리고, 그 아래에 `선택한 경로 요약`, `Portfolio Flow`, 선택 경로별 checkpoint를 배치했다.
  - 여러 후보 묶음 경로는 Candidate Review 저장이 선행이고 Portfolio Proposal은 이미 저장된 후보를 묶는 화면이라는 ownership을 문구로 명확히 했다.

### 2026-05-06
- Phase36 Selected Portfolio Dashboard 목적 재설계:
  - user feedback에 따라 기존 dashboard가 JSON inspection / drift 입력 화면처럼 보여 선정 포트폴리오의 성과 모니터링 목적이 흐려지는 문제를 확인했다.
  - `Operations > Selected Portfolio Dashboard`를 Snapshot / Performance Recheck / What Changed / Allocation Check / Audit 구조로 재배치했다.
  - Performance Recheck는 Final Review에서 선정된 component의 replay contract를 사용자가 지정한 start / end와 virtual capital로 다시 실행해 최신 성과, benchmark spread, component contribution, 강한 / 약한 기간을 보여준다.
  - raw JSON은 접힘 Audit 영역으로 이동했고, 실제 보유 drift는 optional advanced Allocation Check로 낮췄다.
  - Phase36 plan / TODO / first work unit / completion / next-phase preparation / checklist와 roadmap / doc index / comprehensive map / README / code analysis flow를 동기화했다.
  - Verification: `py_compile`, performance recheck defaults / replay smoke, `git diff --check`, finance refinement hygiene helper, Streamlit `127.0.0.1:8505` browser smoke를 통과했다.

### 2026-05-07
- Phase36 Selected Portfolio Dashboard UX 구조 polish:
  - user feedback에 따라 데이터 출처 / 운영 대상 목록 / Snapshot / Performance Recheck / Allocation / Operator Context의 좁은 화면 배치와 의미 연결 문제를 확인했다.
  - 데이터 출처와 화면 경계는 wrapping card와 접힘 registry path로 바꿨다.
  - 운영 대상 목록은 compact table, 짧은 portfolio selector, responsive filter layout으로 정리했다.
  - Snapshot은 selection summary와 Portfolio Blueprint로 재구성하고 target allocation을 포트폴리오 정의 영역으로 이동했다.
  - Performance Recheck 결과는 `Summary`, `Equity Curve`, `Result Table`, `What Changed`, `Contribution`, `Extremes` tab으로 분리했다.
  - Operator Context는 `Monitoring Playbook`으로 바꿔 Selection Evidence / Review Triggers / Holding Drift Check / Execution Boundary를 같은 흐름에서 읽게 했다.
  - Verification: py_compile, `git diff --check`, finance refinement hygiene helper, Streamlit browser smoke, 390px narrow viewport smoke 통과.

### 2026-05-07
- Phase36 Monitoring Playbook Trigger Board 정리:
  - user feedback에 따라 기존 Review Triggers tab이 operator note와 trigger list를 나열하는 수준이라 운영 판단 보드로 보기 어렵다는 문제를 확인했다.
  - Review Triggers tab을 `Trigger Board`로 바꾸고, Final Review evidence / CAGR deterioration / MDD expansion / benchmark underperformance / Holding drift row를 표시하게 했다.
  - Trigger Board는 최신 Performance Recheck 결과와 Holding Drift Check 입력 상태를 읽어 `Clear`, `Watch`, `Breached`, `Needs Input`으로 번역한다.
  - operator reason / constraints / next action / 원본 trigger list는 `Original Operator Notes` expander로 낮췄다.
  - Trigger Board와 drift 결과는 계속 read-only이며 새 registry row나 주문 row를 만들지 않는다.

### 2026-05-07
- Phase36 Selected Portfolio Dashboard flow 재정렬:
  - user feedback에 따라 source boundary, 운영 대상 필터, Portfolio Blueprint, Monitoring Playbook, Holding Drift Check가 주 성과 재검증 흐름을 흐리는 문제를 확인했다.
  - 데이터 출처 / registry path / raw JSON은 `Audit / Developer Details`로 낮추고, 운영 대상이 1개일 때는 compact selected portfolio picker만 보여주게 했다.
  - Snapshot은 단일 component 100% target allocation table을 접힘 details로 낮추고, Performance Recheck setup은 Original End / DB Latest badge와 primary 실행 버튼으로 재배치했다.
  - Monitoring Playbook을 `Portfolio Monitoring`으로 바꾸고 `Review Signals`, `Why Selected`, `Actual Allocation`, `Audit` 흐름으로 정리했다.
  - Holding Drift Check는 `Actual Allocation Check`로 바꿔 current value 입력을 기본으로 두고, shares x price / current weight / threshold 설정은 advanced 영역으로 낮췄다.
  - Actual Allocation 결과는 사용자가 `Update Review Signals`를 누를 때만 Review Signals에 반영하도록 변경했다.

### 2026-05-06
- Ops Review 운영 대시보드 개편:
  - user confirmation에 따라 기존 `Ops Review`의 최근 결과 / history / logs / failure CSV 나열형 UI를 운영 상태 판독 화면으로 개편했다.
  - 렌더링 책임을 `app/web/ops_review.py`로 분리하고, `streamlit_app.py`는 page entry와 navigation만 유지하게 했다.
  - 상단 triage flow, run health cards, action inbox, 선택 run inspector, failure CSV / related logs / artifact index, 다음 이동 안내, system snapshot을 추가했다.
  - job 실행은 `Workspace > Ingestion`, backtest replay는 `Operations > Backtest Run History`, 후보 replay는 `Operations > Candidate Library`가 맡는 경계를 UI와 flow 문서에 명시했다.

### 2026-05-07
- Compare / saved mix 검증 ownership 정리:
  - user feedback에 따라 `Load Saved Mix Into Compare -> Run Strategy Comparison -> 5단계 Compare 결과` 흐름이 저장 mix 검증처럼 보이는 UX 문제를 확인했다.
  - Compare workspace를 `개별 전략 비교`와 `저장된 비중 조합` 용어로 분리하고, 5단계 Compare 보드는 개별 전략 후보만 Candidate Review로 넘기는 판단임을 명시했다.
  - 저장 mix 화면의 primary action은 `Mix 재실행 및 검증`으로 바꾸고, 기존 load action은 `전략 비교에서 수정하기`라는 편집 / 재구성 경로로 낮췄다.
  - GTAA `interval > 1`, `month_end`에서 요청 종료일이 다음 정상 cadence close 전이면 Data Trust hard block이 아니라 cadence-aligned review로 해석하도록 Compare data trust helper를 보정했다.
  - `Portfolio Mix 검증 보드`는 saved mix의 replay, mix data trust, component Real-Money, workflow registry 기록 여부를 mix-level로 읽고 `포트폴리오 후보 초안으로 보내기`로 Portfolio Proposal에 연결한다.
  - `Reference > Guides`와 `BACKTEST_UI_FLOW.md`를 새 용어와 단계 ownership 기준으로 동기화했다.

### 2026-05-08
- Backtest 후보 선정 workflow 3단계 재설계 사전 분석:
  - user feedback에 따라 Candidate Review / Portfolio Proposal / Final Review가 반복 저장과 중복 비중 조합처럼 보이는 구조를 깊게 분석했다.
  - sub-agent 4개 트랙으로 navigation / Candidate Review registry / Portfolio Proposal-Final Review schema / Guides 문서 영향을 분리 조사했다.
  - 구현 전 기준 문서 `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md`를 추가했다.
  - 핵심 판단은 5개 panel label을 바로 3개로 치환하지 않고, visible stage와 legacy internal route를 먼저 분리하는 것이다.
  - 아직 제품 코드는 수정하지 않았다. 다음 단계는 사용자가 guide 방향을 확인한 뒤 route foundation부터 구현하는 것이다.

### 2026-05-10
- Backtest 후보 선정 workflow 재설계 가이드 보강:
  - user feedback에 따라 기존 JSONL을 꼭 main source로 유지하지 않고 archive한 뒤 Clean V2 저장 구조로 다시 시작하는 옵션을 문서화했다.
  - `PORTFOLIO_SELECTION_SOURCES`, `PRACTICAL_VALIDATION_RESULTS`, `FINAL_PORTFOLIO_SELECTION_DECISIONS_V2`, `SELECTED_PORTFOLIO_MONITORING_LOG`, `SAVED_PORTFOLIO_MIXES`의 역할을 정리했다.
  - 사용자가 `Backtest Analysis -> Practical Validation -> Final Review -> Selected Portfolio Dashboard`를 어떻게 지나 최종 후보 선정과 사후관리를 하는지 end-to-end flow를 추가했다.
  - 제품 코드는 아직 수정하지 않았다. 다음 구현은 Clean V2 storage foundation과 route/stage 분리부터 시작하는 것이 맞다.

### 2026-05-10
- Backtest 후보 선정 workflow Clean V2 1차 구현:
  - `Backtest Analysis -> Practical Validation -> Final Review` 3단계 stage routing을 추가하고 legacy panel request를 새 stage로 매핑했다.
  - `app/web/runtime/portfolio_selection_v2.py`를 추가해 selection source, practical validation result, final decision v2, monitoring log, saved mix helper를 정의했다.
  - Single / History / Compare focused strategy / Saved Mix handoff가 Clean V2 selection source를 만들고 Practical Validation으로 이동하도록 연결했다.
  - Final Review는 Practical Validation result를 읽어 `FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl`에 저장하고, Selected Portfolio Dashboard는 V2 decision registry를 읽도록 바꿨다.
  - 기존 Candidate Review / Portfolio Proposal 코드는 삭제하지 않고 legacy compatibility로 유지했다.

### 2026-05-10
- Compare weighted mix Practical Validation handoff UX 보강:
  - user feedback에 따라 방금 만든 weighted portfolio mix를 저장 mix round-trip 없이 Practical Validation으로 보낼 수 없는 문제를 확인했다.
  - `Weighted Portfolio Result` 아래에 `현재 Mix를 Practical Validation으로 보내기` action을 추가해 mix 전체를 Clean V2 selection source로 저장하게 했다.
  - 저장 mix의 `전략 비교에서 수정하기`는 기존 stale compare / weighted 결과를 숨기고, 저장된 전략 / 기간 / 세부 설정 / weight를 form-first 상태로 다시 채우도록 조정했다.
  - Compare / saved mix 문구와 `BACKTEST_UI_FLOW.md`를 Clean V2 Practical Validation ownership 기준으로 갱신했다.

### 2026-05-10
- Portfolio Mix 검증 보드 legacy 문구 정리:
  - user feedback에 따라 saved mix 판정 문구에 남아 있던 `5~10단계 workflow 통과 기록` 표현을 Clean V2 기준으로 교체했다.
  - saved mix 기록 참조 확인 대상에 `PORTFOLIO_SELECTION_SOURCES`, `PRACTICAL_VALIDATION_RESULTS`, `FINAL_PORTFOLIO_SELECTION_DECISIONS_V2`, `SELECTED_PORTFOLIO_MONITORING_LOG`를 추가했다.

### 2026-05-10
- Practical Validation V2 검증 설계 조사 / 문서화:
  - user request에 따라 현재 Practical Validation이 실제로 검증하는 항목과 실전 후보 검증으로 부족한 부분을 정리했다.
  - CFA backtesting / GIPS / SEC performance presentation / SR 11-7 model validation / overfitting / transaction cost / ETF liquidity reference를 조사해 검증 domain으로 번역했다.
  - `.aiworkspace/note/finance/tasks/active/practical-validation-v2/DESIGN.md`를 추가하고, source contract, replay, benchmark, rolling, drawdown, stress, cost, investability, sensitivity, overfit, monitoring plan domain과 구현 우선순위를 정리했다.
  - 제품 코드는 아직 수정하지 않았다. 다음 작업은 사용자가 설계를 확인한 뒤 Slice 1 domain board부터 구현하는 것이 맞다.
- Practical Validation V2 중복 검증 위험 보강:
  - user feedback에 따라 Practical Validation 이전 단계의 Data Trust / Real-Money / Compare / Saved Mix gate와 V2 설계가 겹칠 수 있는 지점을 확인했다.
  - Practical Validation은 upstream runtime / compare / saved mix 검증을 반복하지 않고 `origin`과 `source_ref`를 남겨 상속 / 통합 / 신규 계산 domain을 분리해야 한다고 정리했다.
  - 설계 문서에 Stage Ownership Matrix와 중복 감점 방지 원칙을 추가했다.
- Practical Validation V2 rolling / cost 기본값 확정:
  - user confirmation에 따라 profile별 rolling window 기본값을 방어형 24개월, 균형형 36개월, 성장형 60개월, 전술 / 헤지형 24개월, 사용자 지정 36개월로 정리했다.
  - cost assumption은 거래 수수료 / bid-ask spread / slippage / 세금성 비용을 포함한 거래비용 가정이며, MVP 기본값은 one-way 10 bps로 시작한다고 문서화했다.
  - research / design 문서의 설계 질문 상태에서 rolling window와 cost assumption 항목을 `O`로 변경했다.
- Practical Validation V2 stress calendar / sentiment connector 보강:
  - user request에 따라 2000년 이후 미국 증시 shock event를 `practical_validation_stress_windows_v1.json` static reference data로 추가했다.
  - stress window는 포트폴리오 curve / benchmark curve를 정적 이벤트 구간으로 잘라 return, MDD, benchmark spread를 계산하는 검증 preset으로 정리했다.
  - sentiment connector는 VIX / credit spread / yield curve 같은 market-context 지표를 Practical Validation에 snapshot으로 붙이는 후속 data adapter라고 문서화했다.
  - research / design 문서의 stress window 설계 질문 상태를 `O`로 변경했다.
- Practical Validation V2 baseline / sensitivity / trial-count 설계 완료:
  - user confirmation에 따라 Alternative Portfolio Challenge 1차 baseline을 SPY, QQQ, 60/40 proxy, cash-aware baseline으로 확정하고 All Weather-like proxy는 후속으로 정리했다.
  - sensitivity perturbation grid는 주요 window perturbation, mix weight +/- 5%p, drop-one, 기존 runtime 지원 범위의 strategy-specific 작은 설정 변경으로 시작한다고 문서화했다.
  - run_history trial count는 원본 파일을 저장하지 않고 `overfit_audit` local summary만 validation row에 선택적으로 남기는 방식으로 정리했다.
- Practical Validation V2 sentiment connector 설계 질문 완료:
  - user confirmation에 따라 sentiment connector는 1차 core 이후 후속 module로 붙이고, FRED 기반 VIX / credit spread / yield curve snapshot부터 시작한다고 확정했다.
  - 해당 데이터는 trade signal이나 hard blocker가 아니라 market-context evidence로만 사용한다고 research / design 문서에 반영했다.
- Practical Validation V2 core 구현:
  - `PRACTICAL_VALIDATION_RESULT_SCHEMA_VERSION`을 2로 올리고, 검증 프로필 / 5개 사용자 답변 / profile threshold resolver를 추가했다.
  - Practical Validation result에 Input Evidence와 12개 Practical Diagnostics board를 추가했다. 현재 구현은 asset allocation proxy, concentration / exposure, stress window coverage, alternative baseline placeholder, leveraged / inverse suitability, cost assumption, local trial count summary, monitoring baseline seed를 생성한다.
  - 아직 실제 return matrix 기반 correlation / risk contribution, baseline replay, stress 구간 성과 재계산, ETF expense / spread / ADV, macro / sentiment connector는 `NOT_RUN` 또는 `REVIEW`로 명시한다.
  - Practical Validation 화면은 profile 입력과 diagnostics board를 표시하고, BLOCKED가 없을 때만 Final Review로 보낸다.
  - Final Review 화면과 final decision snapshot은 Practical Diagnostics 요약 / NOT_RUN critical domain / profile evidence를 함께 읽도록 연결했다.
- Practical Validation V2 정량 진단 1차 보강:
  - profile별 domain weight와 score breakdown을 추가해 검증 profile 변경이 score 산정에 반영되도록 했다.
  - Backtest Analysis handoff에서 compact monthly result curve snapshot을 저장하고, 기존 source는 DB price proxy curve로 계산을 시도하도록 했다.
  - rolling validation, static stress window return / MDD / benchmark spread, SPY / QQQ / 60/40 / cash-aware baseline challenge, component correlation / risk contribution proxy, drop-one / weight +5%p sensitivity를 Practical Diagnostics에 연결했다.
  - ETF operability는 DB price / volume proxy와 one-way cost assumption으로 1차 확인하고, macro / sentiment는 FRED connector 전까지 benchmark price-action proxy로 표시한다.
  - Final Review에는 profile score breakdown, curve evidence, rolling evidence를 snapshot으로 남기도록 연결했다.
- Practical Validation V2 남은 구현 계획 문서화:
  - user request에 따라 추가 개발 전 검토용 문서 `.aiworkspace/note/finance/tasks/active/practical-validation-v2/IMPLEMENTATION_PLAN.md`를 추가했다.
  - 현재 구현 완료 범위와 proxy / NOT_RUN / REVIEW로 남은 범위를 12개 diagnostics domain별로 정리했다.
  - 다음 개발 순서를 helper split, actual runtime replay, benchmark parity, validation inspector, strategy-specific sensitivity, provider connector, Final Review / Selected Dashboard 고도화 순으로 제안했다.
  - 제품 코드는 수정하지 않았고, 사용자가 문서를 검토한 뒤 첫 구현 단위를 확정하는 상태다.
- Practical Validation V2 P0 actual replay / provenance 구현:
  - user confirmation에 따라 helper split, actual runtime replay, curve provenance, benchmark parity hardening을 단계별로 구현했다.
  - `backtest_practical_validation_curve.py`와 `backtest_practical_validation_replay.py`를 추가해 curve/parity와 기존 runtime replay 책임을 분리했다.
  - Practical Validation 화면에 `실제 전략 replay 실행` 버튼을 추가했고, 자동 실행 없이 사용자가 명시 실행할 때만 기존 strategy runtime을 호출한다.
  - validation result schema를 v3로 올리고 `curve_provenance`, `benchmark_parity`, `replay_attempt`를 저장하도록 했다.
  - ETF holdings-level look-through, expense / spread / AUM, FRED macro / sentiment connector는 아직 후속으로 남겼다.
- Practical Validation V2 P0 최신 재검증 의미 보정:
  - user feedback에 따라 동일 기간 replay가 Practical Validation에서 충분한 검증 가치가 있는지 재검토했다.
  - 3번 구간을 `최신 데이터 기준 전략 재검증`으로 바꾸고, 기본 모드는 DB 최신 시장일까지 종료일을 확장한 기존 strategy runtime 재검증으로 조정했다.
  - `저장 기간 그대로 재현`은 보조 모드로 남겼고, validation result schema를 v4로 올려 mode, 저장 기간, 요청 기간, 실제 기간, 최신 시장일, 확장 일수, period coverage, curve provenance를 남기도록 했다.
  - 실제 실행은 성공했지만 component cadence / date alignment 때문에 portfolio curve가 요청 종료일까지 오지 못하면 `period_coverage=REVIEW`로 표시하도록 했다.
  - 관련 code analysis 문서와 comprehensive analysis를 최신 재검증 기준으로 갱신했다.

### 2026-05-11
- Practical Validation V2 P2 개발 문서 정리:
  - user request에 따라 P2 실행 계획 문서 `.aiworkspace/note/finance/tasks/active/practical-validation-v2/CONNECTOR_AND_STRESS_PLAN.md`를 추가했다.
  - provider / DB / loader 상세 설계 문서 `.aiworkspace/note/finance/tasks/active/practical-validation-v2/PROVIDER_CONNECTORS.md`를 추가했다.
  - P2 범위를 Cost / Liquidity / ETF Operability connector, ETF holdings / sector look-through, Macro / Sentiment connector, Stress Interpretation, strategy-specific sensitivity runtime 경계로 정리했다.
  - `IMPLEMENTATION_PLAN.md`, `docs/architecture/README.md`, `FINANCE_DOC_INDEX.md`에 새 문서 링크를 반영했다.
  - 제품 코드는 수정하지 않았다. 다음 작업은 provider connector 첫 구현 단위 확정 후 진행한다.
- Practical Validation V2 provider 문서 compact 관리:
  - user feedback에 따라 별도 data collection plan 문서를 만들지 않기로 했다.
  - ETF holdings, macro series, sentiment series 수집 계획을 기존 `.aiworkspace/note/finance/tasks/active/practical-validation-v2/PROVIDER_CONNECTORS.md` 안에 합쳤다.
  - P2 문서 역할을 `P2 전체 계획`과 `provider 수집 / schema / loader 상세 설계` 두 개로 고정했다.
- Practical Validation V2 P2-1 schema / ingestion field 계약 확정:
  - P2-0에서 정한 8개 정상화 대상 진단을 실제 수집 / 저장 / 로딩 가능한 데이터 계약으로 변환했다.
  - 신규 table 후보를 `etf_operability_snapshot`, `etf_holdings_snapshot`, `etf_exposure_snapshot`, `macro_series_observation` 4개로 고정했다.
  - 각 table의 business key, actual / partial / bridge / proxy / NOT_RUN 판정 기준, ingestion 함수 계약, loader compact context 반환 기준을 문서화했다.
  - 제품 코드는 아직 수정하지 않았다. 다음 작업은 P2-2 Cost / Liquidity / ETF Operability schema와 수집 foundation 구현이다.
- Practical Validation V2 P2-2A ETF operability bridge/proxy foundation 구현:
  - `finance/data/db/schema.py`에 `PROVIDER_SCHEMAS["etf_operability_snapshot"]`를 추가했다.
  - `finance/data/etf_provider.py`를 추가해 기존 `nyse_price_history`와 `nyse_asset_profile` 기반 `db_bridge` operability snapshot을 생성하고 UPSERT 저장하게 했다.
  - `finance/loaders/provider.py`와 loader export를 추가해 `load_etf_operability_snapshot()` read path를 제공했다.
  - 현재 구현은 official issuer actual data 수집이 아니라 bridge/proxy foundation이다. expense ratio, NAV, premium/discount, official leverage/inverse metadata는 P2-2B actual provider 수집에서 보강한다.
  - code analysis / data architecture / comprehensive analysis 문서를 새 table과 loader 경계에 맞춰 갱신했다.
- Practical Validation V2 P2-2B ETF operability official issuer row 초기 구현:
  - `finance/data/etf_provider.py`에 iShares / SSGA / Invesco official page adapter를 추가했다.
  - 초기 source map은 iShares `AOR`, `IEF`, `TLT`, SSGA / SPDR `SPY`, `BIL`, `GLD`, Invesco `QQQ`다.
  - official row는 `etf_operability_snapshot`에 `source=ishares|ssga|invesco`, `source_type=official`, `coverage_status=actual|partial|missing|error`로 저장한다.
  - smoke ingestion 결과 `AOR/IEF/TLT/SPY/BIL/GLD`는 `actual`, `QQQ`는 official QQQ page에서 expense ratio / inception만 확보되어 `partial`로 저장됐다.
  - Practical Validation 진단 연결은 아직 하지 않았고 P2-5에서 loader context를 12개 진단에 연결한다.
- Practical Validation V2 P2-3 ETF holdings / exposure foundation 구현:
  - `finance/data/db/schema.py`에 `etf_holdings_snapshot`, `etf_exposure_snapshot` schema를 추가했다.
  - `finance/data/etf_provider.py`에 iShares holdings CSV, SSGA daily holdings XLSX, Invesco holdings / sector API adapter를 추가했다.
  - holdings는 기본 `canonical_refresh`로 fund / as_of_date / source 범위를 삭제 후 재저장하고, exposure는 holdings aggregate와 provider aggregate sector row를 저장한다.
  - smoke ingestion 결과 holdings는 `AOR/IEF/TLT/SPY/BIL/QQQ` 703 rows actual, `GLD`는 row-level holdings source pending으로 missing 처리됐다.
  - exposure smoke 결과 asset class / sector / country / currency exposure 49 rows actual이 저장되고 loader에서 SPY / QQQ sector aggregate를 확인했다.
  - Practical Validation 진단 연결은 아직 하지 않았고 P2-5에서 Asset Allocation Fit / Concentration / Exposure 진단에 연결한다.
- Practical Validation V2 P2-4 macro / sentiment market-context foundation 구현:
  - `finance/data/db/schema.py`에 `macro_series_observation` schema를 추가했다.
  - `finance/data/macro.py`를 추가해 FRED `VIXCLS`, `T10Y3M`, `BAA10Y` series를 API 또는 official CSV download로 수집하고 UPSERT 저장하게 했다.
  - FRED API key는 hardcode하지 않고 `FRED_API_KEY` 또는 함수 인자로만 받으며, key가 없으면 official CSV download를 사용한다.
  - `finance/loaders/macro.py`와 loader export를 추가해 observation range 조회와 기준일 snapshot / staleness 조회를 제공했다.
  - smoke ingestion 결과 2026-01-01~2026-05-11 구간에서 265 rows를 저장했고, 2026-05-11 기준 3개 series 모두 `snapshot_status=actual`로 로딩됐다.
  - Practical Validation 진단 연결은 아직 하지 않았고 P2-5에서 Regime / Macro Suitability와 Sentiment / Risk-On-Off Overlay 진단에 연결한다.
- Practical Validation V2 P2-5A provider snapshot ingestion UI / job wrapper 연결:
  - `app/jobs/ingestion_jobs.py`에 `run_collect_etf_operability_provider()`, `run_collect_etf_holdings_exposure()`, `run_collect_macro_market_context()`를 추가했다.
  - `Workspace > Ingestion > Practical Validation Provider Snapshots`에서 ETF operability, ETF holdings / exposure, macro context 수집을 실행할 수 있게 했다.
  - 이 단계는 Practical Validation 진단 점수 연결이 아니라, DB snapshot을 채우는 운영 실행 지점 연결이다. 12개 diagnostics provider context 연결은 P2-5B에서 진행한다.
  - smoke 결과 `AOR` operability `success 1 row`, `AOR` holdings / exposure `success 17 rows`, `VIXCLS` 2026-01-01~2026-01-05 macro `success 2 rows`를 확인했다.
- Practical Validation V2 P2-5B provider context diagnostics 연결:
  - `app/web/backtest_practical_validation_connectors.py`를 추가해 ETF operability / holdings / exposure / FRED macro loader 결과를 compact provider context로 변환했다.
  - Practical Validation 2, 3, 5, 6, 9, 10번 진단이 DB provider snapshot을 proxy보다 우선 사용하도록 연결했다.
  - official provider row가 부족하고 bridge / proxy만 있으면 `PASS`로 보이지 않도록 `REVIEW`와 `db_bridge` / `price_proxy` origin을 남기게 했다.
  - Practical Validation과 Final Review 화면에 Provider Coverage 요약 table을 추가했고, Final Review decision snapshot에는 compact provider coverage만 저장한다.
  - smoke 결과 AOR 기준 provider coverage는 operability / exposure / macro `PASS`, holdings concentration `REVIEW`로 표시되고 JSON serialization이 통과했다.

### 2026-05-12
- Practical Validation V2 provider snapshot 기준일 보정:
  - 2026-05-11 `saved_portfolio_mix` source에서 ETF Operability / Holdings Exposure가 수집 후에도 `NOT_RUN`으로 보이는 현상을 확인했다.
  - 원인은 source의 backtest `actual_end=2026-02-28`을 provider snapshot 조회 기준일로 사용해, 2026-05월에 수집된 provider row를 loader가 제외한 것이었다.
  - provider snapshot은 실전 투입 전 현재 검증 근거이므로 조회 기준일을 Practical Validation 실행일로 변경했다.
  - 같은 source 기준으로 operability는 38.5%, holdings / exposure는 30.5% coverage까지 읽히며, 전체 11개 ETF 중 미수집 symbol은 partial `REVIEW`로 남는 것을 확인했다.
- Practical Validation Provider Data Gaps UI / 일괄 수집 보강:
  - Provider Coverage 아래에 ETF별 `Operability / Holdings / Exposure` 부족 여부와 source map 상태를 표시하도록 했다.
  - 같은 화면에서 부족한 operability는 official 또는 DB bridge collector로 보강하고, holdings / exposure는 현재 connector source map이 있는 ETF만 일괄 수집할 수 있게 했다.
  - source map이 없는 ETF는 `connector mapping 필요`로 표시해, 단순 미수집과 connector 미지원 상태를 분리했다.
  - provider context coverage 계산에서 `missing/error` row가 covered symbol로 오해되지 않도록 보정했다.
- Practical Validation V2 provider source map discovery 구현:
  - `finance_meta.etf_provider_source_map` schema를 추가하고, `nyse_etf` + `nyse_asset_profile` 기반으로 ETF별 issuer endpoint / parser mapping을 발견해 저장하게 했다.
  - `finance/data/etf_provider.py`에 iShares product list, SSGA holdings XLSX pattern, Invesco holdings / sector API pattern 검증 경로를 추가했다.
  - `GLD`, `IAU` 같은 금 현물 ETF는 row-level stock holdings가 아니라 `commodity_gold` parser로 100% gold holdings / exposure를 저장하게 했다.
  - Ingestion의 Practical Validation Provider Snapshots에 `Provider Source Map` tab을 추가했고, Practical Validation Provider Data Gaps 버튼은 먼저 source map discovery를 실행한 뒤 수집 plan을 다시 계산한다.
  - smoke 결과 `GLD/IAU/MTUM/QUAL/SOXX/USMV/XLE/XLU` source map 16개 verified row를 저장했고, holdings / exposure 수집은 522 holdings rows, 81 exposure rows를 저장했다.
  - 2026-05-11 `saved_portfolio_mix` source 기준으로 Practical Validation holdings / exposure coverage가 100% actual로 올라가고 `connector mapping needed` 목록이 비는 것을 확인했다.
- Practical Validation V2 operability / sensitivity REVIEW 해석 보강:
  - ETF operability 판정에서 `0.0` spread를 missing으로 오해하던 값을 명시적으로 유효값으로 처리했다.
  - 같은 ETF에 official partial row와 DB bridge row가 함께 있으면 빈 field를 병합해 판단하고, evidence source를 `invesco + db_bridge`처럼 표시하게 했다.
  - saved mix 기준으로 `QQQ`는 official expense ratio와 DB bridge AUM / ADV / spread를 합쳐 PASS, `XLU`는 0.00% spread를 정상 인식해 PASS로 바뀌었다.
  - Robustness / Sensitivity는 window perturbation을 curve 기반으로 계산하고, summary 문구를 "일부 계산 완료 / strategy-specific runtime은 별도 실행 필요"로 분리했다.
- Practical Validation V2 P2-6 stress / sensitivity interpretation 구현:
  - Stress / Scenario Diagnostics가 covered stress window와 실제 계산 완료 window를 분리해, compact monthly curve 때문에 daily replay가 필요한 구간을 `REVIEW` trigger로 표시하게 했다.
  - Stress interpretation row에 worst computed MDD, benchmark spread, return shock, 현재 macro / exposure lens를 추가했다.
  - Robustness / Sensitivity는 rolling / window / component dependency / weight tilt / strategy runtime follow-up을 별도 interpretation row로 요약하게 했다.
  - Practical Validation과 Final Review의 Robustness summary에서 Stress / Sensitivity Interpretation tab을 읽을 수 있게 했다.
- Backtest report content-oriented migration:
  - user feedback에 따라 `candidates/point_in_time/`를 현재 후보 폴더처럼 유지하지 않기로 했다.
  - Value / Quality / Quality + Value rerun 근거는 전략별 backtest log에 남아 있으므로 standalone candidate report를 제거했다.
  - weighted portfolio baseline / weight alternative / saved replay 근거는 `validation/runtime/WEIGHTED_PORTFOLIO_REPLAY_VALIDATION.md`로 내용 중심 재작성했다.
  - validation smoke report 파일명은 phase 번호 대신 `QUARTERLY_CONTRACT_RUNTIME_SMOKE`, `GLOBAL_RELATIVE_STRENGTH_RUNTIME_SMOKE`, `GLOBAL_RELATIVE_STRENGTH_UI_REPLAY_SMOKE`로 정리했다.
  - backtest report README / INDEX / migration / validation README를 새 구조에 맞춰 갱신했다.
- Data architecture 문서 docs/data 마이그레이션:
  - 기존 `.aiworkspace/note/finance/data_architecture/`의 `DATA_FLOW_MAP`, `DB_SCHEMA_MAP`, `TABLE_SEMANTICS`, `DATA_QUALITY_AND_PIT_NOTES`를 `.aiworkspace/note/finance/docs/data/`로 이동했다.
  - `docs/data/README.md`를 데이터 문서 입구로 확장해 읽는 순서, DB 그룹, JSONL boundary, 갱신 기준을 합쳤다.
  - `AGENTS.md`, `FINANCE_COMPREHENSIVE_ANALYSIS.md`, `FINANCE_DOC_INDEX.md`, phase / operations README, Practical Validation P2 계획의 data 문서 경로를 새 canonical 위치로 갱신했다.
  - 기존 `.aiworkspace/note/finance/data_architecture/` 폴더는 제거했다.
- Documentation System Rebuild Reference / Glossary 1차 안전장치:
  - `Reference > Guides`가 md 본문을 읽는 구조가 아니라 `app/web/reference_guides.py`의 guide text와 문서 경로 목록을 렌더링하는 구조임을 확인했다.
  - `Reference > Glossary`는 실제 md를 읽는 화면이므로 기존 root glossary 본문을 `.aiworkspace/note/finance/docs/GLOSSARY.md`로 승격하고 앱 읽기 경로를 새 docs 구조로 바꿨다.
  - `Reference > Guides`의 old root / operations / phase36 / code_analysis 문서 경로를 새 `.aiworkspace/note/finance/docs/` 문서 경로로 교체했다.
  - 삭제 전 1차 안전장치만 완료했으며, 남은 legacy root / operations / research / support 문서의 흡수 여부 판단은 다음 단계로 남겼다.
- Documentation System Rebuild 2차 legacy 흡수:
  - legacy root current-state docs는 새 `docs/INDEX.md`, `PROJECT_MAP.md`, `ROADMAP.md`, `GLOSSARY.md`로 대체 가능한 것으로 정리했다.
  - operations registry guide 핵심은 `.aiworkspace/note/finance/registries/README.md`에 current Selection V2 / legacy compatibility 기준으로 흡수했다.
  - runtime artifact hygiene, external research, config externalization 원칙은 `docs/runbooks/README.md`로 축약했다.
  - `research/practical_validation_stress_windows_v1.json`은 런타임 reference data로 확인되어 `.aiworkspace/note/finance/docs/data/`로 이동하고 `STRESS_WINDOW_FILE` 경로를 갱신했다.
  - Practical Validation investment diagnostics research 참조는 active task `DESIGN.md`에 흡수된 기준으로 바꿨고, 3차 삭제 후보 / 유지 주의사항을 doc-system-rebuild `NOTES.md`, `RISKS.md`에 기록했다.
- Documentation System Rebuild 3차 legacy 제거:
  - 새 docs 구조로 대체된 root current-state docs, `archive/`, `operations/`, 남은 `research/`, `support_tracks/`를 제거했다.
  - 기존 `phases/phase1`~`phases/phase36` 상세 문서는 현재 구현과 맞지 않는 legacy history로 보고 제거했다.
  - phase plan / checklist template은 삭제하지 않고 `.aiworkspace/note/finance/docs/runbooks/templates/`로 이동했다.
  - `bootstrap_finance_phase_bundle.py`는 새 template 경로를 읽고 `.aiworkspace/note/finance/phases/active/phase<N>/`에 bundle을 생성하도록 갱신했다.
  - `registries/`, `saved/`, root handoff log, active task docs는 보존했다.
- README 대규모 재작성:
  - 오래된 구현 목록 중심 README를 제거하고, 현재 finance 제품 boundary / 사용 흐름 / quick start / 문서 map 중심으로 다시 작성했다.
  - 사용자-facing program flow를 Mermaid chart로 추가해 `Ingestion -> Backtest Analysis -> Practical Validation -> Final Review -> Selected Portfolio Dashboard` 흐름을 첫 화면에서 이해할 수 있게 했다.
  - 상세 구현과 active progress는 README에 중복하지 않고 `.aiworkspace/note/finance/docs/`와 active task 문서로 연결하는 구조로 정리했다.
- Root handoff log 운영 지침 추가:
  - `WORK_PROGRESS.md`와 `QUESTION_AND_ANALYSIS_LOG.md`는 root handoff map으로 유지하고, 상세 기록은 active task 문서로 보내는 기준을 `AGENTS.md`와 `docs/runbooks/README.md`에 추가했다.
  - root log는 작업 단위당 3~5줄 milestone / decision 중심으로 남기고, 실행 명령 / 긴 분석 / 시행착오는 `RUNS.md`, `NOTES.md`, `DESIGN.md`로 분리한다.
- Skill System Rebuild 1차:
  - `.aiworkspace/note/finance/tasks/active/skill-system-rebuild/`를 열고 stale skill path 보정 작업을 기록했다.
  - `finance-backtest-web-workflow`, `finance-db-pipeline`, `finance-factor-pipeline`, `finance-strategy-implementation`, `finance-doc-sync`가 새 `.aiworkspace/note/finance/docs/` 구조를 참조하도록 수정했다.
  - legacy `finance-phase-management` skill은 삭제했고, roadmap에 skill rebuild active track을 추가했다.
- Skill System Rebuild 2차:
  - 새 `finance-task-management` skill을 만들어 task 분류, active task 운영, root handoff log 관리를 담당하게 했다.
  - Backtest UI / DB / factor / strategy skill은 domain implementation skill로 경계를 보정하고, `finance-doc-sync`는 closeout alignment skill로 좁혔다.
  - `AGENTS.md`와 skill-system-rebuild task 문서에 skill routing 기준과 검증 결과를 기록했다.
- Skill System Rebuild 3차:
  - finance project skill 원본을 repo-local `.aiworkspace/plugins/quant-finance-workflow/skills/`로 옮기고, global `~/.codex/skills/finance-*`는 mirror 설치본으로 동기화했다.
  - 6개 finance skill의 `SKILL.md`를 trigger / first-read / core workflow 중심으로 줄이고, 긴 domain rule은 `references/`로 분리했다.
  - 4차에는 plugin placeholder와 실제 skill trigger / 설치 흐름 검증이 남아 있다.
- AI Workspace Migration:
  - `.note/finance`와 `plugins/quant-finance-workflow`를 `.aiworkspace/note/finance`, `.aiworkspace/plugins/quant-finance-workflow` canonical 구조로 이동했다.
  - 코드 / 문서 / skill의 주요 경로를 새 AI workspace 기준으로 갱신하고 `.aiworkspace/README.md`를 추가했다.
  - run history의 기존 로컬 수정은 새 위치에 unstaged artifact로 보존한다.
- Skill System Rebuild 3차 post-migration 보강:
  - repo-local `finance-backtest-candidate-refinement` skill에 남아 있던 old phase report 중심 표현을 새 `reports/backtests` / registry-backed candidate evidence 흐름으로 정리했다.
  - 7개 repo-local finance skill의 `agents/openai.yaml` default prompt를 `$skill-name` 명시 방식으로 보정했다.
  - 활성 6개 finance skill mirror를 다시 동기화했고, 다음 작업은 4차 plugin placeholder / trigger 점검이다.
- Skill System Rebuild 4차 완료:
  - `quant-finance-workflow` plugin manifest에서 TODO placeholder와 없는 hooks / MCP / app / asset 참조를 제거했다.
  - `.agents/plugins/marketplace.json`이 실제 plugin root인 `./.aiworkspace/plugins/quant-finance-workflow`를 가리키도록 수정했다.
  - repo-local 7개 skill, global mirror 6개 skill, marketplace path, manifest JSON 검증을 완료했다.
- Skill System Rebuild taxonomy 보정:
  - 사용자가 정의한 공통 workflow 4개 + 구현 domain 4개 구조로 skill bundle을 다시 맞췄다.
  - `finance-task-management`는 `finance-task-intake`로 rename했고, `finance-integration-review`, `finance-runbook-maintainer`를 추가했다.
  - `finance-backtest-candidate-refinement`는 phase worktree 공통 skill에서 제거했다.
- AI Workspace README 갱신:
  - `.aiworkspace/README.md`를 현재 `note/finance`와 `plugins/quant-finance-workflow` 구조 기준으로 재작성했다.
  - 4 workflow + 4 domain skill taxonomy, 읽는 순서, artifact / registry 경계, skill 검증 명령을 첫 관문 문서에 반영했다.
- Product Research 2단계 UI platform 조사:
  - Streamlit 기반 UX/UI를 Python quant engine + API + React/Next.js 구조로 분리할지 검토하는 active research bundle을 열었다.
  - 현행 `app/web` 구조, Streamlit coupling, session state 사용, durable workflow docs를 audit했다.
  - 공식 문서/제품 페이지 기준으로 Streamlit, FastAPI, Next.js, Dash, QuantConnect, QuantRocket, OpenBB, TradingView, Composer를 비교했다.
  - 결론과 산출물은 `.aiworkspace/note/finance/researches/active/2026-05-ui-platform-research/RECOMMENDATION.md`부터 보면 된다.
- Product Research 3단계 skill hardening:
  - 2단계 UI platform research 실행 복기 결과를 `.aiworkspace/note/finance/tasks/active/product-research-skill-stage3/`에 기록했다.
  - `finance-task-intake`, `finance-product-audit`, `finance-benchmark-research`, `finance-feature-opportunity`가 research run과 skill hardening, product surface 분류, architecture benchmark, pilot/roadmap 구분을 더 명확히 안내하도록 보강했다.
  - repo-local skill source와 global `~/.codex/skills` mirror 정합성 검증을 완료했다.
- Product Research 4단계 반복 run - Backtest Report Productization:
  - `Backtest Result / Strategy Report` 제품화 주제로 `.aiworkspace/note/finance/researches/active/2026-05-backtest-report-productization/` 리서치 번들을 작성했다.
  - 현행 `reports/backtests`, Streamlit result display, run history, validation/final review replay 구조를 audit했다.
  - QuantConnect, QuantRocket, TradingView, QuantStats/pyfolio, NautilusTrader 패턴을 바탕으로 `BacktestReportPack + Markdown draft generator`를 다음 구현 후보로 추천했다.
- Product Research 5단계 plugin workflow hardening:
  - `.aiworkspace/note/finance/tasks/active/product-research-plugin-stage5/`에서 product research workflow를 plugin 수준으로 고정했다.
  - `finance-product-research-workflow` orchestration skill과 research bundle bootstrap/check helper script를 추가했다.
  - 기존 두 active research bundle 검증, skill quick validation, plugin JSON validation, mirror sync를 완료했다.
- Product Research plugin 분리:
  - product research 관련 4개 skill과 helper script 2개를 별도 `.aiworkspace/plugins/quant-finance-product-research/` plugin으로 이동했다.
  - 기존 `quant-finance-workflow`는 task intake / doc sync / integration / runbook / implementation skill 중심으로 가볍게 정리했다.
  - marketplace에 두 plugin을 모두 등록하고 skill validation, script dry-run, active research bundle check, mirror sync를 완료했다.
- Service Contract Tests:
  - `.aiworkspace/note/finance/tasks/active/service-contract-tests/`를 열고 UI-engine boundary 후속 QA를 단일 task로 진행했다.
  - `tests/test_service_contracts.py`를 추가해 Practical Validation handoff와 Final Review evidence read model contract를 `unittest`로 검증한다.
  - 검증 명령은 `.aiworkspace/note/finance/docs/runbooks/README.md`와 script map / project map에 반영했다.
- Provider Gap Collection Boundary:
  - `.aiworkspace/note/finance/tasks/active/provider-gap-collection-boundary/`를 열고 Practical Validation Provider Data Gaps 수집 책임을 service로 이동했다.
  - `app/web/backtest_practical_validation.py`는 provider gap 표시 / 버튼 / session state만 맡고, `app/services/backtest_practical_validation.py`가 row / plan / ingestion orchestration을 맡는다.
  - `tests/test_service_contracts.py`에 provider gap plan / mocked job orchestration contract를 추가했다.
- Practical Validation Replay Service Boundary:
  - `.aiworkspace/note/finance/tasks/active/practical-validation-replay-service-boundary/`를 열고 Streamlit-free replay helper를 `app/services/backtest_practical_validation_replay.py`로 이동했다.
  - Practical Validation UI는 replay mode 선택 / 버튼 / session state / 결과 표시만 맡고, service가 recheck plan과 actual replay result를 만든다.
  - `tests/test_service_contracts.py`에 replay plan / blocked replay contract를 추가했다.
- UI Engine Boundary Cleanup Task 8:
  - `.aiworkspace/note/finance/tasks/active/runtime-wrapper-cleanup/`를 열고 `app/runtime/backtest.py` 함수군과 public caller surface를 지도화했다.
  - `build_backtest_result_bundle`을 `app/runtime/backtest_result_bundle.py`로 분리하되 `app.runtime.backtest` / `app.runtime` public export는 유지했다.
  - result bundle compatibility / shape contract tests를 추가했고 다음 작업은 Task 9 boundary contract hardening이다.
- UI Engine Boundary Cleanup Task 9 / phase closeout:
  - `.aiworkspace/note/finance/tasks/active/boundary-contract-hardening/`에서 `app.services/app.runtime -> app.web` import를 boundary lint hard failure로 승격했다.
  - `tests/test_service_contracts.py`에 boundary checker behavior contract를 추가했고 service contract suite는 22 tests로 확장됐다.
  - `ui-engine-boundary-cleanup` phase는 Task 6~9 완료 상태로 closeout했다.
- Canonical Finance Note Paths:
  - `.aiworkspace/note/finance/tasks/active/canonical-finance-note-paths/`를 열고 legacy `.note/finance` 직접 참조를 정리했다.
  - `app/workspace_paths.py`를 추가해 `registries`, `saved`, `run_history`, `run_artifacts`, docs path를 canonical `.aiworkspace/note/finance` 기준으로 통일했다.
  - Overview browser smoke에서 Current Candidates / Paper Tracking / Proposal Drafts / Recent Runs가 canonical JSONL 데이터를 읽는 것을 확인했다.
- Overview Market Intelligence research:
  - `.aiworkspace/note/finance/researches/active/2026-05-overview-market-intelligence/`를 열고 Overview 개편 feasibility를 조사했다.
  - Coverage 1000/2000 top movers와 sector / industry leadership은 기존 DB price/profile로 가능하다는 결론을 남겼다.
  - FOMC calendar는 low-risk next slice, earnings calendar는 provider/API/persistence 결정 이후로 분리했다.
- Overview Market Intelligence first slice:
  - `.aiworkspace/note/finance/phases/active/overview-market-intelligence/`와 `.aiworkspace/note/finance/tasks/active/overview-market-intelligence-first-slice/`에서 scope lock 후 구현했다.
  - `app/services/overview_market_intelligence.py`가 local DB 기반 market movers와 sector / industry leadership snapshot을 생성한다.
  - Overview는 Market Movers / Sector-Industry / Events / Candidate Ops 탭 구조로 바뀌었고, calendar ingestion은 후속 task로 남겼다.
- Overview Market Intelligence S&P 500 intraday slice:
  - `.aiworkspace/note/finance/tasks/active/overview-market-intelligence-sp500-intraday/`에서 S&P 500 current universe와 daily previous-close snapshot 방향을 구현했다.
  - `finance/data/market_intelligence.py`와 `finance_price.market_intraday_snapshot` / `finance_meta.market_universe_member`가 추가됐다.
  - Market Movers는 S&P 500 / Top1000 / Top2000, yearly period, sector filter, missing diagnostics를 제공한다.
  - 상단 controls를 segmented control bar와 refresh status bar로 다듬고, S&P 500 daily snapshot이 5분 기준으로 stale이면 update-needed dot / 버튼이 보이도록 했다.
  - S&P 500 snapshot refresh 기본 경로를 Yahoo quote batch fast path로 바꾸고, yfinance 5m OHLCV를 fallback으로 남겼다. Local smoke에서 503개 quote snapshot 저장은 6.514초가 걸렸다.
  - Streamlit이 이전 job-wrapper import를 잡은 상태에서 `quote_batch_size` TypeError가 나던 UI click path를 수정했고, 재시작 후 브라우저에서 503개 snapshot 저장이 7.377초로 완료되는 것을 확인했다.
  - Top1000 / Top2000 daily intraday refresh를 같은 `market_intraday_snapshot` 저장 구조로 확장했다. Local smoke에서 Top1000은 1000 rows / 9.322초, Top2000은 2000 rows / 16.0초로 저장됐고 Overview가 intraday snapshot을 우선 표시한다.
- Overview Market Intelligence Task 4 / Market Event DB Structure:
  - `.aiworkspace/note/finance/tasks/active/overview-market-events-schema/`를 열고 `finance_meta.market_event_calendar` schema를 추가했다.
  - `finance/data/market_intelligence.py`에 event row normalize, `event_key` 기반 UPSERT, date-range read helper를 추가했다.
  - Local DB smoke에서 requested common event columns가 생성된 것을 확인했고, 다음 task는 FOMC collector다.
- Overview Market Intelligence 2차 production baseline:
  - `.aiworkspace/note/finance/phases/active/overview-market-intelligence-productionization/`의 2차 task 2-01~2-03을 완료했다.
  - Market Movers는 refresh state와 missing recommended action을 보여주고, Events는 official / provider estimate / stale estimate read model을 제공한다.
  - 2차 acceptance checklist와 runbook을 정리했고, 다음 단계는 3차 earnings source validation이다.
- Overview Market Intelligence 3차 earnings production baseline:
  - 3차 task 3-01~3-03을 완료해 earnings row에 source validation / lifecycle metadata를 저장한다.
  - yfinance earnings estimate는 선택적으로 Nasdaq earnings calendar와 cross-check하고, 변경된 이전 estimate는 superseded / stale 상태로 정리한다.
  - Ingestion은 latest movers 외에 S&P 500 / Top1000 / Top2000 low-frequency batch 수집을 지원하며 다음 단계는 4차 visuals / calendar UX polish다.
- Overview Market Intelligence 5차 ops hardening:
  - `.aiworkspace/note/finance/tasks/active/overview-mi-ops-hardening/`에서 Overview `Data Health` 탭을 추가했다.
  - Data Health는 DB freshness와 local `WEB_APP_RUN_HISTORY.jsonl`을 결합해 6개 수집 대상의 OK / Stale / Missing / Failed / Partial 상태와 next action을 보여준다.
  - Overview refresh buttons가 실행 결과를 local web app run history에 남기도록 연결했고, service contract / browser smoke 검증을 완료했다.
- Overview Market Intelligence 6차 macro calendar:
  - `.aiworkspace/note/finance/tasks/active/overview-mi-macro-calendar/`에서 BLS / BEA official macro release calendar collector를 추가했다.
  - Events는 `Macro` filter와 `Refresh Macro Calendar` 버튼을 제공하고, Data Health는 Macro Calendar coverage를 7번째 운영 대상으로 표시한다.
  - Local smoke에서 BEA GDP 13개 row 저장은 성공했고, BLS는 HTTP 403으로 차단되어 partial failure로 노출되는 것을 확인했다.
- Overview MI Sector / Industry trend:
  - `.aiworkspace/note/finance/tasks/active/overview-mi-sector-leadership-trend/`에서 Sector / Industry Leadership을 최신 랭킹 + 기간별 추세 화면으로 개편했다.
  - Coverage는 S&P 500 / Top1000 / Top2000을 지원하고, Period는 Daily / Weekly / Monthly로 선택한다.
  - Daily 1개월, Weekly 3개월, Monthly 6개월 trend rows를 DB price history에서 계산하며 browser smoke와 service contract 56 tests를 통과했다.
- Overview MI Sector / Industry detail polish:
  - Sector / Industry trend horizon을 Daily 3개월, Weekly 6개월, Monthly 1년으로 확장했다.
  - Trend Groups multiselect로 라인별 표시를 제어하고, 양수 그룹에는 티커 리더 bar / return-share donut 상세를 추가했다.
  - Service contract 56 tests, module compile, browser smoke를 통과했다.
- Overview MI Sector / Industry daily intraday:
  - Sector / Industry `Daily`는 Market Movers와 같은 `market_intraday_snapshot`을 우선 읽도록 연결했다.
  - Latest Ranking / Positive Group Detail은 `Previous Close -> latest quote` 기준으로 계산하고, Weekly / Monthly는 기존 EOD DB 기준을 유지한다.
  - UI에 Return Window와 Price Mode를 표시해 intraday / EOD 기준 차이를 드러냈다.
