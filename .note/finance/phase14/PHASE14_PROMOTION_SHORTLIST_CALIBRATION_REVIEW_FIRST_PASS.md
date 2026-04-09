# Phase 14 Promotion Shortlist Calibration Review First Pass

## 목적

- Phase 14 first-pass blocker audit 다음 단계로,
  현재 `promotion / shortlist / deployment-readiness`를 실제로 갈라놓는 기준을
  **threshold inventory + family별 해석 차이** 관점에서 다시 정리한다.
- 동시에 사용자가 바로 물었던 질문,
  **"hold가 반복되는 이유가 factor 수가 적어서일 수 있는가?"**
  를 현재 evidence 기준으로 분리해서 평가한다.

## 이번 문서의 결론 한 줄

- 현재 반복 `hold`의 1차 원인은 **factor 부족보다 gate calibration** 쪽에 더 가깝다.
- 다만 factor expansion은 여전히 가치가 있고,
  **calibration 이후 또는 병렬의 통제된 search workstream**으로 여는 것이 맞다.

## 1. Current threshold inventory

### 1-1. Promotion에 직접 들어가는 configurable threshold

`app/web/runtime/backtest.py` 기준 현재 meta에 저장되고 operator 입력으로도 연결되는 기준은 아래다.

- `promotion_min_etf_aum_b = 1.0`
- `promotion_max_bid_ask_spread_pct = 0.005`
- `promotion_min_benchmark_coverage = 0.95`
- `promotion_min_net_cagr_spread = -0.02`
- `promotion_min_liquidity_clean_coverage = 0.90`
- `promotion_max_underperformance_share = 0.55`
- `promotion_min_worst_rolling_excess_return = -0.15`
- `promotion_max_strategy_drawdown = -0.35`
- `promotion_max_drawdown_gap_vs_benchmark = 0.08`

실전적으로 읽으면:

- ETF family는 AUM / spread 쪽 current operability contract가 추가로 강하게 걸린다.
- strict annual family는 benchmark / liquidity / validation / drawdown threshold가 더 핵심이다.

### 1-2. Promotion을 직접 갈라놓는 non-configurable review threshold

현재 `validation_status`, `rolling_review_status`, `out_of_sample_review_status`를 만드는 내부 기준은 아래 수준이다.

- validation drawdown gap:
  - watch: strategy max DD가 benchmark보다 `5%` 이상 더 나쁠 때
  - severe: `10%` 이상 더 나쁠 때
- rolling worst excess:
  - watch: `-10%`
  - severe: `-15%`
- rolling current underperformance streak:
  - watch: `3`
  - severe: `4`
- rolling underperformance share:
  - watch: `60%`
- recent / split-period deterioration:
  - watch: `-10%`
  - severe: `-15%`

즉 current gate는
"수익률이 높냐"보다
"benchmark-relative consistency가 충분히 깨끗하냐"를 훨씬 더 강하게 본다.

## 2. Current representative evidence가 말하는 것

Phase 14 rerun set `9`건 기준 current outcome은 다음이었다.

- `real_money_candidate = 1`
- `production_candidate = 2`
- `hold = 6`

중요한 관찰:

1. 현재 gate가 **절대 통과 불가능한 구조는 아니다**
   - `Value` raw winner는 지금도 `real_money_candidate`까지 올라간다.
2. 반복 `hold`는 전략 family 전반에 무작위로 퍼져 있지 않다
   - strict annual near-miss는 주로 `validation_caution`, `validation_policy_caution`
   - ETF aggressive near-miss는 `etf_operability_caution`
3. `rolling`이나 `out_of_sample`은 중요하지만,
   지금 로직에서는 **promotion의 1차 gate**라기보다
   deployment 해석을 더 보수적으로 만드는 downstream pressure에 가깝다
   - 실제로 `Value` raw winner는 `rolling = watch`, `oos = caution`이어도
     `promotion = real_money_candidate`다.

## 3. "factor가 적어서 hold가 되는가?"에 대한 현재 판단

### 결론

현재 evidence 기준으로는
**"factor 수가 적어서 hold가 반복된다"를 1차 원인으로 보긴 어렵다.**

### 이유 1. 현재 factor set만으로도 non-hold / real-money candidate가 이미 나온다

- `Value` strongest raw winner:
  - 현재 기본 strict value factor 조합만으로
  - `promotion = real_money_candidate`
  - 즉 factor library 자체가 너무 빈약해서 아무 것도 못 올리는 상태는 아니다.
- `GTAA` practical candidate:
  - factor 전략이 아니라 ETF momentum family지만
  - 현재 gate 안에서도 `production_candidate / watchlist_only`가 재현된다.

즉 current gate는 "아무 전략도 못 통과하는 gate"가 아니다.

### 이유 2. hold가 반복되는 위치가 factor 부족보다 validation 쪽에 더 가깝다

strict annual near-miss에서 반복된 직접 원인은:

- `validation_status = caution`
- `validation_policy_status = caution`

이건 "팩터가 더 많아야 한다"보다
"현재 구성 전략이 benchmark-relative consistency 기준에서 어떻게 읽히는가"
에 훨씬 더 가깝다.

### 이유 3. 현재 strict UI factor surface도 아주 작은 편은 아니다

현재 UI에서 노출되는 strict factor 옵션은:

- Quality: `10`개
- Value: `13`개

특히 value 쪽은 이미 classic valuation ratio 대부분을 열어둔 상태다.

- `book_to_market`
- `earnings_yield`
- `sales_yield`
- `ocf_yield`
- `fcf_yield`
- `operating_income_yield`
- `per`
- `pbr`
- `psr`
- `pcr`
- `pfcr`
- `ev_ebit`
- `por`

즉 value family에서 반복 `hold`를
"현재 factor 수가 너무 적어서"라고 보긴 어렵다.

## 4. 그래도 factor expansion은 왜 여전히 가치가 있나

이건 별개로 **충분히 가치 있다.**

이유는 현재 factor storage에는
UI에서 아직 안 여는 후보들이 더 있기 때문이다.

예시:

- quality / robustness 쪽 후보
  - `interest_coverage`
  - `ocf_margin`
  - `fcf_margin`
  - `gross_profit_growth`
  - `op_income_growth`
  - `net_income_growth`
  - `asset_growth`
  - `debt_growth`
  - `fcf_growth`
  - `shares_growth`
- deep value / balance-sheet 쪽 후보
  - `liquidation_value`
  - `net_debt_to_equity`
  - `gpa`
  - `dividend_payout`

즉 factor DB와 schema는 이미 꽤 넓고,
현재 strict UI는 그중 **보수적으로 선별된 subset**을 노출하고 있다.

## 5. 그럼 지금 바로 factor를 대거 추가하는 게 맞나

제 판단은 **지금 바로 대거 추가하는 건 순서상 이르다** 쪽이다.

### 이유

1. gate calibration 문제와 factor expansion 문제가 섞인다
   - 지금 threshold가 과보수적인지
   - 아니면 전략 계약이 약한지
   를 먼저 분리해야 한다.

2. search space가 너무 빨리 커지면 해석력이 떨어진다
   - candidate가 좋아져도
   - 그게 factor 개선 때문인지
   - gate가 우연히 통과된 건지
   분리가 어려워진다.

3. point-in-time safe expansion rule을 먼저 정해야 한다
   - stored factor라고 해도
   - strict annual에서 어떤 sign/normalization/ranking semantics로 읽을지
   먼저 정리해야 한다.

## 6. 추천 순서

### 지금 바로 할 것

1. current threshold inventory를 기준으로
   `promotion / shortlist calibration review`를 먼저 마무리
2. canonical case를 고정
   - `Value` raw winner
   - `Value` balanced near-miss
   - `Quality + Value` defensive non-hold
   - `GTAA` practical non-hold
3. 어떤 threshold가 실제로 과보수적인지 family별로 좁혀보기

### 그 다음 할 것

4. factor expansion candidate shortlist를 별도 문서로 열기
5. 우선 small controlled set만 추가
   - 예: quality 3~5개
   - value/deep-value 2~4개
6. `gate_snapshot` history가 쌓이는 상태에서
   같은 calibration contract로 rerun

## 7. 현재 추천 해석

- **hold의 1차 원인**:
  - `factor 부족`보다는 `validation / validation_policy / ETF operability` 쪽
- **factor expansion의 위치**:
  - 필요함
  - 하지만 calibration을 덮어쓰는 방식이 아니라
    별도 통제된 search workstream으로 여는 것이 맞음

## 한 줄 결론

지금은
**gate를 먼저 교정하고, 그 다음 factor를 넓히는 순서**가 가장 안전하다.

factor를 더 넣는 아이디어 자체는 좋지만,
현재 evidence 기준으로는
그게 반복 `hold`의 가장 직접적인 원인은 아니다.
