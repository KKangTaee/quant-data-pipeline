# Overview Market Context Nasdaq-100 Valuation V1 Notes

Last Updated: 2026-07-12

## Confirmed Decisions

- Display unit: QQQ, not NDX.
- User-facing label: `Nasdaq-100 · QQQ proxy`.
- Source quality: `public_filing_reconstructed_proxy`.
- No paid provider, account, token, public-page scraping, or access bypass.
- Existing FOMC SEP GDP+PCE scenario logic is reused.

## Discovery

- SEC browse-edgar Atom can discover QQQ NPORT-P filings without authentication.
- SEC search found 27 quarterly period endings from 2019-09-30 to 2026-03-31.
- QQQ N-30B-2 annual schedules exist before N-PORT and can provide the 2015+ rolling warmup.
- 2025-03-31 N-PORT sample contained 101 holdings with CUSIP/ISIN/LEI/quantity/value/weight.
- Current DB QQQ holdings have 105 symbols across 2026-05-08 and 2026-05-29 snapshots.
- Current DB diluted EPS exact-symbol coverage is 91/104 symbols and 96.46% by weight.

## Interpretation Boundary

- Reconstructed trailing P/E is a real P/E calculation, not sentiment or a price-only indicator.
- Reconstructed QQQ TTM EPS is `QQQ price / reconstructed P/E`.
- The result is not an official Nasdaq index aggregate because QQQ weights, missing foreign issuers, ADR conversion, and provider conventions can differ.
