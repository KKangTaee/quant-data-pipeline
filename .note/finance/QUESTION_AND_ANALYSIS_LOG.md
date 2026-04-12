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

### 2026-04-05 - ETF AUM/spread operability policy placement
- Request topic:
  - continue Phase 12 hardening with the next practical real-money step
- Interpreted goal:
  - strengthen ETF strategy operability review without forcing an inappropriate AUM/spread model onto strict annual stock strategies
- Result:
  - decided that `AUM` and current `bid/ask spread` belong naturally to ETF strategy current-operability review
  - kept strict annual stock-side work on price/history/liquidity proxy/benchmark/guardrail policy
  - implemented ETF-only current-snapshot operability policy using `nyse_asset_profile`
  - explicitly documented the current boundary:
    - current snapshot overlay
    - not point-in-time ETF operability history
    - not an actual trade-blocking rule yet
- Durable output:
  - `.note/finance/phase12/PHASE12_ETF_AUM_AND_SPREAD_POLICY_FIRST_PASS.md`

### 2026-04-05 - Phase 12 closeout judgment
- Request topic:
  - finish Phase 12 all the way through official closeout
- Interpreted goal:
  - decide whether the remaining items are blockers or should move to next-phase backlog, and leave durable closeout/handoff documents
- Result:
  - judged that Phase 12 core goal was already achieved:
    - strategy promotion contract fixed
    - ETF strategy first-pass hardening completed
    - strict annual family promotion surface completed
    - quarterly family still clearly held as research-only
  - decided that remaining ETF second-pass guardrail / PIT operability items are valuable but not closeout blockers
  - closed Phase 12 as `practical completion` and prepared next-phase direction around deployment-readiness / probation / monitoring
- Durable output:
  - `.note/finance/phase12/PHASE12_COMPLETION_SUMMARY.md`
  - `.note/finance/phase12/PHASE12_NEXT_PHASE_PREPARATION.md`

### 2026-04-05 - Streamlit page list and helper-module collision
- Request topic:
  - fix the import/navigation issue seen before manual Phase 12 testing and improve the top-left page navigation
- Interpreted goal:
  - stop helper modules from appearing as Streamlit pages and make the app navigation align with actual operator workflows
- Result:
  - identified the core structural issue as helper code living under `app/web/pages/`, which let Streamlit auto-discovery treat non-page modules as pages
  - moved `backtest_strategy_catalog` out of the `pages/` directory
  - switched the main app to explicit `st.navigation(..., position=\"top\")`
  - defined the top-level workspace pages as:
    - `Overview`
    - `Ingestion`
    - `Backtest`
    - `Ops Review`
    - `Guides`
- Durable output:
  - `app/web/streamlit_app.py`
  - `app/web/backtest_strategy_catalog.py`

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

### 2026-03-25 - Fix quality preset preview not refreshing until submit
- Request topic:
  - when changing the preset in the Backtest quality strategy form, the ticker preview did not refresh automatically
- Interpreted goal:
  - remove the Streamlit form UX trap so preset changes immediately update the previewed tickers
- Result:
  - confirmed the issue came from `Preset` widgets being inside `st.form(...)`
  - moved the universe/preset selection block outside the submit form for:
    - `Quality Snapshot`
    - `Quality Snapshot (Strict Annual)`
  - added compact ticker preview rendering with ticker count
- Durable output:
  - ticker preview now updates immediately when the preset changes

### 2026-03-25 - Why `Quality Snapshot (Strict Annual)` is slow even on coverage 100
- Request topic:
  - explain what the strict annual quality backtest is doing and why runtime feels very slow for `US Statement Coverage 100`
- Interpreted goal:
  - identify the actual expensive runtime path before deciding whether to optimize or keep the current structure
- Result:
  - the dominant cost is not price loading but repeated strict statement snapshot reconstruction
  - current execution path:
    - load DB-backed monthly price dates
    - for each rebalance date, call `load_statement_quality_snapshot_strict(...)`
    - inside that path, load strict statement values from `nyse_financial_statement_values`
    - filter by `available_at <= as_of_date`
    - rebuild statement-driven fundamentals
    - rebuild quality factors
  - for `2016-01-01 ~ 2026-03-20`, month-end cadence creates about `123` rebalance dates
  - for the current US top-100 annual universe:
    - `nyse_financial_statement_values` annual rows are about `236,627`
  - a single strict snapshot build for the top-100 universe currently takes about:
    - `2016-01-31`: `3.88s`
    - `2020-12-31`: `4.08s`
    - `2026-03-20`: `4.19s`
  - so a full backtest is effectively repeating a multi-second snapshot/factor rebuild roughly `123` times, which explains the multi-minute runtime
  - preflight also adds one more strict snapshot call before the main run starts
- Durable output:
  - current strict annual public candidate is accurate enough for validation, but runtime is dominated by repeated on-the-fly reconstruction from statement values rather than precomputed statement shadow factors

### 2026-03-25 - Strict annual fast path can match prototype if annual shadow history uses true annual periods and first-available timing
- Request topic:
  - continue the remaining strict annual roadmap end-to-end, including speed optimization and follow-on strategy work
- Interpreted goal:
  - make the strict annual public path fast enough to use, but not at the cost of changing the strategy meaning
- Result:
  - public strict annual runtime was switched to a shadow-factor-based fast path
  - initial output diverged materially from the prototype because annual shadow history still had two semantic problems:
    - quarter-like comparative rows were mixed into annual history
    - each `period_end` row used a too-late availability point
  - fixing annual shadow history required:
    - anchoring annual history to reported annual periods
    - rebuilding each `period_end` from a coherent first-available filing snapshot
  - after that fix, sample-universe parity was confirmed:
    - optimized strict public path:
      - about `0.331s`
      - `End Balance = 93934.6`
    - prototype rebuild path:
      - about `17.09s`
      - `End Balance = 93934.6`
  - wider-universe strict annual runtime is now practical:
    - quality strict top-100:
      - about `3.381s`
    - value strict top-100:
      - about `3.399s`
- Durable output:
  - the correct public strict annual path is:
    - statement ledger -> annual shadow fundamentals/factors with first-available timing
    - fast as-of snapshot from `nyse_factors_statement`
    - strategy runtime

### 2026-03-25 - Strict annual fast path is applied, but top-100 still has a smaller remaining runtime cost
- Request topic:
  - verify whether strict annual optimization is actually applied and explain why `US Statement Coverage 100` still feels somewhat slow
- Interpreted goal:
  - confirm the current public runtime path, quantify the speedup, and clarify what parts of roadmap items 4/5/6 changed in code
- Result:
  - the public `Quality Snapshot (Strict Annual)` path is definitely using the optimized shadow-factor runtime:
    - `app/web/runtime/backtest.py` dispatches `run_quality_snapshot_strict_annual_backtest_from_db(...)`
      to `_run_statement_quality_bundle(..., snapshot_source=\"shadow_factors\")`
    - the loader path uses `finance/loaders/factors.py::load_statement_factor_snapshot_shadow(...)`
  - current benchmark:
    - `US Statement Coverage 100`, `2016-01-01 ~ 2026-03-20`, `month_end`, `top_n=10`
    - about `3.268s`
  - sample-universe parity benchmark:
    - optimized strict path:
      - about `0.346s`
      - `End Balance = 93934.6`
    - old prototype rebuild path:
      - about `16.023s`
      - `End Balance = 93934.6`
  - so the large optimization is already applied; the remaining top-100 runtime is mostly from:
    - loading wider price/factor history
    - building `snapshot_by_date` for every rebalance date in Python from shadow factor history
    - strategy simulation/report bundle work
  - roadmap item mapping:
    - `4. strict annual 전략 검증/해석 강화`
      - `app/web/pages/backtest.py`
      - snapshot strategies now show `Selection History`
    - `5. annual coverage 운영화`
      - `app/web/streamlit_app.py`
      - ingestion presets now include `US Statement Coverage 100/300`
    - `6. Value strict 전략 추가`
      - `app/web/runtime/backtest.py`
      - `app/web/pages/backtest.py`
      - `app/web/runtime/history.py`
      - `Value Snapshot (Strict Annual)` is wired into single / compare / history
- Durable output:
  - strict annual optimization is already live and substantial; any next speed work should target the remaining `snapshot_by_date` construction cost rather than raw statement rebuild replacement

### 2026-03-25 - UI now shows measured backtest elapsed time for single-strategy runs
- Request topic:
  - add a clear elapsed-time display because the user observed `Quality Snapshot (Strict Annual)` runs that felt much slower than the benchmark
- Interpreted goal:
  - make the actual execution time visible directly in the Backtest UI instead of relying on perceived wait time
- Result:
  - single-strategy backtest execution now measures elapsed seconds around the actual runtime wrapper call
  - the measured value is written into `bundle.meta.ui_elapsed_seconds`
  - the value is shown in:
    - completion success banner
    - `Latest Backtest Run -> Meta -> Execution Context`
    - persistent backtest history drilldown input view
- Durable output:
  - strict annual runtime disagreements can now be checked against an explicit UI-measured elapsed time before diagnosing further speed issues

### 2026-03-25 - `US Statement Coverage 300` looks sparse mostly because price-date intersection collapses to 3 rows
- Request topic:
  - verify whether `Quality Snapshot (Strict Annual)` with `US Statement Coverage 300` looks sparse because 2016 data is missing
- Interpreted goal:
  - distinguish between statement coverage problems and runtime input-shaping problems
- Result:
  - strict annual statement shadow coverage itself is not the main bottleneck:
    - `2016-01-31` as-of snapshot:
      - `252` covered symbols
      - `58` fully usable symbols across the default quality factors
    - by `2025-12-31`:
      - `295` covered symbols
      - `78` fully usable symbols
  - the larger issue is the current price input path in `finance/sample.py`:
    - it still uses `align_dates()` across all requested tickers
    - for `US Statement Coverage 300`, this collapses the common monthly date set to only `3` rows
    - common aligned range becomes:
      - `2025-12-31 ~ 2026-02-27`
  - corresponding backtest behavior:
    - `Quality Snapshot (Strict Annual)` with `US Statement Coverage 300`
    - `2016-01-01 ~ 2026-03-20`
    - first active date becomes `2025-12-31`
    - only `3` active rebalance rows remain
- Durable output:
  - the current sparse behavior for `US Statement Coverage 300` is driven more by full-universe date intersection than by annual statement coverage alone
  - a real fix would require changing the strategy input path away from full-date intersection for large stock universes

### 2026-03-25 - Strict annual large-universe sparse issue is resolved by union-calendar price alignment
- Request topic:
  - proceed with fixing the strict annual large-universe input path after confirming the full-intersection problem
- Interpreted goal:
  - make `US Statement Coverage 300` usable as an actual long-history strategy instead of a sparse validation artifact
- Result:
  - snapshot strategies now build price inputs with union-calendar alignment instead of full-date intersection
  - rebalance ranking excludes symbols whose current `Close` is unavailable on that date
  - post-fix validation:
    - `Quality Snapshot (Strict Annual)` / `US Statement Coverage 300`
      - `2016-01-29 ~ 2026-03-20`
      - `124` rows
      - `first_active_date = 2016-01-29`
      - runtime about `9.086s`
    - `Quality Snapshot (Strict Annual)` / `US Statement Coverage 100`
      - `first_active_date = 2016-01-29`
      - runtime about `3.320s`
    - `Value Snapshot (Strict Annual)` / `US Statement Coverage 300`
      - `first_active_date = 2021-08-31`
      - `57` active rows
      - runtime about `9.165s`
  - sample-universe strict parity remained intact:
    - optimized fast path about `0.322s`
    - prototype rebuild path about `16.793s`
    - both `End Balance = 93934.6`
- Durable output:
  - strict annual large-universe 전략의 핵심 blocker였던 sparse input path는 해결되었고,
    다음 판단 포인트는 broad/strict 역할 설명 강화와 `Quality`/`Value` strict family 비교 쪽으로 이동했다

### 2026-03-25 - strict annual family comparison now clearly favors quality as the primary public candidate
- Request topic:
  - continue with broad vs strict explanation, strict family comparison, and Phase 4 closeout preparation
- Interpreted goal:
  - finish the current strict annual family workstream cleanly before discussing the next major phase
- Result:
  - quality/value snapshot forms now expose a `Broad vs Strict Guide` in the Backtest UI
  - strict family comparison on the current public path shows:
    - `Quality Snapshot (Strict Annual)` / coverage 100:
      - `3.321s`
      - `End Balance = 79295.2`
    - `Quality Snapshot (Strict Annual)` / coverage 300:
      - `9.264s`
      - `End Balance = 73778.4`
    - `Value Snapshot (Strict Annual)` / coverage 100:
      - `3.197s`
      - `End Balance = 20228.2`
    - `Value Snapshot (Strict Annual)` / coverage 300:
      - `9.080s`
      - `End Balance = 20931.1`
  - current conclusion:
    - `Quality Snapshot (Strict Annual)` is the primary strict annual public candidate
    - `Value Snapshot (Strict Annual)` is the secondary strict annual family
  - Phase 4 closeout summary and next-phase preparation notes are now ready, but the next major phase is not formally opened yet
- Durable output:
  - Phase 4 implementation scope is effectively complete
  - the next major decision should be a user-confirmed phase opening rather than more ad hoc Phase 4 expansion

### 2026-03-25 - quality factor expansion should be coverage-first before widening the strict annual universe
- Request topic:
  - plan the next work for
    - quality factor expansion
    - coverage `300 -> wider universe -> NYSE`
  - and confirm whether late-listed symbols are already handled safely
- Interpreted goal:
  - avoid widening strict annual coverage with a weak default factor set
  - verify that listing-date differences do not break the snapshot strategy path
- Result:
  - latest strict annual shadow snapshot coverage on `US Statement Coverage 300` shows:
    - `roe`: `90.91%`
    - `operating_margin`: `75.08%`
    - `debt_ratio`: `61.28%`
    - `gross_margin`: `42.42%`
  - stronger coverage candidates are:
    - `roa`
    - `net_margin`
    - `asset_turnover`
    - `current_ratio`
  - current recommendation is to move to a coverage-first factor set before attempting wider-universe or NYSE-wide strict annual runs
  - late-listed symbol handling is already safe in the current snapshot path:
    - price inputs use union calendar
    - only symbols with current `Close` on the rebalance date are eligible
    - if no symbols are eligible, the strategy stays in cash
- Durable output:
  - strict annual quality expansion should prioritize factor coverage quality before universe size
  - listing-date differences are already handled gracefully by the current snapshot strategy path

### 2026-03-25 - strict annual quality now uses a coverage-first default factor set
- Request topic:
  - proceed with the recommended implementation order:
    - apply the coverage-first strict annual quality factor set
    - re-check coverage `100 / 300`
- Interpreted goal:
  - stabilize the strict annual quality public default before widening the universe further
- Result:
  - strict annual quality default factors were changed to:
    - `roe`
    - `roa`
    - `net_margin`
    - `asset_turnover`
    - `current_ratio`
  - current public default validation:
    - `US Statement Coverage 100`
      - `3.319s`
      - first active date: `2016-01-29`
      - `End Balance = 107324.3`
    - `US Statement Coverage 300`
      - `9.359s`
      - first active date: `2016-01-29`
      - `End Balance = 366404.7`
- Durable output:
  - strict annual quality now has a coverage-first default factor set
  - this is the right baseline to use before discussing wider-universe or NYSE-wide strict annual expansion

### 2026-03-25 - final-month double rows in strict annual snapshot runs are currently driven by uneven latest daily price coverage
- Request topic:
  - explain why `Quality Snapshot (Strict Annual)` result tables can show both `2026-03-17` and `2026-03-20` in the final month
- Interpreted goal:
  - distinguish between a strategy/runtime issue and a stale or partial price-ingestion issue
- Result:
  - current DB `finance_price.nyse_price_history` confirms mixed latest dates inside the same preset universe:
    - `APH`, `CVNA`, `GWW`, `LLY`, `MPWR` currently stop at `2026-03-17`
    - `APP`, `KLAC`, `LRCX`, `NVDA`, `UI` currently extend to `2026-03-20`
  - because strict annual large-universe snapshot strategies now use union-calendar price alignment,
    the final incomplete month keeps both dates when different symbols have different last available trading rows
  - this is therefore mostly a price-data freshness / partial-ingestion issue, not a selection-logic bug
- Durable output:
  - rerunning the daily market update for stale symbols can make the duplicate final-month rows disappear if the lagging symbols catch up to the same last trading date
  - if mixed last dates remain after refresh, a future UX/data-shaping improvement would be to collapse the incomplete final month to one rebalance row

### 2026-03-25 - targeted daily price refresh resolved the duplicate final-month row issue in strict annual coverage 300
- Request topic:
  - proceed with the suspected stale-price fix and verify whether the final duplicated March rows disappear
- Interpreted goal:
  - confirm whether the issue is operational data freshness rather than a strict annual strategy bug
- Result:
  - first targeted refresh:
    - `APH`, `CVNA`, `GWW`, `LLY`, `MPWR`
    - `2026-03-01 ~ 2026-03-20`
    - success, `75` rows written
  - after broader verification, `US Statement Coverage 300` still had `28` symbols ending at `2026-03-17`
  - second targeted refresh:
    - the remaining `28` lagging symbols
    - `2026-03-18 ~ 2026-03-20`
    - success, `84` rows written
  - after refresh, no `US Statement Coverage 300` symbol remained below `2026-03-20`
  - strict annual quality rerun then collapsed the duplicate last month into a single final row:
    - final rows now end with `2026-03-20`
    - result row count became `123`
    - `End Balance = 192994.7`
    - `CAGR = 33.9064%`
- Durable output:
  - the duplicate final-month rows were confirmed to be caused by uneven latest price coverage inside the preset universe
  - targeted daily price refresh is an effective operational fix
  - strict annual wide-universe presets should be paired with price freshness checks or a final-month preflight

### 2026-03-25 - strict annual single-strategy UI now exposes a price freshness preflight
- Request topic:
  - add a preflight/freshness check so users can see large-universe stale-price issues before running strict annual strategies
- Interpreted goal:
  - surface the latest-date spread operational risk before execution rather than forcing users to infer it from result tables
- Result:
  - added a lightweight loader to aggregate per-symbol latest price dates
  - added a runtime helper that summarizes:
    - common latest date
    - newest latest date
    - spread days
    - stale symbol count
    - missing symbol count
  - added `Price Freshness Preflight` UI sections to both:
    - `Quality Snapshot (Strict Annual)`
    - `Value Snapshot (Strict Annual)`
  - strict annual runtime bundles now also keep this freshness summary in `meta`
- Durable output:
  - strict annual runs now have an explicit operational preflight for stale-price issues
  - this reduces ambiguity between strategy bugs and daily market update freshness problems

### 2026-03-25 - strict annual staged preset/operator path and strict multi-factor candidate were completed as the next post-preflight step
- Request topic:
  - after stale-price preflight, continue the staged strict-annual expansion / feasibility / public-default / interpretability / multi-factor / operatorization sequence end-to-end
- Interpreted goal:
  - turn strict annual from a single validated strategy into a more usable strategy family with clearer operator workflows and next-phase handoff
- Result:
  - strict annual managed presets were expanded to:
    - `US Statement Coverage 500`
    - `US Statement Coverage 1000`
    while keeping `US Statement Coverage 100/300` as the already validated lighter presets
  - current DB audit for wider staged presets showed:
    - `US Statement Coverage 500`: covered `396 / 500`, freshness spread `3d`
    - `US Statement Coverage 1000`: covered `396 / 1000`, freshness spread `49d`
  - therefore the official strict annual public defaults stay:
    - single strategy: `US Statement Coverage 300`
    - compare: `US Statement Coverage 100`
    and `500/1000` remain staged operator presets only
  - strict annual preflight second pass now exposes:
    - stale / missing symbol details
    - copyable `Daily Market Update` payload
    - refresh-symbol CSV block
  - strict annual interpretability was extended with selection-frequency view
  - a new strict multi-factor public candidate was added:
    - `Quality + Value Snapshot (Strict Annual)`
  - a repeatable operator helper was added:
    - `run_strict_annual_shadow_refresh(...)`
    - annual extended statement refresh + fundamentals shadow rebuild + factors shadow rebuild
- Durable output:
  - strict annual family now has a staged operator path beyond the public defaults, but current DB state does not justify widening the official preset beyond `300`
  - `Quality Snapshot (Strict Annual)` remains the primary strict annual public candidate
  - `Value Snapshot (Strict Annual)` remains a secondary strict family
  - `Quality + Value Snapshot (Strict Annual)` is now the first strict multi-factor public candidate
  - next major phase should naturally center on strategy-library/comparative-research work rather than more UI skeleton work

### 2026-03-26 - strict annual staged presets must degrade safely at import time
- Request topic:
  - investigate a Streamlit startup error caused by `QUALITY_STRICT_PRESETS["US Statement Coverage 500"]`
- Interpreted goal:
  - restore application startup and make staged strict-annual presets resilient when DB-backed managed-universe loading is incomplete
- Result:
  - the failure was not a strategy/runtime math issue; it happened during module import
  - `_load_managed_strict_annual_presets()` could legally omit `US Statement Coverage 500/1000`
    when asset-profile loading returned no symbols or failed
  - `app/web/streamlit_app.py` then indexed those missing keys while building `SYMBOL_PRESETS`, producing a `KeyError`
  - the fix was applied in two layers:
    - managed preset builder now always emits fallback values for `500/1000`
    - `streamlit_app.py` now uses safe `.get(...)`-style preset resolution through `_preset_csv(...)`
- Durable output:
  - staged strict-annual managed presets no longer crash app startup when DB-backed wide-universe presets are unavailable
  - current fallback behavior degrades `500/1000` to the best available strict annual preset instead of failing import

### 2026-03-26 - strict annual `Coverage 1000` sparse non-month-end rows are currently caused by fallback-to-300 plus union-calendar price handling
- Request topic:
  - investigate why `Quality Snapshot (Strict Annual)` with `Coverage 1000` can show result-table rows like `2026-02-03`, `2026-03-17` and blank selection rows instead of a clean month-end path
- Interpreted goal:
  - determine whether the issue comes from factor ranking, statement timing, or large-universe price-input construction
- Result:
  - later DB-connected validation corrected one earlier assumption:
    - `US Statement Coverage 1000` is a true top-1000 managed preset in the real runtime, not just a `300` fallback
  - the actual problem was the price-input shaping rule for large-universe snapshot strategies:
    - each symbol first kept its own last available row inside the period
    - those symbol-specific period dates were then union-merged
    - large universes could therefore retain multiple intramonth rebalance rows such as `2026-02-03`, `2026-02-27`, `2026-03-17`, `2026-03-20`
  - the fix was to add canonical period-date alignment:
    - build one canonical date per period across the universe
    - keep each symbol's last available same-period price
    - rewrite the row date to the canonical period date
  - after that fix, strict annual `Coverage 1000` verification showed canonical monthly tails only:
    - `2025-08-29`
    - `2025-09-30`
    - `2025-10-31`
    - `2025-11-28`
    - `2025-12-31`
    - `2026-01-30`
    - `2026-02-27`
    - `2026-03-20`
  - remaining large-universe risk is now mostly operator/data freshness:
    - current `Coverage 1000` preflight still warns that `9` symbols lag the requested end date, with a `49d` spread
- Durable output:
  - sparse non-month-end rows were primarily a large-universe calendar-shaping issue, not a quality-factor bug
  - `Coverage 1000` is now understood as:
    - a real DB-backed top-1000 preset
    - with canonical monthly result rows after the transform fix
    - but still dependent on price-freshness preflight for lagging symbols

### 2026-03-27 - After refreshing the remaining stale symbols, the next work should shift from operator cleanup to strategy-library/comparative research
- Request topic:
  - clarify what the planned next steps are after refreshing the remaining `9` lagging symbols in the strict annual `Coverage 1000` universe
- Interpreted goal:
  - distinguish immediate post-refresh validation from the next larger workstream, so the team knows whether to keep operating on coverage or move into research/product expansion
- Result:
  - immediate post-refresh follow-up should be:
    - rerun strict annual `Coverage 1000` preflight
    - confirm `spread_days = 0` or clearly reduced
    - rerun `Quality Snapshot (Strict Annual)` and verify the canonical monthly tail remains clean
    - decide whether `Coverage 1000` can move from staged preset to a stronger managed-universe candidate
  - after that, the recommended next major direction remains:
    - `Strategy Library And Comparative Research`
  - recommended sequence:
    - strict quality / strict value / strict quality+value comparative evaluation
    - strategy-family interpretability improvement
    - canonical public preset decision for strict annual family
    - then broader annual coverage operations only if the comparative work shows the wider universe is worth operationalizing
- Durable output:
  - refreshing the last `9` symbols is treated as operator cleanup, not the next major phase by itself
  - the next major step after cleanup is still strategy-library/comparative-research work, with coverage operations as the supporting track rather than the primary one

### 2026-03-27 - Phase 4 closeout should include `Coverage 1000` revalidation and `Value Snapshot (Strict Annual)` recovery before the next phase opens
- Request topic:
  - before closing Phase 4, finish three cleanup items:
    - refresh the remaining stale symbols
    - rerun strict annual preflight/backtest validation
    - decide the current position of `US Statement Coverage 1000`
  - then fix `Value Snapshot (Strict Annual)` so it no longer stays flat through `2016~2021`, expand its factor set, and validate it through `Coverage 1000`
- Interpreted goal:
  - close Phase 4 on a reliable strict-annual family rather than leaving `Coverage 1000` and strict value in a half-validated state
- Result:
  - targeted daily-price refresh reduced the strict-annual `Coverage 1000` stale set from `9` symbols to `4`
    - remaining lagging names:
      - `CADE`, `CMA`, `DAY`, `CFLT`
    - common latest remains `2026-01-30`
    - newest latest remains `2026-03-20`
    - spread remains `49d`
  - therefore `US Statement Coverage 1000` is now understood as:
    - a real DB-backed top-1000 managed preset
    - canonically month-shaped
    - usable for staged/operator research
    - but still not ready for public-default promotion
  - the flat `2016~2021` value-strict path was traced to delayed `shares_outstanding` availability inside statement shadow fundamentals
  - statement-driven shares fallback was widened to include historical weighted-average share-count concepts, then annual statement shadow fundamentals/factors were rebuilt for the top-1000 US universe
  - strict annual value defaults were refreshed to a broader value-yield set:
    - `book_to_market`
    - `earnings_yield`
    - `sales_yield`
    - `ocf_yield`
    - `operating_income_yield`
  - after the rebuild, `Value Snapshot (Strict Annual)` now activates from `2016-01-29` instead of waiting until `2021-08-31`
    - `US Statement Coverage 300`:
      - `End Balance = 85378.4`
      - `CAGR = 23.56%`
      - `Sharpe Ratio = 1.1341`
    - `US Statement Coverage 1000`:
      - `End Balance = 91733.7`
      - `CAGR = 24.43%`
      - `Sharpe Ratio = 1.0644`
- Durable output:
  - Phase 4 closeout can now treat strict annual value as a real 2016-start strategy path rather than a late-history partial prototype
  - Phase 4 still should not promote `Coverage 1000` to the public default because freshness risk remains the dominant issue
  - the next major workstream after Phase 4 closeout is still strategy-library / comparative-research work, not more UI skeleton or preset proliferation

### 2026-03-27 - `stale` in strict annual preflight should be explained directly in the UI
- Request topic:
  - the user could not tell what the `stale 4` message in strict annual preflight meant, and also suspected the UI might still be serving an old process
- Interpreted goal:
  - make sure the latest factor UI is actually loaded and reduce ambiguity around the preflight warning language
- Result:
  - confirmed current code already exposes the expanded strict value factor options in `Value Snapshot (Strict Annual)`
  - restarted Streamlit on `http://localhost:8501` so the latest UI is definitely active
  - added an explicit caption to strict annual preflight:
    - `stale` means the symbol's latest daily price in DB stops before the selected end date
- Durable output:
  - strict annual preflight warnings are now more self-explanatory for users who are validating large managed universes

### 2026-03-27 - Remaining strict-annual stale symbols should be fixed with daily price refresh, not fundamentals/statement collection
- Request topic:
  - clarify which ingestion job is actually needed to refresh `CADE`, `CFLT`, `CMA`, `DAY`
- Interpreted goal:
  - make the operational response explicit when strict annual preflight warns about lagging symbols
- Result:
  - the remaining `stale` warning comes from daily price freshness, not from factor or statement coverage
  - therefore the correct job is:
    - `Daily Market Update`
  - and the correct scope is:
    - symbols: `CADE,CFLT,CMA,DAY`
    - timeframe / interval:
      - daily / `1d`
    - date range:
      - a recent trailing window that reaches the selected backtest end date
- Durable output:
  - stale-price strict-annual warnings should be answered with targeted daily OHLCV refresh first
  - `Weekly Fundamental Refresh` or `Extended Statement Refresh` are not the first response for this specific warning

### 2026-03-27 - Current strict factor strategies do not yet include intramonth risk-off overlays
- Request topic:
  - clarify whether the current `Quality`, `Value`, `Quality + Value` strategies already include risk-management behavior such as crash-off, MA200 filter, or intramonth cash conversion
- Interpreted goal:
  - separate the currently implemented strategy contract from possible future overlays
- Result:
  - current strict factor strategies are still:
    - factor ranking
    - top-N selection
    - month-end rebalance
    - equal-weight holding
  - they do **not** currently include:
    - intramonth stop/risk-off events
    - MA200 trend filter
    - drawdown-triggered cash conversion
    - volatility-targeting overlay
  - code path confirmation:
    - `finance/strategy.py:quality_snapshot_equal_weight(...)`
      only re-ranks and reallocates on rebalance rows
      and otherwise carries the selected positions/cash forward
  - by contrast, some price-only strategies already do contain explicit defensive logic:
    - `GTAA`
    - `Risk Parity Trend`
    - `Dual Momentum`
    all have trend/cash-style logic in their own strategy paths
- Durable output:
  - if strict factor strategies need risk management, it should be treated as an added overlay layer rather than something already implied by the current `Quality` / `Value` / `Quality + Value` names
  - the natural future extension is:
    - `Quality (Strict Annual)`
    - `Quality + Trend Filter`
    - `Value + Trend Filter`
    - `Quality + Value + Risk Overlay`

### 2026-03-27 - Next major phase should explicitly include risk overlay work rather than leaving it as an implicit future idea
- Request topic:
  - after reviewing `PHASE4_NEXT_PHASE_PREPARATION.md`, create the next phase in a way that clearly includes later risk-management additions for strict factor strategies
- Interpreted goal:
  - make the absence of current risk overlays explicit and turn their addition into a formal next-phase workstream instead of a vague backlog item
- Result:
  - Phase 5 was opened in planning form with a combined direction:
    - `Strategy Library And Comparative Research`
    - `Risk Overlay For Strict Factor Strategies`
  - created:
    - `.note/finance/phase5/PHASE5_STRATEGY_LIBRARY_AND_RISK_OVERLAY_PLAN.md`
    - `.note/finance/phase5/PHASE5_CURRENT_CHAPTER_TODO.md`
  - updated phase-handoff documents so the next phase is no longer just a candidate list; it now explicitly includes:
    - strict family baseline comparison
    - overlay requirement definition
    - first overlay candidate selection
    - future examples such as
      - `Quality + Trend Filter`
      - `Value + Trend Filter`
      - `Quality + Value + Risk Overlay`
- Durable output:
  - the project now has a formal next-phase container for adding risk management to strict factor strategies later
  - Phase 4 remains closed around current strategy behavior, while overlay logic is clearly deferred into Phase 5

### 2026-03-27 - Phase 5 should also carry over quarterly strict-family work and compare advanced-input parity
- Request topic:
  - before implementation starts, capture two additional desired features in the next-phase plan:
    - quarterly strict family
    - compare-screen advanced-input parity for quality/value strict strategies
- Interpreted goal:
  - avoid losing known UX and strategy-extension requirements between Phase 4 closeout and Phase 5 kickoff
- Result:
  - both items were added to Phase 5 planning documents
  - recommended priority was fixed as:
    1. compare advanced-input parity
    2. quarterly strict-family evaluation / expansion
  - reasoning:
    - compare parity is a near-term UI/runtime consistency gap
    - quarterly strict family is a larger factor-coverage / timing / runtime project and should be treated as a separate expansion candidate
- Durable output:
  - Phase 5 now explicitly includes both:
    - strict factor risk overlay work
    - carry-over compare/quarterly expansion requests

### 2026-03-27 - Phase 5 first overlay should start as month-end trend filter, not intramonth risk-off
- Request topic:
  - execute the recommended Phase 5 order from baseline comparative research through first overlay selection and implementation
- Interpreted goal:
  - make the first strict-family risk overlay small, understandable, and safe enough to wire through UI/runtime/history without prematurely committing to intramonth complexity
- Result:
  - baseline strict-family research was fixed around:
    - compare baseline: `US Statement Coverage 100`
    - single baseline: `US Statement Coverage 300`
  - compare advanced-input parity was implemented for:
    - `Quality Snapshot (Strict Annual)`
    - `Value Snapshot (Strict Annual)`
    - `Quality + Value Snapshot (Strict Annual)`
  - first overlay was explicitly selected as:
    - `month-end MA200 trend filter + cash fallback`
  - the overlay was implemented in first-pass form across strict family runtime/UI/history/result schema
  - selection interpretation now distinguishes:
    - raw factor-ranked candidates
    - overlay-rejected names
    - final selected holdings
  - quarterly strict-family work and second-overlay work were documented as reviewed but deferred
- Durable output:
  - the project now has a concrete first overlay contract instead of a generic “risk overlay later” note
  - strict-family compare is materially closer to single-run parity
  - next Phase 5 decisions can focus on validating and extending the chosen overlay rather than re-deciding its baseline shape

### 2026-03-27 - Trend filter overlay needed an in-UI explanation example
- Request topic:
  - provide a very short practical example of the first strict-family trend filter behavior and expose it directly in the UI as a tooltip
- Interpreted goal:
  - reduce confusion around whether the current overlay is checked daily or only at rebalance time
- Result:
  - added a shared strict-family trend filter tooltip to single and compare forms
  - the tooltip now states that the current first pass is month-end only, not intramonth daily risk-off
  - it also includes a short example: if A and B are selected, and A is below MA200 at rebalance while B is above, then A moves to cash and B remains invested until the next rebalance
- Durable output:
  - the UI now explains the actual overlay semantics at the point of input instead of forcing the user to infer them from docs or chat

### 2026-03-27 - Some stale strict-universe symbols remain stale even after Daily Market Update because the source itself is not returning newer daily bars
- Request topic:
  - verify why `CADE`, `CMA`, `DAY`, `CFLT` still appear in strict-annual price freshness preflight after a user reran `Daily Market Update`
- Interpreted goal:
  - distinguish between a preflight bug, ingestion failure, and upstream price-source unavailability
- Result:
  - preflight is behaving correctly
  - DB latest dates currently are:
    - `CADE`: `2026-01-30`
    - `CMA`: `2026-01-30`
    - `DAY`: `2026-02-03`
    - `CFLT`: `2026-03-17`
  - `Daily Market Update` uses the same yfinance-backed OHLCV path as manual price collection
  - direct yfinance checks showed:
    - `CADE`: recent `1mo` fetch empty, `3mo` only through `2026-01-30`
    - `CMA`: recent `1mo` fetch empty, `3mo` only through `2026-01-30`
    - `DAY`: recent `1mo` fetch empty, `3mo` only through `2026-02-03`
    - `CFLT`: recent fetches only through `2026-03-17`
  - asset profile still marks all four as active, so the issue is not caused by local profile filtering; it is an upstream source freshness / symbol-resolution mismatch
- Durable output:
  - if these names continue to block managed strict presets, the right next fix is not another blind refresh but either:
    - excluding persistently stale names from managed presets, or
    - adding a freshness filter when building strict managed universes

### 2026-03-27 - Practical/investable strict managed universes should prefer backfill-to-target over drop-only
- Request topic:
  - define the practical policy for strict managed universes so the project can move toward a level where the user can realistically review backtests and use them for live investment judgment
- Interpreted goal:
  - move from “research demos that technically run” toward a more operationally trustworthy backtest environment without pretending the system is already full live-trading infrastructure
- Result:
  - the preferred managed-universe policy was fixed as:
    - `backfill-to-target`
  - meaning:
    - stale names are excluded
    - the preset then pulls in next-ranked eligible symbols (`1001`, `1002`, `1003`, ...) until the target count is restored as much as possible
  - this was chosen over `drop-only` because:
    - preset meaning stays more stable
    - `Coverage 1000` remains closer to a real usable 1000-name universe
    - the system becomes more practical for repeated real-world review
  - an important companion rule was also fixed:
    - exclusions and replacements should be shown transparently
  - the project target was explicitly reframed as:
    - decision-support quality research environment for real investment judgment
    - not immediate full live-trading automation
- Durable output:
  - Phase 5 now includes an explicit investable-readiness policy covering:
    - freshness-aware managed universes
    - backfill-to-target as the default policy
    - transparency for stale exclusions / replacements
    - acknowledgement that stale filtering alone does not fully solve delisting/symbol-change classification

### 2026-03-27 - Freshness-aware strict managed preset first pass was implemented at the UI preset-resolution layer
- Request topic:
  - turn the new practical-investment policy into actual behavior for strict managed presets
- Interpreted goal:
  - make `Coverage 300/500/1000` behave more like real usable universes instead of static lists that only warn about stale symbols
- Result:
  - strict managed presets are now resolved dynamically at UI/runtime handoff time
  - policy:
    - `freshness_backfill_to_target`
  - behavior:
    - stale / missing symbols inside the target top-N block are excluded
    - lower-ranked fresh symbols are pulled in until the target count is restored as much as possible
  - both single and compare strict-family flows now use the resolved universe instead of the old static preset list
  - exclusion / replacement details are shown to the user and also stored in metadata/history
  - smoke verification for `end=2026-03-20` showed:
    - `US Statement Coverage 300` -> `300/300`, no changes
    - `US Statement Coverage 1000` -> `1000/1000`, `5` exclusions, `5` replacements
- Durable output:
  - the project now has a first-pass investable managed-universe mechanism
  - next follow-up is no longer “make the preset usable,” but
    - refine stale reason classification
    - decide how aggressively to surface replacement history in compare/results

### 2026-03-27 - Historical backtests should not use end-date freshness replacement as the only universe rule
- Request topic:
  - sanity-check whether a 2016~2026 backtest should really exclude names like `CADE`, `CMA`, `DAY` from the whole run just because they are stale at the selected end date
- Interpreted goal:
  - distinguish between:
    - a practical “what can I invest in now?” managed universe
    - a historically faithful backtest universe
- Result:
  - the current freshness-aware `backfill-to-target` preset resolution is useful for **present-day investable preset hygiene**
  - but for **historical backtest validity**, applying an end-date freshness filter to the whole run is too aggressive
  - a more realistic historical rule is:
    - keep a symbol in the backtest universe until its last valid trading date
    - after that date, naturally exclude it at rebalance time
    - if replacements are desired, do them only on scheduled universe-reconstitution dates, not retroactively from the full-run start
  - therefore the recommended practical direction is to split the behavior into two modes:
    1. `historical_backtest`:
       - no full-run exclusion just because the symbol is stale at the selected end date
       - per-rebalance availability filtering decides whether a symbol can be selected
       - warnings still show stale/end-date issues
    2. `investable_now`:
       - freshness-aware `backfill-to-target`
       - designed for “if I ran this today, what is the usable managed universe now?”
- Durable output:
  - the project should not treat the current run-level freshness replacement policy as the final answer for all strict backtests
  - the more robust design is to separate:
    - historical backtest validity
    - present-day investable universe construction

### 2026-03-27 - Historical-only strict preset semantics were adopted as the current product behavior
- Request topic:
  - decide whether to keep the new freshness-aware replacement logic or return to a pure historical-backtest interpretation
- Interpreted goal:
  - make strict annual backtests valid enough to support real research/investment judgment without retroactively removing names that were still tradable earlier in the test window
- Result:
  - the project does **not** keep a separate `Investable Now` mode at this time
  - strict managed presets now stay fixed for the run
  - `Price Freshness Preflight` remains as a warning/diagnostic layer only
  - symbols are filtered at each rebalance date by actual price/factor availability instead of by selected end-date freshness replacement
  - UI now includes a short tooltip explaining this historical-backtest behavior
- Durable output:
  - current official behavior is:
    - run-level static preset universe
    - rebalance-date candidate filtering
    - freshness warning, but no run-level replacement
  - any future `investable now` mode is deferred and not part of the present product surface

### 2026-03-27 - Compare strategy advanced-input blocks should rerender immediately when the selected strategies change
- Request topic:
  - compare screen did not show the expected advanced input controls for quality/value strict strategies after selecting them
- Interpreted goal:
  - make compare behave like the single-strategy screen, where strategy selection immediately reveals the relevant controls
- Result:
  - the compare `Strategies` selector was inside `st.form(...)`, which prevented immediate reruns
  - it was moved outside the form so the strategy-specific advanced-input sections now update as soon as the selection changes
- Durable output:
  - compare strict-family preset/factor/overlay controls should now appear immediately after selecting the relevant strategies

### 2026-03-27 - Backtest history should live as a shared top-level surface instead of being nested under compare
- Request topic:
  - review whether `Persistent Backtest History` / `History Drilldown` should move into a separate tab because they are shared by single and compare workflows
- Interpreted goal:
  - make the backtest UI structure reflect ownership more clearly and avoid implying that history belongs only to compare/portfolio builder
- Result:
  - the backtest top-level navigation now has a dedicated `History` tab
  - `Persistent Backtest History` and `History Drilldown` were moved there from the bottom of the compare tab
  - compare remains focused on:
    - strategy selection
    - advanced inputs
    - comparison results
    - weighted portfolio builder
- Durable output:
  - history is now presented as a shared cross-workflow surface for:
    - single-strategy execution
    - strategy comparison

### 2026-03-27 - Finish Phase 5 first-pass workstream for overlay validation, stale diagnostics, interpretation, quarterly review, and second-overlay review
- Request topic:
  - finish the pending Phase 5 workstream in order:
    1. overlay on/off validation
    2. stale reason classification
    3. selection interpretation strengthening
    4. quarterly strict family review
    5. second overlay candidate review
- Interpreted goal:
  - move the Phase 5 first chapter from “feature scaffolding exists” to “research/diagnostic results are documented and ready for user testing”
- Result:
  - strict preflight now includes heuristic stale/missing reason classification
  - strict selection history now exposes interpretation summary, cash-share context, and overlay rejection frequency
  - first overlay on/off validation was collected on canonical compare settings
  - quarterly strict family remains deferred, with clearer public-entry criteria
  - second overlay next candidate is still `Market Regime Overlay`, now with clearer entry conditions
- Durable output:
  - current Phase 5 chapter should be understood as:
    - overlay implemented
    - overlay validation documented
    - stale diagnostics implemented
    - selection interpretation strengthened
    - quarterly and second-overlay decisions documented
  - next step is user validation of the current surface before opening the next chapter

### 2026-03-27 - Streamlit runtime error after selection-interpretation change
- Request topic:
  - app crashed while rendering the latest backtest run with `NameError: name 'np' is not defined`
- Interpreted goal:
  - restore the backtest page quickly and keep the new interpretation feature intact
- Result:
  - the selection-interpretation path in `app/web/pages/backtest.py` used `np.where(...)`
    without importing `numpy as np`
  - the missing import was added and the page compiled successfully
- Durable output:
  - this was a hotfix only; no strategy behavior changed
  - the interpretation feature still stands, and the failure was caused only by a missing module import

### 2026-03-28 - Value strict coverage-1000 history rendering failed in selection-history cash-share logic
- Request topic:
  - `Value Snapshot (Strict Annual)` with `Coverage 1000` still crashed while rendering selection history around the `Cash` column path
- Interpreted goal:
  - make the selection-interpretation/history surface robust enough that value strict runs do not fail on result-shape edge cases
- Result:
  - `_build_snapshot_selection_history(...)` was hardened so duplicate column names no longer break the `Cash` / `Total Balance` / selected-count extraction path
  - the function now:
    - de-duplicates duplicate columns defensively
    - resolves the first valid series for duplicate-named fields before numeric coercion
- Durable output:
  - this is a rendering-layer robustness fix
  - it does not change selection logic or backtest strategy behavior

### 2026-03-28 - Latest Backtest Run should not crash when an older selection-history payload is malformed
- Request topic:
  - even after the direct selection-history fix, the user still saw the backtest screen die when rendering the latest run
- Interpreted goal:
  - protect the `Latest Backtest Run` surface from total failure while we flush old payloads and continue verifying the exact edge case
- Result:
  - `_render_snapshot_selection_history(...)` now catches builder failures and falls back to:
    - a warning message
    - a short renderer-detail caption
    - no full-page crash
- Durable output:
  - malformed or older run payloads should no longer take down the entire backtest page
  - rerunning the backtest remains the recommended way to rebuild a clean latest-run bundle

### 2026-03-28 - Provide a practical Phase 5 manual test checklist as a Markdown document
- Request topic:
  - convert the current verbal testing guidance into an actual `.md` file for user-driven verification
- Interpreted goal:
  - make the current strict-family validation process repeatable and easy to follow without relying on chat history
- Result:
  - created a dedicated Phase 5 strict-family checklist document covering:
    - single strategy smoke tests
    - overlay on/off checks
    - preflight / stale-classification checks
    - compare advanced-input checks
    - history tab checks
    - tooltip / copy checks
- Durable output:
  - the current recommended manual QA entry point is:
    - `.note/finance/phase5/PHASE5_STRICT_FAMILY_TEST_CHECKLIST.md`

### 2026-03-28 - Make phase-end manual test checklists a standing repository rule
- Request topic:
  - add a durable instruction so future phases always end with a user-facing test checklist document
- Interpreted goal:
  - prevent phase closeout testing guidance from living only in chat and make final verification repeatable
- Result:
  - updated `AGENTS.md` to require:
    - a phase-specific manual test checklist at practical phase completion
    - checklist coverage for major features, UI paths, and validation points added in that phase
    - checklist sharing as part of final phase handoff
- Durable output:
  - future phase closeouts should now include a checklist document by default, not as an ad hoc extra

### 2026-03-28 - Clarify strict-family interpretation metrics and localize tooltip/help copy to Korean
- Request topic:
  - explain:
    - `Raw Candidate Events`
    - `Final Selected Events`
    - `Overlay Rejection Frequency`
    - `Cash Share`
  - and translate the `?`/tooltip help copy into Korean
- Interpreted goal:
  - make the current strict-family UI easier to understand during manual testing without relying on chat explanations
- Result:
  - clarified the semantics of the interpretation metrics and added Korean help/popover copy for:
    - historical universe behavior
    - trend filter overlay
    - interpretation summary
    - overlay rejection frequency
    - cash share
  - translated the main strict-family single-form help text to Korean as well
- Durable output:
  - strict-family testing should now be possible with in-product Korean explanations for the main interpretation surfaces

### 2026-03-28 - Raw/Final event counts should explain overlay intervention rather than imply universe size
- Request topic:
  - refine the help copy so users do not misread `Raw Candidate Events` / `Final Selected Events` as the size of the filtered universe
- Interpreted goal:
  - make the UI explain that these numbers are event totals used mainly to understand overlay intervention
- Result:
  - updated the interpretation help text so it explicitly says:
    - Raw / Final are cumulative selection-event counts across rebalances
    - they are not the size of the whole eligible universe
    - when overlay is off, Raw and Final are usually the same
    - when overlay is on, the Raw-Final gap measures how much the overlay intervened
- Durable output:
  - the strict-family interpretation UI now better supports the intended reading of the overlay metrics

### 2026-03-28 - Daily Market Update should be optimized to avoid yfinance rate limiting on `NYSE Stocks + ETFs`
- Request topic:
  - reproduce the broad `Daily Market Update` issue on `NYSE Stocks + ETFs`, then propose a direction first in Markdown before implementation
- Interpreted goal:
  - understand why large daily price refreshes start well and then degrade into repeated `Too Many Requests` failures, and define a practical optimization path
- Result:
  - reproduced the issue on the raw exchange source
  - confirmed current raw source size is `11,736` symbols
  - confirmed the raw source contains many noisy non-plain symbols (`434`) compared with the profile-filtered source (`18`)
  - observed that visible rate-limit failures can occur without being captured in current `batch_errors`, because the provider may return partial data while surfacing failures as symbol-level messages
  - created a durable direction document:
    - `.note/finance/DAILY_MARKET_UPDATE_RATE_LIMIT_ANALYSIS_20260328.md`
- Durable output:
  - recommended first-pass direction is:
    - safer/default managed source preference
    - smaller chunk / lower concurrency / jitter
    - rate-limit cooldown / circuit breaker
    - better diagnostics separating provider no-data from true rate limiting

### 2026-03-28 - Daily Market Update rate-limit mitigation implemented as managed-safe default plus raw-heavy fallback
- Request topic:
  - implement the proposed `1차 -> 2차 -> 3차` optimization set for `Daily Market Update`, then leave the system ready for user testing
- Interpreted goal:
  - keep broad daily price refreshes from degrading into repeated rate-limit failures, while preserving operator visibility into what failed and why
- Result:
  - changed the default Daily Market Update source to `Profile Filtered Stocks + ETFs`
  - added execution profiles:
    - `managed_safe`
    - `raw_heavy`
  - hardened `store_ohlcv_to_mysql(...)` with:
    - smaller batches
    - single-worker safe mode
    - retry backoff
    - sleep jitter
    - rate-limit cooldown events
  - added provider-message based diagnostics so results now distinguish:
    - `rate_limited_symbols`
    - `provider_no_data_symbols`
  - added optional raw-source filtering for non-plain symbols
  - added result-level replay payloads for operator reruns
- Durable output:
  - `.note/finance/DAILY_MARKET_UPDATE_RATE_LIMIT_IMPLEMENTATION_20260328.md`

### 2026-03-28 - Daily Market Update should move from pure stabilization to measured speed optimization
- Request topic:
  - after a successful but slow run (~2400 sec), create a second-pass speed optimization plan and implement it in three steps
- Interpreted goal:
  - preserve the new rate-limit stability while improving runtime for managed broad refreshes
- Result:
  - added a planning note for the second-pass speed optimization
  - implemented timing breakdown metrics in the OHLCV writer so slow runs can now be decomposed into:
    - fetch
    - delete
    - upsert
    - retry sleep
    - cooldown sleep
    - inter-batch sleep
  - added a new `managed_fast` execution profile
  - split source-to-profile routing so:
    - `Profile Filtered Stocks + ETFs` uses `managed_fast`
    - raw NYSE sources use `raw_heavy`
    - narrower/manual sources use `managed_safe`
  - surfaced the timing breakdown in the Streamlit result diagnostics
- Durable output:
  - `.note/finance/DAILY_MARKET_UPDATE_SPEED_OPTIMIZATION_PLAN_20260328.md`
  - `.note/finance/DAILY_MARKET_UPDATE_SPEED_OPTIMIZATION_IMPLEMENTATION_20260328.md`

### 2026-03-28 - Phase 5 can now be treated as a completed first chapter and should hand off to next-phase preparation
- Request topic:
  - after user testing indicated the Phase 5 surface is broadly in good shape, determine whether Phase 5 is effectively done and add formal closeout documents
- Interpreted goal:
  - move Phase 5 from active implementation to an explicit closeout-ready state before choosing the next major workstream
- Result:
  - judged the current Phase 5 scope as effectively complete at the first-chapter level
  - added:
    - `.note/finance/phase5/PHASE5_COMPLETION_SUMMARY.md`
    - `.note/finance/phase5/PHASE5_NEXT_PHASE_PREPARATION.md`
  - updated the Phase 5 TODO board, roadmap, and doc index to reflect closeout
- Durable output:
  - Phase 5 should now be read as:
    - first chapter completed
    - next chapter / next phase not yet formally opened

### 2026-03-28 - Phase closeout should also refresh skills and reference guidance when workflows changed
- Request topic:
  - make phase-end closeout update not only the phase docs and test checklist, but also the project’s skill/reference guidance whenever newly implemented behavior changed how future work should be done
- Interpreted goal:
  - prevent future turns from relying on stale workflow guidance after a phase materially changes defaults, operator flow, validation rules, or execution patterns
- Result:
  - updated `AGENTS.md` so phase closeout now explicitly includes a review of:
    - `AGENTS.md`
    - active skills / `SKILL.md`
    - `FINANCE_DOC_INDEX.md`
    - `MASTER_PHASE_ROADMAP.md`
    - phase-specific reference/preparation docs
  - also added the expectation that if no refresh is needed, that outcome should still be recorded briefly in closeout notes or progress logs
- Durable output:
  - future finance phase closeouts should now include:
    - closeout summary
    - next-phase prep
    - manual checklist
    - skill/reference guidance refresh review

### 2026-03-28 - Install Firecrawl and verify Playwright MCP for Codex before the next phase
- Request topic:
  - install Firecrawl MCP and Playwright MCP into Codex before starting the next phase
- Interpreted goal:
  - make the local Codex environment ready to use browser automation and hosted scraping/search tools without delaying the next chapter
- Result:
  - verified that `playwright` MCP was already installed and enabled in `~/.codex/config.toml`
  - added `firecrawl` MCP to Codex as a hosted streamable HTTP server using:
    - `https://mcp.firecrawl.dev/v2/mcp`
    - `FIRECRAWL_API_KEY` as the bearer-token environment variable
  - intentionally avoided storing the Firecrawl API key directly in the config file
- Follow-up note:
  - Firecrawl is installed/configured, but actual use still requires `FIRECRAWL_API_KEY` to be available in the environment of the Codex process.

### 2026-03-28 - Open the next finance phase after Phase 5 closeout
- Request topic:
  - move into the next phase
- Interpreted goal:
  - formally open the next major workstream rather than leaving next steps only in preparatory notes
- Result:
  - opened Phase 6
  - fixed the new phase direction as:
    - second overlay implementation first
    - quarterly strict family entry and validation second
  - created:
    - `.note/finance/phase6/PHASE6_OVERLAY_AND_QUARTERLY_EXPANSION_PLAN.md`
    - `.note/finance/phase6/PHASE6_CURRENT_CHAPTER_TODO.md`
  - synced the new phase into:
    - `MASTER_PHASE_ROADMAP.md`
    - `FINANCE_DOC_INDEX.md`
- Durable output:
  - the next active finance chapter is now Phase 6, with `Market Regime Overlay` as the leading candidate and quarterly strict family work framed as entry/validation rather than immediate full rollout.

### 2026-03-28 - Complete the planned Phase 6 first pass before user testing
- Request topic:
  - follow the recommended Phase 6 implementation order end-to-end and prepare a checklist before user testing
- Interpreted goal:
  - complete the first full chapter pass for:
    - `Market Regime Overlay`
    - strict quarterly family entry path
  - then hand off a concrete manual test checklist instead of partial implementation notes
- Result:
  - fixed the initial runtime blocker in the new strict wrapper path
  - implemented `Market Regime Overlay` first pass for strict family:
    - benchmark/window inputs
    - runtime and strategy integration
    - compare/single/history support
    - interpretation and event-level reporting
  - implemented a research-only single-strategy path:
    - `Quality Snapshot (Strict Quarterly Prototype)`
  - ran DB-backed small-smoke validations for:
    - annual strict quality
    - annual strict value
    - annual strict quality+value
    - strict quarterly prototype
  - documented requirements, implementation, validation, quarterly entry criteria, and the Phase 6 manual test checklist
- Durable output:
  - Phase 6 current chapter should now be read as:
    - implementation first pass complete
    - closeout not yet done
    - manual UI validation next

### 2026-03-28 - Resolve Phase 6 checklist UX and history issues
- Request topic:
  - fix the issues found while manually testing the Phase 6 checklist
- Interpreted goal:
  - make market regime inputs easier to understand and edit
  - fix history/prefill runtime issues
  - make compare/history surfaces easier to interpret during manual validation
- Result:
  - clarified that `Market Regime Window = 200` means the benchmark `200-trading-day moving average`
  - changed strict-family overlay inputs so window / benchmark can be edited before the enable toggle is turned on
  - grouped compare strict annual override sections into clearer separated UI blocks
  - fixed `Load Into Form` for single-strategy history by deferring the strategy selector update until before the widget is instantiated
  - improved compare history drilldown so newer compare records show stored per-strategy summary rows and strategy-level override/regime context instead of only an empty-primary-summary message
  - added clearer copy explaining that `Load Into Form` prefills the single-strategy form for editing rather than rerunning immediately
  - added a quarterly prototype warning that coverage can begin later than the requested start date
- Durable output:
  - Phase 6 history/prefill and compare drilldown should now be read as:
    - single-strategy `Load Into Form` is supported and safe
    - compare records keep strategy-level override context
    - older compare records may still lack stored per-strategy summary rows because they were recorded before the new context shape existed
- updated compare strict annual advanced inputs again so each strategy block is collapsible via expander, reducing visual clutter during manual testing
- extended the compare advanced-input collapsible UI pattern to Equal Weight and GTAA for consistency with the strict annual strategy blocks

### 2026-03-28 - Close out Phase 6 and open Phase 7
- Request topic:
  - finish Phase 6 and move to the next phase
- Interpreted goal:
  - formally close the second-overlay / quarterly-entry chapter
  - open the next major workstream in a way that matches the quarterly prototype findings
- Result:
  - wrote Phase 6 closeout docs:
    - `PHASE6_COMPLETION_SUMMARY.md`
    - `PHASE6_NEXT_PHASE_PREPARATION.md`
  - updated roadmap / index / current chapter documents so Phase 6 now reads as completed
  - opened Phase 7 with:
    - `PHASE7_QUARTERLY_COVERAGE_AND_STATEMENT_PIT_HARDENING_PLAN.md`
    - `PHASE7_CURRENT_CHAPTER_TODO.md`
  - fixed the recommended next direction as:
    - quarterly coverage hardening
    - statement source payload inspection
    - PIT timing / raw ledger hardening
- Durable output:
  - the active finance phase is now Phase 7
  - the immediate next priority is not a new overlay, but rebuilding the quarterly statement / shadow foundation so quarterly strict family can gain longer usable history

### 2026-03-28 - Phase 7 quarterly late-start root cause and hardening decision
- Request topic:
  - execute Phase 7 in the recommended order and prepare a checklist when the first pass is complete
- Interpreted goal:
  - make `Quality Snapshot (Strict Quarterly Prototype)` stop behaving like a near-2025-only strategy
  - verify what the statement source really returns
  - decide whether raw statement tables need destructive redesign
- Result:
  - source inspection showed the EDGAR path already returns long-history facts and real timing fields (`filing_date`, `accepted_at`, `available_at`, `report_date`, `accession`)
  - current raw statement tables were not the main blocker; they already had enough PIT columns for a first-pass quarterly recovery
  - the real blockers were:
    - quarterly ingestion excluded `10-K/FY`
    - statement ingestion defaults were too shallow
    - quarterly shadow fundamentals builder incorrectly filtered rows by `report_date` semantics
  - decision:
    - keep the current raw statement tables
    - harden loader semantics instead of dropping/recreating the schema
    - add a human-readable inspection path rather than a destructive redesign
  - implementation first pass:
    - quarterly path now accepts `10-K/10-K-A` and `FY`
    - statement ingestion now officially supports `periods=0` meaning all available periods
    - quarterly shadow builder no longer drops valid rows via the old `report_date` anchor filter
    - new inspection path:
      - richer `inspect_financial_statement_source()`
      - `load_statement_timing_audit(...)`
  - validation:
    - sample symbols `AAPL/MSFT/GOOG` recovered long quarterly history back to 2006/2007/2012
    - `US Statement Coverage 100` quarterly shadow rebuilt to `100 symbols / 6,796 rows`
    - quarterly prototype on `US Statement Coverage 100` now becomes active from `2016-01-29`
- Durable output:
  - Phase 7 first pass should be understood as a quarterly data-foundation repair, not a new strategy feature
  - destructive schema redesign is not required at this point
  - future quarterly work should start from the repaired statement ingestion + shadow path rather than from the old late-start assumption

### 2026-03-28 - Phase 7 checklist pre-check result
- Request topic:
  - run the Phase 7 checklist once before the user starts manual validation
- Interpreted goal:
  - confirm that the new quarterly PIT/coverage work is actually testable and not just documented
- Result:
  - checklist items 1 through 7 were effectively confirmed by code/runtime checks
  - quarterly prototype now activates from `2016-01-29` for both:
    - manual `AAPL,MSFT,GOOG`
    - `US Statement Coverage 100`
  - helper inspection paths are usable:
    - `load_statement_coverage_summary`
    - `load_statement_timing_audit`
    - `inspect_financial_statement_source`
  - annual strict regression was also checked:
    - runtime path still works
    - manual `AAPL,MSFT,GOOG` annual strict starting in `2025-07-31` is expected given current annual strict data availability and is not a new Phase 7 regression
- Durable output:
  - the user can now run the written Phase 7 checklist with high confidence that the key quarterly recovery path is already working

### 2026-03-28 - Phase 7 supplementary polish direction
- Request topic:
  - proactively organize and add practical Phase 7 improvements before the user starts manual checking
- Interpreted goal:
  - reduce avoidable confusion in the quarterly prototype UI and diagnostics after the core quarterly PIT/coverage repair was already completed
- Result:
  - selected a low-risk polish scope instead of reopening the data foundation:
    - weekend/holiday-aware price freshness preflight
    - quarterly statement shadow coverage preview
    - statement PIT inspection UI card
    - refreshed quarterly prototype UI wording
  - key decision:
    - end-date freshness should be judged against the latest actual market session in DB, not blindly against a non-trading selected date
  - validation:
    - `US Statement Coverage 100`, selected end `2026-03-28` now maps to effective trading end `2026-03-27`
    - `stale_count = 0`
    - quarterly shadow preview reports full preset coverage and long-history period bounds
- Durable output:
  - Phase 7 user validation should now read quarterly prototype state more accurately:
    - fewer false stale warnings on weekends/holidays
    - visible shadow coverage bounds before execution
    - UI-based PIT inspection path without requiring notebook snippets

### 2026-03-28 - Phase 7 validation deferral and Phase 8 opening decision
- Request topic:
  - proceed to the next phase without waiting for immediate Phase 7 manual validation
- Interpreted goal:
  - keep development momentum while the user is occupied, and batch manual validation later with the next phase checklist
- Result:
  - decided to treat Phase 7 as:
    - implementation completed
    - manual validation intentionally deferred
  - decided that the most natural next phase is:
    - `Quarterly Strategy Family Expansion And Promotion Readiness`
  - rationale:
    - Phase 7 repaired quarterly data foundation
    - the next meaningful product step is to expand quarterly from a single quality prototype into a broader strategy family
- Durable output:
  - Phase 7 closeout docs created
  - Phase 8 kickoff docs created
  - future user validation can review Phase 7 + Phase 8 checklists together in one batch

### 2026-03-28 - Phase 8 quarterly family scope and exposure decision
- Request topic:
  - continue Phase 8 autonomously so the user can review later in one batch via checklist
- Interpreted goal:
  - turn quarterly strict from a single quality prototype into a research-ready strategy family without requiring frequent ping-pong decisions
- Result:
  - decided to expose quarterly strict as a 3-strategy research-only family:
    - `Quality Snapshot (Strict Quarterly Prototype)`
    - `Value Snapshot (Strict Quarterly Prototype)`
    - `Quality + Value Snapshot (Strict Quarterly Prototype)`
  - decided to open all three not only in single strategy UI but also in compare first pass
  - rationale:
    - annual vs quarterly and quality vs value vs quality+value research is much weaker if compare remains absent
    - the existing annual strict runtime/UI pattern was reusable enough to open compare without a new architecture pass
- Durable output:
  - quarterly family naming policy fixed as `Strict Quarterly Prototype`
  - compare exposure decision fixed as `enabled first pass`
  - manual validation can now treat quarterly family as a coherent research surface rather than a quality-only experiment

### 2026-03-28 - Phase 8 quarterly value / multi-factor first-pass validation
- Request topic:
  - continue development and leave a later checklist-driven review surface
- Interpreted goal:
  - implement quarterly value and quarterly quality+value product surfaces deeply enough that later user testing can happen in one batch
- Result:
  - implemented runtime/UI/history/compare integration for:
    - `Value Snapshot (Strict Quarterly Prototype)`
    - `Quality + Value Snapshot (Strict Quarterly Prototype)`
  - smoke validation results:
    - manual `AAPL/MSFT/GOOG`
      - value quarterly first active = `2017-05-31`
      - quality+value quarterly first active = `2017-05-31`
    - preset `US Statement Coverage 100`
      - value quarterly first active = `2016-01-29`
      - quality+value quarterly first active = `2016-01-29`
  - compare smoke also succeeded for quarterly value with selection-history build
- Durable output:
  - quarterly strict family should now be understood as:
    - research-ready for single + compare + history
    - still not promotion-ready for public candidate status
  - promotion decision should wait for manual validation plus annual-vs-quarterly comparative readout

### 2026-03-28 - Phase 8 checklist prevalidation result
- Request topic:
  - run the Phase 8 checklist once before the user reviews it later in one batch
- Interpreted goal:
  - reduce the chance that the later manual review finds basic runtime or wiring failures
- Result:
  - all checklist items that are automatable without browser clicks passed
  - verified:
    - quarterly value single path
    - quarterly quality+value single path
    - manual small-universe runs
    - compare exposure and compare execution
    - history append/load/payload/prefill helper
    - quarterly meta/context fields
    - research-only semantics and default preset
  - the only remaining unchecked layer is true browser-side manual UX readability
- Durable output:
  - Phase 8 can now be treated as:
    - implementation complete for first pass
    - checklist prevalidated by assistant
    - user manual validation still pending for final visual confirmation

### 2026-03-28 - Phase 7 ingestion checklist clarification
- Request topic:
  - the user could not find `Financial Statement Ingestion` from the Phase 7 checklist and wanted to understand what `Statement PIT Inspection` actually does
- Interpreted goal:
  - remove UI ambiguity before the user continues with the rest of the Phase 7 manual checklist
- Result:
  - confirmed `Financial Statement Ingestion` still exists, but lives under `Ingestion > Manual Jobs` rather than next to `Extended Statement Refresh`
  - updated the UI copy so the relationship is explicit:
    - `Extended Statement Refresh` is the recommended operational entry point
    - `Financial Statement Ingestion` is the lower-level manual card kept for exception handling / debugging
  - clarified that `Statement PIT Inspection` is not an ingestion job:
    - `Coverage Summary` and `Timing Audit` read existing MySQL statement ledgers
    - `Source Payload Inspection` fetches a live EDGAR sample payload only to inspect source fields
  - updated `PHASE7_TEST_CHECKLIST.md` to match the actual UI layout
- Durable output:
  - future Phase 7 validation should treat item 1 as:
    - operational card = `Extended Statement Refresh`
    - lower-level manual card = `Manual Jobs > Financial Statement Ingestion`
  - item 2 should be read as a PIT inspection / diagnostic helper, not as a data collection step

### 2026-03-28 - Ingestion console structure review
- Request topic:
  - review whether `Operational Pipelines` and `Manual Jobs` should be separated more clearly because the single list layout was causing confusion
- Interpreted goal:
  - make the ingestion console easier to understand before the user continues the Phase 7 checklist
- Result:
  - separated the ingestion console into two explicit tabs:
    - `Operational Pipelines`
    - `Manual Jobs / Inspection`
  - added Korean explanatory boxes at the top of each tab instead of hover-only tooltips because Streamlit tab labels do not support native help icons
  - kept the intended mental model explicit:
    - operational tab = recurring production refresh workflows
    - manual/inspection tab = exception handling, lower-level reruns, debugging, and PIT diagnostics
- Durable output:
  - future ingestion-related checklist/docs should reference the two-tab layout rather than describing the console as one long list

### 2026-03-28 - Statement ingestion field semantics and latest-run UX
- Request topic:
  - clarify the meaning of statement ingestion controls and reduce scroll disruption caused by the global `Latest Completed Run`
- Interpreted goal:
  - let the user continue the Phase 7 checklist without stopping to reverse-engineer ambiguous ingestion fields
- Result:
  - clarified the actual semantics in UI copy:
    - `Financial Statement Freq` = target ledger frequency plus filing/fiscal-period filtering semantics
    - `Financial Statement Period Type` = which EDGAR statement view (`annual` / `quarterly`) is requested from the source
    - normal operator runs should generally keep them aligned
  - clarified `Statement PIT Inspection` field roles:
    - `Timing Audit Symbols` = how many of the selected symbols are included in the timing audit table
    - `Rows / Symbol` = how many timing rows per symbol are shown
    - `Source Sample Size` = how many live payload samples are displayed in source inspection
    - `Source Inspection Symbol` = the single symbol used for the live EDGAR payload inspection
  - moved `Latest Completed Run` rendering away from the global top insertion and now show it inline under the matching ingestion card
- Durable output:
  - Phase 7 ingestion checklist can now be interpreted directly from the UI without relying on chat context

### 2026-03-29 - Statement PIT Inspection role and freq/period UI simplification
- Request topic:
  - clarify whether `Statement PIT Inspection` is mainly a pre-ingestion source check and whether `Financial Statement Freq` and `Financial Statement Period Type` should be unified
- Interpreted goal:
  - reduce operator confusion in the Phase 7 ingestion flow by removing controls that do not provide meaningful day-to-day value
- Result:
  - `Statement PIT Inspection` should be understood as a mixed diagnostic helper, not a single-purpose pre-ingestion checker:
    - `Coverage Summary` and `Timing Audit` inspect already stored MySQL statement ledgers
    - `Source Payload Inspection` is the pre-ingestion/live-source part that shows one EDGAR sample payload and its timing fields
  - therefore the card is useful both before and after ingestion, but only the `Source Payload Inspection` subsection is truly "before-ingestion"
  - for `Financial Statement Ingestion`, the current split between `Financial Statement Freq` and `Financial Statement Period Type` is technically meaningful in the codebase:
    - `freq` controls target ledger frequency plus filing/fiscal-period filtering
    - `period` controls which EDGAR statement view is requested
  - however, current operator usage does not have a strong real-world need to set them differently
- Durable output:
  - recommended UX direction:
    - unify the visible UI into one operator-facing control for normal runs
    - keep the internal code parameters separate behind the scenes
    - if needed later, reintroduce the split as an advanced/override option rather than as the default UI

### 2026-03-29 - Manual statement ingestion UI unified to statement mode
- Request topic:
  - proceed with the freq/period simplification
- Interpreted goal:
  - reduce operator confusion in the manual statement ingestion card without changing the underlying ingestion semantics
- Result:
  - replaced the two separate operator-facing controls with one `Statement Mode` control
  - the selected mode now feeds both internal params:
    - `freq = statement_mode`
    - `period = statement_mode`
  - preserved the backend distinction in code so advanced behavior could be reintroduced later if needed
- Durable output:
  - current operator UX should be treated as:
    - one visible statement mode selector
    - one periods selector
    - no default need to reason about mismatched `freq` vs `period`

### 2026-03-29 - Statement PIT Inspection interpretation guide added
- Request topic:
  - after explaining how to read `Statement PIT Inspection`, add that interpretation guidance back into the UI
- Interpreted goal:
  - keep the user from having to reopen chat to remember how to interpret coverage/timing/source sections
- Result:
  - added Korean interpretation help directly into the card:
    - a top-level `이 카드 읽는 법` expander
    - per-section captions for `Coverage Summary`, `Timing Audit`, and `Source Payload Inspection`
  - the UI now explicitly states:
    - `Coverage Summary` = DB ledger coverage
    - `Timing Audit` = PIT timing/readiness audit
    - `Source Payload Inspection` = live EDGAR source field inspection
- Durable output:
  - future Phase 7 validation can rely on in-app guidance instead of chat-only explanation for PIT inspection interpretation

### 2026-03-29 - Trend overlay cash handling semantics
- Request topic:
  - clarify whether partial trend-overlay rejections in quality/value snapshot strategies move the rejected portion to cash or reallocate across surviving names
- Interpreted goal:
  - explain why the Result Table can show overlay rejections while the `Cash` column stays at zero
- Result:
  - current implementation does **not** keep partial cash for partially rejected month-end selections
  - runtime behavior is:
    - raw top `N` is selected
    - trend overlay removes names that fail `Close >= MA(window)`
    - if at least one name survives, the remaining names are re-equal-weighted across the full base balance
    - therefore `Cash` stays near `0`
  - only two cases move the portfolio to cash:
    - no names survive the final filtered selection
    - market-regime overlay sets the entire rebalance to `risk_off`
- Durable output:
  - current semantics should be read as:
    - partial trend rejection => survivors are reweighted, not partially cash-funded
    - full rejection or regime-off => cash
  - there is currently a wording mismatch because some UI/runtime warning text still says rejected selections "move to cash until next rebalance" even though the code only does that when the final selected set is empty

### 2026-03-29 - Overlay cash policy research
- Request topic:
  - investigate whether partial overlay rejections in the strict factor family should be left as cash or reallocated to surviving names
- Interpreted goal:
  - compare real-world conventions and decide which interpretation best fits the current monthly top-N stock-selection strategy
- Result:
  - confirmed current repo behavior:
    - partial trend-overlay rejections are reallocated across surviving names
    - only `all rejected` or `market regime risk-off` leads to `100% cash`
  - identified a wording mismatch:
    - some runtime/UI copy still implies rejected names move to cash even when only part of the basket is rejected
  - external review separated three practitioner buckets:
    - stock-selection / factor-filter portfolios: usually drop rejected names and equal-weight survivors
    - tactical asset allocation sleeves: usually move failed sleeves to cash / T-bills
    - market-regime overlays: often hedge or reduce net exposure instead of using per-name cash slots
  - recommended for the current project:
    - keep `survivor reweighting` as the default semantics for strict factor strategies
    - treat `partial cash retention` as a separate optional policy only if explicitly desired later
- Durable output:
  - `.note/finance/OVERLAY_CASH_POLICY_RESEARCH.md`

### 2026-03-29 - Price stale diagnosis first pass
- Request topic:
  - propose and implement a practical way to separate delisting/symbol issues, provider source gaps, and local ingestion gaps when strict backtest preflight shows stale symbols
- Interpreted goal:
  - move from a yellow `Price Freshness Preflight` warning to a more actionable diagnosis flow before re-running ingestion
- Result:
  - recommended and implemented a three-step operator flow:
    - stale warning
    - read-only diagnosis
    - explicit retry payload
  - added `Ingestion > Manual Jobs / Inspection > Price Stale Diagnosis`
  - the card combines:
    - DB latest daily price date
    - provider re-probe using `5d`, `1mo`, `3mo`
    - asset profile status summary
  - first-pass diagnosis labels:
    - `up_to_date_in_db`
    - `local_ingestion_gap`
    - `local_ingestion_gap_partial`
    - `provider_source_gap`
    - `provider_source_gap_or_symbol_issue`
    - `likely_delisted_or_symbol_changed`
    - `asset_profile_error`
    - `rate_limited_during_probe`
    - `inconclusive`
  - only `local_ingestion_gap`-class results generate a targeted `Daily Market Update` payload
  - backtest preflight now points users toward this diagnosis card when a stale warning remains yellow
- Durable output:
  - `.note/finance/phase8/PHASE8_PRICE_STALE_DIAGNOSIS_FIRST_PASS.md`

### 2026-03-29 - Statement shadow coverage gap drilldown
- Request topic:
  - when `Statement Shadow Coverage Preview` shows `Covered < Requested`, identify which symbols are missing and whether they need additional statement collection
- Interpreted goal:
  - turn the quarterly prototype preview from a passive metric block into an operator-facing action surface
- Result:
  - expanded `Statement Shadow Coverage Preview` with:
    - help popover
    - coverage gap metrics
    - `Coverage Gap Drilldown`
    - missing symbol table
    - recommended actions
    - targeted statement refresh payload
  - added two durable diagnosis labels:
    - `no_raw_statement_coverage`
    - `raw_statement_present_but_shadow_missing`
  - current interpretation:
    - `no_raw_statement_coverage`
      - strict raw statement ledger is missing
      - additional statement collection is the right next step
    - `raw_statement_present_but_shadow_missing`
      - raw statement rows exist
      - source collection is not the first suspect; shadow rebuild / coverage hardening is
  - validated on `US Statement Coverage 300` quarterly preview:
    - `Requested = 300`
    - `Covered = 100`
    - `Missing = 200`
    - all 200 missing symbols currently fall into `no_raw_statement_coverage`
- Durable output:
  - `.note/finance/phase8/PHASE8_STATEMENT_SHADOW_COVERAGE_GAP_DIAGNOSTICS.md`

### 2026-03-29 - Extended Statement Refresh quarterly shadow rebuild fix
- Request topic:
  - the user reran `Extended Statement Refresh` for a large quarterly universe, but `Quality Snapshot (Strict Quarterly Prototype)` still showed the same coverage gap
- Interpreted goal:
  - verify whether the operational refresh path actually updates the data source that `Statement Shadow Coverage Preview` reads
- Result:
  - confirmed the mismatch:
    - the preview reads quarterly statement shadow coverage from `nyse_fundamentals_statement`
    - the previous `Extended Statement Refresh` implementation refreshed raw statement ledgers only
    - so a successful quarterly refresh could still leave the preview unchanged
  - fixed `run_extended_statement_refresh(...)` so it now runs, for the selected `freq`:
    - raw statement collection
    - statement fundamentals shadow rebuild
    - statement factors shadow rebuild
  - smoke validation on `CRWD`:
    - before fix:
      - quarterly raw statement coverage existed
      - quarterly statement shadow rows = `0`
    - after fixed refresh:
      - quarterly statement shadow rows = `33`
- Durable output:
  - post-fix `Extended Statement Refresh` should now be interpreted as the correct operational recovery path for quarterly preview coverage gaps

### 2026-03-29 - Quarterly shadow preview slowness and low covered-count follow-up
- Request topic:
  - the user reported that `Statement Shadow Coverage Preview` was much slower than `Price Freshness Preflight` and that `Covered` still barely changed after a large quarterly refresh run
- Interpreted goal:
  - determine whether the issue was still broken ingestion, stale UI state, or simply legacy pre-fix raw-only refresh residue
- Result:
  - confirmed that the situation was a mix of three things:
    - many symbols had already been refreshed in the old raw-only path before the fix
    - preview cache was not cleared after statement-related jobs
    - coverage summaries were still computed with heavy Python-side grouping
  - direct inspection on `US Statement Coverage 500` quarterly now shows:
    - `Covered = 101`
    - `Missing = 399`
    - `Need Raw Collection = 3`
    - `Raw Exists / Shadow Missing = 396`
  - this means the current bottleneck is no longer raw statement collection for most symbols; it is legacy `raw present / shadow missing` residue from pre-fix runs
  - validated with symbol-level post-fix reruns:
    - `CME`: shadow rows `0 -> 73`
    - `MCK`: shadow rows `0 -> 73`
  - therefore the correct interpretation is:
    - the pipeline fix works
    - but large pre-fix quarterly runs need to be rerun once under the fixed `Extended Statement Refresh` path before `Covered` rises materially
- Durable output:
  - preview cache is now cleared after statement jobs
  - raw/shadow coverage summaries now use SQL aggregate queries instead of Python-side full-history grouping

### 2026-03-29 - Why the 500-symbol quarterly refresh barely changed coverage
- Request topic:
  - the user reported that after spending about 30 minutes on a `US Statement Coverage 500` quarterly `Extended Statement Refresh`, `Covered` only changed from `101` to `103`
- Interpreted goal:
  - verify whether the long run actually used the fixed shadow-rebuild path or whether the runtime was spent on the old raw-only path
- Result:
  - current post-fix coverage check shows:
    - `Covered = 103`
    - `Missing = 397`
    - `Need Raw Collection = 3`
    - `Raw Exists / Shadow Missing = 394`
  - run-history inspection of the user's 500-symbol job shows:
    - `started_at = 2026-03-29 11:03:02`
    - `duration_sec = 1506.713`
    - `symbols_requested = 500`
    - `step_jobs = []`
  - the empty `step_jobs` proves that this long run executed before the fixed three-stage path was active in the running app process
  - therefore the 30-minute runtime was mostly spent refreshing raw statement ledgers only, not rebuilding quarterly shadow coverage
  - this is consistent with the current bucket mix:
    - only `3` symbols still need raw collection
    - `394` symbols already have raw quarterly statements but still need the post-fix shadow rebuild path
- Durable output:
  - when a long quarterly refresh barely moves `Covered`, check whether the job record has `step_jobs = []`
  - if so, the server likely ran an old raw-only `Extended Statement Refresh` implementation and should be restarted before rerun

### 2026-03-29 - Ingestion UI simplification and utility-panel review
- Request topic:
  - remove redundant `Write Targets`, add fold/unfold behavior for run jobs, and review whether `Recent Logs` / `Failure CSV Preview` are actually useful and functioning
- Interpreted goal:
  - simplify the `Ingestion` surface before the next large rerun and leave a durable recommendation for additional operator-facing improvements
- Result:
  - removed the top-level `Write Targets` table because each run card already carries its own `Writes to:` description
  - converted run jobs to expander-based sections so the ingestion console is no longer one long fully expanded list
  - reviewed utility panels:
    - `Recent Logs`
      - functional
      - reads recent `logs/*.log` and renders tail preview
      - worth keeping
    - `Failure CSV Preview`
      - functional
      - but current operational value is limited because recent modern jobs do not consistently emit failure CSVs
      - more useful if failure artifacts are standardized later
  - documented follow-up recommendations:
    - runtime/build indicator
    - statement shadow rebuild-only helper
    - failure artifact standardization
- Durable output:
  - `.note/finance/phase8/PHASE8_INGESTION_UI_POLISH_AND_REVIEW.md`

### 2026-03-29 - Operator tooling implementation follow-up
- Request topic:
  - after the ingestion UI review, the user asked which recommended follow-up features should be built next and then requested that the top 1~5 operator improvements be implemented together
- Interpreted goal:
  - reduce operator confusion around old runtimes, shorten quarterly coverage recovery loops, and make long ingestion runs easier to inspect after the fact
- Result:
  - implemented a `Runtime / Build` indicator in `Ingestion` showing:
    - runtime marker
    - process loaded timestamp
    - git short SHA
  - added `Statement Shadow Rebuild Only`:
    - a manual helper that rebuilds statement shadow tables from existing raw ledgers without re-calling EDGAR
  - added coverage-gap action bridges from quarterly backtest preview:
    - raw-gap symbols -> `Extended Statement Refresh`
    - raw-present / shadow-missing symbols -> `Statement Shadow Rebuild Only`
  - added `Run Inspector` under persisted ingestion history so a selected run can be re-read with:
    - runtime metadata
    - pipeline steps
    - related log files
    - standardized artifact paths
  - standardized web-app run artifacts first pass:
    - every ingestion run now writes JSON artifacts under `.note/finance/run_artifacts/`
    - runs with symbol-level issues also write standardized `csv/*_failures.csv`
- Durable output:
  - `.note/finance/phase8/PHASE8_OPERATOR_RUNTIME_AND_SHADOW_REBUILD_TOOLING.md`
  - updated `PHASE8_TEST_CHECKLIST.md` with operator-tooling validation items

### 2026-03-29 - Coverage-missing symbol guidance for quarterly statement gaps
- Request topic:
  - when `Statement Shadow Coverage Preview` reports missing symbols such as `MRSH` and `AU`, the user wanted a feature that explains what to do next:
    - whether to run `Extended Statement Refresh`
    - whether `Statement Shadow Rebuild Only` is more appropriate
    - whether recollection is unlikely to help
- Interpreted goal:
  - turn quarterly coverage gaps from a passive warning into an operator decision aid with concrete next steps
- Result:
  - added `Statement Coverage Diagnosis` under `Ingestion > Manual Jobs / Inspection`
  - the card inspects:
    - DB strict raw statement coverage
    - DB statement shadow coverage
    - live EDGAR sample payload
  - it classifies each symbol into recovery buckets and emits:
    - recommended action
    - short note
    - stepwise guidance
  - quarterly backtest coverage drilldown can now prefill this diagnosis card directly
- Durable examples:
  - `MRSH`
    - source sample empty as well as DB coverage empty
    - classified as `source_empty_or_symbol_issue`
    - recommendation: validate symbol/source mapping first, not normal recollection
  - `AU`
    - source facts exist but mainly via `20-F` / `6-K`
    - classified as `foreign_or_nonstandard_form_structure`
    - recommendation: treat as foreign-form support/exclusion decision; recollection alone is unlikely to help
- Durable output:
  - `.note/finance/phase8/PHASE8_STATEMENT_COVERAGE_DIAGNOSIS_GUIDANCE.md`

### 2026-03-29 - Coarse vs fine diagnosis in quarterly coverage UI
- Request topic:
  - the user noticed that `Coverage Gap Drilldown` still showed `no_raw_statement_coverage` for symbols such as `MRSH`, `AU`, `GFS` and asked whether the finer labels should appear there
- Interpreted goal:
  - remove ambiguity between the first-pass coverage status table and the deeper per-symbol diagnosis card
- Result:
  - confirmed the intended two-stage model:
    - `Coverage Gap Drilldown` = coarse status only
    - `Statement Coverage Diagnosis` = fine-grained per-symbol cause classification
  - updated the backtest UI so the coarse table is labeled `Coverage Gap Status`
  - added bridge feedback so button clicks visibly confirm that symbols were loaded into the corresponding ingestion card
- Durable implication:
  - labels such as `source_empty_or_symbol_issue`, `foreign_or_nonstandard_form_structure`, and `source_present_raw_missing` belong to the dedicated diagnosis card, not to the initial coverage-gap table

### 2026-03-29 - Korean operator guidance for statement coverage diagnosis
- Request topic:
  - after confirming that real root-cause checks happen in `Statement Coverage Diagnosis`, the user asked for `Recommended Action` and `Stepwise Guidance` to be shown in Korean
- Interpreted goal:
  - reduce operator friction by keeping the actionable recovery text readable in the same language as the rest of the workflow
- Result:
  - localized the per-symbol operator guidance values to Korean
  - kept the visible result-table column labels in English
- Durable implication:
  - internal diagnosis keys remain English for stable program semantics, but operator-facing recovery text is now Korean

### 2026-03-29 - Phase 7 closeout and Phase 9/10 sequencing guidance
- Request topic:
  - the user reported that Phase 7 testing was largely complete, wanted Phase 7 wrapped up, and asked for guidance on what Phase 9 and Phase 10 should be
- Interpreted goal:
  - formalize Phase 7 closeout while preserving the ability to continue implementation-first work and batch-check later
- Result:
  - Phase 7 was moved from deferred-validation wording to closeout-complete wording
  - Phase 8 remains the active implementation surface with manual validation still pending
  - proposed next planned phases:
    - Phase 9: strict coverage policy and promotion gate
    - Phase 10: portfolio productization and research workflow
- Durable rationale:
  - Phase 9 should convert current diagnostics and coverage exceptions into official policy
  - Phase 10 should take the accumulated strategy / compare / weighted portfolio surfaces and turn them into a more product-like user workflow

### 2026-03-29 - Phase 9 kickoff
- Request topic:
  - after agreeing to keep Phase 8 QA for later batch review, the user asked to begin Phase 9
- Interpreted goal:
  - move from tooling implementation into policy / governance work without blocking on immediate QA completion
- Result:
  - Phase 9 was opened as the active phase
  - a current chapter board was added for:
    - strict coverage exception inventory
    - unsupported filing policy
    - promotion gate definition
    - operator decision policy
- Durable implication:
  - Phase 8 remains implementation-complete with deferred QA
  - Phase 9 is now the active workstream for converting current diagnostics into official strict coverage policy

### 2026-03-29 - Phase 9 plan concretization
- Request topic:
  - after reading the initial Phase 9 plan, the user asked for a more concrete explanation of what the phase would actually do
- Interpreted goal:
  - turn the Phase 9 note from a broad direction statement into an actionable chapter plan with a recommended default stance
- Result:
  - expanded the plan to include:
    - a provisional default policy
    - concrete chapter sequence
    - required decisions for the phase
    - recommended handling for current diagnosis buckets
- Provisional default stance:
  - `source_empty_or_symbol_issue` -> default excluded
  - `foreign_or_nonstandard_form_structure` -> default excluded
  - `raw_present_shadow_missing` -> eligible + shadow rebuild path
  - `source_present_raw_missing` -> review-needed + targeted recollection
  - quarterly family -> remain research-only throughout Phase 9

### 2026-03-29 - Current strict preset semantics vs historical monthly top-N
- Request topic:
  - the user asked whether symbols like `MRSH` / `AU` should really be removed from the whole run when the issue may only appear near the chosen end date, and whether `Coverage 1000` should reflect each historical month’s top-1000 instead of the current top-1000
- Interpreted goal:
  - clarify whether the current backtest is using a historically dynamic universe or a managed static preset, and whether that semantic is acceptable
- Result:
  - confirmed from code and current docs that the current strict preset is:
    - `run-level static preset + rebalance-date availability filtering`
  - this means:
    - a symbol is not globally removed just because it is stale near the final end date
    - if it has usable price/factor data at earlier rebalance dates, it can still participate then
  - however, preset membership itself is still based on the current managed universe, not each historical month’s top-N by market cap
- Durable implication:
  - current `Coverage 100/300/500/1000` should be interpreted as a managed research preset, not as a fully historical point-in-time top-N universe
  - if a true historical monthly top-N universe is desired, it should be introduced as a separate future mode rather than silently reinterpreting the current preset

### 2026-03-29 - Recommended work order for a real-investing target
- Request topic:
  - the user asked how the project should proceed if the long-term goal is to use the backtest program for real investing, not just prototyping
- Interpreted goal:
  - define a practical and professionally defensible execution order between strict coverage policy work, portfolio productization, and any future universe work
- Result:
  - documented the recommendation that:
    - Phase 9 should first lock policy / governance / promotion gate
    - the next major engineering priority should be a separate `historical dynamic PIT universe` mode
    - portfolio productization should come after that, not before
- Durable rationale:
  - current strict coverage presets are still `managed static research universe` contracts
  - this is useful for research and operator tooling, but not strong enough as the final real-money validation contract
  - therefore the most professional path is:
    - freeze the current mode semantics
    - build a true dynamic PIT universe mode
    - only then expand product workflow surfaces as deployment-grade research tooling

### 2026-03-29 - Phase 9 policy first-pass locked
- Request topic:
  - after agreeing to keep the project focused on a real-investing target, the user asked to proceed with Phase 9 as defined and include a checklist
- Interpreted goal:
  - convert the current diagnostics/operator work into durable policy docs that define:
    - strict coverage exception handling
    - promotion gate
    - operator decision flow
    - a review checklist
- Result:
  - added the following Phase 9 document set:
    - `PHASE9_STRICT_COVERAGE_EXCEPTION_INVENTORY.md`
    - `PHASE9_STRICT_COVERAGE_POLICY_DECISION.md`
    - `PHASE9_STRICT_FAMILY_PROMOTION_GATE.md`
    - `PHASE9_OPERATOR_DECISION_TREE.md`
    - `PHASE9_TEST_CHECKLIST.md`
  - confirmed from current preset diagnostics that active quarterly coverage gaps are dominated by:
    - `source_empty_or_symbol_issue`
    - `foreign_or_nonstandard_form_structure`
- Durable implication:
  - current strict preset governance should treat structural buckets as default exclusion, not as simple recollection gaps
  - `strict annual family` remains the leading public-candidate research family
  - `strict quarterly family` remains research-only during Phase 9
  - after Phase 9 policy lock, the recommended next engineering priority remains `historical dynamic PIT universe`

### 2026-03-29 - Batch QA across Phase 8 / 9 / 10 is acceptable
- Request topic:
  - the user asked whether Phase 9 checklist validation could be deferred and later reviewed together with Phase 8 and Phase 10 after more implementation is finished
- Interpreted goal:
  - keep development moving now and batch manual QA later without losing phase discipline
- Result:
  - confirmed that this is acceptable for the current workflow
  - the recommended operating mode is:
    - keep Phase 8 as implementation-complete / validation pending
    - keep Phase 9 as policy-first / validation pending
    - review Phase 8 / 9 / 10 checklists together after Phase 10 work is ready
- Durable tradeoff:
  - this is efficient and fits the current implementation-first pace
  - if a regression appears later, it may take slightly more effort to attribute it to Phase 8 vs 9 vs 10

### 2026-03-29 - Phase 10 prepared without activation
- Request topic:
  - the user asked to prepare Phase 10 and report back before actually entering the workstream
- Interpreted goal:
  - keep Phase 10 ready-to-open with a concrete execution order and a later batch-review checklist, while preserving the current phase order
- Result:
  - added:
    - `PHASE10_CURRENT_CHAPTER_TODO.md`
    - `PHASE10_EXECUTION_PREPARATION.md`
    - `PHASE10_TEST_CHECKLIST.md`
  - clarified that Phase 10 remains `planned`, but is now preparation-complete from a documentation standpoint
- Durable implication:
  - when Phase 10 opens later, the recommended implementation order is:
    - saved portfolio contract
    - compare-to-portfolio bridge
    - saved portfolio UI first pass
    - richer portfolio readouts
    - workflow integration
  - the checklist is already ready for later batch QA with Phase 8 and Phase 9

### 2026-03-29 - Historical dynamic PIT universe is not Phase 10
- Request topic:
  - the user asked whether `historical dynamic PIT universe` would be built inside Phase 10 or only prepared
- Interpreted goal:
  - remove ambiguity between the next validation-critical workstream and the separate productization phase
- Result:
  - clarified that `historical dynamic PIT universe` is **not** the content of Phase 10
  - Phase 10 remains the portfolio productization / workflow phase
  - `historical dynamic PIT universe` should be treated as a **separate next major workstream**, and if the project keeps prioritizing real-money validation, it should come **before** Phase 10 activation
- Durable implication:
  - current Phase 10 docs are only preparation for future productization
  - if the team follows the real-money-first priority, the next actual implementation phase should be the dynamic PIT universe phase, not Phase 10

### 2026-03-29 - Phase numbering reordered around dynamic PIT priority
- Request topic:
  - the user asked for a practical recommendation and explicitly asked not to lose sight of the fact that the project should eventually implement a real-world usable `historical dynamic PIT universe`
- Interpreted goal:
  - align the planned phase numbering with the recommended execution order instead of leaving productization ahead of the validation-critical universe work
- Result:
  - reordered the planned phases so that:
    - `Phase 10` now refers to `historical dynamic PIT universe`
    - `Phase 11` now refers to portfolio productization / research workflow
  - moved the previously prepared productization docs into `phase11/`
  - created the new Phase 10 planning set for dynamic PIT:
    - `PHASE10_HISTORICAL_DYNAMIC_PIT_UNIVERSE_PLAN.md`
    - `PHASE10_CURRENT_CHAPTER_TODO.md`
    - `PHASE10_TEST_CHECKLIST.md`
- Durable implication:
  - the roadmap now matches the real-money-first recommendation directly
  - if the team continues on this path, the next true implementation phase after Phase 9 should be Phase 10 dynamic PIT universe

### 2026-03-29 - Dynamic PIT first-pass should start from annual strict using current DB ingredients
- Request topic:
  - after agreeing to proceed with the dynamic PIT direction, the user asked to continue with the next concrete planning step
- Interpreted goal:
  - move from “dynamic PIT should come next” to “what exact first-pass implementation path is realistic with the current code and schema”
- Result:
  - documented a more concrete first-pass recommendation:
    - do not replace the current static preset mode
    - open a separate dynamic PIT mode
    - begin with `strict annual family`, not quarterly
    - use rebalance-date approximate PIT market-cap membership built from:
      - historical price history
      - latest-known statement `shares_outstanding`
  - also documented the current schema gap:
    - `nyse_asset_profile` is only a current snapshot and is not enough as a historical universe source by itself
- Durable implication:
  - the realistic next implementation is not a perfect constituent-history engine from day one
  - it is an additive annual-first dynamic PIT mode that improves the universe contract materially while staying compatible with the current DB design

### 2026-03-29 - Annual strict single-strategy dynamic PIT first pass was implemented
- Request topic:
  - the user asked to stop preparing and actually start Phase 10 development
- Interpreted goal:
  - open the first real `historical dynamic PIT universe` implementation path without breaking the existing static strict-annual contract
- Result:
  - implemented an additive annual strict single-strategy first pass:
    - `Quality Snapshot (Strict Annual)`
    - `Value Snapshot (Strict Annual)`
    - `Quality + Value Snapshot (Strict Annual)`
  - added `Universe Contract` in the annual strict forms:
    - `Static Managed Research Universe`
    - `Historical Dynamic PIT Universe`
  - dynamic PIT first pass now:
    - keeps the static preset path unchanged
    - rebuilds rebalance-date membership from a candidate pool
    - uses rebalance-date close * latest-known annual `shares_outstanding`
  - result/meta now expose:
    - `Universe Membership Count`
    - `Universe Contract`
    - `universe_contract`
    - `dynamic_candidate_count`
    - `dynamic_target_size`
    - `universe_debug`
  - history/prefill for annual strict single-strategy runs now carries `universe_contract`
- Durable implication:
  - the project now has a real implemented Phase 10 first pass, not just a planning set
  - the current contract is still approximate PIT, annual-only, and single-strategy only
  - compare / quarterly / perfect constituent-history remain later passes

### 2026-03-29 - Dynamic PIT preflight was corrected for late listings
- Request topic:
  - preset-based dynamic PIT smoke showed that current managed 1000 candidate pools contain symbols without full-range historical price data
- Interpreted goal:
  - make the dynamic PIT contract behave like an evolving rebalance-date universe builder rather than a static full-history validator
- Result:
  - annual strict dynamic runtime no longer requires every candidate symbol to have price history from the requested start date
  - the dynamic candidate pool now only requires usable DB price history up to the selected end date
  - symbols without such price history are surfaced as natural exclusions via warnings/meta instead of causing a hard failure
  - preset smoke confirmed:
    - `dynamic_candidate_count = 1000`
    - `universe_debug.candidate_pool_count = 921`
    - first `Universe Membership Count = 100`
- Durable implication:
  - the first-pass dynamic PIT mode now better matches a real evolving-universe contract
  - it is still approximate PIT, but it no longer blocks on a static full-range price-history assumption

### 2026-03-29 - Annual strict compare mode was extended to dynamic PIT first pass
- Request topic:
  - after implementing single-strategy dynamic PIT, the next practical hardening target was making compare mode usable under the same contract
- Interpreted goal:
  - avoid a validation workflow where dynamic PIT can only be tested one strategy at a time
- Result:
  - extended annual strict compare blocks to expose `Universe Contract`
  - compare overrides now pass:
    - `universe_contract`
    - `dynamic_candidate_tickers`
    - `dynamic_target_size`
  - compare readout now surfaces dynamic contract interpretation via:
    - `Universe Contract`
    - `Dynamic Candidate Pool`
    - `Membership Avg`
    - `Membership Range`
  - smoke validation confirmed that annual strict compare overrides reach runtime with `historical_dynamic_pit`
- Durable implication:
  - Phase 10 first pass now supports both single-strategy and compare-level annual strict dynamic validation
  - quarterly / perfect constituent-history still remain later passes

### 2026-03-29 - Dynamic PIT second pass was hardened around continuity, persistence, and quarterly extension
- Request topic:
  - after the first-pass annual dynamic PIT surface was opened, the user asked to continue hardening in this order:
    1. listing / delisting / symbol continuity second pass
    2. dynamic universe snapshot persistence
    3. quarterly family dynamic PIT expansion
    4. perfect constituent-history source reinforcement
- Interpreted goal:
  - make the dynamic PIT contract more usable for real-money style validation without pretending that perfect constituent history already exists
- Result:
  - added continuity diagnostics into `universe_debug`:
    - `continuity_ready_count`
    - `pre_listing_excluded_count`
    - `post_last_price_excluded_count`
    - `asset_profile_delisted_count`
    - `asset_profile_issue_count`
  - added candidate-level status rows:
    - `first_price_date`
    - `last_price_date`
    - `price_row_count`
    - `profile_status`
    - `profile_delisted_at`
    - `profile_error`
  - added history artifact persistence for dynamic runs:
    - `dynamic_universe_artifact`
    - `dynamic_universe_preview_rows`
    - snapshot json under `.note/finance/backtest_artifacts/`
  - extended the same `historical_dynamic_pit` contract to quarterly strict prototype family:
    - `Quality Snapshot (Strict Quarterly Prototype)`
    - `Value Snapshot (Strict Quarterly Prototype)`
    - `Quality + Value Snapshot (Strict Quarterly Prototype)`
    - single-strategy and compare first pass both validated
  - kept the contract boundary explicit:
    - this is still `approximate PIT + diagnostics`
    - `asset_profile` remains diagnostic only
    - licensed perfect constituent-history is still a later step
- Durable implication:
  - Phase 10 dynamic PIT is no longer annual-only in practice
  - the project now persists enough universe-state detail to re-open a run and inspect membership drift later
  - real-money interpretation should prioritize this dynamic contract over static mode, but still treat it as an approximation rather than a perfect historical constituent engine

### 2026-03-30 - Phase 8 checklist was refreshed to include Phase 9/10 surface changes
- Request topic:
  - before starting delayed QA, the user wanted the Phase 8 checklist rewritten because Phase 9 and 10 had changed parts of the same quarterly/operator surface
- Interpreted goal:
  - keep the original Phase 8 validation target, but remove stale assumptions that would make the checklist misleading on the current UI
- Result:
  - rewrote `PHASE8_TEST_CHECKLIST.md` to treat Phase 8 QA as:
    - quarterly strict prototype family still works as `research-only`
    - later Phase 9/10 additions did not break that surface
  - added current expectations for:
    - quarterly `Universe Contract` visibility
    - history/prefill carrying `Universe Contract`
    - coarse `Coverage Gap Status` vs fine `Statement Coverage Diagnosis`
    - operator runtime/rebuild/inspector tooling
    - optional quarterly dynamic PIT regression smoke
- Durable implication:
  - Phase 8 QA should now be read as “current-code quarterly surface validation,” not as a frozen snapshot of the original Phase 8 UI

### 2026-03-30 - Phase 8 QA surfaced a history date-filter bug and ambiguous Load Into Form UX
- Request topic:
  - while running Phase 8 QA, the user reported:
    - `Persistent Backtest History` crashed when only the start of `Recorded Date Range` was selected
    - `Load Into Form` did not make it obvious where the loaded values appeared
    - the Backtest header area felt noisy and English-heavy
- Interpreted goal:
  - fix the actual crash, and make the history-to-form workflow understandable without requiring the user to infer hidden tab state
- Result:
  - fixed history date-range normalization so partial date selection no longer crashes
  - `Load Into Form` now automatically moves the Backtest panel to `Single Strategy`
  - the target screen shows a short Korean summary of the loaded inputs, including universe contract when present
  - replaced the old top-of-page phase/planning blocks with a shorter Korean usage guide
  - clarified two confusing terms in the UI flow:
    - `quarterly strict prototype` = current research-only quarterly strategy surface
    - `late active start` = the strategy does not enter immediately at the requested start because usable statement shadow coverage appears later
- Durable implication:
  - Phase 8 QA is now less dependent on remembering hidden UI state
  - the history workflow is closer to an operator tool rather than an internal dev-only convenience

### 2026-03-30 - Phase 9 real-money validation direction terms were clarified
- Request topic:
  - the user asked what several Phase 9 planning terms actually mean in practical finance/backtest terms:
    - `universe contract`
    - `survivorship / universe drift`
    - `diagnostics bucket -> eligible / review_needed / excluded`
    - `foreign / non-standard form issuer`
    - `portfolio productization`
- Interpreted goal:
  - make the Phase 9 guidance document understandable enough that policy review can happen without guessing at internal jargon
- Result:
  - expanded `PHASE9_REAL_MONEY_VALIDATION_DIRECTION.md` with a dedicated glossary-style section
  - defined `universe contract` as the full rule set for which symbols are in the backtest and when
  - separated `survivorship` from `universe drift` and explained why both matter for real-money validation
  - explained `diagnostics bucket` as a root-cause class that then maps to policy state:
    - `eligible`
    - `review_needed`
    - `excluded`
  - explained `foreign / non-standard form issuer` in the current strict statement context as issuers using forms such as `20-F`, `6-K`, `40-F`
  - explained `portfolio productization` as workflow/UI packaging rather than a stricter validation contract
- Durable implication:
  - the Phase 9 doc now reads more like a policy reference and less like shorthand internal notes
  - this should reduce ambiguity before the user reviews Phase 9 governance decisions

### 2026-03-30 - Remaining universe semantics / PIT validation work was clarified as Phase 10 scope
- Request topic:
  - after reading the Phase 9 direction docs, the user asked whether unfinished `universe semantics / historical point-in-time validation` means the work is still incomplete, and whether that remaining work belongs to Phase 11
- Interpreted goal:
  - clearly separate unfinished validation-contract work from later productization work
- Result:
  - clarified that the project already has an implemented `Historical Dynamic PIT Universe` first/second pass
  - clarified that the unfinished part is the **perfect / stronger PIT reinforcement** side:
    - stronger listing / delisting source
    - better symbol continuity source
    - closer-to-perfect constituent-history reinforcement
  - clarified that these remaining items still belong to **Phase 10**, not Phase 11
  - clarified that `Phase 11` is portfolio productization and workflow expansion, not universe-contract hardening
- Durable implication:
  - the roadmap should be read as:
    - Phase 10 = dynamic PIT validation contract hardening
    - Phase 11 = portfolio productization

### 2026-03-31 - Phase 10 QA clarification: dynamic PIT outputs and compare slowness
- Request topic:
  - during Phase 10 testing, the user asked what `dynamic run`, `dynamic_universe_preview_rows`, `dynamic_universe_artifact`, and continuity/profile diagnostics actually mean, and reported that annual strict compare with dynamic PIT felt too slow
- Interpreted goal:
  - make dynamic PIT runs self-explanatory in the UI/history and reduce avoidable repeated work in compare execution
- Result:
  - clarified the checklist contract: a `dynamic run` means `Universe Contract = Historical Dynamic PIT Universe`
  - added a dedicated `Dynamic Universe` tab in single-run results so:
    - `dynamic_universe_snapshot_rows`
    - `dynamic_candidate_status_rows`
    are directly visible from the run result
  - clarified history artifact semantics:
    - `dynamic_universe_preview_rows` = quick per-date membership preview stored inside history context
    - `dynamic_universe_artifact` = metadata for the separately persisted JSON artifact on disk
  - fixed quarterly quality dynamic metadata scope labeling so it now reflects `quarterly_first_pass`
  - added small in-process caches for repeated dynamic PIT compare inputs shared across strategies
- Durable implication:
  - Phase 10 dynamic PIT runs are now easier to interpret without opening raw JSON first
  - compare performance should improve for repeated strict annual/quarterly runs with shared candidate pools, though larger optimization may still be needed later if candidate pools keep growing

- Follow-up fix: `Load Into Form` no longer writes directly to `backtest_active_panel` after widget instantiation; it now uses a deferred `backtest_requested_panel` handoff applied at state init.

### 2026-03-31 - Phase 10 was closed as a practical dynamic-PIT completion
- Request topic:
  - the user asked to wrap up Phase 10 after the recent QA fixes and dynamic PIT hardening
- Interpreted goal:
  - close Phase 10 without overstating current PIT fidelity, and prepare the next workflow phase cleanly
- Result:
  - created `PHASE10_COMPLETION_SUMMARY.md` and `PHASE10_NEXT_PHASE_PREPARATION.md`
  - marked Phase 10 as practical closeout in roadmap/TODO/index
  - clarified that current dynamic PIT should be read as `approximate PIT + diagnostics`, not perfect constituent-history
  - clarified that the next natural phase is Phase 11 portfolio productization/workflow
- Durable implication:
  - Phase 10 is now documented as complete enough for handoff, while stronger constituent-history reinforcement remains a longer-term backlog rather than an immediate phase blocker

### 2026-03-31 - Phase 11 was opened as saved-portfolio productization first pass
- Request topic:
  - after Phase 10 closeout, the user asked to start Phase 11
- Interpreted goal:
  - begin portfolio productization from the most reusable workflow unit rather than from broader visualization polish
- Result:
  - opened Phase 11 as the active phase
  - chose `saved portfolio contract + load/rerun workflow` as the first implementation slice
  - added a dedicated saved-portfolio store at `.note/finance/SAVED_PORTFOLIOS.jsonl`
  - added `Saved Portfolios` UI under `Compare & Portfolio Builder`
  - implemented:
    - save current weighted portfolio
    - load saved portfolio into compare
    - rerun saved portfolio end-to-end
    - delete saved portfolio
  - added weighted portfolio meta/context readout and saved-portfolio linkage in history context
- Durable implication:
  - Phase 11 should now be read as `in_progress`
  - the project has moved from one-off compare/builder usage into a repeatable saved-portfolio workflow
  - richer portfolio readouts and in-place editing remain later Phase 11 backlog, not first-pass blockers

### 2026-03-31 - Playwright-based public market research framework
- Request topic:
  - whether Playwright can be used to investigate market/institution-themed research topics such as stock screening, DCF valuation, earnings analysis, portfolio construction, technical analysis, dividend research, competitor analysis, pattern detection, and macro impact assessment
- Interpreted goal:
  - define a repeatable public-source research workflow and store it as a durable markdown playbook for future market-investigation tasks
- Result:
  - reframed institution names as research themes rather than claims about proprietary internal methods
  - defined a common three-stage workflow:
    - source mapping / collection
    - structured parsing / normalization
    - synthesis / validation memo
  - mapped the user's requested themes to official/public sources such as:
    - SEC EDGAR
    - company investor-relations earnings pages
    - NYSE listings
    - iShares holdings pages
    - Harvard Management Company annual reports
    - FRED / BLS / BEA / Federal Reserve Beige Book
    - Cboe VIX resources
  - documented that Playwright is most useful for dynamic pages and evidence capture, while direct APIs/downloads remain preferable when official machine-readable sources exist
- Durable output:
  - `.note/finance/PLAYWRIGHT_MARKET_RESEARCH_PLAYBOOK_20260331.md`

### 2026-04-01 - Playwright research playbook was strengthened beyond the original three-step flow
- Request topic:
  - whether the original three-step research flow should be extended with additional stages or mandatory considerations for repeated market-investigation work
- Interpreted goal:
  - harden the playbook so future repeated research runs are more defensible, point-in-time aware, and reproducible
- Result:
  - kept the original three-step flow as the lightweight core:
    - source mapping
    - structured parsing
    - synthesis
  - added an operational five-stage reinforcement model for repeated research:
    - research brief / decision contract
    - source mapping
    - structured parsing
    - synthesis
    - validation / contradiction review / refresh planning
  - added durable guardrails around:
    - filing-time vs acceptance-time handling
    - CIK/accession-based entity identity instead of ticker-only handling
    - macro vintage / revision awareness
    - official-source precedence over flattened secondary datasets
    - API-first collection with browser automation used mainly for dynamic pages and evidence capture
    - SEC fair-access/rate-limit compliance
    - Playwright trace/download preservation
    - contradiction logging and refresh cadence
- Durable output:
  - updated `.note/finance/PLAYWRIGHT_MARKET_RESEARCH_PLAYBOOK_20260331.md`

### 2026-04-04 - Research workflow was clarified as collection -> storage -> rule-based analysis, with staged exceptions
- Request topic:
  - before proceeding further, the user asked whether the overall workflow should be understood as collecting data, storing it in the DB, and then analyzing it according to project-defined rules
- Interpreted goal:
  - clarify the practical operating model connecting Playwright/public-source research work with the existing `finance` package architecture
- Result:
  - confirmed that the default long-term workflow should be read as:
    - collect from public sources
    - normalize and persist what is worth reusing
    - analyze with explicit project rules
  - clarified that not every exploratory item needs to be persisted to MySQL first
  - separated three practical modes:
    - one-off exploration: quick note-first review, optional DB persistence later
    - repeated research: persist normalized/source-traceable data for reuse and comparison
    - productionized research/backtest workflow: DB-first, rule-based analysis, reproducible outputs
  - clarified that Playwright is a collection/evidence layer, not the analysis logic itself
  - clarified that the DB matters mainly for repeatability, point-in-time control, cross-run comparison, and downstream rule/backtest integration
- Durable implication:
  - future market-research work in this repo should generally move toward `source -> normalized storage -> rule-based analysis`, while allowing lightweight note-first exploration before deciding whether a source deserves durable persistence

### 2026-04-04 - Current status was clarified as playbook-ready, not research-executed
- Request topic:
  - whether the work so far should be understood as not having performed actual market research yet
- Interpreted goal:
  - distinguish between framework/design completion and real research-run execution
- Result:
  - clarified that the repo currently has:
    - a research playbook
    - process/guardrail definitions
    - source ideas and categorization
  - clarified that it does not yet have:
    - a real topic-specific research run
    - collected source artifacts for a chosen case
    - normalized research data persisted for that case
    - an actual analytical conclusion produced from a live run
- Durable implication:
  - the project should currently be read as `research-ready` rather than `research-already-executed`

### 2026-04-04 - Public source map for famous US institutions, funds, and investors
- Request topic:
  - investigate where the public portfolios and disclosed strategies of famous US institutions, funds, related vehicles, and notable investors can actually be found using web browsing / Playwright
- Interpreted goal:
  - define the practical discovery layer before any deeper collection, DB persistence, or rule-based analysis begins
- Result:
  - identified the core public disclosure stack as:
    - SEC 13F for institutional long US-listed holdings
    - SEC 13D / 13G for >5% beneficial ownership and activist-style positions
    - SEC N-PORT for registered fund / ETF portfolio disclosures
    - official fund/manager websites for portfolio pages, factsheets, methodology, annual reports, monthly reports, and investor letters
  - documented representative official sources for names such as:
    - Berkshire Hathaway / Warren Buffett
    - Pershing Square / Bill Ackman
    - Bridgewater / Ray Dalio
    - Third Point / Dan Loeb
    - Icahn Enterprises / Carl Icahn
    - Renaissance Technologies
    - BlackRock / iShares
    - ARK Invest / Cathie Wood
    - Harvard Management Company
  - clarified that disclosure quality differs materially by manager:
    - Berkshire / Pershing / ARK / iShares are comparatively open
    - Bridgewater / Renaissance are much more limited
  - clarified that 13F should not be treated as a full portfolio view because it omits major parts of many managers’ books
- Durable output:
  - `.note/finance/US_PUBLIC_PORTFOLIO_AND_STRATEGY_SOURCE_MAP_20260404.md`

### 2026-04-01 - Phase 12 should focus on promoting existing strategies toward real-money use
- Request topic:
  - after Phase 11 testing, the user asked to open a new phase centered on making current strategies usable for real-world investing rather than leaving them at prototype level
- Interpreted goal:
  - do not prioritize adding many new strategies; instead, identify which current strategy families can realistically be hardened for real-money use and define the promotion order and contract
- Result:
  - closed Phase 11 at the `saved portfolio workflow first pass` level and opened Phase 12 as the new active phase
  - fixed Phase 12 around:
    - strategy production audit
    - real-money promotion contract
    - ETF strategy hardening first
    - strict annual family promotion second
    - quarterly strict prototype family hold
  - classified current strategy families as:
    - production-priority: `GTAA`, `Dual Momentum`, `Risk Parity Trend`, strict annual family
    - baseline/reference: `Equal Weight`, broad `Quality Snapshot`
    - research-only/hold: quarterly strict prototype family
- Durable implication:
  - Phase 12 is not a new-strategy expansion phase
  - it is a `real-money strategy promotion` phase focused on investability, turnover/cost, portfolio guardrails, and validation surface
  - quarterly strict prototype family should remain explicitly out of promotion scope for now

### 2026-04-01 - Phase 12 promotion contract terminology was clarified in plain language
- Request topic:
  - the user asked for easier explanations of the `공통 계약 축` items in the Phase 12 real-money promotion contract
- Interpreted goal:
  - keep the policy structure, but make each axis understandable without requiring prior familiarity with quant/backtest terminology
- Result:
  - updated `PHASE12_REAL_MONEY_PROMOTION_CONTRACT.md`
  - added plain-language meaning and “why this matters” notes for:
    - universe / data contract
    - investability filter
    - turnover / transaction cost
    - portfolio guardrail
    - validation surface
- Durable implication:
  - the Phase 12 contract document should now be read as both a policy document and an operator-facing explanation of why real-money strategy hardening needs each axis

### 2026-04-01 - Future phase/policy documents should default to plain-language explanation blocks
- Request topic:
  - the user asked that future phase documents use the same easier explanatory style when documenting policy or real-money concepts
- Interpreted goal:
  - convert a one-off wording preference into a durable repo guidance rule so future phase documents are easier to read without extra chat explanation
- Result:
  - updated `AGENTS.md`
  - added a documentation rule that phase plans, policy docs, validation rules, and real-money guidance docs should include short plain-language explanations for key terms
  - recommended pattern:
    - what this means
    - why it matters
- Durable implication:
  - future phase documents should keep technical precision while remaining understandable on first pass for the operator/user

### 2026-04-01 - Phase 12 strategy promotion plan was also rewritten with easier explanations
- Request topic:
  - the user asked whether `PHASE12_REAL_MONEY_STRATEGY_PROMOTION_PLAN.md` could be rewritten so its terms and chapter plan are easier to understand
- Interpreted goal:
  - apply the same plain-language documentation standard not just to the contract doc, but also to the higher-level phase plan
- Result:
  - updated `PHASE12_REAL_MONEY_STRATEGY_PROMOTION_PLAN.md`
  - added plain-language explanation blocks around:
    - the phase goal
    - strategy classification meaning
    - key terms such as audit / promotion / hardening / dynamic PIT
    - chapter-by-chapter intent
    - the reasoning behind the recommended implementation order
- Durable implication:
  - the Phase 12 plan should now be readable as a practical roadmap for the user/operator, not only as an internal planning note

### 2026-04-01 - A dedicated terminology section was added to the Phase 12 strategy promotion plan
- Request topic:
  - the user asked to organize and clarify the recurring terms used in the Phase 12 plan itself
- Interpreted goal:
  - make the plan document self-contained so key planning words do not require separate explanation in chat
- Result:
  - updated `PHASE12_REAL_MONEY_STRATEGY_PROMOTION_PLAN.md`
  - added a dedicated terminology section covering the repeated planning terms used across the document
- Durable implication:
  - the Phase 12 plan should now serve as both a roadmap and a small glossary for the planning vocabulary used in the phase

### 2026-04-01 - A dedicated terminology section was added to the Phase 12 promotion contract
- Request topic:
  - the user asked to organize and clarify the recurring terms used in the real-money strategy common contract
- Interpreted goal:
  - avoid repeated ambiguity by adding a glossary directly into the contract doc rather than explaining terms only in chat
- Result:
  - updated `PHASE12_REAL_MONEY_PROMOTION_CONTRACT.md`
  - added a dedicated terminology section covering the repeated terms used across the common promotion contract
- Durable implication:
  - the contract document should now work as a self-contained reference for both the meaning of each contract axis and the vocabulary used to describe it

### 2026-04-01 - Phase 12 ETF real-money hardening first pass was implemented
- Request topic:
  - after Phase 12 kickoff, begin the first real implementation slice aimed at making current strategies more usable for real-money interpretation
- Interpreted goal:
  - harden the ETF strategy family first, before strict annual family, by adding the minimum common contract needed for practical interpretation
- Result:
  - implemented ETF first-pass hardening for:
    - `GTAA`
    - `Risk Parity Trend`
    - `Dual Momentum`
  - added real-money inputs to the UI:
    - `Minimum Price`
    - `Transaction Cost (bps)`
    - `Benchmark Ticker`
  - added strategy-level `min_price` filtering
  - added runtime gross-vs-net post-processing with turnover and estimated transaction cost
  - added single-ticker benchmark overlay and summary
  - added single-strategy `Real-Money` tab and compare-level real-money readout
  - synced history / prefill / compare override / saved portfolio compare context for the new fields
- Durable implication:
  - ETF strategies are now no longer "run-only" surfaces; they have a first-pass real-money interpretation contract
  - this is still a first pass, not a full institutional execution model
  - stronger investability, rolling underperformance guardrails, and richer benchmark contracts remain later-pass work

### 2026-04-01 - Phase 12 ETF metric meaning and strict-annual test expectation were clarified
- Request topic:
  - while testing Phase 12, the user asked what `Turnover`, `Gross Total Balance`, `Estimated Cost`, and `Cumulative Estimated Cost` mean, and also flagged that strict annual surfaces did not show the same real-money fields
- Interpreted goal:
  - remove ambiguity in the new ETF real-money metrics and make it explicit whether strict annual missing fields are a bug or simply not implemented yet
- Result:
  - documented the ETF result-table metric reading guide directly in `PHASE12_ETF_REAL_MONEY_HARDENING_FIRST_PASS.md`
  - updated `PHASE12_TEST_CHECKLIST.md` so the strict annual section clearly says those real-money fields are still a later target and their absence is currently expected
- Durable implication:
  - Phase 12 testing now distinguishes ETF first-pass implemented behavior from strict annual future-work items more clearly

### 2026-04-01 - Added a dedicated cross-phase finance term glossary
- Request topic:
  - the user asked for a shared markdown file that collects recurring quant, backtest, and strategy terminology in one place
- Interpreted goal:
  - keep a durable single source of truth for easy term explanations so future phase documents do not need to re-explain the same terms ad hoc
- Result:
  - added `.note/finance/FINANCE_TERM_GLOSSARY.md`
  - seeded it with current recurring terms and explanations using:
    - `기본 설명`
    - `왜 사용되는지`
    - `예시 / 필요 상황`
  - updated `AGENTS.md` so future recurring terms should be added there
  - updated `FINANCE_DOC_INDEX.md` so the glossary is discoverable from the top-level finance index
- Durable implication:
  - future phase plans, policy documents, and validation guides can keep short plain-language explanations locally while accumulating repeated term definitions in the shared glossary

### 2026-04-02 - GTAA default commodity sleeve was changed from DBC to PDBC
- Request topic:
  - the user asked to replace `DBC` with `PDBC` in GTAA because they want to evaluate the strategy with a more comfortable practical default for real-money use
- Interpreted goal:
  - change the current GTAA default universe and sample baseline without making broader claims about current tax treatment or ETF provider policy
- Result:
  - updated the GTAA preset/default ticker set from `DBC` to `PDBC`
  - synced the change across:
    - Backtest GTAA preset
    - compare defaults
    - manual GTAA ticker default text
    - direct/db GTAA sample entrypoints
  - documented the change in the Phase 12 ETF hardening note and the finance comprehensive analysis
- Durable implication:
  - GTAA should now be read as using `PDBC` as the default commodity sleeve in current UI/sample paths
  - prior run-history artifacts may still show `DBC` because they are historical records, not current defaults

### 2026-04-02 - GTAA execution failure after the PDBC swap was traced to missing historical DB coverage
- Request topic:
  - after replacing `DBC` with `PDBC`, the user reported that GTAA failed with `공통 Date가 없습니다.`
- Interpreted goal:
  - determine whether the issue came from GTAA logic or from the current data state
- Result:
  - traced the exception to `finance.transform.align_dfs_by_date_intersection(...)`
  - confirmed that current DB coverage for `PDBC` is only a short recent window:
    - first date in DB: `2026-03-02`
    - last date in DB: `2026-03-31`
    - row count: `22`
  - the rest of the GTAA tickers have multi-year history, so the failure is caused by the GTAA universe no longer having a usable common date intersection for runs that expect older shared history
- Durable implication:
  - current GTAA default universe now depends on `PDBC`, but historical GTAA execution will fail until `PDBC` has sufficient backfilled DB price history
  - the issue is a data-coverage problem, not a GTAA strategy-rule bug

### 2026-04-02 - Daily Market Update custom symbol path still exists, but PDBC needs backfill rather than a routine short refresh
- Request topic:
  - the user asked whether collecting more data would fix the GTAA `PDBC` issue and whether the `Daily Market Update` custom path had disappeared
- Interpreted goal:
  - clarify the current operator path for targeted one-symbol price collection and explain what kind of collection is needed to resolve the GTAA intersection failure
- Result:
  - confirmed that `Daily Market Update` still supports custom symbols through:
    - `Daily Market Symbols Source = Manual`
    - `Daily Market Symbols Preset = Custom`
    - then entering the ticker in the text area
  - clarified that the current GTAA failure is not fixed by a normal short daily refresh
  - `PDBC` needs historical backfill over a long enough date range so it overlaps with the other GTAA tickers
- Durable implication:
  - for a newly introduced default ETF in a long-history strategy universe, routine daily refresh is insufficient unless historical coverage already exists
  - operator guidance should distinguish `daily refresh` from `historical backfill`

### 2026-04-02 - GTAA now provides both PDBC default and DBC comparison presets
- Request topic:
  - after seeing a large performance difference, the user asked whether GTAA could also expose a preset using `DBC`
- Interpreted goal:
  - preserve `PDBC` as the current default while making `DBC` easy to compare without manual ticker editing
- Result:
  - kept `GTAA Universe` as the current `PDBC`-based default preset
  - added `GTAA Universe (DBC)` as an alternate preset in the GTAA form
  - added small captions in the UI so the commodity-sleeve difference is visible at selection time
- Durable implication:
  - GTAA users can now compare `PDBC` vs `DBC` directly at the preset level while keeping the project’s current default universe unchanged

### 2026-04-02 - GTAA now also provides a no-commodity comparison preset
- Request topic:
  - the user asked for one more GTAA preset where both `PDBC` and `DBC` are removed from the list
- Interpreted goal:
  - make it easy to compare GTAA with and without a commodity sleeve, without requiring manual ticker editing
- Result:
  - added `GTAA Universe (No Commodity Sleeve)` to the GTAA preset list
  - added a small UI caption clarifying that this preset excludes both `PDBC` and `DBC`
- Durable implication:
  - GTAA can now be compared across three preset-level commodity sleeve contracts:
    - default `PDBC`
    - alternate `DBC`
    - no commodity sleeve

### 2026-04-02 - GTAA DBC vs PDBC divergence was traced to cadence anchor plus rank/filter amplification
- Request topic:
  - the user asked why `DBC` and `PDBC` look very similar as ETFs, but GTAA results show much larger differences in compound return and MDD, and asked to compare:
    - `DBC`
    - `PDBC`
    - `No Commodity Sleeve`
  - the user also asked whether other commodity ETF alternatives should be considered
- Interpreted goal:
  - determine whether the gap comes from the ETF products themselves, from the current GTAA implementation contract, or from a combination of both, and leave a practical real-money interpretation
- Result:
  - confirmed that `DBC` and `PDBC` are highly similar at the standalone ETF level on common monthly history
  - traced the large GTAA gap to two interacting causes:
    - `Signal Interval = 2` causes a cadence-anchor problem because `PDBC` has a later first usable row, so the entire every-other-month rebalance calendar shifts
    - even when cadence is normalized with `interval = 1` or a common start date, GTAA still amplifies small sleeve differences through:
      - top-3 ranking
      - `MA200` trend filter
      - cash fallback when sleeves drop out
  - current project test results pointed to:
    - `DBC` > `No Commodity Sleeve` > `PDBC`
  - documented the full comparison in:
    - `.note/finance/phase12/PHASE12_GTAA_DBC_PDBC_NO_COMMODITY_ANALYSIS.md`
  - recorded alternative broad commodity ETF candidates for later testing:
    - `CMDY`
    - `BCI`
    - `COMT`
- Durable implication:
  - `PDBC` should not currently be treated as a drop-in strategy-equivalent replacement for `DBC` inside GTAA
  - fair sleeve comparison should use at least:
    - common start alignment
    - the same cost contract
    - preferably `Signal Interval = 1` first
  - future commodity-sleeve decisions should be made from GTAA-in-strategy tests, not ETF-only chart similarity

### 2026-04-02 - GTAA commodity alternative candidate backtests favored DBC, with COMT/CMDY as the best K-1-free follow-ups
- Request topic:
  - the user asked to collect data for alternative commodity ETF candidates and then run backtests to compare them against:
    - `DBC`
    - `PDBC`
    - `No Commodity Sleeve`
- Interpreted goal:
  - move beyond ETF-only product descriptions and determine which replacement candidates have the best chance of working inside the actual GTAA contract
- Result:
  - backfilled DB price history for:
    - `CMDY`
    - `BCI`
    - `COMT`
  - ran GTAA comparisons across:
    - `DBC`
    - `PDBC`
    - `CMDY`
    - `BCI`
    - `COMT`
    - `No Commodity Sleeve`
  - compared both current-contract runs and a common-start normalized run
  - practical ranking from the normalized comparison was:
    - overall: `DBC` > `No Commodity Sleeve` > `COMT` > `CMDY` > `BCI` > `PDBC`
    - among K-1-free alternatives only: `COMT` > `CMDY` > `BCI` > `PDBC`
  - recorded the full comparison in:
    - `.note/finance/phase12/PHASE12_GTAA_COMMODITY_ALTERNATIVE_CANDIDATE_ANALYSIS.md`
- Durable implication:
  - if the project keeps pure strategy performance as the main criterion, `DBC` still remains the best commodity sleeve in current GTAA tests
  - if `DBC` must be avoided for structure/tax reasons, `COMT` and `CMDY` are the most defensible next candidates to test further
  - if no K-1 replacement is required immediately, `No Commodity Sleeve` should remain a serious baseline because it still beat all current no-K-1 candidates in the normalized comparison

### 2026-04-02 - GTAA interval-1 universe variation search favored adding USMV on top of a DBC-based universe
- Request topic:
  - the user asked to hold `Signal Interval = 1` fixed, run ten GTAA universe variations with current and added symbols, collect missing data if needed, and determine whether GTAA can be modified into a better real-money portfolio
- Interpreted goal:
  - move beyond commodity-sleeve-only comparison and identify which practical universe edits improve both return and drawdown inside the existing GTAA contract
- Result:
  - backfilled DB history for:
    - `TIP`
    - `QUAL`
    - `USMV`
    - `VEA`
  - ran 10 GTAA backtests under a common interval-1 contract
  - found the most useful improvement directions were:
    - `DBC + USMV`
    - `DBC + QUAL + USMV`
  - `DBC + USMV` improved both:
    - `CAGR`
    - `MDD`
    relative to the `DBC` base universe
  - `QUAL` by itself raised `CAGR` but made `MDD` worse
  - `TIP` was selected only rarely and did not appear to be a primary improvement driver
  - documented the full 10-run search in:
    - `.note/finance/phase12/PHASE12_GTAA_INTERVAL1_UNIVERSE_VARIATION_SEARCH.md`
- Durable implication:
  - for current GTAA hardening, the next most defensible universe improvement is adding a low-volatility sleeve (`USMV`) rather than focusing only on commodity substitutions
  - `DBC` remains the preferred commodity sleeve in the current contract
  - if the project wants a stronger candidate preset to test later, `DBC + USMV` and `DBC + QUAL + USMV` are the best next-step candidates from this search

### 2026-04-02 - No-DBC GTAA search favored no-commodity-plus-quality/low-vol over PDBC or weaker commodity replacements
- Request topic:
  - the user asked for another 10-run search that excludes `DBC` and changes other symbols as well, to understand which no-DBC GTAA variants deserve attention
- Interpreted goal:
  - determine whether GTAA can still be improved without `DBC`, and whether the next best path is commodity replacement or broader universe redesign
- Result:
  - ran a second GTAA interval-1 search across 10 no-DBC variants using:
    - `PDBC`
    - `COMT`
    - `CMDY`
    - `BCI`
    - `No Commodity`
    plus `QUAL` / `USMV`
  - used a common-start normalized comparison to reduce inception-date distortion
  - strongest no-DBC candidates were:
    - `No Commodity + QUAL + USMV`
    - `COMT + QUAL + USMV`
  - found that `QUAL + USMV` additions improved the no-DBC contract more than trying to rescue `PDBC`
  - documented the full comparison in:
    - `.note/finance/phase12/PHASE12_GTAA_NO_DBC_INTERVAL1_VARIATION_SEARCH.md`
- Durable implication:
  - if `DBC` must be excluded, the best current GTAA direction is not simply "replace DBC with another commodity ETF"
  - the more effective path is:
    - either remove commodity and add `QUAL + USMV`
    - or keep commodity via `COMT` and still add `QUAL + USMV`
  - `PDBC` should not currently be treated as the default no-DBC solution

### 2026-04-02 - GTAA now provides two recommended no-DBC presets derived from the search results
- Request topic:
  - after reviewing the no-DBC search, the user asked which no-DBC configuration should be recommended and whether it could be exposed directly as presets
- Interpreted goal:
  - make the strongest no-DBC GTAA candidates runnable from the UI without requiring manual ticker editing
- Result:
  - added:
    - `GTAA Universe (COMT + QUAL + USMV)`
    - `GTAA Universe (No Commodity + QUAL + USMV)`
  - kept the current default preset unchanged so this is an additive comparison surface, not a forced default change
- Durable implication:
  - current GTAA UI now directly exposes the strongest no-DBC candidates found in Phase 12 search work
  - future QA can compare:
    - current `PDBC`
    - `DBC`
    - no commodity baseline
    - recommended no-DBC presets

### 2026-04-04 - Daily Market Update short-window refresh should be faster than long historical fetches and needs a separate execution contract
- Request topic:
  - the user reported that `Daily Market Update` on `Profile Filtered Stocks + ETFs` still took about `2,384 sec` for a short refresh and asked why `1d` and `20y` felt similarly slow, while also asking for a safe optimization that respects the previous yfinance rate-limit work
- Interpreted goal:
  - reduce wall time for routine short-window daily refreshes without undoing earlier rate-limit hardening for large universes
- Result:
  - verified from the latest broad managed run that the slowdown was almost entirely fetch-bound, not DB-bound:
    - `fetch_sec = 2367.96`
    - `delete_sec = 2.663`
    - `upsert_sec = 2.758`
    - `batch_count = 178`
    - `rate_limited_symbols = 0`
  - concluded that `1d` and `20y` felt similarly slow because symbol count and provider batch overhead dominated more than row volume
  - added a new OHLCV execution profile:
    - `managed_refresh_short`
  - routed short-window managed daily refreshes to that profile:
    - managed source
    - `interval = 1d`
    - `period = 1d`
    - or explicit date window around `10` days or shorter
  - kept long historical fetches and raw broad sweeps on the previous profiles so prior rate-limit safeguards remain in place
  - tuned the short-window profile from measured local comparison:
    - `managed_fast` on the same `240`-symbol sample: `40.221 sec`
    - `60x2` trial: `36.365 sec`
    - `70x2` trial: `23.886 sec`
    - adopted `chunk_size = 70`, `max_workers = 2`, `sleep = 0.01`

### 2026-04-04 - GTAA preset changes should refresh selected tickers immediately, and a DB-backed ETF group search favored QQQ plus IAU/XLE
- Request topic:
  - fix a GTAA UI issue where changing the preset did not immediately refresh the `Selected tickers` preview, and then run a new GTAA search using the current core plus broader DB-backed ETF combinations to find higher-CAGR / lower-MDD candidates
- Interpreted goal:
  - make GTAA preset iteration less frustrating in the UI, and then search the existing ETF database more systematically for a better real-money GTAA universe under the current contract
- Result:
  - fixed the GTAA Backtest form so universe controls are rendered outside the submit form:
    - preset changes now rerender immediately
    - `Selected tickers` updates without waiting for submit
  - backfilled missing ETF histories for the search:
    - `XLP`, `XLU`, `XLV`, `XLE`, `SHY`, `AGG`, `HYG`, `IAU`, `VEU`, `VWO`, `EWJ`, `VUG`, `VTV`, `RSP`, `ACWV`, `VGK`
  - ran an 18-group DB-backed GTAA search under the current default-style contract:
    - `start = 2016-01-01`
    - `end = 2026-04-02`
    - `top = 3`
    - `signal interval = 2`
    - `month_end`
    - `min_price = 5`
    - `transaction_cost = 10 bps`
  - the strongest direction in this contract came from combining:
    - `QQQ`
    - `IAU`
    - `XLE`
    with `QUAL` / `USMV` as secondary broadeners
  - best focused result:
    - `Base + QQQ + QUAL + USMV + XLE + IAU`
    - `CAGR = 11.50%`
    - `MDD = -16.69%`
    - `Sharpe = 1.184`
  - saved the full study to:
    - `.note/finance/phase12/PHASE12_GTAA_DB_ETF_GROUP_SEARCH.md`
- Durable implication:
  - under the current GTAA contract, the most promising next-step universe edit is not adding more bond sleeves or defensive sectors
  - the more defensible additive direction is:
    - offensive growth leadership via `QQQ`
    - alternative / inflation / cyclicality support via `IAU` and `XLE`
    - optional broadening via `QUAL` / `USMV`
  - `AGG`, `HYG`, `SHY`, and `TIP` should not currently be treated as high-value GTAA improvement levers relative to the existing bond sleeves

### 2026-04-04 - GTAA default signal interval was rebased from 2 to 1 and the main candidates were rerun under that new default
- Request topic:
  - after the GTAA group search, the user asked to rerun GTAA with `signal interval = 1` and also make `1` the new default instead of `2`
- Interpreted goal:
  - shift GTAA's default cadence to monthly signals and verify whether the previously identified best directions still hold under the new default contract
- Result:
  - changed GTAA default interval to `1` across:
    - single-strategy default input
    - compare default input
    - history / `Load Into Form` fallback
    - saved-portfolio compare override fallback
    - runtime/sample helper defaults
  - reran the main GTAA candidates under an interval-1 contract with a normalized common start date (`2016-08-31`) for fairer comparison
  - best interval-1 result remained:
    - `Base + QQQ + QUAL + USMV + XLE + IAU`
    - `CAGR = 11.41%`
    - `MDD = -21.96%`
  - strong runner-up:
    - `Base + QQQ + XLE + IAU + TIP`
    - `CAGR = 10.08%`
    - `MDD = -21.60%`
  - among existing UI presets, the strongest interval-1 candidates were:
    - `GTAA Universe (No Commodity + QUAL + USMV)` for higher CAGR
    - `GTAA Universe (DBC)` for slightly lower MDD
  - the current default `GTAA Universe` based on `PDBC` remained relatively weak even after the cadence rebase
  - saved the normalized rerun note as:
    - `.note/finance/phase12/PHASE12_GTAA_INTERVAL1_DEFAULT_REBASE_ANALYSIS.md`
- Durable implication:
  - GTAA should now be read as a monthly-signal default strategy in current UI/runtime paths
  - however, changing interval alone does not make the current `PDBC` default universe the strongest option
  - the most durable current direction is still centered on:
    - `QQQ`
    - `IAU`
    - `XLE`
    with `QUAL` / `USMV` as secondary broadeners

### 2026-04-04 - GTAA preset list was pruned to the default plus the current top three candidates
- Request topic:
  - keep `GTAA Universe`, remove the rest of the older GTAA presets, and replace them with the current top three candidate portfolios
- Interpreted goal:
  - reduce GTAA preset clutter and make the UI reflect the current Phase 12 conclusions instead of every historical comparison branch
- Result:
  - removed older comparison presets such as the prior `DBC`, `No Commodity Sleeve`, and `COMT + QUAL + USMV` variants
  - kept only:
    - `GTAA Universe`
    - `GTAA Universe (No Commodity + QUAL + USMV)`
    - `GTAA Universe (QQQ + XLE + IAU + TIP)`
    - `GTAA Universe (QQQ + QUAL + USMV + XLE + IAU)`
- Durable implication:
  - GTAA preset selection should now be read as:
    - one current default
    - three actively endorsed candidate universes
  - older exploratory universes still exist in analysis notes, but they are no longer treated as first-class UI presets

### 2026-04-04 - GTAA now exposes score-weight and risk-off contract controls in the UI
- Request topic:
  - expose GTAA's fixed `1/3/6/12` score mix to the UI and make the risk-off contract user-adjustable, including:
    - stronger bond preference
    - regime filter
    - crash-side guardrail
- Interpreted goal:
  - move GTAA from a hardcoded strategy flavor toward a tunable real-money research surface where the user can test whether score weighting and defensive behavior materially improve robustness
- Result:
  - GTAA score calculation is now user-configurable via:
    - `1M Weight`
    - `3M Weight`
    - `6M Weight`
    - `12M Weight`
  - GTAA risk-off contract is now user-configurable via:
    - `Trend Filter Window`
    - `Fallback Mode`
    - `Defensive Tickers`
    - `Market Regime Overlay`
    - `Crash Guardrail`
  - these controls were wired through:
    - single strategy form
    - compare GTAA block
    - history / prefill
    - saved-portfolio compare override
    - runtime/sample defaults
  - GTAA result rows now expose more diagnostic columns around risk-off behavior:
    - `Defensive Fallback Count`
    - `Regime State`
    - `Crash Guardrail Triggered`
    - `Risk-Off Reason`
  - saved the implementation note as:
    - `.note/finance/phase12/PHASE12_GTAA_SCORE_WEIGHT_AND_RISK_OFF_FIRST_PASS.md`
- Durable implication:
  - GTAA should no longer be read as having a single hardcoded score contract
  - future GTAA hardening can now compare:
    - equal-weight score blend vs tilted score blend
    - pure cash fallback vs defensive bond preference
    - no overlay vs regime/crash overlays
- Durable output:
  - `.note/finance/DAILY_MARKET_UPDATE_SHORT_WINDOW_ACCELERATION_20260404.md`

### 2026-04-04 - GTAA score contract was clarified further: users must be able to choose the horizons, not only the weights

- Request topic:
  - the user clarified that the GTAA score UI should not keep `1M / 3M / 6M / 12M` fixed and only expose weights
  - instead, the user wants a row-style contract:
    - default rows `1M / 3M / 6M / 12M`
    - add new month rows when needed
    - disallow duplicate months
- Interpreted goal:
  - turn GTAA score controls into an editable month-horizon contract rather than a fixed 4-leg blend with adjustable weights
- Result:
  - GTAA now exposes a row-based score editor
  - the default rows are `1M / 3M / 6M / 12M`
  - rows can be removed
  - new month rows like `9M` can be added
  - duplicate month rows are blocked
  - only the current rows are included in the score calculation
- defaults remain unchanged:
    - initial rows are `1M / 3M / 6M / 12M`
    - equal weights of `1`
  - the new `score_lookback_months` / derived `score_return_columns` contract is now preserved through:
    - single GTAA form
    - compare GTAA override
    - runtime metadata
    - history record / `Load Into Form`
    - saved strategy override
- Durable implication:
  - GTAA score testing can now separate two questions:
    - which month horizons should exist in the score at all
    - how heavily each included horizon should be weighted

### 2026-04-04 - GTAA score UI was simplified again: equal-weight horizon selection is the final first-pass contract

- Request topic:
  - after trying the row-based score editor, the user asked to simplify the GTAA score UI again
  - desired final behavior:
    - back to the simpler style
    - no visible weight inputs
    - selected horizons should all be weighted equally
- Interpreted goal:
  - reduce GTAA tuning UI complexity while keeping the useful part:
    horizon selection
- Result:
  - GTAA score UI now exposes only `Score Horizons`
  - selectable horizons are:
    - `1M`
    - `3M`
    - `6M`
    - `12M`
  - all selected horizons are treated equally
  - defaults remain:
    - `1M / 3M / 6M / 12M` all selected
  - runtime metadata now records equal `score_weights` only for the selected horizons
- Durable implication:
  - current GTAA first-pass score contract should be read as:
    - selectable horizon set
    - equal-weight blend across that set

### 2026-04-04 - GTAA vs SPY dominance search found no tested Phase 12 configuration that beat SPY on both CAGR and MDD

- Request topic:
  - check whether a GTAA portfolio can be found that has:
    - lower MDD than `SPY`
    - higher CAGR than `SPY`
- Interpreted goal:
  - treat `SPY` as the practical benchmark to beat on two axes at once,
    not just on one metric
- Result:
  - compared Phase 12 GTAA candidates against a common `SPY` baseline over the shared period starting `2016-08-31`
  - `SPY` baseline came out to approximately:
    - `CAGR 12.21%`
    - `MDD -24.80%`
  - base search plus overlay-extended search still produced:
    - winner count `0`
  - closest offensive candidate:
    - `GTAA Universe (QQQ + XLE + IAU + TIP)` or `GTAA Universe (QQQ + XLE + IAU)`
    - `Score Horizons = 1/3/6`
    - `CAGR 11.90%`
    - `MDD -20.03%`
  - strongest defensive candidate:
    - `GTAA Universe (No Commodity + QUAL + USMV)`
    - `CAGR 8.96%`
    - `MDD -16.17%`
- Durable implication:
  - current Phase 12 GTAA contract can meaningfully improve drawdown relative to `SPY`
  - but within the tested search space it has not yet produced a configuration that dominates `SPY` on both CAGR and MDD simultaneously
  - if that remains the target, the next levers are:
    - wider ETF universe search
    - different `top N`
    - further risk-off contract changes

### 2026-04-04 - GTAA practical floor search found a candidate above CAGR 9 and above MDD -16

- Request topic:
  - search for a GTAA configuration with:
    - `CAGR >= 9%`
    - `MDD >= -16%`
- Interpreted goal:
  - find a practical minimum bar for a real-money GTAA candidate
- Result:
  - broad manual universes plus `top / interval / score horizon` variation produced a strong candidate:
    - universe: `QQQ|VUG|RSP|VTV|QUAL|USMV|XLE|IAU|TIP|TLT|LQD|ACWV|SPY`
    - `top=2`
    - `interval=2`
    - `Score Horizons = 1/3`
    - `risk-off = cash_only`
  - performance:
    - `CAGR 12.90%`
    - `MDD -11.10%`
- Durable implication:
  - current Phase 12 GTAA search space is capable of producing a candidate that clears the practical floor
  - the candidate is materially better than the requested floor on both axes

### 2026-04-04 - GTAA cadence-expanded floor search found many stronger target hits

- Request topic:
  - continue the practical floor search by varying universe mix and rebalance cadence
- Interpreted goal:
  - see whether the `CAGR >= 9%` and `MDD >= -16%` floor can be met by multiple GTAA contracts, not just one narrow configuration
- Result:
  - total search size:
    - `180` DB-backed backtests
  - target hits:
    - `88`
  - strongest offensive candidate:
    - `U3_commodity`
    - `interval=3`
    - `top=2`
    - `horizons=1/3/6`
    - `CAGR 16.66%`
    - `MDD -11.29%`
  - strongest balanced candidate:
    - `U1_offensive`
    - `interval=3`
    - `top=2`
    - `horizons=1/3/6/12`
    - `CAGR 16.25%`
    - `MDD -10.59%`
  - strongest defensive candidate:
    - `U5_smallcap_value`
    - `interval=3`
    - `top=3`
    - `horizons=1/3/6/12`
    - `CAGR 12.04%`
    - `MDD -9.79%`
- Durable implication:
  - the GTAA contract family already contains multiple configurations that satisfy the practical floor
  - rebalance cadence matters materially, and in this search `interval=3` was especially strong
  - the remaining decision is not whether the floor can be reached, but which candidate family should become the default real-money GTAA baseline

### 2026-04-04 - Verified GTAA target-search candidates were promoted into UI preset bases

- Request topic:
  - create GTAA presets from the newly verified candidate families
- Interpreted goal:
  - make the best Phase 12 GTAA universes reusable from the UI without re-entering long ticker lists
- Result:
  - added:
    - `GTAA Universe (U3 Commodity Candidate Base)`
    - `GTAA Universe (U1 Offensive Candidate Base)`
    - `GTAA Universe (U5 Smallcap Value Candidate Base)`
  - each preset caption now shows the currently validated contract recommendation for that universe base
- Durable implication:
  - GTAA candidate comparison can now start from stable preset universes
  - the preset itself only controls the universe; users should still pair it with the recommended `top`, `interval`, and `Score Horizons`

### 2026-04-04 - Backtest sensitivity alone is not enough to justify real-money deployment; robustness and rationale must come first

- Request topic:
  - if backtest results move materially when rebalance cadence, score horizon, or related contract choices change, is it still reasonable to use that strategy for real-money investing?
- Interpreted goal:
  - define the standard for when a backtest is only an interesting research result versus when it becomes a defensible basis for live capital allocation
- Result:
  - a strong backtest by itself is not enough
  - if small parameter changes cause large performance swings, that is a warning sign for overfitting or contract fragility
  - real-money use becomes more defensible only when three things hold together:
    - economic rationale:
      there is a believable reason the strategy should work
    - robustness:
      nearby parameter choices, neighboring rebalance cadences, and different sample windows still look acceptable
    - implementability:
      turnover, cost, investability, and operational simplicity remain realistic
- Practical standard:
  - the right question is not
    - “what single backtest is best?”
  - but rather
    - “is there a broad stable region where the strategy remains acceptable?”
- Durable implication:
  - current GTAA candidate results should be treated as promotion candidates, not final live-allocation proof
  - before committing real money, the next validation layer should focus on:
    - parameter stability surfaces
    - subperiod / walk-forward consistency
    - benchmark-relative behavior
    - cost / execution realism
    - a paper-trading or small-capital probation phase

### 2026-04-04 - GTAA compare mode now supports the same universe contract as single mode, and the target-search note includes a candidate decision table

- Request topic:
  - create the promised GTAA real-money candidate summary
  - and add missing GTAA preset selection to `Compare & Portfolio Builder`
- Interpreted goal:
  - make the top GTAA candidates easier to read as practical choices
  - and remove the mismatch where single GTAA had preset/manual universe control but compare GTAA did not
- Result:
  - expanded `.note/finance/phase12/PHASE12_GTAA_CAGR9_MDD16_TARGET_SEARCH.md` with a decision table covering:
    - offensive candidate
    - balanced candidate
    - defensive candidate
    - recommended contract
    - strengths
    - cautions
    - current status
  - added GTAA universe selection to compare mode:
    - `Preset` / `Manual`
    - compare execution now respects the chosen GTAA preset/ticker set
  - compare prefill and saved-portfolio compare restoration now also preserve:
    - GTAA tickers
    - GTAA preset name
    - GTAA universe mode
- Durable implication:
  - GTAA should now be read as having one consistent universe-contract surface across:
    - single strategy
    - compare
    - history / prefill
    - saved portfolio compare context

### 2026-04-04 - Equal Weight compare mode also needed the same universe selector treatment

- Request topic:
  - after adding GTAA compare universe selection, the user noticed that `Equal Weight` still did not appear as an equivalent strategy-specific option surface in compare mode
- Interpreted goal:
  - remove the remaining compare-mode inconsistency so `Equal Weight` and `GTAA` both expose their universe contract clearly
- Result:
  - added `Equal Weight Universe` to `Compare & Portfolio Builder`
  - compare now supports:
    - `Preset` / `Manual`
    - execution with the chosen equal-weight universe
    - prefill / saved-portfolio restoration of the equal-weight universe contract
- Durable implication:
  - compare mode should now be read as supporting the same universe-contract surface for:
    - `Equal Weight`
    - `GTAA`

### 2026-04-04 - Compare universe selectors were moved under each strategy block for a more regular UI contract

- Request topic:
  - the user asked why `Equal Weight Universe` and `GTAA Universe` were not inside `Advanced Inputs > Strategy-Specific Advanced Inputs`, and requested that they be moved there for more regular management
- Interpreted goal:
  - keep compare strategy configuration grouped by strategy instead of splitting universe selection outside and execution options inside
- Result:
  - moved `Equal Weight Universe` and `GTAA Universe` into each strategy's own compare block under `Advanced Inputs`
  - kept execution/prefill/saved-portfolio restoration working with the same universe-contract fields
- Durable implication:
  - compare strategy configuration should now be read as one grouped contract per strategy
  - the tradeoff is that universe selection now follows compare form submission semantics again

### 2026-04-04 - GTAA was intentionally paused and Phase 12 resumed with strict annual hardening

- Request topic:
  - the user asked to stop pushing GTAA for now and return to the original Phase 12 workstream
- Interpreted goal:
  - resume the Phase 12 main path instead of spending more time on GTAA candidate exploration
- Result:
  - resumed `Strict Annual Family` as the next active implementation target
  - implemented annual strict real-money hardening first pass for:
    - `Quality Snapshot (Strict Annual)`
    - `Value Snapshot (Strict Annual)`
    - `Quality + Value Snapshot (Strict Annual)`
  - added:
    - `Minimum Price`
    - `Transaction Cost (bps)`
    - `Benchmark Ticker`
    to single, compare, history/prefill, and runtime paths
  - extended annual strict runtime so min-price filtering is applied before selection and the result surface now exposes gross/net/turnover/cost/benchmark in the same contract style as ETF strategies
- Durable implication:
  - Phase 12 should now be read as having:
    - ETF real-money hardening first pass completed
    - strict annual real-money hardening first pass completed
  - the next annual strict work is no longer first-pass contract wiring, but second-pass guardrail / validation reinforcement

### 2026-04-04 - Strict annual next step was interpreted as validation-surface reinforcement rather than immediate hard guardrails

- Request topic:
  - after annual strict first-pass hardening, the next step in Phase 12 needed to continue without returning to GTAA
- Interpreted goal:
  - make annual strict more useful for real-money review, but avoid prematurely baking fragile benchmark rules directly into portfolio decisions
- Result:
  - added shared benchmark-relative validation diagnostics:
    - strategy / benchmark max drawdown
    - rolling underperformance
    - `validation_status = normal / watch / caution`
  - surfaced them in:
    - single-strategy `Real-Money` tab
    - compare `Strategy Highlights`
    - focused strategy `Real-Money Contract`
    - `Execution Context`
- Durable implication:
  - current Phase 12 second pass should be read as:
    - stronger review / caution surface
    - not yet automatic stop/risk-off strategy rules
  - if later we add hard guardrails, they should be treated as a separate decision from this validation-surface layer

### 2026-04-05 - Promotion decision should be exposed as a read-only review surface before any stronger guardrail is added

- Request topic:
  - after the next Phase 12 step resumed, the runtime already had promotion-decision logic but the UI surface was incomplete
- Interpreted goal:
  - finish the annual strict second pass by making the promotion recommendation visible wherever validation is already reviewed
- Result:
  - exposed:
    - `promotion_decision`
    - `promotion_rationale`
    - `promotion_next_step`
  in:
    - single-strategy `Real-Money`
    - compare `Strategy Highlights`
    - `Execution Context`
- Durable implication:
  - current Phase 12 should now be read as having:
    - validation diagnostics
    - promotion guidance
  but still not automatic hard guardrails
  - the next deeper step remains stronger guardrail / actual strategy-rule reinforcement, not more UI plumbing

### 2026-04-05 - Strict annual underperformance guardrail was promoted from review-only concept to optional actual rule

- Request topic:
  - continue the next Phase 12 step after validation/promotion surface and add commit workflow guidance to project instructions
- Interpreted goal:
  - keep strict annual family moving toward a more practical real-money contract by turning one benchmark-relative warning into an optional, explicit strategy rule
- Result:
  - added an optional underperformance guardrail for annual strict family only
  - contract:
    - benchmark-relative trailing excess return
    - configurable lookback window
    - configurable worst-excess threshold
  - behavior:
    - when the guardrail is enabled and trailing excess return breaches the threshold on rebalance,
      the strategy stays in cash for that rebalance
  - surfaced guardrail diagnostics in:
    - single `Real-Money`
    - compare `Strategy Highlights`
    - `Execution Context`
    - history/prefill contract
  - also added AGENTS guidance to commit each finished implementation unit with a descriptive log
- Durable implication:
  - Phase 12 strict annual family now has:
    - first-pass real-money hardening
    - second-pass validation/promotion surface
    - first-pass optional actual guardrail
  - later work should focus on:
    - stronger investability proxy
    - richer benchmark contract
    - broader promotion robustness

### 2026-04-05 - Strict annual stronger investability proxy should start with history-length, not full liquidity modeling

- Request topic:
  - continue the next Phase 12 step after guardrail work
- Interpreted goal:
  - make annual strict real-money review less fragile by filtering out symbols that technically exist in the universe but do not yet have enough usable price history
  - also make benchmark comparison easier to interpret than raw end-balance overlay alone
- Result:
  - added `Minimum History (Months)` as the first stricter investability proxy for annual strict family
  - added richer benchmark summary fields:
    - `Benchmark CAGR`
    - `Net CAGR Spread`
    - `Benchmark Coverage`
  - connected the new contract to:
    - single
    - compare
    - history / prefill
    - runtime metadata
- Durable implication:
  - current Phase 12 annual strict contract now has:
    - minimum price
    - minimum history
    - turnover / cost
    - benchmark-relative validation
    - optional underperformance guardrail
  - but this is still not the final liquidity model
  - later passes should add:
    - volume / spread / AUM-aware investability
    - richer benchmark policy
    - stricter promotion reinforcement

### 2026-04-05 - WORK_PROGRESS should stay canonical, but future archive should be phase-based rather than month-based

- Request topic:
  - review whether `WORK_PROGRESS` should remain one file, or be split monthly / by phase
  - refresh current guidance/reference docs based on how the repository is actually being used now
- Interpreted goal:
  - reduce future note sprawl without losing the convenience of a single top-level progress log
- Result:
  - keep `.note/finance/WORK_PROGRESS.md` as the canonical active log
  - do not adopt monthly splitting as the default
  - when the log grows too large or a phase accumulates heavy detail, archive by phase instead
  - preferred structure:
    - root `WORK_PROGRESS.md` for active/high-signal summary
    - `phase*/PHASE*_WORKLOG.md` for detailed archive when needed
  - also refreshed repo guidance so future commit descriptions default to Korean for this repository
- Durable implication:
  - the repository remains easy to open from one top-level log
  - but future cleanup should happen by phase, not by calendar month
  - workflow guidance now matches the actual phase-managed operating model of the project

### 2026-04-05 - Strict annual later-pass investability should start with average dollar volume, not a full trading model

- Request topic:
  - continue the next Phase 12 step after minimum-history / benchmark reinforcement
- Interpreted goal:
  - improve real-money usefulness of annual strict family by filtering out candidates that may pass price/history rules but still look too small in actual trading activity
- Result:
  - added `Min Avg Dollar Volume 20D ($M)` to:
    - `Quality Snapshot (Strict Annual)`
    - `Value Snapshot (Strict Annual)`
    - `Quality + Value Snapshot (Strict Annual)`
  - implementation uses DB daily `close * volume` and trailing 20-day average dollar volume
  - the filter now travels through:
    - single
    - compare
    - history / prefill
    - execution context
    - real-money tab
  - result rows now also keep:
    - `Liquidity Excluded Ticker`
    - `Liquidity Excluded Count`
- Durable implication:
  - current strict annual contract now has:
    - minimum price
    - minimum history
    - minimum average dollar volume
    - turnover / cost
    - benchmark-relative validation
    - optional underperformance guardrail
  - but this is still a practical proxy, not a full execution model
  - later passes should still consider:
    - spread-aware liquidity
    - richer benchmark policy
    - broader promotion robustness

### 2026-04-05 - Strict annual promotion should treat benchmark quality as a policy gate, not just a readout

- Request topic:
  - continue the next Phase 12 strict annual hardening step after liquidity proxy first pass
- Interpreted goal:
  - make promotion decisions more trustworthy by checking whether the benchmark comparison itself is strong enough to rely on
- Result:
  - added two strict annual promotion-policy inputs:
    - `Min Benchmark Coverage (%)`
    - `Min Net CAGR Spread (%)`
  - runtime now evaluates:
    - `benchmark_policy_status = normal / watch / caution / unavailable`
    - `benchmark_policy_watch_signals`
    - coverage/spread pass state
  - `promotion_decision` now uses benchmark policy status together with:
    - `validation_status`
    - `universe_contract`
    - `price_freshness`
  - UI/history surface now shows and restores the new policy fields across:
    - single
    - compare
    - history / `Load Into Form`
    - execution context
- Durable implication:
  - strict annual no longer treats benchmark overlay as "present vs absent" only
  - it now distinguishes:
    - benchmark exists but is policy-weak
    - benchmark exists and is promotion-usable
  - this makes `hold / production_candidate / real_money_candidate` more explainable before real-money promotion

### 2026-04-05 - Strict annual liquidity should be judged by how often liquidity exclusions actually happen

- Request topic:
  - continue the next strict annual later-pass investability step after benchmark policy reinforcement
- Interpreted goal:
  - treat liquidity as a promotion-quality signal, not only as a raw filter setting
- Result:
  - added a new strict annual policy input:
    - `Min Liquidity Clean Coverage (%)`
  - runtime now evaluates:
    - `liquidity_rebalance_rows`
    - `liquidity_excluded_active_rows`
    - `liquidity_clean_coverage`
    - `liquidity_policy_status = normal / watch / caution / unavailable`
  - `promotion_decision` now uses liquidity policy status together with:
    - benchmark policy
    - validation status
    - universe contract
    - price freshness
  - UI/history surface now shows and restores the new policy fields across:
    - single
    - compare
    - history / `Load Into Form`
    - execution context
- Durable implication:
  - strict annual now distinguishes between:
    - liquidity filter exists
    - liquidity exclusions are actually rare enough for promotion
  - this makes real-money promotion less optimistic when the strategy keeps running into liquidity limits at rebalance time

### 2026-04-05 - Quality/value strategy logic should stay in finance layers while the Backtest UI surface is simplified

- Request topic:
  - review whether `backtest.py` should keep holding every strategy surface directly
  - clarify how quality/value strategies are currently managed
  - simplify the visible strategy list into `Quality`, `Value`, `Quality + Value`
- Interpreted goal:
  - make the strategy surface easier to manage without destabilizing already-working runtime code
- Result:
  - confirmed the current ownership boundary is:
    - `finance/strategy.py` = simulation / decision logic
    - `finance/sample.py` = DB-backed snapshot / factor assembly
    - `app/web/runtime/backtest.py` = runtime wrapper / bundle contract
    - `app/web/pages/backtest.py` = Streamlit UI / compare / history orchestration
  - added `app/web/pages/backtest_strategy_catalog.py` to hold:
    - family labels
    - variant labels
    - concrete display names
    - concrete strategy keys
  - simplified the user-facing top-level strategy surface in both single and compare to:
    - `Quality`
    - `Value`
    - `Quality + Value`
  - kept concrete runtime keys unchanged so:
    - history records
    - `Load Into Form`
    - compare prefill
    - runtime dispatch
    remain backward-compatible
- Durable implication:
  - this was a safe first-pass UI/orchestration refactor, not a strategy-logic rewrite
  - future work can still split large quality/value form renderers into more files, but the family/variant contract is now centralized first

### 2026-04-05 - `backtest.py` size and strategy code organization should move toward family-level composition, not per-strategy inheritance

- Request topic:
  - ask whether current `app/web/pages/backtest.py` size is acceptable
  - ask whether strategy management should stay centralized or split into separate files
  - ask whether a base/abstract-class inheritance model would be the right direction
- Interpreted goal:
  - choose a maintenance direction that improves readability without destabilizing already-working backtest code
- Result:
  - current file sizes were checked:
    - `app/web/pages/backtest.py`: `8563` lines
    - `app/web/runtime/backtest.py`: `2971` lines
    - `finance/sample.py`: `2075` lines
    - `finance/strategy.py`: `1182` lines
  - judgement:
    - `backtest.py` is now beyond a comfortable long-term maintenance size
    - it is still workable today because roles are known, but it is large enough that future changes will become slower and riskier if left as-is
  - recommended direction:
    - keep `backtest.py` as the page orchestrator
    - keep strategy simulation logic in finance layers
    - split UI/orchestration by family and shared helper units, not by one-file-per-strategy blindly
  - concrete recommendation:
    - `app/web/pages/backtest.py`
      - page composition / top-level routing only
    - `app/web/pages/backtest_strategy_catalog.py`
      - family / variant / concrete strategy mapping
    - future good split units:
      - quality family UI module
      - value family UI module
      - quality+value family UI module
      - shared compare helpers
      - shared history/prefill helpers
  - strategy-code recommendation:
    - do **not** move quality/value simulation logic into `backtest.py`
    - keep the current functional boundary:
      - `finance/sample.py` = DB-backed input assembly
      - `finance/strategy.py` = simulation / decision logic
      - `app/web/runtime/backtest.py` = runtime wrapper / result bundle
  - inheritance judgement:
    - a heavy base-class / abstract-class hierarchy is **not** the best next step for the current codebase
    - current strategies differ mainly in:
      - input contract
      - loader/runtime wrapper
      - factor configuration
      - UI surface
    - they do not yet benefit enough from deep OO inheritance to justify the complexity
    - better near-term pattern:
      - composition
      - small shared helpers
      - strategy/family catalog
      - possibly light `dataclass` or spec objects later
- Durable implication:
  - next refactor should be:
    - `large page -> family modules + shared helpers`
  - not:
    - `every strategy -> subclass hierarchy`
  - if `finance/strategy.py` grows further, a later split by domain is reasonable:
    - price-only strategies
    - statement/factor strategies
    - shared simulation helpers

### 2026-04-05 - Current recommendation is selective refactor, not large rewrite

- Request topic:
  - ask whether we should proactively refactor more now or leave the current structure alone if it is still working
- Interpreted goal:
  - choose the best maintenance path for future finance work without creating unnecessary regression risk
- Result:
  - recommended stance:
    - **do not** perform a large structural rewrite immediately
    - **do** continue with small, high-signal refactors when a touched area is already causing friction
  - practical recommendation:
    1. keep `finance/strategy.py` as-is for now
       - it is not yet the biggest maintenance hotspot
       - its current role boundary is still understandable
    2. keep `backtest.py` as the page orchestrator
       - but gradually peel off large family UI blocks into helper/modules
       - especially when touching the same area again
    3. avoid deep inheritance as the next move
       - current strategy differences are driven more by inputs/configuration/UI surface than by a clean polymorphic class tree
    4. prefer staged refactor triggers
       - refactor when:
         - the same file area is touched repeatedly
         - one family block becomes hard to review safely
         - compare/prefill/history logic keeps duplicating
       - do not refactor only for aesthetics
- Durable implication:
  - best near-term path is:
    - keep current runtime boundaries stable
    - refactor only the hotspots we touch next
    - treat `backtest.py` modularization as incremental maintenance, not a big-bang rewrite

### 2026-04-05 - Strict annual promotion should use validation metrics as policy, not only readout

- Request topic:
  - continue Phase 12 after strict annual validation / liquidity / benchmark surfaces were already visible
- Interpreted goal:
  - move strict annual promotion one step closer to a real-money contract by using existing validation metrics as actual promotion thresholds
- Result:
  - added two later-pass promotion thresholds:
    - `Max Underperformance Share (%)`
    - `Min Worst Rolling Excess (%)`
  - introduced `validation_policy_status = normal / watch / caution / unavailable`
  - updated `promotion_decision` so that validation policy now matters alongside:
    - benchmark policy
    - liquidity policy
    - dynamic/static universe contract
    - price freshness
- Durable implication:
  - strict annual promotion is no longer based only on benchmark spread/coverage and liquidity cleanliness
  - rolling-underperformance robustness is now part of the actual promotion contract

### 2026-04-05 - Strict annual benchmark review should go beyond a single ticker benchmark

- Request topic:
  - continue Phase 12 after validation / liquidity / promotion policy later passes were already connected
- Interpreted goal:
  - widen strict annual benchmark interpretation so promotion-grade review can compare not only against a broad ETF like `SPY`, but also against a simple baseline built from the same candidate universe
- Result:
  - added `Benchmark Contract` for strict annual family:
    - `Ticker Benchmark`
    - `Candidate Universe Equal-Weight`
  - runtime now records:
    - `benchmark_contract`
    - `benchmark_label`
    - `benchmark_symbol_count`
    - `benchmark_eligible_symbol_count`
  - single / compare / history / `Load Into Form` all preserve the chosen benchmark contract
- Durable implication:
  - strict annual review can now answer two different questions:
    1. is the strategy better than a broad reference ticker like `SPY`?
    2. is the strategy better than simply holding the same candidate universe equally?
  - underperformance guardrail actual-rule still uses `benchmark_ticker` in this first pass, so the broader benchmark contract currently widens validation/promotion interpretation more than execution rules

### 2026-04-05 - Strict annual promotion should also cap drawdown behavior

- Request topic:
  - continue Phase 12 after broader benchmark contract was already connected
- Interpreted goal:
  - make strict annual promotion more conservative when drawdown itself is too deep or too much worse than benchmark, instead of relying only on benchmark spread, liquidity cleanliness, and rolling-underperformance validation
- Result:
  - added two drawdown-based promotion thresholds:
    - `Max Strategy Drawdown (%)`
    - `Max Drawdown Gap vs Benchmark (%)`
  - introduced:
    - `guardrail_policy_status = normal / watch / caution / unavailable`
    - `guardrail_policy_watch_signals`
    - `drawdown_gap_vs_benchmark`
  - updated `promotion_decision` so that guardrail policy now matters alongside:
    - benchmark policy
    - liquidity policy
    - validation policy
    - dynamic/static universe contract
- Durable implication:
  - strict annual promotion is now closer to a real-money review contract where drawdown severity matters directly
  - this is still a promotion/interpretation rule, not an actual strategy-side drawdown guardrail that changes rebalance behavior

### 2026-04-05 - Strict annual should support an actual drawdown-based risk-off rule

- Request topic:
  - continue Phase 12 after drawdown-based promotion policy was already connected
- Interpreted goal:
  - move one step beyond promotion-only review and allow strict annual family to actually step aside when recent drawdown behavior is too severe
- Result:
  - added an optional actual guardrail to strict annual family:
    - `Drawdown Guardrail`
    - `Drawdown Window (Months)`
    - `Strategy DD Threshold (%)`
    - `Drawdown Gap Threshold (%)`
  - rebalance can now move to cash when:
    - trailing strategy max drawdown is too deep
    - or drawdown gap vs benchmark is too large
  - runtime/result/meta now record:
    - guardrail state
    - trigger count/share
    - strategy drawdown
    - benchmark drawdown
    - drawdown gap
    - blocked ticker/count
- Durable implication:
  - strict annual family now has both:
    - promotion-side drawdown policy
    - actual strategy-side drawdown guardrail
  - this makes annual strict real-money review materially closer to a true operating contract instead of a read-only interpretation layer

### 2026-04-05 - Phase 13 should start as deployment-readiness and probation, not as a new strategy expansion phase

- Request topic:
  - start Phase 13 after Phase 12 practical closeout
- Interpreted goal:
  - open the next finance phase in a way that narrows real-money candidates into actual deployment candidates, instead of immediately adding many new strategies
- Result:
  - opened Phase 13 as:
    - deployment-readiness
    - probation
    - monitoring
    - rolling / out-of-sample review
  - created:
    - `.note/finance/phase13/PHASE13_DEPLOYMENT_READINESS_AND_PROBATION_PLAN.md`
    - `.note/finance/phase13/PHASE13_CURRENT_CHAPTER_TODO.md`
  - synced:
    - master roadmap
    - finance doc index
    - work progress log
- Durable implication:
  - the project should now interpret strategy work in this order:
    1. Phase 12 established real-money candidate contracts
    2. Phase 13 narrows those candidates into shortlist / probation states
    3. backlog items like ETF second-pass guardrails belong to Phase 13 only insofar as they improve deployment-readiness
  - current operating state should be read as:
    - `Phase 12`: implementation closed / manual_validation_pending
    - `Phase 13`: active phase

### 2026-04-05 - Quality / Value / Quality+Value family is not uniformly ready for real-money deployment

- Request topic:
  - before continuing Phase 13, confirm whether `Quality`, `Value`, `Quality + Value` strategies are already fully implemented for actual use
- Interpreted goal:
  - distinguish which variants are truly usable as real-money candidates versus which still remain research-only
- Result:
  - the correct interpretation is variant-specific, not family-wide
  - `Research` variants:
    - usable for exploration
    - not a real-money deployment target
  - `Strict Annual` variants:
    - now have substantial real-money candidate surface
    - including dynamic PIT contract, investability filters, transaction cost, benchmark contract, liquidity proxy, validation policy, promotion policy, and actual drawdown guardrail
    - should be read as `real-money candidate` or `production candidate`, not as fully deployment-ready live strategies
  - `Strict Quarterly Prototype` variants:
    - remain explicitly `research-only`
    - should not be interpreted as ready for actual capital deployment
- Durable implication:
  - the annual strict family is sufficiently implemented to enter Phase 13 shortlist / probation review
  - but it is still not the same thing as “safe to deploy live immediately”
  - Phase 13 exists exactly because deployment-readiness, probation, monitoring, and rolling/out-of-sample review are still needed after Phase 12

### 2026-04-05 - Phase 13 first pass should reinterpret promotion into shortlist language

- Request topic:
  - start actual Phase 13 implementation after confirming that strict annual is only at candidate stage, not full live-deployment stage
- Interpreted goal:
  - make the existing promotion surface operationally useful by translating it into shortlist states that map to actual next actions
- Result:
  - added a shortlist layer on top of `promotion_decision`
  - runtime now records:
    - `strategy_family`
    - `shortlist_family`
    - `shortlist_status`
    - `shortlist_next_step`
    - `shortlist_rationale`
  - first-pass shortlist mapping was fixed as:
    - `hold -> hold`
    - `production_candidate -> watchlist`
    - `real_money_candidate -> paper_probation`
    - annual strict `real_money_candidate` with actual guardrails and candidate-equal-weight benchmark -> `small_capital_trial`
  - UI surface now shows shortlist state in:
    - single / focused `Real-Money`
    - `Execution Context`
    - compare `Strategy Highlights`
    - compare meta table
- Durable implication:
  - Phase 13 no longer starts from raw backtest winner interpretation
  - it now starts from an operational shortlist language that separates:
    - candidate quality
    - immediate next action
    - whether the strategy should stay on watchlist, go to paper probation, or be considered for small-capital trial

### 2026-04-05 - ETF second-pass hardening should add actual guardrail rules, not only read-only review overlays

- Request topic:
  - continue Phase 13 into the next ETF second-pass step after the shortlist layer
- Interpreted goal:
  - make ETF deployment-readiness more operational by allowing `GTAA`, `Risk Parity Trend`, and `Dual Momentum` to enforce benchmark-relative guardrails at rebalance time
- Result:
  - added actual ETF-side:
    - `Underperformance Guardrail`
    - `Drawdown Guardrail`
  - the new contract now propagates through:
    - single strategy forms
    - compare overrides
    - history / `Load Into Form`
    - saved-portfolio compare context
    - runtime / sample / strategy execution
  - ETF rebalance behavior now moves to cash when the configured underperformance or drawdown rule is breached
  - ETF result rows now record guardrail state / trigger columns, and runtime meta collects ETF trigger counts
- Durable implication:
  - the ETF second-pass guardrail item is now implemented as a first pass
  - ETF current-operability remains a current-snapshot overlay, not PIT operability history
  - actual AUM/spread block rules remain later-pass backlog

### 2026-04-05 - Phase 13 should turn shortlist into a probation and monitoring workflow before adding more ETF operability rules

- Request topic:
  - continue into the next Phase 13 step after ETF guardrail second pass
- Interpreted goal:
  - make deployment-readiness operational by telling us not only whether a strategy is shortlisted, but how it should now be observed and reviewed
- Result:
  - added a probation / monitoring workflow layer on top of the existing shortlist contract
  - new runtime meta now includes:
    - `probation_status`
    - `probation_stage`
    - `probation_review_frequency`
    - `probation_next_step`
    - `monitoring_status`
    - `monitoring_focus`
    - `monitoring_breach_signals`
    - `monitoring_review_frequency`
    - `monitoring_next_step`
  - first-pass probation mapping was fixed as:
    - `hold -> not_ready`
    - `watchlist -> watchlist_review`
    - `paper_probation -> paper_tracking`
    - `small_capital_trial -> small_capital_live_trial`
  - monitoring status is derived conservatively from existing validation / policy states and actual guardrail trigger counts, producing:
    - `blocked`
    - `routine_review`
    - `heightened_review`
    - `breach_watch`
  - UI surface now shows the new workflow state in:
    - single `Real-Money`
    - `Execution Context`
    - compare `Strategy Highlights`
    - compare meta table
- Durable implication:
  - Phase 13 can now express "what to do next" as an operational review workflow, not only as a static shortlist label
  - this keeps the project conservative: it adds deployment-readiness guidance without turning current-snapshot ETF operability data into a look-ahead-prone actual block rule

### 2026-04-05 - The next Phase 13 step should add rolling and out-of-sample review before any stronger ETF operability block rule

- Request topic:
  - continue Phase 13 after shortlist, ETF guardrails, and probation / monitoring workflow
- Interpreted goal:
  - add a more realistic deployment-readiness review layer that checks whether the strategy still behaves acceptably in recent regimes and in later-period split samples
- Result:
  - added a rolling / out-of-sample validation workflow first pass
  - new runtime meta now includes:
    - `rolling_review_status`
    - `rolling_review_recent_excess_return`
    - `rolling_review_recent_drawdown_gap`
    - `out_of_sample_review_status`
    - `out_of_sample_in_sample_excess_return`
    - `out_of_sample_out_sample_excess_return`
    - `out_of_sample_excess_change`
  - recent regime review now reads the latest `12M` or `252D` window against the benchmark and compares it with the previous window when available
  - split-period review now compares the aligned first half and second half so that later-period deterioration is explicit
  - this first pass does not change `promotion_decision`; instead it makes `probation / monitoring` interpretation more conservative
  - UI surface now shows the new review state in:
    - single `Real-Money`
    - `Execution Context`
    - compare `Strategy Highlights`
    - compare meta table
- Durable implication:
  - Phase 13 is no longer only about shortlist and monthly monitoring
  - it now includes a lightweight current-regime and split-period consistency check before capital increases
  - this remains safer than turning current-snapshot ETF operability data into a hard actual block rule too early

### 2026-04-05 - After shortlist, probation, and rolling review, Phase 13 should surface a deployment-readiness checklist

- Request topic:
  - continue Phase 13 into the next step after rolling / out-of-sample review
- Interpreted goal:
  - make the current deployment-readiness state readable as one operational checklist rather than as scattered policy fields
- Result:
  - added a deployment-readiness checklist first pass on top of:
    - shortlist
    - probation / monitoring
    - rolling / out-of-sample review
    - benchmark / liquidity / validation / guardrail policy
  - new runtime meta now includes:
    - `deployment_readiness_status`
    - `deployment_readiness_next_step`
    - `deployment_checklist_rows`
    - pass/watch/fail/unavailable counts
  - first-pass deployment status was fixed as:
    - `blocked`
    - `review_required`
    - `watchlist_only`
    - `paper_only`
    - `small_capital_ready`
    - `small_capital_ready_with_review`
  - UI surface now shows the checklist in:
    - single `Real-Money`
    - `Execution Context`
    - compare `Strategy Highlights`
    - compare meta table
- Durable implication:
  - Phase 13 now has a product-surface summary for "can we move toward deployment yet?"
  - this checklist is still conservative and read-only; it is not an automatic execution approval rule

### 2026-04-05 - Phase 13 can be closed out after deployment-readiness checklist, with manual validation still pending

- Request topic:
  - finish Phase 13 and prepare the user-facing checklist before opening the next phase
- Interpreted goal:
  - decide whether the remaining ETF operability / deployment items are closeout blockers, and if not, close the phase cleanly with a practical summary and manual checklist
- Result:
  - treated the following as later-pass backlog, not closeout blockers:
    - ETF current-operability actual block rule
    - ETF point-in-time operability history
    - monthly probation note logging
    - richer live deployment workflow
  - concluded that Phase 13 is now:
    - `practical closeout`
    - `manual_validation_pending`
  - added:
    - completion summary
    - next-phase preparation
    - manual test checklist
  - updated roadmap, index, progress log, and current TODO board to match the closeout state
- Durable implication:
  - Phase 13 is no longer the active implementation phase
  - the project now has deployment-readiness / probation / monitoring / rolling review / checklist layers in place, and the next decision is about which live deployment or PIT execution-readiness direction to open next

### 2026-04-05 - The Phase 13 checklist should explicitly point users to the Real-Money tab, and shortlist terms should live in the glossary

- Request topic:
  - the user could not find `Promotion Decision`, `Candidate Shortlist`, `Shortlist Status`, `Shortlist Next Step` while reading the Phase 13 checklist
- Interpreted goal:
  - make the checklist location more concrete and store the related terms in the shared glossary so future Phase 13 testing is easier to follow
- Result:
  - clarified the checklist wording so `Candidate Shortlist Surface` explicitly points to:
    - `Backtest > Single Strategy`
    - run result area
    - `Real-Money` tab
    - `Execution Context`
  - added glossary entries for:
    - `Real-Money Tab`
    - `Promotion Decision`
    - `Candidate Shortlist`
    - `Shortlist Status`
    - `Shortlist Next Step`
    - `Execution Context`
- Durable implication:
  - Phase 13 manual QA now has a clearer UI path
  - the core operational terms are no longer only explained in chat and can be reused across later phases

### 2026-04-05 - The Real-Money tab should be reorganized around user decision flow rather than raw policy order

- Request topic:
  - the user felt that the `Real-Money` result tab contained too much information in a fragmented order and wanted a more intuitive UX with short explanations
- Interpreted goal:
  - keep the same runtime/meta semantics, but restructure the UI so users can judge the current state more quickly without reading every policy block linearly
- Result:
  - reorganized the `Real-Money` tab into four internal tabs:
    - `현재 판단`
    - `검토 근거`
    - `실행 부담`
    - `상세 데이터`
  - added a short reading guide at the top of the tab
  - moved lower-signal detail to:
    - a collapsed policy expander
    - the final detail tab
  - kept core status blocks first:
    - promotion
    - shortlist
    - probation / monitoring
    - deployment readiness
  - placed benchmark / rolling / out-of-sample review into the evidence layer
  - placed cost / liquidity / ETF operability / actual guardrails into the operability layer
- Durable implication:
  - the `Real-Money` tab now follows the operator’s decision order rather than the implementation order
  - future checklist wording should reference the internal `Real-Money` tabs when guiding manual QA

### 2026-04-05 - Validation, benchmark, liquidity, and guardrail terms should be easy to look up in one shared glossary

- Request topic:
  - the user wanted a simpler explanation of `validation`, `benchmark`, `liquidity`, and `guardrail`, and asked for the shared term document to be updated if these terms were missing or too thin
- Interpreted goal:
  - make the core Phase 12 / 13 interpretation vocabulary reusable without relying on chat explanations
- Result:
  - kept the existing `Benchmark`, `Liquidity Policy`, and `Portfolio Guardrail` entries
  - added or expanded:
    - `Benchmark Policy`
    - `Liquidity`
    - `Validation`
    - `Validation Policy`
    - `Guardrail Policy`
  - aligned the new terms with the same glossary structure:
    - basic explanation
    - why it is used
    - example / use case
- Durable implication:
  - future manual QA and result interpretation can point to the glossary directly when users ask what these policy layers mean

### 2026-04-05 - The Latest Backtest Run header should be easier to scan and read in Korean

- Request topic:
  - the user felt that the multiple guidance lines shown under `Latest Backtest Run` were not visually organized and wanted them reworked into a clearer Korean UX
- Interpreted goal:
  - keep the same result content, but make the top of the single-run result screen easier to scan before the user dives into the tabs
- Result:
  - added a grouped Korean guidance block explaining:
    - how to read the result
    - which surfaces are available in this run
    - what warnings should be reviewed together
  - merged scattered per-run warning lines into one consolidated warning block
  - replaced the old English first-pass caption with Korean operator-facing copy
- Durable implication:
  - users can now orient themselves faster at the top of the result surface before moving into `Summary`, `Equity Curve`, `Real-Money`, or `Meta`

### 2026-04-05 - The Real-Money tab should visually separate related information more clearly

- Request topic:
  - the user liked the reorganized Real-Money tab, but still felt that related information inside each internal tab was not visually grouped strongly enough
- Interpreted goal:
  - keep the same information and tab order, but make section boundaries clearer so users can distinguish one block of meaning from another at a glance
- Result:
  - wrapped the main Real-Money sections in bordered containers
  - standardized each section to show:
    - title
    - short explanation
    - related metrics / rationale / status message
  - applied this to:
    - promotion
    - shortlist
    - probation / monitoring
    - deployment readiness
    - benchmark / validation
    - rolling / out-of-sample review
    - execution contract
    - ETF operability
    - actual guardrails
    - detail previews
- Durable implication:
  - the Real-Money tab now separates related meaning visually as well as logically, reducing the chance that users read adjacent sections as one continuous block

### 2026-04-05 - `resolve_validation_gaps_before_promotion` means promotion is blocked by concrete validation or policy issues

- Request topic:
  - the user asked what should actually be done when `Promotion Next Step` shows `resolve_validation_gaps_before_promotion`
- Interpreted goal:
  - explain the operational meaning of this next step and translate the runtime rule into concrete debugging actions
- Result:
  - confirmed from runtime logic that this next step is used only when `promotion_decision = hold`
  - the main blockers are:
    - `benchmark_unavailable`
    - `validation_status = caution`
    - `benchmark_policy_status = caution`
    - ETF strategies only: `etf_operability_status = caution / unavailable`
    - `liquidity_policy_status = caution / unavailable`
    - `validation_policy_status = caution / unavailable`
    - `guardrail_policy_status = caution / unavailable`
    - `price_freshness.status = error`
  - clarified that the following do **not** trigger this hold path by themselves:
    - `static_universe_contract`
    - `validation/watch`
    - policy `watch`
    - `price_freshness.warning`
  - recommended the operator flow:
    - check `Real-Money > 현재 판단` for the hold message
    - check `Promotion rationale`
    - then inspect `검토 근거` and `실행 부담` to find which policy block is `caution` or `unavailable`
- Durable implication:
  - users can now interpret `resolve_validation_gaps_before_promotion` as a concrete validation/debugging to-do rather than a vague status label

### 2026-04-06 - Deployment-readiness checklist `blocked` does not itself recalculate promotion to `hold`

- Request topic:
  - the user asked whether failing the checklist rows under deployment readiness means the strategy automatically becomes `hold`
- Interpreted goal:
  - clarify the relationship between promotion-level status and the later deployment-readiness summary layer
- Result:
  - confirmed that `promotion_decision` is calculated earlier from:
    - benchmark availability
    - validation status
    - benchmark / liquidity / validation / guardrail policy status
    - ETF operability status
    - price freshness
    - universe contract
  - confirmed that `deployment_readiness_status` is calculated later as a downstream operational summary using:
    - shortlist
    - probation
    - monitoring
    - rolling / out-of-sample review
    - policy check rows
  - therefore:
    - checklist failure does **not** directly recalculate promotion to `hold`
    - but a strategy that is already `hold` usually causes checklist rows like `Shortlist = fail` and `Probation = fail`, which often leads deployment readiness to `blocked`
  - also clarified:
    - not all non-pass checklist rows imply `hold`
    - `watch` / `unavailable` can still lead to `paper_only`, `watchlist_only`, or `small_capital_ready_with_review`
    - `fail` rows can lead to either `blocked` or `review_required` depending on shortlist/probation stage
- Durable implication:
  - users should read promotion as the earlier "can this strategy be promoted?" gate
  - users should read deployment readiness as the later "can we actually move toward paper/live operation?" checklist layer

### 2026-04-06 - When promotion is `hold`, the UI should show a concrete fix guide rather than only raw rationale codes

- Request topic:
  - the user confirmed that the real goal is to eventually get a portfolio into a usable state rather than leaving it at `hold`, and asked whether the product can briefly explain what to change when `hold` appears
- Interpreted goal:
  - turn `resolve_validation_gaps_before_promotion` from a technical status into an actionable operator guide inside the result UI
- Result:
  - added a `Hold 해결 가이드` block to `Real-Money > 현재 판단`
  - the guide appears when `promotion_decision = hold`
  - it translates blocking rationale codes into a short table with:
    - `막히는 항목`
    - `먼저 볼 위치`
    - `권장 조치`
  - the mapped blockers currently include:
    - benchmark unavailable
    - validation caution
    - benchmark / liquidity / validation / guardrail policy caution or unavailable
    - ETF operability caution or unavailable
    - price freshness error
- Durable implication:
  - users no longer need to infer the debugging path from raw rationale codes alone
  - Phase 13 manual QA should explicitly verify that hold cases show this guide

### 2026-04-06 - The execution-burden tab should explain liquidity-policy blockers directly where the hold guide points

- Request topic:
  - after seeing `Hold 해결 가이드`, the user followed the pointer to `실행 부담 > 실행 계약 요약 / Liquidity Policy` and found that the execution tab still showed only raw liquidity metrics without enough explanation
- Interpreted goal:
  - make the execution-burden surface self-explanatory enough that users can actually resolve `liquidity_policy_unavailable` or related issues without guessing
- Result:
  - added a dedicated `Liquidity Policy` section inside `Real-Money > 실행 부담`
  - the section now surfaces:
    - `Policy Status`
    - `Min Avg Dollar Volume 20D`
    - `Min Clean Coverage`
    - `Actual Clean Coverage`
    - `Liquidity Excluded Rows`
  - also added direct Korean explanations for:
    - why `unavailable / watch / caution` is currently shown
    - what the user should change next
  - specifically, when `Min Avg Dollar Volume 20D = 0`, the UI now explains that the liquidity filter is effectively disabled and that promotion-grade liquidity review cannot run until the value is set above zero
- Durable implication:
  - the hold-resolution flow is now connected end-to-end:
    - hold reason
    - where to go
    - why that section is blocking
    - what to modify next

### 2026-04-06 - `Min Avg Dollar Volume 20D` should be explained as an explicit glossary term

- Request topic:
  - the user asked what `Min Avg Dollar Volume 20D` means exactly
- Interpreted goal:
  - explain the metric in plain language and preserve the explanation as durable project terminology
- Result:
  - clarified that it means recent 20-trading-day average dollar trading volume
  - explained that it is a simple liquidity filter used to avoid candidates that are too hard to trade in practice
  - clarified that `0.0M` effectively means the liquidity filter is off, which often leads `Liquidity Policy` to `unavailable`
- Durable implication:
  - future UI explanations and hold-resolution flows can refer users to a glossary-backed meaning instead of re-explaining the metric ad hoc

### 2026-04-06 - A practical non-hold example should prefer a realistic benchmark over an artificially easy benchmark

- Request topic:
  - the user asked whether we could run several backtests from different angles and find one portfolio setup that does not land in `hold`
- Interpreted goal:
  - provide one concrete configuration the user can copy, so they can see what a usable non-hold run looks like in practice
- Result:
  - a practical non-hold case was found with:
    - strategy: `GTAA`
    - preset: `GTAA Universe (U1 Offensive Candidate Base)`
    - benchmark: `SPY`
    - `top=2`
    - `rebalance interval=3`
    - score horizons: `1/3/6/12`
    - `risk_off_mode=cash_only`
    - ETF operability policy disabled for that run
  - resulting state:
    - `promotion_decision = production_candidate`
    - `shortlist_status = watchlist`
    - `deployment_readiness_status = review_required`
    - `validation_status = watch`
    - summary stats: approximately `CAGR 16.24%`, `MDD -10.59%`
  - also found that the same GTAA candidate can become `real_money_candidate` with bond benchmarks such as `TLT`, `IEF`, or `LQD`
  - however, that was not recommended as the main example because it makes the comparison frame too easy and is less aligned with a broad-equity operator reference frame like `SPY`
- Durable implication:
  - when showing users a non-hold reference run, prefer a realistic benchmark-aligned example even if it lands at `production_candidate` rather than forcing `real_money_candidate` through a weaker comparison contract

### 2026-04-06 - Quality + Value strict annual can reach real-money-candidate when the contract is monthly and dynamic PIT

- Request topic:
  - the user asked whether we could make and share a similar non-hold example for the `Quality + Value` strategy family
- Interpreted goal:
  - provide one concrete `Quality + Value > Strict Annual` setup the user can copy to understand what a usable non-hold configuration looks like
- Result:
  - a UI-reproducible example was found with:
    - strategy family: `Quality + Value`
    - variant: `Strict Annual`
    - preset: `US Statement Coverage 100`
    - universe contract: `Historical Dynamic PIT Universe`
    - benchmark contract: `Candidate Universe Equal-Weight`
    - benchmark ticker: `SPY`
    - start: `2020-01-01`
    - rebalance option: `month_end`
    - rebalance interval: `1`
    - `top_n = 10`
    - `Minimum Price = 5.0`
    - `Minimum History = 12M`
    - `Min Avg Dollar Volume 20D = 5.0M`
    - `Transaction Cost = 10 bps`
    - trend filter off, market regime off, underperformance guardrail on, drawdown guardrail on
  - resulting state:
    - `promotion_decision = real_money_candidate`
    - `shortlist_status = small_capital_trial`
    - `deployment_readiness_status = review_required`
    - `validation_status = normal`
    - `benchmark_policy_status = normal`
    - `liquidity_policy_status = normal`
    - `validation_policy_status = normal`
    - `guardrail_policy_status = normal`
    - `rolling_review_status = normal`
    - `out_of_sample_review_status = normal`
    - `promotion_rationale = []`
    - summary stats: approximately `CAGR 32.44%`, `MDD -28.35%`
- Durable implication:
  - for strict annual factor families, a monthly rebalance cadence plus `Historical Dynamic PIT Universe` can materially improve promotion readiness because it removes the `static_universe_contract` blocker while keeping the other policy surfaces evaluable

### 2026-04-06 - Real-money 입력 항목은 의미와 목적을 같이 설명해야 혼란이 줄어든다

- Request topic:
  - the user asked what `Minimum Price`, `Minimum History`, `Min Avg Dollar Volume 20D`, `Transaction Cost`, `Trend Filter`, `Market Regime`, `Underperformance Guardrail`, and `Drawdown Guardrail` mean and why they are used
- Interpreted goal:
  - make the real-money controls understandable in operator language, not just raw parameter labels
- Result:
  - documented the missing terms in the glossary and strengthened the cost explanation with a `bps` example
  - clarified that these inputs fall into a few operator categories:
    - investability: `Minimum Price`, `Minimum History`, `Min Avg Dollar Volume 20D`
    - execution realism: `Transaction Cost`
    - risk control: `Trend Filter`, `Market Regime`, `Underperformance Guardrail`, `Drawdown Guardrail`
- Durable implication:
  - future UX around real-money forms should explain inputs by purpose group, not just by field name, because operators naturally ask both “what is this?” and “why do I need it?”

### 2026-04-06 - 2016년 시작과 MDD 15% 이내를 동시에 만족하는 비보류 포트폴리오 후보 탐색

- Request topic:
  - the user asked whether we could construct a portfolio that starts in January 2016 and keeps `MDD` within `15%`
- Interpreted goal:
  - find one concrete, non-hold backtest configuration that is practical to inspect and copy
- Result:
  - interpreted `MDD 15 이하` as `Maximum Drawdown >= -15%`
  - the cleaner candidate found was:
    - strategy: `GTAA`
    - preset family: `U1 Offensive Candidate Base`
    - benchmark: `TLT`
    - `top=2`
    - `rebalance interval=3`
    - score horizons: `1/3/6/12`
    - start: `2016-01-01`
    - no extra trend/regime overlay
    - ETF operability policy disabled for the search path
  - resulting state:
    - `promotion_decision = real_money_candidate`
    - `shortlist_status = paper_probation`
    - `deployment_readiness_status = paper_only`
    - `validation_status = normal`
    - `rolling_review_status = normal`
    - `out_of_sample_review_status = normal`
    - summary stats: approximately `CAGR 15.04%`, `MDD -9.82%`
- Important caveat:
  - this candidate met the condition with a bond benchmark (`TLT`), not with `SPY`
  - under the same 2016-start and MDD constraint, the `SPY` benchmark runs that were checked tended to stay in `hold` because `validation = caution`
- Durable implication:
  - when a strict drawdown target is imposed over a long 2016-start window, a usable candidate may exist only under a more defensive benchmark frame, so benchmark choice must be disclosed clearly when sharing “usable” portfolio examples

### 2026-04-06 - Quality + Value dynamic PIT에 2016 시작과 MDD 15% 이내를 동시에 요구하면 현재 구현 범위에선 비현실적이다

- Request topic:
  - the user corrected the previous request and fixed the strategy family to `Quality + Value` with `Historical Dynamic PIT Universe`
- Interpreted goal:
  - find one `Quality + Value` portfolio configuration that starts in January 2016 and still keeps `Maximum Drawdown` within `15%`
- Result:
  - interpreted `MDD 15 이하` as `Maximum Drawdown >= -15%`
  - re-ran `Quality + Value > Strict Annual` across practical UI-reproducible variations:
    - `top_n`
    - rebalance cadence
    - benchmark contract / benchmark ticker
    - trend filter, market regime, guardrail combinations
  - did not find a convincing `hold 아님` configuration that also stayed within the `-15%` MDD target over the full `2016-01-01 ~ 2026-04-01` window
  - the previously found stronger non-hold configuration for this family remained around `MDD ≈ -28%`
- Durable implication:
  - for the current strict-annual `Quality + Value` implementation, a long 2016-start window plus a `-15%` drawdown ceiling is too strict to be a realistic operator target
  - if the user wants to stay within this family, the next practical levers are:
    - relax the MDD target
    - shorten the start window
    - or accept `hold` and use a stronger defensive overlay as a research-only experiment rather than a production-ready reference

### 2026-04-06 - factor 자체를 바꿔도 `Quality + Value`는 2016 시작 저낙폭 목표와 비보류 상태를 동시에 맞추지 못했다

- Request topic:
  - after learning that the earlier search did not vary factors, the user asked to explore again by changing other options and factor composition
- Interpreted goal:
  - determine whether `Quality + Value > Strict Annual` can escape `hold` while also keeping `Maximum Drawdown >= -15%` under:
    - `Historical Dynamic PIT Universe`
    - `start = 2016-01-01`
- Result:
  - re-ran with defensive factor sets and slower cadence
  - factor changes did materially affect drawdown
  - best low-drawdown case reached about `MDD = -13.57%`, but stayed in `hold`
    - quality: `current_ratio, cash_ratio, debt_to_assets, debt_ratio`
    - value: `ocf_yield, fcf_yield, pcr, pfcr`
    - `month_end / interval 6 / top_n 30`
    - `Candidate Universe Equal-Weight` benchmark
  - retuning benchmark to `LQD` produced a usable non-hold candidate, but drawdown worsened again
    - best non-hold near-miss:
      - same defensive factor set
      - `month_end / interval 6 / top_n 40 or 50`
      - `benchmark = LQD`
      - `promotion = production_candidate`
      - `MDD ≈ -18.91%`
- Durable implication:
  - within practical UI-reproducible settings, the current `Quality + Value` strict annual family still exhibits a hard trade-off:
    - defensive factor sets can push drawdown under the target, but then validation keeps the strategy in `hold`
    - benchmark choices that lift the strategy out of `hold` push drawdown back above the `-15%` target
  - the user should treat:
    - `MDD 15% 이내`
    - `hold 아님`
    - `2016 시작 dynamic PIT`
    as a simultaneously difficult constraint set for this family under the current implementation

### 2026-04-06 - `CAGR 15% 이상 + MDD 20% 이내` 조건에서는 Value Strict Annual이 exact hit를 만들었다

- Request topic:
  - after the earlier long-window/SPY comparison work, the user asked for another search using sub-agents
- Interpreted goal:
  - find one portfolio under:
    - `start = 2016-01-01`
    - `Universe Contract = Historical Dynamic PIT Universe`
    - `top_n <= 10`
    - `CAGR >= 15%`
    - `Maximum Drawdown >= -20%`
- Result:
  - `Quality`, `Value`, and `Quality + Value` strict annual families were explored in parallel
  - the best exact hit came from `Value Strict Annual`
  - main-environment revalidation confirmed:
    - factors:
      - `earnings_yield`
      - `ocf_yield`
      - `operating_income_yield`
      - `fcf_yield`
    - `month_end`
    - `rebalance_interval = 1`
    - `top_n = 9`
    - `Benchmark = SPY`
    - `Trend Filter = on`
    - `Market Regime = on`
    - `Underperformance Guardrail = on`
    - `Drawdown Guardrail = on`
    - `CAGR = 15.84%`
    - `MDD = -17.42%`
    - `promotion = hold`
    - `shortlist = hold`
    - `deployment = blocked`
- Durable implication:
  - the project can now point to one exact-hit configuration for the requested numeric target
  - however, this configuration still fails the current promotion/deployment contract
  - this is a clear example where:
    - return/risk numbers are good enough for the user's target
    - but the product's operator policy still keeps the strategy in `hold`

### 2026-04-06 - `hold 아님 + CAGR 20% 이상 + MDD 25% 이내` 조건은 current strict annual 범위에선 exact hit가 없었다

- Request topic:
  - the user asked for another sub-agent search with:
    - `promotion != hold`
    - `CAGR >= 20%`
    - `Maximum Drawdown >= -25%`
- Interpreted goal:
  - determine whether a truly operator-acceptable candidate exists under a tougher return target while preserving a still-defensive drawdown ceiling
- Result:
  - sub-agents explored `Quality`, `Value`, and `Quality + Value` strict annual families
  - no exact-hit candidate was found in the searched practical setting space
  - the strongest near-miss again came from `Value > Strict Annual`
    - default value factor set
    - `month_end / rebalance_interval 1 / top_n 10`
    - `Benchmark = SPY`
    - `Trend Filter = on`
    - `Market Regime = on`
    - `Underperformance Guardrail = on`
    - `Drawdown Guardrail = on`
    - `CAGR = 18.81%`
    - `MDD = -23.71%`
    - `promotion = hold`
- Durable implication:
  - current strict annual families can approach the requested numeric band, but not while also clearing the current promotion contract
  - the practical bottleneck remains:
    - validation / promotion policy
    - not simple factor/universe/cadence tuning alone

### 2026-04-06 - hold의 직접 원인은 validation caution이었고, requested family 내 non-hold exact hit는 아직 못 찾았다

- Request topic:
  - the user asked to identify why the current best candidate was held and then find a non-hold portfolio satisfying the same numeric target
- Interpreted goal:
  - diagnose the hold reason for the `Value Strict Annual` exact-hit candidate
  - search `Quality` and `Quality + Value` strict annual families for a non-hold candidate under:
    - `CAGR >= 15%`
    - `MDD >= -20%`
    - `start = 2016-01-01`
    - `Historical Dynamic PIT Universe`
    - `top_n <= 10`
- Result:
  - exact-hit `Value Strict Annual` candidate remained `hold` because:
    - `validation_status = caution`
    - `validation_policy_status = caution`
    - `rolling_review_status = caution`
  - requested-family search did not produce a non-hold exact hit
  - the closest non-hold Q+V candidates all achieved `production_candidate` but at much lower CAGR
- Durable implication:
  - the blocking issue is now clearly identified as the validation layer, not just the raw return/risk envelope
  - if the user wants a true non-hold candidate, the next useful work is to relax or reinterpret the validation policy, or to accept a weaker return target

### 2026-04-06 - SPY 대비 CAGR/MDD를 동시에 만족하는 Value Strict Annual 후보를 찾았다

- Request topic:
  - the user asked for a portfolio that beats `SPY` on both return and drawdown, with `start = 2016-01-01`, `top_n <= 10`, and `Historical Dynamic PIT Universe`
- Interpreted goal:
  - search across `Quality`, `Value`, and `Quality + Value` strict annual families and find a candidate that satisfies:
    - `CAGR >= 15%`
    - `Maximum Drawdown >= -20%`
    - relative to `SPY`
- Result:
  - after family-by-family search, `Value Strict Annual` produced the clearest match
  - best exact candidate:
    - factor set: `earnings_yield`, `ocf_yield`, `operating_income_yield`, `fcf_yield`
    - `month_end`
    - `rebalance_interval = 1`
    - `top_n = 9`
    - `trend_filter = on`
    - `market_regime = on`
    - `underperformance_guardrail = on`
    - `drawdown_guardrail = on`
    - benchmark: `SPY`
    - result:
      - `CAGR = 15.84%`
      - `MDD = -17.42%`
      - `promotion = hold`
  - near misses:
    - same factor set with `top_n = 7`
      - `CAGR = 15.24%`
      - `MDD = -19.57%`
    - same factor set with `top_n = 10`
      - `CAGR = 14.61%`
      - `MDD = -15.16%`
- Durable implication:
  - if the user's main requirement is beating `SPY` on both CAGR and MDD, the current best reference is the `Value Strict Annual` setup above
  - if the user also insists on `hold` being cleared, the next improvement has to come from the validation/policy layer rather than the raw return series

### 2026-04-06 - SPY 대비 우위 + `CAGR >= 15%` + `MDD >= -20%`를 만족하는 후보를 family별로 다시 탐색했지만 교집합은 없었다

- Request topic:
  - the user asked to search, via sub-agents, for a portfolio that beats `SPY` while also meeting:
    - `start = 2016-01-01`
    - `Historical Dynamic PIT Universe`
    - `top_n <= 10`
    - `CAGR >= 15%`
    - `Maximum Drawdown >= -20%`
- Interpreted goal:
  - find the strongest practical candidate across `Quality`, `Value`, and `Quality + Value` strict annual families
- Result:
  - family-level search was completed
  - `Value Strict Annual` was the strongest family overall
  - best raw value candidate:
    - `v_default`
    - `month_end / interval=1 / top_n=10`
    - `CAGR 29.89%`
    - `MDD -29.15%`
    - `promotion = real_money_candidate`
  - best low-drawdown value near-miss:
    - `v_profit_cashflow`
    - `month_end / interval=1 / top_n=5`
    - `benchmark = LQD`
    - `CAGR 13.16%`
    - `MDD -19.18%`
    - `promotion = hold`
  - `Quality Strict Annual` had `SPY`-beating raw candidates, but they remained `hold`
  - `Quality + Value Strict Annual` could lower drawdown, but not while keeping CAGR above the target
- Durable implication:
  - in the tested grid, there is no clean intersection of:
    - `SPY` outperformance
    - `CAGR >= 15%`
    - `MDD >= -20%`
    - `top_n <= 10`
    - `Historical Dynamic PIT Universe`
  - the nearest practical choices are either:
    - accept `CAGR >= 15%` with higher drawdown
    - or accept lower CAGR with drawdown near the target

### 2026-04-06 - Quality Strict Annual는 SPY를 이기는 raw candidate가 있으나 full hardening까지는 아직 부족하다

- Request topic:
  - the user asked to search the `Quality Strict Annual` family only and to find portfolios that beat the SPY baseline on both CAGR and drawdown
- Interpreted goal:
  - find practical UI-reproducible `Quality Snapshot (Strict Annual)` settings with:
    - `start = 2016-01-01`
    - `end = 2026-04-01`
    - `Universe Contract = Historical Dynamic PIT Universe`
    - `top_n <= 10`
    - `CAGR > 14.09%`
    - `MDD > -33.72%`
- Result:
  - a broad factor screen showed that `Quality` alone can beat SPY on raw performance
  - best SPY-dominance candidates found under a practical UI pass with `trend_filter = on` and `market_regime = on` were:
    - `capital_discipline`:
      - `roe, roa, cash_ratio, debt_to_assets`
      - `month_end / interval 1 / top_n 10`
      - `CAGR = 15.80%`
      - `MDD = -27.97%`
    - `balance_sheet`:
      - `current_ratio, cash_ratio, debt_to_assets, debt_ratio`
      - `month_end / interval 1 / top_n 5`
      - `CAGR = 15.71%`
      - `MDD = -33.20%`
    - `balance_sheet`:
      - same factor set
      - `month_end / interval 1 / top_n 10`
      - `CAGR = 14.46%`
      - `MDD = -26.83%`
  - when full real-money hardening was re-enabled (`underperformance_guardrail` + `drawdown_guardrail`), the edge disappeared and the same family moved back toward `hold`
- Durable implication:
  - `Quality` family has a genuine SPY-dominance path in raw backtest terms
  - however, current full hardening still needs additional refinement before the family can be treated as a clean deployment-ready reference

### 2026-04-06 - `Quality` 단독 strict annual은 SPY 기준선을 넘는 후보를 찾았지만 아직 non-hold는 못 찾았다

- Request topic:
  - the user asked for a portfolio that beats `SPY` on both return and drawdown, with `start = 2016-01-01`, `Universe Contract = Historical Dynamic PIT Universe`, and `top_n <= 10`
- Interpreted goal:
  - search `Quality`, `Value`, and `Quality + Value` strict annual families for a practical UI-reproducible portfolio that dominates the `SPY` baseline
- Result:
  - the best confirmed winners came from the `Quality Snapshot (Strict Annual)` family using the default quality factor set:
    - `month_end`, `rebalance_interval = 1`, `top_n = 2`
      - `CAGR = 29.69%`
      - `MDD = -25.19%`
    - `month_end`, `rebalance_interval = 1`, `top_n = 1`
      - `CAGR = 21.09%`
      - `MDD = -27.08%`
    - `month_end`, `rebalance_interval = 1`, `top_n = 5`
      - `CAGR = 21.20%`
      - `MDD = -29.56%`
  - all three beat the SPY baseline on both `CAGR` and `MDD`
  - however, under the current validation contract they still stayed in `hold`
  - value-only was not competitive in the checked grid, and `Quality + Value` remained weaker than the best quality-only result for this specific objective
- Durable implication:
  - if the user's only hard requirement is "must beat SPY", then `Quality` strict annual is the best confirmed family so far
  - if the user also requires `hold` to clear, the next step is to keep the same family but search a smaller factor/risk-contract neighborhood around the `q_default` quality-only candidate

### 2026-04-06 - SPY를 기준으로 보면 Value Strict Annual family가 Quality보다 낫지만, 승자는 아직 hold였다

- Request topic:
  - the user asked for a portfolio that beats `SPY` on both `CAGR` and `MDD`, under `start=2016-01-01`, `top_n <= 10`, and `Historical Dynamic PIT Universe`
- Interpreted goal:
  - compare `Quality`, `Value`, and `Quality + Value` families, but prioritize whichever family produces the best `SPY`-beating result
- Result:
  - `SPY` baseline over the effective comparison window:
    - `CAGR = 14.0899%`
    - `MDD = -33.7172%`
  - `Quality Strict Annual`:
    - no tested candidate beat `SPY` on both `CAGR` and `MDD`
  - `Value Strict Annual`:
    - produced the best candidates
    - top three winners all beat `SPY` on both metrics but still had `promotion = hold`
    - best three:
      - `v_default / month_end / interval 1 / top_n 10`
        - `CAGR = 18.81%`
        - `MDD = -23.71%`
      - `v_default / month_end / interval 1 / top_n 5`
        - `CAGR = 17.20%`
        - `MDD = -29.62%`
      - `v_profit_cashflow / month_end / interval 1 / top_n 10`
        - `CAGR = 14.61%`
        - `MDD = -15.16%`
- Durable implication:
  - when the comparison target is explicitly `SPY`, `Value Strict Annual` is the strongest of the tested families under the current search constraints
  - but the current validation / promotion contract is still too strict for those candidates to escape `hold`

### 2026-04-06 - Value Strict Annual의 hold 원인을 validation layer로 좁혔고, benchmark / cadence / trend / regime 조정만으로는 hold-free exact hit를 못 찾았다

- Request topic:
  - the user asked to diagnose why the best `Value Strict Annual` candidate was still `hold`, then search again for a non-hold candidate under the same numeric target
- Interpreted goal:
  - keep the existing practical UI constraints:
    - `Value Strict Annual`
    - `Historical Dynamic PIT Universe`
    - `start = 2016-01-01`
    - `top_n <= 10`
  - vary benchmark contract / ticker, factor set, cadence, and trend/regime switches
  - only after that, decide whether validation thresholds themselves need to be relaxed
- Result:
  - the exact-hit candidate remained:
    - `earnings_yield`, `ocf_yield`, `operating_income_yield`, `fcf_yield`
    - `month_end / interval 1 / top_n 9`
    - `benchmark = SPY`
    - `CAGR = 15.84%`
    - `MDD = -17.42%`
    - `promotion = hold`
  - the blocking reasons stayed:
    - `validation_status = caution`
    - `validation_policy_status = caution`
    - `rolling_review_status = caution`
  - no non-hold exact hit was found in the tested practical grid
- Durable implication:
  - benchmark / cadence / trend-regime changes were not enough to structurally resolve the hold
  - if the user wants the same numeric envelope but a non-hold state, the next useful lever is the validation / promotion threshold layer

### 2026-04-06 - `CAGR 20% 이상 + MDD 25% 이내 + hold 아님` exact hit는 이번 탐색 범위에서도 없었다

- Request topic:
  - the user relaxed the drawdown target to `25%` and raised the CAGR target to `20%`, while still requiring `hold` to be avoided
- Interpreted goal:
  - search practical UI-reproducible `Quality / Value / Quality+Value` strict annual candidates under:
    - `start = 2016-01-01`
    - `end = 2026-04-01`
    - `Historical Dynamic PIT Universe`
    - `top_n <= 10`
    - `CAGR >= 20%`
    - `Maximum Drawdown >= -25%`
    - `promotion != hold`
- Result:
  - the tested grid still did not produce a non-hold exact hit
  - the best raw candidate remained the earlier `Value Strict Annual` exact-hit shape, but it still sat at:
    - `CAGR = 15.84%`
    - `MDD = -17.42%`
    - `promotion = hold`
  - the blocking signals remained validation-driven:
    - `validation_status = caution`
    - `validation_policy_status = caution`
    - `rolling_review_status = caution`
- Durable implication:
  - increasing the drawdown tolerance to `25%` does not automatically unlock a usable non-hold portfolio
  - in the current contract, the main blocker is still the validation / promotion layer rather than the raw performance envelope

### 2026-04-06 - strict annual family 백테스트를 Quality / Value / Quality+Value 기준으로 한 장에 정리했다

- Request topic:
  - the user asked for one Markdown summary that organizes the backtests run so far across `Quality`, `Value`, and `Quality + Value`
- Interpreted goal:
  - reduce the need to reopen many phase13 search notes
  - leave one durable document that shows:
    - strongest family
    - strongest candidate by family
    - best defensive candidate
    - the common reason `hold` keeps appearing
- Result:
  - created `.note/finance/phase13/PHASE13_STRICT_ANNUAL_FAMILY_BACKTEST_SUMMARY.md`
  - the summary records that:
    - `Value Strict Annual` was the strongest family overall
    - `Quality Strict Annual` had meaningful raw candidates but stayed conservative under full hardening
    - `Quality + Value Strict Annual` was better for lowering drawdown than for maximizing CAGR
    - the common blocker across the strongest candidates was still the `validation / promotion` layer, especially rolling underperformance
- Durable implication:
  - future strict annual family discussions can now start from the new summary doc instead of reopening each search note one by one

### 2026-04-06 - Coverage 300/500/1000까지 넓혀도 strict annual target exact-hit는 확인되지 않았다

- Request topic:
  - the user asked to rerun the strict annual target search with wider presets after confirming the earlier search had effectively fixed `Coverage 100`
- Interpreted goal:
  - test whether `US Statement Coverage 300`, `500`, or `1000` could unlock a portfolio that satisfies:
    - `Historical Dynamic PIT Universe`
    - `2016-01-01 ~ 2026-04-01`
    - `top_n <= 10`
    - `CAGR >= 15%`
    - `Maximum Drawdown >= -20%`
    - `promotion != hold`
- Result:
  - `Coverage 300`: no exact-hit found
  - `Coverage 500`: no exact-hit found
  - `Coverage 1000`: no exact-hit surfaced within the current search window; strongest candidate remained inconclusive
  - strongest confirmed `Coverage 500` candidate:
    - `Value > Strict Annual`
    - `earnings_yield`, `ocf_yield`, `operating_income_yield`, `fcf_yield`
    - `month_end / interval 1 / top_n 9`
    - `benchmark = SPY`
    - `CAGR = 7.66%`
    - `MDD = -20.58%`
    - `promotion = hold`
- Durable implication:
  - widening statement coverage by itself did not resolve the target search
  - the next meaningful lever remains the validation / promotion / liquidity / benchmark-policy layer rather than coverage breadth alone

### 2026-04-06 - strict annual family에서 `real_money_candidate + SPY 초과 CAGR + MDD 25% 이내` exact-hit는 없었다

- Request topic:
  - the user asked to use sub-agents and find one portfolio across `Quality`, `Value`, and `Quality + Value` that satisfies:
    - `promotion = real_money_candidate`
    - `CAGR > SPY`
    - `Maximum Drawdown >= -25%`
- Interpreted goal:
  - keep the search inside the strict annual family surface
  - compare the three families fairly under:
    - `Historical Dynamic PIT Universe`
    - `2016-01-01 ~ 2026-04-01`
    - practical UI-reproducible settings
    - `top_n <= 10` first
- Result:
  - `Quality`: no exact-hit
  - `Value`: no exact-hit, but strongest family overall
  - `Quality + Value`: no exact-hit
  - strongest raw `real_money_candidate`:
    - `Value > Strict Annual`
    - default value factors
    - `CAGR = 29.89%`
    - `MDD = -29.15%`
  - strongest balanced near-miss:
    - `Value > Strict Annual`
    - `earnings_yield`, `ocf_yield`, `operating_income_yield`, `fcf_yield`
    - `CAGR = 15.84%`
    - `MDD = -17.42%`
    - but `promotion = hold`
- Durable implication:
  - under the current strict annual contract, the family search still splits into two separate winners:
    - a raw `real_money_candidate` with drawdown too deep
    - a balanced numeric candidate that remains blocked by `validation`

### 2026-04-06 - strongest Value raw winner를 다시 넣는 방법을 별도 backtest 가이드로 정리했다

- Request topic:
  - the user asked for a Markdown guide that explains how to configure the strongest `Value` portfolio in the backtest UI
- Interpreted goal:
  - leave one durable reproduction guide for the `Value > Strict Annual` raw winner
  - make the result easier to rerun without reopening multiple phase13 analysis notes
- Result:
  - created `.note/finance/phase13/PHASE13_VALUE_RAW_WINNER_BACKTEST_GUIDE.md`
  - the guide records:
    - `Value > Strict Annual`
    - `US Statement Coverage 100`
    - `Historical Dynamic PIT Universe`
    - default value factors
    - `month_end / rebalance_interval = 1 / top_n = 10`
    - `Trend Filter = off`
    - `Market Regime = off`
    - expected result:
      - `CAGR = 29.89%`
      - `MDD = -29.15%`
      - `promotion = real_money_candidate`
- Durable implication:
  - the strongest raw `Value` candidate can now be rerun directly from one guide document instead of being reconstructed from multiple search notes

### 2026-04-06 - phase 문서와 분리된 backtest 결과 전용 폴더를 도입하기로 했다

- Request topic:
  - the user suggested creating a separate folder that stores only Markdown files for backtest results and strategy/backtest summaries
- Interpreted goal:
  - reduce mixing between:
    - phase execution documents
    - durable backtest outcome reports
  - make past portfolio searches easier to find later
- Result:
  - created `.note/finance/backtest_reports/README.md`
  - created `.note/finance/backtest_reports/BACKTEST_REPORT_INDEX.md`
  - updated `AGENTS.md` and `FINANCE_DOC_INDEX.md` so future turns know to store reusable backtest result reports in the new folder
- Durable implication:
  - phase folders remain the home for execution management
  - the new backtest-reports folder becomes the home for reusable result summaries and rerun guides

### 2026-04-06 - Phase 13 backtest 결과 문서를 backtest_reports/phase13으로 재배치했다

- Request topic:
  - after agreeing with the separate backtest-results folder approach, the user asked to organize the Phase 13 backtest results there
- Interpreted goal:
  - keep Phase 13 execution documents in place
  - move reusable result reports to a dedicated result folder
  - avoid breaking the old paths immediately
- Result:
  - moved the main Phase 13 backtest-result documents into `.note/finance/backtest_reports/phase13/`
  - left short redirect stubs at the old `.note/finance/phase13/` paths
  - updated the report index and finance document index to point at the new canonical locations
- Durable implication:
  - future Phase 13 result review should start from `backtest_reports/phase13/`
  - old phase13 paths are now compatibility pointers rather than the canonical storage location

### 2026-04-06 - phase 기준 raw report보다 전략별 허브 문서가 더 낫다는 방향으로 backtest report 구조를 보강했다

- Request topic:
  - the user found the phase-based moved files awkward to browse and suggested strategy-specific report entry points
- Interpreted goal:
  - make backtest results easier to consume by strategy first
  - still preserve phase association and raw evidence documents
- Result:
  - created strategy hub Markdown files for:
    - `Quality > Strict Annual`
    - `Value > Strict Annual`
    - `Quality + Value > Strict Annual`
  - repositioned `phase13/` as the raw archive layer
  - updated the backtest report index so the recommended reading order starts from strategy hubs
- Durable implication:
  - future backtest-result reading should start from strategy hubs
  - phase folders remain useful as raw chronological archives, not as the primary reading surface

### 2026-04-06 - GTAA single form에서 universe payload 변수명이 어긋나던 regression을 수정했다

- Request topic:
  - running `GTAA` from the backtest page raised `NameError: name 'universe_mode' is not defined`
- Interpreted goal:
  - restore the GTAA single-strategy execution path without changing the new universe-input helper contract
- Result:
  - confirmed that `_render_gtaa_universe_inputs()` returns `_universe_mode`
  - fixed `_render_gtaa_form()` so the payload uses `_universe_mode` instead of the stale `universe_mode` name
- Durable implication:
  - GTAA single-form payload is now aligned with the helper return contract
  - this closes a regression introduced during the universe-input surface refactor

### 2026-04-07 - GTAA에서 non-hold이면서 SPY보다 좋은 practical candidate를 다시 찾았다

- Request topic:
  - the user clarified that the real ask was to search the `GTAA` strategy itself and save the result in the backtest-report folder
- Interpreted goal:
  - use sub-agents to search multiple GTAA ETF combinations from the DB-backed ETF list
  - find a candidate that satisfies:
    - `promotion != hold`
    - `deployment_readiness_status != blocked`
    - `CAGR > SPY`
    - `MDD better than SPY`
    - `2016-01-01` start
- Result:
  - practical final candidate:
    - tickers: `SPY, QQQ, GLD, LQD`
    - `top = 2`
    - `interval = 3`
    - `score horizons = 1M / 3M`
    - `risk_off_mode = cash_only`
    - `benchmark = SPY`
    - `CAGR = 14.7671%`
    - `MDD = -11.5626%`
    - `promotion = production_candidate`
    - `deployment = watchlist_only`
  - created:
    - `.note/finance/backtest_reports/phase13/PHASE13_GTAA_NONHOLD_SPY_OUTPERFORMANCE_SEARCH.md`
    - `.note/finance/backtest_reports/strategies/GTAA.md`
- Durable implication:
  - GTAA now has one documented practical reference candidate that both beats `SPY` on raw `CAGR / MDD` and avoids the `hold / blocked` state

### 2026-04-06 - Phase 13 테스트 체크리스트를 수정 이력과 현재 UI 기준으로 다시 맞췄다

- Request topic:
  - after several test-driven UX improvements during Phase 13 validation, the user asked to refresh the manual checklist based on the modified history
- Interpreted goal:
  - make the checklist match the current product surface rather than the earlier Phase 13 closeout snapshot
- Result:
  - updated `.note/finance/phase13/PHASE13_TEST_CHECKLIST.md`
  - added explicit checks for:
    - `Latest Backtest Run` guidance area
    - `Real-Money` internal tab structure
    - `Hold 해결 가이드 -> Liquidity Policy` connection
    - Korean explanatory copy for `Min Avg Dollar Volume 20D = 0.0M`
    - glossary-to-UI terminology consistency
- Durable implication:
  - future Phase 13 manual validation can now follow the actual current UI flow more directly

### 2026-04-07 - SPY drawdown 수치가 `-15%`인지 `-30%`인지 검증했다

- Request topic:
  - the user questioned whether `SPY` from January 2016 to the current window could really have only about `-15%` maximum drawdown and asked for confirmation
- Interpreted goal:
  - verify whether the previously quoted `-15.9042%` was a true daily `SPY` buy-and-hold drawdown or a sampled benchmark statistic inside a GTAA run
- Result:
  - raw daily `SPY` from DB price history (`2016-01-04 ~ 2026-04-02`) has `Maximum Drawdown = -33.72%`
  - the previously quoted `-15.9042%` came from `benchmark_summary_df` inside the documented GTAA candidate run
  - that GTAA benchmark used only `42` benchmark points from `2016-01-29 ~ 2026-04-02` because the strategy was configured with `option = month_end` and `interval = 3`
  - this means the earlier `-15.9042%` was a quarterly-sampled benchmark drawdown, not a full daily buy-and-hold drawdown
- Durable implication:
  - future comparisons against `SPY` should explicitly distinguish:
    - raw daily `SPY` buy-and-hold metrics
    - strategy-window sampled benchmark metrics inside a backtest result bundle

### 2026-04-07 - Promotion과 Shortlist 단계 및 승격 조건을 다시 정리했다

- Request topic:
  - the user asked for a clean explanation of the `promotion` and `shortlist` stages and what must change for a strategy to be promoted between those states
- Interpreted goal:
  - explain the current runtime contract using the actual code rules rather than only UI wording
- Result:
  - `promotion` has three stages:
    - `hold`
    - `production_candidate`
    - `real_money_candidate`
  - promotion is primarily determined by:
    - `benchmark_available`
    - `validation_status`
    - `benchmark_policy_status`
    - `etf_operability_status`
    - `liquidity_policy_status`
    - `validation_policy_status`
    - `guardrail_policy_status`
    - `universe_contract`
    - `price_freshness.status`
  - promotion transition rules:
    - `hold -> production_candidate`:
      remove `caution` / `unavailable` / `error` blockers, but `watch`, static-universe usage, or freshness warning may still remain
    - `production_candidate -> real_money_candidate`:
      benchmark must be available, validation/policy surfaces must all be `normal`, ETF operability must be `normal` for ETF strategies, universe must not be `static_managed_research`, and price freshness must not be warning/error
  - `shortlist` is downstream from promotion:
    - `promotion = hold` -> `shortlist = hold`
    - `promotion = production_candidate` -> `shortlist = watchlist`
    - `promotion = real_money_candidate` -> usually `paper_probation`
    - `promotion = real_money_candidate` -> `small_capital_trial` only when:
      - strategy is not ETF-family
      - drawdown guardrail is enabled
      - underperformance guardrail is enabled
      - benchmark is available
      - universe is not static managed research
      - `benchmark_contract = candidate_universe_equal_weight`
- Durable implication:
  - the practical minimum for a strategy to stop being "blocked for real use" is usually:
    - `promotion != hold`
    - `deployment != blocked`
  - but reaching `small_capital_trial` requires stricter shortlist preconditions than simply clearing `hold`

### 2026-04-07 - Guides 페이지에 Promotion/Shortlist 설명을 사용자 친화적으로 추가했다

- Request topic:
  - the user wanted the promotion and shortlist explanation surfaced directly in `Guides`
- Interpreted goal:
  - reduce the need to jump between glossary, checklist, and result tabs when understanding the real-money stage model
- Result:
  - added a new `실전 승격 흐름 빠른 설명` section to `Guides`
  - included:
    - `Promotion` stages
    - `Shortlist` stages
    - practical transition rules for moving upward
    - a direct UI reading path: `Backtest 결과 -> Real-Money -> 현재 판단`
  - also elevated `PHASE13_TEST_CHECKLIST.md` in the recommended document list
- Durable implication:
  - users now have an on-screen operator guide for stage interpretation without needing to infer the rules from glossary entries alone

### 2026-04-07 - Guides의 단계 상승 설명 탭 가독성을 다시 손봤다

- Request topic:
  - the user felt the `어떻게 다음 단계로 가나` section in `Guides` was not rendering cleanly enough and remained hard to read
- Interpreted goal:
  - keep the same content but make the transition logic visually easier to scan
- Result:
  - split the tab into two bordered sections for `Promotion` and `Shortlist`
  - broke the transition rules into shorter numbered step blocks
  - reduced the amount of long wrapped markdown under a single heading
- Durable implication:
  - the operator guide now better supports quick scanning during Phase 13 validation and real-money review

### 2026-04-07 - 상태값이 어디에 보이고 무엇을 바꿔야 하는지 UX를 더 직접적으로 보강했다

- Request topic:
  - the user pointed out that even after the stage explanation improved, it was still unclear:
    - where each `caution / unavailable / error` state is exposed
    - what concrete action should reduce each issue
- Interpreted goal:
  - turn the current guidance from "what to read" into "where to look and what to change"
- Result:
  - upgraded `Hold 해결 가이드` from a simple blocker/location/action table into a richer table with:
    - `항목`
    - `현재 상태`
    - `상태를 보는 위치`
    - `이 상태의 뜻`
    - `바로 해볼 일`
  - added a `상태는 어디에서 보나` section to `Guides`
  - added a `상태가 뜻하는 바` summary for `Watch / Caution / Unavailable / Error`
  - refreshed the Phase 13 checklist so this richer guidance is now part of manual validation
- Durable implication:
  - users can now trace a blocked promotion from result state -> exact UI location -> recommended fix without relying on inferred terminology

### 2026-04-07 - Guides의 상태 위치 목록 표기를 더 읽기 쉽게 다듬었다

- Request topic:
  - the user wanted the `상태는 어디에서 보나` list to show a clearer separator between the item name and the path
- Interpreted goal:
  - improve quick scanning without changing the underlying content
- Result:
  - changed the list formatting so each line reads as `단어: 확인 경로`
- Durable implication:
  - the guides page now uses a clearer visual rhythm for state-location mapping

### 2026-04-07 - real-money gate가 너무 빡빡한지와 통과 후 상태가 최종인지 다시 정리했다

- Request topic:
  - while reflecting on the Phase 12/13 work, the user asked whether repeated difficulty finding `promotion` / `shortlist` passing portfolios means the current real-money gate may be too strict, and whether passing those stages should be treated as the final state for real investing
- Interpreted goal:
  - distinguish between:
    - "the gate is so strict that no future search will ever pass"
    - "the system is doing its job, but more development and calibration are still needed before true live use"
- Result:
  - not finding many passing candidates does **not** mean no future backtest can pass
  - it does mean at least one of the following is likely true:
    - the current search space or family constraints are narrow
    - the current promotion / validation policy is conservative by design
    - some policy surfaces are still transitional and not yet the final live-deployment contract
  - in practice, repeated near-misses are a signal to study the blocker distribution, not to conclude the framework is broken immediately
  - current real-money interpretation is best read as:
    - `promotion / shortlist` = candidate gate
    - `probation / monitoring / deployment` = operating-readiness gate
  - therefore clearing `promotion != hold` and `shortlist` is important, but it is **not** the same thing as "ready for real capital at full confidence"
- Recommended framing:
  - if many strong portfolios repeatedly fail on the same validation/policy item, the next task should be gate calibration analysis rather than endless brute-force backtest search
  - the product is not yet at "fully finished live-investing platform" status
  - remaining work still naturally includes:
    - execution / portfolio action workflow
    - probation logging and monthly review workflow
    - richer PIT operability and execution-readiness policy
    - live deployment safeguards and actual capital-handling workflow
- Durable implication:
  - the current system should be understood as a strong candidate-evaluation and readiness-screening layer, not yet the final fully automated live-investment endpoint

### 2026-04-07 - ETF guardrail이 안 보이는 QA 이슈를 수정했다

- Request topic:
  - during Phase 13 checklist QA, the user found that `Underperformance Guardrail`, `Drawdown Guardrail`, and trigger metrics were not visible in `Real-Money > 실행 부담`, even though nearby sections such as `실행 계약 요약` and `ETF 운용 가능성` were visible
- Interpreted goal:
  - make the ETF guardrail surface visible and testable regardless of whether the guardrails are enabled or disabled
- Result:
  - changed the ETF guardrail surface so it is shown for ETF strategies even when both guardrails are disabled
  - `Execution Context` now also displays guardrail state as `ON/OFF`
  - trigger count / trigger share are shown consistently instead of disappearing with the whole section
- Durable implication:
  - Phase 13 checklist can now treat ETF guardrails as a stable visible contract rather than a conditional UI element that vanishes when disabled

### 2026-04-07 - 전략 Advanced Inputs를 그룹형 UX로 정리했다

- Request topic:
  - the user wanted strategy `Advanced Inputs` to keep basic contracts visible while grouping newer overlays and real-money controls so the UI would stay readable as more features are added
- Interpreted goal:
  - create a stable UX pattern that separates core strategy setup from optional overlays / execution contracts / guardrails and prevents future asymmetry between strategies
- Result:
  - single strategy ETF and strict annual forms now group additional controls into expanders such as `Overlay & Defensive Rules`, `Real-Money Contract`, and `Guardrails`
  - compare strategy-specific inputs were aligned to the same grouped structure for the same strategy families
- Durable implication:
  - future strategy UI growth should follow the grouped advanced-input pattern rather than adding more flat rows to each form

### 2026-04-07 - Quality family에서 Research variant를 active UI에서 제거했다

- Request topic:
  - the user wanted the unused `Research` variant removed from the `Quality` family surface
- Interpreted goal:
  - simplify the active Quality family so the UI focuses on currently used strict strategies instead of leaving an extra unused branch
- Result:
  - removed `Research` from the active `Quality` family variant catalog
  - preserved legacy `quality_snapshot` display labeling for older records
- Durable implication:
  - the current active Quality family should now be read as strict-only from the UI perspective, while the old broad quality path remains legacy code rather than an active product surface

### 2026-04-07 - Reference 그룹에 검색 가능한 Glossary 페이지를 추가했다

- Request topic:
  - the user wanted a page separate from `Guides` where current quant-program terms could be organized and searched more easily
- Interpreted goal:
  - keep `.note/finance/FINANCE_TERM_GLOSSARY.md` as the single durable source, but expose it inside the app as a searchable reference UI
- Result:
  - added `Reference > Glossary`
  - the page loads glossary sections from the Markdown file, separates document meta sections from term entries, and supports title/body search
  - related overview text, finance analysis doc, doc index, and Phase 13 checklist were updated to reflect the new surface
- Durable implication:
  - term definitions can keep living in one Markdown file while users browse them inside the product without leaving the app

### 2026-04-08 - 저장소 README와 README 유지 규칙을 추가했다

- Request topic:
  - the user wanted a Git-visible repository README and also wanted future implementation work to update that README as part of the normal workflow
- Interpreted goal:
  - give the repository a clear first-screen explanation for future collaborators while making README maintenance a durable project rule instead of a one-off task
- Result:
  - created a root `README.md` covering:
    - finance-centered scope
    - current console pages
    - implemented ingestion / backtest surfaces
    - project layout
    - quick-start commands
    - key finance reference docs
  - updated `AGENTS.md` so materially user-facing changes must review and update `README.md`
- Durable implication:
  - project overview drift should now be caught as part of normal implementation review rather than only after the README falls behind

### 2026-04-09 - Phase 13 QA 피드백에 맞춰 Guides와 glossary 설명을 더 보강했다

- Request topic:
  - the user felt the current Guide explanations were still too weak around:
    - what `Watch / Caution / Unavailable / Error` concretely mean
    - where `Hold 해결 가이드` actually appears
    - how to interpret `Probation / Monitoring`, `Rolling / Out-of-Sample Review`, `Deployment Readiness`, and `Strategy Highlights`
- Interpreted goal:
  - make the product explain not just labels, but also source location, common cause, and practical meaning so QA can continue without guesswork
- Result:
  - expanded the `상태가 뜻하는 바` section in `Guides` into a richer status table with meaning, common cause, and first action
  - added explicit path explanations for `Hold 해결 가이드` and compare-only `Strategy Highlights`
  - clarified the compare `Strategy Highlights` caption inside the product
  - added missing glossary entries for probation/monitoring/review/deployment surface terms and deployment checklist counts
  - updated the Phase 13 checklist to test these exact paths and glossary links
- Durable implication:
  - the operator-facing explanation layer is now much closer to the actual screen structure, reducing the gap between checklist language and runtime UI

### 2026-04-09 - Guides에 단계형 프로그램 사용 가이드를 추가했다

- Request topic:
  - the user wanted a practical step-by-step guide inside `Guides` explaining how the program should be used from testing toward commercialization-ready candidate review
- Interpreted goal:
  - move beyond term explanation and provide an operator runbook that answers "what do we do first, next, and last?"
- Result:
  - added a numbered `1단계 ~ 8단계` guide to `Guides`
  - the flow now explicitly covers:
    - refresh
    - single backtest
    - real-money interpretation
    - hold resolution
    - compare
    - history/reporting
    - probation/monitoring
    - final commercialization-candidate judgment
  - updated Phase 13 checklist, finance analysis doc, and README wording to reference the new stepwise guide
- Durable implication:
  - `Guides` is now not only a glossary/interpretation surface but also a lightweight in-product operator runbook

### 2026-04-09 - Phase 14 kickoff 준비와 보류 논의 재등록

- Request topic:
  - the user wanted to finish Phase 13 and prepare the project for Phase 14, while checking whether the previously deferred discussion was still remembered
- Interpreted goal:
  - open the next phase explicitly and anchor it around the deferred real-money gate calibration discussion instead of letting that concern remain only in chat
- Result:
  - confirmed the deferred topic:
    - repeated `promotion / shortlist` non-pass outcomes and whether the current real-money gate is too conservative
  - created Phase 14 planning documents focused on:
    - gate blocker distribution audit
    - promotion / shortlist calibration review
    - deployment workflow bridge
    - ETF PIT operability later-pass planning
  - updated roadmap, doc index, and top-level overview status to reflect Phase 14 kickoff
- Durable implication:
  - Phase 14 should now be read as the point where the project shifts from building interpretation surfaces to calibrating them and connecting them to actual operator workflow

### 2026-04-09 - Phase 14 representative rerun evidence로 gate blocker 분포를 다시 고정했다

- Request topic:
  - start Phase 14 proper and proceed with the `real-money gate calibration` workstream, using sub-agents if helpful
- Interpreted goal:
  - move from a qualitative Phase 13 impression ("good candidates still become hold") to a first-pass evidence set that shows which blockers actually recur under current code
- Result:
  - used the current runtime gate logic plus a representative `9`-case rerun set across strict annual and ETF families
  - confirmed the first-pass blocker distribution more concretely:
    - `hold` cases were dominated by `validation_status = caution`
    - strict annual near-miss cases repeatedly added `validation_policy_status = caution`
    - ETF aggressive near-miss cases were additionally blocked by `etf_operability_status = caution`
  - confirmed an important layer split:
    - `Value` raw winner still reaches `real_money_candidate` even with `rolling = watch` and `out_of_sample = caution`
    - this means current promotion logic is driven more directly by `validation / validation_policy / benchmark/liquidity/operability` than by rolling/OOS review alone
- Durable implication:
  - Phase 14 calibration should focus first on:
    - `validation_status`
    - `validation_policy_status`
    - ETF `etf_operability_status`
  - and it should treat `promotion` vs `deployment` as distinct gates rather than one flat pass/fail ladder

### 2026-04-09 - factor 부족이 repeated hold의 원인인지 calibration review에서 분리했다

- Request topic:
  - continue Phase 14 and assess whether repeated `hold` outcomes might be happening because the current program exposes too few factors, and whether broader factor expansion plus more backtests would be a better next move
- Interpreted goal:
  - avoid overfitting the wrong problem by separating:
    - current gate calibration issues
    - current strategy search-space limits
- Result:
  - reviewed the current strict factor surface and factor storage scope
  - confirmed current strict UI already exposes:
    - `Quality` options: `10`
    - `Value` options: `13`
  - confirmed current factor storage is broader than the active UI and already contains additional candidates such as:
    - `interest_coverage`
    - `ocf_margin`
    - `fcf_margin`
    - `gross_profit_growth`
    - `op_income_growth`
    - `net_income_growth`
    - `asset_growth`
    - `debt_growth`
    - `fcf_growth`
    - `shares_growth`
    - `liquidation_value`
    - `net_debt_to_equity`
    - `gpa`
  - but concluded that factor scarcity is not the first-order explanation for current repeated `hold`, because:
    - current factor sets already produce `real_money_candidate` and `production_candidate` cases
    - repeated `hold` aligns much more directly with `validation_status`, `validation_policy_status`, and ETF `etf_operability_status`
- Durable implication:
  - factor expansion remains worthwhile, but it should be treated as a later controlled workstream after calibration, not as the first universal fix for repeated `hold`

### 2026-04-09 - Phase 14 first-pass blocker audit should use representative reports plus richer future history records

- Request topic:
  - the user asked to actually begin Phase 14 work
- Interpreted goal:
  - move from planning into a concrete first work unit that explains repeated `hold / blocked` outcomes and sets up better evidence collection for later calibration work
- Result:
  - audited the current real-money gate logic and documented the first-pass blocker pattern in:
    - `.note/finance/phase14/PHASE14_GATE_BLOCKER_DISTRIBUTION_AUDIT_FIRST_PASS.md`
  - the strongest repeated blocker in strict annual family was recorded as:
    - `validation`
    - `validation_policy`
    - related rolling underperformance review
  - the more distinct ETF-family blocker was recorded as:
    - `ETF operability`
    - plus practical validation interpretation
  - identified a structural evidence gap:
    - persisted backtest history did not keep gate states, so later aggregate audit would remain weaker than necessary
  - fixed that by upgrading new history records to carry a `gate_snapshot`
- Durable implication:
  - Phase 14 calibration discussion should now be based on two layers:
    - representative candidate case studies from Phase 13 reports
    - newly accumulated history records that persist gate-status snapshots for later aggregate analysis

### 2026-04-10 - real-money contract 값의 의미와 영향 설명을 UI reference에 추가했다

- Request topic:
  - explain what the values inside `Real-Money Contract` mean, why they are necessary, and how they affect interpretation, and expose that explanation in the UI through `Reference`, `Guides`, or `Glossary`
- Interpreted goal:
  - reduce operator confusion around real-money inputs by moving from raw field labels to an in-app explanation layer
- Result:
  - added `Guides > Real-Money Contract 값 해설`
  - grouped the explanation by:
    - common inputs
    - strict annual-specific inputs
    - ETF-specific inputs
    - recommended reading order
  - added form-level pointers so each `Real-Money Contract` block now tells the user where to find the explanation again
  - expanded glossary coverage to include:
    - `Real-Money Contract`
    - `Benchmark Ticker`
    - `Benchmark Contract`
    - `Min Benchmark Coverage`
    - `Min Net CAGR Spread`
    - `Min Liquidity Clean Coverage`
    - `Max Underperformance Share`
    - `Min Worst Rolling Excess`
    - `Max Strategy Drawdown`
    - `Max Drawdown Gap vs Benchmark`
    - `Min ETF AUM ($B)`
    - `Max Bid-Ask Spread (%)`
- Durable implication:
  - the program now explains not just status outputs, but also the meaning and effect of the real-money input contract that produces those outputs

### 2026-04-10 - strict annual 유동성 판단은 close x volume 기반 20일 평균 거래대금으로 한다

- Request topic:
  - clarify exactly how liquidity is checked in the current program and whether it uses OHLCV `close * volume`
- Interpreted goal:
  - make the strict annual liquidity rule concrete enough that the operator understands what data is being used and how the policy status is produced
- Result:
  - confirmed that strict annual liquidity filtering uses DB-backed price history and computes:
    - `dollar_volume = close * volume`
    - `avg_dollar_volume_20d = rolling_mean(dollar_volume, 20 trading days)`
  - this series is built in:
    - `finance/sample.py`
  - each rebalance snapshot then checks whether the symbol's trailing 20-day average dollar volume is at least:
    - `Min Avg Dollar Volume 20D ($M) * 1,000,000`
  - symbols that fail are excluded at rebalance time and counted as:
    - `Liquidity Excluded Ticker`
    - `Liquidity Excluded Count`
  - the later `Liquidity Policy` status is not based on raw OHLCV alone, but on how often the strategy passes this filter across rebalance rows:
    - `liquidity_clean_coverage`
    - compared against `promotion_min_liquidity_clean_coverage`
- Durable implication:
  - strict annual liquidity is currently a two-step contract:
    - candidate-level screen using `close * volume` 20-day average dollar volume
    - strategy-level promotion interpretation using liquidity clean coverage

### 2026-04-10 - strict annual 유동성 field tooltip에 계산식과 clean coverage 의미를 넣었다

- Request topic:
  - put the actual liquidity explanation into the small field tooltip/help bubble in the strict annual form
- Interpreted goal:
  - let the operator understand the liquidity rule at the point of input, not only later in guides or result interpretation
- Result:
  - updated the `Min Avg Dollar Volume 20D ($M)` tooltip to say it uses:
    - OHLCV `close × volume`
    - trailing 20-day average dollar volume
  - updated the `Min Liquidity Clean Coverage (%)` tooltip to explain:
    - symbol-level liquidity screen first
    - then strategy-level `Liquidity Policy` interpretation using clean coverage
- Durable implication:
  - the strict annual liquidity contract is now described directly at the field where the user sets it

### 2026-04-10 - strict annual robustness threshold tooltip에 rolling 개념과 해석을 넣었다

- Request topic:
  - improve the tooltip/help text for `Max Underperformance Share`, `Min Worst Rolling Excess`, `Max Strategy Drawdown`, and `Max Drawdown Gap vs Benchmark`, and clarify what `rolling` means
- Interpreted goal:
  - make the robustness thresholds understandable at the point of input instead of forcing the operator to infer the semantics from labels alone
- Result:
  - updated the strict annual form tooltips so each threshold now explains:
    - what is being measured
    - what kind of weakness it is trying to prevent
  - added an inline caption that defines `rolling 구간` as a moving comparison window
  - added `Rolling Window` to the glossary as a durable operator-facing term
- Durable implication:
  - users can now read the robustness contract directly in the form and understand how those thresholds connect to promotion interpretation

### 2026-04-10 - current real-money default는 완전히 과보수적이라기보다 validation/operability 중심의 보수적 gate로 해석하는 편이 맞다

- Request topic:
  - assess whether the current default `Real-Money Contract` values are too conservative, and whether Phase 14 work is already considering that possibility
- Interpreted goal:
  - separate two questions:
    - are the defaults so strict that almost no strategy can pass?
    - or are they reasonable first-pass defaults that still need family-specific calibration review?
- Result:
  - current evidence does **not** support the claim that the defaults are universally too conservative
  - reasons:
    - representative rerun set still produced
      - `real_money_candidate = 1`
      - `production_candidate = 2`
    - so the gate is not structurally impossible to pass
    - repeated `hold` aligned more with
      - `validation_status`
      - `validation_policy_status`
      - ETF `etf_operability_status`
      than with every threshold simply being globally too tight
  - practical reading:
    - current defaults are better described as
      - `benchmark-relative consistency` oriented
      - `operability-aware`
      - intentionally conservative first-pass values
    - not obviously "too conservative everywhere"
  - but family-level calibration still remains necessary:
    - strict annual likely needs closer review around validation / validation-policy interpretation
    - ETF family likely needs closer review around operability thresholds and validation watch/caution boundary
- Durable implication:
  - Phase 14 should continue as a calibration phase, not as a blanket relaxation phase

### 2026-04-10 - Gate Calibration 용어를 glossary에 추가했다

- Request topic:
  - add `gate calibration` itself to the glossary after clarifying what the Phase 14 workstream means
- Interpreted goal:
  - make the core Phase 14 concept discoverable from the UI reference layer instead of leaving it only in chat
- Result:
  - added `Gate Calibration` to `.note/finance/FINANCE_TERM_GLOSSARY.md`
  - defined it as the work of tuning pass/hold thresholds so they are neither universally too strict nor too loose
- Durable implication:
  - the app glossary can now explain the Phase 14 core term directly to operators

### 2026-04-10 - near-miss candidate case study로 Phase 14 calibration 질문을 더 좁혔다

- Request topic:
  - continue Phase 14 after the controlled factor expansion shortlist and proceed with the next concrete workstream
- Interpreted goal:
  - move from blocker distribution counts to representative candidate case reading so the next calibration experiment can be chosen more precisely
- Result:
  - created:
    - `.note/finance/phase14/PHASE14_NEAR_MISS_CANDIDATE_CASE_STUDY_FIRST_PASS.md`
  - re-read representative cases:
    - `Value` balanced exact-hit hold
    - `Quality` SPY-dominance near miss
    - `GTAA` practical non-hold
    - `GTAA` aggressive near miss
  - concluded:
    - strict annual near-miss is still mainly a `validation / validation_policy` calibration problem
    - ETF near-miss is more about `operability` plus the practical `watch/caution` boundary
- Durable implication:
  - the next Phase 14 experiment should be family-specific sensitivity review rather than blanket threshold relaxation

### 2026-04-10 - controlled factor expansion first pass에서는 sign 해석이 비교적 명확한 small-set만 먼저 연다

- Request topic:
  - proceed with Phase 14 after calibration review and move into the next active workstream
- Interpreted goal:
  - widen the strict annual search space carefully without mixing calibration review with a large uncontrolled factor explosion
- Result:
  - created a controlled shortlist document at:
    - `.note/finance/phase14/PHASE14_CONTROLLED_FACTOR_EXPANSION_SHORTLIST_FIRST_PASS.md`
  - opened only a small first-pass set in the strict annual UI:
    - Quality:
      - `interest_coverage`
      - `ocf_margin`
      - `fcf_margin`
      - `net_debt_to_equity`
    - Value:
      - `liquidation_value`
  - deliberately deferred harder candidates such as:
    - `dividend_payout`
    - `gpa`
    - growth family factors
  - because their sign semantics or family placement are more ambiguous and would mix calibration with a broader strategy redesign
- Durable implication:
  - Phase 14 factor expansion is now a controlled widening step, not a blanket release of every stored factor

### 2026-04-10 - Phase 14 sensitivity review는 strict annual과 ETF에서 서로 다른 blocker를 보여줬다

- Request topic:
  - continue Phase 14, keep work moving efficiently, and explicitly record that sub-agents should be used when they help but are not mandatory
- Interpreted goal:
  - progress from the general calibration review into evidence-backed sensitivity work, while also updating repo guidance for future parallel investigation
- Result:
  - added AGENTS guidance:
    - use sub-agents when a workstream can be split into independent tracks
    - proceed directly when sub-agents are unnecessary or the current session does not make them practical
  - created:
    - `.note/finance/phase14/PHASE14_STRICT_ANNUAL_VALIDATION_POLICY_SENSITIVITY_REVIEW_FIRST_PASS.md`
    - `.note/finance/phase14/PHASE14_ETF_OPERABILITY_SENSITIVITY_REVIEW_FIRST_PASS.md`
  - strict annual rerun evidence showed:
    - relaxing `promotion_min_worst_rolling_excess_return` can normalize `validation_policy_status`
    - but exact-hit hold and quality near-miss still stay `hold` because fixed internal `validation_status` remains `caution`
  - ETF rerun evidence showed:
    - practical GTAA is stable across AUM/spread threshold sweeps
    - aggressive GTAA remains `hold` even when AUM/spread are effectively disabled
    - its repeated blocker is `etf_operability_partial_data_coverage`
- Durable implication:
  - next calibration work should target:
    - strict annual `validation_status` fixed thresholds
    - ETF partial-data coverage interpretation
  - not blanket relaxation of every configurable threshold

### 2026-04-10 - Phase 14 다음 calibration은 threshold 완화가 아니라 family별 해석 규칙 설계에 더 가깝다

- Request topic:
  - continue Phase 14 again after the sensitivity review
- Interpreted goal:
  - take the next concrete step so the phase moves from broad threshold discussion into more precise family-specific experiment planning
- Result:
  - created:
    - `.note/finance/phase14/PHASE14_STRICT_ANNUAL_VALIDATION_STATUS_FIXED_THRESHOLD_REVIEW_FIRST_PASS.md`
    - `.note/finance/phase14/PHASE14_ETF_OPERABILITY_DATA_COVERAGE_INTERPRETATION_REVIEW_FIRST_PASS.md`
  - main analysis result:
    - strict annual:
      - the most direct current blocker is the internal `worst rolling excess <= -15%` severe boundary
      - because a single severe signal already makes `validation = caution`
      - so the next useful experiment is not policy relaxation alone, but reviewing the fixed severe / caution rule itself
    - ETF:
      - the most direct current blocker is `partial data coverage` interpretation
      - practical GTAA already passes operability cleanly
      - aggressive GTAA remains `hold` even when AUM/spread thresholds are effectively disabled
      - so the next useful experiment is not another threshold sweep, but reviewing `data_coverage < 75%`, missing-data semantics, and denominator choice
- Durable implication:
  - Phase 14 is now ready to move into a family-specific threshold experiment design step instead of another generic relaxation pass

### 2026-04-10 - Phase 14 closeout은 threshold 실행이 아니라 bounded next-step 정의까지로 보는 것이 맞다

- Request topic:
  - carry Phase 14 through to the end and share the checklist at completion
- Interpreted goal:
  - close Phase 14 in a way that leaves the real-money gate workstream understandable, bounded, and ready for the next implementation phase
- Result:
  - created:
    - `.note/finance/phase14/PHASE14_FAMILY_SPECIFIC_THRESHOLD_EXPERIMENT_DESIGN_FIRST_PASS.md`
    - `.note/finance/phase14/PHASE14_DEPLOYMENT_WORKFLOW_BRIDGE_FIRST_PASS.md`
    - `.note/finance/phase14/PHASE14_PIT_OPERABILITY_LATER_PASS_DECISION.md`
    - `.note/finance/phase14/PHASE14_TEST_CHECKLIST.md`
    - `.note/finance/phase14/PHASE14_COMPLETION_SUMMARY.md`
    - `.note/finance/phase14/PHASE14_NEXT_PHASE_PREPARATION.md`
  - updated the active TODO board, roadmap, and doc index so Phase 14 now reads as `practical closeout / manual_validation_pending`
  - fixed the main handoff decision:
    - next work should be one of:
      - family-specific threshold experiment execution
      - operator workflow persistence
      - PIT operability implementation
    - not another blanket threshold discussion
- Durable implication:
  - Phase 14 should now be read as the phase that made the real-money gate explainable and bounded
  - the next phase should implement selected calibration or workflow changes, not rediscover where the blockers are

### 2026-04-10 - Phase 14 이후 current runtime strict annual family를 다시 돌리면 strongest candidate는 여전히 Value다

- Request topic:
  - after the Phase 14 improvements, rerun `Quality`, `Value`, and `Quality + Value` strict annual families and organize which strategies are now closest to practical use
- Interpreted goal:
  - check whether current runtime has moved any strict annual family closer to
    - `promotion = real_money_candidate`
    - `shortlist >= paper_probation`
    - `deployment != blocked`
  - and leave a durable backtest report rather than only a chat answer
- Result:
  - created:
    - `.note/finance/backtest_reports/phase14/PHASE14_STRICT_ANNUAL_NONHOLD_CANDIDATE_REFRESH.md`
  - main rerun conclusions:
    - `Value`:
      - current best candidate is still the default value factor set with `SPY` benchmark
      - `promotion = real_money_candidate`
      - `shortlist = paper_probation`
      - `deployment = review_required`
      - `CAGR = 29.89%`
      - `MDD = -29.15%`
    - `Quality + Value`:
      - current strongest non-hold is default blend with `candidate_universe_equal_weight` benchmark
      - `promotion = production_candidate`
      - `shortlist = watchlist`
      - `deployment = review_required`
      - `CAGR = 28.51%`
      - `MDD = -28.35%`
    - `Quality`:
      - current strongest non-hold is `capital_discipline` with `LQD` benchmark
      - `promotion = production_candidate`
      - `shortlist = watchlist`
      - `deployment = review_required`
      - `CAGR = 14.84%`
      - `MDD = -27.97%`
- Durable implication:
  - Phase 14 improvements did not change the strongest strict annual family ordering:
    - `Value` remains the only current exact candidate that reaches `real_money_candidate / paper_probation`
    - `Quality` and `Quality + Value` can be documented as current non-hold families, but still stop at `production_candidate / watchlist`

### 2026-04-13 - strongest Value 후보는 허브 문서보다 전략 구성 one-pager가 더 읽기 쉽다

- Request topic:
  - ask whether there is a single concrete strategy-summary document for the strongest `Value` portfolio, not just linked related documents
- Interpreted goal:
  - make the strongest `Value` candidate understandable in one place without requiring the user to jump across hub/search/archive docs
- Result:
  - created:
    - `.note/finance/backtest_reports/strategies/VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md`
  - the new one-pager fixes:
    - exact family / variant
    - universe / period
    - factor set
    - real-money contract inputs
    - benchmark / overlay settings
    - current expected statuses and performance
- Durable implication:
  - strongest `Value` candidate is now documented in a form that is immediately reusable for portfolio reconstruction, not only for report navigation
