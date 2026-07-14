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

## 1차 Implementation Decisions

- FY-derived Q4 accepts `report_date == period_end` as the primary true-year-end proof.
- Legacy normalized FY rows without `report_date` are accepted only within a bounded 180-day first-filing lag; later comparative facts are rejected.
- A split affects an EPS fact only when the split date is after that fact's `available_at` and on or before the valuation month-end.
- Each discrete quarter is normalized independently, preventing a TTM assembled from mixed pre/post-split filings from changing share units mid-sum.
- Monthly rows remain explicit when price or EPS is missing; no neighboring month is substituted and invalid/non-positive EPS never produces P/E.

## 2차 Implementation Decisions

- The loader reads one symbol across the existing `finance_meta`, `finance_price`, and `finance_fundamental` databases with no new table or write path.
- Main READY classification uses 60 complete positive P/E months; 1/3/5-year history separately reports its 71/95/119-month rolling warmup requirement.
- Company growth uses positive-to-positive quarterly TTM YoY observations only, selects the latest applicable SEP median vintage at each filing availability date, and Tukey-clips rather than deleting outliers.
- The service preserves `index_scenario` as the generic chart handoff key for compatibility, but its label and limitation are explicitly stock-relative rather than index target-price language.
- Missing price/statement raw data can become COLLECTABLE; negative EPS, short listing, unverified ADR units, and structurally insufficient growth remain non-collectable.

## 3차 Implementation Decisions

- Search starts at two characters, reads only current `sec_company_tickers_exchange` lifecycle evidence, and ranks exact/prefix ticker matches before company-name matches.
- `kind=stock` is not treated as sufficient security-type proof; quote type, exchange, name patterns, active status, and CIK are defensively filtered.
- Main READY uses 60 complete months even though the loader reads up to 119 months for optional 5-year scenario warmup.
- Preflight derives price gaps from explicit monthly missing rows and uses the bounded statement lookback for SEC gap collection.
- The synchronous runner validates ticker/CIK before any provider call, preserves partial-success writes, and converts inclusive UI price end to the collector's exclusive end.
- Overview retries re-run preflight and execute only remaining scopes; an already READY plan is an idempotent no-op.

## 4차 Implementation Decisions

- The combined contract is now `market_context_valuation_v3` with exactly `sp500` and `us_stock`; each builder remains isolated so selected-stock failure cannot alter the S&P payload.
- Search and selection events only update Streamlit session state and re-read cached DB-backed models; only `collect_us_stock_valuation` can cross into the synchronous ingestion action.
- Collection validates that the event ticker matches the current selected ticker and consumes each nonce once before calling the job boundary.
- The React surface always exposes the exact `S&P 500 | 미국 개별주식` selector and keeps search above the selected-stock state/result.
- `COLLECTABLE` is the only state with a collection action; NOT_SELECTED, NOT_APPLICABLE, and ERROR render explanations without provider actions.
- S&P keeps its existing read model, provisional P/E presentation, macro inputs, and 1/3/5-year history route while the stock branch uses filing-aware terminology and relative-value disclaimers.
- The old Nasdaq model, repair facade, ingestion job, automation spec, tables, and tests remain in the repository; only the user-facing combined/UI connection was removed.

## 5차 Actual-DB Hardening Decisions

- Current listing identity can come from any active stored lifecycle snapshot plus active equity profile; a missing `sec_company_tickers_exchange` snapshot must not block read-only valuation of already stored price/EPS evidence.
- CIK is optional for DB-only search/read but mandatory before external collection. When raw gaps and CIK are both missing, the explicit collection action first runs the existing selected-symbol SEC ticker/CIK crosscheck, re-plans, then runs only remaining price/statement scopes.
- Listing duration uses the earliest stored price date and lifecycle first-seen date, preventing a recently refreshed listing snapshot from misclassifying a long-listed company as a new IPO.
- Profile exchanges `NMS/NGM/NCM/NYQ/ASE` are normalized to user-facing Nasdaq/NYSE/NYSE American labels.
- A non-U.S. issuer profile without explicit per-share/ADR-ratio evidence is conservatively `ADR_UNIT_UNVERIFIED` and cannot expose a collection action.

## Product Language

- Prefer: `상대적 고평가/저평가`, `상대가치 시나리오`, `자체 재구성`
- Avoid: `공식 적정가`, `목표주가`, `매수/매도 신호`, `애널리스트 컨센서스`
