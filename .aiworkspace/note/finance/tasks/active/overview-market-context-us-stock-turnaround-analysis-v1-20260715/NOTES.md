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

## Implementation Decisions

- duration resolver는 direct Q를 우선하고 `H1-Q1`, `9M-H1`, `FY-Q1-Q2-Q3`만 허용한다. concept/unit/fiscal identity가 다르거나 operand가 빠지면 quarter를 만들지 않는다.
- later comparative filing은 original primary quarter를 덮지 못하고, derived quarter의 `available_at`은 사용한 operand 중 가장 늦은 공개일이다.
- selected-symbol loader는 duration/instant query를 분리하고 최대 7 fiscal years만 읽는다. 분석 selector 전환은 React local state이며 provider/action event를 내지 않는다.
- service recommendation은 positive current TTM EPS와 기존 Graph 1 READY를 모두 만족할 때만 `per`다. 그 외에는 전환 분석을 기본으로 열되 사용자는 같은 종목에서 PER 상태를 확인할 수 있다.
- SEC CIK가 없으면 raw repair는 `BLOCKED/CIK_MISSING`이다. 이 collection limitation은 저장 facts로 만든 READY 분석의 status를 ERROR로 낮추지 않는다.
- numeric valuation은 fresh/aligned USD profile·price·statement input이 있을 때만 허용한다. stale market cap은 operating/cash/risk section을 숨기지 않고 valuation section만 BLOCKED로 둔다.

## Actual QA Interpretation

- RIVN/LCID/PLTR는 저장 quarter evidence만으로 전환 분석이 READY였지만 실제 lifecycle CIK가 비어 있어 명시 수집은 차단됐다. 이번 QA는 read-only로 끝냈고 외부 source를 호출하지 않았다.
- AMD/AAPL은 기존 PER 분석이 적용 가능하므로 내부 selector의 추천이 PER로 유지됐다. turnaround payload 추가 전후의 기존 PER field/value는 동일했다.
- symbol-keyed selector는 새 종목에서 service 추천을 따르고 같은 종목의 명시 선택은 rerender 후에도 보존한다. Browser QA에서 RIVN의 전환 분석과 PER `NOT_APPLICABLE/STRUCTURALLY_SHORT_LISTING`을 왕복 확인했다.
- actual read-time latency는 RIVN `1.739s`, LCID `2.065s`, PLTR `2.128s`, AMD `3.627s`, AAPL `7.231s`였다. selected-company V1에는 허용했지만 broad discovery로 일반화하지 않는다.
