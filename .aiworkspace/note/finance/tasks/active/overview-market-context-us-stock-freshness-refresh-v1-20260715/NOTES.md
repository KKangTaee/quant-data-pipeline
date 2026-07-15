# Overview Market Context US Stock Freshness Refresh V1 Notes

Last Updated: 2026-07-15

## Decisions

- PER와 turnaround에 각각 버튼을 두지 않고 selected-stock 상단 action 하나를 사용한다.
- stale 판정은 오늘 날짜가 아니라 마지막 완료 NYSE session을 기준으로 한다.
- 재무 period end가 과거라는 이유만으로 수집하지 않는다.
- profile/price 수집은 CIK와 분리하고 SEC statement에만 CIK identity equality를 요구한다.
- action의 제품 가치는 갱신된 기준일과 재계산 결과이며 별도 진단 panel을 만들지 않는다.

## Actual NET Evidence

- latest price: `2026-07-07`, `268.8299865722656`
- market cap snapshot: `2026-02-04`, `59,199,270,001 USD`
- latest statement: `2026-Q1`, period end `2026-03-31`, available `2026-05-08`
- TTM FCF: `320,701,000 USD`
- valuation: `BLOCKED/INPUT_STALE`
- lifecycle CIK: missing
