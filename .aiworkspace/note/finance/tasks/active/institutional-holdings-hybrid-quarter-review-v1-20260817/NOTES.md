# Institutional Holdings Hybrid Quarter Review V1 Notes

## Confirmed Facts

- 2026-08-17 local DB bulk dataset status remains `2026-march-april-may`; explicit hybrid refresh
  added twelve `2026-06-30` watchlist filing accessions through EDGAR fallback.
- SEC official bulk page still lists `2026 March April May 13F` as its newest dataset.
- Berkshire, Bridgewater and Duquesne already have `2026-06-30` 13F filings dated
  `2026-08-14` in SEC submissions data.
- Actual Q2 watchlist ledger contains 12 filings, including two notice-only `13F-NT`, and 1,640
  holding rows. Notice filings count as submitted but do not promote a holdings portfolio.
- Berkshire, Bridgewater and Duquesne now load both `2026-06-30` and `2026-03-31` effective
  quarters from local MySQL.
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
- Actual Berkshire final proxy evidence is +8.42% for quarter-end to quarter-end and +6.48% for
  filing-to-filing, each with 99.99% prior reported-value coverage. Final review replaced raw close
  with stored adjusted close and excludes non-common instruments.
