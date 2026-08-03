# Notes

## 2026-08-04 Diagnosis

- Latest manual refresh: success, 96.836 seconds, 17 requested/processed, 0 failed.
- Current month-end observed phase: contraction.
- Current transition anchor/target: recovery -> expansion.
- Transition conditions: 0/3, WATCH, non-adjacent observation.
- `confirmed_at` is current-release-only and cannot identify the active anchor's date.
- Current ribbon has phase colors but only one generic model legend and native title tooltip.
- Current quadrant renders 12 points and labels 6M/3M/current.

## 2026-08-04 Implementation Result

- Active transition anchors now retain start/source/confirmation provenance for new snapshots.
- Legacy snapshots recover a confirmed anchor date when possible; otherwise they use the explicit
  `조회 이력 내 최초 관측` fallback instead of claiming an exact confirmation date.
- Freshness keeps the calculation cutoff distinct from the latest source observation and last
  successful collection check.
- The chart keeps the monthly observed path but emphasizes only 6M, 3M, 1M and current labels.
- A non-adjacent current observation points to its own structural adjacent phase. In the verified
  contraction case the arrow points to recovery, while recovery -> expansion remains the anchor
  condition route and is explicitly labeled as non-forecast.
- Ribbon tooltip content includes Korean month, phase, NBER context, confidence and revision
  sensitivity and is available by hover or keyboard focus.
- `자산별 확인 포인트` was not edited.
