# Phase 15 Current Chapter TODO

## 상태 요약

- `in_progress` Phase 15 kickoff
- 현재 phase 목적:
  - candidate quality improvement
  - downside improvement search
  - strategy-specific cumulative backtest logging

## Workstream A. Value Downside Improvement

- `completed` strongest baseline 고정
  - `Value > Strict Annual`
  - `Coverage 100`
  - `Historical Dynamic PIT Universe`
  - strongest current candidate를 anchor로 둔다

- `completed` overlay / cadence / top-N downside search
  - baseline factor set 유지
  - `Trend Filter`, `Market Regime`, `Top N`, `Rebalance Interval` 조합 탐색
  - first pass 결론:
    - overlay / cadence는 `hold`로 돌아가기 쉬웠다
    - `Top N = 14`가 downside-improved current candidate로 가장 균형이 좋았다

- `completed` factor subset / addition downside search
  - baseline 5-factor를 중심으로
    more defensive subset / addition 후보를 탐색
  - first added-factor result:
    - `psr` addition이 current best balanced candidate였다
    - `CAGR = 28.13%`
    - `MDD = -24.55%`

- `pending` Quality / Quality + Value candidate improvement로 확장
  - same bounded addition approach를
    `Quality` / `Quality + Value` family에 적용한다

- `completed` strongest baseline 대비 비교 정리
  - `CAGR`
  - `MDD`
  - `Promotion`
  - `Shortlist`
  - `Deployment`

## Workstream B. Quality Candidate Improvement

- `pending` controlled factor expansion 기준 재탐색
- `pending` non-hold / production_candidate 근접 후보 정리

## Workstream C. Quality + Value Candidate Improvement

- `pending` blend family defensive 탐색
- `pending` strongest practical candidate refresh

## Workstream D. Reporting

- `completed` phase15 backtest report 첫 문서 작성
- `completed` 전략별 backtest log append
- `completed` strategy hub snapshot 갱신

## 현재 추천 후보

- strongest baseline:
  - `Top N = 10`
  - `CAGR = 29.89%`
  - `MDD = -29.15%`
- downside-improved current candidate:
  - `Top N = 14`
  - `CAGR = 27.48%`
  - `MDD = -24.55%`
  - `Promotion = real_money_candidate`
  - `Shortlist = paper_probation`
  - `Deployment = review_required`
- best addition candidate:
  - `Top N = 14 + psr`
  - `CAGR = 28.13%`
  - `MDD = -24.55%`
  - `Promotion = real_money_candidate`
  - `Shortlist = paper_probation`
  - `Deployment = review_required`

## 현재 판단

- gate 자체를 더 느슨하게 만들기보다
  먼저 후보 전략 품질을 높이는 방향이 맞다.
- Phase 15 first pass에서는
  `Value downside-improvement search`의 첫 practical candidate를 확보했다.
- Phase 15 second pass에서는
  `psr` addition이 current best balanced candidate가 되었다.
- 다음 active step은
  `Quality` / `Quality + Value` family에 같은 bounded addition search를 적용하는 것이다.
