# Notes

## Discovery

- Local service call showed `as_of_date=2026-06-18` returns `requested_as_of=2026-06-18` but `current_as_of=2026-05-29`.
- Coverage showed XLB rows through 2026-06-18, while SPY / QQQ / GLD / TLT / IWM / HYG / LQD rows ended at 2026-05-29. The common price matrix therefore ended at 2026-05-29.
- Direct `as_of_date=2026-05-29` changed leadership sector / proxy to Technology / XLK, confirming selected dates can change when the effective data boundary supports them.

## Boundaries

- Historical analog remains context-only and DB-backed.
- Macro-conditioned comparison remains a narrowing layer over broad anchors, not a separate prediction model or trading signal.
- The UI still uses current universe / sector metadata for selected-as-of replay. It now makes the data basis clearer but does not solve full PIT sector classification.
- FRED / Events / Sentiment remain preview / annotation / deferred dimensions, not hard filters.
