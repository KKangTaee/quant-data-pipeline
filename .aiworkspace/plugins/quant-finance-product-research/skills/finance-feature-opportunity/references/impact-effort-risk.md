# Impact Effort Risk Scoring

Use this scoring guide to keep feature recommendations comparable.

## Scores

Use 1 to 5 scores.

| Score | Impact | Effort | Risk | Confidence | Strategic Fit |
|---:|---|---|---|---|---|
| 1 | Small workflow polish | Tiny change | Low blast radius | Weak evidence | Weak fit |
| 3 | Meaningful workflow gain | Multi-file task | Manageable uncertainty | Moderate evidence | Clear fit |
| 5 | Core product improvement | Phase-sized work | High uncertainty or data risk | Strong evidence | Central fit |

## Suggested Priority Formula

Use judgment, but start from:

```text
priority = impact + strategic_fit + confidence - effort - risk
```

Then adjust for:

- whether the feature unblocks other work
- whether it reduces data correctness risk
- whether it clarifies a confusing user workflow
- whether it creates maintenance burden
- whether it conflicts with no-live-trading boundaries

## Candidate Buckets

- `Now`: high fit, evidence-backed, manageable scope
- `Next`: promising but needs dependency or narrower design
- `Later`: valuable but not urgent
- `Parking Lot`: interesting but weak fit, weak evidence, or boundary conflict

## Required Notes

Each candidate should name:

- implementation owner area
- affected UI or workflow
- affected data or registry boundary
- likely validation command or QA surface
- documentation that would need alignment
