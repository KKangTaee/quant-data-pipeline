# Phase 14 ETF Operability Data Coverage Interpretation Review First Pass

## 목적

- Phase 14 ETF operability sensitivity review 다음 단계로,
  ETF family repeated `hold`를 고정시키는
  **partial data coverage 해석 규칙**을 별도로 읽는다.
- 특히 아래 질문에 답하기 위한 문서다.
  - 왜 AUM / spread threshold를 완화해도 aggressive ETF candidate는 여전히 `hold`인가?
  - current operability에서 다시 봐야 할 해석 규칙은 무엇인가?

## 이번 문서의 한 줄 결론

- ETF repeated `hold`의 핵심은
  AUM / spread 숫자 자체보다
  **`partial data coverage`를 언제 `caution`으로 해석하느냐**에 더 가깝다.
- 따라서 다음 calibration 실험은
  threshold sweep보다
  **coverage boundary / missing-data semantics / denominator**
  를 먼저 보는 쪽이 더 효과적이다.

## 근거 코드

- `app/web/runtime/backtest.py::_build_etf_operability_policy_surface`
- `app/web/runtime/backtest.py::_build_promotion_decision`

## 1. Current interpretation rule

현재 ETF operability는 아래 두 coverage를 만든다.

- `data_coverage`
  - usable AUM + usable spread 데이터가 모두 있는 ETF 비율
- `clean_coverage`
  - AUM / spread policy를 둘 다 통과한 ETF 비율

### current 분기

- `data_coverage < 1.0`
  - `watch`
- `data_coverage < 0.75`
  - severe -> `caution`
- AUM fail 또는 spread fail 존재
  - `watch`
- AUM/spread fail이 있고 `clean_coverage < 0.75`
  - severe -> `caution`

즉 current ETF gate는
**threshold fail 없이도 partial data coverage만으로 `caution`까지 갈 수 있다.**

## 2. Representative evidence

### Case A. practical GTAA non-hold

대상:

- `SPY, QQQ, GLD, LQD`
- `top = 2`
- `interval = 3`
- score horizons `1M, 3M`

결과:

- `promotion = production_candidate`
- `deployment = watchlist_only`
- `etf_operability = normal`
- `etf_operability_clean_coverage = 100%`
- `etf_operability_data_coverage = 100%`

해석:

- practical candidate는 current default contract를 이미 깨끗하게 통과한다.
- 즉 이 케이스는 AUM / spread sensitivity보다
  **coverage interpretation의 영향을 거의 받지 않는 reference**다.

### Case B. aggressive GTAA near miss

대상:

- `SPY, QQQ, SOXX, VUG, VTV, RSP, IAU, XLE, TIP, TLT, IEF, LQD, VNQ, EFA, GLD`
- `top = 2`
- `interval = 3`
- score horizons `1M, 3M, 6M`

결과:

- `promotion = hold`
- `deployment = blocked`
- `validation = watch`
- `etf_operability = caution`
- `etf_operability_watch_signals = ['etf_operability_partial_data_coverage']`
- `etf_operability_clean_coverage = 0.4`
- `etf_operability_data_coverage = 0.4`

해석:

- 이 케이스는 AUM / spread threshold를 사실상 꺼도 결과가 안 바뀐다.
- current blocker는
  **현재 시점 asset profile data가 부분적으로 비어 있다는 해석 자체**다.

## 3. 지금 무엇이 1차 blocker인가

current ETF repeated hold를 더 직접적으로 좌우하는 순서는 이렇다.

### 1순위

- `partial data coverage < 75% -> caution`

이유:

- aggressive GTAA near miss는 threshold sweep과 무관하게 여기서 고정된다.

### 2순위

- missing-data semantics

이유:

- 현재는 current-date profile missing이 곧바로 operability signal로 올라간다.
- 하지만 이걸 always-risk로 볼지,
  informational watch로만 둘지를 분리해서 볼 여지가 있다.

### 3순위

- coverage denominator

이유:

- 현재는 전체 candidate ETF row 기준 mean이다.
- 하지만 실제 전략이 쓰는 top asset 기준으로 읽을지,
  full candidate pool 기준으로 계속 읽을지는 실무 해석에 차이가 크다.

### 우선순위 낮음

- `promotion_min_etf_aum_b`
- `promotion_max_bid_ask_spread_pct`

이유:

- practical reference는 이미 default를 통과한다.
- aggressive near-miss는 threshold를 완화해도 그대로 막힌다.

## 4. 다음 calibration experiment 후보

이번 first pass 기준으로 다음 실험 후보는 아래 순서가 자연스럽다.

1. `data_coverage` watch/caution boundary review
   - current:
     - `< 1.0 -> watch`
     - `< 0.75 -> caution`
   - 질문:
     - ETF family practical contract에서는 `0.75`가 너무 보수적인가?

2. missing-data interpretation review
   - current:
     - current-date profile missing이 바로 operability signal
   - 질문:
     - missing data만으로 `caution`까지 올리는 것이 맞는가?

3. denominator review
   - current:
     - full candidate ETF 기준 mean
   - 질문:
     - selected/top asset 기준 coverage가 더 실무적인가?

4. threshold sweep은 2차 실험으로 유지
   - 현재 evidence상 AUM / spread 완화는 1차 blocker를 안 건드린다.

## 5. 이번 단계에서 아직 하지 않는 것

- AUM / spread default를 즉시 바꾸는 작업
- current snapshot operability를 PIT operability처럼 해석하는 작업
- operability unavailable semantics 완화

## 한 줄 결론

ETF next calibration은
**`Min ETF AUM`이나 `Max Spread` 숫자 조정보다
`partial data coverage`를 언제 `caution`으로 읽을지**
를 먼저 다시 보는 단계다.
