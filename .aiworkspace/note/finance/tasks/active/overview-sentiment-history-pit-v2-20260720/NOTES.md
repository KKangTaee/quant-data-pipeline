# Notes

## 2026-07-20 Read-Only Audit

- CNN headline canonical DB: 282 rows, 2025-06-04~2026-07-17, weekday continuity, maximum calendar gap 4 days.
- CNN current provider response: about 250 headline observations over roughly one rolling year plus one current row for each of seven components.
- AAII canonical DB: 28 Wednesday observations per series, 2026-01-07~2026-07-15, exact seven-day cadence.
- AAII current provider response: 21 weekly observations per series.
- CNN components: 23~24 canonical rows per series since 2026-06-04; provider supplies only one current component row per response.
- Provider/current-DB overlap: 332/332 rows matched at audit time.
- All overlapping canonical rows had later `updated_at` and latest `collected_at`; previous captured values/timestamps were overwritten and cannot be recovered.
- Run history: 57 successful collections across 23 distinct days from 2026-06-06 through 2026-07-20, with up to seven runs on one day and no execution-mode provenance on those legacy rows.
- `build_market_sentiment_snapshot(max_history_days=180)` explicitly limits the visible history query to the latest 180 calendar days.
- `overview_automation.py` has no market sentiment job spec; Data Health only sets a 24-hour cadence target.

## Decisions

- User priority: maximize trustworthy PIT accumulation from now rather than claim reconstructed historical publication snapshots.
- Store normalized capture views, not full raw payload archives.
- Retain repeated identical source captures because observation time itself is provenance.
- Do not migrate legacy canonical rows into the immutable table with fabricated earlier timestamps.
- Use `수집 당시 기록` in product copy instead of `원장`.
