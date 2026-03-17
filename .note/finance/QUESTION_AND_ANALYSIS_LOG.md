# Finance Question And Analysis Log

## Purpose
This file stores durable summaries of `finance`-related questions, design interpretations, and analysis outcomes.

Use this for:
- architecture discussions
- feature planning decisions
- package understanding summaries
- guidance that should survive beyond one conversation turn

Do not copy full chat transcripts. Keep only the durable result.

## Entries

### 2026-03-11 - Finance package structure analysis
- Request topic:
  - understand the `finance` package structure and summarize it for future conversations
- Interpreted goal:
  - produce a stable project context document for continued collaboration
- Result:
  - analyzed `finance` excluding `financial_advisor`
  - identified the package as a combined data-ingestion and quant-backtest workspace
  - documented data, transform, strategy, engine, performance, and DB layers
- Durable output:
  - `.note/finance/FINANCE_COMPREHENSIVE_ANALYSIS.md`

### 2026-03-11 - Agent and skill design guidance
- Request topic:
  - propose how to structure agents and skills for this project
- Interpreted goal:
  - define a lightweight but durable operating model for future `finance` development
- Result:
  - recommended a small number of role-oriented agents rather than many narrow agents
  - prioritized skills over agent proliferation because the project has strong repeatable workflows
  - identified four core skills:
    - finance-doc-sync
    - finance-db-pipeline
    - finance-strategy-implementation
    - finance-factor-pipeline
- Durable output:
  - project-level `AGENTS.md`
  - skills under `/Users/taeho/.codex/skills/`

### 2026-03-11 - OHLCV and financial ingestion implementation check
- Request topic:
  - verify whether OHLCV DB ingestion and financial statement DB ingestion are already implemented
- Interpreted goal:
  - separate already-built ingestion capabilities from still-missing operational pieces before new implementation work begins
- Result:
  - confirmed OHLCV DB ingestion exists via `store_ohlcv_to_mysql(...)`
  - confirmed normalized fundamentals ingestion exists via `upsert_fundamentals(...)`
  - confirmed detailed financial statement ingestion exists via `upsert_financial_statements(...)`
  - confirmed factor derivation pipeline exists via `upsert_factors(...)`
  - identified main gaps as:
    - incremental ingestion
    - `end` handling in OHLCV ingestion path
    - point-in-time enforcement
    - DB-backed backtest integration
    - orchestration, validation, and test coverage
- Durable output:
  - `.note/finance/OHLCV_AND_FINANCIAL_INGESTION_REVIEW.md`

### 2026-03-11 - Data collection UI planning
- Request topic:
  - define how to build a web or GUI program that makes daily data collection easy through buttons
- Interpreted goal:
  - decide the right first operational interface before implementing the full DB-driven backtest product
- Result:
  - framed the target as an internal admin console rather than a public product UI
  - compared desktop GUI, internal web app, and CLI-first approaches
  - recommended starting with a lightweight internal web app
  - recommended separating:
    - UI layer
    - job wrapper layer
    - existing finance/data ingestion logic
  - recommended phased rollout:
    - manual button execution first
    - run result display
    - execution history
    - scheduler later
- Durable output:
  - `.note/finance/DATA_COLLECTION_UI_STRATEGY.md`

### 2026-03-11 - Internal web app development sequence
- Request topic:
  - produce a concrete step-by-step implementation guide for the internal web app
- Interpreted goal:
  - define an execution order that can be followed directly during development
- Result:
  - produced a phased guide from scope definition to job wrapper design, web app shell, button wiring, result rendering, run history, and pipeline execution
  - centered the first implementation on:
    - Streamlit
    - wrapper jobs
    - OHLCV / fundamentals / factors first
- Durable output:
  - `.note/finance/INTERNAL_WEB_APP_DEVELOPMENT_GUIDE.md`

### 2026-03-11 - Phase 1 web app scope definition
- Request topic:
  - start Phase 1 of the internal web app plan
- Interpreted goal:
  - lock the first-release feature boundary before code implementation begins
- Result:
  - fixed Phase 1 scope around a minimal internal admin console
  - included only:
    - OHLCV ingestion
    - fundamentals ingestion
    - factor calculation
    - run result visibility
  - explicitly excluded backtest UI, automation, complex frontend, and multi-user features
- Durable output:
  - `.note/finance/PHASE1_WEB_APP_SCOPE.md`

### 2026-03-11 - Phase 1 job wrapper interface planning
- Request topic:
  - continue Phase 1 planning after scope definition
- Interpreted goal:
  - define the execution boundary between the future web UI and existing ingestion functions
- Result:
  - fixed the first wrapper targets to:
    - OHLCV ingestion
    - fundamentals ingestion
    - factor calculation
  - defined a common result payload for UI integration
  - recommended a thin wrapper layer rather than rewriting ingestion logic
- Durable output:
  - `.note/finance/PHASE1_JOB_WRAPPER_INTERFACE.md`

### 2026-03-11 - Phase 1 job wrapper implementation
- Request topic:
  - proceed to the next implementation step after wrapper interface planning
- Interpreted goal:
  - turn the wrapper design into executable code that the future web UI can call directly
- Result:
  - created `app/jobs/ingestion_jobs.py`
  - implemented:
    - `parse_symbols(...)`
    - `_build_result(...)`
    - `run_collect_ohlcv(...)`
    - `run_collect_fundamentals(...)`
    - `run_calculate_factors(...)`
  - kept the layer thin by reusing existing `finance/data/*` ingestion functions
- Durable output:
  - `app/jobs/ingestion_jobs.py`

### 2026-03-11 - Phase 1 Streamlit shell implementation
- Request topic:
  - proceed to the next step after job wrapper implementation
- Interpreted goal:
  - create the first executable internal web UI that can trigger the wrapper jobs directly
- Result:
  - added Streamlit as a project dependency
  - created `app/web/streamlit_app.py`
  - implemented:
    - shared sidebar inputs
    - three execution buttons
    - result summary rendering
    - in-session recent run history
- Durable output:
  - `app/web/streamlit_app.py`

### 2026-03-11 - OHLCV button responsiveness review
- Request topic:
  - review why the OHLCV button appears unresponsive while fundamentals and factors finish quickly
- Interpreted goal:
  - distinguish between UI issues and actual ingestion failure before deeper debugging
- Result:
  - reproduced the OHLCV wrapper successfully outside the UI
  - confirmed the path completes, but it blocks synchronously during yfinance download
  - identified that the app showed no progress state during execution, making the button look inactive
  - also removed yfinance console progress output from the OHLCV path
- Durable output:
  - UI now shows Streamlit spinners during execution
  - `get_ohlcv(...)` now calls `yf.download(..., progress=False)`

### 2026-03-11 - Log and failure visibility for admin UI
- Request topic:
  - continue the next phase of the internal web app after establishing the first executable shell
- Interpreted goal:
  - make the app usable as an operational tool by exposing recent logs and failure artifacts
- Result:
  - added recent log file selection and tail preview
  - added recent failure CSV selection and table preview
  - kept the implementation file-based and lightweight for Phase 1
- Durable output:
  - `app/web/streamlit_app.py`

### 2026-03-11 - Core pipeline execution button
- Request topic:
  - move to the next step after log and failure visibility
- Interpreted goal:
  - provide a single action for the most common operational sequence instead of forcing three separate manual clicks
- Result:
  - created a composite wrapper for the core sequence:
    - OHLCV
    - fundamentals
    - factors
  - added a `Run Core Pipeline` button to the admin UI
  - added per-step summaries inside the result details
- Durable output:
  - `app/jobs/ingestion_jobs.py`
  - `app/web/streamlit_app.py`

### 2026-03-11 - Persistent run history for web app
- Request topic:
  - proceed to the next implementation step after adding the core pipeline button
- Interpreted goal:
  - preserve execution history across Streamlit session restarts so the app can function more like an operational console
- Result:
  - added JSONL-based run history persistence under `.note/finance/`
  - appended each executed job result to persistent history
  - added a persistent run history table to the Streamlit UI
- Durable output:
  - `app/jobs/run_history.py`
  - `app/web/streamlit_app.py`

### 2026-03-11 - Admin UI expansion for additional ingestion jobs
- Request topic:
  - extend the web app beyond the core pipeline to cover more of the finance ingestion system
- Interpreted goal:
  - make the admin tool closer to the full data-ingestion surface already implemented in the project
- Result:
  - added asset profile collection wrapper and UI button
  - added detailed financial statement ingestion wrapper and UI button
  - exposed additional financial-statement parameters in the sidebar
- Durable output:
  - `app/jobs/ingestion_jobs.py`
  - `app/web/streamlit_app.py`

### 2026-03-11 - UI guidance and precondition clarity
- Request topic:
  - improve the app by making each job's preconditions and input behavior clearer in the UI
- Interpreted goal:
  - reduce ambiguity about which jobs use `Symbols` and which jobs depend on prior ingestion steps
- Result:
  - added a top-level app note explaining shared input behavior
  - added job-level captions describing:
    - whether `Symbols` is used
    - execution order recommendations
    - preconditions for factor calculation
    - why asset profile collection behaves differently
    - why financial statement ingestion may be slower
- Durable output:
  - `app/web/streamlit_app.py`

### 2026-03-11 - Pre-execution validation in admin UI
- Request topic:
  - improve execution stability by validating job prerequisites before the user clicks run
- Interpreted goal:
  - move beyond static guidance text and expose simple operational readiness checks in the UI
- Result:
  - added symbol-presence validation
  - added factor prerequisite checks against MySQL:
    - price data existence
    - fundamentals existence
  - added asset profile prerequisite checks against NYSE universe tables
  - surfaced these checks in the UI as info/warning/error blocks with optional details
- Durable output:
  - `app/jobs/preflight_checks.py`
  - `app/web/streamlit_app.py`

### 2026-03-11 - Invalid symbol handling fix
- Request topic:
  - review why a clearly invalid symbol like `야호` still produced a pipeline result that looked partially successful
- Interpreted goal:
  - make invalid input fail early instead of silently flowing into ingestion and returning misleading status
- Result:
  - identified that prior validation only checked for non-empty input
  - added symbol format validation
  - changed wrappers so no-row outcomes no longer appear as partial success
  - confirmed `야호` now fails immediately in both preflight and execution layers
- Durable output:
  - `app/jobs/ingestion_jobs.py`
  - `app/jobs/preflight_checks.py`

### 2026-03-11 - UX cleanup phase start
- Request topic:
  - move to the UX-cleanup phase after invalid-symbol handling was confirmed
- Interpreted goal:
  - reduce user confusion and prevent obviously bad executions before they start
- Result:
  - grouped sidebar inputs by job context
  - reused validation results across the page instead of recalculating inline
  - disabled execution buttons when validation reaches blocking error state
- Durable output:
  - `app/web/streamlit_app.py`

### 2026-03-11 - Job-local input UX
- Request topic:
  - continue the UX-cleanup phase by separating inputs per job instead of sharing a large common input area
- Interpreted goal:
  - make it obvious which input fields affect which execution buttons
- Result:
  - replaced the shared input model with job-local inputs embedded in each card
  - each execution block now owns the fields it actually uses
  - validation state is now shown next to the specific job it affects
- Durable output:
  - `app/web/streamlit_app.py`

### 2026-03-11 - Preset-based repeated-operation UX
- Request topic:
  - continue UX cleanup by improving repeated-use ergonomics
- Interpreted goal:
  - reduce manual typing for common admin workflows
- Result:
  - added symbol presets:
    - Big Tech
    - Core ETFs
    - Dividend ETFs
    - Custom
  - added period presets for OHLCV and pipeline jobs
  - preserved custom manual entry paths for non-preset runs
- Durable output:
  - `app/web/streamlit_app.py`

### 2026-03-11 - Execution stability visibility improvement
- Request topic:
  - prioritize execution stability improvements instead of preset management
- Interpreted goal:
  - make failed and zero-row runs easier to diagnose from the admin UI
- Result:
  - strengthened zero-row result messages for OHLCV, fundamentals, factors, and financial statements
  - added failed-symbol counts to the summary cards
  - changed pipeline-step rendering from plain text lines to a table
  - improved recent-run visibility for failure counts
- Durable output:
  - `app/jobs/ingestion_jobs.py`
  - `app/web/streamlit_app.py`

### 2026-03-11 - DB-backed all-symbol source selection
- Request topic:
  - support running jobs against all tracked symbols instead of manually typing symbol lists
- Interpreted goal:
  - make daily or weekly OHLCV and related ingestion practical at scale
- Result:
  - added selectable symbol sources for symbol-based jobs
  - supported sources:
    - Manual
    - NYSE Stocks
    - NYSE ETFs
    - NYSE Stocks + ETFs
    - Profile Filtered Stocks
    - Profile Filtered ETFs
    - Profile Filtered Stocks + ETFs
  - kept manual preset workflow for smaller ad hoc runs
- Durable output:
  - `app/jobs/symbol_sources.py`
  - `app/web/streamlit_app.py`

### 2026-03-11 - UI write-target transparency
- Request topic:
  - make it explicit in the UI which buttons actually write to which databases and tables
- Interpreted goal:
  - remove ambiguity about whether the web app triggers real persistence and where that data lands
- Result:
  - added a write-target summary table near the top of the app
  - added per-job `Writes to` captions on each execution card
- Durable output:
  - `app/web/streamlit_app.py`

### 2026-03-11 - Large-run safeguards for all-symbol ingestion
- Request topic:
  - add better visual handling for large all-symbol runs such as OHLCV collection over the full universe
- Interpreted goal:
  - reduce accidental long-running executions and make the cost of large runs more visible before execution
- Result:
  - added symbol-count based warnings
  - added estimated runtime using prior run history when available
  - added confirmation checkbox gating for very large runs
- Durable output:
  - `app/jobs/run_history.py`
  - `app/web/streamlit_app.py`

### 2026-03-11 - Single-job lock and running banner for admin UI
- Request topic:
  - prevent other buttons from running while one ingestion job is already in progress and show a visible running banner
- Interpreted goal:
  - reduce accidental duplicate execution and make long-running ingestion state explicit in the internal admin console
- Result:
  - changed the Streamlit execution flow from direct button-run behavior to a scheduled single-job model
  - added a session-level running job lock so all execution buttons are disabled while a job is active
  - added a top-level running banner and a latest-completed-run summary after completion
- Durable output:
  - `app/web/streamlit_app.py`

### 2026-03-11 - Short OHLCV period support in the admin UI
- Request topic:
  - support `1d` and `7d` in the pipeline period selector
- Interpreted goal:
  - make short-window OHLCV collection easier from the web UI without forcing manual start/end entry
- Result:
  - added `1d` directly as a period preset
  - added `7d` as a UI alias that resolves to a rolling 7-day `start/end` window because the provider period format does not reliably accept `7d`
- Durable output:
  - `app/web/streamlit_app.py`

### 2026-03-11 - Large-run UX simplification
- Request topic:
  - remove the confirmation toggle for large symbol runs and review whether live progress visualization is practical
- Interpreted goal:
  - reduce friction for large manual runs while keeping operators informed about scale and duration
- Result:
  - removed the large-run confirmation checkbox and kept warning / estimated-runtime messaging
  - extended the running banner to show target symbol count for symbol-based jobs
  - confirmed that true live progress is feasible for OHLCV, but it requires callback-style refactoring in the low-level batch ingestion loop
- Durable output:
  - `app/web/streamlit_app.py`

### 2026-03-11 - Restoring local loading feedback in the admin UI
- Request topic:
  - keep the global running banner but restore job-local loading feedback similar to the earlier per-button behavior
- Interpreted goal:
  - make long-running execution feel active both globally and in the card where the operator clicked
- Result:
  - kept the top-level running banner for global lock visibility
  - moved scheduled execution into the matching job card so the loading state appears again in the local card context
- Durable output:
  - `app/web/streamlit_app.py`

### 2026-03-11 - Live OHLCV progress visualization for large runs
- Request topic:
  - add visual progress feedback for large symbol runs instead of only showing a static running banner
- Interpreted goal:
  - make long-running OHLCV ingestion operationally safer by exposing real-time progress within the web app
- Result:
  - added a batch-level progress callback to the low-level OHLCV MySQL ingestion loop
  - threaded that callback through the OHLCV wrapper and the core pipeline wrapper
  - added Streamlit progress bars and processed-symbol counters for large OHLCV runs and for the OHLCV stage of the core pipeline when symbol count is at least 100
- Durable output:
  - `finance/data/data.py`
  - `app/jobs/ingestion_jobs.py`
  - `app/web/streamlit_app.py`

### 2026-03-11 - Keep non-run panels visible during execution
- Request topic:
  - avoid hiding other jobs and log/history panels while a run is active; only block the run controls and live-updating widgets
- Interpreted goal:
  - preserve operator visibility into logs and prior runs during long ingestion work without allowing duplicate execution
- Result:
  - changed the execution flow so the page renders both left and right panels first, then runs the active job
  - kept the run controls disabled during execution, while allowing the non-run panels to remain visible
- Durable output:
  - `app/web/streamlit_app.py`

### 2026-03-11 - Phase 2 planning for web app and backtest transition
- Request topic:
  - create a concrete Phase 2 plan before continuing implementation
- Interpreted goal:
  - define the next development sequence after the first admin-console milestone, with emphasis on operational maturity and DB-backed backtesting preparation
- Result:
  - defined Phase 2 around five tracks:
    - execution/history hardening
    - operational pipeline restructuring
    - configuration externalization
    - backtest data loader layer
    - strategy execution UI
  - recommended starting with daily/weekly/monthly pipeline separation before moving to backtest UI
- Durable output:
  - `.note/finance/PHASE2_WEB_APP_AND_BACKTEST_PLAN.md`

### 2026-03-11 - Why detailed financial statement tables must remain first-class
- Request topic:
  - clarify why `nyse_financial_statement_labels` and `nyse_financial_statement_values` matter even though `nyse_fundamentals` and `nyse_factors` already exist
- Interpreted goal:
  - preserve an important architectural assumption for future data collection, loader design, and long-horizon backtesting
- Result:
  - recorded that `nyse_fundamentals` and `nyse_factors` are currently `yfinance`-based summary datasets with limited historical depth
  - recorded the user's working assumption that these summary datasets effectively cover only roughly the most recent 4 years
  - recorded that the detailed financial statement tables are being collected specifically to preserve:
    - older pre-2022 style history
    - more granular account-level data
    - future custom factor derivation potential
    - longer-horizon backtest support
  - concluded that the detailed statement tables should be treated as a first-class raw ledger, not as an optional side dataset
- Durable output:
  - `.note/finance/PHASE2_WEB_APP_AND_BACKTEST_PLAN.md`

### 2026-03-12 - Phase 2 start: operational pipeline separation
- Request topic:
  - start Phase 2 implementation
- Interpreted goal:
  - begin with the highest-priority Phase 2 task: restructuring the admin app around routine operational pipelines instead of only low-level component jobs
- Result:
  - added operational wrappers for:
    - daily market update
    - weekly fundamental refresh
    - extended statement refresh
    - metadata refresh
  - added a dedicated Operational Pipelines section to the Streamlit UI
  - kept the existing manual job cards for lower-level control
- Durable output:
  - `app/jobs/ingestion_jobs.py`
  - `app/jobs/__init__.py`
  - `app/web/streamlit_app.py`

### 2026-03-12 - Simplify Extended Statement Refresh frequency selection
- Request topic:
  - avoid confusing mismatches between `Extended Statement Freq` and `Extended Statement Period Type`
- Interpreted goal:
  - make the operational pipeline UI safer by preventing semantically inconsistent parameter combinations
- Result:
  - removed the separate frequency selector from the operational `Extended Statement Refresh` UI
  - aligned `freq` automatically to the selected `Period Type`
- Durable output:
  - `app/web/streamlit_app.py`

### 2026-03-17 - Phase 2 execution-history hardening start
- Request topic:
  - continue Phase 2 by moving into the next concrete work item after operational pipeline separation
- Interpreted goal:
  - make the persisted run history durable enough to explain how each job was executed, not only whether it succeeded
- Result:
  - added `run_metadata` capture to scheduled UI jobs
  - began storing symbol source, symbol count, and key input parameters alongside execution results
  - updated the UI history views to surface symbol source and input parameters more directly
- Durable output:
  - `app/web/streamlit_app.py`

### 2026-03-17 - Current PHASE2 chapter TODO note
- Request topic:
  - show the currently active TODO work for the present Phase 2 chapter
- Interpreted goal:
  - separate immediate execution tasks from the broader Phase 2 plan so ongoing implementation is easier to track
- Result:
  - created a dedicated current-chapter TODO note with status, remaining work, and recommended next actions
- Durable output:
  - `.note/finance/PHASE2_CURRENT_CHAPTER_TODO.md`

### 2026-03-17 - Convert the current PHASE2 TODO into a larger execution board
- Request topic:
  - manage the ongoing chapter with a larger TODO and visible step-by-step check progress
- Interpreted goal:
  - make the active PHASE2 work easier to track collaboratively while implementing one checked item at a time
- Result:
  - rewrote the current chapter TODO into a grouped execution board
  - organized it by major workstreams with `pending / in_progress / completed` item states
  - fixed the immediate next target as `B-6 pipeline_type` under execution-history hardening
- Durable output:
  - `.note/finance/PHASE2_CURRENT_CHAPTER_TODO.md`

### 2026-03-17 - Add explanations to each current PHASE2 checklist item
- Request topic:
  - make each detailed TODO item explain what that work actually means
- Interpreted goal:
  - improve the current chapter board so it works not only as a checklist but also as a readable execution guide
- Result:
  - added short explanations under each detailed checklist item in the current PHASE2 board
- Durable output:
  - `.note/finance/PHASE2_CURRENT_CHAPTER_TODO.md`

### 2026-03-17 - Complete TODO item B-6 pipeline_type storage
- Request topic:
  - proceed with the next tracked TODO item in the current PHASE2 board
- Interpreted goal:
  - make persisted run history explicitly record what operational or manual pipeline type each execution belongs to
- Result:
  - added `pipeline_type` into `run_metadata` for all scheduled Streamlit jobs
  - distinguished operational pipelines and manual jobs with explicit pipeline labels
  - updated the current TODO board so B-6 is completed and B-7 is the next target
- Durable output:
  - `app/web/streamlit_app.py`
  - `.note/finance/PHASE2_CURRENT_CHAPTER_TODO.md`

### 2026-03-17 - Complete TODO item B-7 execution_mode storage
- Request topic:
  - proceed with the next tracked TODO item after pipeline_type storage
- Interpreted goal:
  - make persisted history clearly distinguish routine operational runs from manual lower-level runs
- Result:
  - added `execution_mode` into `run_metadata` for all scheduled Streamlit jobs
  - used `operational` for routine pipeline buttons and `manual` for detailed job cards
  - surfaced the field in both recent-run and persistent-history UI views
  - updated the current TODO board so B-7 is completed and B-8 is the next target
- Durable output:
  - `app/web/streamlit_app.py`
  - `.note/finance/PHASE2_CURRENT_CHAPTER_TODO.md`

### 2026-03-17 - Complete TODO item B-8 execution_context storage
- Request topic:
  - proceed with the next tracked TODO item after execution_mode storage
- Interpreted goal:
  - preserve a short human-readable explanation of why or in what context each execution was performed
- Result:
  - added `execution_context` into `run_metadata` for all scheduled Streamlit jobs
  - populated it automatically with short descriptions for each operational pipeline and manual job type
  - surfaced the field in both recent-run and persistent-history UI views
  - updated the current TODO board so B-8 is completed and B-9 is the next target
- Durable output:
  - `app/web/streamlit_app.py`
  - `.note/finance/PHASE2_CURRENT_CHAPTER_TODO.md`

### 2026-03-17 - Complete TODO item B-9 persistent history table reflection
- Request topic:
  - proceed with the next tracked TODO item for history UI reflection
- Interpreted goal:
  - make the new run-metadata fields actually readable in the persistent history table, not only stored in JSONL
- Result:
  - reorganized the persistent history table columns to foreground execution mode, pipeline type, source, context, and parameter summary
  - updated the current TODO board so B-9 is completed and the next target is the JSONL schema review step
- Durable output:
  - `app/web/streamlit_app.py`
  - `.note/finance/PHASE2_CURRENT_CHAPTER_TODO.md`

### 2026-03-17 - Complete TODO item B-10 JSONL schema review and normalization
- Request topic:
  - proceed with the final tracked TODO item under execution-history hardening
- Interpreted goal:
  - verify the actual persisted JSONL history shape and prevent older rows from becoming second-class records as the schema evolves
- Result:
  - reviewed the existing run history samples and confirmed that older rows lacked `run_metadata`
  - added run-history normalization so legacy rows are enriched on load with inferred pipeline type, execution mode, and execution context when possible
  - added a run-history schema version for newly written records
  - updated the current TODO board so execution-history hardening is now complete
- Durable output:
  - `app/jobs/run_history.py`
  - `.note/finance/PHASE2_CURRENT_CHAPTER_TODO.md`

### 2026-03-17 - Complete TODO item A-7 operational pipeline cadence guidance
- Request topic:
  - proceed with the next tracked TODO item after execution-history hardening completed
- Interpreted goal:
  - make each operational pipeline easier to use by stating when it should normally be run
- Result:
  - added recommended cadence captions to:
    - Daily Market Update
    - Weekly Fundamental Refresh
    - Extended Statement Refresh
    - Metadata Refresh
  - updated the current TODO board so A-7 is completed and A-8 is the next target
- Durable output:
  - `app/web/streamlit_app.py`
  - `.note/finance/PHASE2_CURRENT_CHAPTER_TODO.md`

### 2026-03-17 - Complete TODO item A-8 operational symbol-source guidance
- Request topic:
  - proceed with the next tracked TODO item under operational pipeline cleanup
- Interpreted goal:
  - make each operational pipeline easier to use by clarifying which symbol source is the recommended default
- Result:
  - added symbol-source guidance captions to each operational pipeline card
  - updated the current TODO board so A-8 is completed and A-9 is the next target
- Durable output:
  - `app/web/streamlit_app.py`
  - `.note/finance/PHASE2_CURRENT_CHAPTER_TODO.md`

### 2026-03-17 - Complete TODO item A-9 operational vs manual role clarity
- Request topic:
  - proceed with the next tracked TODO item under operational pipeline cleanup
- Interpreted goal:
  - reduce operator confusion by clearly distinguishing routine operational buttons from lower-level manual execution cards
- Result:
  - strengthened the Operational Pipelines section caption to make it the default path for recurring work
  - added a Manual Jobs section caption describing it as exception handling / partial rerun / fine-grained control territory
  - adjusted the Core Market Data Pipeline description so it reads as a manual composite job rather than the default routine path
  - updated the current TODO board so A-9 is completed and A-10 is the next target
- Durable output:
  - `app/web/streamlit_app.py`
  - `.note/finance/PHASE2_CURRENT_CHAPTER_TODO.md`

### 2026-03-17 - Complete TODO item A-10 operational default review
- Request topic:
  - proceed with the next tracked TODO item after clarifying operational/manual role differences
- Interpreted goal:
  - make the operational pipeline defaults better match actual recurring usage rather than leaving them at generic development defaults
- Result:
  - parameterized the symbol-source input helper so each operational card can choose its own default source
  - set Daily Market Update defaults to `NYSE Stocks`, `1mo`, `1d`
  - set Weekly Fundamental Refresh defaults to `NYSE Stocks`, `quarterly`
  - set Extended Statement Refresh defaults to `Profile Filtered Stocks`, `annual`, `8 periods`
  - marked the entire operational-pipeline cleanup track as complete and moved the current focus to configuration externalization preparation
- Durable output:
  - `app/web/streamlit_app.py`
  - `.note/finance/PHASE2_CURRENT_CHAPTER_TODO.md`

### 2026-03-18 - Complete TODO item C-1 hardcoded constant inventory
- Request topic:
  - proceed with the next tracked TODO item after operational pipeline cleanup completed
- Interpreted goal:
  - prepare configuration externalization by first identifying which runtime and UI values are currently hardcoded in code
- Result:
  - created a dedicated inventory note covering:
    - web-app defaults
    - DB connection constants
    - batch/sleep/retry ingest parameters
    - period/freq defaults
    - UI display limits
    - low-priority non-config constants
  - updated the current TODO board so C-1 is completed and C-2 is the next target
- Durable output:
  - `.note/finance/CONFIG_EXTERNALIZATION_INVENTORY.md`
  - `.note/finance/PHASE2_CURRENT_CHAPTER_TODO.md`

### 2026-03-18 - Complete TODO item C-2 externalization priority classification
- Request topic:
  - proceed with the next tracked TODO item under configuration externalization preparation
- Interpreted goal:
  - move from a raw inventory of hardcoded constants to a staged externalization plan that clarifies what should be extracted first
- Result:
  - classified config candidates into:
    - immediate externalization
    - next-stage externalization
    - later externalization
    - not-recommended / deferred
  - updated the current TODO board so C-2 is completed and C-3 is the next target
- Durable output:
  - `.note/finance/CONFIG_EXTERNALIZATION_INVENTORY.md`
  - `.note/finance/PHASE2_CURRENT_CHAPTER_TODO.md`
