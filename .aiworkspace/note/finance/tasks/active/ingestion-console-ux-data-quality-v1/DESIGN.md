# Ingestion Console UX / Data Quality V1 Design

## Current Findings

- Main UI owner: `app/web/streamlit_app.py`
- Job wrapper owner: `app/jobs/ingestion_jobs.py`
- Existing Ingestion grouping is `Operational Pipelines` / `Manual Jobs / Inspection`.
- Hidden-but-implemented lifecycle wrappers exist in `app/jobs/ingestion_jobs.py`:
  - `run_collect_symbol_directory_snapshots`
  - `run_collect_sec_company_ticker_crosscheck`
  - `run_collect_computed_snapshot_lifecycle`
- Current dispatch in `app/web/streamlit_app.py` does not route those lifecycle wrappers.
- Data docs already distinguish current listing snapshot, Form 25 delisting evidence, and computed partial lifecycle evidence.

## Implementation Direction

- Add a small job metadata catalog in `streamlit_app.py`.
  - User-facing Korean title
  - Internal job id
  - purpose
  - target tables
  - downstream use
  - data quality caveats
  - recommended next action
- Render this metadata in job cards and result summary.
- Rename top-level tabs to user-oriented Korean labels while preserving existing internal action names.
- Add lifecycle evidence sub-tabs under Practical Validation / evidence data collection.
- Wire dispatch for the three existing lifecycle job wrappers.
- Keep raw result JSON, artifacts, logs, and failure CSV in collapsed / right-side operational detail areas.

## Data Quality Notes To Surface

- OHLCV: provider no-data, rate limit, stale / sparse response, requested window coverage risk.
- Broad fundamentals / factors: research convenience layer, not strict filing-time PIT.
- Financial statements: `period_end` and `available_at` must be interpreted separately.
- ETF provider snapshots: current snapshot, not historical PIT holdings / operability truth.
- FRED macro: observation-date data, not ALFRED vintage PIT.
- Lifecycle: current listing snapshots and computed partial rows are not survivorship PASS proof.
- Earnings: free-provider estimates are not official confirmed dates.

## Files Expected To Change

- `app/web/streamlit_app.py`
- `.aiworkspace/note/finance/tasks/active/ingestion-console-ux-data-quality-v1/*`
- root handoff logs and possibly durable docs after implementation
