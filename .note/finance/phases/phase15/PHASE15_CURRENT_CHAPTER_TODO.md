# Phase 15 Current Chapter TODO

## 상태 요약

- `completed` Phase 15 practical closeout 준비
- 현재 phase 목적:
  - candidate quality improvement
  - downside improvement search
  - strategy-specific cumulative backtest logging
  - strongest/current candidate closeout 정리

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
- `completed` benchmark / overlay structural rescue search
  - `capital_discipline + LQD + trend on + regime off + Top N 10`
    조합에서 `real_money_candidate / paper_probation / review_required`를 회복했다
- `completed` rescued anchor 기준 downside / top-N search
  - `Top N = 12`
    - `CAGR = 26.02%`
    - `MDD = -25.57%`
    - `real_money_candidate / paper_probation / review_required`
    로 current recommended downside-improved candidate를 확보했다
- `completed` rescued anchor 기준 bounded factor addition / replacement search
  - baseline을 넘는 bounded factor change는 없었다
  - `+ net_debt_to_equity`만 non-hold를 유지했지만
    `CAGR`와 `MDD`가 baseline보다 둘 다 나빠졌다
- `completed` rescued anchor alternate contract search
  - `LQD + trend on + regime off + Top N 12`
    가 여전히 strongest practical point로 남았다
  - `SPY + trend on + regime off + Top N 12`
    는 same `MDD`와 cleaner `Validation / Rolling / OOS`
    를 주지만 `Deployment = paper_only`로 더 보수적이었다
  - 더 방어적인 overlay는 오히려 `hold / blocked`로 후퇴했다

## Workstream C. Quality + Value Candidate Improvement

- `completed` bounded blend addition 탐색
- `completed` best raw addition candidate 정리
  - value-side addition까지 넓혀 보니 `per`가 current best practical candidate가 되었다
  - `real_money_candidate / small_capital_trial / review_required`까지 올라갔다
- `completed` `per` anchor 기준 top_n downside search
  - `Top N = 10`이 여전히 strongest practical point로 남았다
- `completed` benchmark / quality-side pruning search
  - `Candidate Universe Equal-Weight + per` baseline이
    여전히 strongest practical point로 남았다
  - `Ticker Benchmark = SPY`는 same return이어도 shortlist tier가 낮아졌다
  - quality-side pruning은 전부 `hold / blocked`였다
- `completed` value-side replacement / bounded removal search
  - value-side removal은 gate tier를 낮췄다
  - `ocf_yield -> pcr` replacement는
    same gate / same MDD를 유지하면서 `CAGR`를 `29.43% -> 30.05%`로 올렸다
- `completed` replacement-anchor follow-up search
  - `ocf_yield -> pcr` new anchor에서도
    `Top N = 10 + Candidate Universe Equal-Weight`
    가 strongest practical point로 유지됐다
  - `Top N = 8`은 수익률은 더 높았지만
    `production_candidate / watchlist`로 내려갔다
  - `Ticker Benchmark = SPY`는
    same return / same drawdown이지만
    shortlist를 `paper_probation`으로 한 단계 낮췄다
- `completed` quality-side one-more bounded replacement search
  - `ocf_yield -> pcr` anchor 위에서 quality-side replacement를 다시 본 결과
    `net_margin -> operating_margin`
    가 same gate를 유지하면서
    `CAGR = 31.25% / MDD = -26.63%`
    로 current strongest practical point를 갱신했다
  - `current_ratio -> operating_margin`은
    더 낮은 `MDD`를 줬지만
    `production_candidate / watchlist`로 내려가 strongest point를 넘진 못했다
- `completed` new strongest anchor `Top N` follow-up search
  - new anchor 위에서 `Top N = 8, 9, 10, 11, 12`를 다시 본 결과
    `Top N = 10`이 여전히 strongest practical point로 유지됐다
  - `Top N = 9`는
    `CAGR = 31.08% / MDD = -25.61%`
    로 숫자는 attractive했지만
    `production_candidate / watchlist`로 내려갔다
  - `Top N = 12`부터는 `hold / blocked`로 무너졌다

## Workstream D. Reporting

- `completed` phase15 backtest report 첫 문서 작성
- `completed` 전략별 backtest log append
- `completed` strategy hub snapshot 갱신
- `completed` Phase 15 closeout 문서 / handoff / checklist 정리

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
  - rescued current candidate 확보
  - `capital_discipline + LQD + trend on + regime off + Top N 10`
    - `CAGR = 24.28%`
    - `MDD = -31.48%`
    - `Promotion = real_money_candidate`
    - `Shortlist = paper_probation`
    - `Deployment = review_required`
- Quality downside-improved current candidate:
  - `capital_discipline + LQD + trend on + regime off + Top N 12`
    - `CAGR = 26.02%`
    - `MDD = -25.57%`
    - `Promotion = real_money_candidate`
    - `Shortlist = paper_probation`
    - `Deployment = review_required`
- Quality conservative clean alternative:
  - `capital_discipline + LQD + trend on + regime off + Top N 16`
    - `CAGR = 20.23%`
    - `MDD = -25.73%`
    - `Promotion = real_money_candidate`
    - `Shortlist = paper_probation`
    - `Deployment = review_required`
- Quality + Value best raw addition:
  - `+ per`
  - `CAGR = 29.43%`
  - `MDD = -27.43%`
  - `Promotion = real_money_candidate`
  - `Shortlist = small_capital_trial`
  - `Deployment = review_required`
- Quality + Value current strongest practical point:
  - `Top N = 10 + per`
  - with value replacement:
    - `ocf_yield -> pcr`
  - with quality replacement:
    - `net_margin -> operating_margin`
  - `CAGR = 31.25%`
  - `MDD = -26.63%`
  - `Promotion = real_money_candidate`
  - `Shortlist = small_capital_trial`
  - `Deployment = review_required`
- Quality + Value notable alternatives:
  - previous anchor:
    - `Top N = 10`
    - value-side only:
      - `ocf_yield -> pcr`
    - `CAGR = 30.05%`
    - `MDD = -27.43%`
    - `Promotion = real_money_candidate`
    - `Shortlist = small_capital_trial`
  - lower-MDD but weaker gate:
    - `Top N = 10`
    - `current_ratio -> operating_margin`
    - `CAGR = 30.84%`
    - `MDD = -24.09%`
    - `Promotion = production_candidate`
    - `Shortlist = watchlist`
  - higher-CAGR but weaker gate:
    - `Top N = 8`
    - `CAGR = 31.69%`
    - `MDD = -27.64%`
    - `Promotion = production_candidate`
    - `Shortlist = watchlist`
  - cleaner human-readable benchmark:
    - `Top N = 10`
    - `Ticker Benchmark = SPY`
    - `CAGR = 30.05%`
    - `MDD = -27.43%`
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
- `Quality`는 current literal preset semantics 기준으로
  bounded single-factor addition만으로는 recovery가 안 됐지만,
  structural rescue search에서는 current candidate를 다시 회복했다.
- `Quality + Value`는 value-side controlled addition까지 넓혀 보니
  `per`가 gate tier를 실제로 끌어올렸다.
- 그리고 `Top N` downside search와 benchmark / pruning second pass까지 보면
  `Top N = 10 + per`가 strongest practical point였고,
  value-side third pass에서는 `ocf_yield -> pcr`가 그 practical point를 한 단계 더 개선했다.
- replacement-anchor follow-up fourth pass까지 보면
  `Top N = 10 + Candidate Universe Equal-Weight`가 그대로 strongest practical point였고,
  `Top N = 8`과 `Ticker Benchmark = SPY`는 각각
  higher-CAGR / cleaner-benchmark 대안이지만 strongest practical point를 넘지는 못했다.
- 그 다음 quality-side fifth pass에서는
  `net_margin -> operating_margin`
  replacement가 current strongest practical point를 실제로 갱신했다.
- 그리고 sixth pass에서 new anchor 기준 `Top N`을 다시 봐도
  `Top N = 10`이 strongest practical point로 유지됐다.
- 다음 active step은
  - manual validation checklist 기준으로
    current strongest candidates 문서와 log 체계를 확인한다
  - next phase 방향은
    candidate consolidation / downside follow-up / operator workflow persistence
    중 어느 쪽으로 열지 사용자와 다시 정한다
