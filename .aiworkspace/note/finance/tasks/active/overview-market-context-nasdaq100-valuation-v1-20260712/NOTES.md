# Overview Market Context Nasdaq-100 Valuation V1 Notes

Last Updated: 2026-07-13

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

## 2026-07-13 Coverage Spike Result

- SEC filing discovery returned 30 required anchors from 2016-09 through 2026-03: 3 annual N-30B-2 warmup anchors and 27 quarterly N-PORT anchors.
- Strict parser output was 101~107 equity rows per anchor with approximately 100% weight.
- CUSIP/name/reviewed rename mapping raised identity coverage to 99.60% for 2016-09, 99.62% for 2017-09, 100% for 2018-09, and 99.74% for the previously weak 2020-12 N-PORT anchor.
- Filing-aware diluted EPS plus existing component/QQQ EOD produced 119 monthly rows for 2016-09~2026-07.
- Approved 95% gate result: latest 60 months complete `5/60`; minimum coverage `92.63%`; 2026-07 coverage `94.47%`.
- If the coverage gate is temporarily disabled only for diagnosis, 2026-07 reconstructed trailing P/E is `31.91997`; public fixture `31.89` absolute percentage error is `0.094%`.

## Blocking Source Boundary

- SEC CIK-based companyfacts can recover USD/share EPS for current and delisted issuers without ticker lookup. Examples verified: STX, FISV, LULU, PTON, ATVI, WBA, ALXN, XLNX, ANSS, SGEN, MXIM, CERN.
- Existing DB has no EOD rows for several later-delisted/acquired 2021 constituents. Current yfinance requests return delisted/404 for these tickers.
- Stooq's unauthenticated CSV endpoint currently returns a proof-of-work verification page, so it is not a stable automated ingestion source for this task.
- Holding the missing ticker weight constant, interpolating N-PORT quarter prices, lowering 95%, or treating annual-only foreign EPS as current TTM would change the approved calculation contract and was not done.

## Implemented Boundary

- `finance_meta.etf_holdings_snapshot`은 SEC identity/timing field를 additive column으로 받으며 기존 Invesco rows는 null 호환이다.
- `finance_meta.nasdaq100_monthly_valuation`은 blocked month도 삭제하지 않고 `(observation_month, proxy_symbol, source)`로 UPSERT한다.
- combined service는 instrument별 예외를 격리한다. 실제 smoke에서 S&P `READY`, Nasdaq `BLOCKED`가 동시에 반환됐다.
- React는 운영 row/job panel을 추가하지 않고 사용자의 판단 질문에 필요한 selector와 coverage gate만 제공한다.
- 무료·무계정 방향은 SEC holdings/company facts와 DB QQQ EOD를 사용한다. 화면은 SEC/Invesco/Yahoo를 직접 호출하지 않는다.
