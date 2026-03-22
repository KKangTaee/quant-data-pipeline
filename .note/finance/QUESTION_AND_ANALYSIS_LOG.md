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
