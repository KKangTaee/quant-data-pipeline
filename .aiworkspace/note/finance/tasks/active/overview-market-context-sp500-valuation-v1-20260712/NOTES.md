# Overview Market Context S&P 500 Valuation V1 Notes

Status: Active
Last Updated: 2026-07-12

## Confirmed Decisions

- Exactly two primary valuation surfaces.
- Five-year/60-month log(PER) distribution is the official regime window.
- Three-year/36-month result is sensitivity evidence only.
- EPS basis should remain As-Reported across historical and current calculations.
- SPX owns valuation math; SPY is a same-date proportional conversion.
- FOMC SEP economic projections, not the interest-rate dots themselves, own GDP/PCE inputs.
- New SEP releases must be discovered and stored by vintage.
- Old Market Context visible UI must be removed.
- New visible UI must use React in the same product style as other React-backed Overview surfaces.

## Source Findings

- Shiller provides monthly price, earnings, CAPE, CPI, and 10-year rate research data.
- Shiller monthly earnings are interpolated from S&P quarterly four-quarter totals and are not strict PIT release-vintage proof.
- S&P Index Earnings exposes index earnings/estimates but automated workbook access may be restricted.
- LSEG I/B/E/S supports index aggregates and deep historical forward estimates but is licensed/deferred.

## Empirical Window Check

Using the latest complete Shiller earnings month available during design review, 2026-03:

- 3y log-multiple center: about 26.38x; current z about -0.52
- 5y log-multiple center: about 25.13x; current z about +0.11
- 10y log-multiple center: about 24.85x; current z about +0.17

This supports 5y as the primary window and 3y as regime sensitivity, not the main classification.

## 1차 Implementation Decisions

- Three finance_meta tables preserve monthly valuation, explicit EPS status/basis/release vintage, and SEP release vintage separately.
- Shiller rows are labeled `interpolated`; the collector never promotes them to strict PIT actual observations.
- S&P earnings import requires explicit `period_end`, `status`, and EPS columns. It does not infer actual/estimate from workbook formatting.
- The S&P official download can remain operator-supplied when automated access is blocked; release date is mandatory.
- SEP discovery selects the latest dated official accessible-material link and keeps every release as a separate vintage.

## 2차 Implementation Decisions

- Monthly valuation loading returns ascending months even though the DB query selects newest rows first.
- TTM evidence deduplicates a quarter by newest source release before selecting four quarters.
- A TTM value is returned only with four completed distinct quarters; fewer rows remain `INSUFFICIENT_HISTORY`.
- Official classification thresholds are log(PER) z-score `< -1 LOW`, `< 1 NEUTRAL`, `< 2 HIGH`, otherwise `EXTREME_HIGH`.
- The 36-month bucket never replaces the 60-month bucket; disagreement is exposed through `period_sensitive`.

## 3차 Implementation Decisions

- Nominal EPS sensitivity compounds SEP inputs as `(1 + real GDP) × (1 + PCE) - 1`; it does not simply add percentages.
- Conservative/baseline/optimistic use central-tendency lower/median/central-tendency upper endpoints respectively.
- SPX lower/baseline/upper scenarios combine the matching EPS sensitivity with -1σ/mean/+1σ trailing multiple values.
- SPY equivalents are proportional convenience values only and are omitted when SPX/SPY EOD dates differ.
- SEP older than 180 days relative to the SPX as-of date is marked `STALE_SEP` and blocks the index scenario.
- Mixed or non-actual EPS never enters the calculation; the read model returns Korean blocking reasons.
