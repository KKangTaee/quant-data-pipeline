# Overview Market Context US Stock Turnaround Analysis V1 Notes

Last Updated: 2026-07-15

## Decisions

- 새 최상위 Market Context instrument가 아니라 미국 개별주식 내부 분석 selector다.
- V1은 selected company 분석이며 universe-wide turnaround discovery/ranking은 후속이다.
- graph는 current PER monthly chart를 복제하지 않고 quarterly filing cadence에 맞춘다.
- operating milestone과 distress/dilution risk는 독립 evidence다.
- numeric valuation은 target price가 아니라 currently applicable method/value input disclosure다.
- `EV/OCF`는 numerator/denominator claim mismatch 때문에 사용하지 않는다.
- cash-flow turn은 one-quarter OCF가 아니라 two consecutive positive quarterly TTM OCF로 확인한다.
- negative earnings는 turnaround analysis의 NOT_APPLICABLE 이유가 아니다.

## Repository Findings

- current `MarketContextValuation.tsx`가 S&P/미국 개별주 selector, stock search, PER states, graphs를 소유한다.
- current stock loader는 EPS concepts만 bounded load한다. Turnaround는 revenue, gross profit/cost, operating income, net income, OCF, CapEx, cash, investments, debt, interest, D&A, diluted shares를 별도 bounded load해야 한다.
- statement shadow는 useful fallback이지만 transition history의 cumulative H1/9M/FY를 정확한 discrete quarter로 재구성하는 authoritative input은 raw `nyse_financial_statement_values`다.
- `nyse_asset_profile.market_cap`은 존재하지만 symbol별 수집시점이 달라 freshness gate가 필요하다.

## Actual Coverage Snapshot

- RIVN: main flow concepts 약 16 distinct quarters
- PLTR: main flow concepts 약 19 distinct quarters
- LCID: operating/net income 18, OCF 17, CapEx 15 distinct quarters
- LCID direct GrossProfit coverage가 약해 revenue-cost derivation이 필요하다.
- AMD/AAPL은 profitable-company and long-history regression fixture에 충분하다.

## Interpretation Boundary

- stage는 매수/매도 신호가 아니다.
- runway는 constant-burn mechanical estimate다.
- 1.0pp/5%/10%/4분기/8분기 threshold는 V1 materiality/risk display heuristic이며 보편적 투자 법칙이 아니다.
- partial metric coverage는 pass로 처리하지 않고 UNKNOWN/PARTIAL로 남긴다.
