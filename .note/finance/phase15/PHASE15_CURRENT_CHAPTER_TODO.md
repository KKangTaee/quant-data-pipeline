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

- `completed` Quality / Quality + Value candidate improvement로 확장
  - same bounded addition approach를
    `Quality` / `Quality + Value` family에 적용한다

- `completed` strongest baseline 대비 비교 정리
  - `CAGR`
  - `MDD`
  - `Promotion`
  - `Shortlist`
  - `Deployment`

## Workstream B. Quality Candidate Improvement

- `completed` controlled factor expansion 기준 재탐색
- `completed` current literal preset semantics 기준 rerun 정리
  - single-factor addition만으로는 non-hold candidate를 회복하지 못했다
- `pending` benchmark / overlay / factor replacement rescue search

## Workstream C. Quality + Value Candidate Improvement

- `completed` bounded blend addition 탐색
- `completed` best raw addition candidate 정리
  - value-side addition까지 넓혀 보니 `per`가 current best practical candidate가 되었다
  - `real_money_candidate / small_capital_trial / review_required`까지 올라갔다
- `pending` benchmark / top_n / factor replacement search

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
- Quality current state:
  - bounded single-factor addition 기준 current non-hold candidate 없음
  - best near-miss:
    - `+ net_debt_to_equity`
    - `CAGR = 13.51%`
    - `MDD = -23.84%`
    - `Promotion = hold`
- Quality + Value best raw addition:
  - `+ per`
  - `CAGR = 29.43%`
  - `MDD = -27.43%`
  - `Promotion = real_money_candidate`
  - `Shortlist = small_capital_trial`
  - `Deployment = review_required`

## 현재 판단

- gate 자체를 더 느슨하게 만들기보다
  먼저 후보 전략 품질을 높이는 방향이 맞다.
- Phase 15 first pass에서는
  `Value downside-improvement search`의 첫 practical candidate를 확보했다.
- Phase 15 second pass에서는
  `psr` addition이 current best balanced candidate가 되었다.
- `Quality`는 current literal preset semantics 기준으로
  bounded single-factor addition만으로는 recovery가 안 된다.
- `Quality + Value`는 value-side controlled addition까지 넓혀 보니
  `per`가 gate tier를 실제로 끌어올렸다.
- 다음 active step은
  - `Quality`:
    - `benchmark / overlay / factor replacement` rescue search
  - `Quality + Value`:
    - `per` anchor 기준 `top_n / downside / factor replacement` search
  쪽이다.
