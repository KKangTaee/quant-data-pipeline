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
  - `.note/finance/phase1/INTERNAL_WEB_APP_DEVELOPMENT_GUIDE.md`

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
  - `.note/finance/phase1/PHASE1_WEB_APP_SCOPE.md`

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
  - `.note/finance/phase1/PHASE1_JOB_WRAPPER_INTERFACE.md`

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

### 2026-03-18 - Backtest loader input contract
- Request topic:
  - define the common input contract that future backtest loaders should follow
- Interpreted goal:
  - prevent loader implementations from diverging on symbol resolution, date filtering, and frequency semantics before code is written
- Result:
  - defined precedence rules for `symbols` and `universe_source`
  - separated `timeframe` for price loaders from `freq` for fundamentals / factors / statements
  - standardized `start/end` range filtering and `as_of_date` snapshot usage
  - recorded that detailed financial statement loaders are core ledger loaders, not optional side loaders
- Durable output:
  - `.note/finance/phase2/BACKTEST_LOADER_INPUT_CONTRACT.md`

### 2026-03-18 - Backtest point-in-time guidelines
- Request topic:
  - separate point-in-time cautions into an explicit loader-design note before backtest implementation starts
- Interpreted goal:
  - prevent future backtest and loader work from silently using `period_end` as if it were the real market-available date
- Result:
  - documented the difference between `period_end` and real information availability
  - defined staged implementation guidance:
    - temporary `period_end <= as_of_date` snapshots
    - conservative lag fallback
    - later strict filing-date-based point-in-time
  - recorded table-specific cautions for fundamentals, factors, and detailed financial statement loaders
- Durable output:
  - `.note/finance/phase2/BACKTEST_POINT_IN_TIME_GUIDELINES.md`

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
  - `.note/finance/phase2/PHASE2_WEB_APP_AND_BACKTEST_PLAN.md`

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
  - `.note/finance/phase2/PHASE2_WEB_APP_AND_BACKTEST_PLAN.md`

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
  - `.note/finance/phase2/PHASE2_CURRENT_CHAPTER_TODO.md`

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
  - `.note/finance/phase2/PHASE2_CURRENT_CHAPTER_TODO.md`

### 2026-03-17 - Add explanations to each current PHASE2 checklist item
- Request topic:
  - make each detailed TODO item explain what that work actually means
- Interpreted goal:
  - improve the current chapter board so it works not only as a checklist but also as a readable execution guide
- Result:
  - added short explanations under each detailed checklist item in the current PHASE2 board
- Durable output:
  - `.note/finance/phase2/PHASE2_CURRENT_CHAPTER_TODO.md`

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
  - `.note/finance/phase2/PHASE2_CURRENT_CHAPTER_TODO.md`

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
  - `.note/finance/phase2/PHASE2_CURRENT_CHAPTER_TODO.md`

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
  - `.note/finance/phase2/PHASE2_CURRENT_CHAPTER_TODO.md`

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
  - `.note/finance/phase2/PHASE2_CURRENT_CHAPTER_TODO.md`

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
  - `.note/finance/phase2/PHASE2_CURRENT_CHAPTER_TODO.md`

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
  - `.note/finance/phase2/PHASE2_CURRENT_CHAPTER_TODO.md`

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
  - `.note/finance/phase2/PHASE2_CURRENT_CHAPTER_TODO.md`

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
  - `.note/finance/phase2/PHASE2_CURRENT_CHAPTER_TODO.md`

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
  - `.note/finance/phase2/PHASE2_CURRENT_CHAPTER_TODO.md`

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
  - `.note/finance/phase2/PHASE2_CURRENT_CHAPTER_TODO.md`

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
  - `.note/finance/phase2/PHASE2_CURRENT_CHAPTER_TODO.md`

### 2026-03-18 - Complete TODO item C-3 config file path decision
- Request topic:
  - proceed with the next tracked TODO item under configuration externalization preparation
- Interpreted goal:
  - fix a stable path for the first runtime config file before deciding the file format and actual keys
- Result:
  - decided to use `config/finance_web_app.toml` as the first runtime config path
  - recorded why runtime config belongs under a dedicated `config/` directory instead of `.note/finance`
  - updated the current TODO board so C-3 is completed and C-4 is the next target
- Durable output:
  - `.note/finance/CONFIG_EXTERNALIZATION_INVENTORY.md`
  - `.note/finance/phase2/PHASE2_CURRENT_CHAPTER_TODO.md`

### 2026-03-18 - Complete TODO item C-4 config format draft
- Request topic:
  - proceed with the next tracked TODO item after deciding the config file path
- Interpreted goal:
  - define the first runtime config structure clearly enough that actual file creation and code wiring can follow without rethinking the format
- Result:
  - selected TOML as the config format
  - drafted the first `config/finance_web_app.toml` section structure and example keys
  - recorded which sections should be included first and which can be deferred
  - updated the current TODO board so configuration externalization preparation is complete and the next focus is the backtest-loader planning track
- Durable output:
  - `.note/finance/CONFIG_EXTERNALIZATION_INVENTORY.md`
  - `.note/finance/phase2/PHASE2_CURRENT_CHAPTER_TODO.md`

### 2026-03-18 - Complete TODO item D-2 backtest loader function draft
- Request topic:
  - proceed with the next tracked TODO item after configuration externalization preparation completed
- Interpreted goal:
  - define the first concrete loader-function surface so the future DB-backed backtest layer has a stable API direction before implementation starts
- Result:
  - created a dedicated loader draft note covering:
    - universe loader
    - price loader
    - fundamentals loader
    - factor loader
    - detailed financial statement loader
    - common helper functions
  - prioritized initial loader implementation order
  - updated the current TODO board so D-2 is completed and D-3 is the next target
- Durable output:
  - `.note/finance/phase2/BACKTEST_LOADER_FUNCTION_DRAFT.md`
  - `.note/finance/phase2/PHASE2_CURRENT_CHAPTER_TODO.md`

### 2026-03-18 - EDGAR detailed statement payload and point-in-time schema redesign
- Request topic:
  - inspect the actual API behind `nyse_financial_statement_labels` / `nyse_financial_statement_values`, confirm whether filing-time metadata exists, and redesign the table structure so public-availability timing can be stored correctly
- Interpreted goal:
  - replace assumption-based detailed-statement storage with a source-verified EDGAR ingestion design that preserves real filing timing and is easier for humans to inspect
- Result:
  - confirmed by direct EDGAR inspection on representative issuers that raw `FinancialFact` records include:
    - actual `period_end`
    - `filing_date`
    - `form_type`
    - `accession`
    - statement/concept/unit metadata
  - confirmed filing-level `acceptance_datetime` and `report_date` are available through `Company.get_filings(...)`
  - identified that the old ingestion path lost this metadata because it depended on `as_dataframe=True` statement views
  - identified a second critical bug:
    - the old label parser inferred `FY 2025 -> 2025-12-31` and `Q1 2026 -> 2026-03-31`, which is wrong for non-calendar fiscal year issuers
  - redesigned the ingestion around raw facts plus filing metadata
  - added `nyse_financial_statement_filings` for human inspection of filing-level availability metadata
  - expanded `nyse_financial_statement_values` to store `available_at`, `accession_no`, `form_type`, actual `period_end`, concept/unit/taxonomy, and audit/restatement flags
  - expanded `nyse_financial_statement_labels` to summarize latest concept and filing metadata per label/as-of row
  - changed value-row uniqueness to filing-aware identity so different filings for the same accounting period are no longer collapsed
- Important follow-up decisions:
  - raw detailed-statement storage now prioritizes provider truth over synthetic convenience
  - quarterly DB storage does not synthesize Q4 at ingestion time; if Q4 is needed later it should be derived in a loader or transformation step with explicit logic
  - when interpreting detailed-statement rows, `period_end` and `accession_no` should be treated as the primary row identity; provider `fiscal_year` / `fiscal_period` can reflect filing context on comparative facts
- Durable output:
  - `finance/data/financial_statements.py`
  - `finance/data/db/schema.py`
  - `.note/finance/FINANCE_COMPREHENSIVE_ANALYSIS.md`

### 2026-03-18 - Post-change review of detailed-statement point-in-time design
- Request topic:
  - review the newly modified point-in-time code from another thread and decide what still needs to be fixed before moving to the next chapter
- Interpreted goal:
  - turn the raw code change into an explicit engineering judgment with concrete next patch priorities instead of assuming the redesign is already strict-PIT complete
- Result:
  - confirmed the redesign is directionally correct because filing-level metadata and `available_at` are now preserved
  - identified two immediate follow-up risks:
    - `available_at` falls back to `filing_date 00:00:00`, which is too early for strict PIT
    - the raw values unique key still depends on nullable fields, which can break idempotent ingestion
  - identified one secondary design issue:
    - `nyse_financial_statement_labels` can collapse concept-level meaning and should be treated as an operator-facing summary table unless its identity is widened
  - recorded the recommended patch order around fallback timing, key stabilization, and labels-table role definition
- Durable output:
  - `.note/finance/phase2/POINT_IN_TIME_SCHEMA_REVIEW_AND_PATCH_PLAN.md`

### 2026-03-18 - Start next PHASE2 point-in-time hardening chapter
- Request topic:
  - create the next TODO board and begin the follow-up hardening work step by step
- Interpreted goal:
  - move from design review into concrete point-in-time stabilization tasks without losing the chapter-based execution style
- Result:
  - created a dedicated next-chapter TODO board for point-in-time hardening
  - completed the first code patch by making `available_at` conservative when `accepted_at` is missing
  - verified the new behavior locally:
    - `filing_date` only -> `23:59:59`
    - explicit `accepted_at` -> preserved
- Durable output:
  - `.note/finance/phase2/PHASE2_POINT_IN_TIME_HARDENING_TODO.md`
  - `finance/data/financial_statements.py`

### 2026-03-18 - Audit current detailed-statement raw identity readiness
- Request topic:
  - continue the new point-in-time hardening chapter by checking whether the values-table identity can actually support strict PIT behavior
- Interpreted goal:
  - avoid patching the schema blindly by first measuring how much of the existing table still reflects the old legacy ingestion format
- Result:
  - verified that `nyse_financial_statement_values` is still mixed-state
  - measured:
    - 303,054 total rows
    - 302,712 rows without `accession_no`
    - 302,712 rows without `unit`
    - only 342 accession-bearing rows across 2 symbols
  - concluded that future strict identity must distinguish between:
    - new raw rows that can use accession-based identity
    - legacy rows that need backfill or rebuild before they are PIT-safe
- Durable output:
  - `.note/finance/phase2/PHASE2_POINT_IN_TIME_HARDENING_TODO.md`
  - `.note/finance/phase2/POINT_IN_TIME_SCHEMA_REVIEW_AND_PATCH_PLAN.md`

### 2026-03-18 - Add raw-identity guard to new detailed-statement ingestion path
- Request topic:
  - continue the hardening chapter after the mixed-state DB audit by making the new raw ingestion path refuse identity-incomplete rows
- Interpreted goal:
  - improve future PIT ledger quality immediately without trying to hard-migrate the entire legacy table in the same patch
- Result:
  - verified on representative raw sources that current EDGAR statement facts do carry both `accession` and `unit`
  - added an ingestion-side guard so `_iter_value_rows_from_source(...)` skips rows lacking either `accession_no` or `unit`
  - kept the DB-level strict constraint as a later step because the existing table is still dominated by legacy rows
- Durable output:
  - `finance/data/financial_statements.py`
  - `.note/finance/phase2/PHASE2_POINT_IN_TIME_HARDENING_TODO.md`

### 2026-03-18 - Validate accession-based reingestion stability on new raw path
- Request topic:
  - continue the hardening chapter by verifying that the new accession-based rows do not duplicate on rerun
- Interpreted goal:
  - confirm that the ingestion-side identity guard plus the existing unique key are sufficient for new raw rows before attempting broader schema hardening
- Result:
  - reran quarterly detailed-statement ingestion for `AAPL`
  - confirmed accession-bearing quarterly rows stayed at 139 before and after rerun
  - confirmed duplicate groups under `(symbol, freq, accession_no, statement_type, concept, period_end, unit)` remained 0
  - concluded that the immediate remaining issue is legacy-row cleanup, not new-path duplicate behavior
- Durable output:
  - `.note/finance/phase2/PHASE2_POINT_IN_TIME_HARDENING_TODO.md`

### 2026-03-18 - Define legacy backfill and strict-constraint transition strategy
- Request topic:
  - continue the hardening chapter by deciding how to handle the legacy/new mixed-state values table before applying stricter PIT constraints
- Interpreted goal:
  - avoid forcing DB constraints too early by first deciding how strict loaders, backfills, and eventual schema hardening should interact
- Result:
  - defined a staged strategy:
    - keep new-path ingestion guards
    - let strict PIT loaders read accession-bearing rows only
    - backfill research-first universes first
    - delay DB-level strict constraints until coverage is sufficient
  - documented that the immediate next focus should move from raw identity to labels/loader boundary
- Durable output:
  - `.note/finance/phase2/POINT_IN_TIME_BACKFILL_AND_CONSTRAINT_STRATEGY.md`
  - `.note/finance/phase2/PHASE2_POINT_IN_TIME_HARDENING_TODO.md`

### 2026-03-18 - Clarify labels vs values responsibility in loader design
- Request topic:
  - continue the hardening chapter by making the labels table role explicit before loader implementation proceeds
- Interpreted goal:
  - prevent future loaders from treating the summary labels table as the semantic source of truth
- Result:
  - updated the loader design notes so:
    - `nyse_financial_statement_values` is the raw ledger source of truth
    - `nyse_financial_statement_labels` is an operator-facing summary / lookup helper
  - shifted the next TODO focus toward writing strict PIT loader query conditions
- Durable output:
  - `.note/finance/phase2/BACKTEST_LOADER_INPUT_CONTRACT.md`
  - `.note/finance/phase2/BACKTEST_LOADER_FUNCTION_DRAFT.md`
  - `.note/finance/phase2/PHASE2_POINT_IN_TIME_HARDENING_TODO.md`

### 2026-03-18 - Draft strict PIT statement-loader query rules
- Request topic:
  - continue the hardening chapter by writing the actual query conditions a future strict PIT statement loader should use
- Interpreted goal:
  - make the move from design principles to implementable loader-query rules while the mixed-state DB caveats are still fresh
- Result:
  - drafted strict filters around:
    - `accession_no`
    - `unit`
    - `available_at`
  - documented that strict snapshots must prioritize `available_at <= as_of_date`, not just `period_end`
  - provided latest-available selection patterns using window-function and subquery styles
- Durable output:
  - `.note/finance/phase2/STRICT_PIT_LOADER_QUERY_DRAFT.md`
  - `.note/finance/phase2/PHASE2_POINT_IN_TIME_HARDENING_TODO.md`

### 2026-03-18 - One-time cleanup redesign of statement labels/values tables
- Request topic:
  - decide whether the old `nyse_financial_statement_labels` / `nyse_financial_statement_values` tables should be kept or heavily revised, with permission to discard data if needed
- Interpreted goal:
  - avoid carrying early-stage schema compromises forward now that these tables are still unused and can be reset safely
- Result:
  - concluded that a cleanup redesign was preferable
  - tightened `nyse_financial_statement_values` into a stricter raw ledger by requiring `concept`, `unit`, `available_at`, and `accession_no`
  - changed `nyse_financial_statement_labels` into a concept-centered summary table keyed by `(symbol, statement_type, concept, as_of)`
  - recreated the local labels/values tables and confirmed sample reingestion succeeded
- Durable output:
  - `finance/data/db/schema.py`
  - `finance/data/financial_statements.py`
  - `.note/finance/FINANCE_COMPREHENSIVE_ANALYSIS.md`
  - `.note/finance/phase2/PHASE2_POINT_IN_TIME_HARDENING_TODO.md`

### 2026-03-22 - Establish phase-based project management as the default workflow
- Request topic:
  - formalize phase-based project management, documentation, and future phase creation as the standard way to run the finance project
- Interpreted goal:
  - make future development easier to track and maintain by putting all major work under explicit phases tied to the product goals of data collection and backtesting
- Result:
  - created a top-level master phase roadmap
  - created a finance document index
  - updated `AGENTS.md` so future work follows:
    - phase-first planning
    - per-phase TODO boards
    - roadmap/index maintenance
    - explicit user confirmation before opening major new phases
- Durable output:
  - `.note/finance/MASTER_PHASE_ROADMAP.md`
  - `.note/finance/FINANCE_DOC_INDEX.md`
  - `AGENTS.md`

### 2026-03-22 - Reorganize finance notes into phase folders
- Request topic:
  - review whether phase-based folders under `.note/finance/` would be better than keeping all documents flat, and proceed if beneficial
- Interpreted goal:
  - keep the growing documentation set maintainable by separating phase-specific execution docs from cross-phase reference documents
- Result:
  - moved phase-specific documents into:
    - `.note/finance/phase1/`
    - `.note/finance/phase2/`
    - `.note/finance/phase3/`
  - kept cross-phase anchor documents at the `.note/finance/` root
  - updated roadmap/index/log references to the new structure
- Durable output:
  - `.note/finance/FINANCE_DOC_INDEX.md`
  - `.note/finance/MASTER_PHASE_ROADMAP.md`
  - `AGENTS.md`

### 2026-03-22 - Close Phase 2 and open Phase 3
- Request topic:
  - finish Phase 2 and proceed into Phase 3 work
- Interpreted goal:
  - turn the current loader/backtest-preparation state into a clean phase transition so future work starts from an explicit Phase 3 runtime implementation baseline
- Result:
  - created a Phase 2 completion summary
  - created a Phase 3 plan document
  - created the first Phase 3 TODO board
  - updated the roadmap and doc index to show Phase 2 completed and Phase 3 active
- Durable output:
  - `.note/finance/phase2/PHASE2_COMPLETION_SUMMARY.md`
  - `.note/finance/phase3/PHASE3_LOADER_AND_RUNTIME_PLAN.md`
  - `.note/finance/phase3/PHASE3_CURRENT_CHAPTER_TODO.md`
  - `.note/finance/MASTER_PHASE_ROADMAP.md`

### 2026-03-22 - Fix Phase 3 loader naming policy
- Request topic:
  - continue Phase 3 by deciding how broad research loaders and strict PIT loaders should be named
- Interpreted goal:
  - avoid ambiguity before loader implementation starts by making function names encode the intended data assumptions
- Result:
  - fixed the policy that:
    - base names are for broad research loaders
    - `*_snapshot` is for broad snapshot reads
    - `*_snapshot_strict` is for strict PIT snapshot reads
  - recorded this as the default naming rule for Phase 3
- Durable output:
  - `.note/finance/phase3/PHASE3_LOADER_NAMING_POLICY.md`
  - `.note/finance/phase3/PHASE3_CURRENT_CHAPTER_TODO.md`

### 2026-03-22 - Fix the initial strict statement loader scope for Phase 3
- Request topic:
  - continue Phase 3 by deciding what the first strict detailed financial statement loader should and should not do
- Interpreted goal:
  - lock the conservative point-in-time scope before implementation so the first loader path favors correctness over breadth
- Result:
  - fixed the policy that the first strict loader is:
    - values-table-centered
    - snapshot-oriented
    - availability-gated by `available_at <= as_of_date`
    - limited to accession-bearing and identity-complete rows
  - explicitly excluded `nyse_financial_statement_labels` from the strict source-of-truth path
  - left full-history strict reads and broad research coverage decisions for later steps
- Durable output:
  - `.note/finance/phase3/PHASE3_STRICT_STATEMENT_LOADER_SCOPE.md`
  - `.note/finance/phase3/PHASE3_CURRENT_CHAPTER_TODO.md`
  - `.note/finance/FINANCE_DOC_INDEX.md`

### 2026-03-22 - Fix the broad statement loader policy for Phase 3
- Request topic:
  - continue Phase 3 by deciding how broad statement loaders should differ from strict PIT loaders
- Interpreted goal:
  - avoid reintroducing early mixed-state compromises while still leaving room for research-oriented reads
- Result:
  - fixed the policy that broad statement loaders:
    - can read history by `period_end`
    - can skip strict PIT snapshot semantics
    - remain values-table-centered
    - do not reopen support for broken legacy rows after the Phase 2 schema cleanup
  - clarified that the strict/broad difference is now about time semantics and use case, not row-identity quality
- Durable output:
  - `.note/finance/phase3/PHASE3_BROAD_STATEMENT_LOADER_POLICY.md`
  - `.note/finance/phase3/PHASE3_CURRENT_CHAPTER_TODO.md`
  - `.note/finance/FINANCE_DOC_INDEX.md`

### 2026-03-22 - Fix the first loader implementation set for Phase 3
- Request topic:
  - continue Phase 3 by deciding which loaders should be implemented first
- Interpreted goal:
  - open the shortest possible DB-backed strategy runtime path before expanding into more complex loader families
- Result:
  - fixed the first implementation set as:
    - `load_universe(...)`
    - `load_price_history(...)`
    - `load_price_matrix(...)`
  - moved fundamentals / factors / statements behind the first price-based strategy milestone
  - recorded the reasoning that existing strategies are currently price-centric, so price loaders are the safest first implementation target
- Durable output:
  - `.note/finance/phase3/PHASE3_INITIAL_LOADER_IMPLEMENTATION_SET.md`
  - `.note/finance/phase3/PHASE3_CURRENT_CHAPTER_TODO.md`
  - `.note/finance/FINANCE_DOC_INDEX.md`

### 2026-03-22 - Fix the loader module path for Phase 3
- Request topic:
  - continue Phase 3 by deciding where the loader implementation should live in the package structure
- Interpreted goal:
  - separate runtime/read-path code from the existing ingestion/write-path code before implementation begins
- Result:
  - fixed the loader path as `finance/loaders/*`
  - documented module responsibilities for:
    - `__init__.py`
    - `_common.py`
    - `universe.py`
    - `price.py`
    - `fundamentals.py`
    - `factors.py`
    - `financial_statements.py`
  - created the initial `finance/loaders/__init__.py` scaffold so the package boundary is now real, not just planned
- Durable output:
  - `.note/finance/phase3/PHASE3_LOADER_MODULE_PATH.md`
  - `finance/loaders/__init__.py`
  - `.note/finance/phase3/PHASE3_CURRENT_CHAPTER_TODO.md`
  - `.note/finance/FINANCE_DOC_INDEX.md`

### 2026-03-22 - Fix the shared helper scope for Phase 3 loaders
- Request topic:
  - continue Phase 3 by deciding which shared helpers belong in the common loader layer
- Interpreted goal:
  - avoid duplicated input-normalization logic before domain-specific loader modules are implemented
- Result:
  - fixed the helper boundary so `_common.py` contains only shared input and symbol-resolution logic
  - created common helpers for:
    - symbol parsing
    - universe resolution
    - date normalization
    - freq/timeframe normalization
    - snapshot input validation
  - explicitly left domain-specific query logic out of `_common.py`
- Durable output:
  - `.note/finance/phase3/PHASE3_LOADER_HELPER_SCOPE.md`
  - `finance/loaders/_common.py`
  - `.note/finance/phase3/PHASE3_CURRENT_CHAPTER_TODO.md`
  - `.note/finance/FINANCE_DOC_INDEX.md`

### 2026-03-22 - Fix the first implementation entry set for Phase 3
- Request topic:
  - continue Phase 3 by deciding the first implementation order, first DB-backed strategy candidate, and minimal validation path
- Interpreted goal:
  - remove the last major uncertainty before actual loader coding starts
- Result:
  - fixed the first implementation order as:
    - `load_universe(...)`
    - `load_price_history(...)`
    - `load_price_matrix(...)`
    - runtime adapter
  - fixed the first DB-backed strategy candidate as `EqualWeightStrategy`
  - fixed the minimal validation path as:
    - DB price loader
    - adapter
    - `EqualWeightStrategy`
    - result DataFrame checks
- Durable output:
  - `.note/finance/phase3/PHASE3_FIRST_LOADER_IMPLEMENTATION_ORDER.md`
  - `.note/finance/phase3/PHASE3_FIRST_DB_BACKED_STRATEGY_CANDIDATE.md`
  - `.note/finance/phase3/PHASE3_MINIMAL_VALIDATION_PATH.md`
  - `.note/finance/phase3/PHASE3_CURRENT_CHAPTER_TODO.md`
  - `.note/finance/FINANCE_DOC_INDEX.md`

### 2026-03-22 - Start the first concrete loader implementation for Phase 3
- Request topic:
  - continue Phase 3 into actual code after the policy and entry-set documents were fixed
- Interpreted goal:
  - turn the first agreed loader set into a real package entry path that later runtime code can call
- Result:
  - opened a dedicated loader implementation TODO board
  - implemented:
    - `finance/loaders/universe.py`
    - `finance/loaders/price.py`
  - re-exported the first public loader functions from `finance/loaders/__init__.py`
- Durable output:
  - `.note/finance/phase3/PHASE3_LOADER_IMPLEMENTATION_TODO.md`
  - `finance/loaders/universe.py`
  - `finance/loaders/price.py`
  - `finance/loaders/__init__.py`

### 2026-03-22 - Add the first runtime adapter for Phase 3
- Request topic:
  - continue Phase 3 by connecting loader output to the existing strategy input shape
- Interpreted goal:
  - make the first DB-backed strategy validation path executable without rewriting the current strategy layer
- Result:
  - added a runtime adapter that converts long-form price history into the existing ticker-keyed OHLCV dict shape
  - added a convenience helper that loads and adapts DB price history in one step
  - updated the validation example to use symbols currently confirmed in the local DB
- Durable output:
  - `finance/loaders/runtime_adapter.py`
  - `.note/finance/phase3/PHASE3_RUNTIME_ADAPTER_PATH.md`
  - `.note/finance/phase3/PHASE3_MINIMAL_VALIDATION_PATH.md`
  - `.note/finance/phase3/PHASE3_LOADER_IMPLEMENTATION_TODO.md`

### 2026-03-22 - Validate the first DB-backed strategy runtime path
- Request topic:
  - continue Phase 3 by running the first end-to-end DB-backed strategy check
- Interpreted goal:
  - verify that the new loader path is not just importable, but actually usable by an existing strategy
- Result:
  - validated `DB price loader -> runtime adapter -> EqualWeightStrategy` successfully
  - used local DB-backed symbols with confirmed coverage:
    - `AAPL`
    - `MSFT`
    - `GOOG`
  - confirmed 252 daily rows per symbol, 252 strategy result rows, and a final balance of `12998.14`
- Durable output:
  - `.note/finance/phase3/PHASE3_FIRST_DB_BACKED_RUNTIME_VALIDATION.md`
  - `.note/finance/phase3/PHASE3_LOADER_IMPLEMENTATION_TODO.md`

### 2026-03-22 - Add DB-backed sample entrypoints without changing the old strategy samples
- Request topic:
  - keep the existing sample functions intact and add separate `*_from_db` functions for DB-backed testing
- Interpreted goal:
  - preserve the old external-source strategy tests while giving the user explicit DB-based entrypoints for Phase 3 validation
- Result:
  - added `BacktestEngine.load_ohlcv_from_db(...)`
  - added separate DB-backed sample functions in `finance/sample.py`
  - kept the old `get_*` functions unchanged
- Durable output:
  - `finance/engine.py`
  - `finance/sample.py`
  - `.note/finance/phase3/PHASE3_DB_SAMPLE_ENTRYPOINTS.md`

### 2026-03-22 - Verify missing ETF OHLCV rows for DB-backed sample testing
- Request topic:
  - confirm whether `VIG`, `SCHD`, `DGRO`, `GLD` actually exist in MySQL price history after the DB-backed equal-weight sample raised a missing-data error
- Interpreted goal:
  - distinguish between a loader bug and a genuine data-availability problem
- Result:
  - confirmed that `finance_price.nyse_price_history` currently has no rows for:
    - `VIG`
    - `SCHD`
    - `DGRO`
    - `GLD`
  - confirmed that the same symbols do exist in `finance_meta.nyse_etf`
  - confirmed that ETF OHLCV is not stored in a separate ETF-specific price table; both stock and ETF OHLCV go into the same `finance_price.nyse_price_history` table
  - likely cause: the earlier collection path did not actually ingest those ETF symbols into price history

### 2026-03-22 - Harden OHLCV ingestion for shared stock and ETF price collection
- Request topic:
  - update OHLCV DB collection so stock and ETF can both be collected smoothly, reduce all-symbol collection latency, and make Daily Market Update behave correctly
- Interpreted goal:
  - keep a single shared price ledger for mixed-asset backtesting while fixing both ingestion performance and Daily Market Update correctness
- Result:
  - decided to keep stock and ETF OHLCV in the same `finance_price.nyse_price_history` table
  - improved the low-level OHLCV writer by adding:
    - true `start/end` support
    - parallel batch fetches
    - retry/backoff
    - missing-symbol / symbols-with-data stats
  - fixed the Manual preset/custom symbol UX in the Streamlit app
  - changed Daily Market Update defaults toward a stock + ETF broad market refresh
  - validated ETF ingestion for `VIG`, `SCHD`, `DGRO`, `GLD`
  - validated DB-backed ETF equal-weight sample execution
- Durable output:
  - `.note/finance/phase3/PHASE3_OHLCV_INGESTION_HARDENING_TODO.md`
  - `.note/finance/phase3/PHASE3_OHLCV_STORAGE_DECISION.md`
  - `.note/finance/phase3/PHASE3_OHLCV_INGESTION_VALIDATION.md`
  - `finance/data/data.py`
  - `app/jobs/ingestion_jobs.py`
  - `app/web/streamlit_app.py`
  - `.note/finance/FINANCE_COMPREHENSIVE_ANALYSIS.md`

### 2026-03-22 - Defer deeper yfinance optimization and extend broad fundamentals/factors loaders
- Request topic:
  - keep the current OHLCV hardening result, defer deeper yfinance optimization for later, and continue to the next Phase 3 step
- Interpreted goal:
  - preserve momentum by moving from ingestion stabilization back into loader/runtime expansion
- Result:
  - recorded that deeper yfinance / very-large-universe optimization will be handled later
  - implemented broad fundamentals and factors loaders under `finance/loaders/*`
  - verified the new loaders against local DB data for `AAPL`, `MSFT`, and `GOOG`
- Durable output:
  - `finance/loaders/fundamentals.py`
  - `finance/loaders/factors.py`
  - `finance/loaders/__init__.py`
  - `.note/finance/FINANCE_COMPREHENSIVE_ANALYSIS.md`

### 2026-03-22 - Implement broad and strict financial statement loaders
- Request topic:
  - continue Phase 3 by finishing the financial statement loader layer
- Interpreted goal:
  - complete the first broad/strict loader set so the read-path covers price, fundamentals, factors, and detailed statements
- Result:
  - implemented:
    - `load_statement_values(...)`
    - `load_statement_labels(...)`
    - `load_statement_snapshot_strict(...)`
  - verified the new loaders against local annual statement data for `AAPL` and `MSFT`
  - confirmed that the broad/strict statement policy is now represented in code, not only in docs
- Durable output:
  - `finance/loaders/financial_statements.py`
  - `finance/loaders/__init__.py`
  - `.note/finance/phase3/PHASE3_STATEMENT_LOADER_VALIDATION.md`
  - `.note/finance/FINANCE_COMPREHENSIVE_ANALYSIS.md`

### 2026-03-22 - Close Phase 3 chapter 1 and open the next runtime chapter
- Request topic:
  - wrap the current Phase 3 work once before moving forward
- Interpreted goal:
  - mark the loader/runtime groundwork as complete, preserve the achieved structure in docs, and open a focused next chapter without prematurely opening a new major phase
- Result:
  - created a dedicated Phase 3 chapter completion summary
  - opened a new Phase 3 TODO board for runtime generalization and Phase 4 handoff preparation
  - updated the master roadmap and finance doc index so the current project position is clearer
- Durable output:
  - `.note/finance/phase3/PHASE3_CHAPTER1_COMPLETION_SUMMARY.md`
  - `.note/finance/phase3/PHASE3_RUNTIME_GENERALIZATION_TODO.md`
  - `.note/finance/MASTER_PHASE_ROADMAP.md`
  - `.note/finance/FINANCE_DOC_INDEX.md`

### 2026-03-22 - Extend Daily Period preset to 20 years
- Request topic:
  - allow `Daily Period` to go beyond `15y` and support `20y`
- Interpreted goal:
  - support longer-horizon OHLCV collection directly from the Streamlit operating console without requiring custom date entry
- Result:
  - added `20y` to the shared period preset list used by Daily Market Update and OHLCV-related UI controls
  - verified locally that yfinance accepts `period='20y'` for daily OHLCV downloads
- Durable output:
  - `app/web/streamlit_app.py`

### 2026-03-22 - Analyze discrepancy between direct sample results and DB-backed sample results
- Request topic:
  - explain why `portfolio_sample(...)` and `portfolio_sample_from_db(...)` return materially different backtest metrics from the same nominal start point
- Interpreted goal:
  - distinguish between expected DB-vs-provider differences and real runtime/data bugs before changing the strategy path further
- Result:
  - identified two separate root causes:
    1. `finance_price.nyse_price_history` is still mixed-state for older OHLCV history
       - several dividend-paying assets have legacy rows where `close` matches provider `Adj Close` rather than raw `Close`
       - example pattern was confirmed for `VIG`, `SCHD`, `DGRO`, `SPY`, `TLT`, `IEF`, `LQD`, `QQQ`, `IWM`, `SOXX`, `BIL`, `MTUM`
       - this explains why even `Equal Weight` can start on the same date but end with a different balance under DB-backed execution
    2. DB-backed sample functions load from the requested `start` date before computing warmup-dependent indicators
       - `get_gtaa3_from_db(...)`, `get_risk_parity_trend_from_db(...)`, and `get_dual_momentum_from_db(...)` call `load_ohlcv_from_db(start=...)` first, then compute `MA200` and trailing return columns
       - the legacy direct-fetch sample path loads a longer period first, computes indicators, and only slices after that
       - this explains the later DB-backed start dates such as `2016-10-31` and `2017-10-31`
- Durable output:
  - issue analysis recorded in this log

### 2026-03-22 - Align DB-backed sample warmup behavior with the direct runtime path
- Request topic:
  - proceed with the discrepancy fix after identifying the causes
- Interpreted goal:
  - remove the avoidable runtime-order mismatch first, while leaving the historical OHLCV mixed-state issue as a separate data cleanup track
- Result:
  - added `history_start` support to `BacktestEngine.load_ohlcv_from_db(...)`
  - updated DB-backed sample functions so indicator-heavy strategies load buffered history first and slice back to the requested range afterwards
  - revalidated that `GTAA`, `Risk Parity`, and `Dual Momentum` now start on the same first month-end date and row count as the direct sample path
  - remaining performance differences are now attributable mainly to `nyse_price_history` historical price-state inconsistency
- Durable output:
  - `finance/engine.py`
  - `finance/sample.py`
  - `.note/finance/phase3/PHASE3_DB_SAMPLE_ALIGNMENT_VALIDATION.md`
  - `.note/finance/FINANCE_COMPREHENSIVE_ANALYSIS.md`

### 2026-03-22 - Re-check remaining discrepancy after warmup alignment
- Request topic:
  - verify whether any further code changes are still needed after the DB-backed sample warmup fix
- Interpreted goal:
  - separate remaining runtime-order issues from underlying DB price-history consistency problems
- Result:
  - confirmed that the warmup-related discrepancy is resolved:
    - DB-backed `GTAA`, `Risk Parity`, and `Dual Momentum` now start on the same first month-end and have the same row counts as the direct path
  - confirmed that the remaining performance gap is data-driven:
    - many symbols in `finance_price.nyse_price_history` still have `close` values that effectively match provider `Adj Close` instead of raw `Close`
    - `adj_close` is still null across the checked historical DB rows
    - therefore direct provider-based samples and DB-backed samples are still not expected to match until price history is canonicalized or rebuilt
- Durable output:
  - issue analysis recorded in this log

### 2026-03-22 - Canonicalize sample-universe OHLCV and achieve direct-vs-DB sample parity
- Request topic:
  - continue after the remaining discrepancy review and fix the residual gap
- Interpreted goal:
  - make DB-backed sample results match the legacy direct sample results by fixing the historical OHLCV consistency problem, not only the runtime order
- Result:
  - hardened the OHLCV writer so explicit `end` is treated as inclusive when fetching from yfinance
  - prevented blank price rows from being inserted during canonical refresh
  - allowed requested OHLCV ranges to be replaced and reinserted cleanly
  - rebuilt the sample strategy universe in `finance_price.nyse_price_history`
  - revalidated parity between direct and DB-backed sample paths for:
    - `Equal Weight`
    - `GTAA`
    - `Risk Parity`
    - `Dual Momentum`
- Durable output:
  - `finance/data/data.py`
  - `.note/finance/phase3/PHASE3_DB_SAMPLE_ALIGNMENT_VALIDATION.md`
  - `.note/finance/FINANCE_COMPREHENSIVE_ANALYSIS.md`

### 2026-03-22 - Summarize what changed between the mismatch state and the final parity state
- Request topic:
  - compare the earlier inconsistent `portfolio_sample(...)` / `portfolio_sample_from_db(...)` outputs with the final matching outputs and explain what changed
- Interpreted goal:
  - leave a durable team-facing record of the root causes, observed before/after metrics, and the exact fixes that restored parity
- Result:
  - created a comparison-focused postmortem document that captures:
    - the earlier mismatched metrics
    - the two root causes
    - the runtime-order fix
    - the canonical OHLCV rebuild fix
    - the final matching state
- Durable output:
  - `.note/finance/phase3/PHASE3_PORTFOLIO_SAMPLE_PARITY_POSTMORTEM.md`

### 2026-03-22 - Separate the roles of the direct-fetch sample path and the DB-backed runtime path
- Request topic:
  - continue Phase 3 after restoring sample parity
- Interpreted goal:
  - reduce confusion between the old provider-backed sample route and the newer DB-backed runtime route before moving further into runtime generalization
- Result:
  - documented the runtime path split in a dedicated Phase 3 note
  - updated `finance/sample.py` docstrings to make the distinction explicit in code
  - advanced the Phase 3 runtime-generalization board to the next strategy-alignment step
- Durable output:
  - `.note/finance/phase3/PHASE3_RUNTIME_PATH_ROLE_SPLIT.md`
  - `finance/sample.py`

### 2026-03-22 - Unify the common runtime start pattern for price-only strategy samples
- Request topic:
  - continue the next Phase 3 runtime-generalization step
- Interpreted goal:
  - reduce duplicated engine start logic across direct-fetch and DB-backed price-only sample functions before expanding runtime alignment further
- Result:
  - added `_build_price_only_engine(...)` in `finance/sample.py`
  - refactored the direct / DB-backed sample pairs for:
    - `Equal Weight`
    - `GTAA`
    - `Risk Parity`
    - `Dual Momentum`
  - documented the common pattern in a dedicated Phase 3 note
  - advanced the runtime-generalization board from `B-1` to `B-2`
- Durable output:
  - `finance/sample.py`
  - `.note/finance/phase3/PHASE3_PRICE_ONLY_RUNTIME_PATTERN.md`
  - `.note/finance/phase3/PHASE3_RUNTIME_GENERALIZATION_TODO.md`

### 2026-03-22 - Remove the recurring Pandas SettingWithCopy warning in transform filtering
- Request topic:
  - explain and clean up the `SettingWithCopyWarning` seen during DB-backed sample execution
- Interpreted goal:
  - confirm whether the warning reflects a real issue and remove it if it is just an unsafe Pandas assignment pattern
- Result:
  - identified the warning source in `filter_finance_history(...)`
  - changed the grouped result to an explicit `.copy()`
  - aligned dividend sums by grouped index before assignment
  - re-ran the DB-backed Equal Weight smoke path and confirmed the warning no longer appears
- Durable output:
  - `finance/transform.py`

### 2026-03-22 - Define the runtime connection points for future factor and fundamental strategies
- Request topic:
  - continue the next Phase 3 runtime-generalization step
- Interpreted goal:
  - prevent future factor / fundamental strategy work from becoming sample-specific glue by fixing the loader-to-runtime boundary first
- Result:
  - documented that price-only runtime is a special case and future accounting-driven strategies should use:
    - loader
    - rebalance-date snapshot connection helper
    - strategy
  - clarified that `BacktestEngine` should not absorb ad hoc factor / fundamental query logic before the snapshot payload contract is fixed
  - advanced the active board from `B-2` to `B-3`
- Durable output:
  - `.note/finance/phase3/PHASE3_FACTOR_FUNDAMENTAL_RUNTIME_CONNECTIONS.md`
  - `.note/finance/phase3/PHASE3_RUNTIME_GENERALIZATION_TODO.md`

### 2026-03-22 - Fix the Phase 3 strategy input contract at the runtime payload level
- Request topic:
  - continue the next Phase 3 runtime-generalization step after defining factor / fundamental connection points
- Interpreted goal:
  - make the expected runtime payload explicit before Phase 4 handoff so future strategy work does not reinvent incompatible input shapes
- Result:
  - documented the current runtime input contract split:
    - price-only strategies use `{ticker: price_df}`
    - future factor / fundamental strategies should use
      `price_dfs + snapshot_by_date + rebalance_dates`
  - aligned the active Phase 3 board and comprehensive analysis document with that contract
  - advanced the board from `B-3` to `C-1`
- Durable output:
  - `.note/finance/phase3/PHASE3_RUNTIME_STRATEGY_INPUT_CONTRACT.md`
  - `.note/finance/phase3/PHASE3_RUNTIME_GENERALIZATION_TODO.md`

### 2026-03-22 - Reassess the roles and collection quality of `nyse_fundamentals` and `nyse_factors`
- Request topic:
  - analyze whether `nyse_fundamentals` / `nyse_factors` are correctly collected and calculated, decide whether they should remain, and strengthen them for future factor-based backtests
- Interpreted goal:
  - treat the two tables as proto-era structures that may be redefined or rebuilt now, while keeping the long-term product centered on valid factor/fundamental strategy inputs
- Result:
  - concluded that both tables should remain, but not as raw truth
  - fixed their target roles as:
    - `nyse_fundamentals`: broad coverage summary layer
    - `nyse_factors`: broad research derived layer
  - kept `nyse_financial_statement_filings/values/labels` as the strict raw ledger path
  - hardened fundamentals ingestion by adding:
    - more base accounting fields
    - derivation/source metadata
    - blank-row filtering
    - canonical symbol/freq refresh behavior
  - hardened factor calculation by adding:
    - price attachment metadata
    - broader valuation / margin / leverage / growth factor coverage
    - canonical symbol/freq refresh behavior
  - validated the new path on `AAPL`, `MSFT` annual/quarterly samples
  - documented that a full-universe backfill is still a separate operational decision
- Durable output:
  - `.note/finance/phase3/PHASE3_FUNDAMENTALS_FACTORS_HARDENING_TODO.md`
  - `.note/finance/phase3/PHASE3_FUNDAMENTALS_FACTORS_REVIEW_AND_DIRECTION.md`
  - `finance/data/fundamentals.py`
  - `finance/data/factors.py`
  - `finance/data/db/schema.py`

### 2026-03-22 - Decide whether `nyse_fundamentals` should store all yfinance statement values or only curated fields
- Request topic:
  - clarify whether the project should store every value from yfinance financial statements in `nyse_fundamentals` / `nyse_factors`, or keep only selected important fields
- Interpreted goal:
  - lock the table philosophy now while schema changes and data loss are still acceptable
- Result:
  - decided that `nyse_fundamentals` / `nyse_factors` should stay curated
  - they should store normalized, intentionally selected fields that are useful for downstream factor research and backtests
  - storing every provider field inside `nyse_fundamentals` is not recommended because:
    - provider labels are unstable
    - many fields are redundant or issuer-specific
    - table meaning becomes ambiguous
    - summary/derived layers become harder to validate
  - if full provider retention is ever needed, that should be a separate raw provider table, not `nyse_fundamentals`
  - long-term raw truth remains the detailed statement ledger (`filings/values/labels`)
- Durable output:
  - no code change
  - architectural direction fixed in analysis log

### 2026-03-22 - Defer full-universe fundamentals/factors backfill and return to the main Phase 3 runtime board
- Request topic:
  - after the fundamentals/factors hardening detour, return to the original Phase 3 next step instead of running a full-universe backfill immediately
- Interpreted goal:
  - keep the hardening outcome, but avoid turning this turn into a long operational backfill job and continue runtime-phase execution
- Result:
  - marked the hardening workstream complete with full backfill explicitly deferred
  - returned to the main `PHASE3_RUNTIME_GENERALIZATION_TODO.md` board
  - completed `C-1` by documenting a repeatable DB-backed smoke-scenario set for regression checks
- Durable output:
  - `.note/finance/phase3/PHASE3_REPEATABLE_DB_BACKED_SMOKE_SCENARIOS.md`
  - `.note/finance/phase3/PHASE3_RUNTIME_GENERALIZATION_TODO.md`
  - `.note/finance/phase3/PHASE3_FUNDAMENTALS_FACTORS_HARDENING_TODO.md`

### 2026-03-22 - Add ready-to-run loader/runtime validation examples for Phase 3
- Request topic:
  - continue the next Phase 3 runtime-generalization step after defining repeatable smoke scenarios
- Interpreted goal:
  - make the validation harness easier to execute by pairing the scenario list with concrete example snippets
- Result:
  - added a dedicated validation-examples document covering:
    - price loader to strategy-dict path
    - engine DB price path
    - DB-backed sample strategy
    - direct vs DB parity
    - fundamentals/factors loader examples
    - statement loader examples
    - fundamentals/factors rebuild examples
  - advanced the main Phase 3 board from `C-2` to `C-3`
- Durable output:
  - `.note/finance/phase3/PHASE3_LOADER_RUNTIME_VALIDATION_EXAMPLES.md`
  - `.note/finance/phase3/PHASE3_RUNTIME_GENERALIZATION_TODO.md`

### 2026-03-22 - Split the Phase 3 runtime cleanup backlog and define the first UI runtime function candidates
- Request topic:
  - continue the next Phase 3 runtime-generalization steps after the validation examples work
- Interpreted goal:
  - separate non-blocking cleanup/optimization items from the active board
  - then begin Phase 4 handoff prep by fixing the minimal public runtime entrypoint direction for the future UI
- Result:
  - created a dedicated runtime cleanup backlog document that distinguishes:
    - items already resolved during Phase 3
    - deferred operational work
    - deferred optimization work
    - deferred architecture work
  - marked `C-3` complete on the main runtime-generalization board
  - created a dedicated document for minimal UI runtime function candidates
  - decided that the Phase 4 first pass should not call `sample.py` or raw engine chains directly
  - fixed the recommended UI runtime direction as:
    - strategy-specific DB-backed runtime wrappers
    - plus a shared backtest result bundle builder
  - advanced the main board from `D-1` to `D-2`
- Durable output:
  - `.note/finance/phase3/PHASE3_RUNTIME_CLEANUP_BACKLOG.md`
  - `.note/finance/phase3/PHASE3_UI_RUNTIME_FUNCTION_CANDIDATES.md`
  - `.note/finance/phase3/PHASE3_RUNTIME_GENERALIZATION_TODO.md`

### 2026-03-22 - Define the minimal user-facing input set for the future strategy execution UI
- Request topic:
  - continue the next Phase 3 runtime-generalization step by fixing what users should directly input in the first strategy execution UI
- Interpreted goal:
  - keep the first UI small and stable by exposing only the minimum fields needed for DB-backed price-only strategy execution
- Result:
  - created a dedicated document for the Phase 4 first-pass user-facing input set
  - fixed the first-pass minimal input groups as:
    - strategy
    - universe mode plus tickers or preset
    - start/end date
  - decided to keep the following hidden or advanced by default:
    - `timeframe`
    - engine option details
    - warmup/history buffer
    - DB/direct mode
    - most strategy-specific tuning params
  - documented that future factor/fundamental strategy UI will need additional inputs such as rebalance frequency and snapshot mode, but that is outside the first pass
  - advanced the main board from `D-2` to `D-3`
- Durable output:
  - `.note/finance/phase3/PHASE3_UI_USER_INPUT_SET_DRAFT.md`
  - `.note/finance/phase3/PHASE3_RUNTIME_GENERALIZATION_TODO.md`

### 2026-03-22 - Define the first result bundle shape for the future strategy execution UI
- Request topic:
  - continue the next Phase 3 runtime-generalization step by fixing the output structure that UI-facing runtime wrappers should return
- Interpreted goal:
  - make the future strategy execution UI simple to implement by standardizing a minimal, reusable runtime result bundle
- Result:
  - created a dedicated Phase 3 result-bundle draft document
  - fixed the recommended first-pass result bundle shape as:
    - `strategy_name`
    - `result_df`
    - `summary_df`
    - `chart_df`
    - `meta`
  - decided to reuse `portfolio_performance_summary(...)` for summary generation
  - decided to keep `chart_df` as a thin chart-friendly projection of `result_df`
  - explicitly deferred richer fields such as trade logs and position tables to later phases
  - marked `D-3` complete and moved the runtime-generalization board to chapter completion review state
- Durable output:
  - `.note/finance/phase3/PHASE3_UI_RESULT_BUNDLE_DRAFT.md`
  - `.note/finance/phase3/PHASE3_RUNTIME_GENERALIZATION_TODO.md`

### 2026-03-22 - Open Phase 4 and lock the user-confirmation rule for UI choices
- Request topic:
  - move into Phase 4 and require that non-obvious UI/runtime choices are not decided unilaterally
- Interpreted goal:
  - begin the strategy execution UI phase, but make sure product-facing decisions are explained as concrete options and only implemented after the user selects one
- Result:
  - opened Phase 4 planning and the first Phase 4 chapter board
  - marked Phase 4 active in the master roadmap
  - fixed an explicit collaboration rule in the Phase 4 plan:
    - UI structure, public runtime boundary, and related UX choices must be explained as alternatives first
    - implementation should proceed only after the user chooses a direction
  - set the first active Phase 4 task to `A-1 UI 구조 선택지 정리`
- Durable output:
  - `.note/finance/phase4/PHASE4_UI_AND_BACKTEST_PLAN.md`
  - `.note/finance/phase4/PHASE4_CURRENT_CHAPTER_TODO.md`
  - `.note/finance/MASTER_PHASE_ROADMAP.md`

### 2026-03-22 - Choose a separate Streamlit backtest app for the first Phase 4 UI structure
- Request topic:
  - after opening Phase 4, choose one of the UI structure options for the first backtest UI implementation
- Interpreted goal:
  - lock the first UI structure before runtime wrapper implementation begins
- Result:
  - selected the separate-app option
  - fixed the Phase 4 first UI structure as:
    - `app/web/streamlit_app.py` remains the ingestion/operations console
    - `app/web/backtest_app.py` becomes the backtest UI entrypoint
  - created a structure decision document and a first backtest app shell
  - advanced the Phase 4 first chapter from UI structure decision to runtime public boundary work
- Durable output:
  - `.note/finance/phase4/PHASE4_UI_STRUCTURE_DECISION.md`
  - `.note/finance/phase4/PHASE4_CURRENT_CHAPTER_TODO.md`

### 2026-03-22 - Revise the Phase 4 UI structure to one main app with separate ingestion/backtest tabs
- Request topic:
  - after reviewing the separate-app direction, clarify that the desired product shape is one main app with collection and analysis together, but managed through separate scripts/modules
- Interpreted goal:
  - preserve a unified user experience while still keeping the codebase organized by concern
- Result:
  - revised the Phase 4 structure decision
  - fixed the first UI structure as:
    - one main `streamlit_app.py`
    - ingestion tab + backtest tab
    - internal code split by tab/concern rather than one giant file
  - removed the previously created separate `backtest_app.py` direction to avoid stale architecture drift
- Durable output:
  - `.note/finance/phase4/PHASE4_UI_STRUCTURE_DECISION.md`
  - `.note/finance/phase4/PHASE4_UI_AND_BACKTEST_PLAN.md`
  - `.note/finance/phase4/PHASE4_CURRENT_CHAPTER_TODO.md`

### 2026-03-22 - Implement the first unified-app tab shell for Phase 4
- Request topic:
  - reflect the chosen one-app structure in the actual Streamlit code without yet deciding the first backtest screen details
- Interpreted goal:
  - make the unified product shape visible in code while keeping future UI/runtime choices open for later user confirmation
- Result:
  - updated `app/web/streamlit_app.py` to use two tabs:
    - `Ingestion`
    - `Backtest`
  - added the first tab-specific module:
    - `app/web/pages/backtest.py`
  - kept the backtest tab as a placeholder so the next decisions can still be made explicitly with the user
- Durable output:
  - `app/web/streamlit_app.py`
  - `app/web/pages/backtest.py`

### 2026-03-22 - Fix the first public Phase 4 runtime wrapper boundary
- Request topic:
  - proceed with the first public runtime wrapper after choosing `Equal Weight` as the first exposed backtest strategy
- Interpreted goal:
  - make the Backtest tab call a stable DB-backed wrapper instead of `sample.py` or raw engine chains
- Result:
  - added `app/web/runtime/backtest.py`
  - implemented:
    - `run_equal_weight_backtest_from_db(...)`
    - `build_backtest_result_bundle(...)`
  - fixed the first public runtime boundary around:
    - normalized tickers
    - DB-backed `Equal Weight` execution
    - shared UI-facing bundle construction
- Durable output:
  - `.note/finance/phase4/PHASE4_RUNTIME_WRAPPER_SIGNATURES.md`
  - `app/web/runtime/backtest.py`

### 2026-03-22 - Implement the first Backtest tab execution form
- Request topic:
  - after fixing the first public wrapper boundary, start with the execution form before rendering results
- Interpreted goal:
  - visualize the minimum user-facing input contract for the first `Equal Weight` screen without yet widening the implementation scope
- Result:
  - added a first-pass `Equal Weight` form to the Backtest tab
  - included:
    - preset/manual universe selection
    - start/end date inputs
    - advanced inputs for timeframe / option / rebalance interval
    - runtime payload preview on submit
  - kept actual wrapper execution and result rendering for the next step
- Durable output:
  - `.note/finance/phase4/PHASE4_FIRST_SCREEN_SCOPE.md`
  - `app/web/pages/backtest.py`

### 2026-03-22 - Connect the first Backtest form to the public runtime wrapper
- Request topic:
  - after the first `Equal Weight` form was opened, connect it to the real DB-backed runtime path
- Interpreted goal:
  - let the Backtest tab execute the first public wrapper end-to-end without yet broadening scope to multiple strategies
- Result:
  - connected form submit to `run_equal_weight_backtest_from_db(...)`
  - added first-pass UI output for:
    - success/error state
    - summary table
    - Total Balance chart
    - execution meta
    - result preview table
  - kept the next UI step focused on result layout polish rather than strategy expansion
- Durable output:
  - `app/web/pages/backtest.py`

### 2026-03-22 - Polish the first Backtest result layout
- Request topic:
  - after connecting the first runtime path, make the result area read more like a product surface
- Interpreted goal:
  - improve readability without expanding scope to a second strategy or a more complex analytics surface
- Result:
  - replaced the flat first-pass result view with:
    - KPI metric row
    - `Summary / Equity Curve / Result Table / Meta` tabs
  - kept the chart focused on `Total Balance` only for the first pass
  - separated raw result preview from execution metadata to reduce visual clutter
- Durable output:
  - `.note/finance/phase4/PHASE4_FIRST_RESULT_LAYOUT_DRAFT.md`
  - `app/web/pages/backtest.py`

### 2026-03-22 - Harden first-pass backtest error and empty-result handling
- Request topic:
  - before moving to the next Phase 4 expansion, make the first `Equal Weight` screen handle failure cases more clearly
- Interpreted goal:
  - keep the first screen usable when inputs are invalid or DB-backed OHLCV is missing, without widening the feature scope
- Result:
  - introduced runtime-side error classes:
    - `BacktestInputError`
    - `BacktestDataError`
  - added DB preflight checks for requested tickers/date range
  - separated UI handling for:
    - input problems
    - data-availability problems
    - generic execution failures
  - added a durable Phase 4 note for error/empty-result rules
- Durable output:
  - `.note/finance/phase4/PHASE4_ERROR_AND_EMPTY_RESULT_RULES.md`
  - `app/web/runtime/backtest.py`
  - `app/web/pages/backtest.py`

### 2026-03-22 - Add GTAA as the second public Phase 4 strategy
- Request topic:
  - after stabilizing the first `Equal Weight` path, add a second strategy rather than moving immediately to visualization or history
- Interpreted goal:
  - confirm that the Phase 4 public runtime boundary and first UI can scale beyond a trivial strategy while still staying within price-only scope
- Result:
  - added `run_gtaa_backtest_from_db(...)`
  - extended the Backtest tab to switch between:
    - `Equal Weight`
    - `GTAA`
  - added a GTAA-specific form including `top` parameter input
  - verified the GTAA wrapper with DB-backed parity output
- Durable output:
  - `.note/finance/phase4/PHASE4_SECOND_STRATEGY_GTAA_ADDITION.md`
  - `app/web/runtime/backtest.py`
  - `app/web/pages/backtest.py`

### 2026-03-22 - Add Risk Parity Trend as the third public Phase 4 strategy
- Request topic:
  - after `Equal Weight` and `GTAA`, continue expanding the first Phase 4 public strategy set with another price-only strategy
- Interpreted goal:
  - broaden the first UI to cover a different portfolio-construction style without yet moving into factor/fundamental strategy territory
- Result:
  - added `run_risk_parity_trend_backtest_from_db(...)`
  - extended the Backtest tab strategy selector to:
    - `Equal Weight`
    - `GTAA`
    - `Risk Parity Trend`
  - added a Risk Parity Trend form with its default universe
  - verified DB-backed wrapper parity for the default sample universe
- Durable output:
  - `.note/finance/phase4/PHASE4_THIRD_STRATEGY_RISK_PARITY_ADDITION.md`
  - `app/web/runtime/backtest.py`
  - `app/web/pages/backtest.py`

### 2026-03-22 - Update finance skills to match the project's current Phase 3 operating patterns
- Request topic:
  - review whether the existing finance-related Codex skills should be updated based on the work completed so far, then apply the recommended updates
- Interpreted goal:
  - make future Codex turns more consistent with the repo's current runtime, loader, documentation, and ingestion conventions
- Result:
  - updated `finance-strategy-implementation` to reflect:
    - direct-fetch vs DB-backed sample/runtime role separation
    - warmup/history buffer expectations for indicator strategies
    - UI-facing runtime wrappers as a separate concern from sample functions
  - updated `finance-doc-sync` to reflect:
    - phase-based document management
    - TODO board synchronization
    - `FINANCE_DOC_INDEX.md` updates when new durable docs are created
  - updated `finance-factor-pipeline` to reflect:
    - `nyse_fundamentals` as curated summary layer
    - `nyse_factors` as broad research derived layer
    - full backfill as a separate operational step from code hardening
  - updated `finance-db-pipeline` to reflect:
    - stock + ETF shared `nyse_price_history`
    - canonical refresh for legacy mixed-state data
    - inclusive `end` and blank-row prevention expectations for OHLCV collection
- Durable output:
  - `/Users/taeho/.codex/skills/finance-strategy-implementation/SKILL.md`
  - `/Users/taeho/.codex/skills/finance-doc-sync/SKILL.md`
  - `/Users/taeho/.codex/skills/finance-factor-pipeline/SKILL.md`
  - `/Users/taeho/.codex/skills/finance-db-pipeline/SKILL.md`

### 2026-03-22 - Add Dual Momentum as the fourth public DB-backed Phase 4 strategy
- Request topic:
  - continue the Phase 4 Backtest tab expansion by adding `Dual Momentum` after `Equal Weight`, `GTAA`, and `Risk Parity Trend`
- Interpreted goal:
  - expose the fourth representative price-only strategy through the same public runtime wrapper and unified Backtest tab UI
- Result:
  - added `run_dual_momentum_backtest_from_db(...)` as the fourth public runtime wrapper
  - expanded the Backtest strategy selector to:
    - `Equal Weight`
    - `GTAA`
    - `Risk Parity Trend`
    - `Dual Momentum`
  - added a Dual Momentum-specific execution form using the default universe `QQQ, SPY, IWM, SOXX, BIL`
  - verified DB-backed runtime smoke output with `End Balance = 24600.7`
- Durable output:
  - `.note/finance/phase4/PHASE4_FOURTH_STRATEGY_DUAL_MOMENTUM_ADDITION.md`
  - `app/web/runtime/backtest.py`
  - `app/web/pages/backtest.py`

### 2026-03-22 - Plan the next Phase 4 step for visualization strengthening and weighted portfolio construction
- Request topic:
  - strengthen Backtest-tab visualization, add weighted strategy-combination portfolios, and support multi-strategy graphs in one view
- Interpreted goal:
  - move the first-pass single-strategy UI toward a more practical research dashboard without breaking the existing Phase 4 public runtime boundary
- Result:
  - confirmed local code already has usable primitives:
    - `make_monthly_weighted_portfolio(...)`
    - summary helpers
    - multi-curve comparison helpers
  - concluded this is primarily a UI-flow decision, not a missing-core-logic problem
  - documented explicit choices for:
    - screen structure
    - implementation order
    - comparison scope
  - current recommended direction:
    - split the Backtest tab into `Single Strategy` and `Compare / Portfolio Builder`
    - build comparison first
    - then weighted portfolio builder
    - then richer annotations like top/bottom periods
- Durable output:
  - `.note/finance/phase4/PHASE4_VISUALIZATION_AND_PORTFOLIO_BUILDER_OPTIONS.md`

### 2026-03-22 - Implement the selected Phase 4 compare-first path with weighted portfolio builder
- Request topic:
  - proceed with the recommended Phase 4 route:
    - split the Backtest tab into `Single Strategy` and `Compare & Portfolio Builder`
    - implement comparison first
    - then open weighted portfolio construction
    - allow comparison up to 4 strategies
- Interpreted goal:
  - make the Backtest tab useful for research workflows where multiple DB-backed strategies must be compared and combined, while keeping the current public runtime boundary intact
- Result:
  - split the Backtest tab into:
    - `Single Strategy`
    - `Compare & Portfolio Builder`
  - added multi-strategy comparison for up to 4 strategies
  - added:
    - summary comparison table
    - equity overlay chart
    - drawdown overlay chart
    - execution meta table
  - added a first-pass weighted portfolio builder that reuses comparison results
  - verified a concrete example:
    - `Dual Momentum 50 + GTAA 50`
    - `Weighted Portfolio End Balance = 23594.9`
- Durable output:
  - `.note/finance/phase4/PHASE4_COMPARE_AND_WEIGHTED_PORTFOLIO_FIRST_PASS.md`
  - `app/web/pages/backtest.py`

### 2026-03-22 - Fix GTAA visibility in the compare equity overlay
- Request topic:
  - investigate why `GTAA` looked missing in the compare equity overlay
- Interpreted goal:
  - determine whether the compare-mode data path was broken or whether the chart was failing to present a sparse strategy clearly
- Result:
  - confirmed this was not a runtime/data bug
  - `GTAA` result rows are intentionally sparser because the strategy output only has rebalance-period observations
  - the original `st.line_chart` compare rendering made sparse paths hard to see
  - updated compare charts to use `line + point` Altair rendering so sparse strategies remain visible
- Durable output:
  - `app/web/pages/backtest.py`
  - `.note/finance/phase4/PHASE4_COMPARE_AND_WEIGHTED_PORTFOLIO_FIRST_PASS.md`

### 2026-03-22 - Expose GTAA interval as an advanced input in the Backtest tab
- Request topic:
  - make GTAA's currently fixed `2`-month interval adjustable from the Backtest UI
- Interpreted goal:
  - remove a hardcoded GTAA cadence from the user-facing execution path while keeping the existing default behavior intact
- Result:
  - added `interval` support to:
    - `get_gtaa3(...)`
    - `get_gtaa3_from_db(...)`
    - `run_gtaa_backtest_from_db(...)`
  - added `Signal Interval (months)` to the GTAA advanced inputs in the Backtest UI
  - verified the parameter changes both runtime meta and end result:
    - `interval=2` -> `End Balance = 22589.1`
    - `interval=1` -> `End Balance = 23383.5`
- Durable output:
  - `finance/sample.py`
  - `app/web/runtime/backtest.py`
  - `app/web/pages/backtest.py`

### 2026-03-22 - Allow strategy-specific advanced overrides inside compare mode
- Request topic:
  - make the compare-strategies screen support advanced input changes for each selected strategy
- Interpreted goal:
  - keep the compare flow shared at the date/timeframe layer, while still allowing each strategy to expose its own meaningful tuning parameters
- Result:
  - compare mode now supports per-strategy advanced overrides for:
    - `Equal Weight`: rebalance interval
    - `GTAA`: top assets, signal interval
    - `Risk Parity Trend`: rebalance interval, vol window
    - `Dual Momentum`: top assets, rebalance interval
  - extended sample/runtime wrappers where needed so the overrides reach the actual backtest execution path
  - verified that changed compare inputs propagate to both runtime meta and end results
- Durable output:
  - `finance/sample.py`
  - `app/web/runtime/backtest.py`
  - `app/web/pages/backtest.py`
  - `.note/finance/phase4/PHASE4_COMPARE_AND_WEIGHTED_PORTFOLIO_FIRST_PASS.md`

### 2026-03-22 - Add first-pass persistent backtest history
- Request topic:
  - start with backtest execution history as the next Phase 4 improvement
- Interpreted goal:
  - make the Backtest tab usable as a research surface where previous runs can be reviewed instead of disappearing after execution
- Result:
  - added a dedicated backtest-history JSONL path:
    - `.note/finance/BACKTEST_RUN_HISTORY.jsonl`
  - implemented append/load helpers in:
    - `app/web/runtime/history.py`
  - wired history recording for:
    - single strategy execution
    - strategy comparison
    - weighted portfolio build
  - added a `Persistent Backtest History` section in the Backtest tab
  - verified append/load behavior for all three run kinds and cleared the temporary validation file afterwards
- Durable output:
  - `.note/finance/phase4/PHASE4_BACKTEST_HISTORY_FIRST_PASS.md`
  - `app/web/runtime/history.py`
  - `app/web/runtime/__init__.py`
  - `app/web/pages/backtest.py`

### 2026-03-22 - Add first-pass visualization enhancements to the Backtest tab
- Request topic:
  - move on to visualization strengthening after the first pass of backtest history
- Interpreted goal:
  - make single-strategy and compare views easier to interpret without changing the public runtime boundary again
- Result:
  - single strategy:
    - upgraded the equity curve to an Altair chart with `High / Low / End` markers
    - added a `Period Extremes` tab for top 3 best / worst periods by `Total Return`
  - compare mode:
    - added a `Total Return` overlay tab
  - verified both helper outputs and compare datasets locally
- Durable output:
  - `.note/finance/phase4/PHASE4_VISUALIZATION_ENHANCEMENT_FIRST_PASS.md`
  - `app/web/pages/backtest.py`

### 2026-03-22 - Extend visualization markers to best/worst periods and weighted portfolio
- Request topic:
  - continue the recommended visualization-improvement path after the first-pass charts landed
- Interpreted goal:
  - make the equity curve itself more explanatory and keep the weighted-portfolio result view aligned with the single-strategy reading experience
- Result:
  - single-strategy equity charts now annotate not only `High / Low / End` but also `Best Period / Worst Period`
  - weighted-portfolio results now reuse the same marker-based equity chart and `Period Extremes` tab structure
  - Phase 4 planning/docs were synced so the implemented visualization state no longer lagged behind the code
- Durable output:
  - `.note/finance/phase4/PHASE4_VISUALIZATION_ENHANCEMENT_FIRST_PASS.md`
  - `.note/finance/phase4/PHASE4_UI_AND_BACKTEST_PLAN.md`
  - `app/web/pages/backtest.py`

### 2026-03-22 - Deepen compare and weighted visual interpretation
- Request topic:
  - continue with deeper visualization improvements in Phase 4
- Interpreted goal:
  - keep the compare overlay useful at a glance while giving the user a way to inspect one chosen strategy or weighted result in more detail
- Result:
  - compare mode gained a `Focused Strategy` drilldown with:
    - KPI summary
    - marker-based equity curve
    - `Top 3 Balance Highs / Lows`
    - `Top 3 Best / Worst Periods`
  - single-strategy and weighted-portfolio views both gained `Balance Extremes` tables
  - documentation was synced so the implemented Phase 4 visualization state matches the code
- Durable output:
  - `.note/finance/phase4/PHASE4_COMPARE_AND_WEIGHTED_PORTFOLIO_FIRST_PASS.md`
  - `.note/finance/phase4/PHASE4_VISUALIZATION_ENHANCEMENT_FIRST_PASS.md`
  - `app/web/pages/backtest.py`

### 2026-03-22 - Enhance persistent backtest history with filter and drilldown
- Request topic:
  - start the next Phase 4 step by improving backtest history first
- Interpreted goal:
  - turn history from a simple append-only table into a surface where previous runs can be found and inspected again
- Result:
  - added run-kind filtering for:
    - `single_strategy`
    - `strategy_compare`
    - `weighted_portfolio`
  - added text search across strategy, ticker, preset, and selected strategies
  - added a selected-record drilldown with:
    - `Summary`
    - `Input & Context`
    - `Raw Record`
  - synced Phase 4 docs and the finance analysis document to reflect the stronger history surface
- Durable output:
  - `.note/finance/phase4/PHASE4_BACKTEST_HISTORY_ENHANCEMENT_FIRST_PASS.md`
  - `app/web/pages/backtest.py`

### 2026-03-22 - Add weighted portfolio contribution visualization
- Request topic:
  - continue Phase 4 with additional visualization strengthening
- Interpreted goal:
  - make weighted portfolio results explainable, not just report a final end balance
- Result:
  - added a `Contribution` tab to weighted portfolio results
  - added:
    - configured weight vs ending share snapshot
    - stacked contribution amount chart
    - stacked contribution share chart
  - implemented the contribution view as a UI-layer monthly decomposition that follows the same `date_policy` used by the weighted builder
  - verified both a synthetic decomposition and a real `Dual Momentum 50 + GTAA 50` example
- Durable output:
  - `.note/finance/phase4/PHASE4_WEIGHTED_PORTFOLIO_CONTRIBUTION_FIRST_PASS.md`
  - `app/web/pages/backtest.py`

### 2026-03-22 - Add second-pass backtest history controls
- Request topic:
  - continue Phase 4 with the second round of backtest-history improvements
- Interpreted goal:
  - make stored history not only readable but also sortable, date-filterable, and partly reusable
- Result:
  - added `recorded_at` date range filter
  - added metric sort options:
    - end balance
    - CAGR
    - Sharpe ratio
    - drawdown
  - added `Run Again` for supported single-strategy records
  - intentionally kept compare / weighted rerun closed because the current stored context is not yet rich enough to replay them safely
- Durable output:
  - `.note/finance/phase4/PHASE4_BACKTEST_HISTORY_ENHANCEMENT_SECOND_PASS.md`
  - `app/web/pages/backtest.py`

### 2026-03-23 - Add second-pass compare visualization aids
- Request topic:
  - continue Phase 4 with the next round of visualization strengthening
- Interpreted goal:
  - make compare overlays easier to read without forcing the user to switch immediately into single-strategy drilldown
- Result:
  - compare overlay charts now show end markers and strategy labels at the latest point
  - compare mode gained a `Strategy Highlights` tab summarizing each strategy's:
    - high
    - low
    - end
    - best period
    - worst period
  - the Phase 4 docs and finance analysis document were synced to reflect the stronger compare visualization state
- Durable output:
  - `.note/finance/phase4/PHASE4_VISUALIZATION_ENHANCEMENT_SECOND_PASS.md`
  - `app/web/pages/backtest.py`

### 2026-03-23 - Add third-pass backtest history reuse flow
- Request topic:
  - finish the next Phase 4 history enhancement step after the visualization pass
- Interpreted goal:
  - make stored single-strategy backtests easier to filter and safer to reuse without forcing immediate rerun
- Result:
  - added metric threshold filters for:
    - end balance
    - CAGR
    - Sharpe ratio
    - drawdown
  - added `Load Into Form` for supported single-strategy history records
  - wired stored payloads back into the current single-strategy forms through session-state prefill
  - intentionally kept compare / weighted rerun closed because the current stored context is still not rich enough to replay advanced overrides safely
- Durable output:
  - `.note/finance/phase4/PHASE4_BACKTEST_HISTORY_ENHANCEMENT_THIRD_PASS.md`
  - `app/web/pages/backtest.py`

### 2026-03-23 - Tighten metric-threshold handling for history rows with missing values
- Request topic:
  - fix the narrow issue where metric threshold filters did not exclude `None` rows consistently
- Interpreted goal:
  - make enabled metric thresholds behave predictably by excluding rows that do not have the required metric
- Result:
  - when `Min End Balance`, `Min CAGR`, `Min Sharpe Ratio`, or `Max Drawdown` is enabled,
    rows with `None` for that metric are now excluded from the filtered history view
- Durable output:
  - `app/web/pages/backtest.py`

### 2026-03-23 - Open the next Phase 4 chapter for factor / fundamental entry
- Request topic:
  - proceed with the next major Phase 4 step after the price-only UI chapter
- Interpreted goal:
  - transition from completed price-only strategy UI work into the preparation chapter for factor / fundamental strategies
- Result:
  - documented that the first Phase 4 UI execution chapter is effectively complete
  - opened a new Phase 4 TODO board focused on factor / fundamental strategy entry
  - created a first-strategy options memo comparing:
    - Value snapshot strategy
    - Quality snapshot strategy
    - Simple multi-factor strategy
  - narrowed the realistic first candidate set to `Value` or `Quality`
- Durable output:
  - `.note/finance/phase4/PHASE4_UI_CHAPTER1_COMPLETION_SUMMARY.md`
  - `.note/finance/phase4/PHASE4_FACTOR_FUNDAMENTAL_ENTRY_TODO.md`
  - `.note/finance/phase4/PHASE4_FACTOR_FUNDAMENTAL_FIRST_STRATEGY_OPTIONS.md`

### 2026-03-23 - Fix the first factor/fundamental strategy direction to Quality
- Request topic:
  - choose `Quality` as the first factor / fundamental strategy direction
- Interpreted goal:
  - move from generic entry prep into a concrete first-strategy path that can be implemented next
- Result:
  - fixed the first strategy direction to `Quality Snapshot Strategy`
  - documented the first-pass quality factor set around:
    - `roe`
    - `gross_margin`
    - `operating_margin`
    - `debt_ratio`
  - documented the first wrapper shape and narrowed the next unresolved decision to `snapshot_mode`
- Durable output:
  - `.note/finance/phase4/PHASE4_QUALITY_SNAPSHOT_STRATEGY_SCOPE.md`
  - `.note/finance/phase4/PHASE4_QUALITY_RUNTIME_WRAPPER_DRAFT.md`

### 2026-03-23 - Choose broad_research mode and implement the first quality runtime path
- Request topic:
  - proceed with option `1`, using `broad_research` as the first public snapshot mode
- Interpreted goal:
  - move beyond planning and open the first working factor / fundamental runtime path
- Result:
  - fixed `broad_research` as the first public mode for `Quality Snapshot Strategy`
  - implemented the first-pass quality simulation function
  - added a DB-backed sample entrypoint
  - added a public backtest runtime wrapper
  - validated the path on `AAPL/MSFT/GOOG`
- Durable output:
  - `.note/finance/phase4/PHASE4_QUALITY_BROAD_RESEARCH_DECISION.md`
  - `.note/finance/phase4/PHASE4_QUALITY_SNAPSHOT_IMPLEMENTATION_FIRST_PASS.md`
  - `finance/strategy.py`
  - `finance/sample.py`
  - `app/web/runtime/backtest.py`

### 2026-03-23 - Define Quality Snapshot UI inputs and expose it in the Backtest UI
- Request topic:
  - do both:
    1. organize the UI inputs first
    2. then expose the strategy in the UI
- Interpreted goal:
  - avoid dumping too many factor-strategy controls into the UI while still making the first factor strategy actually usable
- Result:
  - documented the first-pass quality UI input split into:
    - basic
    - advanced
    - hidden defaults
  - exposed `Quality Snapshot` as the fifth public strategy in the Backtest selector
  - extended history/meta/prefill support for the quality strategy
  - also allowed first-pass compare exposure for the quality path
- Durable output:
  - `.note/finance/phase4/PHASE4_QUALITY_UI_INPUT_DRAFT.md`
  - `.note/finance/phase4/PHASE4_FIFTH_STRATEGY_QUALITY_ADDITION.md`
  - `app/web/pages/backtest.py`
  - `app/web/runtime/history.py`

### 2026-03-23 - Clarify which ingestion jobs are required for the first-pass Quality Snapshot backtest
- Request topic:
  - ask which collection jobs are needed before running the current quality backtest
- Interpreted goal:
  - identify the minimum required data-refresh path for the new factor/fundamental strategy UI
- Result:
  - confirmed that the current first-pass `Quality Snapshot` strategy reads:
    - DB-backed price history from `finance_price.nyse_price_history`
    - factor snapshots from `finance_fundamental.nyse_factors`
  - therefore the practical minimum collection path is:
    - `Daily Market Update` or equivalent OHLCV collection for price history
    - `Weekly Fundamental Refresh` for `nyse_fundamentals` and `nyse_factors`
  - confirmed that `Extended Statement Refresh` is not required for the current public quality strategy, because the runtime wrapper does not read the detailed statement ledger directly
- Durable output:
  - `app/web/runtime/backtest.py`
  - `finance/sample.py`
  - `app/web/streamlit_app.py`

### 2026-03-24 - Surface Quality Snapshot data requirements directly in the UI
- Request topic:
  - continue the next Phase 4 step after clarifying the required collection path for the quality strategy
- Interpreted goal:
  - reduce user confusion by making the collection prerequisites visible where the strategy is actually run
- Result:
  - added in-form guidance to the `Quality Snapshot` UI explaining that the current public path depends on:
    - price history from `Daily Market Update` / OHLCV collection
    - factor data from `Weekly Fundamental Refresh`
  - clarified in the UI that:
    - the public mode is `broad_research`
    - the strategy is stock-oriented
    - `Extended Statement Refresh` is not a first-pass requirement
- Durable output:
  - `app/web/pages/backtest.py`
  - `.note/finance/phase4/PHASE4_QUALITY_UI_INPUT_DRAFT.md`
  - `.note/finance/phase4/PHASE4_FIFTH_STRATEGY_QUALITY_ADDITION.md`

### 2026-03-24 - Investigate flat early Quality Snapshot results and improve Weekly Fundamental Refresh progress visibility
- Request topic:
  - verify why `Quality Snapshot` appears flat before 2022 for `AAPL/MSFT/GOOG`
  - add Daily-like progress visibility for long `Weekly Fundamental Refresh` runs
- Interpreted goal:
  - separate true strategy/data coverage behavior from UI bugs, and reduce uncertainty during long summary-factor refresh jobs
- Result:
  - confirmed the flat 2016~2021 equity segment is expected under the current data state:
    - the strategy itself is not broken
    - the current annual factor coverage in `nyse_factors` for the tested symbols begins only around 2021/2022
    - therefore `Quality Snapshot` stays in cash until the first usable factor snapshot date
  - verified concrete examples:
    - `load_factor_snapshot(..., as_of_date='2021-01-29', freq='annual')` returned no rows
    - `load_factor_snapshot(..., as_of_date='2022-01-31', freq='annual')` returned only `GOOG`
    - `load_factor_snapshot(..., as_of_date='2023-01-31', freq='annual')` returned `AAPL`, `GOOG`, `MSFT`
  - added a runtime warning so the UI now explains when the first usable factor snapshot is materially later than the requested start date
  - added stage-based progress support for `Weekly Fundamental Refresh`:
    - `fundamentals`
    - `factors`
    so long NYSE-stock runs now show stage progress rather than only a blocking spinner
- Durable output:
  - `app/web/runtime/backtest.py`
  - `app/web/pages/backtest.py`
  - `app/jobs/ingestion_jobs.py`
  - `app/web/streamlit_app.py`

### 2026-03-24 - Measure actual historical depth of Weekly Fundamental Refresh
- Request topic:
  - run `Weekly Fundamental Refresh` directly and verify how far back the current summary/factor pipeline can collect data
- Interpreted goal:
  - determine whether the missing pre-2022 quality backtest coverage is a pipeline bug or a source-depth limitation
- Result:
  - executed `run_weekly_fundamental_refresh(['AAPL','MSFT','GOOG'], freq='annual')`
    - completed successfully in about 6.1s
    - wrote 12 fundamentals rows and 12 factor rows
  - executed `run_weekly_fundamental_refresh(['AAPL','MSFT','GOOG'], freq='quarterly')`
    - completed successfully in about 4.6s
    - wrote 17 fundamentals rows and 17 factor rows
  - post-run DB inspection confirmed shallow historical depth:
    - annual:
      - `GOOG` begins at `2021-12-31`
      - `MSFT` begins at `2022-06-30`
      - `AAPL` begins at `2022-09-30`
    - quarterly:
      - `GOOG`, `MSFT` begin at `2024-06-30`
      - `AAPL` begins at `2024-12-31`
  - conclusion:
    - the current yfinance-backed `Weekly Fundamental Refresh` path is working, but its available historical depth is too short for a meaningful 2016-start quality backtest
    - this is a source-depth / current-pipeline limitation, not a basic job failure
- Durable output:
  - `app/jobs/ingestion_jobs.py`
  - `finance/data/fundamentals.py`
  - `finance/data/factors.py`

### 2026-03-24 - Present options for enabling longer-history quality backtests
- Request topic:
  - provide concrete next-step options after confirming that the current public quality path does not reach back to 2016
- Interpreted goal:
  - choose a practical product/engineering direction for longer-history factor/fundamental backtests
- Result:
  - narrowed the realistic options to three paths:
    1. keep the current broad-research quality path and limit the visible date range to available factor history
    2. rebuild quality factors from the detailed statement ledger for longer and stricter history
    3. add a separate deeper-history provider/raw summary path before recomputing factors
  - recommended option `2` as the long-term architecture fit because it aligns with the existing statement-ledger direction and improves both history depth and timing semantics

### 2026-03-24 - Validate whether option 2 can start immediately with the current statement ledger
- Request topic:
  - proceed with option `2`, i.e. move toward a statement-driven quality path
- Interpreted goal:
  - verify whether the existing `nyse_financial_statement_values` coverage is already sufficient to start rebuilding longer-history quality factors
- Result:
  - checked current local statement ledger coverage for `AAPL/MSFT/GOOG`
  - confirmed that the current statement ledger is also still too shallow for the intended 2016-start quality backtest:
    - `AAPL annual` begins around `2024-09-28`
    - `MSFT annual` begins around `2025-05-01`
    - `GOOG` currently has no local statement rows in the checked ledger result
  - conclusion:
    - option `2` remains the right direction architecturally
    - but the immediate next task is not more strategy code
    - the immediate next task is securing deeper statement history / backfill coverage first
- Durable output:
  - `.note/finance/phase4/PHASE4_STATEMENT_DRIVEN_QUALITY_BLOCKER_AND_NEXT_STEPS.md`
  - `.note/finance/phase4/PHASE4_FACTOR_FUNDAMENTAL_ENTRY_TODO.md`

### 2026-03-24 - Execute the agreed feasibility-first, then targeted-backfill sequence for statement-driven quality
- Request topic:
  - do option `2` first (small feasibility test), then option `1` (statement ledger backfill)
- Interpreted goal:
  - validate the statement-based path with low risk first, then immediately turn the successful test into useful coverage for the sample quality universe
- Result:
  - ran `Extended Statement Refresh` for `AAPL/MSFT/GOOG` with:
    - `annual`, `periods=12`
    - `quarterly`, `periods=12`
  - both runs completed successfully
  - the same runs functioned as a targeted sample-universe statement backfill
  - coverage improved materially:
    - `AAPL annual`: starts around `2021-09-25`
    - `GOOG annual`: starts around `2021-12-31`
    - `MSFT annual`: starts around `2023-12-31`
  - strict annual snapshot checks still show that usable statement-driven quality coverage does not yet reach back to `2016`
  - conclusion:
    - statement-driven quality is a viable path
    - but it still needs deeper history before it can replace the current public quality strategy for long backtests
- Durable output:
  - `.note/finance/phase4/PHASE4_STATEMENT_LEDGER_FEASIBILITY_AND_TARGETED_BACKFILL.md`
  - `.note/finance/phase4/PHASE4_FACTOR_FUNDAMENTAL_ENTRY_TODO.md`

### 2026-03-24 - Build a sample-universe statement-driven quality prototype after feasibility and targeted backfill
- Request topic:
  - proceed with the next recommended step: create a sample-universe statement-driven quality prototype before deciding on wider public exposure
- Interpreted goal:
  - prove that strict statement snapshots can drive a real quality backtest path, using the existing targeted sample universe, without prematurely exposing the path in the public UI
- Result:
  - implemented reusable preprocessing/mapping helpers:
    - `build_fundamentals_from_statement_snapshot(...)` in `finance/data/fundamentals.py`
    - `build_quality_factor_snapshot_from_statement_snapshot(...)` in `finance/data/factors.py`
  - implemented a DB-backed sample entrypoint:
    - `get_statement_quality_snapshot_from_db(...)` in `finance/sample.py`
  - implemented a runtime wrapper:
    - `run_statement_quality_prototype_backtest_from_db(...)` in `app/web/runtime/backtest.py`
  - the prototype uses:
    - strict annual statement snapshots from `load_statement_snapshot_strict(...)`
    - derived quality columns:
      - `roe`
      - `gross_margin`
      - `operating_margin`
      - `debt_ratio`
    - the existing `quality_snapshot_equal_weight(...)` strategy simulation
  - validation run:
    - tickers: `AAPL/MSFT/GOOG`
    - period: `2023-01-01 ~ 2026-03-20`
    - result:
      - first active date `2023-01-31`
      - `End Balance = 23645.4`
      - `CAGR = 0.316218`
      - `Sharpe Ratio = 1.587924`
  - conclusion:
    - the statement-driven quality path is now proven at prototype level for the targeted sample universe
    - but it remains inappropriate to expose as a long-history public strategy until statement coverage becomes deeper and more even across the universe
- Durable output:
  - `.note/finance/phase4/PHASE4_STATEMENT_DRIVEN_QUALITY_PROTOTYPE_FIRST_PASS.md`
  - `.note/finance/phase4/PHASE4_FACTOR_FUNDAMENTAL_ENTRY_TODO.md`

### 2026-03-24 - Move statement-driven quality preprocessing into reusable data-layer mapping
- Request topic:
  - after confirming the overall direction, continue with the next work needed for a real statement-ledger-based path
- Interpreted goal:
  - stop treating the statement-driven quality prototype as a one-off transform and create a reusable mapping path that can later support rebuilt fundamentals/factors
- Result:
  - added `build_fundamentals_from_statement_snapshot(...)` to `finance/data/fundamentals.py`
  - added:
    - `calculate_quality_factors_from_fundamentals(...)`
    - `build_quality_factor_snapshot_from_statement_snapshot(...)`
    to `finance/data/factors.py`
  - refactored the statement-driven quality sample to use:
    - strict statement snapshot
    - normalized fundamentals mapping
    - quality factor snapshot mapping
    - existing quality strategy
  - conclusion:
    - the project now has a reusable `statement -> fundamentals -> factors` code path
    - this still does not mean public replacement of the current broad-research quality path
    - but it is the right base for any future statement-driven rebuild/backfill
- Durable output:
  - `.note/finance/phase4/PHASE4_STATEMENT_TO_FUNDAMENTALS_FACTORS_MAPPING_FIRST_PASS.md`
  - `.note/finance/phase4/PHASE4_FACTOR_FUNDAMENTAL_ENTRY_TODO.md`

### 2026-03-24 - Add a strict statement quality loader boundary on top of the new mapping
- Request topic:
  - continue the same workstream so the statement-driven path has a proper loader/read boundary rather than only sample-time builder composition
- Interpreted goal:
  - make the prototype path easier to reuse and keep the architecture consistent with the rest of the DB-backed runtime flow
- Result:
  - added `load_statement_quality_snapshot_strict(...)` to `finance/loaders/factors.py`
  - exported the loader from `finance/loaders/__init__.py`
  - refactored `get_statement_quality_snapshot_from_db(...)` to consume the loader
  - validated the loader directly for `AAPL/MSFT/GOOG` at `2025-01-31`
  - revalidated the sample-universe prototype end-to-end with unchanged final balance
- Durable output:
  - `.note/finance/phase4/PHASE4_STATEMENT_QUALITY_LOADER_FIRST_PASS.md`

### 2026-03-24 - Start the statement-driven fundamentals/factors backfill planning step
- Request topic:
  - proceed with the next recommended step: statement-driven fundamentals/factors backfill preparation
- Interpreted goal:
  - define how this backfill should begin without accidentally overwriting the current broad-research public tables
- Result:
  - documented the key structural constraint:
    - current `nyse_fundamentals` / `nyse_factors` unique keys do not allow broad and statement-driven rows to coexist for the same `symbol/freq/period_end`
  - narrowed the realistic storage choices to:
    - overwrite current tables
    - shadow tables
    - same-table multi-mode schema expansion
  - recommended the shadow-table path as the safest first rollout
  - added `load_statement_coverage_summary(...)` so statement usable history can be audited before any write path is chosen
- Durable output:
  - `.note/finance/phase4/PHASE4_STATEMENT_DRIVEN_BACKFILL_PLAN_FIRST_PASS.md`

### 2026-03-24 - Open the statement-driven shadow-table backfill path
- Request topic:
  - proceed with the recommended shadow-table direction rather than overwriting the current broad-research public tables
- Interpreted goal:
  - implement a first safe write/read path for statement-driven fundamentals/factors so sample-universe history can be backfilled and compared without changing public UI behavior
- Result:
  - added schema-backed shadow tables:
    - `nyse_fundamentals_statement`
    - `nyse_factors_statement`
  - added first-pass write paths:
    - `upsert_statement_fundamentals_shadow(...)`
    - `upsert_statement_factors_shadow(...)`
  - added matching loader read paths:
    - `load_statement_fundamentals_shadow(...)`
    - `load_statement_factors_shadow(...)`
  - validated annual sample-universe write/read on `AAPL/MSFT/GOOG`
  - confirmed current shadow path is useful for accounting-quality history, but valuation fields remain incomplete because statement-driven `shares_outstanding` is still sparse
- Durable output:
  - `.note/finance/phase4/PHASE4_STATEMENT_SHADOW_TABLES_FIRST_PASS.md`

### 2026-03-24 - Add first-pass shares fallback to the statement-driven shadow path
- Request topic:
  - continue with the next recommended step: improve `shares_outstanding` so shadow factor history can populate valuation fields
- Interpreted goal:
  - keep the new statement-driven shadow path useful not only for quality/accounting ratios, but also for `market_cap` / `per` / `pbr` where reasonable
- Result:
  - confirmed the current local statement ledger for `AAPL/MSFT/GOOG` does not contain the expected direct shares concepts
  - added a conservative fallback from broad `nyse_fundamentals`
    using nearest `period_end`, same `symbol/freq`, and `15-day` tolerance
  - re-ran sample-universe annual shadow backfill and verified:
    - `shares_outstanding` now populates on `10 / 12` rows
    - `market_cap` now populates on `10 / 12` rows
    - valuation fields such as `per` / `pbr` are available for most rows
  - clarified the new meaning:
    - accounting quality fields remain statement-driven
    - valuation fields are currently `statement + broad shares fallback` hybrid rows
- Durable output:
  - `.note/finance/phase4/PHASE4_STATEMENT_SHADOW_SHARES_ENHANCEMENT_FIRST_PASS.md`

### 2026-03-24 - Verify user-run Extended Statement Refresh and recheck the shadow path
- Request topic:
  - verify the user's new `Extended Statement Refresh` run and continue the in-progress statement-driven workstream
- Interpreted goal:
  - confirm how much annual/quarterly statement coverage actually improved, then rebuild the shadow fundamentals/factors and see which strict statement path is the more usable candidate
- Result:
  - verified strict annual coverage for `AAPL/MSFT/GOOG` is still more useful than quarterly
  - verified quarterly strict coverage now exists, but mostly begins in `2024`
  - rebuilt both annual and quarterly shadow tables successfully
  - revalidated statement-driven quality prototype:
    - annual path:
      - `first_active = 2023-01-31`
      - `End Balance = 23645.4`
    - quarterly path:
      - `first_active = 2024-10-31`
      - `End Balance = 13952.3`
  - current conclusion:
    - annual strict statement path remains the better sample-universe candidate
    - quarterly path is working but still too shallow to be the next public candidate
- Durable output:
  - `.note/finance/phase4/PHASE4_EXTENDED_STATEMENT_REFRESH_VERIFICATION_AND_SHADOW_REBUILD.md`

### 2026-03-24 - Fix annual statement period limiting and reopen long-history strict quality on the sample universe
- Request topic:
  - continue the next recommended statement-driven work after the user refreshed annual/quarterly extended statements
- Interpreted goal:
  - identify why annual strict coverage was still too shallow and fix the actual collector behavior rather than treating it as a source-data limitation
- Result:
  - confirmed the source itself already had deeper annual reported periods for `AAPL/MSFT/GOOG`
  - found the real issue in `finance.data.financial_statements._iter_value_rows_from_source(...)`:
    - `periods=N` was being limited by raw row-level `period_end`
    - this let recent 10-K facts with quarter-end-like `period_end` values crowd out older true annual history
  - changed the limit semantics to use reported period identity:
    - `report_date` first
    - `period_end` fallback
  - added canonical refresh behavior in `upsert_financial_statements(...)` for the refreshed symbol/freq scope so old semantics rows do not linger
  - reran sample-universe annual refresh and verified annual strict coverage now reaches roughly `2011~2025`
  - rebuilt annual shadow fundamentals/factors and revalidated the statement-driven quality prototype:
    - `first_active = 2016-02-29`
    - long-history annual strict quality backtest is now actually usable on `AAPL/MSFT/GOOG`
- Durable output:
  - `.note/finance/phase4/PHASE4_ANNUAL_STATEMENT_PERIOD_LIMIT_FIX_AND_COVERAGE_EXPANSION.md`

### 2026-03-24 - Promote strict annual statement quality into a public UI candidate
- Request topic:
  - proceed with the recommended next step after strict annual sample-universe coverage became usable again
- Interpreted goal:
  - stop keeping the strict annual statement-driven quality path as backend-only and expose it in the Backtest product surface without breaking the current broad quality path
- Result:
  - added `run_quality_snapshot_strict_annual_backtest_from_db(...)`
  - kept existing broad `Quality Snapshot` unchanged
  - exposed a separate sixth strategy in the UI:
    - `Quality Snapshot (Strict Annual)`
  - connected the new strategy to:
    - single-strategy execution
    - compare mode
    - persistent history
    - form reload / rerun
  - validated wrapper output on `AAPL/MSFT/GOOG` over `2016-01-01 ~ 2026-03-20`
  - current product meaning:
    - broad quality = current research-oriented public path
    - strict annual quality = statement-driven public candidate path
- Durable output:
  - `.note/finance/phase4/PHASE4_STRICT_ANNUAL_QUALITY_PUBLIC_CANDIDATE_FIRST_PASS.md`

### 2026-03-24 - Prefer annual statement coverage expansion before treating strict annual quality as trustworthy
- Request topic:
  - the user preferred annual statement coverage work first because `Quality Snapshot (Strict Annual)` still did not yet feel like a trustworthy finished strategy
- Interpreted goal:
  - stop polishing the strict annual strategy in isolation and instead make wider annual statement coverage operationally feasible so the strategy can later be judged on broader data
- Result:
  - confirmed `Profile Filtered Stocks` currently resolves to about `5783` symbols, so wider annual coverage is a genuinely heavy run
  - added batch-progress emission to `upsert_financial_statements(...)`
  - extended the progress path through:
    - `run_collect_financial_statements(...)`
    - `run_extended_statement_refresh(...)`
    - Streamlit live progress rendering for large runs
  - manual `Financial Statement Ingestion` now benefits from the same progress path
  - sample validation confirmed the new callback contract works and result details now expose `upserted_filings`
- Durable output:
  - `.note/finance/phase4/PHASE4_ANNUAL_STATEMENT_COVERAGE_OPERATOR_SUPPORT_FIRST_PASS.md`

### 2026-03-24 - Stage 1 wider annual coverage run shows strict annual path can scale, but foreign issuers distort naive top-market-cap rollout
- Request topic:
  - proceed with a staged annual coverage run instead of jumping directly to the full `Profile Filtered Stocks` universe
- Interpreted goal:
  - confirm that annual strict statement coverage can expand beyond `AAPL/MSFT/GOOG` while keeping operational risk reasonable
- Result:
  - chose stage 1 as `Profile Filtered Stocks` top `100` by `market_cap`
  - annual statement refresh completed successfully:
    - `rows_written = 188709`
    - `upserted_labels = 85164`
    - `upserted_filings = 8575`
    - `failed_symbols = 0`
  - annual shadow fundamentals/factors rebuild also completed:
    - `2376` rows each
  - strict annual coverage was confirmed on `80 / 100` symbols
  - `68` symbols already have `12+` annual accessions
  - the `20` missing symbols are mostly foreign issuers (`TSM`, `AZN`, `ASML`, `BABA`, `TM`, `HSBC`, etc.)
- Durable output:
  - `.note/finance/phase4/PHASE4_ANNUAL_STATEMENT_COVERAGE_STAGE1_TOP100_RUN.md`

### 2026-03-24 - Stage 2 US top-300 annual coverage run shows strict annual path is viable beyond the sample universe
- Request topic:
  - continue the next staged annual coverage expansion after stage 1
- Interpreted goal:
  - test whether refining the universe toward US / EDGAR-friendly stocks materially improves strict annual coverage
- Result:
  - selected stage 2 as:
    - `Profile Filtered Stocks`
    - `country = United States`
    - `market_cap DESC`
    - top `300`
  - annual statement refresh completed successfully:
    - `rows_written = 701189`
    - `upserted_labels = 316761`
    - `upserted_filings = 30170`
    - `failed_symbols = 0`
  - annual shadow fundamentals/factors rebuild completed:
    - `9385` rows each
  - strict annual coverage was confirmed on `297 / 300` symbols
  - only `3` symbols were still missing:
    - `MRSH`
    - `AU`
    - `CUK`
  - this materially increases confidence that the strict annual path is not just a sample-universe artifact
- Durable output:
  - `.note/finance/phase4/PHASE4_ANNUAL_STATEMENT_COVERAGE_STAGE2_US_TOP300_RUN.md`

### 2026-03-25 - Redefine strict annual quality as a verified wider-universe public candidate
- Request topic:
  - continue with the recommended next step after stage 2 annual coverage succeeded
- Interpreted goal:
  - stop presenting `Quality Snapshot (Strict Annual)` as only a sample-universe candidate and align its public role/default universe with the wider annual coverage evidence
- Result:
  - broad quality presets and strict annual presets were separated in the Backtest UI
  - broad `Quality Snapshot` stayed on:
    - `Big Tech Quality Trial`
  - strict annual quality now exposes:
    - `US Statement Coverage 300`
    - `US Statement Coverage 100`
    - `Big Tech Strict Trial`
  - single-strategy strict annual default was moved to:
    - `US Statement Coverage 300`
  - compare-mode strict annual default was set to:
    - `US Statement Coverage 100`
    - this keeps compare runs lighter while preserving the wider-universe product meaning
- Durable output:
  - `.note/finance/phase4/PHASE4_STRICT_ANNUAL_QUALITY_PUBLIC_ROLE_AND_DEFAULT_UNIVERSE.md`
