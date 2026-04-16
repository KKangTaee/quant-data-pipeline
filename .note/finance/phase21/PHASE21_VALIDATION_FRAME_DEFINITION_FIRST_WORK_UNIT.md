# Phase 21 Validation Frame Definition First Work Unit

## 이 문서는 무엇인가

- `Phase 21`의 첫 실제 작업으로,
  integrated deep validation을 어떤 기준으로 다시 열지 고정한 문서다.
- 쉽게 말하면
  **"무엇을, 어떤 기간과 어떤 이름으로 다시 돌릴지"**
  를 먼저 정한 문서다.

## 목적

- family별 rerun이 제각각 해석되지 않도록
  공통 validation frame을 먼저 고정한다.
- `Value`, `Quality`, `Quality + Value`, portfolio bridge를
  같은 phase 언어로 다시 읽을 수 있게 만든다.
- 이후 rerun report / strategy log / candidate summary가
  같은 naming과 같은 판단 기준을 쓰게 만든다.

## 쉽게 말하면

- 지금은 rerun을 많이 돌리는 것보다,
  **무엇을 다시 보는지부터 분명히 정하는 단계**
  가 더 중요하다.
- 이 문서는
  - 다시 볼 후보
  - 공통 기간
  - 어디에 기록할지
  - 문서 이름을 어떻게 맞출지
  를 먼저 정리한 기준표다.

## 왜 필요한가

- `Phase 15 ~ 20` 동안 current anchor와 alternative는 충분히 쌓였다.
- 하지만 family별 문서, structural follow-up, operator workflow 문서가 섞여 있어
  지금 바로 rerun을 시작하면
  결과가 "같은 검증 frame"보다 "이전 phase 문맥"으로 다시 흩어질 수 있다.
- `Phase 18`도 closeout 처리되었기 때문에,
  이제는 구조 실험을 하나 더 여는 것보다
  **현재 후보를 같은 기준으로 다시 읽는 일**
  이 우선이다.

## 이번 작업에서 고정한 공통 validation frame

### 1. 공통 기간과 cadence

- `Start Date`: `2016-01-01`
- `End Date`: `2026-04-01`
- `Option`: `month_end`
- `Rebalance Interval`: `1`

왜 이렇게 정했나:

- current anchor / alternative one-pager와 hub 문서가
  이미 이 기간 기준으로 가장 많이 정리되어 있다.
- 지금 phase의 목적은 최신 date 확장보다
  **같은 frame에서 유지 / 교체 / 보류를 다시 읽는 것**
  이기 때문이다.

### 2. 공통 universe frame

- `Preset`: `US Statement Coverage 100`
- `Universe Contract`: `Historical Dynamic PIT Universe`

왜 이렇게 정했나:

- current practical candidate 문서와 registry가
  이 contract 기준으로 가장 잘 정리되어 있다.
- annual strict family를 지금 단계에서 다시 비교하려면
  contract를 더 넓히기보다
  **현재 실전형 baseline을 그대로 쓰는 편**이 맞다.

### 3. 공통 practical-reading 원칙

- `Minimum Price = 5.0`
- `Minimum History = 12M`
- `Min Avg Dollar Volume 20D = 5.0M`
- `Transaction Cost = 10 bps`
- underperformance / drawdown guardrail:
  - current candidate 문서에 적힌 실전형 contract 기준을 그대로 따른다

중요:

- benchmark contract, benchmark ticker, trend filter, market regime는
  family별 current candidate 설정을 그대로 유지한다.
- 즉 이번 phase는
  "모든 전략을 같은 benchmark로 통일"하는 단계가 아니라,
  **각 current candidate가 원래 어떤 practical contract였는지 그대로 두고 다시 읽는 단계**
  다.

## 이번 phase에서 다시 볼 후보 pack

### 1. Value rerun pack

- current anchor:
  - registry id: `value_current_anchor_top14_psr`
  - 해석:
    - `Top N = 14 + psr`
    - `28.13% / -24.55%`
    - `real_money_candidate / paper_probation / review_required`
- lower-MDD alternative:
  - registry id: `value_lower_mdd_near_miss_pfcr`
  - 해석:
    - `+ pfcr`
    - `27.22% / -21.16%`
    - `production_candidate / watchlist / review_required`

이번 pack의 핵심 질문:

- current anchor를 그대로 유지하는가
- lower-MDD near-miss가 여전히 weaker-gate alternative로 남는가

### 2. Quality rerun pack

- current anchor:
  - registry id: `quality_current_anchor_top12_lqd`
  - 해석:
    - `capital_discipline + LQD + trend on + regime off + Top N 12`
    - `26.02% / -25.57%`
    - `real_money_candidate / paper_probation / review_required`
- cleaner alternative:
  - registry id: `quality_cleaner_alternative_top12_spy`
  - 해석:
    - `SPY + trend on + regime off + Top N 12`
    - `25.18% / -25.57%`
    - `real_money_candidate / paper_probation / paper_only`

이번 pack의 핵심 질문:

- `LQD` anchor가 여전히 current practical point인가
- `SPY` cleaner alternative가 readability-only 대안인지,
  아니면 current 추천점까지 다시 위협하는지

### 3. Quality + Value rerun pack

- current anchor:
  - registry id: `quality_value_current_anchor_top10_por`
  - 해석:
    - `operating_margin + pcr + por + per + Top N 10 + Candidate Universe Equal-Weight`
    - `31.82% / -26.63%`
    - `real_money_candidate / small_capital_trial / review_required`
- lower-MDD weaker-gate alternative:
  - registry id: `quality_value_lower_mdd_near_miss_top9`
  - 해석:
    - `Top N = 9`
    - `31.08% / -25.61%`
    - `production_candidate / watchlist / review_required`

이번 pack의 핵심 질문:

- current strongest practical point를 그대로 유지하는가
- lower-MDD alternative가 여전히 gate-lower near-miss로 남는가

## portfolio bridge validation frame

### 1. compare source

- `Compare & Portfolio Builder`
- `Quick Re-entry From Current Candidates`
- `Load Recommended Candidates`

이번 phase에서 representative bridge는
위 버튼으로 불러온 current recommended bundle을 기준으로 읽는다.

즉:

- `Value` current anchor
- `Quality` current anchor
- `Quality + Value` current anchor

를 같은 compare에서 다시 읽는 흐름을 기준 bridge로 삼는다.

### 2. representative weighted portfolio

- source bundle:
  - current recommended candidates 3종
- weight:
  - first pass는 near-equal weight로 본다
  - 추천 기준:
    - `33 / 33 / 34`
- `Date Alignment`:
  - `intersection`

왜 이렇게 정했나:

- 지금 phase에서 weighted portfolio는
  alpha optimization이 아니라
  **bridge가 candidate lane으로 읽힐 만큼 의미가 있는지**
  를 보는 용도이기 때문이다.
- 따라서 first pass는 가장 해석하기 쉬운 equal-like 조합이 맞다.

### 3. representative saved portfolio

- representative weighted portfolio를
  `Phase 21` validation용 이름으로 저장한다.
- 추천 이름:
  - `phase21_validation_recommended_equal_weight_v1`

이번 pack에서 확인할 것:

- `Load Saved Setup Into Compare`
  - compare / weighted 입력이 다시 잘 복원되는가
- `Replay Saved Portfolio`
  - same frame에서 다시 읽을 만한 candidate artifact인가

## 이번 phase의 결과를 남기는 위치

### 1. phase report

- family rerun report:
  - `.note/finance/backtest_reports/phase21/PHASE21_VALUE_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md`
  - `.note/finance/backtest_reports/phase21/PHASE21_QUALITY_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md`
  - `.note/finance/backtest_reports/phase21/PHASE21_QUALITY_VALUE_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md`
- bridge report:
  - `.note/finance/backtest_reports/phase21/PHASE21_PORTFOLIO_BRIDGE_VALIDATION_FIRST_PASS.md`

### 2. strategy hub / backtest log

- rerun 결과가 의미 있으면
  family별 strategy hub와 backtest log에도 같은 판단을 남긴다.
- 핵심 규칙:
  - phase report는 이번 phase의 비교 기록
  - strategy hub / log는 그 결과를 durable knowledge로 남기는 위치

### 3. candidate summary

- rerun 결과로
  `유지 / 교체 / 보류`
  판단이 생기면
  `.note/finance/backtest_reports/strategies/CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md`
  도 마지막에 같이 갱신한다.

## rerun pack naming rule

### phase report 이름

- family별:
  - `PHASE21_<FAMILY>_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md`
- portfolio bridge:
  - `PHASE21_PORTFOLIO_BRIDGE_VALIDATION_FIRST_PASS.md`

### strategy log entry 이름

- `2026-04-16 - phase21 integrated validation first pass (value)`
- `2026-04-16 - phase21 integrated validation first pass (quality)`
- `2026-04-16 - phase21 integrated validation first pass (quality_value)`
- `2026-04-16 - phase21 portfolio bridge validation first pass`

왜 naming을 고정하나:

- 이번 phase는 rerun 수가 늘어날수록
  보고서와 log 제목이 뒤섞이기 쉽다.
- 이름을 먼저 고정해두면
  나중에 summary / closeout / handoff에서 다시 찾기 쉬워진다.

## 이번 작업이 끝나면 좋은 점

- 이제 `Phase 21`은 막연한 deep validation phase가 아니라
  **실제로 무엇을 다시 돌릴지 정해진 phase**가 된다.
- 다음 작업은 문서 고민보다
  실제 rerun 실행과 결과 정리로 바로 넘어갈 수 있다.

## 다음 작업

- `Value` rerun pack 실행
- `Quality` rerun pack 실행
- `Quality + Value` rerun pack 실행
- representative portfolio bridge validation 실행

## 한 줄 정리

- 이번 첫 작업은 `Phase 21`의 **공통 검증 frame과 rerun pack 범위를 먼저 고정해, 이후 deep validation을 같은 기준에서 읽히게 만든 정리 작업**이다.
