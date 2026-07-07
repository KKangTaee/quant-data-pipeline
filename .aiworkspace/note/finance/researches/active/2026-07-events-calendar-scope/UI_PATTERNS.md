# UI Patterns

## Brief First

The first screen should answer:

- What is the next major market event?
- What is happening today, this week, and in the next 30 days?
- Which events are official vs estimated?
- Which estimated earnings dates are stale or not confirmed?
- What source freshness is the brief based on?

## Event Rails

Recommended rails:

- Recent major.
- Today.
- This week.
- Next 30 days.
- Later.

Each row should carry event type, source authority, confirmation state, and stale/review badges.

## Calendar and Density

Calendar and chart views should show event density and evidence quality:

- Monthly grid with per-day counts by event family.
- Weekly density chart for clustering.
- Hover detail with date, event families, count, top titles, stale count, and review count.

The chart should not encode signal, bullish/bearish meaning, or action recommendations.

## Evidence Placement

Raw rows, URLs, confidence, collected_at, and raw payload fields remain available but should live in a lower evidence section. The product should not make raw tables the main reading path.

