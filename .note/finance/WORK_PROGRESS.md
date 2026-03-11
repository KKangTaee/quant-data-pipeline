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
