# Overview Sentiment Aligned Start And Latest End Design

Date: 2026-07-20
Status: Approved by user request

## Why This Change

The first common-period implementation used the intersection of both source ranges for both the start and end. That made the charts comparable, but it also hid CNN observations newer than AAII's weekly release. In the actual 2026-07-20 screen, the current CNN card showed `37.1` for `2026-07-20` while the CNN history chart stopped at `41.2` for `2026-07-16`.

## Approved Contract

- Align the chart start to the later of the two source start dates.
- Set the shared x-axis end to the later of the two source end dates.
- Filter each source only to that shared display window.
- Do not forward-fill, interpolate, or extend a source beyond its own latest observation.
- Keep both panels on the same x-domain so dates remain directly comparable.
- Rename the payload field from `common` to `aligned` because the end is no longer a strict intersection.
- Rename user-facing `공통 전체` to `전체` and `비교 구간` to `정렬 구간`.

With the current data, the aligned display range is `2025-06-04~2026-07-20`. CNN ends at `2026-07-20` with `37.1`; AAII ends at `2026-07-16` and its line visibly stops there.

## Edge Case

The aligned range is unavailable when the later source start is after the earlier source end. This ensures the chosen start still represents a date from which both sources have at least one observation. When overlap exists, the end may extend beyond one source's latest date by design.

## Files

- `app/services/overview/sentiment.py`: calculate aligned coverage.
- `app/web/overview/sentiment_helpers.py`: serialize `history_coverage.aligned`.
- `app/web/streamlit_components/sentiment_workbench/src/SentimentWorkbench.tsx`: rename the payload type.
- `app/web/streamlit_components/sentiment_workbench/src/SentimentHistorySection.tsx`: build the shared period from aligned coverage and update copy.
- `tests/test_service_contracts.py`: lock the backend, payload, and React contracts.

## Verification

- A focused service test proves start=`max(starts)` and end=`max(ends)` when overlap exists.
- A no-overlap test keeps the aligned range unavailable.
- React source contracts prove both chart panels use one aligned extent.
- The Streamlit component production build must pass.

