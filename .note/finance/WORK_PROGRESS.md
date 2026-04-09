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

### 2026-04-05
- Continued Phase 12 ETF real-money hardening with a current-operability policy first pass for `GTAA`, `Risk Parity Trend`, and `Dual Momentum`.
- Expanded `finance_meta.nyse_asset_profile` to store ETF-oriented current snapshot fields:
  - `fund_family`
  - `total_assets`
  - `bid`
  - `ask`
  - `bid_size`
  - `ask_size`
- Updated asset-profile collection to sync the schema and persist the new ETF fields from yfinance metadata/quote payloads.
- Extended asset-profile loader summaries so runtime policy helpers can read:
  - `total_assets`
  - `fund_family`
  - `bid`
  - `ask`
  - `bid_size`
  - `ask_size`
- Added ETF real-money inputs:
  - `Min ETF AUM ($B)`
  - `Max Bid-Ask Spread (%)`
- Added shared ETF operability policy output:
  - `etf_operability_status`
  - coverage/pass counts
  - failed-symbol previews
- Connected the ETF operability policy to:
  - single strategy forms
  - compare overrides
  - history / `Load Into Form`
  - saved strategy overrides
  - `Real-Money`
  - `Execution Context`
  - compare `Strategy Highlights`
- Reflected ETF operability status in `promotion_decision` so `caution` / `unavailable` states hold back promotion.
- Documented the change as a current-snapshot ETF operability overlay rather than a point-in-time ETF liquidity history model.
- Reviewed Phase 12 remaining work and decided the current ETF second-pass items are next-phase backlog rather than closeout blockers.
- Created:
  - `.note/finance/phase12/PHASE12_COMPLETION_SUMMARY.md`
  - `.note/finance/phase12/PHASE12_NEXT_PHASE_PREPARATION.md`
- Marked Phase 12 as practical closeout in:
  - roadmap
  - doc index
  - phase TODO board
- Fixed Streamlit navigation structure before Phase 12 manual testing:
  - moved `backtest_strategy_catalog` helper out of `app/web/pages/`
  - switched the main app to explicit top navigation
  - added `Overview`, `Ingestion`, `Backtest`, `Ops Review`, `Guides` pages
- This also removes the accidental helper-page exposure that previously showed `backtest_strategy_catalog` in the UI page list.

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

### 2026-03-29 - Statement coverage diagnosis guidance

- Added `Statement Coverage Diagnosis` under `Ingestion > Manual Jobs / Inspection`:
  - combines DB strict raw coverage
  - DB statement shadow coverage
  - live EDGAR sample inspection
  - returns per-symbol next-action guidance instead of showing only a numeric coverage gap
- Added quarterly backtest bridge:
  - `Coverage Gap Drilldown` can now send missing symbols directly to `Statement Coverage Diagnosis`
- Implemented per-symbol diagnosis buckets:
  - `shadow_available`
  - `raw_present_shadow_missing`
  - `source_present_raw_missing`
  - `foreign_or_nonstandard_form_structure`
  - `source_empty_or_symbol_issue`
  - `source_present_but_not_supported_for_current_mode`
  - `inconclusive_statement_coverage`
- Verified real examples:
  - `MRSH` -> `source_empty_or_symbol_issue`
  - `AU` -> `foreign_or_nonstandard_form_structure`
- Validation:
  - `python3 -m py_compile app/jobs/diagnostics.py app/web/streamlit_app.py app/web/pages/backtest.py`
  - `.venv/bin/python` smoke test confirmed per-symbol diagnosis output and no recommended refresh/rebuild payload for `MRSH`, `AU`

### 2026-03-29 - Coverage Gap Drilldown wording and bridge feedback polish

- Clarified that `Coverage Gap Drilldown` is a coarse stage only:
  - renamed the table column from `Diagnosis` to `Coverage Gap Status`
  - added caption text explaining that fine-grained root-cause labels live in `Statement Coverage Diagnosis`
- Added backtest-side feedback after bridge buttons are pressed:
  - when a handoff button is clicked, backtest now shows a success banner after rerun
  - this makes it visible that symbols were loaded into the target ingestion card instead of looking like “nothing happened”

### 2026-03-29 - Statement coverage guidance localized to Korean

- Localized per-symbol operator guidance text in `Statement Coverage Diagnosis`:
  - `recommended_action`
  - `note`
  - `stepwise_guidance`
- Kept the column labels in English and localized only the values shown inside those columns.
- Validation:
  - `python3 -m py_compile app/jobs/diagnostics.py app/web/streamlit_app.py`
  - smoke check confirmed Korean action/guidance output for `MRSH`, `AU`

### 2026-03-29 - Phase 7 closeout and Phase 9/10 guidance prep

- Marked Phase 7 as closeout-complete after substantial checklist review and later operator follow-up absorption into Phase 8 tooling
- Updated roadmap state:
  - `Phase 7 = completed`
  - `Phase 8 = implementation_completed / manual_validation_pending`
- Added forward guidance docs:
  - `phase9/PHASE9_STRICT_COVERAGE_POLICY_AND_PROMOTION_PLAN.md`
  - `phase10/PHASE10_PORTFOLIO_PRODUCTIZATION_AND_RESEARCH_WORKFLOW_PLAN.md`
- Intent:
  - keep Phase 8 active for later batch validation
  - prepare the next two major workstreams without prematurely opening them

### 2026-03-29 - Phase 9 kickoff

- Opened `Phase 9` as the active policy/governance phase
- Added:
  - `phase9/PHASE9_CURRENT_CHAPTER_TODO.md`
- Updated roadmap state:
  - `Phase 8 = implementation_completed / manual_validation_pending`
  - `Phase 9 = in_progress`
- Current Phase 9 focus:
  - strict coverage exception inventory
  - foreign / non-standard form policy
  - annual / quarterly promotion gate

### 2026-03-29 - Phase 9 plan concretized

- Expanded `PHASE9_STRICT_COVERAGE_POLICY_AND_PROMOTION_PLAN.md` from a directional note into a more concrete execution plan
- Added:
  - recommended default policy stance
  - chapter-by-chapter execution order
  - concrete decisions that must be locked this phase
  - provisional default handling for:
    - `source_empty_or_symbol_issue`
    - `foreign_or_nonstandard_form_structure`
    - `raw_present_shadow_missing`
    - `source_present_raw_missing`
- Updated `PHASE9_CURRENT_CHAPTER_TODO.md` with the same provisional baseline

### 2026-03-29 - Static preset vs historical dynamic universe clarification

- Confirmed current strict preset semantics from code and docs:
  - preset membership is loaded from the current managed market-cap/profile universe
  - the run then applies rebalance-date availability filtering for price/factor usability
- Interpretation:
  - current `Coverage 100/300/500/1000` is **not** a historical monthly top-N universe
  - it is a **run-level static managed research universe**
- Added this semantic decision as an explicit Phase 9 policy item

### 2026-03-29 - Real-money validation direction documented

- Added `phase9/PHASE9_REAL_MONEY_VALIDATION_DIRECTION.md`
- Documented the recommended order for a real-investing target:
  - Phase 9 locks policy / governance / promotion gate
  - the next major engineering priority should be `historical dynamic PIT universe`
  - portfolio productization should follow after the PIT universe contract is available
- Synced the same guidance into:
  - `PHASE9_STRICT_COVERAGE_POLICY_AND_PROMOTION_PLAN.md`
  - `PHASE9_CURRENT_CHAPTER_TODO.md`
  - `PHASE10_PORTFOLIO_PRODUCTIZATION_AND_RESEARCH_WORKFLOW_PLAN.md`
  - `FINANCE_DOC_INDEX.md`

### 2026-03-29 - Phase 9 policy document set completed (first pass)

- Added:
  - `phase9/PHASE9_STRICT_COVERAGE_EXCEPTION_INVENTORY.md`
  - `phase9/PHASE9_STRICT_COVERAGE_POLICY_DECISION.md`
  - `phase9/PHASE9_STRICT_FAMILY_PROMOTION_GATE.md`
  - `phase9/PHASE9_OPERATOR_DECISION_TREE.md`
  - `phase9/PHASE9_TEST_CHECKLIST.md`
- Assistant-side precheck used current diagnostics/contracts:
  - `US Statement Coverage 300` -> covered `298`, missing `2`
  - `US Statement Coverage 500` -> covered `497`, missing `3`
  - `US Statement Coverage 1000` -> covered `988`, missing `12`
  - active missing symbols were dominated by:
    - `source_empty_or_symbol_issue`
    - `foreign_or_nonstandard_form_structure`
- Synced the same first-pass policy conclusion into:
  - `PHASE9_CURRENT_CHAPTER_TODO.md`
  - `MASTER_PHASE_ROADMAP.md`
  - `FINANCE_DOC_INDEX.md`
  - `FINANCE_COMPREHENSIVE_ANALYSIS.md`
- Current Phase 9 status:
  - policy/guidance/checklist first pass completed
  - user review and later checklist confirmation still pending

### 2026-03-29 - Phase 8/9/10 batch validation path agreed

- Confirmed that the user can defer manual validation and later run:
  - `Phase 8 checklist`
  - `Phase 9 checklist`
  - `Phase 10 checklist`
  together as a batch review
- Recorded the guidance that:
  - this is operationally acceptable
  - the tradeoff is slightly harder regression isolation if an issue appears later
- Synced the same note into `phase9/PHASE9_CURRENT_CHAPTER_TODO.md`

### 2026-03-29 - Phase 10 preparation documents added

- Added:
  - `phase10/PHASE10_CURRENT_CHAPTER_TODO.md`
  - `phase10/PHASE10_EXECUTION_PREPARATION.md`
  - `phase10/PHASE10_TEST_CHECKLIST.md`
- Goal:
  - keep Phase 10 prepared without activating it yet
  - make the execution order explicit once productization becomes the active workstream
- Key preparation decision:
  - if Phase 10 opens later, the preferred order is:
    - saved portfolio contract
    - compare-to-portfolio bridge
    - saved portfolio UI first pass
    - richer portfolio readouts
    - workflow integration
- Synced the new docs into:
  - `PHASE10_PORTFOLIO_PRODUCTIZATION_AND_RESEARCH_WORKFLOW_PLAN.md`
  - `FINANCE_DOC_INDEX.md`
  - `MASTER_PHASE_ROADMAP.md`

### 2026-03-29 - Phase 10 vs dynamic PIT scope clarified

- Clarified the phase boundary:
  - `historical dynamic PIT universe` is not part of Phase 10
  - Phase 10 remains the portfolio productization/workflow phase
- Recommended execution order remains:
  - Phase 9 policy lock
  - separate dynamic PIT universe workstream
  - then Phase 10 activation if productization is the next priority

### 2026-03-29 - Phase numbering reordered for real-money priority

- Reordered the planned phases to match the actual recommended execution order:
  - `Phase 10` -> `historical dynamic PIT universe`
  - `Phase 11` -> portfolio productization / research workflow
- Moved the previously prepared productization docs from `phase10/` to `phase11/`
- Added the new dynamic-PIT planning docs:
  - `phase10/PHASE10_HISTORICAL_DYNAMIC_PIT_UNIVERSE_PLAN.md`
  - `phase10/PHASE10_CURRENT_CHAPTER_TODO.md`
  - `phase10/PHASE10_TEST_CHECKLIST.md`
- Synced the renumbering into:
  - `MASTER_PHASE_ROADMAP.md`
  - `FINANCE_DOC_INDEX.md`
  - `QUESTION_AND_ANALYSIS_LOG.md`

### 2026-03-29 - Phase 10 dynamic PIT plan concretized

- Added:
  - `phase10/PHASE10_PIT_SOURCE_AND_SCHEMA_GAP_ANALYSIS.md`
  - `phase10/PHASE10_DYNAMIC_PIT_FIRST_PASS_IMPLEMENTATION_ORDER.md`
- Confirmed from current code/schema:
  - `nyse_asset_profile` is a current snapshot, not historical PIT universe history
  - `nyse_price_history` is usable as rebalance-date price input
  - `nyse_fundamentals_statement` and `nyse_factors_statement` contain PIT-aware shadow timing and shares-outstanding / market-cap ingredients
- First-pass implementation recommendation was tightened to:
  - keep current static preset mode unchanged
  - start dynamic PIT with `strict annual family`
  - build rebalance-date approximate PIT market-cap membership from:
    - price history
    - latest known statement `shares_outstanding`
- Synced the same planning set into:
  - `PHASE10_CURRENT_CHAPTER_TODO.md`
  - `PHASE10_HISTORICAL_DYNAMIC_PIT_UNIVERSE_PLAN.md`
  - `FINANCE_DOC_INDEX.md`
  - `MASTER_PHASE_ROADMAP.md`

### 2026-03-29 - Phase 10 annual strict dynamic PIT first pass implemented

- Started actual Phase 10 implementation with annual strict single-strategy family first.
- Added a new `Universe Contract` selector to:
  - `Quality Snapshot (Strict Annual)`
  - `Value Snapshot (Strict Annual)`
  - `Quality + Value Snapshot (Strict Annual)`
- Kept the existing static contract unchanged:
  - `static_managed_research`
- Added a new additive first-pass contract:
  - `historical_dynamic_pit`
- Implemented a rebalance-date approximate PIT universe builder in `finance/sample.py` that:
  - reads rebalance-date price rows
  - selects the latest annual statement-shadow row with `latest_available_at <= rebalance_date`
  - uses `shares_outstanding`
  - recomputes approximate market cap and top-N membership
- Integrated the new builder into annual strict runtime wrappers in `app/web/runtime/backtest.py`.
- Added first-pass result/meta readouts:
  - result row:
    - `Universe Membership Count`
    - `Universe Contract`
  - meta:
    - `universe_contract`
    - `dynamic_candidate_count`
    - `dynamic_target_size`
    - `universe_debug`
- Added history/prefill carry-through for `universe_contract` on annual strict single-strategy runs.
- Smoke validation in `.venv` confirmed:
  - annual strict quality / value / quality+value dynamic bundles all return
  - `Universe Membership Count` is written into result rows
  - `universe_debug` is present in bundle meta
- Dynamic preset smoke exposed a contract mismatch and it was corrected:
  - dynamic PIT candidate pools should not fail just because some late listings do not have full-range price history
  - annual strict dynamic preflight now only requires usable DB price history up to the selected end date
  - preset smoke after the fix completed with:
    - `dynamic_candidate_count = 1000`
    - `universe_debug.candidate_pool_count = 921`
    - first `Universe Membership Count = 100`
- Extended the same dynamic contract into annual strict compare mode:
  - compare blocks now expose `Universe Contract`
  - compare runtime passes `universe_contract`, `dynamic_candidate_tickers`, `dynamic_target_size`
  - `Strategy Highlights` now exposes `Universe Contract`, `Dynamic Candidate Pool`, `Membership Avg`, `Membership Range`
- Compare smoke in `.venv` confirmed:
  - annual strict compare override reaches runtime with `historical_dynamic_pit`
  - highlight rows render dynamic membership columns
- Updated:
  - `PHASE10_CURRENT_CHAPTER_TODO.md`
  - `PHASE10_TEST_CHECKLIST.md`
  - `PHASE10_ANNUAL_STRICT_DYNAMIC_PIT_FIRST_PASS.md`
  - `FINANCE_COMPREHENSIVE_ANALYSIS.md`
  - `FINANCE_DOC_INDEX.md`
  - `MASTER_PHASE_ROADMAP.md`

### 2026-03-29 - Phase 10 dynamic PIT second pass hardened

- Continued Phase 10 in the agreed order:
  1. listing / delisting / symbol continuity second pass
  2. dynamic universe snapshot persistence
  3. quarterly family dynamic PIT expansion
  4. perfect constituent-history source reinforcement first pass
- Extended `finance/sample.py` dynamic universe builder to emit continuity diagnostics:
  - `continuity_ready_count`
  - `pre_listing_excluded_count`
  - `post_last_price_excluded_count`
  - `asset_profile_delisted_count`
  - `asset_profile_issue_count`
- Added candidate-level continuity/profile status rows:
  - `first_price_date`
  - `last_price_date`
  - `price_row_count`
  - `profile_status`
  - `profile_delisted_at`
  - `profile_error`
- Added dynamic universe artifact persistence in backtest history:
  - `.note/finance/backtest_artifacts/.../dynamic_universe_snapshot.json`
  - history context now stores `dynamic_universe_artifact` and `dynamic_universe_preview_rows`
- Extended `historical_dynamic_pit` to quarterly strict prototype family:
  - `Quality Snapshot (Strict Quarterly Prototype)`
  - `Value Snapshot (Strict Quarterly Prototype)`
  - `Quality + Value Snapshot (Strict Quarterly Prototype)`
  - both single-strategy and compare first pass now work under the same contract
- Kept the constituent-history source boundary explicit:
  - current contract is still `approximate PIT + diagnostics`
  - asset profile status remains diagnostic only, not a hard membership filter
- `.venv` smoke validation confirmed:
  - annual strict dynamic 3종 모두 정상 bundle 반환
  - quarterly strict dynamic 3종 모두 정상 bundle 반환
  - annual/quarterly compare dynamic override 모두 정상 runtime 연동
  - dynamic history append 후 artifact json path 실존 확인
- Updated:
  - `phase10/PHASE10_CURRENT_CHAPTER_TODO.md`
  - `phase10/PHASE10_TEST_CHECKLIST.md`
  - `phase10/PHASE10_ANNUAL_STRICT_DYNAMIC_PIT_FIRST_PASS.md`
  - `phase10/PHASE10_DYNAMIC_PIT_SECOND_PASS_HARDENING.md`
  - `FINANCE_COMPREHENSIVE_ANALYSIS.md`
  - `FINANCE_DOC_INDEX.md`
  - `MASTER_PHASE_ROADMAP.md`

### 2026-03-30 - Phase 8 checklist refreshed against Phase 9/10 changes

- Reworked `phase8/PHASE8_TEST_CHECKLIST.md` so it matches the current codebase rather than the original Phase 8-only snapshot.
- Kept the core Phase 8 validation target unchanged:
  - quarterly strict prototype family should still work as a research-only single / compare / history surface
- Added later-phase regression expectations now visible on the same UI:
  - quarterly forms now expose `Universe Contract`
  - history/prefill now includes `Universe Contract`
  - coverage guidance is split into coarse `Coverage Gap Status` vs fine `Statement Coverage Diagnosis`
  - operator tooling expectations now include runtime/build, rebuild, run inspector, and standardized guidance behavior
- Added an explicit optional Phase 10 regression item:
  - quarterly `Historical Dynamic PIT Universe` runs should complete without breaking the original quarterly surface

### 2026-03-30 - Phase 8 QA follow-up fixes for history UX and backtest navigation

- Fixed `Persistent Backtest History` recorded-date filtering crash:
  - when the user selected only the start side of `Recorded Date Range`, Streamlit returned a partial date tuple and the history filter compared `datetime.date` against a tuple
  - added `_normalize_recorded_date_range(...)` so partial / single-date inputs normalize safely
- Improved `Load Into Form` UX:
  - loading a history record now switches the Backtest panel to `Single Strategy`
  - the Single Strategy panel now shows a short Korean summary of the loaded inputs:
    - strategy
    - date range
    - preset/manual universe
    - top N
    - universe contract when present
- Simplified the top Backtest header surface:
  - removed the old `Current Direction / Planned First Strategies / Current Phase 4 Status / Next Step` blocks
  - replaced them with a shorter Korean `Backtest 사용 안내` expander
  - clarified `research-only quarterly strict prototype` and `late active start` semantics in Korean

### 2026-03-30 - Phase 9 real-money validation direction doc clarified with glossary

- Expanded `phase9/PHASE9_REAL_MONEY_VALIDATION_DIRECTION.md` with a new terminology section.
- Added practical Korean explanations for:
  - `universe contract`
  - `survivorship`
  - `universe drift`
  - `diagnostics bucket`
  - `eligible / review_needed / excluded`
  - `foreign / non-standard form issuer`
  - `portfolio productization`
- The document now explains these terms as current project contracts rather than leaving them as shorthand.

### 2026-03-31 - Phase 10 QA follow-up: dynamic PIT result semantics and compare reuse

- Added a dedicated `Dynamic Universe` result tab for dynamic PIT runs so `dynamic_universe_snapshot_rows` and `dynamic_candidate_status_rows` are visible directly from a run result instead of only through history artifacts.
- Clarified history drilldown wording for:
  - `dynamic_universe_preview_rows`
  - `dynamic_universe_artifact`
  including what the persisted path fields mean.
- Fixed `universe_builder_scope` in strict quarterly quality dynamic runs so it reflects `quarterly_first_pass` instead of always `annual_first_pass`.
- Added small in-process caches for repeated DB-backed dynamic PIT inputs:
  - price panel build
  - statement factor shadow load
  - statement fundamentals shadow load
  - asset profile status summary
- Goal: reduce repeated compare overhead when annual/quarterly strict strategies share the same candidate pool and date window.

- Fixed Streamlit panel-switch crash in `Load Into Form` by introducing `backtest_requested_panel` and applying panel changes before the radio widget is instantiated.

### 2026-03-31 - Phase 10 practical closeout

- Added `phase10/PHASE10_COMPLETION_SUMMARY.md` and `phase10/PHASE10_NEXT_PHASE_PREPARATION.md`.
- Marked Phase 10 as practical closeout in roadmap/TODO/index.
- Synced comprehensive analysis to reflect current dynamic PIT result surface (`Dynamic Universe` tab, history artifact semantics, small compare caches).
- Clarified next direction: Phase 11 remains the next natural product/workflow phase after dynamic PIT validation contract hardening.

### 2026-03-31 - Phase 11 first pass: saved portfolio workflow opened

- Opened Phase 11 as the active productization/workflow phase after Phase 10 practical closeout.
- Added a dedicated saved-portfolio store:
  - `.note/finance/SAVED_PORTFOLIOS.jsonl`
  - `app/web/runtime/portfolio_store.py`
- Added `Saved Portfolios` workspace to `Backtest > Compare & Portfolio Builder`.
- Implemented first-pass workflow:
  - save current weighted portfolio
  - inspect saved portfolios
  - `Load Into Compare`
  - `Run Saved Portfolio`
  - `Delete`
- Added compare prefill + deferred weight/date-policy prefill so saved portfolios can be brought back into the compare screen without manual re-entry.
- Added weighted portfolio `Meta` tab and saved-portfolio context linkage in history.
- Synced Phase 11 roadmap/TODO/checklist/docs to reflect that Phase 11 is now `in_progress`.

### 2026-03-31 - Added Playwright-based public market research playbook

- Added `.note/finance/PLAYWRIGHT_MARKET_RESEARCH_PLAYBOOK_20260331.md`.
- Organized institution-themed market-research requests into public-source workflows for:
  - screening
  - DCF valuation
  - earnings analysis
  - portfolio construction
  - technical analysis
  - dividend/income strategy
  - competitor analysis
  - pattern detection
  - macro impact assessment
- Fixed the playbook around a shared three-stage process:
  - source mapping / collection
  - structured parsing / normalization
  - synthesis / decision memo
- Synced the new research note into `FINANCE_DOC_INDEX.md`.
- Appended durable analysis context to `QUESTION_AND_ANALYSIS_LOG.md`.

### 2026-04-01 - Strengthened the Playwright research playbook for repeated use

- Expanded `.note/finance/PLAYWRIGHT_MARKET_RESEARCH_PLAYBOOK_20260331.md` beyond the original lightweight three-step flow.
- Added a repeatable five-stage operating model with:
  - research brief / decision contract
  - source mapping
  - structured parsing
  - synthesis
  - validation / contradiction review / refresh planning
- Added cross-cutting guidance for:
  - point-in-time and filing acceptance timing
  - ticker vs CIK/accession identity handling
  - macro vintage / revision management
  - official-source precedence
  - API-first collection and Playwright evidence capture
  - fair-access / rate-limit compliance
  - trace/download preservation
  - refresh-policy management
- Updated the finance document index description and appended the durable analysis result.

### 2026-04-04 - Added a US public portfolio/strategy source map for discovery-stage research

- Added `.note/finance/US_PUBLIC_PORTFOLIO_AND_STRATEGY_SOURCE_MAP_20260404.md`.
- Organized the discovery layer for finding public portfolios and disclosed strategies of notable US institutions, funds, and investors.
- Fixed the core source stack around:
  - SEC 13F
  - SEC 13D / 13G
  - SEC N-PORT
  - official annual reports / investor letters / product holdings pages / methodology pages
- Added representative official examples for Berkshire, Pershing, Bridgewater, Third Point, Icahn, Renaissance, BlackRock/iShares, ARK, and Harvard Management Company.
- Synced the new source map into `FINANCE_DOC_INDEX.md`.
- Appended the durable discovery-model summary to `QUESTION_AND_ANALYSIS_LOG.md`.

### 2026-04-01 - Phase 11 practical closeout and Phase 12 kickoff

- Recorded Phase 11 as first-pass practical closeout after saved-portfolio workflow validation.
- Added:
  - `phase11/PHASE11_COMPLETION_SUMMARY.md`
  - `phase11/PHASE11_NEXT_PHASE_PREPARATION.md`
- Opened Phase 12 as the new active phase for real-money strategy promotion.
- Added Phase 12 planning/execution docs:
  - `phase12/PHASE12_REAL_MONEY_STRATEGY_PROMOTION_PLAN.md`
  - `phase12/PHASE12_CURRENT_CHAPTER_TODO.md`
  - `phase12/PHASE12_STRATEGY_PRODUCTION_AUDIT_MATRIX.md`
  - `phase12/PHASE12_REAL_MONEY_PROMOTION_CONTRACT.md`
  - `phase12/PHASE12_TEST_CHECKLIST.md`
- Fixed the next implementation order around:
  - ETF strategy hardening first
  - strict annual family promotion second
  - quarterly strict prototype family hold
- Synced roadmap, document index, and Phase 11/12 phase boards to reflect that Phase 12 is now the active direction.
- No finance code paths were changed in this step; this was a phase-management and real-money strategy planning update.

### 2026-04-01 - Clarified the real-money promotion contract wording for Phase 12

- Expanded `phase12/PHASE12_REAL_MONEY_PROMOTION_CONTRACT.md` so the `공통 계약 축` section is easier to read.
- Added plain-language explanations for:
  - `Universe / Data Contract`
  - `Investability Filter`
  - `Turnover / Transaction Cost`
  - `Portfolio Guardrail`
  - `Validation Surface`
- Added “why this matters” guidance for each axis so the document reads as an operator/decision aid rather than only as compressed policy language.
- No code paths changed; this was a documentation clarification update for Phase 12 kickoff.

### 2026-04-01 - Added a durable documentation-writing rule for future phase docs

- Updated `AGENTS.md` so future phase/policy/real-money guidance documents should include plain-language explanations for important concepts instead of leaving them as compressed jargon only.
- Added a preferred structure:
  - what this means
  - why it matters
- Goal: keep future finance phase documents understandable on first pass without losing technical precision.

### 2026-04-01 - Clarified the Phase 12 strategy promotion plan wording in plain language

- Expanded `phase12/PHASE12_REAL_MONEY_STRATEGY_PROMOTION_PLAN.md` with easier explanations for:
  - the overall phase goal
  - strategy classification buckets
  - promotion / hardening / audit terminology
  - chapter-by-chapter intent
  - why ETF-first / annual-next / quarterly-hold is the recommended order
- Goal: make the plan read as a practical guide, not only as compressed policy shorthand.

### 2026-04-01 - Added a terminology section to the Phase 12 strategy promotion plan

- Expanded `phase12/PHASE12_REAL_MONEY_STRATEGY_PROMOTION_PLAN.md` with a dedicated glossary-style section.
- Added short definitions for recurring planning terms such as:
  - `prototype`
  - `research-only`
  - `public-candidate`
  - `production-grade`
  - `promotion`
  - `hardening`
  - `candidate`
  - `strategy family`
  - `baseline`
  - `universe semantics`
  - `dynamic PIT`
  - `hold`
  - `checklist`
- Goal: make the Phase 12 plan self-explanatory without requiring extra chat interpretation of each planning term.

### 2026-04-01 - Added a glossary for the Phase 12 real-money promotion contract

- Expanded `phase12/PHASE12_REAL_MONEY_PROMOTION_CONTRACT.md` with a dedicated terminology section.
- Added short definitions for recurring terms such as:
  - `contract`
  - `universe`
  - `managed static research universe`
  - `historical dynamic PIT universe`
  - `look-ahead bias`
  - `survivorship bias`
  - `investability`
  - `turnover`
  - `slippage`
  - `portfolio guardrail`
  - `production candidate`
  - `real-money candidate`
- Goal: let the user/operator read the common promotion contract without needing extra chat clarification for each term.

### 2026-04-01 - Phase 12 ETF real-money hardening first pass

- Implemented Phase 12 ETF hardening first pass across:
  - `finance/strategy.py`
  - `finance/sample.py`
  - `app/web/runtime/backtest.py`
  - `app/web/runtime/history.py`
  - `app/web/pages/backtest.py`
- Added common ETF real-money inputs:
  - `Minimum Price`
  - `Transaction Cost (bps)`
  - `Benchmark Ticker`
- Added missing single-strategy knobs so ETF forms are closer to compare parity:
  - `Risk Parity Trend`: rebalance interval, vol window
  - `Dual Momentum`: top assets, rebalance interval
- Added strategy-level `min_price` investability filter to:
  - `GTAA`
  - `Risk Parity Trend`
  - `Dual Momentum`
- Added runtime post-process for ETF strategies:
  - `Gross Total Balance`
  - `Gross Total Return`
  - `Turnover`
  - `Estimated Cost`
  - `Cumulative Estimated Cost`
  - `Net Total Balance`
  - `Net Total Return`
- Added benchmark overlay first pass:
  - `benchmark_chart_df`
  - `benchmark_summary_df`
  - benchmark availability / end-balance / excess-balance meta
- Added single-strategy `Real-Money` tab and compare-level real-money readout.
- Synced history/prefill/saved-portfolio compare context so:
  - `min_price_filter`
  - `transaction_cost_bps`
  - `benchmark_ticker`
  round-trip through `Load Into Form`, `Run Again`, and compare overrides.
- Verified compile and DB-backed smoke:
  - `GTAA`
  - `Risk Parity Trend`
  - `Dual Momentum`
  - compare override path
  - history payload path

### 2026-04-01 - Clarified Phase 12 ETF result-table metric meaning and strict-annual checklist scope

- Added a plain-language interpretation block to `phase12/PHASE12_ETF_REAL_MONEY_HARDENING_FIRST_PASS.md` for:
  - `Turnover`
  - `Gross Total Balance`
  - `Total Balance`
  - `Estimated Cost`
  - `Cumulative Estimated Cost`
- Updated `phase12/PHASE12_TEST_CHECKLIST.md` so `Strict Annual Family Promotion Surface` is explicitly marked as a later target, not an already-implemented expectation in the ETF-first pass.

### 2026-04-01 - Added a shared finance term glossary

- Added `.note/finance/FINANCE_TERM_GLOSSARY.md` as a cross-phase glossary for recurring quant / backtest / real-money terminology.
- Seeded the glossary with current recurring terms such as:
  - `Universe Contract`
  - `Historical Dynamic PIT Universe`
  - `Turnover`
  - `Transaction Cost`
  - `Benchmark`
  - `Portfolio Guardrail`
- Updated `AGENTS.md` so future recurring terms should be added to the glossary using:
  - `기본 설명`
  - `왜 사용되는지`
  - `예시 / 필요 상황`
- Updated `FINANCE_DOC_INDEX.md` so the glossary is part of the durable finance documentation set.

### 2026-04-02 - Swapped the default GTAA commodity sleeve from DBC to PDBC

- Updated the current GTAA default universe to use `PDBC` instead of `DBC`.
- Synced the change across:
  - `app/web/pages/backtest.py`
  - `finance/sample.py`
- Kept the change at the default/preset layer so:
  - GTAA preset execution
  - compare defaults
  - manual default ticker input
  - sample entrypoints
  all point to the same current baseline universe.
- Updated Phase 12 and finance analysis docs so the current GTAA default universe change is explicit.

### 2026-04-02 - Added a DBC comparison preset for GTAA

- Kept `GTAA Universe` as the current default preset using `PDBC`.
- Added `GTAA Universe (DBC)` as an alternate preset so the user can compare `PDBC` vs `DBC` without switching to manual ticker entry.
- Added small UI captions clarifying which preset uses `PDBC` and which one uses `DBC`.
- Updated the Phase 12 ETF hardening note so the alternate DBC preset is documented.

### 2026-04-02 - Added a no-commodity GTAA comparison preset

- Added `GTAA Universe (No Commodity Sleeve)` so the user can compare GTAA with both `PDBC` and `DBC` removed from the universe.
- Added a UI caption clarifying that this preset excludes both commodity sleeve tickers.
- Updated the Phase 12 ETF hardening note so the third GTAA preset is documented.

### 2026-04-02 - Analyzed GTAA DBC vs PDBC vs no-commodity sleeve behavior

- Ran DB-backed GTAA comparisons for:
  - `PDBC`
  - `DBC`
  - `No Commodity Sleeve`
- Confirmed that `DBC` and `PDBC` are highly similar at the standalone ETF level, but GTAA amplifies small differences because it uses:
  - top-3 ranking
  - `MA200` trend filter
  - cash fallback
  - interval-based rebalance anchoring
- Identified a major structural driver in the current default-like comparison:
  - with `Signal Interval = 2`, `PDBC` starts later, so the usable start date and the entire every-other-month rebalance cadence shift
- Verified that even after normalizing to a common start date, `DBC` still outperformed:
  - `PDBC`
  - `No Commodity Sleeve`
- Added a dedicated Phase 12 analysis note with:
  - root-cause breakdown
  - result tables
  - practical interpretation
  - alternative commodity ETF candidates and official source links

### 2026-04-02 - Backfilled and tested GTAA commodity alternative candidates

- Backfilled targeted daily price history for:
  - `CMDY`
  - `BCI`
  - `COMT`
- Confirmed DB coverage after backfill and then ran GTAA comparisons across:
  - `DBC`
  - `PDBC`
  - `CMDY`
  - `BCI`
  - `COMT`
  - `No Commodity Sleeve`
- Compared both:
  - current-contract runs
  - common-start normalized runs
- Found that:
  - `DBC` remains the strongest sleeve in current GTAA tests
  - among K-1-free alternatives, `COMT` and `CMDY` are the most plausible next candidates
  - however, both still lagged `No Commodity Sleeve` in the normalized comparison
- Added a dedicated candidate-analysis note with:
  - official ETF information
  - DB backfill status
  - `CAGR` / `MDD` comparison tables
  - practical recommendation ordering

### 2026-04-02 - Ran a 10-configuration GTAA interval-1 universe variation search

- Fixed the GTAA search contract to:
  - `Signal Interval = 1`
  - `month_end`
  - `top = 3`
  - `Minimum Price = 5`
  - `Transaction Cost = 10 bps`
- Backfilled additional ETF history for:
  - `TIP`
  - `QUAL`
  - `USMV`
  - `VEA`
- Tested 10 GTAA universe variants including:
  - current `PDBC`
  - `DBC`
  - no commodity
  - `DBC` plus `TIP`
  - `DBC` plus `QUAL`
  - `DBC` plus `USMV`
  - `DBC` plus `VEA`
  - multi-add variants
- Found the most promising real-money improvement directions were:
  - `DBC + USMV`
  - `DBC + QUAL + USMV`
- Confirmed that:
  - `USMV` improved both `CAGR` and `MDD` relative to `DBC` base
  - `QUAL` alone helped `CAGR` but worsened `MDD`
  - `TIP` was selected rarely and is not currently a strong GTAA improvement lever
- Added a dedicated search note summarizing:
  - all 10 backtests
  - candidate rationale
  - result ranking
  - practical GTAA modification guidance

### 2026-04-02 - Ran a no-DBC GTAA interval-1 variation search

- Built a second 10-run GTAA search where `DBC` was fully excluded.
- Tested practical no-DBC families built around:
  - `PDBC`
  - `COMT`
  - `CMDY`
  - `BCI`
  - `No Commodity`
  plus:
  - `QUAL`
  - `USMV`
- Compared both:
  - current full-history runs
  - common-start `2020-01-31` normalized runs
- Found the strongest no-DBC candidates were:
  - `No Commodity + QUAL + USMV`
  - `COMT + QUAL + USMV`
- Confirmed that in the no-DBC setting:
  - `QUAL + USMV` additions mattered more than picking a different commodity sleeve
  - `PDBC` remained weak even after additive tweaks
- Added a dedicated note summarizing the 10-run no-DBC comparison and practical recommendation ordering.

### 2026-04-02 - Added recommended no-DBC GTAA presets based on the search results

- Added two GTAA comparison presets to the Backtest UI:
  - `GTAA Universe (COMT + QUAL + USMV)`
  - `GTAA Universe (No Commodity + QUAL + USMV)`
- These were chosen from the no-DBC interval-1 search as the most practical next-step presets to test:
  - keep commodity via `COMT` while adding `QUAL` and `USMV`
  - remove commodity entirely while adding `QUAL` and `USMV`
- Kept the current default preset unchanged:
  - `GTAA Universe` still uses `PDBC`

### 2026-04-04 - Daily Market Update short-window acceleration implemented

- Investigated why `Daily Market Update` on `Profile Filtered Stocks + ETFs` still took about `2,384 sec` even for a short refresh.
- Confirmed from the latest broad managed run that the bottleneck was almost entirely provider fetch time:
  - `fetch_sec = 2367.96`
  - `delete_sec = 2.663`
  - `upsert_sec = 2.758`
  - `batch_count = 178`
  - `rate_limited_symbols = 0`
- Concluded that `1d` and `20y` felt similarly slow because wall time was dominated by batch fetch overhead, not rows written.
- Added a new OHLCV execution profile:
  - `managed_refresh_short`
- Routed short-window daily managed refreshes to that profile:
  - managed source
  - `interval = 1d`
  - `period = 1d`
  - or explicit date span roughly `10` days or shorter
- Kept long historical fetches and raw broad sweeps on their previous profiles so earlier rate-limit stabilization is preserved.
- Tuned the new profile from measured local comparison on the same managed-symbol sample:
  - `managed_fast` baseline on `240` symbols: `40.221 sec`
  - `60x2` trial: `36.365 sec`
  - `70x2` trial: `23.886 sec`
  - adopted `chunk_size = 70`, `max_workers = 2`, `sleep = 0.01`
- Added a dedicated implementation note:
  - `.note/finance/DAILY_MARKET_UPDATE_SHORT_WINDOW_ACCELERATION_20260404.md`

### 2026-04-04 - Fixed GTAA preset refresh UX and ran a DB-backed ETF group search under the current contract

- Fixed a GTAA Backtest UX issue where changing the preset did not immediately refresh the `Selected tickers` preview.
- Moved the GTAA universe-mode / preset / manual-ticker controls outside the submit form so preset changes rerender immediately.
- Backfilled additional ETF histories needed for a broader GTAA search:
  - `XLP`, `XLU`, `XLV`, `XLE`, `SHY`, `AGG`, `HYG`, `IAU`, `VEU`, `VWO`, `EWJ`, `VUG`, `VTV`, `RSP`, `ACWV`, `VGK`
- Ran an 18-group DB-backed GTAA search under the current default-style contract:
  - `start = 2016-01-01`
  - `end = 2026-04-02`
  - `top = 3`
  - `signal interval = 2`
  - `month_end`
  - `min_price = 5`
  - `transaction_cost = 10 bps`
- Used theme-based ETF groups rather than random combinations:
  - growth leadership
  - quality / low-volatility
  - defensive sectors
  - bond-menu expansion
  - alternative / inflation / cyclicality
- Confirmed that the strongest additive direction in the current GTAA contract is centered on:
  - `QQQ`
  - `IAU`
  - `XLE`
- Best current result from the focused follow-up:
  - `Base + QQQ + QUAL + USMV + XLE + IAU`
  - `CAGR = 11.50%`
  - `MDD = -16.69%`
  - `Sharpe = 1.184`
- Simpler runner-up:
  - `Base + QQQ + XLE + IAU + TIP`
  - `CAGR = 11.02%`
  - `MDD = -16.69%`
  - `TIP` looked largely redundant in actual selection counts
- Observed that:
  - extra bond menu expansion (`AGG`, `HYG`, `SHY`, `TIP`) added little because the base universe already carries strong bond sleeves
  - defensive-sector-only additions (`XLP`, `XLU`, `XLV`) hurt CAGR more than they helped drawdown
  - `QUAL` and `USMV` work better as supporting broadeners than as the primary engine
- Saved the full study as:
  - `.note/finance/phase12/PHASE12_GTAA_DB_ETF_GROUP_SEARCH.md`

### 2026-04-04 - Rebased GTAA default signal interval to 1 and reran the main candidates under the new default

- Changed the GTAA default signal interval from `2` to `1` across:
  - single-strategy default input
  - compare default input
  - history / `Load Into Form` fallback
  - saved-portfolio compare override fallback
  - runtime/sample helper defaults
- Kept explicit historical payload values intact; only missing-value fallbacks were rebased.
- Ran a normalized interval-1 comparison on the main GTAA candidates using a common start date (`2016-08-31`) so `PDBC`-based and non-`PDBC` universes are compared more fairly.
- Interval-1 results still favored the same broad direction:
  - `Base + QQQ + QUAL + USMV + XLE + IAU`
    - `CAGR = 11.41%`
    - `MDD = -21.96%`
  - `Base + QQQ + XLE + IAU + TIP`
    - `CAGR = 10.08%`
    - `MDD = -21.60%`
- Among already-exposed UI presets, the strongest interval-1 choices were:
  - `GTAA Universe (No Commodity + QUAL + USMV)` for higher CAGR
  - `GTAA Universe (DBC)` for slightly lower MDD
- Confirmed that rebasing interval to `1` does not by itself fix the relative weakness of the current default `PDBC` preset.
- Saved the rerun note as:
  - `.note/finance/phase12/PHASE12_GTAA_INTERVAL1_DEFAULT_REBASE_ANALYSIS.md`

### 2026-04-04 - Simplified GTAA preset surface to the default plus the current top three candidates

- Removed older comparison/experiment presets from the GTAA preset list so the UI no longer presents every historical search branch.
- Kept only:
  - `GTAA Universe`
  - `GTAA Universe (No Commodity + QUAL + USMV)`
  - `GTAA Universe (QQQ + XLE + IAU + TIP)`
  - `GTAA Universe (QQQ + QUAL + USMV + XLE + IAU)`
- This keeps the default benchmark universe available while also surfacing the three strongest Phase 12 candidate directions without forcing manual ticker edits.

### 2026-04-04 - Added GTAA score-weight controls and a first-pass configurable risk-off contract

- Extended GTAA so the score blend is no longer fixed to a hardcoded equal average of `1M / 3M / 6M / 12M`.
- Added user-facing score-weight inputs for:
  - `1M Weight`
  - `3M Weight`
  - `6M Weight`
  - `12M Weight`
- Added a first-pass GTAA risk-off contract surface:
  - `Trend Filter Window`
  - `Fallback Mode` (`Cash Only` vs `Defensive Bond Preference`)
  - `Defensive Tickers`
  - `Market Regime Overlay`
  - `Crash Guardrail`
- Implemented weighted score computation in `finance.transform.add_avg_score(...)`.
- Reworked GTAA sample/runtime path so GTAA can now run with:
  - custom score weights
  - custom trend filter window
  - defensive bond fallback
  - benchmark-based market regime gating
  - benchmark drawdown-based crash guardrail
- Extended GTAA history/prefill/save/compare flow so the new contract values round-trip instead of getting lost after execution.
- Added result/debug columns so GTAA runs can now show:
  - `Defensive Fallback Count`
  - `Regime State`
  - `Crash Guardrail Triggered`
  - `Risk-Off Reason`
- Saved the implementation note as:
  - `.note/finance/phase12/PHASE12_GTAA_SCORE_WEIGHT_AND_RISK_OFF_FIRST_PASS.md`

### 2026-04-04 - Expanded GTAA score controls from fixed 1/3/6/12 weights to editable month-horizon rows

- The first GTAA score UI only allowed changing the weights of a fixed `1M / 3M / 6M / 12M` blend.
- Reworked it into a row-based score editor:
  - default rows: `1M`, `3M`, `6M`, `12M`
  - user can remove rows
  - user can add new month horizons such as `9M`
  - duplicate month rows are blocked
- Kept the default behavior unchanged:
  - initial rows are still `1M / 3M / 6M / 12M`
  - initial weights are all `1`
- Wired the new `score_lookback_months` / derived `score_return_columns` contract through:
  - single GTAA form
  - compare GTAA override block
  - runtime meta/history
  - history `Load Into Form`
  - saved override prefill
- Verified with a DB-backed GTAA smoke run that custom rows like:
  - `1M, 3M, 9M`
  correctly reach runtime/meta as:
  - `score_lookback_months=[1,3,9]`
  - `score_return_columns=['1MReturn','3MReturn','9MReturn']`

### 2026-04-04 - Simplified GTAA score UI back down to equal-weight horizon selection

- The row-based add/remove editor worked functionally, but it made the GTAA UI heavier than the user wanted.
- Simplified the GTAA score surface back to a cleaner selector:
  - fixed selectable horizons: `1M / 3M / 6M / 12M`
  - no visible weight inputs
  - all selected horizons are treated equally
- Kept the default behavior as:
  - `1M / 3M / 6M / 12M` all selected
  - equal weighting across the selected horizons
- Reintegrated the score selector into the GTAA form / compare expander so the UI flow feels like the previous version again.
- Adjusted runtime metadata so `score_weights` now matches the selected horizons instead of retaining the old full default dict when fewer horizons are chosen.

### 2026-04-04 - Ran a GTAA vs SPY dominance search and documented that no tested Phase 12 configuration beat SPY on both CAGR and MDD

- Defined the practical test as:
  - `GTAA` candidate CAGR must be strictly higher than `SPY`
  - `GTAA` candidate MDD must be less negative than `SPY`
- Rebased the comparison to a common start point:
  - `2016-08-31`
- Measured the `SPY` baseline:
  - `CAGR 12.21%`
  - `MDD -24.80%`
- Ran two search passes:
  - base GTAA dominance search across universe / horizon / risk-off combinations
  - overlay-extended dominance search with `Regime`, `Crash`, `Regime + Crash`
- Result:
  - no tested Phase 12 GTAA configuration dominated `SPY` on both axes
- Closest offensive candidate:
  - `GTAA Universe (QQQ + XLE + IAU + TIP)` or `GTAA Universe (QQQ + XLE + IAU)`
  - `Score Horizons = 1/3/6`
  - `CAGR 11.90%`
  - `MDD -20.03%`
- Strongest defensive candidate:
  - `GTAA Universe (No Commodity + QUAL + USMV)`
  - `CAGR 8.96%`
  - `MDD -16.17%`
- Saved the durable note as:
  - `.note/finance/phase12/PHASE12_GTAA_VS_SPY_DOMINANCE_SEARCH.md`

### 2026-04-04 - Found a GTAA candidate that meets the practical CAGR 9 / MDD 16 floor

- Expanded the GTAA search to broader manual universes and tightened the contract around a more favorable cadence.
- Best practical-floor candidate:
  - universe: `QQQ|VUG|RSP|VTV|QUAL|USMV|XLE|IAU|TIP|TLT|LQD|ACWV|SPY`
  - `top=2`
  - `interval=2`
  - `Score Horizons = 1/3`
  - `risk-off = cash_only`
- Result:
  - `CAGR 12.90%`
  - `MDD -11.10%`
- Saved the durable note as:
  - `.note/finance/phase12/PHASE12_GTAA_CAGR9_MDD16_TARGET_SEARCH.md`

### 2026-04-04 - Expanded the GTAA practical-floor search with cadence follow-up and found stronger target hits

- Extended the search to:
  - 6 universe groups
  - `top=2/3/4`
  - score horizons `1/3`, `1/3/6`, `1/3/6/12`
  - `cash_only` and `defensive_bond_preference`
  - `interval=1` first pass
  - `interval=2/3` on the strongest universe groups
- Total search size:
  - `180` DB-backed backtests
- Result:
  - `88` target hits satisfying:
    - `CAGR >= 9%`
    - `MDD >= -16%`
- Best offensive candidate:
  - `U3_commodity`
  - `interval=3`
  - `top=2`
  - `horizons=1/3/6`
  - `CAGR 16.66%`
  - `MDD -11.29%`
- Best balanced candidate:
  - `U1_offensive`
  - `interval=3`
  - `top=2`
  - `horizons=1/3/6/12`
  - `CAGR 16.25%`
  - `MDD -10.59%`
- Best defensive candidate:
  - `U5_smallcap_value`
  - `interval=3`
  - `top=3`
  - `horizons=1/3/6/12`
  - `CAGR 12.04%`
  - `MDD -9.79%`
- Saved the durable note as:
  - `.note/finance/phase12/PHASE12_GTAA_CAGR9_MDD16_TARGET_SEARCH.md`

### 2026-04-04 - Added verified GTAA candidate-base presets to the UI

- Added three GTAA universe presets backed by the verified practical-floor search:
  - `GTAA Universe (U3 Commodity Candidate Base)`
  - `GTAA Universe (U1 Offensive Candidate Base)`
  - `GTAA Universe (U5 Smallcap Value Candidate Base)`
- Added captions that show the best validated contract for each preset base:
  - recommended `top`
  - recommended `interval = 3`
  - recommended `Score Horizons`
- Kept the existing default and earlier comparison presets intact.

### 2026-04-04 - Extended GTAA universe selection into compare mode and added a real-money candidate decision table

- Added the GTAA `Preset` / `Manual` universe selector to `Compare & Portfolio Builder`.
- Kept the selector outside the compare submit form so preset changes refresh the ticker preview immediately.
- Wired the compare GTAA universe contract through:
  - compare execution
  - history/saved-portfolio prefill
  - saved strategy override restoration
- Expanded `.note/finance/phase12/PHASE12_GTAA_CAGR9_MDD16_TARGET_SEARCH.md` with a candidate decision table:
  - offensive
  - balanced
  - defensive

### 2026-04-04 - Equal Weight compare mode now exposes the same universe contract as single mode

- Added `Equal Weight Universe` selection to `Compare & Portfolio Builder`.
- Compare now supports:
  - `Preset` / `Manual`
  - compare execution using the selected equal-weight ticker set
  - prefill / saved-portfolio restoration of equal-weight universe choice

### 2026-04-04 - Compare strategy option surface is now opened by default so preset-only confusion is reduced

- `Compare & Portfolio Builder` had a confusing structure where universe preset selectors were visible first, but the actual per-strategy execution controls were hidden inside collapsed nested expanders.
- Changed compare UI so:
  - the outer `Advanced Inputs` block opens by default
  - selected strategy blocks such as `Equal Weight` and `GTAA` also open by default
  - a short caption now clarifies that preset/universe selection and strategy execution options are separate layers

### 2026-04-04 - Compare universe selectors were moved back under strategy-specific advanced inputs for a more regular layout

- Moved `Equal Weight Universe` and `GTAA Universe` into:
  - `Advanced Inputs`
  - `Strategy-Specific Advanced Inputs`
  - each strategy's own block
- This keeps compare strategy configuration in one place instead of splitting:
  - universe/preset selection
  - strategy execution options
  across different sections.
- The layout is now more regular, but universe preview follows form semantics again because those selectors now live inside the compare form.

### 2026-04-04 - Strict annual family real-money hardening first pass was implemented

- Resumed Phase 12 after pausing GTAA-specific exploration and moved the next active implementation target back to `Strict Annual Family`.
- Added first-pass real-money inputs to:
  - `Quality Snapshot (Strict Annual)`
  - `Value Snapshot (Strict Annual)`
  - `Quality + Value Snapshot (Strict Annual)`
- Added the same contract to compare overrides:
  - `Minimum Price`
  - `Transaction Cost (bps)`
  - `Benchmark Ticker`
- Extended annual strict runtime so the same hardening contract now applies:
  - candidate-level `min_price` filter
  - turnover / gross-vs-net postprocess
  - benchmark overlay
- Connected history / `Load Into Form` / compare prefill restoration for annual strict real-money fields.
- Added Phase 12 documentation and checklist sync for the new annual strict first pass.

### 2026-04-04 - Shared real-money validation surface second pass was added for annual strict review

- Extended the shared real-money runtime helper so benchmark-backed runs now also compute:
  - benchmark-relative drawdown diagnostics
  - rolling underperformance diagnostics
  - `validation_status = normal / watch / caution`
- Exposed the new validation surface in:
  - single-strategy `Real-Money` tab
  - compare `Strategy Highlights`
  - focused strategy `Real-Money Contract`
  - `Execution Context`
- This was driven by the strict annual next-step goal, but the helper is shared so ETF strategies also inherit the same validation surface.
- The current scope is still read-only diagnostics; it does not yet convert underperformance into automatic strategy guardrails.

### 2026-04-05 - Promotion decision surface was wired into the strict annual second-pass UI

- Shared real-money runtime was already computing:
  - `promotion_decision`
  - `promotion_rationale`
  - `promotion_next_step`
- Completed the remaining UI integration so these values now show up in:
  - single-strategy `Real-Money` tab
  - compare `Strategy Highlights`
  - `Execution Context`
- Kept this as a review surface, not a hard trading rule:
  - `real_money_candidate`
  - `production_candidate`
  - `hold`
  should currently be read as promotion guidance, not automatic portfolio behavior.

### 2026-04-05 - Strict annual underperformance guardrail first pass was wired as an optional actual strategy rule

- Added an optional benchmark-relative trailing excess return guardrail to:
  - `Quality Snapshot (Strict Annual)`
  - `Value Snapshot (Strict Annual)`
  - `Quality + Value Snapshot (Strict Annual)`
- Added new annual strict inputs in single and compare:
  - `Underperformance Guardrail`
  - `Guardrail Window (Months)`
  - `Worst Excess Threshold (%)`
- Extended strict annual runtime and strategy paths so that when the guardrail is enabled:
  - trailing strategy excess return vs benchmark is tracked
  - rebalance dates that breach the threshold move to cash
  - trigger/state/count diagnostics are exposed in result rows and real-money surfaces
- Synced history/prefill/meta so the same guardrail contract survives:
  - `Load Into Form`
  - compare prefill
  - execution context
- Added AGENTS guidance that finished implementation units should be committed in coherent groups with descriptive commit logs.

### 2026-04-05 - Strict annual minimum-history filter and richer benchmark surface were added

- Extended the strict annual family (`Quality`, `Value`, `Quality+Value`) with a stronger first-pass investability proxy:
  - `Minimum History (Months)`
- The new filter now travels through:
  - single-strategy form
  - compare override
  - runtime bundle meta
  - history / `Load Into Form`
- Strategy/runtime behavior now also exposes richer benchmark-relative metrics:
  - `Benchmark CAGR`
  - `Net CAGR Spread`
  - `Benchmark Coverage`
- Result rows now preserve history-specific diagnostics:
  - `Minimum History Months`
  - `History Excluded Count`
- Added a dedicated Phase 12 implementation note and refreshed:
  - current TODO board
  - Phase 12 checklist
  - comprehensive analysis
  - doc index

### 2026-04-05 - Refreshed finance work-log operating guidance

- Reviewed whether `.note/finance/WORK_PROGRESS.md` should keep growing as a single file or be split.
- Chosen direction:
  - keep the root `WORK_PROGRESS.md` as the canonical active log
  - do not split by month
  - when detail volume grows, archive by phase instead
- Added repo guidance so future turns follow:
  - root summary log + phase-specific detailed worklog/archive
- Added commit-language guidance:
  - future commit descriptions for this repository should prefer Korean unless explicitly requested otherwise
- Added a new reference note:
  - `.note/finance/FINANCE_WORK_PROGRESS_POLICY.md`

### 2026-04-05 - Strict annual liquidity proxy first pass was added

- Extended the strict annual family (`Quality`, `Value`, `Quality+Value`) with a later-pass investability filter:
  - `Min Avg Dollar Volume 20D ($M)`
- Implementation detail:
  - uses DB daily `close * volume`
  - computes trailing 20-day average dollar volume before each rebalance
  - excludes candidates that fall below the configured threshold
- The new contract now travels through:
  - single-strategy form
  - compare override
  - runtime metadata
  - result rows / real-money tab
  - history / `Load Into Form`
- Added new result diagnostics:
  - `Minimum Avg Dollar Volume 20D ($M)`
  - `Liquidity Excluded Ticker`
  - `Liquidity Excluded Count`
- Added a dedicated Phase 12 implementation note and refreshed:
  - current TODO board
  - Phase 12 checklist
  - comprehensive analysis
  - doc index

### 2026-04-05 - Strict annual benchmark policy / promotion reinforcement later pass was added

- Extended the strict annual family (`Quality`, `Value`, `Quality+Value`) with two promotion-policy inputs:
  - `Min Benchmark Coverage (%)`
  - `Min Net CAGR Spread (%)`
- Added benchmark-policy evaluation to the shared real-money helper:
  - `benchmark_policy_status = normal / watch / caution / unavailable`
  - `benchmark_policy_watch_signals`
  - coverage/spread pass flags
- Promotion decision now considers benchmark policy together with:
  - validation status
  - universe contract
  - price freshness
- The new contract now travels through:
  - single-strategy form
  - compare override
  - runtime metadata
  - real-money tab
  - execution context
  - history / `Load Into Form`
- Added a dedicated Phase 12 implementation note and refreshed:
  - current TODO board
  - Phase 12 checklist
  - comprehensive analysis
  - doc index

### 2026-04-05 - Strict annual liquidity policy / later-pass investability reinforcement was added

- Extended the strict annual family (`Quality`, `Value`, `Quality+Value`) with:
  - `Min Liquidity Clean Coverage (%)`
- The shared real-money helper now evaluates:
  - `liquidity_rebalance_rows`
  - `liquidity_excluded_active_rows`
  - `liquidity_clean_coverage`
  - `liquidity_policy_status = normal / watch / caution / unavailable`
- Promotion decision now considers liquidity policy together with:
  - benchmark policy
  - validation status
  - universe contract
  - price freshness
- The new contract now travels through:
  - single-strategy form
  - compare override
  - runtime metadata
  - real-money tab
  - execution context
  - history / `Load Into Form`
- Added a dedicated Phase 12 implementation note and refreshed:
  - current TODO board
  - Phase 12 checklist
  - comprehensive analysis
  - doc index
  - glossary

### 2026-04-05 - Backtest strategy surface was consolidated around strategy families

- Reviewed the current ownership boundary for quality/value strategies and kept the runtime layers unchanged:
  - `finance/strategy.py` remains the simulation / decision layer
  - `finance/sample.py` remains the DB-backed factor / snapshot assembly layer
  - `app/web/runtime/backtest.py` remains the runtime wrapper / bundle layer
- Added a new surface-level catalog module:
  - `app/web/pages/backtest_strategy_catalog.py`
- Simplified the user-facing top-level strategy list in both `Single Strategy` and `Compare & Portfolio Builder` to:
  - `Quality`
  - `Value`
  - `Quality + Value`
- Moved family / variant / concrete strategy-key mapping into the catalog module and kept concrete runtime keys stable for:
  - history
  - `Load Into Form`
  - compare prefill
- Added a dedicated Phase 12 implementation note and refreshed:
  - current TODO board
  - Phase 12 checklist
  - comprehensive analysis
  - doc index

### 2026-04-05 - Reviewed next-step architecture direction for `backtest.py` and strategy ownership

- Checked current file sizes:
  - `app/web/pages/backtest.py`: `8563` lines
  - `app/web/runtime/backtest.py`: `2971` lines
  - `finance/sample.py`: `2075` lines
  - `finance/strategy.py`: `1182` lines
- Confirmed the recommended next-step direction is:
  - keep `backtest.py` as the page orchestrator
  - keep strategy simulation in finance layers
  - split by family/shared helper modules rather than forcing a deep inheritance hierarchy
- Logged the durable guidance in:
  - `QUESTION_AND_ANALYSIS_LOG.md`

### 2026-04-05 - Strict annual validation policy later pass was connected to promotion decision

- Added stricter later-pass promotion thresholds for strict annual family:
  - `Max Underperformance Share (%)`
  - `Min Worst Rolling Excess (%)`
- Connected the new thresholds through:
  - single strategy strict annual forms
  - compare overrides
  - history / `Load Into Form`
  - runtime meta
  - `Real-Money`
  - `Execution Context`
  - compare `Strategy Highlights`
- Added `validation_policy_status = normal / watch / caution / unavailable`
  and made `promotion_decision` consider that status.
- Verified:
  - `py_compile`
  - DB-backed strict annual smoke with preset-backed tickers
- Added a dedicated Phase 12 implementation note and refreshed:
  - current TODO board
  - Phase 12 checklist
  - comprehensive analysis
  - doc index

### 2026-04-05 - Strict annual broader benchmark contract later pass was added

- Added `Benchmark Contract` to strict annual family:
  - `Ticker Benchmark`
  - `Candidate Universe Equal-Weight`
- Connected the new benchmark contract through:
  - strict annual single strategy forms
  - compare overrides
  - history / `Load Into Form`
  - runtime meta
  - `Real-Money`
  - `Execution Context`
  - compare `Strategy Highlights`
- Candidate benchmark now records:
  - `benchmark_label`
  - `benchmark_symbol_count`
  - `benchmark_eligible_symbol_count`
- Verified:
  - `py_compile`
  - page import smoke
  - DB-backed strict annual smoke for both benchmark contracts
- Added a dedicated Phase 12 implementation note and refreshed:
  - current TODO board
  - Phase 12 checklist
  - comprehensive analysis
  - doc index

### 2026-04-05 - Strict annual portfolio guardrail policy later pass was added

- Added two drawdown-based promotion thresholds to strict annual family:
  - `Max Strategy Drawdown (%)`
  - `Max Drawdown Gap vs Benchmark (%)`
- Runtime now records:
  - `guardrail_policy_status`
  - `guardrail_policy_watch_signals`
  - `drawdown_gap_vs_benchmark`
- Promotion decision now considers guardrail policy together with:
  - benchmark policy
  - liquidity policy
  - validation policy
- Connected the new contract through:
  - strict annual single strategy forms
  - compare overrides
  - history / `Load Into Form`
  - `Real-Money`
  - `Execution Context`
  - compare `Strategy Highlights`
- Verified:
  - `py_compile`
  - page import smoke
  - DB-backed strict annual manual-ticker smoke showing `normal` and `caution` guardrail states
- Added a dedicated Phase 12 implementation note and refreshed:
  - current TODO board
  - Phase 12 checklist
  - comprehensive analysis
  - doc index

### 2026-04-05 - Strict annual actual drawdown guardrail first pass was added

- Added an optional actual strategy-side drawdown guardrail to strict annual family:
  - `Drawdown Guardrail`
  - `Drawdown Window (Months)`
  - `Strategy DD Threshold (%)`
  - `Drawdown Gap Threshold (%)`
- Connected the new contract through:
  - strict annual single strategy forms
  - compare overrides
  - history / `Load Into Form`
  - runtime meta
  - `Real-Money`
  - `Execution Context`
  - compare `Strategy Highlights`
- Strategy rows now record:
  - drawdown guardrail state / trigger
  - strategy drawdown
  - benchmark drawdown
  - drawdown gap
  - blocked ticker/count
- Verified:
  - `py_compile`
  - page import smoke
  - DB-backed strict annual quality / value / quality+value smoke
- Added a dedicated Phase 12 implementation note and refreshed:
  - current TODO board
  - Phase 12 checklist
  - comprehensive analysis
  - doc index

### 2026-04-05 - Phase 13 deployment-readiness and probation phase was opened

- Opened `Phase 13` as the next active finance phase after Phase 12 practical closeout
- Fixed the new phase direction as:
  - candidate shortlist contract
  - ETF second-pass hardening
  - probation / monitoring workflow
  - out-of-sample / rolling validation
  - deployment-readiness checklist
- Recorded the current operating status as:
  - `Phase 12`: implementation closed / manual_validation_pending
  - `Phase 13`: active planning and implementation
- Added the initial Phase 13 documents:
  - `.note/finance/phase13/PHASE13_DEPLOYMENT_READINESS_AND_PROBATION_PLAN.md`
  - `.note/finance/phase13/PHASE13_CURRENT_CHAPTER_TODO.md`
- Synced:
  - master phase roadmap
  - finance doc index
  - question and analysis log

### 2026-04-05 - Phase 13 candidate shortlist contract first pass was added

- Added a new Phase 13 shortlist layer on top of the existing `promotion_decision`
- Runtime now records:
  - `strategy_family`
  - `shortlist_family`
  - `shortlist_status`
  - `shortlist_next_step`
  - `shortlist_rationale`
- First-pass shortlist mapping was fixed as:
  - `hold -> hold`
  - `production_candidate -> watchlist`
  - `real_money_candidate -> paper_probation`
  - strict annual `real_money_candidate` with actual guardrails and candidate-equal-weight benchmark -> `small_capital_trial`
- Connected shortlist readout through:
  - single / focused `Real-Money`
  - `Execution Context`
  - compare `Strategy Highlights`
  - compare meta table
- Verified:
  - `py_compile`
  - DB-backed smoke for strict annual and GTAA shortlist meta linkage
  - helper-level smoke for `hold / watchlist / paper_probation / small_capital_trial`
- Added a dedicated Phase 13 implementation note and refreshed:
  - current TODO board
  - finance doc index
  - comprehensive analysis
  - question and analysis log

### 2026-04-05 - Phase 13 ETF second-pass guardrail first pass was added

- Added optional ETF actual guardrail rules to:
  - `GTAA`
  - `Risk Parity Trend`
  - `Dual Momentum`
- Connected the ETF guardrail contract through:
  - single strategy forms
  - compare overrides
  - history / `Load Into Form`
  - saved-portfolio compare context
- ETF runtime wrappers and DB-backed sample functions now carry:
  - `underperformance_guardrail_enabled`
  - `underperformance_guardrail_window_months`
  - `underperformance_guardrail_threshold`
  - `drawdown_guardrail_enabled`
  - `drawdown_guardrail_window_months`
  - `drawdown_guardrail_strategy_threshold`
  - `drawdown_guardrail_gap_threshold`
- ETF result rows now expose guardrail state / trigger columns, so runtime meta can collect trigger counts in the same way as strict annual.
- Verified:
  - `py_compile`
  - page/runtime import smoke
  - DB-backed ETF smoke for `GTAA`, `Risk Parity Trend`, `Dual Momentum`
- Added a dedicated Phase 13 implementation note and refreshed:
  - current TODO board
  - finance doc index
  - comprehensive analysis
  - question and analysis log

### 2026-04-05 - Phase 13 probation and monitoring workflow first pass was added

- Added a new deployment-readiness layer on top of shortlist meta:
  - `probation_status`
  - `probation_stage`
  - `probation_review_frequency`
  - `probation_next_step`
  - `monitoring_status`
  - `monitoring_focus`
  - `monitoring_breach_signals`
  - `monitoring_review_frequency`
  - `monitoring_next_step`
- First-pass probation mapping now reads:
  - `hold -> not_ready`
  - `watchlist -> watchlist_review`
  - `paper_probation -> paper_tracking`
  - `small_capital_trial -> small_capital_live_trial`
- Monitoring is now derived from existing policy statuses and guardrail trigger counts, so Phase 13 can surface:
  - `blocked`
  - `routine_review`
  - `heightened_review`
  - `breach_watch`
- Connected the new workflow readout through:
  - single strategy `Real-Money`
  - `Execution Context`
  - compare `Strategy Highlights`
  - compare meta table
- Verified:
  - `py_compile`
  - page/runtime import smoke
  - helper-level branch smoke for probation / monitoring mappings
  - DB-backed strict annual and ETF smoke for meta propagation
- Added a dedicated Phase 13 implementation note and refreshed:
  - current TODO board
  - finance doc index
  - comprehensive analysis
  - question and analysis log

### 2026-04-05 - Phase 13 rolling and out-of-sample validation workflow first pass was added

- Added a new review layer on top of the existing benchmark-aligned validation surface:
  - `rolling_review_status`
  - `rolling_review_recent_excess_return`
  - `rolling_review_recent_drawdown_gap`
  - `out_of_sample_review_status`
  - `out_of_sample_in_sample_excess_return`
  - `out_of_sample_out_sample_excess_return`
  - `out_of_sample_excess_change`
- Recent regime review now reads the latest `12M` / `252D` window and compares it with the previous window when available.
- Split-period review now reads the aligned history as first-half vs second-half and flags later-period deterioration.
- This first pass does not change `promotion_decision`; instead it feeds:
  - single strategy `Real-Money`
  - `Execution Context`
  - compare `Strategy Highlights`
  - compare meta table
  - probation / monitoring review interpretation
- Added a dedicated Phase 13 implementation note and refreshed:
  - current TODO board
  - finance doc index
  - comprehensive analysis
  - question and analysis log

### 2026-04-05 - Phase 13 deployment-readiness checklist first pass was added

- Added a new deployment checklist layer on top of:
  - shortlist
  - probation / monitoring
  - rolling / out-of-sample review
  - benchmark / liquidity / validation / guardrail policy
- New runtime meta now includes:
  - `deployment_readiness_status`
  - `deployment_readiness_next_step`
  - `deployment_checklist_rows`
  - pass/watch/fail/unavailable counts
- First-pass deployment status now reads:
  - `blocked`
  - `review_required`
  - `watchlist_only`
  - `paper_only`
  - `small_capital_ready`
  - `small_capital_ready_with_review`
- Connected the new checklist through:
  - single strategy `Real-Money`
  - `Execution Context`
  - compare `Strategy Highlights`
  - compare meta table
- Added a dedicated Phase 13 implementation note and refreshed:
  - current TODO board
  - finance doc index
  - comprehensive analysis
  - question and analysis log

### 2026-04-05 - Phase 13 was closed out at practical completion

- Reviewed the remaining Phase 13 backlog and separated:
  - closeout blockers
  - later-pass backlog
- Concluded that the following remain valuable but are not closeout blockers:
  - ETF current-operability actual block rule
  - ETF point-in-time operability history
  - monthly probation note logging
  - richer live deployment workflow
- Marked Phase 13 as:
  - `practical closeout`
  - `manual_validation_pending`
- Added closeout / handoff documents:
  - `PHASE13_COMPLETION_SUMMARY.md`
  - `PHASE13_NEXT_PHASE_PREPARATION.md`
  - `PHASE13_TEST_CHECKLIST.md`
- Refreshed:
  - current TODO board
  - roadmap
  - finance doc index
  - question and analysis log

### 2026-04-05 - Phase 13 checklist location wording and glossary terms were clarified

- Clarified the Phase 13 checklist so that `Candidate Shortlist Surface` explicitly points to:
  - `Backtest > Single Strategy`
  - run result area
  - `Real-Money` tab
  - `Execution Context`
- Added glossary entries for:
  - `Real-Money Tab`
  - `Promotion Decision`
  - `Candidate Shortlist`
  - `Shortlist Status`
  - `Shortlist Next Step`
  - `Execution Context`

### 2026-04-05 - Real-Money 탭 UX를 판단 순서 중심으로 재구성

- Reorganized the single-strategy `Real-Money` tab into four clearer groups:
  - `현재 판단`
  - `검토 근거`
  - `실행 부담`
  - `상세 데이터`
- Added a top-level reading guide so users can understand:
  - what to look at first
  - what explains the current decision
  - what belongs to operability / cost burden
- Moved lower-signal details into:
  - collapsed policy/detail areas
  - the final detail tab
- Updated the Phase 13 checklist wording so it points to the new `Real-Money` internal tab structure.

### 2026-04-05 - 실전형 핵심 용어를 glossary에 추가 정리

- Added glossary entries or clearer definitions for:
  - `Validation`
  - `Validation Policy`
  - `Liquidity`
  - `Benchmark Policy`
  - `Guardrail Policy`
- Kept the existing:
  - `Benchmark`
  - `Liquidity Policy`
  - `Portfolio Guardrail`
  entries and aligned the new terms around the same explanation structure.

### 2026-04-05 - Latest Backtest Run 안내 영역을 한국어 중심으로 재구성

- Reorganized the header area under `Latest Backtest Run` so the user sees:
  - how to read the result
  - which result surfaces are available in this run
  - what warnings should be reviewed together
- Replaced scattered English guidance with grouped Korean guidance.
- Merged per-run warnings into one clearer warning block instead of rendering them as disconnected lines.

### 2026-04-05 - Real-Money 탭 섹션을 카드형 그룹으로 시각 정리

- Wrapped the main Real-Money sections in bordered containers so related metrics and captions read as one group.
- Added consistent section structure:
  - title
  - short explanation
  - metrics / rationale / status message
- Kept the same underlying runtime/meta semantics while making section boundaries easier to scan.

### 2026-04-06 - Hold 상태 해결 가이드를 Real-Money 탭에 추가

- Added a `Hold 해결 가이드` block under `Real-Money > 현재 판단` when `Promotion Decision = hold`.
- Mapped promotion rationale codes into operator-friendly Korean guidance rows:
  - `막히는 항목`
  - `먼저 볼 위치`
  - `권장 조치`
- Updated the Phase 13 checklist so manual QA explicitly checks that this guide appears for hold cases.

### 2026-04-06 - 실행 부담 탭의 Liquidity Policy 노출을 강화

- Added a dedicated `Liquidity Policy` section inside `Real-Money > 실행 부담`.
- Surfaced the key metrics together:
  - `Policy Status`
  - `Min Avg Dollar Volume 20D`
  - `Min Clean Coverage`
  - `Actual Clean Coverage`
  - `Liquidity Excluded Rows`
- Added direct Korean explanations for why `unavailable / watch / caution` appears and what the user should change next.

### 2026-04-06 - `Min Avg Dollar Volume 20D` 용어를 glossary에 명시적으로 추가

- Added a dedicated glossary entry for `Min Avg Dollar Volume 20D`.
- Clarified:
  - that it means recent 20-day average dollar trading volume
  - why it is used as a simple liquidity filter
  - that `0.0M` effectively means the liquidity filter is off

### 2026-04-06 - Hold를 벗어나는 현실적인 Phase 13 후보 설정을 한 번 더 탐색

- Ran a targeted search for a non-hold example the user can actually use as a reference.
- A practical example was found with:
  - `GTAA Universe (U1 Offensive Candidate Base)`
  - benchmark `SPY`
  - `top=2`
  - `rebalance interval=3`
  - score horizons `1/3/6/12`
  - `risk_off_mode=cash_only`
  - ETF operability policy disabled for this run (`promotion_min_etf_aum_b=None`, `promotion_max_bid_ask_spread_pct=None`)
- Outcome for that configuration:
  - `promotion_decision = production_candidate`
  - `shortlist_status = watchlist`
  - `deployment_readiness_status = review_required`
  - `validation_status = watch`
  - summary: `CAGR 16.24%`, `MDD -10.59%`
- Also observed that some bond benchmarks (`TLT`, `IEF`, `LQD`) could push the same GTAA candidate to `real_money_candidate`,
  but that path was considered less operator-honest as a default example because the benchmark is less aligned with the user's likely broad-equity comparison frame.

### 2026-04-06 - Quality + Value strict annual에서도 hold를 벗어나는 재현 가능한 예시를 확보

- Ran a focused search for a `Quality + Value > Strict Annual` configuration that the user can reproduce directly from the UI without hidden/disabled policy toggles.
- A stronger example than expected was found with:
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
  - `trend_filter = off`
  - `market_regime = off`
  - `underperformance_guardrail = on`
  - `drawdown_guardrail = on`
- Outcome for that configuration:
  - `promotion_decision = real_money_candidate`
  - `shortlist_status = small_capital_trial`
  - `deployment_readiness_status = review_required`
  - `validation / benchmark / liquidity / validation policy / guardrail policy / rolling / out_of_sample = normal`
  - `promotion_rationale = []`
  - summary: `CAGR 32.44%`, `MDD -28.35%`
- Compared to the static contract version, the practical difference was that `dynamic PIT` removed the lingering `static_universe_contract` blocker while leaving the other policy surfaces healthy.

### 2026-04-06 - 실전형 입력 항목 설명을 용어 사전에 보강

- Added glossary entries for:
  - `Minimum Price`
  - `Minimum History`
  - `Trend Filter`
  - `Market Regime`
  - `Underperformance Guardrail`
  - `Drawdown Guardrail`
- Also strengthened the existing `Transaction Cost` entry with a simple `bps` interpretation example.
- Purpose:
  - make real-money input controls easier to understand without re-explaining them ad hoc in chat each time.

### 2026-04-06 - 2016년 시작, MDD 15% 이내 조건에서 비보류 포트폴리오 후보를 재탐색

- Interpreted the user's `MDD 15 이하` request as `Maximum Drawdown >= -15%`.
- Re-ran practical candidates with `start='2016-01-01'` across:
  - GTAA candidate universes
  - ETF strategy candidates
  - `Quality + Value > Strict Annual`
- Observed:
  - with `SPY` as benchmark, several GTAA candidates met the MDD target but still remained `hold` because `validation = caution`
  - `Quality + Value > Strict Annual` met non-hold in some contracts, but did not satisfy the stricter `MDD <= 15%` target for the full 2016-start window
- A usable candidate was found with:
  - strategy: `GTAA`
  - preset base: `U1 Offensive Candidate Base`
  - benchmark: `TLT` (also `IEF`/`LQD` worked similarly)
  - `top=2`
  - `rebalance interval=3`
  - score horizons `1/3/6/12`
  - `start='2016-01-01'`
  - no extra trend/regime overlay
  - ETF operability policy disabled for this search path
- Outcome:
  - `promotion_decision = real_money_candidate`
  - `shortlist_status = paper_probation`
  - `deployment_readiness_status = paper_only`
  - `validation / rolling / out_of_sample = normal`
  - summary: `CAGR 15.04%`, `MDD -9.82%`

### 2026-04-06 - Quality + Value dynamic PIT에 2016 시작과 MDD 15% 이내를 동시에 요구하면 현실적인 비보류 후보가 잘 나오지 않음

- Re-ran `Quality + Value > Strict Annual` with the user's corrected fixed constraints:
  - strategy family fixed to `Quality + Value`
  - `Universe Contract = Historical Dynamic PIT Universe`
  - `start = 2016-01-01`
  - target interpreted as `Maximum Drawdown >= -15%`
- Searched across practical UI-reproducible settings:
  - `top_n` variations
  - monthly / slower rebalance cadence
  - `Candidate Universe Equal-Weight` and defensive ticker benchmarks
  - trend/regime on/off and guardrail combinations
- Result:
  - did not find a convincing non-hold candidate that also stayed within the `-15%` MDD target
  - the stronger previously found non-hold `Quality + Value` candidate still sat closer to `MDD ≈ -28%`
  - more defensive trend/regime configurations often reduced activity but still did not get both:
    - `hold 아님`
    - `MDD -15% 이내`
- Practical implication:
  - under the full 2016-start window, the current `Quality + Value` strict annual family appears too equity-exposed to satisfy that drawdown target without either:
    - shortening the start window
    - relaxing the drawdown target
    - or moving to a different strategy family

### 2026-04-06 - `Quality` 단독 strict annual은 SPY를 이기는 후보를 만들 수 있지만 현재 검증 계약에선 hold가 남음

- Search goal:
  - find a portfolio with `start = 2016-01-01`, `Universe Contract = Historical Dynamic PIT Universe`, `top_n <= 10` that beats the `SPY` baseline on both `CAGR` and `MDD`
- Search focus:
  - `Quality Snapshot (Strict Annual)` family
  - default quality factor set
  - `month_end`, `rebalance_interval = 1`
  - `trend_filter = off`
  - `market_regime = off`
  - underperformance / drawdown guardrails on
- Best confirmed candidates:
  - `top_n = 2`
    - `CAGR = 29.69%`
    - `MDD = -25.19%`
  - `top_n = 1`
    - `CAGR = 21.09%`
    - `MDD = -27.08%`
  - `top_n = 5`
    - `CAGR = 21.20%`
    - `MDD = -29.56%`
- Comparison against SPY baseline:
  - all three beat `SPY` on both `CAGR` and `MDD`
  - however, they still remained in `hold` under the current validation contract
- Practical implication:
  - `quality-only` strict annual is currently the best confirmed family for the user's "beat SPY" criterion
  - but within the tested practical UI settings, it does not yet convert into a non-hold deployment candidate
  - next levers are:
    - refine the quality factor set further
    - test a slightly different benchmark contract only for promotion interpretation
    - or widen the search window around `top_n = 1 / 2 / 5`

### 2026-04-06 - Quality + Value factor 및 option 자체를 바꿔도 2016 시작에서 `hold 아님 + MDD 15% 이내`는 끝내 못 맞춤

- Follow-up exploration after the user explicitly asked whether factor changes had been tested.
- Fixed constraints kept:
  - `Quality + Value > Strict Annual`
  - `Universe Contract = Historical Dynamic PIT Universe`
  - `start = 2016-01-01`
  - target interpreted as `Maximum Drawdown >= -15%`
- Re-ran with defensive factor sets plus slower cadence:
  - quality:
    - `q_balance_sheet = current_ratio, cash_ratio, debt_to_assets, debt_ratio`
    - `q_capital_discipline = roe, roa, cash_ratio, debt_to_assets`
    - `q_profitability = roe, roa, net_margin, operating_margin, gross_margin`
  - value:
    - `v_cashflow_only = ocf_yield, fcf_yield, pcr, pfcr`
    - `v_asset_earnings = book_to_market, earnings_yield, operating_income_yield`
- Best low-drawdown case:
  - `q_balance_sheet + v_cashflow_only`
  - `month_end`, `rebalance_interval = 6`, `top_n = 30`
  - `Candidate Universe Equal-Weight` benchmark
  - result:
    - `promotion = hold`
    - `CAGR = 2.40%`
    - `MDD = -13.57%`
- Best non-hold case after benchmark retune:
  - same defensive factor set with `benchmark = LQD`
  - `month_end`, `rebalance_interval = 6`, `top_n = 40` or `50`
  - result:
    - `promotion = production_candidate`
    - `shortlist = watchlist`
    - `deployment = review_required`
    - `CAGR ≈ 5.48%`
    - `MDD ≈ -18.91%`
- Practical implication:
  - factor changes do help, but in the current implementation there is still a trade-off:
    - `MDD 15% 이내`까지 낮추면 `hold`가 남고
    - `hold`를 벗어나면 `MDD`가 다시 `-19%` 안팎으로 커짐
  - current conclusion remains:
    - within practical UI-reproducible settings, no `Quality + Value` configuration met both:
      - `hold 아님`
      - `2016 시작 + MDD 15% 이내`

### 2026-04-06 - 서브 에이전트 병렬 탐색으로 `CAGR 15% 이상 + MDD 20% 이내` exact hit를 찾았고, Value Strict Annual이 최종 승자였음

- The user asked for another search, explicitly requesting sub-agents.
- Fixed constraints used:
  - `start = 2016-01-01`
  - `end = 2026-04-01`
  - `Universe Contract = Historical Dynamic PIT Universe`
  - `top_n <= 10`
  - target:
    - `CAGR >= 15%`
    - `Maximum Drawdown >= -20%`
- `Quality`, `Value`, `Quality + Value` strict annual families were explored in parallel by sub-agents, then the best candidate was re-checked in the main environment.
- Final exact-hit candidate:
  - family: `Value > Strict Annual`
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
- Main-environment revalidation:
  - `CAGR = 15.84%`
  - `MDD = -17.42%`
  - `promotion = hold`
  - `shortlist = hold`
  - `deployment = blocked`
- Practical implication:
  - this candidate satisfies the user's numeric target
  - but still does not clear the current promotion/deployment contract
  - so it is best interpreted as:
    - a strong research/selection reference
    - not yet a promotion-cleared operating candidate

### 2026-04-06 - `hold 아님 + CAGR 20% 이상 + MDD 25% 이내` 조건은 strict annual 범위에서 exact hit가 없었음

- The user asked for another sub-agent search with a stricter return target:
  - `promotion != hold`
  - `CAGR >= 20%`
  - `Maximum Drawdown >= -25%`
  - `start = 2016-01-01`
  - `Universe Contract = Historical Dynamic PIT Universe`
  - `top_n <= 10`
- `Quality`, `Value`, `Quality + Value` strict annual families were explored in parallel.
- Result:
  - no exact-hit candidate was found in the searched practical setting space
  - the search again converged on `Value > Strict Annual`
- Best near-miss:
  - default value factor set
  - `month_end`
  - `rebalance_interval = 1`
  - `top_n = 10`
  - `benchmark = SPY`
  - `trend_filter = on`
  - `market_regime = on`
  - `underperformance_guardrail = on`
  - `drawdown_guardrail = on`
  - `CAGR = 18.81%`
  - `MDD = -23.71%`
  - `promotion = hold`
- Practical implication:
  - current strict annual implementation can get close to the requested return/risk band
  - but not while also escaping `hold`
  - this suggests the next binding constraint is the validation/promotion contract, not simple universe/cadence tuning

### 2026-04-06 - SPY 대비 성과와 저낙폭을 동시에 만족하는 Value Strict Annual 후보를 찾음

- New search goal:
  - find a portfolio with
    - `CAGR >= 15%`
    - `Maximum Drawdown >= -20%`
    - `start = 2016-01-01`
    - `Universe Contract = Historical Dynamic PIT Universe`
    - `top_n <= 10`
    - benchmark compared against `SPY`
- Family search summary:
  - `Quality Strict Annual`:
    - found SPY-beating candidates on raw CAGR/MDD, but none met the tighter `-20%` drawdown target
  - `Quality + Value Strict Annual`:
    - explored, but no strong candidate surfaced within the practical settings checked so far
  - `Value Strict Annual`:
    - best fit for the user's target
- Best exact candidate:
  - factor set:
    - `earnings_yield`
    - `ocf_yield`
    - `operating_income_yield`
    - `fcf_yield`
  - `month_end`, `rebalance_interval = 1`, `top_n = 9`
  - `trend_filter = on`
  - `market_regime = on`
  - `underperformance_guardrail = on`
  - `drawdown_guardrail = on`
  - `benchmark = SPY`
  - result:
    - `CAGR = 15.84%`
    - `MDD = -17.42%`
    - `promotion = hold`
- Practical implication:
  - this is currently the clearest `SPY`-beating candidate that also satisfies the user's `CAGR / MDD` thresholds
  - if the user wants to remove `hold`, the next step is to relax or retune the policy layer, not the raw return profile

### 2026-04-06 - SPY 대비 우위와 `CAGR >= 15%`, `MDD >= -20%`를 동시에 만족하는 후보를 family별로 다시 탐색했지만, 최종 교집합은 찾지 못함

- Follow-up exploration requested by the user:
  - search for a portfolio that beats `SPY` on both CAGR and drawdown
  - fixed constraints:
    - start `2016-01-01`
    - end `2026-04-01`
    - `Universe Contract = Historical Dynamic PIT Universe`
    - `top_n <= 10`
    - `CAGR >= 15%`
    - `Maximum Drawdown >= -20%`
- Search coverage:
  - `Quality Strict Annual`
  - `Value Strict Annual`
  - `Quality + Value Strict Annual`
- Useful findings:
  - `Value Strict Annual` was the strongest family in this search
  - best raw candidate:
    - `v_default`
    - `month_end / interval=1 / top_n=10`
    - `CAGR 29.89%`
    - `MDD -29.15%`
    - `promotion = real_money_candidate`
  - best low-drawdown candidate:
    - `v_profit_cashflow`
    - `month_end / interval=1 / top_n=5`
    - `benchmark = LQD`
    - `CAGR 13.16%`
    - `MDD -19.18%`
    - `promotion = hold`
- Practical implication:
  - within the tested practical settings, the user’s target set remains a hard trade-off:
    - when CAGR is high enough, drawdown stays above the requested floor
    - when drawdown is below the requested floor, CAGR falls below the requested floor
  - no family produced a clean `CAGR >= 15%` and `MDD >= -20%` intersection in the tested grid

### 2026-04-06 - Quality Strict Annual는 SPY를 이기는 raw candidate가 있지만 full hardening을 켜면 edge가 사라짐

- Ran a SPY-dominance search for `Quality Snapshot (Strict Annual)` with:
  - `start = 2016-01-01`
  - `end = 2026-04-01`
  - `Universe Contract = Historical Dynamic PIT Universe`
  - `top_n <= 10`
- 1st pass screen:
  - factor sets compared:
    - `default`
    - `legacy`
    - `profitability`
    - `balance_sheet`
    - `capital_discipline`
    - `efficiency`
  - base settings:
    - `month_end`
    - `rebalance_interval = 1`
    - `top_n = 2 / 5 / 10`
    - `trend_filter = off`
    - `market_regime = off`
    - `underperformance_guardrail = off`
    - `drawdown_guardrail = off`
    - `benchmark = SPY`
- 2nd pass verification:
  - re-tested the top candidates with `trend_filter = on`, `market_regime = on`
  - left `underperformance_guardrail` and `drawdown_guardrail` off to keep the signal visible
- Best SPY-dominance candidates:
  - `capital_discipline`
    - `roe, roa, cash_ratio, debt_to_assets`
    - `month_end / interval 1 / top_n 10`
    - `trend_filter = on`, `market_regime = on`
    - `CAGR = 15.80%`
    - `MDD = -27.97%`
  - `balance_sheet`
    - `current_ratio, cash_ratio, debt_to_assets, debt_ratio`
    - `month_end / interval 1 / top_n 5`
    - `trend_filter = on`, `market_regime = on`
    - `CAGR = 15.71%`
    - `MDD = -33.20%`
  - `balance_sheet`
    - same factor set
    - `month_end / interval 1 / top_n 10`
    - `trend_filter = on`, `market_regime = on`
    - `CAGR = 14.46%`
    - `MDD = -26.83%`
- Important follow-up:
  - when `underperformance_guardrail` and `drawdown_guardrail` are both turned on, the edge disappears again and the candidates fall back to `hold`
  - this means the family can beat SPY on raw return/risk, but the full operational contract still requires more work

### 2026-04-06 - SPY 기준 outperformance 탐색에서는 Value Strict Annual family가 Quality보다 우세했지만, 승자들도 hold를 벗어나지 못함

- Request:
  - find a portfolio that beats SPY on both CAGR and MDD under:
    - `start = 2016-01-01`
    - `Universe Contract = Historical Dynamic PIT Universe`
    - `top_n <= 10`
  - strategy family could be `Quality`, `Value`, or `Quality + Value`, but the best option should be reported
- Search scope:
  - `Quality Strict Annual`
  - `Value Strict Annual`
  - practical UI-reproducible settings only
  - `trend_filter`, `market_regime`, `underperformance_guardrail`, `drawdown_guardrail` all on
- Result:
  - `Quality` family did not produce any candidate that beat SPY on both CAGR and MDD
  - `Value` family produced the best candidates
  - top winners were all still `hold`
  - best three value candidates:
    - `v_default / month_end / interval 1 / top_n 10`
      - `CAGR = 18.81%`
      - `MDD = -23.71%`
    - `v_default / month_end / interval 1 / top_n 5`
      - `CAGR = 17.20%`
      - `MDD = -29.62%`
    - `v_profit_cashflow / month_end / interval 1 / top_n 10`
      - `CAGR = 14.61%`
      - `MDD = -15.16%`
- Practical implication:
  - if the user wants a strict `SPY` outperformance filter, `Value Strict Annual` is the best of the tested families
  - however, within the current validation contract, even the best SPY-beating `Value` candidates still remained `hold`

### 2026-04-06 - hold 원인은 validation caution이었고, requested family 내 non-hold exact hit는 아직 못 찾음

- Re-checked the strongest numeric candidate:
  - `Value > Strict Annual`
  - factors:
    - `earnings_yield`
    - `ocf_yield`
    - `operating_income_yield`
    - `fcf_yield`
  - `month_end / interval 1 / top_n 9`
  - `benchmark = SPY`
  - `CAGR = 15.84%`
  - `MDD = -17.42%`
- Hold cause:
  - `validation_status = caution`
  - `validation_policy_status = caution`
  - `rolling_review_status = caution`
  - `promotion_rationale = ['validation_caution', 'validation_policy_caution']`
- Follow-up search across `Quality` and `Quality + Value` strict annual families:
  - no non-hold exact hit found for the requested `CAGR >= 15%` and `MDD >= -20%` target
  - the best non-hold near-misses were Q+V production-candidate configurations with much lower CAGR
- Practical implication:
  - the remaining blocker is not the raw return/drawdown pair alone
  - it is the validation layer that still keeps the best numeric candidate in `hold`

### 2026-04-06 - Value Strict Annual hold-free exact hit는 benchmark / cadence / trend / regime를 바꿔도 끝내 못 찾았음

- Follow-up exploration after the user asked to isolate the `hold` reason and then search again for a non-hold candidate under the same numeric target.
- Fixed constraints:
  - `Value > Strict Annual`
  - `Universe Contract = Historical Dynamic PIT Universe`
  - `start = 2016-01-01`
  - `top_n <= 10`
  - target:
    - `promotion != hold`
    - `CAGR >= 15%`
    - `MDD >= -20%`
- Practical UI-exposed dimensions checked:
  - benchmark contract / ticker
  - factor combinations
  - `top_n` in the `7~10` range
  - cadence with `rebalance_interval = 1 / 3`
  - `trend_filter` on/off
  - `market_regime` on/off
- Result:
  - the best numeric candidate remained the same `Value Strict Annual` exact-hit setup:
    - `CAGR = 15.84%`
    - `MDD = -17.42%`
    - `promotion = hold`
    - `reason = validation_caution + validation_policy_caution`
  - no non-hold exact hit was found in the tested grid
- Practical implication:
  - benchmark / cadence / trend-regime tuning did not structurally resolve the hold
  - the remaining next lever is the validation / promotion policy layer, not the raw return profile

### 2026-04-06 - `CAGR 20% 이상 + MDD 25% 이내 + hold 아님` exact hit는 이번 탐색 범위에서도 찾지 못함

- Follow-up search after the user relaxed the drawdown target and raised the CAGR target.
- Fixed constraints kept:
  - `start = 2016-01-01`
  - `end = 2026-04-01`
  - `Universe Contract = Historical Dynamic PIT Universe`
  - `top_n <= 10`
  - target interpreted as:
    - `CAGR >= 20%`
    - `Maximum Drawdown >= -25%`
    - `promotion != hold`
- Searched practical UI-reproducible spaces across:
  - `Quality Strict Annual`
  - `Value Strict Annual`
  - `Quality + Value Strict Annual`
  - factor combinations
  - benchmark contract/ticker variants
  - cadence / top_n
  - trend and market regime toggles
- Result:
  - no non-hold exact hit was found in the tested grid
  - the strongest candidate in the space remained the `Value Strict Annual` exact-hit setup around:
    - `CAGR = 15.84%`
    - `MDD = -17.42%`
    - `promotion = hold`
  - the blocker remained:
    - `validation_status = caution`
    - `validation_policy_status = caution`
    - `rolling_review_status = caution`
- Practical implication:
  - relaxing the drawdown target to `25%` was not sufficient by itself to unlock a non-hold candidate with `CAGR >= 20%`
  - the next lever is still the validation / promotion threshold layer, not just raw factor or cadence tuning

### 2026-04-06 - strict annual family 백테스트 탐색 결과를 Quality / Value / Quality+Value 기준으로 통합 정리함

- The user asked for one summary document that organizes the backtests run so far across:
  - `Quality`
  - `Value`
  - `Quality + Value`
- Created:
  - `.note/finance/phase13/PHASE13_STRICT_ANNUAL_FAMILY_BACKTEST_SUMMARY.md`
- Consolidated practical conclusions:
  - `Value Strict Annual` was the strongest family overall
  - `Quality Strict Annual` could produce useful raw candidates, but full hardening often still ended in `hold`
  - `Quality + Value Strict Annual` was best for lowering drawdown, but usually sacrificed too much CAGR
  - the most common remaining blocker across the strongest candidates was the `validation / promotion` layer rather than benchmark or liquidity alone
- Also updated:
  - `.note/finance/FINANCE_DOC_INDEX.md`
  - `.note/finance/QUESTION_AND_ANALYSIS_LOG.md`

### 2026-04-06 - strict annual family target search를 Coverage 300/500/1000까지 넓혀 다시 확인함

- The user asked to retry the target search with wider strict annual presets:
  - `US Statement Coverage 300`
  - `US Statement Coverage 500`
  - `US Statement Coverage 1000`
- Target stayed fixed:
  - `Historical Dynamic PIT Universe`
  - `2016-01-01 ~ 2026-04-01`
  - `top_n <= 10`
  - `CAGR >= 15%`
  - `Maximum Drawdown >= -20%`
  - `promotion != hold`
- Used sub-agent parallel search by coverage and consolidated the result in:
  - `.note/finance/phase13/PHASE13_STRICT_ANNUAL_COVERAGE300_500_1000_TARGET_SEARCH.md`
- Practical result:
  - no exact-hit was confirmed for `Coverage 300` or `Coverage 500`
  - `Coverage 1000` did not surface an exact-hit within the current exploratory window and remained inconclusive
  - widening coverage alone did not solve the target search
  - wider coverage exposed more `validation`, `liquidity`, and `benchmark policy` friction

### 2026-04-06 - strict annual family에서 `real_money_candidate + SPY 초과 CAGR + MDD 25% 이내` exact-hit를 다시 탐색함

- The user asked for one practical strict annual portfolio from:
  - `Quality`
  - `Value`
  - `Quality + Value`
- Target:
  - `promotion = real_money_candidate`
  - raw `CAGR > SPY`
  - `Maximum Drawdown >= -25%`
  - `2016-01-01 ~ 2026-04-01`
  - `Historical Dynamic PIT Universe`
- Used sub-agent parallel search by family and consolidated the result in:
  - `.note/finance/phase13/PHASE13_REAL_MONEY_CANDIDATE_SPY_MDD25_SEARCH.md`
- Practical result:
  - no family produced an exact-hit under the tested practical grid
  - `Value` remained the strongest family
  - strongest raw `real_money_candidate`:
    - default value factors
    - `CAGR = 29.89%`
    - `MDD = -29.15%`
  - strongest balanced near-miss:
    - `earnings_yield / ocf_yield / operating_income_yield / fcf_yield`
    - `CAGR = 15.84%`
    - `MDD = -17.42%`
    - but `promotion = hold`

### 2026-04-06 - Value raw winner를 백테스트 UI에서 다시 넣을 수 있는 가이드 문서 추가

- The user asked for a backtest-facing Markdown guide that explains how to reproduce the strongest `Value` raw winner.
- Created:
  - `.note/finance/phase13/PHASE13_VALUE_RAW_WINNER_BACKTEST_GUIDE.md`
- The guide records:
  - which family / variant to pick
  - which preset and universe contract to use
  - the exact factor set
  - rebalance / top_n / risk overlay settings
  - the expected result:
    - `CAGR = 29.89%`
    - `MDD = -29.15%`
    - `promotion = real_money_candidate`
- Also documented the balanced near-miss so the user can compare “raw strongest” vs “safer but still hold”.

### 2026-04-06 - backtest 결과 문서 전용 폴더와 인덱스 운영 기준을 추가함

- The user suggested separating result-oriented backtest Markdown files from phase execution docs.
- Created:
  - `.note/finance/backtest_reports/README.md`
  - `.note/finance/backtest_reports/BACKTEST_REPORT_INDEX.md`
- Updated guidance so future durable result notes can be managed separately from phase planning / TODO / checklist documents.
- Practical decision:
  - existing phase docs stay where they are for now
  - new result-centered backtest docs should gradually move toward `.note/finance/backtest_reports/`

### 2026-04-06 - Phase 13 backtest 결과 문서를 전용 폴더로 실제 이동함

- Moved the major Phase 13 result-oriented Markdown reports into:
  - `.note/finance/backtest_reports/phase13/`
- Left short compatibility stubs in:
  - `.note/finance/phase13/`
  so existing references do not immediately break.
- Updated:
  - `.note/finance/backtest_reports/BACKTEST_REPORT_INDEX.md`
  - `.note/finance/FINANCE_DOC_INDEX.md`
- Practical implication:
  - Phase 13 execution docs remain in `phase13/`
  - Phase 13 backtest result docs now have a dedicated canonical home under `backtest_reports/phase13/`

### 2026-04-06 - backtest_reports를 전략 허브 중심 구조로 다시 정리함

- The user pointed out that phase-based raw report files are not the most comfortable reading surface.
- Created strategy hub documents:
  - `.note/finance/backtest_reports/strategies/QUALITY_STRICT_ANNUAL.md`
  - `.note/finance/backtest_reports/strategies/VALUE_STRICT_ANNUAL.md`
  - `.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL.md`
- Updated:
  - `.note/finance/backtest_reports/BACKTEST_REPORT_INDEX.md`
  - `.note/finance/backtest_reports/README.md`
  - `.note/finance/backtest_reports/phase13/README.md`
  so reading now starts from strategy hubs, while phase13 remains the raw archive layer.

### 2026-04-06 - GTAA single backtest form의 universe payload regression을 수정함

- The GTAA form raised `NameError: name 'universe_mode' is not defined` when the user tried to run a single GTAA backtest.
- Root cause:
  - the form now receives `_universe_mode` from `_render_gtaa_universe_inputs()`
  - but the payload builder still referenced the removed `universe_mode` local name
- Fixed:
  - `app/web/pages/backtest.py`
  - GTAA payload now uses `_universe_mode` directly, consistent with the equal-weight path and helper return contract

### 2026-04-07 - GTAA non-hold / SPY outperformance 후보를 다시 탐색해 backtest report로 정리함

- The user clarified that the actual ask was not a category explanation, but a GTAA search that finds a portfolio satisfying:
  - `promotion != hold`
  - `deployment_readiness_status != blocked`
  - better `CAGR` than `SPY`
  - better `MDD` than `SPY`
- Used sub-agent parallel search across DB-backed ETF candidates with 2016+ history.
- Practical final candidate:
  - `SPY, QQQ, GLD, LQD`
  - `top = 2`
  - `interval = 3`
  - `score horizons = 1M / 3M`
  - `benchmark = SPY`
  - `promotion = production_candidate`
  - `deployment = watchlist_only`
  - `CAGR = 14.7671%`
  - `MDD = -11.5626%`
- Created:
  - `.note/finance/backtest_reports/phase13/PHASE13_GTAA_NONHOLD_SPY_OUTPERFORMANCE_SEARCH.md`
  - `.note/finance/backtest_reports/strategies/GTAA.md`

### 2026-04-06 - Phase 13 테스트 체크리스트를 실제 수정 이력 기준으로 다시 정리함

- During manual-test-driven Phase 13 follow-up work, several UX surfaces changed:
  - `Latest Backtest Run` guidance became more structured and Korean-first
  - `Real-Money` was reorganized into clearer internal tabs and grouped sections
  - `Hold 해결 가이드` and `Liquidity Policy` became more directly connected
- Updated:
  - `.note/finance/phase13/PHASE13_TEST_CHECKLIST.md`
- Practical result:
  - the checklist now follows the current UI reading order instead of the original Phase 13 first-pass layout

### 2026-04-07 - SPY MDD 수치 차이의 원인을 확인함

- Verified that the earlier `-15.9042%` figure was not raw daily `SPY` buy-and-hold drawdown.
- Confirmed with DB-backed price history:
  - raw daily `SPY` (`2016-01-04 ~ 2026-04-02`) `Maximum Drawdown = -33.72%`
  - month-end sampled `SPY` over the same broad window `Maximum Drawdown = -23.93%`
  - GTAA candidate benchmark surface (`2016-01-29 ~ 2026-04-02`, 42 rows, `interval = 3`) `Maximum Drawdown = -15.90%`
- Practical result:
  - the `-15.9%` value should be read as `GTAA internal quarterly-sampled benchmark MDD`, not as full daily `SPY` drawdown

### 2026-04-07 - Guides 페이지에 Promotion/Shortlist 승격 설명을 추가함

- Added a new Korean-first explainer section to `Guides` so users can understand:
  - `Promotion`
  - `Shortlist`
  - what must improve for those stages to move upward
- Also promoted `PHASE13_TEST_CHECKLIST.md` into the top recommended document list on the same page.
- Practical result:
  - users can now read the stage meanings and transition logic directly from `Guides` without opening the glossary first

### 2026-04-07 - Guides의 단계 상승 설명 탭을 더 읽기 쉽게 재구성함

- The `어떻게 다음 단계로 가나` tab previously rendered as one long markdown block and felt visually dense.
- Reworked the section into two side-by-side bordered cards:
  - `Promotion이 올라가려면`
  - `Shortlist가 올라가려면`
- Practical result:
  - transition conditions are now split into short steps instead of one merged paragraph-heavy list

### 2026-04-07 - Hold 해결 가이드와 Guides에 상태 위치/해결 액션 설명을 더 보강함

- Users still needed more direct guidance on:
  - where `caution / unavailable / error / warning` actually appear
  - what they should change to reduce each issue
- Updated:
  - `Real-Money > 현재 판단 > Hold 해결 가이드`
  - `Guides > 실전 승격 흐름 빠른 설명`
  - `.note/finance/phase13/PHASE13_TEST_CHECKLIST.md`
- Practical result:
  - hold guidance now shows `항목 / 현재 상태 / 상태를 보는 위치 / 이 상태의 뜻 / 바로 해볼 일`
  - guides now explain where each status is exposed and how to interpret it before changing settings

### 2026-04-07 - Guides 상태 위치 목록의 구분자를 더 명확히 정리함

- Adjusted the `상태는 어디에서 보나` list so the term and the UI path are separated with `:`.
- Practical result:
  - the scan pattern is now more consistent and easier to read at a glance

### 2026-04-07 - real-money gate 해석과 남은 개발 범위를 다시 정리함

- Revisited the current meaning of repeated `hold` / `watchlist` outcomes during Phase 12/13 backtest exploration.
- Clarified that:
  - repeated non-pass results do not automatically mean the framework is broken
  - but they can indicate that gate calibration analysis is now as important as more brute-force backtests
- Also clarified that:
  - `promotion / shortlist` passing is not the same thing as final live-investment readiness
  - additional deployment workflow and execution-readiness work still remains after the current Phase 13 surface

### 2026-04-07 - ETF guardrail surface를 OFF 상태도 보이도록 보강함

- During Phase 13 checklist QA, the user reported that `Underperformance Guardrail` / `Drawdown Guardrail` were not visible in `Real-Money > 실행 부담` or `Execution Context` for ETF strategies.
- Root cause:
  - the UI only rendered the section when the guardrail booleans were truthy
  - disabled ETF runs therefore looked as if the feature did not exist
- Updated:
  - ETF strategies now show the guardrail section even when disabled
  - `Execution Context` also shows guardrail state as `ON/OFF`
  - trigger count / trigger share stay visible with zero/default values when disabled

### 2026-04-07 - 전략 Advanced Inputs를 핵심 계약과 추가 계약으로 그룹화함

- The user pointed out that strategy `Advanced Inputs` were becoming too long and uneven as new overlay / real-money / guardrail controls were added.
- Updated:
  - single strategy ETF and strict annual forms now keep core execution inputs visible while grouping overlays, real-money contract, and guardrails into expanders
  - compare strategy-specific inputs were also regrouped for the same ETF and strict annual strategy families
- Durable implication:
  - future advanced options should be added to grouped sections instead of extending each form linearly

### 2026-04-07 - Quality family에서 Research variant를 active UI에서 제거함

- The user no longer wanted the broad `Quality Snapshot` research variant exposed in the `Quality` family because it is not being used in current workflow.
- Updated:
  - removed `Research` from the active `Quality` family variant list
  - kept the legacy `quality_snapshot` display-name mapping so older records still have a readable label
- Durable implication:
  - the active Quality family now starts at strict candidates only, which better matches the current backtest and QA workflow

### 2026-04-07 - Reference 그룹에 검색 가능한 Glossary 페이지를 추가함

- The user wanted a separate reference page, beyond `Guides`, where current quant-program terms could be browsed and searched more easily.
- Updated:
  - added `Reference > Glossary` page to the top navigation
  - the page now reads `.note/finance/FINANCE_TERM_GLOSSARY.md` directly and exposes title/body search
  - overview text, finance analysis doc, doc index, and Phase 13 checklist were aligned to the new page
- Practical result:
  - glossary remains single-source as Markdown, while the app now provides a searchable operator-facing reference UI

### 2026-04-08 - 저장소 README와 README 유지 지침을 추가함

- The user wanted a repository-level README that explains the current project surface on GitHub, plus a rule to keep it updated when features or workflows change.
- Updated:
  - created a root `README.md` that summarizes the finance-centered scope, current Finance Console pages, implemented ingestion/backtest surfaces, project layout, quick-start commands, and key reference docs
  - updated `AGENTS.md` so future work that changes the top-level product surface or startup/navigation flow must also review and update `README.md`
- Practical result:
  - the Git landing page now explains the project coherently, and README maintenance is now part of the durable workflow guidance

### 2026-04-09 - Guides와 glossary를 Phase 13 QA 피드백 기준으로 더 보강함

- The user needed clearer guidance on:
  - what `Watch / Caution / Unavailable / Error` actually mean
  - where `Hold 해결 가이드` really lives
  - how to interpret `Probation / Monitoring`, `Rolling / Out-of-Sample Review`, `Deployment Readiness`, and `Strategy Highlights`
- Updated:
  - `Guides > 실전 승격 흐름 빠른 설명` now includes richer status meaning rows plus explicit source paths for `Hold 해결 가이드` and compare-only `Strategy Highlights`
  - compare `Strategy Highlights` tab caption was clarified so users do not confuse it with single-run `Real-Money`
  - glossary now includes the missing operator-facing terms for probation, monitoring, rolling/OOS review, deployment checklist counts, and compare highlights
  - Phase 13 checklist and finance analysis doc were synced to the new UX wording
- Practical result:
  - users can now move from checklist -> guide -> actual result surface with much less ambiguity

### 2026-04-09 - Guides에 단계형 프로그램 사용 가이드를 추가함

- The user wanted a more practical "how to use this program for testing and commercialization review" guide in `Guides`, written as a numbered step flow.
- Updated:
  - added a new step-by-step operator runbook to `Guides`
  - the flow now covers:
    - ingestion refresh
    - single strategy baseline
    - real-money interpretation
    - hold blocker resolution
    - compare
    - history / backtest report handoff
    - probation / monitoring
    - final commercialization-candidate judgment
  - synced Phase 13 checklist, finance analysis doc, and README wording to the new guide
- Practical result:
  - users now have a single in-product path for "what do we do next?" from first refresh to paper probation / small-capital-trial interpretation

### 2026-04-09 - Phase 14 준비 문서를 열고 현재 상태를 갱신함

- The user wanted to close Phase 13 and prepare for Phase 14, while explicitly revisiting the previously deferred discussion about real-money gate calibration.
- Updated:
  - created Phase 14 plan doc:
    - `.note/finance/phase14/PHASE14_REAL_MONEY_GATE_CALIBRATION_AND_DEPLOYMENT_WORKFLOW_PLAN.md`
  - created Phase 14 TODO board:
    - `.note/finance/phase14/PHASE14_CURRENT_CHAPTER_TODO.md`
  - updated:
    - `.note/finance/MASTER_PHASE_ROADMAP.md`
    - `.note/finance/FINANCE_DOC_INDEX.md`
    - `app/web/streamlit_app.py` overview status metric
- Practical result:
  - Phase 14 is now opened as a real-money gate calibration and deployment-workflow-bridge phase instead of leaving the next direction implicit

### 2026-04-09 - Phase 14 gate blocker audit 문서를 representative rerun evidence 기준으로 보강함

- The existing Phase 14 first-pass audit already identified the high-level blocker families, but we wanted the document to reflect current rerun evidence instead of staying at a mostly report-derived summary.
- Updated:
  - re-ran a representative `9`-case set across:
    - strict annual `Quality / Value / Quality + Value`
    - ETF family `GTAA / Risk Parity Trend / Dual Momentum`
  - refreshed the audit doc with concrete outcome counts:
    - `real_money_candidate = 1`
    - `production_candidate = 2`
    - `hold = 6`
  - tightened the blocker distribution summary:
    - `validation_caution` dominated strict annual and ETF hold cases
    - `validation_policy_caution` repeated mainly in strict annual near-miss cases
    - `etf_operability_caution` concentrated in aggressive ETF candidates
- Durable implication:
  - the next Phase 14 workstream should focus on threshold inventory and calibration review, not on widening search space blindly
  - `rolling / out_of_sample` should be read as downstream deployment pressure more than a direct promotion gate because the current `Value` raw winner still reaches `real_money_candidate` with `rolling = watch`, `oos = caution`

### 2026-04-09 - Phase 14 calibration review first pass에서 factor 부족 가설을 분리함

- The user asked whether repeated `hold` outcomes might be happening simply because the current strategy families do not expose enough factors yet, and whether adding more factors plus broader backtests would be the right next move.
- Updated:
  - created:
    - `.note/finance/phase14/PHASE14_PROMOTION_SHORTLIST_CALIBRATION_REVIEW_FIRST_PASS.md`
  - documented the current threshold inventory that actually drives `promotion / shortlist`
  - separated two questions:
    - is the current gate too conservative?
    - is the current factor surface too narrow?
  - recorded the first-pass conclusion:
    - current repeated `hold` is more directly explained by `validation / validation_policy / ETF operability`
    - factor expansion is still valuable, but should follow calibration as a controlled search workstream
- Durable implication:
  - Phase 14 should now treat factor expansion as a later bounded experiment, not as the first lever to pull for every repeated `hold`

### 2026-04-09 - Phase 14 gate blocker audit first pass와 history gate snapshot persistence를 추가함

- The user wanted to start Phase 14 proper, and the first concrete workstream was the `real-money gate blocker audit`.
- Implemented:
  - reviewed current gate logic in `app/web/runtime/backtest.py`
  - documented a first-pass blocker audit at:
    - `.note/finance/phase14/PHASE14_GATE_BLOCKER_DISTRIBUTION_AUDIT_FIRST_PASS.md`
  - updated:
    - `.note/finance/phase14/PHASE14_CURRENT_CHAPTER_TODO.md`
    - `.note/finance/MASTER_PHASE_ROADMAP.md`
    - `.note/finance/FINANCE_DOC_INDEX.md`
    - `.note/finance/FINANCE_COMPREHENSIVE_ANALYSIS.md`
  - upgraded backtest history persistence to schema v2 so new records now store a compact `gate_snapshot`
    with promotion / shortlist / probation / monitoring / deployment / policy states
  - exposed that `gate_snapshot` in backtest history drilldown and added promotion / shortlist / deployment columns
- Practical result:
  - Phase 14 now has a documented first-pass answer for “what is actually blocking promotion?”
  - future blocker audits no longer need to depend only on phase report docs because new history records will carry gate status snapshots

### 2026-04-10 - Real-Money Contract 값 설명을 Guides와 Glossary에 보강함

- The user said they still did not have a clear mental model for what the values inside `Real-Money Contract` mean, why they are needed, and how they affect the result interpretation.
- Updated:
  - `app/web/streamlit_app.py`
    - added a new `Guides > Real-Money Contract 값 해설` section
    - organized it into common inputs / strict annual / ETF / reading order
  - `app/web/pages/backtest.py`
    - added a direct pointer from each `Real-Money Contract` form block to `Reference > Guides` and `Reference > Glossary`
  - `.note/finance/FINANCE_TERM_GLOSSARY.md`
    - added missing terms for benchmark contract and real-money threshold inputs
  - `.note/finance/FINANCE_COMPREHENSIVE_ANALYSIS.md`
    - synced the new operator-facing guide behavior
- Durable implication:
  - users can now learn the real-money contract in-app instead of having to infer it only from raw labels or result surfaces

### 2026-04-10 - strict annual 유동성 tooltip을 계산식과 해석 순서 중심으로 보강함

- The user wanted the small help bubble on the strict annual liquidity inputs to explain the actual calculation and interpretation flow more directly.
- Updated:
  - `app/web/pages/backtest.py`
    - `Min Avg Dollar Volume 20D ($M)` help text now explicitly says it uses OHLCV `close × volume` and a trailing 20-day average
    - `Min Liquidity Clean Coverage (%)` help text now explains the two-step contract:
      candidate-level liquidity screen first, then strategy-level clean coverage interpretation
- Durable implication:
  - operators can understand the strict annual liquidity contract directly from the field tooltip without jumping out to Guides first

### 2026-04-10 - strict annual robustness threshold tooltip에 rolling 구간 설명을 추가함

- The user then asked for the same tooltip-level explanation for:
  - `Max Underperformance Share`
  - `Min Worst Rolling Excess`
  - `Max Strategy Drawdown`
  - `Max Drawdown Gap vs Benchmark`
- Updated:
  - `app/web/pages/backtest.py`
    - expanded those help texts to explain the actual interpretation in plain language
    - added an inline caption that defines `rolling 구간` right under the robustness inputs
  - `.note/finance/FINANCE_TERM_GLOSSARY.md`
    - added `Rolling Window`
- Durable implication:
  - users can now understand the strict robustness thresholds at the point of input without having to infer what `rolling` means
