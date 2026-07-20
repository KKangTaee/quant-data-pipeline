# Overview Sentiment Long History And Point-In-Time Capture V2 Design

Date: 2026-07-20
Status: Approved

## Why This Change

Overview Sentiment currently answers the present-tense CNN and AAII question well, but its stored history cannot yet support trustworthy historical replay.

- The UI requests only the latest 180 calendar days, so the chart appears to be a continuously rolling six-month view even when the canonical DB contains older dates.
- `macro_series_observation` preserves distinct observation dates, but its unique key is `(series_id, observation_date, source)`. A refresh overwrites the value, metadata, and `collected_at` for an already stored date.
- CNN provides a rolling headline history, while its seven components provide only their current values. Component history therefore begins only when this application captures it.
- AAII currently provides a bounded weekly table. Repeated refreshes can extend the canonical date range as older provider rows roll off, but they do not preserve what the provider response looked like on each collection date.

This stage must begin preserving what the application actually observed at each collection time. That foundation is required before any one-week or one-month sentiment outlook can be evaluated without future-data leakage.

## Audit Baseline

The read-only audit on 2026-07-20 found:

| Data | Canonical DB coverage | Current provider response | Continuity |
|---|---:|---:|---|
| CNN headline | 282 rows, 2025-06-04 to 2026-07-17 | about 250 headline rows, 2025-07-21 to 2026-07-17 | no gap above four calendar days |
| AAII four series | 28 weekly rows per series, 2026-01-07 to 2026-07-15 | 21 weekly rows per series | exact seven-day Wednesday cadence |
| CNN components | 23-24 rows per component, 2026-06-04 to 2026-07-17 | one current row per component | only application capture dates are available |

Every overlapping CNN headline and AAII row matched the current provider response at audit time. However, every overlapping canonical row had been updated by a later refresh, and the previous values and previous collection timestamps were no longer recoverable.

The run history contained 57 successful collections across 23 distinct days from 2026-06-06 through 2026-07-20. The current Overview automation registry does not own market sentiment collection; refreshes are initiated from the Overview or Ingestion UI and Data Health only evaluates a 24-hour freshness target.

These counts are an audit snapshot, not permanent product constants.

## User-Facing Vocabulary

Use `수집 당시 기록` in user-facing Korean copy. Avoid exposing `ledger` or `원장` unless discussing the internal implementation.

- `현재 화면용 이력`: the latest provider view stored in `macro_series_observation`
- `수집 당시 기록`: an immutable normalized snapshot of the values observed in one source response
- `known_at`: the UTC time when this application successfully observed the source response
- `PIT 축적 시작일`: the first trustworthy `known_at` stored by the new capture path

`known_at` is not claimed to be the provider's exact publication time. It is a conservative statement that the application knew the value no later than its successful collection time.

## Goals

1. Preserve every normalized CNN and AAII source view without overwriting earlier captures.
2. Keep the current fast canonical table and all existing Overview behavior compatible.
3. Provide a deterministic loader for “what values had this application observed by this time?”
4. Add a reliable daily capture path while preserving manual refresh.
5. Let users switch the charts between 6M, 1Y, and all stored canonical history.
6. Show compact, decision-relevant coverage evidence rather than a run-oriented diagnostics panel.
7. Keep one-week and one-month outlook publication blocked until a later chronological validation gate is defined and passed.

## Non-Goals

- Reconstructing publication-time snapshots that were never captured
- Claiming the legacy canonical rows are historical point-in-time truth
- Adding CFTC, Cboe, FRED, or another sentiment provider
- Publishing a one-week or one-month forecast or probability
- Turning collection batches, job counts, or stored-row counts into the primary UI
- Changing CNN or AAII classification thresholds
- Combining CNN and AAII into a synthetic score
- Adding a trading, validation, monitoring, or portfolio action signal

## Recommended Architecture: Dual Store

Keep two stores with separate responsibilities.

```text
CNN / AAII response
    -> source capture batch
       -> append normalized values to immutable capture history
       -> UPSERT the same normalized values into canonical latest history
       -> mark the source batch complete
```

### Canonical latest history

`finance_meta.macro_series_observation` remains the source for the current Overview cards and the visible chart.

- Existing loaders and current-value semantics remain compatible.
- Distinct observation dates continue to accumulate as provider rolling windows move forward.
- Revisions continue to update the canonical latest view.
- The table is not used by future chronological validation as publication-time truth.

### Source capture batch

Add `finance_meta.market_sentiment_collection_batch`, with one row per source attempt. A top-level collection that requests CNN and AAII therefore creates two source batches linked by one `collection_id`.

Required contract:

- `batch_id`: stable UUID for an individual source attempt
- `collection_id`: stable UUID grouping source attempts from one job invocation
- `source`, `source_ref`, `schema_version`
- `status`: `success`, `partial`, `missing`, or `error`
- `requested_at`, `observed_at`, and `completed_at` in UTC
- normalized observation-date minimum and maximum
- normalized row count and expected-series coverage metadata
- bounded error text for unsuccessful captures
- created and updated timestamps

Index source/time/status and collection ID. Do not require a user-facing operations panel for this table.

### Immutable normalized capture history

Add `finance_meta.market_sentiment_observation_snapshot`.

Each row stores the normalized observation as it appeared in one successful or partial source response:

- `batch_id`, `collection_id`
- `series_id`, `observation_date`, `source`
- `source_type`, `source_mode`, `source_ref`
- `series_name`, `category`, `frequency`, `units`
- `value`, `release_lag_days`, `coverage_status`
- existing compact metadata JSON, including CNN rating when available
- `observed_at` as the `known_at` boundary
- bounded error text, created timestamp

Use `(batch_id, series_id, observation_date, source)` as the idempotency key. Deduplicate duplicate normalized keys inside a single response before writing. Rows from different batches are intentionally retained even when their values are identical.

Index `(series_id, source, observed_at, observation_date)` and `batch_id`. Retention is indefinite for this stage; the expected normalized volume is small enough that a time-based purge is unnecessary.

Do not store full raw provider responses in this stage. The normalized source view, source reference, metadata, and capture boundary are sufficient for the required replay contract and avoid creating an unbounded raw-payload archive.

## Collection And Transaction Contract

### Source-owned capture time

Generate one UTC `observed_at` for each successfully received source response and pass that exact timestamp to every normalized row from the response. Do not infer a release timestamp from the observation date.

### Source isolation

CNN and AAII are independent transaction units.

1. Fetch and normalize one source.
2. Validate required series coverage and deduplicate the response.
3. Begin a DB transaction.
4. Insert the source batch and immutable snapshot rows.
5. UPSERT canonical latest rows.
6. Mark the batch `success` or `partial` and commit.

If steps 4-5 fail, roll back that source transaction so capture and canonical history cannot disagree. Then record a bounded error batch in a separate transaction. A CNN failure must not roll back a successfully persisted AAII source, and vice versa.

### Job compatibility

Keep the existing `collect_market_sentiment` job name, refresh actions, and primary `rows_written` behavior compatible. Add capture counts and batch IDs under job details instead of changing the existing UI contract unexpectedly.

Update the Ingestion action registry target tables to list all three persistence targets.

### Existing data boundary

Do not fabricate pre-feature capture timestamps and do not copy legacy canonical rows into the immutable table as if they were historical snapshots.

The first successful new source capture may contain older observation dates from the provider's rolling response. Those rows become known only at that first `observed_at`. Therefore:

- canonical charts may still show all existing stored dates;
- point-in-time queries before the first capture return no new capture data;
- UI copy reports the actual PIT accumulation start separately from the visible canonical chart range.

## Automation Contract

Add market sentiment to the Overview automation registry with a 24-hour cadence.

- Preferred scheduled execution is after the US market close.
- `market_hours_only` remains false because AAII is weekly and browser/session catch-up may occur outside market hours.
- Safe, standard, broad, and browser-safe profiles may run the lightweight capture when due.
- Manual Overview and Ingestion refreshes remain available and create their own source batches.
- Multiple captures on the same date are valid because `observed_at` distinguishes what was seen at each time.

The actual capture timestamp, not an assumed schedule time, is authoritative. Deployment scheduling guidance belongs in the existing Overview Market Intelligence runbook.

## Point-In-Time Loader Contract

Add a loader dedicated to immutable history rather than extending the canonical loader with ambiguous flags.

Conceptual interface:

```python
load_market_sentiment_as_known(
    *,
    known_at: str,
    series_ids: Iterable[str] | None = None,
    observation_start: str | None = None,
    observation_end: str | None = None,
) -> pd.DataFrame
```

For each `(series_id, observation_date, source)`, return the latest snapshot whose `observed_at <= known_at`. Default `observation_end` to the date portion of `known_at` so a future-dated observation cannot enter the result accidentally.

Tie-break identical `observed_at` values deterministically by snapshot ID. Return `observed_at`, `batch_id`, and source metadata so later validation can prove provenance.

Keep `load_market_sentiment_history()` on the canonical latest table for current charts. Callers must choose the loader that matches their question rather than receiving silently mixed semantics.

## Overview Chart And Coverage Design

### Period control

The History section gets one shared period selector that applies to both visible chart panels:

- `6M` default
- `1Y`
- `전체`

Load the available canonical history once and filter presentation points in the React component. Preserve the existing 180-day window for “recent range” analysis and current interpretation so choosing `전체` does not silently redefine percentile or direction semantics.

### Insufficient range

Do not render an empty chart merely because the selected period is longer than stored coverage. Render every available point and state the actual range, for example `현재 저장 범위 28주`.

### Compact evidence

Near the History heading or chart metadata, expose only decision-relevant coverage:

- available canonical date range and observation count for the active source
- latest successful capture time
- PIT accumulation start date
- material gap status
- CNN component note: `수집 시작 이후 현재값을 축적 중`

Do not add a refresh-job result panel, batch table, failed-row dashboard, or raw operational status surface. Existing Data Health and the raw evidence disclosure remain the supporting diagnostic paths.

### Current two-chart layout

Keep the approved structure:

- row 1: CNN headline chart
- row 2: one AAII chart with `AAII 응답` and `AAII Spread` switching
- straight point-to-point lines and edge-safe tooltips

## Data Quality Contract

Compute source quality from stored facts rather than hard-coded claims.

- canonical start/end and distinct observation count
- first and latest immutable `observed_at`
- latest successful or partial source batch
- expected cadence gaps: business-day-aware CNN headline and seven-day AAII cadence
- component history marked as prospective capture-only
- source response coverage for required CNN headline, seven CNN components, and four AAII series

Do not define an arbitrary “forecast ready” sample threshold in this stage. Stage 2-5 will inspect accumulated PIT history, define targets and chronological splits, and decide whether validation is possible.

## Error And Edge Cases

- Missing schema: existing current loaders still return their established empty frames; the new PIT loader returns an empty typed frame.
- Source blocked or malformed: store a bounded error batch without snapshot rows; do not alter valid canonical rows.
- Partial source response: persist available rows, mark the batch partial, and preserve existing missing-source warnings.
- Duplicate manual click or job retry: each new request has a new collection ID; retrying the same batch ID is idempotent.
- Same value in repeated batches: retain both capture views because successful observation time is evidence.
- Revised past value: retain old and new snapshot rows; canonical history shows the newest view.
- No PIT history yet: show `PIT 축적 시작 전` rather than implying a failure or backfilled truth.
- Provider history shrinks: do not delete canonical dates or immutable snapshots that are absent from a later rolling response.

## File Ownership

Expected implementation ownership:

- `finance/data/db/schema.py`: two new table schemas and schema synchronization contract
- `finance/data/sentiment.py`: collection IDs, response deduplication, source transaction, immutable writes, canonical UPSERT
- `finance/loaders/sentiment.py`: as-known and compact capture-summary loaders
- `app/jobs/ingestion_jobs.py`: compatible job detail expansion
- `app/jobs/overview_automation.py`: 24-hour sentiment automation spec
- `app/web/ingestion/registry.py`: three target tables
- `app/services/overview/sentiment.py`: full canonical chart history, fixed recent-analysis window, coverage read model
- `app/web/overview/sentiment_helpers.py`: period/coverage payload fields
- `app/web/streamlit_components/sentiment_workbench/src/`: shared period control and coverage presentation
- `tests/test_service_contracts.py` and focused frontend tests: regression and PIT contracts
- `.aiworkspace/note/finance/docs/runbooks/OVERVIEW_MARKET_INTELLIGENCE.md`: daily capture and recovery guidance

The exact helper split may change during implementation, but DB, loader, service, and React ownership must remain separated.

## Test Strategy

### Schema and ingestion

- New tables expose the approved keys and indexes.
- One successful source response writes one batch, all immutable snapshots, and canonical rows.
- A second response revising the same observation preserves both snapshots and updates only the canonical row.
- Identical repeated responses remain separate capture batches.
- Retrying one batch ID does not duplicate snapshots.
- A write failure rolls back both immutable and canonical writes for that source.
- CNN failure does not prevent AAII commit, and vice versa.
- A later rolling response never deletes older canonical or snapshot rows.

### Loader

- A cutoff before first capture returns no PIT rows.
- A cutoff between two revisions returns the first observed value.
- A later cutoff returns the revision.
- Default observation end blocks future-dated observations.
- Missing-table behavior returns a typed empty frame.

### Service and payload

- Current interpretation continues to use a fixed 180-day recent-analysis window.
- Full canonical history is available for chart period filtering.
- Coverage metadata distinguishes canonical range from PIT accumulation start.
- CNN component history is labeled prospective capture-only.
- Existing CNN/AAII cross-read, badge, chart, tooltip, and forecast-unavailable contracts remain unchanged.

### Frontend and Browser QA

- `6M`, `1Y`, and `전체` filter both chart panels to the same date horizon.
- Default remains `6M`.
- Insufficient coverage reports the actual available range and still renders points.
- Existing AAII tab keyboard interaction and chart tooltip behavior remain intact.
- Desktop and 420px views have no horizontal overflow.
- A QA screenshot is produced as an uncommitted generated artifact.

## Delivery Stages

This is stage 2 of the overall four-stage Sentiment roadmap.

1. **2-1 audit — complete:** provider window, canonical coverage, gaps, overwrite behavior, and collection ownership
2. **2-2 storage contract — approved by this design:** dual store, source batch, immutable normalized capture, as-known semantics
3. **2-3 implementation:** schema, source transaction, loader, daily automation, regression tests
4. **2-4 product evidence:** period selector, compact coverage evidence, long-chart QA and runbook alignment
5. **2-5 readiness decision:** inspect accumulated PIT history and specify whether 1W/1M validation can begin

Stage 2 completion does not mean a forecast is available. Overall roadmap stages 3 and 4 remain conditional.

## Acceptance Criteria

- Re-collecting the same observation date never destroys an earlier captured value.
- Current Overview cards and the canonical default chart remain compatible.
- A caller can reproduce the latest value known by an explicit UTC cutoff.
- Daily and manual collection both use the same immutable path.
- Users can view 6M, 1Y, or all available canonical history and understand the actual stored range.
- The UI distinguishes canonical chart coverage from PIT accumulation start without surfacing a run-centric dashboard.
- No historical capture is claimed before the application actually observed it.
- No 1W/1M probability or trading signal is published in this stage.
