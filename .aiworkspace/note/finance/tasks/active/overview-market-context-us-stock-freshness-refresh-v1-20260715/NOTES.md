# Overview Market Context US Stock Freshness Refresh V1 Notes

Last Updated: 2026-07-15

## Decisions

- PER와 turnaround에 각각 버튼을 두지 않고 selected-stock 상단 action 하나를 사용한다.
- stale 판정은 오늘 날짜가 아니라 마지막 완료 NYSE session을 기준으로 한다.
- 재무 period end가 과거라는 이유만으로 수집하지 않는다.
- profile/price 수집은 CIK와 분리하고 SEC statement에만 CIK identity equality를 요구한다.
- action의 제품 가치는 갱신된 기준일과 재계산 결과이며 별도 진단 panel을 만들지 않는다.
- 기업 선택 시 cached DB UI를 즉시 표시하고 freshness만 자동 판정한다. Provider 수집은 상단 CTA 클릭에만 허용한다.
- 버튼은 종목이 `REFRESH_AVAILABLE`일 때만 header와 PER/전환 selector 사이에 한 번 표시한다. READY이면 최신 기준일만 보여주고 버튼은 숨긴다.
- 가격 수집의 selected-stock end date는 completed-session inclusive 계약이다. provider adapter가 exclusive end를 처리하므로 caller에서 하루를 중복 가산하지 않는다.

## Actual NET Evidence Before Refresh

- latest price: `2026-07-07`, `268.8299865722656`
- market cap snapshot: `2026-02-04`, `59,199,270,001 USD`
- latest statement: `2026-Q1`, period end `2026-03-31`, available `2026-05-08`
- TTM FCF: `320,701,000 USD`
- valuation: `BLOCKED/INPUT_STALE`
- lifecycle CIK: missing

## Actual NET Evidence After Explicit Refresh

- expected completed NYSE price date: `2026-07-14`
- latest price: `2026-07-14`
- profile collected at: `2026-07-15`
- latest statement: period end `2026-03-31`, available `2026-05-08`
- unified freshness: `READY`, gaps `[]`
- SEC CIK: still missing; no statement refresh was required by the stored raw coverage contract

## Session Boundary Correction

- 첫 actual 실행에서 caller와 yfinance adapter가 모두 end date에 하루를 더해 진행 중인 `2026-07-15` daily row가 들어오는 문제를 발견했다.
- new unified caller의 중복 `+1 day`를 제거하고 회귀 테스트를 먼저 고정했다.
- 실행 전 존재하지 않았던 NET `2026-07-15` row만 정확히 제거했으며 기존 사용자 자료는 되돌리지 않았다.
