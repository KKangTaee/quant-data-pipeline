# Institutional Holdings Hybrid Quarter Review V1 Notes

## Confirmed Facts

- 2026-08-17 local DB dataset: `2026-march-april-may`; selected watchlist managers are
  generally report period `2026-03-31` with filing date `2026-05-15`.
- SEC official bulk page still lists `2026 March April May 13F` as its newest dataset.
- Berkshire, Bridgewater and Duquesne already have `2026-06-30` 13F filings dated
  `2026-08-14` in SEC submissions data.
- Existing raw filing/holding tables preserve accession/report period and can support historical
  comparison, but the local DB currently lacks the prior watchlist quarter needed by the existing
  comparison path.
- Current `is_stale` means a collection succeeded and has usable rows; it does not compare the
  stored report period with a calendar/latest SEC period.

## User Decisions

- Use a hybrid source: individual EDGAR for early watchlist availability and SEC bulk ZIP for
  later full reconciliation.
- Do not make live external checks when the tab opens.
- Show an update action from local report-period/due-date logic and call SEC only after click.
- Display both quarter-end and filing-to-filing performance proxy windows.
- Add `NEW / ADD / KEEP / REDUCE / DROP`; retain `REDUCE` and `NEW` even though the initial user
  examples mentioned keep/add/drop.

## Terminology

- A filing submitted in August 2026 with `period_of_report=2026-06-30` is the 2026 Q2 portfolio.
- The 2026 Q3 portfolio has report period `2026-09-30` and is due in November 2026; it is not
  available in August 2026.
- “Performance” in this task always means a reported-long-holdings price proxy unless explicitly
  qualified otherwise.
