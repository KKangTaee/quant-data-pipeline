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
