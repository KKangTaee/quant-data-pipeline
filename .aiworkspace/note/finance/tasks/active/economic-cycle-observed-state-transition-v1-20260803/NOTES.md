# Economic Cycle Observed State / Transition V1 Notes

Last Updated: 2026-08-03

## Durable Decisions

- Past sessions and existing economic-cycle research conclusions were not used as authority.
  The audit was rebuilt from current code, DB rows, tests and official primary references.
- Current phase is a deterministic relative growth-cycle quadrant, not an h0 probability
  argmax and not an NBER recession determination.
- Public phase vocabulary is recovery / expansion / slowdown / contraction, rendered as
  회복 / 확장 / 둔화 / 위축.
- Future 1M / 2M probability cards and future graph points are removed from the product.
- Future information is expressed as adjacent-phase conditions and status, not a target date.
- Latest comparable month-end remains headline authority. Intramonth data is provisional.
- Asset checkpoints are a frozen downstream surface. No redesign is authorized.
- Headline phase is the immediately observed quadrant. Transition confirmation keeps a separate
  last-confirmed anchor so a first boundary crossing can be shown immediately without being
  called a confirmed regime change.
- The v3 service has no `forecast_path_json` or `probabilities_json` read path. Legacy rows with
  no observed-state JSON remain limited instead of reconstructing a phase from h0 probability.
- The v3 cycle map is a maximum 12-month trail of persisted actual level/momentum coordinates;
  the current snapshot replaces a same-date history point so headline and graph cannot diverge.
- Market implications receive the same evidence, market, price, earnings and reference-date
  inputs as before. Their unused legacy horizon argument is now an empty tuple, verified by
  deep-equality regression.

## Reproduced Root Causes

- 2026-06-30 rule quadrant was contraction while stored/displayed h0 dominant phase was
  recovery at 46.7%.
- Stored replay comparison found 42 mismatches in 121 months between the deterministic label
  and stored current model output.
- Current artifact h1 / h2 validation did not beat required baselines consistently; h2 was
  worse than historical transition on both Brier and log loss.
- UI probability coordinates were not actual level / momentum coordinates.
- USREC override kept some strong 2020-2021 recovery months labeled recession until NBER
  announcement status changed.
- h0 feature coverage counted forecast-only inputs that h0 did not use.

## Candidate Comparison

- Raw monthly: 345 transitions, 82 one-month flipbacks, median run 1 month.
- 3M-smoothed: 249 transitions, 32 one-month flipbacks, median run 3 months.
- 3M-smoothed plus two-release confirmation: 168 transitions, zero one-month flipbacks,
  median run 4 months.
- 6M-smoothed reduced revision mismatch further but added unacceptable lag relative to the
  user's concern about conservative diagnosis.

## Current Data Illustration

For 2026-06-30 under the approved candidate:

- 3M-smoothed level: approximately -0.561
- momentum: approximately -0.239
- observed quadrant: contraction / 위축
- level and momentum breadth: both mixed near 50%
- resulting presentation: 위축 유지, 회복 조건 관찰; confidence is not high

The values above are a design-time reproduction, not a hard-coded UI fixture.

## Approval Record

- User approved proceeding with relative growth-cycle and separate NBER reference.
- User approved the recommended decision-centered screen structure.
- User explicitly confirmed twice that `자산별 확인 포인트` must retain the current design.
- User authorized continuing the work after the scope was restated.
