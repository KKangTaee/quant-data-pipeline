# Notes

## 2026-08-17 진단 기준값

- official observed state: recovery, as_of 2026-07-31, duration 7 months.
- level -0.32564, 3-month momentum +0.07483.
- recent composite: 1m -0.02438 with 0/4 improving; 3m +0.07483 with 2/4; 6m +0.27454 with 3/4.
- transition pressure: 63.59% in next 3 usable releases.
- conditional destination: contraction 69.72%, expansion 23.93%, slowdown 6.36%.
- confirmed ribbon: 2025-08~2025-12 contraction, 2026-01~2026-07 recovery.

## 핵심 원인

- freshness owner mismatch: official RTDSM current snapshot vs legacy intramonth weekday comparison.
- React collecting state reset omission.
- production current evidence vs preserved legacy asset evidence mismatch.
- missing RTDSM quality metadata and hard-coded UI denominator 8.
- quarterly RUC threshold 120 days makes a 121-day normal cadence look stale.

