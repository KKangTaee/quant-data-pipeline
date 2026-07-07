# Risks

## Data Quality

- Earnings dates are often estimates before company confirmation.
- Provider calendars may disagree or may derive dates algorithmically from history.
- Official sources use different file formats: HTML, PDF, XLSX, and sometimes JavaScript-rendered pages.
- Release time and timezone must be normalized; date-only storage is not enough for major macro events.

## Product Risk

- Expanding coverage can make the Events tab noisy unless the UI separates macro, earnings, market structure, and raw evidence.
- Event density can be misread as a signal. Copy and chart labels must keep the context-only boundary explicit.
- Corporate actions and investor events may require paid or licensed sources for reliable coverage.

## Implementation Risk

- Existing `market_event_calendar` can likely store many categories, but richer fields may require schema or payload extension.
- React should render only service-owned structured payload. New event explanations should live in Python read models.
- Refresh UI must not become an operations dashboard; freshness should explain why a collection update is useful.

