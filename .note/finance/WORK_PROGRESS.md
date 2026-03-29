# Finance Work Progress

## Purpose
This file is the running implementation log for `finance` package work.

Record here:
- active development tasks
- major milestones
- important implementation decisions
- completion status

Keep entries append-only and concise.

## Entries

### 2026-03-11
- Initialized `.note/finance` as the top-level note location for `finance` work.
- Moved the comprehensive finance analysis document from `finance/docs/` to `.note/finance/`.
- Established progress logging and question/analysis logging as standard workflow requirements in `AGENTS.md`.
- Created initial Codex skills for:
  - finance-doc-sync
  - finance-db-pipeline
  - finance-strategy-implementation
  - finance-factor-pipeline
- Reviewed current implementation status for:
  - OHLCV DB ingestion
  - financial statement DB ingestion
- Added a dedicated review note for implemented ingestion features and remaining gaps.
- Added a planning note for a future data-collection UI layer:
  - web vs desktop options
  - recommended architecture
  - staged implementation strategy
- Added a step-by-step internal web app development guide with:
  - implementation order
  - goals by phase
  - outputs
  - validation criteria
- Started Phase 1 internal web app implementation by fixing the first-release scope.
- Defined Phase 1 as:
  - Streamlit internal admin app
  - OHLCV ingestion
  - fundamentals ingestion
  - factor calculation
  - result visibility
- Completed Phase 1 interface planning for the job wrapper layer.
- Fixed the first wrapper targets as:
  - run_collect_ohlcv
  - run_collect_fundamentals
  - run_calculate_factors
- Added the first executable job wrapper module under `app/jobs/`.
- Implemented:
  - common symbol parsing
  - common result payload builder
  - OHLCV collection wrapper
  - fundamentals collection wrapper
  - factor calculation wrapper
- Added the first Streamlit web app shell under `app/web/`.
- Connected the first three buttons to the job wrappers:
  - OHLCV collection
  - fundamentals ingestion
  - factor calculation
- Added shared input controls and in-session recent run display.
- Reviewed the OHLCV button behavior after UI testing.
- Identified the main issue as synchronous execution without visible progress feedback.
- Improved the UI by adding Streamlit spinners for all three job buttons.
- Disabled yfinance download progress-bar output in the OHLCV path.
- Added log visibility to the Streamlit admin UI.
- Added failure CSV preview to the Streamlit admin UI.
- Phase 1 app now supports:
  - job execution
  - recent run visibility
  - recent log inspection
  - failure file preview
- Added a first composite pipeline wrapper for the core sequence:
  - OHLCV
  - fundamentals
  - factors
- Added a `Run Core Pipeline` button to the Streamlit admin UI.
- Added pipeline step summaries to the result detail view.
- Added persistent web-app run history storage as JSONL under `.note/finance/`.
- Added a persistent run history table to the Streamlit admin UI.
- Extended the admin UI to cover more of the finance ingestion surface.
- Added:
  - asset profile collection wrapper and button
  - financial statement ingestion wrapper and button
- Improved the admin UI guidance text.
- Added explicit job-level precondition and input-scope explanations to reduce operator confusion.
- Added preflight validation helpers for:
  - symbol presence
  - factor prerequisites in MySQL
  - asset profile universe-table readiness
- Added validation messages to the Streamlit UI before execution.
- Tightened symbol validation so obviously invalid tickers do not execute ingestion jobs.
- Changed zero-row ingestion outcomes to fail instead of looking like partial success.
- Started the UX-cleanup phase.
- Reorganized sidebar inputs by job context.
- Added button disabling for blocking validation errors.
- Moved from shared sidebar inputs toward job-local inputs in each execution card.
- Reduced ambiguity about which fields affect which jobs.
- Added symbol presets and period presets for repeated admin use.
- Started moving the UI toward faster repeated operation instead of manual re-entry.
- Improved execution-result visibility with clearer failure-oriented messaging.
- Added failed-symbol counts to result summaries and recent-run views.
- Added DB-backed symbol source selection for symbol-based jobs.
- Users can now resolve symbols from NYSE tables or filtered asset-profile universes instead of typing all symbols manually.
- Added visible DB/table write-target mapping to the admin UI.
- Each job card now shows which MySQL tables it writes to.
- Added large-run UX safeguards.
- The app now warns on large symbol counts, shows estimated runtime when possible, and requires confirmation for very large runs.

- Added a global single-job execution lock to the Streamlit admin UI.
- Switched button behavior from direct execution to scheduled execution so the UI can show a running banner and disable all execution buttons while a job is active.
- Added a top-level running banner and a latest-completed-run summary to make long-running ingestion jobs easier to monitor.

- Expanded OHLCV/UI period presets to include `1d` and a UI-level `7d` rolling window alias.
- Implemented `7d` handling as derived `start/end` dates so it works safely with the existing yfinance ingestion path.

- Removed the large-run confirmation checkbox from the Streamlit admin UI; large runs now show warnings and estimates without an extra confirmation gate.
- Extended the running banner to show the current target-symbol count for symbol-based jobs.

- Restored per-card running feedback in the Streamlit admin UI while keeping the top-level global running banner.
- Moved scheduled job execution into the matching job card so loading feedback appears in the local card context again.

- Added live batch-progress callbacks to the OHLCV ingestion path.
- Added Streamlit progress-bar rendering for large OHLCV runs and for the OHLCV stage inside the core pipeline when the symbol count is 100 or more.

- Adjusted the Streamlit execution flow so non-run panels keep rendering while a job is active; only run controls remain blocked.
- The right-side recent-run, history, log, and failure panels now stay visible during execution.

- Added a dedicated Phase 2 plan document covering operational pipeline restructuring, settings externalization, backtest loader design, and strategy UI preparation.

- Updated the Phase 2 plan to treat detailed financial statement tables as a first-class loader source for long-horizon backtests and custom factor derivation, based on the historical-depth limitations of the yfinance summary datasets.

- Started Phase 2 implementation by separating routine operational pipelines from manual component jobs.
- Added new pipeline wrappers for daily market update, weekly fundamental refresh, extended statement refresh, and metadata refresh.
- Added a new Operational Pipelines section to the Streamlit admin UI while keeping the existing manual job cards.

- Simplified the operational Extended Statement Refresh UI so `freq` is no longer separately selectable; it now follows the selected statement period type automatically.

- Started the Phase 2 execution-history hardening work.
- Added run metadata capture for symbol source, symbol count, and key input parameters so future history analysis can reconstruct how each job was executed.

- Added a current-chapter TODO note for active PHASE2 work, separating immediate implementation tasks from the broader Phase 2 plan.

- Reworked the current PHASE2 chapter TODO note into a larger status-based execution board with grouped major tasks and per-item checklist states.

- Expanded the current PHASE2 TODO board so each checklist item now includes a short explanation of what the work item actually does.

- Completed TODO item B-6 by adding `pipeline_type` to web-app run metadata for both operational pipelines and manual jobs.

- Completed TODO item B-7 by adding `execution_mode` to run metadata and exposing it in both recent-run and persistent history views.

- Completed TODO item B-8 by adding `execution_context` to run metadata and surfacing it in recent-run and persistent-history views.

- Completed TODO item B-9 by making Persistent Run History explicitly show execution mode, pipeline type, source, context, and parameter summary in a more readable table layout.

- Completed TODO item B-10 by reviewing the existing JSONL run history samples and normalizing legacy records during load/append with a schema version and inferred run metadata.

- Completed TODO item A-7 by adding recommended execution cadence guidance to each operational pipeline card in the Streamlit admin UI.

- Completed TODO item A-8 by adding recommended symbol-source guidance to each operational pipeline card.

- Completed TODO item A-9 by clarifying in the UI that Operational Pipelines are the default routine path and Manual Jobs are for exceptions, partial reruns, and fine-grained control.

- Completed TODO item A-10 by reviewing and adjusting operational defaults: Daily now defaults to NYSE Stocks + 1mo + 1d, Weekly defaults to quarterly refresh on NYSE Stocks, and Extended Statement Refresh defaults to Profile Filtered Stocks + annual + 8 periods.

- Completed TODO item C-1 by extracting the current hardcoded-constant inventory into a dedicated config externalization note.

- Completed TODO item C-2 by classifying externalization targets into immediate, next, later, and not-recommended groups inside the config inventory note.

- Completed TODO item C-3 by fixing the future runtime config path to `config/finance_web_app.toml`.

- Completed TODO item C-4 by drafting the first `config/finance_web_app.toml` structure, sections, and staged implementation order in the config externalization inventory note.

- Completed TODO item D-2 by defining the first backtest-loader function draft, covering universe, price, fundamentals, factors, and detailed financial statement loaders.

- Completed TODO item D-3 by documenting a shared input contract for universe, price, fundamentals, factor, and detailed-statement loaders, including precedence rules for `symbols` vs `universe_source`, date-range handling, `freq` vs `timeframe`, and snapshot-style `as_of_date` usage.

- Completed TODO item D-4 by separating point-in-time guidance into a dedicated loader-design note, covering look-ahead bias risks, `period_end` vs availability timing, staged fallback rules, and table-specific handling for fundamentals, factors, and detailed financial statements.

### 2026-03-18
- Started detailed financial statement ingestion review focused on point-in-time availability fields and the actual EDGAR payload shape behind `nyse_financial_statement_labels` / `nyse_financial_statement_values`.
- Verified by direct EDGAR API inspection on representative symbols (`AAPL`, `MSFT`, `JPM`, `XOM`, `O`) that raw fact objects include:
  - actual `period_end`
  - `filing_date`
  - `form_type`
  - `accession`
  - filing-level `acceptance_datetime` via the filings endpoint
- Identified the main design gap in the old implementation:
  - `Company(...).income_statement(..., as_dataframe=True)` drops filing metadata
  - inferred `FY 2025 -> 2025-12-31` style parsing is wrong for non-calendar fiscal year issuers
  - the old `uk_fin(symbol, freq, period_end, statement_type, label)` key can collapse different filings for the same accounting period
- Reworked detailed financial statement ingestion to use raw EDGAR facts plus filing metadata instead of only the wide statement DataFrame.
- Added `finance_fundamental.nyse_financial_statement_filings` as a human-inspectable filing ledger keyed by `(symbol, accession_no)`.
- Expanded `nyse_financial_statement_values` to store:
  - `period_start`
  - actual `period_end`
  - `source_period_type`
  - `fiscal_period`
  - `concept`
  - `taxonomy`
  - `unit`
  - `available_at`
  - `report_date`
  - `form_type`
  - `accession_no`
  - audit/restatement/quality metadata
- Expanded `nyse_financial_statement_labels` to store latest concept and filing metadata for easier operator review.
- Added schema/index migration logic so existing environments can move from the old value-row uniqueness to filing-aware uniqueness.
- Added reusable inspection/sample helpers for detailed financial statement source review and updated the Streamlit write-target captions to include the new filings table.
- Verified locally that the new raw-fact path produces:
  - correct non-calendar `period_end` values for issuers like `AAPL` and `MSFT`
  - populated `accepted_at` / `available_at`
  - filing-aware `accession_no`
  - bounded latest-period filtering via the existing `periods` parameter
- Ran live MySQL verification on `finance_fundamental` with:
  - `AAPL`, `MSFT` annual 2 periods
  - `AAPL` quarterly 3 periods
- Confirmed in MySQL that:
  - `nyse_financial_statement_filings` was created and populated

  - backfill research-first universes first
  - defer DB-level strict constraints until coverage improves
- Updated the loader design notes to explicitly position `nyse_financial_statement_labels` as a summary layer and keep future strict PIT statement loaders values-centered.
- Added a strict PIT loader query draft covering:
  - accession-bearing row filters
  - `available_at <= as_of_date` snapshot rules
  - latest-available ordering by `available_at`, `period_end`, and `accession_no`
- Decided that the early-stage `nyse_financial_statement_labels` / `nyse_financial_statement_values` design was worth cleaning up immediately rather than preserving legacy compromises.
- Tightened `nyse_financial_statement_values` into a stricter raw ledger:
  - `concept`, `unit`, `available_at`, and `accession_no` are now required in the schema
  - ingestion skips rows that cannot satisfy that identity
- Re-centered `nyse_financial_statement_labels` around concept identity by changing it to a `(symbol, statement_type, concept, as_of)` summary key.
- Dropped and recreated the local `nyse_financial_statement_labels` / `nyse_financial_statement_values` tables, then reingested `AAPL` and `MSFT` annual sample rows successfully.
- Added a top-level phase-management structure for future finance work:
  - a master roadmap document
  - a finance document index
  - updated project instructions in `AGENTS.md` to prefer phase-based execution and documentation
- Reorganized `.note/finance/` so phase-specific documents now live under:
  - `phase1/`
  - `phase2/`
  - `phase3/`
  while cross-phase documents remain at the `.note/finance/` root.
- Closed Phase 2 with a dedicated completion summary document.
- Opened Phase 3 with:
  - a loader/runtime plan document
  - a first chapter TODO board
- Updated the master roadmap and finance document index so the project now reflects:
  - Phase 2 completed
  - Phase 3 in progress
- Completed the first Phase 3 task by fixing the loader naming policy:
  - base names for broad research loaders
  - `*_snapshot_strict` for strict PIT snapshot loaders
- Completed the next Phase 3 policy step by fixing the conservative scope of the first strict statement loader:
  - values-table-first
  - snapshot-first
  - `available_at <= as_of_date`
  - accession-bearing / identity-complete rows only
- Explicitly scoped `nyse_financial_statement_labels` out of the strict source path and positioned it as a summary/support layer.
- Completed the complementary Phase 3 policy step for broad statement loaders:
  - broadness means research-oriented time semantics, not broken-row tolerance
  - `period_end`-centered history reads are allowed
  - legacy mixed-state support is not being reintroduced after the stricter ledger cleanup
- Fixed the initial Phase 3 loader implementation set around the shortest DB-backed runtime path:
  - `load_universe(...)`
  - `load_price_history(...)`
  - `load_price_matrix(...)`
- Explicitly moved fundamentals / factors / statements behind the first price-based runtime milestone.
- Finalized the loader package location as `finance/loaders/*` and created the package scaffold.
- Kept the separation explicit:
  - `finance/data/*` for write path
  - `finance/loaders/*` for read path
- Finalized the shared loader helper scope and created `finance/loaders/_common.py`.
- Put the following shared concerns into the common loader layer:
  - symbol list parsing
  - symbol/universe resolution
  - date normalization
  - freq/timeframe normalization
  - snapshot input validation
- Closed `A. Loader Scope Finalization` on the Phase 3 board.
- Closed `C. Implementation Entry Set` on the Phase 3 board by fixing:
  - the first implementation order
  - the first DB-backed strategy candidate
  - the minimal validation path
- Fixed the first DB-backed strategy candidate as `EqualWeightStrategy`.
- Fixed the first validation path as:
  - `load_universe(...)`
  - `load_price_history(...)`
  - runtime adapter
  - `EqualWeightStrategy`
- Opened a dedicated Phase 3 loader implementation chapter board.
- Implemented the first concrete loader modules:
  - `finance/loaders/universe.py`
  - `finance/loaders/price.py`
- Exported the first public loader functions from `finance/loaders/__init__.py`:
  - `load_universe(...)`
  - `load_price_history(...)`
  - `load_price_matrix(...)`
- Verified loader smoke checks with the project virtualenv:
  - `load_universe(symbols=['spy','tlt','spy']) -> ['SPY', 'TLT']`
  - `load_price_history` / `load_price_matrix` import successfully from `finance.loaders`
- Added the first runtime adapter module:
  - `finance/loaders/runtime_adapter.py`
- Exported runtime adapter helpers:
  - `adapt_price_history_to_strategy_dfs(...)`
  - `load_price_strategy_dfs(...)`
- Updated the minimal validation path to use currently populated DB symbols:
  - `AAPL`, `MSFT`, `GOOG`
- Verified the first DB-backed runtime path end-to-end in the project virtualenv:
  - `load_price_strategy_dfs(symbols=['AAPL','MSFT','GOOG'], start='2024-01-01', end='2024-12-31')`
  - `EqualWeightStrategy(start_balance=10000, rebalance_interval=21)`
  - 252 rows per symbol
  - 252 result rows
  - final `Total Balance = 12998.14`
- Added `BacktestEngine.load_ohlcv_from_db(...)` so the existing engine chain can load DB-backed OHLCV.
- Added DB-backed strategy sample entrypoints in `finance/sample.py`:
  - `get_equal_weight_from_db(...)`
  - `get_gtaa3_from_db(...)`
  - `get_risk_parity_trend_from_db(...)`
  - `get_dual_momentum_from_db(...)`
  - `portfolio_sample_from_db(...)`
- Verified `get_equal_weight_from_db(...)` in the project virtualenv with:
  - `tickers=['AAPL','MSFT','GOOG']`
  - `start='2024-01-01'`
  - `end='2024-12-31'`
  - `interval=21`
- Result:
  - 12 monthly rows after `month_end` filtering
  - final `Total Balance = 12602.0`
- Observed an existing `SettingWithCopyWarning` in `finance/transform.py:121`, but the DB-backed sample path completed successfully.
- Completed OHLCV ingestion hardening for stock + ETF support.
- Kept `finance_price.nyse_price_history` as the single shared price fact table for both stock and ETF assets.
- Improved OHLCV ingestion by:
  - adding real `end` support to yfinance fetches
  - parallelizing batch fetches
  - adding retry/backoff and better missing-symbol stats
- Updated Daily Market Update defaults and manual symbol handling so ETF-heavy refresh paths are easier to execute correctly.
- Verified ETF ingestion with:
  - `VIG`, `SCHD`, `DGRO`, `GLD`
  - 251 daily rows per ETF after a 1-year refresh
- Re-verified DB-backed strategy execution with the ETF set:
  - `get_equal_weight_from_db(tickers=['VIG','SCHD','DGRO','GLD'], start='2025-01-01', end='2026-03-22', interval=1)`
  - final `Total Balance = 11815.2`
- Decided to defer deeper yfinance / large-universe optimization beyond the current hardening pass and keep it as a later optimization track.
- Implemented broad fundamentals / factors loaders in `finance/loaders/*`:
  - `load_fundamentals(...)`
  - `load_fundamental_snapshot(...)`
  - `load_factors(...)`
  - `load_factor_snapshot(...)`
  - `load_factor_matrix(...)`
- Verified loader smoke checks in the project virtualenv with `AAPL`, `MSFT`, `GOOG`:
  - fundamentals annual history: 15 rows
  - fundamentals annual snapshot: 3 rows
  - factors annual history: 15 rows
  - factor snapshot: 3 rows
  - factor matrix shape: `(15, 3)`
- Implemented detailed financial statement loaders in `finance/loaders/financial_statements.py`:
  - `load_statement_values(...)`
  - `load_statement_labels(...)`
  - `load_statement_snapshot_strict(...)`
- Verified statement loader smoke checks in the project virtualenv with `AAPL`, `MSFT`:
  - values annual history: 203 rows
  - labels summary rows: 203 rows
  - strict annual snapshot rows: 138
- Phase 3 current chapter and loader implementation chapter are now effectively complete from the loader/runtime groundwork perspective.
- Added a dedicated Phase 3 chapter completion summary document for the finished loader/runtime groundwork.
- Opened the next Phase 3 execution board:
  - `.note/finance/phase3/PHASE3_RUNTIME_GENERALIZATION_TODO.md`
- Reframed the active Phase 3 focus from “first loader implementation” to “runtime generalization and Phase 4 handoff preparation”.
- Extended the Streamlit OHLCV period presets to include `20y` for long-horizon Daily Market Update and manual OHLCV runs.
- Verified with the project virtualenv that yfinance accepts `period='20y'` for daily OHLCV fetches.
- Analyzed the discrepancy between `portfolio_sample(...)` and `portfolio_sample_from_db(...)`.
- Refined `BacktestEngine.load_ohlcv_from_db(...)` with `history_start` so DB-backed runtime can load extra history for indicator warmup.
- Updated DB-backed sample functions to read buffered history first and then slice back to the requested `start/end`.
- Revalidated that DB-backed `GTAA`, `Risk Parity`, and `Dual Momentum` now start on the same first month-end date as the direct path.
- Confirmed that the remaining performance gap is now primarily explained by legacy mixed-state OHLCV in `finance_price.nyse_price_history`.
- Hardened `finance/data/data.py` further so canonical OHLCV refresh can:
  - skip blank price rows
  - treat explicit `end` as inclusive for yfinance fetches
  - replace an already-requested date range before reinserting fresh rows
- Rebuilt the sample strategy OHLCV universe in `finance_price.nyse_price_history` for `2010-01-01 ~ 2026-03-20`.
- Revalidated that direct sample paths and DB-backed sample paths now match for:
  - Equal Weight
  - GTAA
  - Risk Parity
  - Dual Momentum
- Added a dedicated postmortem document comparing the original mismatch state with the final parity state for `portfolio_sample(...)` vs `portfolio_sample_from_db(...)`.
- Added a dedicated Phase 3 runtime path role-split document to clarify:
  - legacy direct-fetch sample path
  - DB-backed runtime sample path
- Updated `finance/sample.py` docstrings so the two path families are easier to distinguish in code.
- Refactored `finance/sample.py` so price-only strategy samples now share `_build_price_only_engine(...)` for:
  - Equal Weight
  - GTAA
  - Risk Parity
  - Dual Momentum
- Added a dedicated Phase 3 note documenting the common price-only runtime start pattern.
- Advanced the active Phase 3 runtime-generalization board from `B-1` to `B-2`.
- Cleaned up the recurring `SettingWithCopyWarning` in `finance/transform.py` by:
  - materializing the grouped slice with `.copy()`
  - aligning grouped dividend sums by index before assignment
- Re-ran the DB-backed Equal Weight smoke path and confirmed the warning no longer appears.
- Documented the Phase 3 connection policy for future factor / fundamental strategies:
  - loader
  - snapshot connection helper
  - strategy
- Advanced the active runtime-generalization board from `B-2` to `B-3`.
- Added a dedicated Phase 3 runtime strategy input contract document:
  - price-only strategies use `{ticker: price_df}` directly
  - future factor / fundamental strategies are expected to use
    `price_dfs + snapshot_by_date + rebalance_dates`
- Advanced the active runtime-generalization board from `B-3` to `C-1`.
- Opened a dedicated Phase 3 hardening board for `nyse_fundamentals` / `nyse_factors`.
- Reframed the two tables as:
  - `nyse_fundamentals`: broad coverage summary layer
  - `nyse_factors`: broad research derived layer
- Hardened `finance/data/fundamentals.py` by:
  - filtering blank summary rows
  - adding additional base fields for factor use
  - storing derivation/source metadata for key normalized fields
  - refreshing symbol/freq history canonically during reingestion
- Hardened `finance/data/factors.py` by:
  - storing price attachment metadata
  - expanding valuation / margin / leverage / growth factor coverage
  - calculating interest coverage when interest expense exists
  - refreshing symbol/freq history canonically during recalculation
- Extended `schema.py` and loader column lists to match the revised fundamentals/factors meaning.
- Validated the revised pipeline with `AAPL`, `MSFT` annual/quarterly sample runs.
- Confirmed that legacy blank annual rows are removed under the new canonical refresh path.
- Deferred the full-universe fundamentals/factors backfill as a later operational task.
- Returned to the main Phase 3 runtime-generalization board.
- Added a dedicated Phase 3 repeatable DB-backed smoke-scenario document covering:
  - minimal DB-backed price strategy
  - ETF ingestion + DB runtime
  - direct vs DB portfolio parity
  - broad loader smoke
  - fundamentals/factors hardening sample
- Advanced the main Phase 3 runtime-generalization board from `C-1` to `C-2`.
- Added a dedicated Phase 3 loader/runtime validation examples document with ready-to-run snippets for:
  - price loader + adapter
  - engine DB price path
  - DB-backed sample strategy
  - parity check
  - fundamentals/factors loaders
  - statement loaders
  - fundamentals/factors rebuild sample
- Advanced the main Phase 3 runtime-generalization board from `C-2` to `C-3`.
- Added a dedicated Phase 3 runtime cleanup backlog document and marked `C-3` complete.
- Split the Phase 3 runtime backlog into:
  - resolved during Phase 3
  - deferred operational work
  - deferred optimization work
  - deferred architecture work
- Advanced the main Phase 3 runtime-generalization board from `C-3` to `D-1`.
- Added a dedicated Phase 3 UI runtime function candidates document.
- Chose the Phase 4 first-pass runtime direction as:
  - strategy-specific DB-backed runtime wrappers
  - plus a shared backtest result bundle builder
- Advanced the main Phase 3 runtime-generalization board from `D-1` to `D-2`.
- Added a dedicated Phase 3 user-facing input-set draft document for the future strategy UI.
- Fixed the Phase 4 first-pass user input direction as:
  - strategy selection
  - universe mode plus tickers or preset
  - start/end date
- Chose to keep `timeframe`, warmup, DB/direct mode, and most strategy-specific parameters hidden or advanced by default.
- Advanced the main Phase 3 runtime-generalization board from `D-2` to `D-3`.
- Added a dedicated Phase 3 UI result-bundle draft document.
- Fixed the Phase 4 first-pass output direction as:
  - `result_df`
  - `summary_df`
  - `chart_df`
  - `meta`
- Chose to reuse `portfolio_performance_summary(...)` for summary generation and to keep chart data as a thin view over `result_df`.
- Marked `D-3` complete and moved the runtime-generalization chapter to completion review state.
- Updated the following Codex finance skills to reflect the project's Phase 3 operating patterns:
  - `finance-strategy-implementation`
  - `finance-doc-sync`
  - `finance-factor-pipeline`
  - `finance-db-pipeline`
- Added guidance for:
  - direct-fetch vs DB-backed runtime role separation
  - DB-backed warmup/parity checks
  - phase-board and finance doc index synchronization
  - curated `nyse_fundamentals` / broad `nyse_factors` table roles
  - canonical refresh and shared stock+ETF price-table rules
- Opened Phase 4 and added:
  - `.note/finance/phase4/PHASE4_UI_AND_BACKTEST_PLAN.md`
  - `.note/finance/phase4/PHASE4_CURRENT_CHAPTER_TODO.md`
- Updated the roadmap to mark Phase 4 as active.
- Fixed the Phase 4 collaboration rule explicitly:
  - non-obvious UI/runtime/product choices must be explained as options
  - implementation proceeds only after the user selects a direction
- Started the first Phase 4 task as `A-1 UI 구조 선택지 정리`.
- Revised the Phase 4 UI structure decision after clarifying the desired product shape.
- Finalized the Phase 4 first UI structure as:
  - one main app
  - ingestion tab + backtest tab
  - internal code split by tab/concern
- Dropped the separate `app/web/backtest_app.py` direction to avoid a stale unused entrypoint.
- Kept the Phase 4 first chapter moving at `B-1` with the updated structure assumption.
- Implemented the first unified-app tab shell in `app/web/streamlit_app.py`.
- Added `app/web/pages/backtest.py` as the first tab-specific page module.
- Kept the ingestion console path working inside the `Ingestion` tab and opened the `Backtest` tab as a Phase 4 placeholder.
- Added `app/web/runtime/backtest.py` as the first Phase 4 public runtime boundary module.
- Implemented `run_equal_weight_backtest_from_db(...)` and `build_backtest_result_bundle(...)` for the first DB-backed backtest UI path.
- Verified with `.venv` that the first wrapper returns the agreed bundle shape:
  - `strategy_name`
  - `result_df`
  - `summary_df`
  - `chart_df`
  - `meta`
- Implemented the first `Equal Weight` execution form in `app/web/pages/backtest.py`.
- Added:
  - preset/manual universe input
  - start/end date inputs
  - advanced input expander
  - runtime payload preview on submit
- Connected the first Backtest form to `run_equal_weight_backtest_from_db(...)`.
- Added first-pass result visibility in the Backtest tab:
  - execution success/error state
  - summary table
  - Total Balance line chart
  - execution meta
  - result preview table
- Polished the first result layout into a more product-like structure:
  - KPI metric row
  - `Summary / Equity Curve / Result Table / Meta` tabs
  - clearer separation between summary, raw result, and execution context
- Hardened first-pass backtest error handling.
- Added runtime/UI separation for:
  - input validation errors
  - DB data availability errors
  - generic execution errors
- Added explicit missing-data guidance for DB-backed failures.
- Added `GTAA` as the second public Phase 4 strategy.
- Implemented:
  - `run_gtaa_backtest_from_db(...)`
  - backtest strategy selector (`Equal Weight` / `GTAA`)
  - GTAA-specific execution form with `top` parameter
- Verified GTAA wrapper smoke output with DB-backed runtime parity (`End Balance = 22589.1`).
- Added `Risk Parity Trend` as the third public Phase 4 strategy.
- Implemented:
  - `run_risk_parity_trend_backtest_from_db(...)`
  - backtest strategy selector expansion to three strategies
  - Risk Parity Trend-specific execution form
- Verified Risk Parity Trend wrapper smoke output with DB-backed runtime parity (`End Balance = 15880.0`).
- Recorded `Dual Momentum` as the next ready-to-implement public strategy candidate after the first three price-only strategies.
- Added `Dual Momentum` as the fourth public Phase 4 strategy.
- Implemented:
  - `run_dual_momentum_backtest_from_db(...)`
  - backtest strategy selector expansion to four strategies
  - Dual Momentum-specific execution form with preset/manual universe flow
- Verified Dual Momentum wrapper smoke output with DB-backed runtime parity (`End Balance = 24600.7`).
- Reviewed the next Phase 4 UI request around:
  - stronger portfolio visualization
  - weighted multi-strategy portfolio construction
  - multi-strategy comparison graphs
- Confirmed the repo already has the core building blocks:
  - `make_monthly_weighted_portfolio(...)`
  - summary helpers
  - multi-curve visualization primitives
- Wrote a dedicated Phase 4 options document before implementation so the next UI choice can be made explicitly.
- Implemented the chosen Phase 4 path:
  - `Backtest` tab split into `Single Strategy` and `Compare & Portfolio Builder`
  - multi-strategy comparison for up to 4 strategies
  - summary/equity/drawdown comparison views
  - weighted portfolio builder based on comparison outputs
- Verified first-pass weighted example:
  - `Dual Momentum 50 + GTAA 50`
  - `Weighted Portfolio End Balance = 23594.9`
- Investigated a compare-chart visibility issue where `GTAA` looked missing in the equity overlay.
- Root cause:
  - `GTAA` emits sparser rebalance dates than monthly strategies
  - the original compare `st.line_chart` made that path hard to see
- Updated compare charts to use `line + point` rendering so sparse strategies remain visible.
- Exposed GTAA's previously hardcoded `2`-month interval as a user-facing advanced input.
- Wired the parameter through:
  - `finance/sample.py`
  - `app/web/runtime/backtest.py`
  - `app/web/pages/backtest.py`
- Verified:
  - `interval=2` -> `End Balance = 22589.1`
  - `interval=1` -> `End Balance = 23383.5`
- Extended compare mode so each selected strategy can override its own advanced inputs.
- Added compare-mode strategy-specific controls for:
  - `Equal Weight`: rebalance interval
  - `GTAA`: top assets, signal interval
  - `Risk Parity Trend`: rebalance interval, vol window
  - `Dual Momentum`: top assets, rebalance interval
- Verified compare/runtime propagation:
  - `GTAA(top=4, interval=1)` -> `End Balance = 22430.9`
  - `Risk Parity Trend(rebalance_interval=2, vol_window=9)` -> `End Balance = 14829.2`
  - `Dual Momentum(top=2, rebalance_interval=2)` -> `End Balance = 24832.5`
- Added first-pass persistent backtest history support.
- Introduced:
  - `app/web/runtime/history.py`
  - `.note/finance/BACKTEST_RUN_HISTORY.jsonl`
- Backtest history now records:
  - `single_strategy`
  - `strategy_compare`
  - `weighted_portfolio`
- Added `Persistent Backtest History` view to the Backtest tab.
- Verified append/load behavior for all three run kinds, then cleared the temporary validation file.
- Added first-pass visualization enhancements to the Backtest tab.
- Implemented:
  - single-strategy equity chart with `High / Low / End` markers
  - `Period Extremes` tab with top 3 best / worst periods
  - compare-mode `Total Return` overlay
- Verified helper outputs for:
  - single-strategy best/worst periods
  - compare-mode total return overlay dataset
- Extended the same visualization language to deeper chart annotations.
- Single-strategy equity charts now also show:
  - `Best Period`
  - `Worst Period`
  markers directly on the chart
- Weighted portfolio results now reuse:
  - the same marker-based equity chart
  - the same `Period Extremes` view
- Synced Phase 4 docs and the finance analysis document to reflect the new weighted-portfolio visualization state.
- Added a second-pass compare/readability enhancement.
- Compare mode now includes:
  - `Focused Strategy` drilldown
  - one selected strategy's KPI summary
  - marker equity curve
  - `Top 3 Balance Highs / Lows`
  - `Top 3 Best / Worst Periods`
- Single-strategy and weighted-portfolio results also gained `Balance Extremes` tables.
- Enhanced persistent backtest history beyond a flat table.
- Added:
  - run kind filter
  - search across strategy/ticker/preset/selected strategies
  - selected record drilldown with `Summary / Input & Context / Raw Record`
- Registered the new Phase 4 history-enhancement document and synced analysis docs.
- Added a weighted-portfolio contribution visualization first pass.
- Weighted portfolio results now include:
  - `Contribution` tab
  - configured weight vs ending share snapshot
  - stacked contribution amount chart
  - stacked contribution share chart
- Verified:
  - synthetic helper decomposition
  - real `Dual Momentum 50 + GTAA 50` contribution shape `(62, 2)`
  - ending share roughly `52.1% / 47.9%`
- Added backtest history second-pass improvements.
- Persistent history now supports:
  - recorded date range filter
  - metric-based sorting
  - `Run Again` for supported single-strategy records
- Kept compare / weighted rerun intentionally closed until enough context is stored to replay them safely.
- Added visualization second-pass improvements for compare mode.
- Compare results now include:
  - end markers on overlay charts
  - a `Strategy Highlights` table with high / low / end / best / worst period stats
- Verified compare highlight extraction for `Equal Weight` and `GTAA`.
- Closed the third pass of backtest-history enhancement.
- Added:
  - metric threshold filters
  - `Load Into Form` for supported single-strategy records
  - single-strategy form prefill from stored history payloads
- Kept compare / weighted rerun intentionally deferred because the current stored context is not rich enough to replay their advanced overrides safely.
- Synced Phase 4 docs and the finance analysis document to reflect the stronger history workflow.
- Narrow follow-up fix:
  - when a metric threshold is enabled, history rows with `None` for that metric are now excluded instead of silently passing through the filter
- Closed the first Phase 4 UI execution chapter in documentation.
- Opened the next Phase 4 chapter for factor / fundamental strategy entry.
- Added:
  - a chapter-completion summary for the current price-only UI state
  - a new factor / fundamental entry TODO board
  - a first-strategy options memo covering `Value` vs `Quality` vs simple multi-factor
- Fixed the first factor / fundamental strategy direction to `Quality Snapshot Strategy`.
- Added:
  - a strategy-scope document for the quality snapshot path
  - a first public runtime wrapper draft for the quality path
  - updated the Phase 4 board so the next active decision is `snapshot_mode`
- Chose `broad_research` as the first public snapshot mode for the quality path.
- Implemented:
  - `quality_snapshot_equal_weight(...)` in `finance/strategy.py`
  - `get_quality_snapshot_from_db(...)` in `finance/sample.py`
  - `run_quality_snapshot_backtest_from_db(...)` in `app/web/runtime/backtest.py`
- Verified the first-pass quality strategy on `AAPL/MSFT/GOOG` with annual snapshots and monthly rebalance.
- Defined the Quality Snapshot UI input boundary:
  - basic inputs
  - advanced inputs
  - hidden defaults
- Exposed `Quality Snapshot` as the fifth public strategy in the Backtest UI.
- Extended history/meta/prefill handling so the quality strategy participates in:
  - persistent backtest history
  - form reload
  - rerun flow
  - compare first-pass
- Added first-pass data requirements guidance directly to the Quality Snapshot form so the UI now explains:
  - price data is expected from `Daily Market Update` / OHLCV collection
  - factor data is expected from `Weekly Fundamental Refresh`
  - `Extended Statement Refresh` is not required for the current public broad-research quality path
- Investigated why `Quality Snapshot` stays flat before 2022 for `AAPL/MSFT/GOOG` and confirmed the current annual factor coverage only begins around 2021/2022 in `nyse_factors`, so early months remain in cash until the first usable snapshot appears.
- Added a runtime warning to the Quality Snapshot result view when the first usable factor snapshot starts materially later than the requested backtest start date.
- Added stage-based progress support for `Weekly Fundamental Refresh` so large NYSE-stock runs now show fundamentals/factors stage progress instead of only a blocking spinner.
- Ran `Weekly Fundamental Refresh` directly on `AAPL/MSFT/GOOG` for both `annual` and `quarterly` to inspect practical historical depth from the current yfinance-backed pipeline.
- Verified that the current broad-research summary/factor path still has shallow history:
  - annual factors begin around `2021/2022`
  - quarterly factors begin around `2024`
  for the tested symbols, which explains why the public Quality Snapshot path cannot meaningfully backtest into 2016 yet.
- Checked the current detailed statement ledger as the next candidate source for longer-history quality factors and found that it is also not yet deep enough for the target universe:
  - `AAPL` annual statement values currently begin around `2024`
  - `MSFT` annual statement values currently begin around `2025`
  - `GOOG` statement coverage is not yet available in the current local ledger
- Recorded this as a formal blocker for the statement-driven quality path and shifted the next decision from “implement the new strategy now” to “secure statement history depth first.”
- Ran the agreed `2 -> 1` sequence for the statement-driven quality path:
  - first, a small feasibility test with `Extended Statement Refresh` on `AAPL/MSFT/GOOG`
  - then, the same run served as a targeted statement backfill for the sample quality universe
- Results:
  - annual 12 periods: `rows_written = 1407`
  - quarterly 12 periods: `rows_written = 1545`
- Post-backfill coverage improved materially:
  - `AAPL` annual now starts around `2021-09-25`
  - `GOOG` annual now starts around `2021-12-31`
  - `MSFT` annual now starts around `2023-12-31`
- This confirms the statement path is viable, but still not deep enough to support a meaningful `2016`-start statement-driven quality backtest yet.
- Implemented the next agreed step after feasibility/backfill:
  - a sample-universe `statement-driven quality prototype`
  - using strict annual statement snapshots instead of the public broad-research factor snapshot path
- Added:
  - `build_fundamentals_from_statement_snapshot(...)` in `finance/data/fundamentals.py`
  - `calculate_quality_factors_from_fundamentals(...)` in `finance/data/factors.py`
  - `build_quality_factor_snapshot_from_statement_snapshot(...)` in `finance/data/factors.py`
  - `get_statement_quality_snapshot_from_db(...)` in `finance/sample.py`
  - `run_statement_quality_prototype_backtest_from_db(...)` in `app/web/runtime/backtest.py`
- Verified the prototype on `AAPL/MSFT/GOOG`, `2023-01-01 ~ 2026-03-20`:
  - first active date: `2023-01-31`
  - final `End Balance = 23645.4`
  - `CAGR = 0.316218`
  - `Sharpe Ratio = 1.587924`
- Kept this path out of the public UI for now and documented it as a prototype rather than a production/public factor strategy.
- Follow-up hardening in the same workstream:
  - moved the statement-driven quality preprocessing out of `transform.py`
    and into reusable data-layer mapping helpers
  - the current path is now explicitly:
    `strict statement snapshot -> normalized fundamentals -> quality factor snapshot -> strategy`
- Added a strict statement quality loader boundary on top of that mapping:
  - `load_statement_quality_snapshot_strict(...)` in `finance/loaders/factors.py`
- Refactored the statement-driven sample path to consume the loader instead of directly wiring builders in sample code.
- Started the actual `statement-driven fundamentals/factors backfill` preparation step:
  - documented why the current `nyse_fundamentals` / `nyse_factors` keys cannot safely hold both broad and statement-driven rows at the same time
  - documented rollout options:
    - overwrite current tables
    - shadow tables
    - same-table multi-mode key expansion
- Added `load_statement_coverage_summary(...)` in `finance/loaders/financial_statements.py`
  so strict statement usable history can be audited before any backfill write is attempted.
- Continued the same workstream into the first actual shadow-table rollout for statement-driven backfill.
- Added schema-backed shadow write paths:
  - `upsert_statement_fundamentals_shadow(...)` in `finance/data/fundamentals.py`
  - `upsert_statement_factors_shadow(...)` in `finance/data/factors.py`
- Added matching loader read paths:
  - `load_statement_fundamentals_shadow(...)`
  - `load_statement_factors_shadow(...)`
- Kept current public broad tables intact and wrote statement-driven rows into:
  - `finance_fundamental.nyse_fundamentals_statement`
  - `finance_fundamental.nyse_factors_statement`
- Verified sample-universe annual backfill on `AAPL/MSFT/GOOG`:
  - fundamentals shadow rows written: `12`
  - factors shadow rows written: `12`
- Verified loader readback:
  - fundamentals shadow shape: `(12, 39)`
  - factors shadow shape: `(12, 53)`
- Confirmed current first-pass limitation:
  - accounting quality fields populate meaningfully
  - `shares_outstanding` is still mostly unavailable from the statement-driven path
  - therefore valuation fields such as `market_cap` remain `NULL` in the current shadow factor history
- Followed up immediately with a shares enhancement pass for the same shadow path.
- Added broad-summary fallback for `shares_outstanding` in `finance/data/fundamentals.py`:
  - nearest `period_end`
  - same `symbol/freq`
  - `15-day` tolerance
- Re-ran sample-universe annual shadow backfill on `AAPL/MSFT/GOOG`.
- Result after the shares fallback:
  - `shares_outstanding` populated on `10 / 12` shadow fundamentals rows
  - `market_cap` populated on `10 / 12` shadow factor rows
  - valuation fields such as `per` / `pbr` now populate for most sample-universe rows
- Important meaning note:
  - the shadow path is now `statement-driven` for accounting fields
  - but valuation fields may be `statement + broad shares fallback` hybrid rows
- Verified the user-triggered `Extended Statement Refresh` after both:
  - `annual, periods=12`
  - `quarterly, periods=12`
- Coverage check results:
  - annual strict history remains earlier and more usable than quarterly for `AAPL/MSFT/GOOG`
  - quarterly strict history is now present but mostly starts in `2024`
- Rebuilt both annual and quarterly shadow tables immediately after verification:
  - annual shadow: `12` fundamentals rows, `12` factor rows
  - quarterly shadow: `18` fundamentals rows, `18` factor rows
- Revalidated the statement-driven quality prototype:
  - annual path:
    - `first_active = 2023-01-31`
    - `End Balance = 23645.4`
  - quarterly path:
    - `first_active = 2024-10-31`
    - `End Balance = 13952.3`
- Current conclusion after refresh:
  - annual strict statement path is still the more usable sample-universe candidate
  - quarterly path is technically working, but not yet the better public candidate
- Investigated why annual strict statement coverage still looked too short after the refresh.
- Confirmed the blocker was not source scarcity:
  - `AAPL`, `MSFT`, `GOOG` source facts already had deeper annual reported periods
  - the collector was trimming `periods=N` by raw row-level `period_end`, which let quarter-end-like facts inside recent 10-K rows crowd out older true annual periods
- Fixed `finance.data.financial_statements._iter_value_rows_from_source(...)` to limit latest N periods by reported period:
  - `report_date` first
  - `period_end` fallback
- Added canonical refresh semantics to `upsert_financial_statements(...)` for the successful symbol/freq scope:
  - delete `nyse_financial_statement_values` by `symbol + freq`
  - delete `nyse_financial_statement_labels` by `symbol + as_of_period_type`
  - then reinsert latest canonical rows
- Re-ran sample-universe annual refresh on `AAPL/MSFT/GOOG` with `periods=12`.
- Post-fix annual strict coverage now reaches:
  - `AAPL`: `2011-09-24 ~ 2025-09-27`
  - `GOOG`: `2012-12-31 ~ 2025-12-31`
  - `MSFT`: `2011-06-30 ~ 2025-06-30`
- Rebuilt annual statement-driven shadow tables:
  - fundamentals rows written: `92`
  - factors rows written: `92`
- Revalidated annual statement-driven quality prototype on `2016-01-01 ~ 2026-03-20`:
  - `first_active = 2016-02-29`
  - `End Balance = 93934.6`
- Current meaning:
  - sample-universe annual strict statement path is no longer blocked by shallow history
  - next decision moves to public promotion vs wider-universe coverage expansion
- Promoted the strict annual statement-driven quality path into a public candidate strategy instead of keeping it backend-only.
- Added:
  - `run_quality_snapshot_strict_annual_backtest_from_db(...)` in `app/web/runtime/backtest.py`
  - shared strict statement quality bundle helper
- Exposed `Quality Snapshot (Strict Annual)` in the Backtest UI:
  - single-strategy selector
  - compare strategy options
  - history / prefill / rerun mapping
- Kept the current broad `Quality Snapshot` path intact and exposed the strict path as a separate strategy so the two semantics remain easy to compare.
- Verified wrapper output on `AAPL/MSFT/GOOG`, `2016-01-01 ~ 2026-03-20`:
  - `End Balance = 93934.6`
- Current meaning:
  - Phase 4 now has both
    - broad quality public path
    - strict annual statement quality public candidate
  - next decision moves to coexistence rules vs wider-universe coverage expansion
- The user preferred annual statement coverage work before further strict-quality polishing because the current strict annual strategy still did not yet feel fully trustworthy as a finished strategy.
- Verified the operational scale of annual coverage expansion:
  - `Profile Filtered Stocks` currently resolves to about `5783` symbols
  - so wider annual runs need better operator support before execution
- Added live progress support for statement-ingestion jobs:
  - `finance.data.financial_statements.upsert_financial_statements(...)` now emits batch progress events
  - `run_collect_financial_statements(...)` and `run_extended_statement_refresh(...)` now pass progress callbacks through
  - Streamlit now renders live progress for:
    - `Extended Statement Refresh`
    - `Financial Statement Ingestion`
- Added richer statement job result details:
  - `upserted_filings`
  - cumulative values / labels / filings progress in the live caption
- Verified the new operator path with a sample run:
  - `AAPL/MSFT/GOOG`, `annual`, `periods=1`
  - `status = success`
  - `rows_written = 575`
  - `upserted_labels = 573`
  - `upserted_filings = 309`
- Current meaning:
  - wider-universe annual coverage has not been executed yet
  - but the operational path is now better prepared for a long `Extended Statement Refresh`
- Executed the first staged annual statement coverage run instead of jumping directly to all `Profile Filtered Stocks`.
- Stage 1 universe:
  - `Profile Filtered Stocks` ordered by `market_cap DESC`
  - top `100` symbols
- Annual statement refresh result:
  - `status = success`
  - `rows_written = 188709`
  - `upserted_labels = 85164`
  - `upserted_filings = 8575`
  - `failed_symbols = 0`
- Annual shadow rebuild result:
  - fundamentals rows: `2376`
  - factors rows: `2376`
- Coverage audit result:
  - covered symbols: `80 / 100`
  - `12+` annual accessions: `68`
  - `8+` annual accessions: `74`
  - missing coverage symbols are dominated by foreign issuers such as:
    - `TSM`, `AZN`, `ASML`, `BABA`, `TM`, `HSBC`, `NVS`, `RY`
- Current meaning:
  - annual strict coverage clearly scales beyond the sample universe
  - but the next staged rollout should refine the universe toward EDGAR-friendly stocks rather than blindly expanding by market cap alone
- Executed stage 2 annual coverage on a refined US/EDGAR-friendly universe.
- Stage 2 universe:
  - `Profile Filtered Stocks`
  - `country = United States`
  - `market_cap DESC`
  - top `300`
- Annual statement refresh result:
  - `status = success`
  - `rows_written = 701189`
  - `upserted_labels = 316761`
  - `upserted_filings = 30170`
  - `failed_symbols = 0`
- Annual shadow rebuild result:
  - fundamentals rows: `9385`
  - factors rows: `9385`
- Coverage audit result:
  - covered symbols: `297 / 300`
  - `12+` annual accessions: `251`
  - `8+` annual accessions: `266`
  - `5+` annual accessions: `286`
  - missing symbols only:
    - `MRSH`, `AU`, `CUK`
- Current meaning:
  - refined US/EDGAR-friendly annual coverage scales well
  - strict annual path now has strong wider-universe support beyond the sample universe

### 2026-03-25 - Strict annual quality public role/default-universe refinement

- Split broad quality presets and strict annual presets in the Backtest UI.
- Added strict annual preset sets:
  - `US Statement Coverage 300`
  - `US Statement Coverage 100`
  - `Big Tech Strict Trial`
- Kept broad `Quality Snapshot` on `Big Tech Quality Trial`.
- Switched strict annual single-strategy default toward the verified wider stock universe.
- Kept strict annual compare default lighter at `US Statement Coverage 100` so multi-strategy runs stay responsive.
- Synced prefill/history handling to use strict preset validation instead of the broad preset set.

### 2026-03-25 - Quality preset preview refresh UX fix

- Fixed the quality single-strategy preset preview UX in `app/web/pages/backtest.py`.
- Moved `Quality Snapshot` / `Quality Snapshot (Strict Annual)` universe selection widgets outside the submit form so Streamlit reruns immediately on preset change.
- Added compact ticker preview rendering with ticker count and truncated preview text.
- Result:
  - changing the preset now refreshes the ticker preview immediately instead of waiting for form submit.

### 2026-03-25 - Strict annual fast path, interpretation, and value strict rollout

- Optimized `Quality Snapshot (Strict Annual)` to use statement shadow factor history instead of rebuilding strict statement snapshots on every rebalance date.
- Added `load_statement_factor_snapshot_shadow(...)` and DB-backed shadow snapshot sample/runtime wiring.
- Found and fixed a semantic bug in annual shadow rebuild:
  - annual shadow history had quarter-like comparative rows mixed in
  - and stored too-late availability for each period end
- Corrected annual shadow fundamentals/factors toward:
  - report-date-anchored annual periods
  - `first_available_for_period_end`
- Verified sample-universe parity:
  - optimized strict annual path and prototype rebuild path now both return
    `End Balance = 93934.6`
- Added `Selection History` to snapshot strategies in the Backtest result UI.
- Added `Value Snapshot (Strict Annual)` to:
  - single strategy
  - compare
  - history / prefill
- Added operator-facing symbol presets:
  - `US Statement Coverage 100`
  - `US Statement Coverage 300`
  to the ingestion app as well.
- Rebuilt annual shadow for `US Statement Coverage 300` after the timing fix:
  - fundamentals rows: `3286`
  - factors rows: `3286`
- Runtime checks:
  - strict annual top-100 quality:
    - `3.381s`
    - `End Balance = 20198.7`
  - strict annual top-100 value:
    - `3.399s`
    - `End Balance = 19578.5`

### 2026-03-25 - Strict annual productionization doc sync and final validation

- Synced Phase 4 plan and comprehensive analysis to the latest strict annual state.
- Recorded that the public strict annual path now uses:
  - `nyse_factors_statement` fast runtime
  - `Selection History` interpretation view
  - `Value Snapshot (Strict Annual)` companion strategy
  - annual coverage operator presets (`US Statement Coverage 100/300`)
- Re-ran compile validation for the strict annual UI/runtime path.
- Confirmed the Streamlit app is live on `http://localhost:8501`.

### 2026-03-25 - Backtest UI elapsed-time display for strict annual validation

- Added explicit elapsed-time recording to Backtest single-strategy execution.
- The last-run result view now shows `Elapsed` under execution context.
- The success banner now includes the measured seconds for the completed run.
- Backtest history records now persist `ui_elapsed_seconds` for later drilldown.

### 2026-03-25 - Strict annual large-universe calendar fix

- Replaced full-date intersection with union-calendar alignment for snapshot strategy price inputs.
- Added `align_dfs_by_date_union(...)` in `finance/transform.py`.
- Added snapshot-specific price builder in `finance/sample.py`.
- Hardened `quality_snapshot_equal_weight(...)` so rebalance selection excludes symbols whose current `Close` is unavailable.
- Validation:
  - `US Statement Coverage 300` strict quality:
    - first active date moved from effectively `2025-12-31` to `2016-01-29`
    - active rows: `124`
    - runtime: `9.086s`
    - end balance: `73778.4`
  - `US Statement Coverage 100` strict quality:
    - first active date: `2016-01-29`
    - active rows: `124`
    - runtime: `3.320s`
    - end balance: `79295.2`
  - sample-universe strict parity stayed intact:
    - optimized strict path `0.322s`
    - prototype rebuild path `16.793s`
    - both `End Balance = 93934.6`

### 2026-03-25 - Broad/strict guide, strict family comparison, and Phase 4 closeout prep

- Added `Broad vs Strict Guide` to the quality/value snapshot forms in the Backtest UI.
- Re-ran strict annual family comparison on the current public path:
  - quality strict / coverage 100:
    - `3.321s`
    - `End Balance = 79295.2`
  - quality strict / coverage 300:
    - `9.264s`
    - `End Balance = 73778.4`
  - value strict / coverage 100:
    - `3.197s`
    - `End Balance = 20228.2`
  - value strict / coverage 300:
    - `9.080s`
    - `End Balance = 20931.1`
- Recorded the current interpretation:
  - `Quality Snapshot (Strict Annual)` is the primary strict annual public candidate
  - `Value Snapshot (Strict Annual)` remains the secondary strict annual family
- Added Phase 4 closeout documents and next-phase preparation notes without formally opening a new phase.

### 2026-03-25 - Quality factor expansion shortlist for wider-universe strict annual path

- Measured latest-snapshot factor coverage on `US Statement Coverage 300` annual shadow factors.
- Confirmed that the current default strict-quality set has uneven coverage:
  - `roe`: `90.91%`
  - `operating_margin`: `75.08%`
  - `debt_ratio`: `61.28%`
  - `gross_margin`: `42.42%`
- Identified stronger coverage candidates:
  - `roa`
  - `net_margin`
  - `asset_turnover`
  - `current_ratio`
- Wrote a factor-expansion recommendation doc with three options and a coverage-first recommendation.

### 2026-03-25 - Strict annual quality default factor set refreshed to coverage-first

- Applied the coverage-first strict annual quality default:
  - `roe`
  - `roa`
  - `net_margin`
  - `asset_turnover`
  - `current_ratio`
- Updated:
  - strict annual sample defaults
  - strict annual runtime defaults
  - Backtest single-strategy strict annual form defaults
  - compare-mode strict annual form defaults
  - history/prefill fallback defaults
- Re-validated current public default:
  - coverage 100:
    - `3.319s`
    - `End Balance = 107324.3`
  - coverage 300:
    - `9.359s`
    - `End Balance = 366404.7`

### 2026-03-25 - Strict annual final-month duplicate rows traced to uneven daily price freshness and resolved by targeted refresh

- Investigated why `Quality Snapshot (Strict Annual)` on `US Statement Coverage 300` showed both `2026-03-17` and `2026-03-20` in the final month.
- Confirmed the first suspected lagging names (`APH`, `CVNA`, `GWW`, `LLY`, `MPWR`) were stale through `2026-03-17`, then refreshed them with a targeted `Daily Market Update`.
- Re-checked the full `US Statement Coverage 300` universe and found `28` symbols still ending at `2026-03-17`.
- Ran a second targeted `Daily Market Update` for those `28` lagging symbols and confirmed all `300` symbols now reach at least `2026-03-20`.
- Re-ran `Quality Snapshot (Strict Annual)` on `US Statement Coverage 300`:
  - final duplicated March rows collapsed to a single `2026-03-20` row
  - row count moved from `124` to `123`
  - `End Balance = 192994.7`
  - `CAGR = 33.91%`
- This verified that the duplicate final-month rows were driven by uneven price freshness rather than a strict-annual ranking bug.

### 2026-03-25 - Strict annual price freshness preflight added to single-strategy UI and runtime metadata

- Added `load_price_freshness_summary(...)` to the loader layer for lightweight latest-date aggregation.
- Added `inspect_strict_annual_price_freshness(...)` to the backtest runtime.
- Strict annual quality/value wrappers now append price freshness warnings and store compact freshness metadata in result `meta`.
- Added `Price Freshness Preflight` sections to:
  - `Quality Snapshot (Strict Annual)`
  - `Value Snapshot (Strict Annual)`
- Verified current `US Statement Coverage 300` state:
  - `status = ok`
  - `common_latest_date = 2026-03-20`
  - `spread_days = 0`

### 2026-03-25 - Strict annual operator UX, wider managed presets, and staged audit refresh

- Added `load_top_symbols_from_asset_profile(..., order_by='market_cap_desc')` so strict annual managed universes can be built from asset-profile DB state instead of hardcoded arrays only.
- Expanded strict annual managed presets to:
  - `US Statement Coverage 100`
  - `US Statement Coverage 300`
  - `US Statement Coverage 500`
  - `US Statement Coverage 1000`
  - `Big Tech Strict Trial`
- Added preflight second-pass UX:
  - stale / missing symbol payload for `Daily Market Update`
  - preset-status note in strict annual forms
- Current DB wider-universe audit:
  - `Profile Filtered Stocks / United States = 4441`
  - coverage `500`:
    - covered `396 / 500`
    - price freshness spread `3d`
  - coverage `1000`:
    - covered `396 / 1000`
    - price freshness spread `49d`
- Decision:
  - strict annual public default remains
    - single: `US Statement Coverage 300`
    - compare: `US Statement Coverage 100`
  - `500/1000` stay as staged operator presets for now

### 2026-03-25 - Strict annual interpretability and multi-factor family extended

- Selection-history UI now includes `Selection Frequency`.
- Added new public candidate:
  - `Quality + Value Snapshot (Strict Annual)`
- Integrated it into:
  - single strategy
  - compare strategy
  - history / prefill
  - runtime wrapper family
- First-pass multi-factor validation:
  - coverage `100`:
    - `3.569s`
    - `End Balance = 24778.9`
    - `CAGR = 9.36%`
  - coverage `300`:
    - `9.785s`
    - `End Balance = 16931.4`
    - `CAGR = 5.33%`

### 2026-03-25 - Strict annual operator automation first pass

- Added `run_strict_annual_shadow_refresh(...)` helper job.
- Flow:
  - annual `Extended Statement Refresh`
  - statement fundamentals shadow rebuild
  - statement factors shadow rebuild
- Smoke check:
  - `AAPL/MSFT/GOOG`, `periods=1`
  - `status = success`
  - `rows_written = 581`

### 2026-03-25 - Phase 4 closeout docs synced after staged strict-annual expansion

- Synced Phase 4 closeout documents so the current public strategy set now explicitly includes:
  - `Quality + Value Snapshot (Strict Annual)`
- Synced strict-annual chapter docs with the completed staged-operator work:
  - wider managed presets `500/1000`
  - stale-symbol operator UX
  - repeatable shadow refresh helper
- Reconfirmed the current product stance in docs:
  - strict annual public default remains `US Statement Coverage 300` for single strategy
  - strict annual compare default remains `US Statement Coverage 100`
  - `500/1000` remain staged operator presets pending deeper coverage

### 2026-03-26 - Strict annual managed preset import crash fixed

- Investigated Streamlit startup failure at:
  - `app/web/streamlit_app.py:52`
  - `QUALITY_STRICT_PRESETS["US Statement Coverage 500"]`
- Root cause:
  - strict managed preset loading could omit `500/1000` when DB-backed asset-profile loading returned no rows or raised, but `streamlit_app.py` assumed those keys always existed during import.
- Fix:
  - `app/web/pages/backtest.py`
    - `_load_managed_strict_annual_presets()` now always emits fallback values for
      `US Statement Coverage 500` and `US Statement Coverage 1000`
      by degrading to the best available strict annual preset
  - `app/web/streamlit_app.py`
    - `SYMBOL_PRESETS` now uses a safe `_preset_csv(...)` helper instead of direct dictionary indexing
- Verification:
  - `PYTHONPYCACHEPREFIX=/tmp/pycache python3 -m py_compile app/web/pages/backtest.py app/web/streamlit_app.py`
  - `.venv` import of `app.web.streamlit_app` succeeded
  - currently exposed counts:
    - `US Statement Coverage 100`: `100`
    - `US Statement Coverage 300`: `300`
    - `US Statement Coverage 500`: fallback `300`
    - `US Statement Coverage 1000`: fallback `300`

### 2026-03-26 - Strict annual wide presets now resolve true DB-backed top-N sets, and canonical monthly rows are fixed

- Revalidated strict annual managed universes in a DB-connected runtime instead of the earlier sandbox-only import path.
- Current DB-backed managed preset counts are:
  - `US Statement Coverage 100`: `100`
  - `US Statement Coverage 300`: `300`
  - `US Statement Coverage 500`: `500`
  - `US Statement Coverage 1000`: `1000`
- Current annual shadow coverage was rechecked directly from DB:
  - `US Statement Coverage 500`: covered `496 / 500`
  - `US Statement Coverage 1000`: covered `987 / 1000`
- Added canonical period-date alignment for snapshot strategies:
  - `finance/transform.py`
    - `align_dfs_to_canonical_period_dates(...)`
  - `finance/sample.py`
    - snapshot price builders now apply union-calendar alignment first, then collapse each period to one canonical date
- This fixes the large-universe strict annual result-table issue where month-end runs could emit symbol-specific dates like `2026-02-03` or `2026-03-17`.
- Runtime verification for `Quality Snapshot (Strict Annual)` on `US Statement Coverage 1000`:
  - ticker count: `1000`
  - result rows: `15` for `2025-01-01 ~ 2026-03-20`
  - tail dates are now canonical monthly rows:
    - `2025-08-29`
    - `2025-09-30`
    - `2025-10-31`
    - `2025-11-28`
    - `2025-12-31`
    - `2026-01-30`
    - `2026-02-27`
    - `2026-03-20`
- `Price Freshness Preflight` still matters at the 1000-name scale:
  - current spread: `49d`
  - lagging symbols:
    - `CADE`, `CMA`, `DAY`, `CFLT`, `GSAT`, `UBSI`, `WMG`, `WTS`, `WWD`

### 2026-03-27 - Coverage 1000 closeout and value strict recovery completed

- Refreshed the remaining stale names inside `US Statement Coverage 1000` with a targeted `Daily Market Update` run:
  - `CADE`, `CMA`, `DAY`, `CFLT`, `GSAT`, `UBSI`, `WMG`, `WTS`, `WWD`
- Rechecked strict annual `Coverage 1000` freshness after refresh:
  - stale symbols reduced from `9` to `4`
  - remaining lagging names:
    - `CADE`, `CMA`, `DAY`, `CFLT`
  - common latest stayed at `2026-01-30`
  - newest latest stayed at `2026-03-20`
  - spread remains `49d`
- Kept the public-position decision unchanged:
  - `US Statement Coverage 1000` is usable and real DB-backed top-1000
  - but still remains a staged operator preset rather than the public default
- Investigated why `Value Snapshot (Strict Annual)` stayed flat through `2016~2021` and traced it to late `shares_outstanding` availability in statement shadow fundamentals.
- Expanded statement-driven shares fallback in `finance/data/fundamentals.py` to use historical weighted-average share-count concepts when direct outstanding concepts are absent.
- Rebuilt annual statement shadow fundamentals/factors for the top-1000 US universe after the shares-fallback change:
  - fundamentals rows: `10292`
  - factors rows: `10292`
- Expanded the strict annual value factor set and UI options:
  - new strict default factors:
    - `book_to_market`
    - `earnings_yield`
    - `sales_yield`
    - `ocf_yield`
    - `operating_income_yield`
  - additional UI-selectable strict value factors:
    - `fcf_yield`, `per`, `pbr`, `psr`, `pcr`, `pfcr`, `ev_ebit`, `por`
- Revalidated `Value Snapshot (Strict Annual)` after the shadow rebuild:
  - `US Statement Coverage 300`
    - `first_active = 2016-01-29`
    - `End Balance = 85378.4`
    - `CAGR = 23.56%`
    - `Sharpe Ratio = 1.1341`
  - `US Statement Coverage 1000`
    - `first_active = 2016-01-29`
    - `End Balance = 91733.7`
    - `CAGR = 24.43%`
    - `Sharpe Ratio = 1.0644`
- Closeout interpretation:
  - `Quality Snapshot (Strict Annual)` remains the primary strict annual public candidate
  - `Value Snapshot (Strict Annual)` now behaves as a real 2016-start strategy path instead of a 2021-onward partial path
  - `Coverage 1000` remains staged because freshness risk, not strategy logic, is still the limiting factor
- Added one more UI clarification to strict annual preflight:
  - `stale` now explicitly means that the symbol's latest daily price in DB stops before the selected end date

### 2026-03-27 - Phase 5 strategy-library and risk-overlay direction opened

- After Phase 4 closeout, the next major direction was user-confirmed and documented as a new Phase 5 workstream.
- Added Phase 5 planning documents:
  - `.note/finance/phase5/PHASE5_STRATEGY_LIBRARY_AND_RISK_OVERLAY_PLAN.md`
  - `.note/finance/phase5/PHASE5_CURRENT_CHAPTER_TODO.md`
- The next phase direction is now explicitly:
  - strategy library / comparative research
  - strict factor risk overlay design
  - first overlay candidate selection before implementation
- Synced the phase handoff documents so they now point from Phase 4 closeout into the opened Phase 5 kickoff/planning state.

### 2026-03-27 - Phase 5 carry-over requests registered

- Added two user-requested follow-up items into Phase 5 planning:
  - compare-screen advanced-input parity for strict factor strategies
  - quarterly strict family expansion candidate
- Current recommendation/order was documented as:
  - compare advanced-input parity first
  - quarterly expansion later
- Rationale:
  - compare parity is a smaller UI/runtime consistency fix
  - quarterly strict family is a larger coverage/timing/runtime expansion and should be treated as a separate candidate track

### 2026-03-27 - Phase 5 first chapter baseline, compare parity, and first overlay first pass

- Executed the first recommended Phase 5 sequence:
  - baseline strict-family comparative research
  - compare advanced-input parity
  - overlay requirement lock
  - first overlay selection
  - overlay runtime first pass
  - strict family compare / interpretation expansion
  - quarterly strict-family review
  - second overlay candidate review
- Compare strict factor strategies now expose strategy-specific advanced overrides for:
  - preset
  - factor set
  - `top_n`
  - `rebalance_interval`
  - trend filter on/off
  - trend filter window
- The first overlay was fixed as:
  - `month-end MA200 trend filter + cash fallback`
- Implemented the overlay across strict annual quality / value / quality+value:
  - sample/runtime wrappers accept overlay inputs
  - strategy result schema now records raw selected names vs overlay-rejected names
  - single-run history and compare focused-strategy interpretation now surface those fields
- Added durable Phase 5 docs for:
  - baseline comparative research
  - compare parity first pass
  - first overlay requirements and selection
  - overlay runtime first pass
  - quarterly review
  - second overlay review
- Validation:
  - `python3 -m py_compile` passed for all changed finance/UI/runtime files
  - `.venv` smoke checks confirmed:
    - compare strict quality override can switch preset and persist overlay meta
    - strict value overlay path records `Overlay Rejected Ticker`
    - strict quality+value overlay path reuses the same first-pass overlay contract

### 2026-03-27 - Added trend-filter tooltip/explanation to strict family UI

- Added a shared inline help popover for the strict-family trend filter overlay in both single-strategy and compare forms.
- The tooltip now explains the actual first-pass behavior with a short A/B example:
  - month-end only check
  - `Close < MA(window)` moves that selected name to cash until the next rebalance
  - not an intramonth daily trigger

### 2026-03-27 - Phase 5 investable-readiness policy documented

- Fixed the Phase 5 operating direction around a more practical, investable research goal.
- Added a dedicated Phase 5 policy document:
  - `.note/finance/phase5/PHASE5_PRACTICAL_INVESTMENT_READINESS_POLICY.md`
- The policy now explicitly states:
  - the target is a decision-support quality research environment, not immediate live trading automation
  - strict managed universes should evolve toward freshness-aware presets
  - the preferred managed-universe policy is `backfill-to-target`, not `drop-only`
  - stale exclusions and replacement symbols should be shown transparently rather than silently hidden
- Synced the Phase 5 plan/TODO, Phase 4 handoff, roadmap, and doc index so the same practical-investment direction is visible from the planning documents.

### 2026-03-27 - Strict managed preset freshness backfill first pass implemented

- Implemented freshness-aware strict managed preset resolution in `app/web/pages/backtest.py`.
- Managed presets (`100/300/500/1000`) now:
  - scan a wider asset-profile candidate pool
  - exclude stale / missing symbols for the selected end date
  - backfill from lower-ranked eligible symbols
  - preserve target count as much as possible
- Added reporting for:
  - excluded symbols
  - replacement symbols
  - target vs resolved count
  - candidate scan size
- Single strict forms now show:
  - managed preset resolution summary
  - managed preset resolution details expander
- Compare strict forms now also use the same freshness-aware resolution instead of the old static preset list.
- Metadata/history now retain `managed_universe_resolution`.
- Validation:
  - `python3 -m py_compile` passed
  - smoke check:
    - `US Statement Coverage 300` -> `300/300`, no replacements
    - `US Statement Coverage 1000` -> `1000/1000`, `5` exclusions, `5` replacements

### 2026-03-27 - Historical-only strict preset semantics restored

- Rolled back the run-level freshness replacement experiment for strict managed presets.
- Current strict preset behavior is now:
  - preset ticker list stays fixed for the run
  - stale / missing symbols are not replaced at run level
  - each rebalance date naturally filters to symbols with usable price and factor data
- Kept `Price Freshness Preflight` as a diagnostic layer and added a short historical-backtest help tooltip in the UI.
- Removed managed-universe replacement metadata from:
  - `app/web/pages/backtest.py`
  - `app/web/runtime/backtest.py`
  - `app/web/runtime/history.py`
- Synced Phase 5 policy / roadmap / index docs so the current code now clearly reflects:
  - historical backtest first
  - no `Investable Now` mode in the current product surface

### 2026-03-27 - Compare strict strategy advanced-input visibility fixed

- Fixed the compare-screen UX issue where selecting strict family strategies did not immediately reveal their strategy-specific advanced inputs.
- Root cause:
  - the compare `Strategies` selector lived inside `st.form(...)`
  - so Streamlit did not rerun until submit, and the conditional advanced-input blocks stayed stale
- Changed `Strategies` selection to live outside the form while keeping execution inputs/submission inside the form.
- Added a short caption explaining that strategy-specific advanced inputs now update immediately.

### 2026-03-27 - Shared backtest history moved to its own top-level tab

- Reviewed the role of `Persistent Backtest History` / `History Drilldown` and confirmed they are shared assets for both:
  - single-strategy runs
  - compare / strategy-comparison runs
- Updated the backtest top-level tab structure to:
  - `Single Strategy`
  - `Compare & Portfolio Builder`
  - `History`
- Moved the shared history surface out of the compare tab into the new dedicated history tab.
- Added a short caption clarifying that the history view is common to both single and compare workflows.

### 2026-03-27 - Strict preflight stale classification and selection interpretation expanded

- Added heuristic stale / missing reason classification to strict annual price freshness preflight.
- Current classification labels:
  - `likely_delisted_or_symbol_changed`
  - `asset_profile_error`
  - `missing_price_rows`
  - `minor_source_lag`
  - `source_gap_or_symbol_issue`
  - `persistent_source_gap_or_symbol_issue`
- Added `Interpretation` support to strict selection history:
  - cash share computation
  - interpretation summary
  - overlay rejection frequency
  - row-level explanation strings

### 2026-03-27 - First overlay on/off validation completed

- Collected canonical overlay on/off validation results for:
  - `Quality Snapshot (Strict Annual)`
  - `Value Snapshot (Strict Annual)`
  - `Quality + Value Snapshot (Strict Annual)`
- Validation baseline:
  - `US Statement Coverage 100`
  - `2016-01-01 ~ 2026-03-20`
  - `month_end`
  - `MA200`
- Added wide-preset sanity check for `Quality Snapshot (Strict Annual)` on `US Statement Coverage 300`.
- Main result:
  - `Quality` strict saw a more defensive but weaker outcome with overlay on
  - `Value` and `Quality + Value` strict improved on canonical compare metrics with overlay on
- Synced the result into Phase 5 validation / roadmap docs.

### 2026-03-27 - Backtest selection interpretation hotfix: missing numpy import

- Fixed a runtime `NameError: name 'np' is not defined` in `app/web/pages/backtest.py`.
- Root cause:
  - the new selection-interpretation path uses `np.where(...)`
  - but `numpy as np` was not imported in the page module
- Added the missing import and re-ran `py_compile` for the page module successfully.

### 2026-03-28 - Value strict selection history hotfix: duplicate-column-safe cash handling

- Fixed a follow-up runtime failure while rendering `Selection History` for `Value Snapshot (Strict Annual)` runs.
- Root cause:
  - `_build_snapshot_selection_history(...)` assumed `selection_df['Cash']` and similar columns were always a 1-D series
  - some result shapes can surface duplicate column names, which makes `frame['Cash']` return a DataFrame instead
- Added duplicate-column-safe first-series extraction for:
  - `Selected Count`
  - `Raw Selected Count`
  - `Cash`
  - `Total Balance`
- Also de-duplicates columns defensively before building the selection-history view.

### 2026-03-28 - Latest-run selection-history renderer fallback added

- Added a defensive fallback in `_render_snapshot_selection_history(...)`.
- If an older or malformed run payload still fails the selection-history builder,
  the page now shows a warning with renderer detail instead of crashing the entire `Backtest` screen.
- This keeps the latest-run UI usable while older session/history payloads are being flushed or rerun.

### 2026-03-28 - Phase 5 strict family manual test checklist documented

- Added a dedicated manual QA checklist document for the current Phase 5 strict-family surface.
- Coverage includes:
  - single-strategy smoke
  - overlay on/off comparison
  - preflight / freshness diagnostics
  - compare strategy advanced inputs
  - shared history tab behavior
  - tooltip / copy verification
- Added the new checklist document to `FINANCE_DOC_INDEX.md`.

### 2026-03-28 - Phase closeout checklist rule added to repository guidance

- Updated `AGENTS.md` so future phase closeouts explicitly require:
  - a phase-specific manual test checklist document
  - user-facing verification coverage for the main features and UI paths added in that phase
  - checklist sharing as part of the final phase handoff

### 2026-03-28 - Strict-family interpretation/help copy localized to Korean

- Added Korean help/popover copy for the strict-family interpretation surfaces.
- Updated:
  - historical-universe help
  - trend-filter help
  - interpretation summary help
  - overlay rejection frequency help
  - cash-share help
- Also translated the main strict-family widget help text in single-strategy forms so tooltip copy aligns with the Korean UI flow.

### 2026-03-28 - Interpretation metric help refined for Raw/Final event semantics

- Refined strict-family interpretation help copy so `Raw Candidate Events` / `Final Selected Events` are described as:
  - rebalance-level selection event totals
  - not full eligible-universe size
- Added the practical reading rule:
  - overlay off -> Raw and Final are usually the same
  - overlay on -> the gap between Raw and Final indicates overlay intervention
- Added a short caption under `Interpretation Summary` to reinforce this reading in the UI.

### 2026-03-28 - Daily Market Update rate-limit reproduction and direction note

- Investigated `Daily Market Update` for `NYSE Stocks + ETFs` broad refresh behavior.
- Confirmed current raw source size:
  - `11,736` symbols
  - `434` non-plain symbols in the raw exchange source
- Reproduced early `YFRateLimitError('Too Many Requests...')` on broad runs.
- Also confirmed a secondary issue:
  - visible rate-limit failures do not always populate `batch_errors`
  - because `yfinance` can return partial frames while only surfacing symbol failures in provider output
- Added a durable analysis / direction document:
  - `.note/finance/DAILY_MARKET_UPDATE_RATE_LIMIT_ANALYSIS_20260328.md`

### 2026-03-28 - Daily Market Update rate-limit mitigation first pass implemented

- Implemented first-pass stabilization for `Daily Market Update`.
- Changed the UI default source from raw `NYSE Stocks + ETFs` to managed `Profile Filtered Stocks + ETFs`.
- Added OHLCV execution profiles:
  - `managed_safe`
  - `raw_heavy`
- Hardened the yfinance write path with:
  - smaller chunking
  - single-worker safe mode
  - retry backoff
  - sleep jitter
  - rate-limit cooldown events
- Added provider-message diagnostics so result details now track:
  - `rate_limited_symbols`
  - `provider_no_data_symbols`
  - `provider_message_batches`
  - `cooldown_events`
- Added raw-source optional filtering for non-plain symbols such as preferred/unit/special share classes.
- Added operator replay support in the result summary via:
  - `rerun_missing_payload`
  - `rerun_rate_limited_payload`
- Added an implementation summary note:
  - `.note/finance/DAILY_MARKET_UPDATE_RATE_LIMIT_IMPLEMENTATION_20260328.md`

### 2026-03-28 - Daily Market Update speed optimization second pass implemented

- Added a dedicated speed-optimization planning note after user validation showed a successful but slow broad run (~2400 sec).
- Implemented timing breakdown metrics in `store_ohlcv_to_mysql(...)`:
  - fetch
  - delete
  - upsert
  - retry sleep
  - cooldown sleep
  - inter-batch sleep
  - batch counts
- Surfaced the timing breakdown in the Streamlit `OHLCV Diagnostics` result panel.
- Added a new `managed_fast` execution profile for broad managed universes.
- Split execution profile routing by source:
  - `Profile Filtered Stocks + ETFs` -> `managed_fast`
  - raw NYSE sources -> `raw_heavy`
  - narrower/manual/profile-filtered single-side sources -> `managed_safe`
- Added a speed-optimization implementation note:
  - `.note/finance/DAILY_MARKET_UPDATE_SPEED_OPTIMIZATION_IMPLEMENTATION_20260328.md`

### 2026-03-28 - Backtest end-date default switched to today

- Replaced the hardcoded backtest end-date default (`2026-03-20`) with a shared `DEFAULT_BACKTEST_END_DATE = date.today()` constant.
- Applied the change across:
  - single-strategy forms
  - compare form
  - history/prefill fallback path
- This keeps new backtest runs aligned with the current calendar date by default.

### 2026-03-28 - Phase 5 first chapter closeout documentation added

- Added Phase 5 closeout documents:
  - `.note/finance/phase5/PHASE5_COMPLETION_SUMMARY.md`
  - `.note/finance/phase5/PHASE5_NEXT_PHASE_PREPARATION.md`
- Updated the Phase 5 current-chapter TODO board to reflect effective completion.
- Updated the roadmap and finance doc index so Phase 5 now reads as a closed first chapter with next-step candidates prepared.

### 2026-03-28 - Phase closeout rule expanded to include skill/reference refresh

- Updated `AGENTS.md` so future phase closeouts do not stop at:
  - completion summary
  - next-phase prep
  - manual test checklist
- Phase closeout now also requires a review of:
  - `AGENTS.md`
  - active finance skills / `SKILL.md`
  - `FINANCE_DOC_INDEX.md`
  - `MASTER_PHASE_ROADMAP.md`
  - phase-specific reference/preparation docs
- The new rule explicitly says that workflow/guidance changes should be refreshed at phase end if the implemented behavior changed how future work should be executed.

### 2026-03-28 - Codex MCP tool setup refreshed before next phase

- Confirmed `playwright` MCP was already installed and enabled in `~/.codex/config.toml`.
- Added `firecrawl` MCP to Codex using the hosted MCP endpoint:
  - `https://mcp.firecrawl.dev/v2/mcp`
  - bearer token env var: `FIRECRAWL_API_KEY`
- Kept the Firecrawl API key out of the Codex config file so the secret can be supplied via environment variable later.
- Scope note:
  - this is Codex/tooling setup work rather than a finance package behavior change.

### 2026-03-28 - Phase 6 formally opened

- Opened Phase 6 as the next major chapter after the Phase 5 first-chapter closeout.
- Fixed the new phase direction as:
  - second overlay implementation first
  - quarterly strict family entry/validation second
- Added:
  - `.note/finance/phase6/PHASE6_OVERLAY_AND_QUARTERLY_EXPANSION_PLAN.md`
  - `.note/finance/phase6/PHASE6_CURRENT_CHAPTER_TODO.md`
- Synced the new phase opening into:
  - `MASTER_PHASE_ROADMAP.md`
  - `FINANCE_DOC_INDEX.md`

### 2026-03-28 - Phase 6 first pass implemented: market regime overlay + strict quarterly prototype

- Fixed the initial Phase 6 runtime blocker in `app/web/runtime/backtest.py` where a stray `strict_label` reference caused the new strict wrapper path to fail.
- Implemented `Market Regime Overlay` first pass across strict family code paths:
  - strategy-level market-state evaluation in `finance/strategy.py`
  - benchmark MA data build path in `finance/sample.py`
  - strict annual runtime wrappers in `app/web/runtime/backtest.py`
  - single / compare / history / interpretation UI in `app/web/pages/backtest.py`
  - history persistence in `app/web/runtime/history.py`
- Added a research-only single-strategy path:
  - `Quality Snapshot (Strict Quarterly Prototype)`
- Verified DB-backed smoke runs for:
  - annual strict quality with trend + market regime overlay
  - annual strict value with trend + market regime overlay
  - annual strict quality+value with trend + market regime overlay
  - quarterly strict quality prototype with trend + market regime overlay
- Added Phase 6 reference and validation docs:
  - `.note/finance/phase6/PHASE6_MARKET_REGIME_OVERLAY_REQUIREMENTS.md`
  - `.note/finance/phase6/PHASE6_MARKET_REGIME_OVERLAY_FIRST_PASS.md`
  - `.note/finance/phase6/PHASE6_MARKET_REGIME_OVERLAY_VALIDATION.md`
  - `.note/finance/phase6/PHASE6_STRICT_QUARTERLY_ENTRY_CRITERIA.md`
  - `.note/finance/phase6/PHASE6_STRICT_QUARTERLY_FIRST_PASS_VALIDATION.md`
  - `.note/finance/phase6/PHASE6_TEST_CHECKLIST.md`
- Updated the Phase 6 TODO board, roadmap, finance doc index, and comprehensive analysis to reflect the implemented first pass.
- Current state:
  - Phase 6 implementation work for the planned `1 -> 9` first pass is complete
  - manual user testing is the next step

### 2026-03-28 - Phase 6 checklist-driven UX/history fixes

- Applied follow-up fixes from manual Phase 6 checklist review in `app/web/pages/backtest.py`.
- Clarified `Market Regime Window` semantics in help copy:
  - `200` now explicitly means the benchmark `200-trading-day moving average`.
- Relaxed regime/trend overlay input editing semantics:
  - window / benchmark inputs stay editable even when overlay enable is off
  - this applies to single strict forms and compare strict-family overrides
- Improved compare strict-family readability:
  - grouped each annual strict strategy override block into a separate bordered container
- Fixed single-strategy history prefill path:
  - `Load Into Form` now defers strategy selector changes until before widget creation, avoiding the Streamlit session-state mutation error
- Improved history drilldown:
  - compare records now store per-strategy summary rows in context
  - drilldown summary renders those rows instead of a confusing empty-primary-summary message
  - drilldown context now exposes strategy-level trend / market regime overrides in a readable table
- Added clearer UI copy:
  - `Load Into Form` action meaning
  - quarterly prototype late-coverage / delayed-active-period warning
- Added collapsible expander sections for compare strict annual family overrides so Quality / Value / Quality+Value settings can be opened and closed independently.
- Extended compare advanced-input collapsible expander pattern to `Equal Weight` and `GTAA` so their override sections can also be opened and closed independently.

### 2026-03-28 - Phase 6 closeout and Phase 7 opening

- Closed out Phase 6 with:
  - `.note/finance/phase6/PHASE6_COMPLETION_SUMMARY.md`
  - `.note/finance/phase6/PHASE6_NEXT_PHASE_PREPARATION.md`
- Marked the Phase 6 chapter TODO and phase plan as closeout-complete.
- Updated roadmap/index/comprehensive analysis so Phase 6 now reads as completed.
- Opened Phase 7 as the next active chapter with:
  - `.note/finance/phase7/PHASE7_QUARTERLY_COVERAGE_AND_STATEMENT_PIT_HARDENING_PLAN.md`
  - `.note/finance/phase7/PHASE7_CURRENT_CHAPTER_TODO.md`
- Fixed the next-phase direction as:
  - quarterly coverage hardening first
  - statement raw payload / PIT timing reality-check first
  - quarterly prototype longer-history recovery second

### 2026-03-28 - Phase 7 statement payload inspection and quarterly hardening

- Inspected live EDGAR statement source payloads for `AAPL`, `MSFT`, `GOOG`, `NVDA`, `JPM`.
- Confirmed the source already provides long-history fact coverage and real timing fields:
  - `filing_date`
  - `accepted_at`
  - `available_at`
  - `report_date`
  - `accession`
- Confirmed quarterly late-start was not primarily a source problem.
- Identified the concrete blockers:
  - quarterly ingestion excluded `10-K/FY` rows
  - statement ingestion defaults were too shallow
  - quarterly shadow builder was dropping valid rows via a `report_date` anchor filter
- Patched:
  - `finance/data/financial_statements.py`
  - `finance/data/fundamentals.py`
  - `finance/loaders/financial_statements.py`
  - `finance/loaders/__init__.py`
  - `app/jobs/ingestion_jobs.py`
  - `app/web/streamlit_app.py`
- Opened `periods=0` as `all available periods` in both statement-ingestion UI paths.
- Added human-readable inspection path:
  - richer `inspect_financial_statement_source()`
  - new `load_statement_timing_audit(...)`
- Reingested quarterly all-history sample symbols:
  - `AAPL`, `MSFT`, `GOOG`
- Verified raw quarterly ledger recovery:
  - `AAPL`: `2024-09-28 -> 2006-09-30`
  - `MSFT`: `2024-09-30 -> 2007-06-30`
  - `GOOG`: `2024-06-30 -> 2012-12-31`
- Rebuilt quarterly statement shadow fundamentals/factors for the sample and confirmed the strict quarterly prototype becomes active again from `2016-01-29`.
- Rebuilt quarterly `US Statement Coverage 100`:
  - raw values ingest job: `509.03s`, `inserted_values=1,023,285`
  - raw values table state: `100 symbols`, `876,657 rows`, `distinct_accessions=6,163`, `min_period_end=2000-01-01`
  - shadow fundamentals/factors: `100 symbols`, `6,796 rows`, `min_period_end=2006-09-24`
- Confirmed `Quality Snapshot (Strict Quarterly Prototype)` on `US Statement Coverage 100` now opens from `2016-01-29` rather than only near `2025`.

### 2026-03-28 - Phase 7 checklist pre-validation by assistant

- Re-ran the Phase 7 checklist before user handoff.
- Verified UI/input semantics by code inspection:
  - `Extended Statement Periods` and `Financial Statement Periods` both allow `0`
  - both surfaces include `0 = all available periods` guidance
- Verified helper/runtime checkpoints:
  - `load_statement_coverage_summary(..., freq="quarterly")` shows restored long-history sample coverage for `AAPL/MSFT/GOOG`
  - `load_statement_timing_audit(...)` returns the expected PIT timing columns
  - `inspect_financial_statement_source(...)` returns `fiscal_period_counts`, `timing_field_inventory`, and `sample_filings`
- Verified quarterly prototype behavior:
  - `US Statement Coverage 100` first active date = `2016-01-29`
  - manual `AAPL,MSFT,GOOG` first active date = `2016-01-29`
  - 2016 balances move over time, so the prototype is no longer stuck in flat late-start cash mode
- Verified quarterly shadow coverage:
  - `nyse_fundamentals_statement` quarterly = `100 symbols`, `6,796 rows`
- Verified annual strict regression:
  - annual strict quality/value runtime still execute successfully
  - manual `AAPL,MSFT,GOOG` annual strict late start remains around `2025-07-31`, which matches current annual strict data availability and is not introduced by Phase 7

### 2026-03-28 - Phase 7 supplementary polish pass

- Audited remaining practical gaps after the quarterly coverage/PIT hardening first pass.
- Added weekend/holiday-aware strict price freshness handling:
  - new loader helper `load_latest_market_date(...)`
  - preflight now compares against `effective trading end` instead of blindly using the selected end date
- Verified `US Statement Coverage 100` with end `2026-03-28` now reports:
  - `effective trading end = 2026-03-27`
  - `stale_count = 0`
- Added `Statement Shadow Coverage Preview` to the quarterly prototype single-strategy form.
  - preview now shows:
    - requested / covered
    - earliest period
    - latest period
    - median rows per symbol
- Added `Statement PIT Inspection` card to the `Ingestion` tab.
  - UI now exposes:
    - DB coverage summary
    - DB timing audit
    - EDGAR source payload inspection
  - this reduces the need for separate notebook snippets during Phase 7 validation
- Refreshed quarterly prototype guidance text to reflect Phase 7 coverage recovery.
- Synced:
  - `PHASE7_QUARTERLY_RERUN_VALIDATION.md`
  - `PHASE7_CURRENT_CHAPTER_TODO.md`
  - `PHASE7_QUARTERLY_COVERAGE_AND_STATEMENT_PIT_HARDENING_PLAN.md`
  - `PHASE7_TEST_CHECKLIST.md`
  - `FINANCE_COMPREHENSIVE_ANALYSIS.md`
  - `FINANCE_DOC_INDEX.md`

### 2026-03-28 - Phase 7 deferred-validation closeout and Phase 8 kickoff

- Added Phase 7 closeout docs:
  - `PHASE7_COMPLETION_SUMMARY.md`
  - `PHASE7_NEXT_PHASE_PREPARATION.md`
- Marked Phase 7 as:
  - implementation completed
  - user manual validation deferred for later batch review together with Phase 8
- Opened Phase 8 documents:
  - `PHASE8_QUARTERLY_STRATEGY_FAMILY_EXPANSION_PLAN.md`
  - `PHASE8_CURRENT_CHAPTER_TODO.md`
- Updated:
  - `MASTER_PHASE_ROADMAP.md`
  - `FINANCE_DOC_INDEX.md`
  - `PHASE7_CURRENT_CHAPTER_TODO.md`
- Fixed the next active direction as:
  - quarterly strategy family expansion
  - quarterly promotion readiness

### 2026-03-28 - Phase 8 quarterly family first pass

- Implemented quarterly strict family expansion beyond the existing quality-only prototype.
- Added runtime wrappers:
  - `run_value_snapshot_strict_quarterly_prototype_backtest_from_db(...)`
  - `run_quality_value_snapshot_strict_quarterly_prototype_backtest_from_db(...)`
- Added single-strategy UI forms:
  - `Value Snapshot (Strict Quarterly Prototype)`
  - `Quality + Value Snapshot (Strict Quarterly Prototype)`
- Opened quarterly family compare exposure for all three quarterly prototypes:
  - quality
  - value
  - quality + value
- Wired quarterly strategy keys through:
  - latest run selection history
  - history payload rerun / load-into-form prefill
  - focused strategy interpretation
  - compare strategy defaults / preset resolution
- Validation:
  - manual `AAPL/MSFT/GOOG`
    - quarterly value first active = `2017-05-31`
    - quarterly quality+value first active = `2017-05-31`
  - preset `US Statement Coverage 100`
    - quarterly value first active = `2016-01-29`
    - quarterly quality+value first active = `2016-01-29`
  - compare smoke:
    - `_run_compare_strategy(\"Value Snapshot (Strict Quarterly Prototype)\")` returned a bundle
    - selection history build returned `123` rows
  - compile/import:
    - `py_compile` passed for pages/runtime/sample touched in Phase 8
    - `app.web.streamlit_app` import OK
- Added Phase 8 durable docs:
  - `PHASE8_QUARTERLY_FAMILY_SCOPE_AND_COMPARE_DECISION.md`
  - `PHASE8_QUARTERLY_VALUE_AND_MULTI_FACTOR_FIRST_PASS.md`
  - `PHASE8_QUARTERLY_VALIDATION_FIRST_PASS.md`
  - `PHASE8_PROMOTION_READINESS_CRITERIA_DRAFT.md`
  - `PHASE8_TEST_CHECKLIST.md`
- Synced:
  - `PHASE8_CURRENT_CHAPTER_TODO.md`
  - `PHASE8_QUARTERLY_STRATEGY_FAMILY_EXPANSION_PLAN.md`
  - `FINANCE_COMPREHENSIVE_ANALYSIS.md`
  - `FINANCE_DOC_INDEX.md`

### 2026-03-28 - Phase 8 checklist prevalidation by assistant

- Ran an automated prevalidation pass against `PHASE8_TEST_CHECKLIST.md`.
- Confirmed all checklist items that are testable without a browser:
  - single quarterly value runtime/UI wiring
  - single quarterly quality+value runtime/UI wiring
  - manual small-universe runs
  - compare quarterly-family exposure
  - compare execution
  - history append/load/payload/prefill helper
  - quarterly meta/context fields
  - research-only semantics and default preset
- Notable outputs:
  - preset `US Statement Coverage 100`
    - value quarterly `End Balance = 140,853.2`
    - quality+value quarterly `End Balance = 187,769.4`
  - manual `AAPL/MSFT,GOOG`
    - quality quarterly first active = `2016-01-29`
    - value quarterly first active = `2017-05-31`
    - quality+value quarterly first active = `2017-05-31`
- Created:
  - `PHASE8_CHECKLIST_PREVALIDATION.md`
- Remaining validation:
  - browser-level visual/manual UX readout by the user later

### 2026-03-28 - Phase 7 ingestion UI clarification pass

- Addressed user confusion around Phase 7 checklist item 1 and 2:
  - clarified in `Ingestion > Extended Statement Refresh` that the older lower-level `Financial Statement Ingestion` card still exists further below under `Manual Jobs`
  - clarified in `Ingestion > Financial Statement Ingestion` that it is a lower-level manual card and that routine statement history recovery should start with `Extended Statement Refresh`
  - clarified in `Ingestion > Statement PIT Inspection` that it is read-only:
    - `Coverage Summary` and `Timing Audit` read already stored MySQL statement ledgers
    - `Source Payload Inspection` fetches one live EDGAR sample payload only for field inspection
- Updated `PHASE7_TEST_CHECKLIST.md` so item 1 points to the actual UI structure and item 2 explains what PIT inspection reads.
- Validation:
  - `python3 -m py_compile app/web/streamlit_app.py` passed

### 2026-03-28 - Ingestion console tab separation

- Reworked the `Ingestion` left-side console to separate collection work into two explicit tabs:
  - `Operational Pipelines`
  - `Manual Jobs / Inspection`
- Added Korean top-of-tab guidance boxes because Streamlit tab labels do not support native hover help:
  - operational tab now explains it owns recurring production refresh work
  - manual tab now explains it owns exception handling, partial reruns, debugging, and PIT inspection
- Moved the Phase 7/8 mental model into the UI:
  - routine statement history recovery starts from `Extended Statement Refresh`
  - lower-level `Financial Statement Ingestion` and `Statement PIT Inspection` live under the manual/inspection tab
- Updated `PHASE7_TEST_CHECKLIST.md` to match the new tab layout.
- Validation:
  - `python3 -m py_compile app/web/streamlit_app.py` passed

### 2026-03-28 - Ingestion UI clarification and inline result placement

- Added inline help/caption clarification for:
  - `Financial Statement Freq` vs `Financial Statement Period Type`
  - `Timing Audit Symbols`
  - `Rows / Symbol`
  - `Source Sample Size`
  - `Source Inspection Symbol`
- Interpretation now exposed in UI:
  - `Statement PIT Inspection` is read-only
  - `Financial Statement Freq` controls target ledger frequency / allowed filing filters
  - `Financial Statement Period Type` controls the EDGAR statement view request
  - normal runs should usually keep the two aligned
- Removed the global top-of-page `Latest Completed Run` insertion from the ingestion console and now render the latest completed result inline under the matching job card to reduce scroll disruption after job completion.
- Validation:
  - `python3 -m py_compile app/web/streamlit_app.py` passed

### 2026-03-29 - Manual financial statement ingestion mode simplification

- Simplified `Ingestion > Manual Jobs / Inspection > Financial Statement Ingestion`:
  - removed separate operator-facing `Financial Statement Freq` and `Financial Statement Period Type` controls
  - added one operator-facing `Statement Mode` control (`annual` / `quarterly`)
  - internal job params still pass both `freq` and `period`, but now they are aligned automatically from the selected mode
- Updated:
  - `PHASE7_TEST_CHECKLIST.md`
  - `FINANCE_COMPREHENSIVE_ANALYSIS.md`
- Validation:
  - `python3 -m py_compile app/web/streamlit_app.py` passed

### 2026-03-29 - Statement PIT Inspection interpretation guide

- Added inline interpretation help to `Ingestion > Manual Jobs / Inspection > Statement PIT Inspection`:
  - top-level `이 카드 읽는 법` expander
  - per-section captions for:
    - `Coverage Summary`
    - `Timing Audit`
    - `Source Payload Inspection`
- The card now explains in Korean how to read:
  - DB coverage vs timing audit vs live source sample
  - `Inspection Frequency`
  - `Timing Audit Symbols`
  - `Rows / Symbol`
  - `Source Sample Size`
  - `Source Inspection Symbol`
- Synced:
  - `FINANCE_COMPREHENSIVE_ANALYSIS.md`
- Validation:
  - `python3 -m py_compile app/web/streamlit_app.py` passed

### 2026-03-29 - Overlay cash policy research

- Researched overlay cash-handling semantics for the strict factor family without changing strategy logic.
- Reconfirmed current implementation behavior:
  - partial trend-overlay rejections are reallocated across surviving names
  - only `all rejected` and market-regime `risk_off` paths create full cash states
- Collected practitioner references across three buckets:
  - stock-selection / factor-filter portfolios
  - tactical asset allocation sleeves
  - market-regime / hedge overlays
- Concluded that the current strict family is closer to the stock-selection bucket, where survivor reweighting is the more typical default.
- Added a durable research note:
  - `.note/finance/OVERLAY_CASH_POLICY_RESEARCH.md`
- Synced:
  - `FINANCE_DOC_INDEX.md`
  - `QUESTION_AND_ANALYSIS_LOG.md`
  - `FINANCE_COMPREHENSIVE_ANALYSIS.md`

### 2026-03-29 - Price stale diagnosis first pass

- Added a read-only stale-price diagnosis flow under:
  - `Ingestion > Manual Jobs / Inspection > Price Stale Diagnosis`
- Implemented provider probing without DB writes:
  - `5d`
  - `1mo`
  - `3mo`
- The diagnosis now combines:
  - DB latest daily price date
  - provider re-probe result
  - asset profile status summary
- Added first-pass operator classifications:
  - `local_ingestion_gap`
  - `provider_source_gap`
  - `likely_delisted_or_symbol_changed`
  - `asset_profile_error`
  - `rate_limited_during_probe`
  - `inconclusive`
- Added targeted `Daily Market Update` payload output only for:
  - `local_ingestion_gap`
  - `local_ingestion_gap_partial`
- Updated strict backtest preflight copy so yellow stale warnings now point to the new diagnosis card for deeper triage.
- Synced:
  - `FINANCE_DOC_INDEX.md`
  - `FINANCE_COMPREHENSIVE_ANALYSIS.md`
  - `QUESTION_AND_ANALYSIS_LOG.md`
  - `PHASE7_TEST_CHECKLIST.md`
  - `PHASE8_TEST_CHECKLIST.md`

### 2026-03-29 - Statement shadow coverage gap diagnostics

- Expanded quarterly prototype `Statement Shadow Coverage Preview` so it no longer stops at `Requested` / `Covered` metrics.
- Added:
  - help popover explaining what `Covered` means
  - `Coverage Gap Drilldown`
  - missing symbol table
  - raw-statement-vs-shadow classification
  - targeted `Extended Statement Refresh` / `Financial Statement Ingestion` payload for symbols with no strict raw statement coverage
- Introduced two operator-facing labels:
  - `no_raw_statement_coverage`
  - `raw_statement_present_but_shadow_missing`
- Verified on `US Statement Coverage 300` quarterly preview:
  - `Requested = 300`
  - `Covered = 100`
  - `Missing = 200`
  - `Need Raw Collection = 200`
  - `Raw Exists / Shadow Missing = 0`
- Synced:
  - `FINANCE_DOC_INDEX.md`
  - `FINANCE_COMPREHENSIVE_ANALYSIS.md`
  - `PHASE7_TEST_CHECKLIST.md`
  - `PHASE8_TEST_CHECKLIST.md`
  - `PHASE8_CURRENT_CHAPTER_TODO.md`

### 2026-03-29 - Extended Statement Refresh shadow rebuild fix

- Investigated why `Quality Snapshot (Strict Quarterly Prototype)` could still show the same `Statement Shadow Coverage Preview` after a user-triggered quarterly `Extended Statement Refresh`.
- Confirmed the root cause:
  - `Extended Statement Refresh` had only been refreshing raw statement ledgers
  - quarterly preview reads `nyse_fundamentals_statement`
  - therefore preview coverage could stay unchanged even after a successful raw refresh
- Updated `run_extended_statement_refresh(...)` to execute three stages for the selected `freq`:
  - `collect_financial_statements`
  - `statement_fundamentals_shadow`
  - `statement_factors_shadow`
- Updated `Ingestion > Extended Statement Refresh` copy to describe the shadow rebuild behavior and write targets.
- Smoke validation:
  - before fix, `CRWD` quarterly raw ledger existed while quarterly shadow rows were `0`
  - after the fixed `Extended Statement Refresh`, `CRWD` quarterly shadow rows became `33`

### 2026-03-29 - Ingestion UI polish and utility review

- Removed the top-level `Write Targets` table from `Ingestion` because the same information already exists in each card's `Writes to:` caption.
- Converted the left-column run-job surfaces to expander-based sections in both:
  - `Operational Pipelines`
  - `Manual Jobs / Inspection`
- Reviewed utility panels:
  - `Recent Logs`
    - confirmed functional
    - reads latest `*.log` files and renders tail preview
  - `Failure CSV Preview`
    - confirmed functional
    - currently lower operational value because only legacy `*failures*.csv` artifacts are present and not all modern jobs emit them
- Added captions to make the current intended semantics of both panels explicit.
- Added durable review note:
  - `.note/finance/phase8/PHASE8_INGESTION_UI_POLISH_AND_REVIEW.md`

### 2026-03-29 - Quarterly shadow preview cache/performance follow-up

- Investigated the user report that:
  - `Statement Shadow Coverage Preview` was slower than `Price Freshness Preflight`
  - `Covered` barely moved after large quarterly refresh runs
- Confirmed three root causes:
  - pre-fix `Extended Statement Refresh` had left many symbols in `raw present / shadow missing` state
  - preview helper used `lru_cache` and was not cleared after statement-related jobs
  - preview diagnostics still relied on expensive Python-side grouping for raw/shadow coverage summaries
- Implemented:
  - cache clear after `extended_statement_refresh` and `collect_financial_statements`
  - SQL aggregate loader for raw statement coverage summary
  - SQL aggregate loader for statement shadow coverage summary
- Validation snapshot on `US Statement Coverage 500` quarterly:
  - `Covered = 101`
  - `Missing = 399`
  - `Need Raw Collection = 3`
  - `Raw Exists / Shadow Missing = 396`
- Verified that post-fix refresh now repairs the large `raw present / shadow missing` bucket:
  - `CME`: shadow rows `0 -> 73`
  - `MCK`: shadow rows `0 -> 73`
- Verified the user's long `US Statement Coverage 500` run via `WEB_APP_RUN_HISTORY.jsonl`:
  - `2026-03-29 11:03:02`
  - `symbols_requested = 500`
  - `duration_sec = 1506.713`
  - `step_jobs = []`
- Interpretation:
  - that 500-symbol run was executed on the old raw-only `Extended Statement Refresh` path
  - therefore it consumed runtime but could not materially raise quarterly `Statement Shadow Coverage Preview`
- Current post-fix coverage snapshot:
  - `Covered = 103`
  - `Missing = 397`
  - `Need Raw Collection = 3`
  - `Raw Exists / Shadow Missing = 394`

### 2026-03-29 - Operator runtime / shadow rebuild / artifact tooling

- Implemented `Runtime / Build` indicator at the top of `Ingestion`:
  - shows runtime marker, process loaded time, and git short SHA
  - the same runtime metadata now flows into persisted run metadata
- Added `Statement Shadow Rebuild Only` under `Ingestion > Manual Jobs / Inspection`:
  - rebuilds `nyse_fundamentals_statement` and `nyse_factors_statement`
  - does not call EDGAR raw collection again
- Added coverage-gap action bridge from quarterly backtest preview:
  - raw-gap symbols can be sent to `Extended Statement Refresh`
  - raw-present / shadow-missing symbols can be sent to `Statement Shadow Rebuild Only`
- Added `Run Inspector` under persisted ingestion history:
  - re-renders selected run summary
  - shows runtime marker and related logs
  - exposes standardized artifact paths
- Added standardized run artifact emission for web-app ingestion runs:
  - `.note/finance/run_artifacts/<run-key>/result.json`
  - `.note/finance/run_artifacts/<run-key>/manifest.json`
  - `csv/<run-key>_failures.csv` when symbol-level issues exist
- Validation:
  - `py_compile` passed for updated app/job/backtest files
  - `run_rebuild_statement_shadow(['CRWD'], freq='quarterly')` returned `success`
  - current quarterly coverage summary for `US Statement Coverage 500` still reads:
    - `Covered = 103`
    - `Missing = 397`
    - `Need Raw Collection = 3`
    - `Raw Exists / Shadow Missing = 394`
  - both action payloads now exist:
    - raw refresh payload = `True`
    - shadow rebuild payload = `True`
