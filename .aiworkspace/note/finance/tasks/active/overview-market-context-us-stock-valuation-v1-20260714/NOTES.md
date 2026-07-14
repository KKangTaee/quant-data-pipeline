# Overview Market Context US Stock Valuation V1 Notes

Last Updated: 2026-07-14

## Confirmed Product Decisions

- Keep S&P 500 valuation as the primary index valuation surface.
- Replace only the user-facing Nasdaq selector; do not delete historical Nasdaq DB data or collectors.
- Add a DB-backed company/ticker search above the individual-stock valuation.
- Do not fetch providers when searching or opening the tab.
- Use an explicit synchronous collection action when selected-symbol raw data is missing.
- Use monthly price with quarterly filing-aware TTM EPS carry-forward; do not invent monthly EPS.
- Use log(P/E) for positive monthly multiple distribution.
- Use FOMC GDP+PCE as a macro anchor, not as a direct company EPS forecast.
- Add company historical EPS growth in excess of applicable SEP macro baseline.
- Treat negative EPS and structurally short history as NOT_APPLICABLE, not collection failure.

## Confirmed Current Assets

- The React valuation component already consumes instrument-scoped JSON models.
- `finance_price.nyse_price_history` stores daily price and stock-split evidence.
- `finance_fundamental.nyse_financial_statement_values` stores SEC detailed statement facts with `available_at`.
- SEC current ticker/CIK and symbol lifecycle sources exist.
- FOMC SEP current/history loaders and S&P scenario calculations exist.
- Actual DB samples checked during feasibility review:
  - AAPL/MSFT/NVDA/AMZN positive price history begins in 2006.
  - META positive price history begins 2012-05-18.
  - TSLA positive price history begins 2010-06-29.
  - all six samples have long SEC diluted-EPS histories.

## Correctness Prerequisites

- Existing Nasdaq TTM resolver treats comparative FY facts as separate year-end FY rows and can create false Q4 values.
- Raw-close drift can create split discontinuities.
- Individual-stock work must begin by fixing these shared correctness issues with real-like regressions.

## Product Language

- Prefer: `상대적 고평가/저평가`, `상대가치 시나리오`, `자체 재구성`
- Avoid: `공식 적정가`, `목표주가`, `매수/매도 신호`, `애널리스트 컨센서스`
