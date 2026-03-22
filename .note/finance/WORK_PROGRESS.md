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
  - existing labels/values tables received the new point-in-time columns
  - AAPL annual rows store `period_end=2025-09-27`, filing `2025-10-31`, acceptance `2025-10-31 06:01:26`
  - MSFT annual rows store `period_end=2025-06-30`, filing `2025-07-30`, acceptance `2025-07-30 20:11:40`
- Confirmed a known raw-provider behavior during quarterly verification:
  - comparative rows inside a 10-Q can carry the filing's `fiscal_period` context even when the row `period_end` is an earlier quarter
  - downstream loaders should treat `period_end` and `accession_no` as the primary row identity, not `fiscal_period` alone
- Reviewed the new detailed-statement point-in-time design and recorded the next patch priorities:
  - conservative `available_at` fallback
  - non-null/stable raw value identity for unique keys
  - summary-only positioning for the labels table unless concept-level identity is introduced
- Added a dedicated review-and-patch-plan note for the new detailed-statement point-in-time schema.
- Created the next PHASE2 chapter TODO board for point-in-time hardening work.
- Completed the first hardening patch by changing `_available_at_from_dates(...)` to use a conservative end-of-day fallback when only `filing_date` is available.
- Verified locally with the project virtualenv that:
  - `filing_date`-only rows now fall back to `23:59:59`
  - rows with `accepted_at` still preserve the accepted timestamp
- Audited the current `nyse_financial_statement_values` table for raw-identity readiness and found it is still in a mixed state:
  - 303,054 total rows
  - 302,712 rows missing `accession_no`
  - 302,712 rows missing `unit`
  - only 342 rows currently carry accession-based raw identity, across 2 symbols
- Recorded the resulting policy decision:
  - new raw-path rows should move toward strict accession-based identity
  - legacy rows should not be assumed strict-PIT-ready until backfilled or rebuilt
- Verified on representative raw EDGAR sources (`AAPL`, `MSFT`, `JPM`) that statement facts currently carry both `accession` and `unit` consistently.
- Added an ingestion-side identity guard so the new PIT raw path skips value rows that do not have both `accession_no` and `unit`.
- Re-ran quarterly detailed-statement ingestion for `AAPL` and verified that accession-bearing raw rows remain stable:
  - 139 accession-based quarterly rows before rerun
  - 139 accession-based quarterly rows after rerun
  - 0 duplicate groups under `(symbol, freq, accession_no, statement_type, concept, period_end, unit)`
- Added a dedicated strategy note for how to move from the current mixed-state table toward stricter PIT behavior:
  - keep ingestion guards
  - use accession-bearing rows for strict loaders
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
