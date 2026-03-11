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
