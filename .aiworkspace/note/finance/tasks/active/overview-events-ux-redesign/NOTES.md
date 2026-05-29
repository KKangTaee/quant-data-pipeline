# Notes

- This is a UI/readability pass only. The event source of truth remains `finance_meta.market_event_calendar`.
- Source lane status is derived from the currently loaded rows and respects the selected Type filter: missing selected source rows show `Missing`, rows requiring validation/source action show `Review`, otherwise source blocks show `OK`.
- `Agenda` is the default interpretation layer for upcoming events; `Quality` is where estimate-only, not-confirmed, stale, or action-required rows are grouped.
