# Phase 14 ETF Operability Sensitivity Review First Pass

## 목적

- ETF family near-miss에서 repeatedly 등장한 `etf_operability_status`를
  **AUM / spread threshold 문제인지, current data coverage 문제인지** 분리해서 본다.
- 특히 `GTAA` practical candidate와 aggressive near-miss를 기준으로
  current operability gate가 실제로 어디서 갈리는지 first-pass evidence를 남긴다.

## 한 줄 결론

- 현재 ETF near-miss의 핵심은
  **AUM / spread threshold 자체보다 profile data coverage interpretation** 쪽이다.
- threshold를 완화해도 aggressive GTAA는 그대로 `operability = caution`에 남았다.

## 근거 코드

- `app/web/runtime/backtest.py::_build_etf_operability_policy_surface`
- `app/web/runtime/backtest.py::_build_promotion_decision`
- `app/web/runtime/backtest.py::run_gtaa_backtest_from_db`

## 1. Current code path 정리

### 1-1. current configurable threshold

ETF operability contract는 아래 두 값으로 시작한다.

- `promotion_min_etf_aum_b`
- `promotion_max_bid_ask_spread_pct`

default:

- `promotion_min_etf_aum_b = 1.0`
- `promotion_max_bid_ask_spread_pct = 0.005`

### 1-2. current derived coverage

operability surface는 각 ETF에 대해:

- `aum_b`
- `bid_ask_spread_pct`
- `clean_mask = aum_pass & spread_pass`
- `operability_data_mask = available_aum & available_spread`

를 만든다.

그리고:

- `clean_coverage = clean_mask.mean()`
- `data_coverage = operability_data_mask.mean()`

를 계산한다.

### 1-3. current status 판정

watch / caution 분기는 아래와 같다.

- `data_coverage < 1.0`
  - `watch_signals += etf_operability_partial_data_coverage`
- `data_coverage < 0.75`
  - `severe_signals += 1`
- AUM fail symbol 존재:
  - `watch_signals += etf_aum_below_policy`
  - `clean_coverage < 0.75`면 severe
- spread fail symbol 존재:
  - `watch_signals += etf_bid_ask_spread_above_policy`
  - `clean_coverage < 0.75`면 severe

판정:

- severe signal이 있으면 `caution`
- watch signal만 있으면 `watch`
- 없으면 `normal`

즉 current ETF gate는
**threshold fail뿐 아니라 profile data partial coverage도 직접 `caution`까지 올릴 수 있다.**

## 2. Representative rerun A: practical GTAA

대상 케이스:

- tickers:
  - `SPY`
  - `QQQ`
  - `GLD`
  - `LQD`
- `top = 2`
- `interval = 3`
- `score horizons = 1M, 3M`
- benchmark: `SPY`

threshold sweep:

| label | `Min ETF AUM` | `Max Spread` | `operability` | `promotion` | `deployment` |
| --- | --- | --- | --- | --- | --- |
| default | `1.0B` | `0.5%` | `normal` | `production_candidate` | `watchlist_only` |
| mid | `0.5B` | `1.0%` | `normal` | `production_candidate` | `watchlist_only` |
| disabled_like | `0.0B` | `100%` | `normal` | `production_candidate` | `watchlist_only` |

현재 meta:

- `etf_operability_clean_coverage = 100%`
- `etf_operability_data_coverage = 100%`
- `etf_operability_watch_signals = []`

읽는 법:

- practical GTAA는 threshold sensitivity가 거의 없다.
- 즉 current non-hold practical case는
  **이미 operability 기준을 안정적으로 통과하는 candidate**다.

## 3. Representative rerun B: aggressive GTAA near miss

대상 케이스:

- tickers:
  - `SPY, QQQ, SOXX, VUG, VTV, RSP, IAU, XLE, TIP, TLT, IEF, LQD, VNQ, EFA, GLD`
- `top = 2`
- `interval = 3`
- `score horizons = 1M, 3M, 6M`
- benchmark: `SPY`

threshold sweep:

| label | `Min ETF AUM` | `Max Spread` | `operability` | `promotion` | `deployment` |
| --- | --- | --- | --- | --- | --- |
| default | `1.0B` | `0.5%` | `caution` | `hold` | `blocked` |
| mid | `0.5B` | `1.0%` | `caution` | `hold` | `blocked` |
| disabled_like | `0.0B` | `100%` | `caution` | `hold` | `blocked` |

현재 meta:

- `etf_operability_watch_signals = ['etf_operability_partial_data_coverage']`
- `etf_operability_clean_coverage = 0.4`
- `etf_operability_data_coverage = 0.4`
- `validation = watch`

읽는 법:

- 이 케이스는 AUM / spread 기준을 느슨하게 해도 결과가 안 바뀐다.
- current blocker는
  **"일부 ETF의 current profile data가 충분하지 않다"**
  는 해석 자체다.

즉 aggressive GTAA near-miss에서 operability sensitivity는
threshold sweep보다
**data coverage 해석 rule**에 더 가깝다.

## 4. First-pass 해석

### 4-1. 현재 configurable sensitivity knob

ETF operator가 현재 직접 조절할 수 있는 값:

- `promotion_min_etf_aum_b`
- `promotion_max_bid_ask_spread_pct`

이 둘은 AUM / spread fail 여부를 바꾼다.

### 4-2. 현재 code-level sensitivity knob

이번 evidence 기준으로 더 중요한 fixed internal knob는 아래다.

- `data_coverage < 1.0`이면 watch
- `data_coverage < 0.75`이면 severe -> `caution`
- AUM/spread fail이 있더라도 severe는 `clean_coverage < 0.75`에서 강화

즉 ETF near-miss에서는
**partial data coverage rule이 사실상 1차 gate**처럼 작동한다.

## 5. Candidate calibration knobs

다음 calibration 후보는 아래 순서가 맞다.

1. `partial data coverage` watch/caution boundary
   - current:
     - `< 1.0 -> watch`
     - `< 0.75 -> caution`
   - 이유:
     - aggressive GTAA near-miss가 threshold 완화와 무관하게 여기서 고정된다.

2. missing-data interpretation
   - current:
     - missing data가 operability partial coverage로 바로 watch/caution에 반영된다
   - 질문:
     - current-date profile missing을 `watch`로만 둘지
     - 특정 family/portfolio size에서만 `caution`으로 볼지

3. coverage denominator
   - current:
     - 전체 ETF row 기준 mean
   - 질문:
     - selected/used ETF 중심으로 볼지
     - candidate pool 전체로 계속 볼지

4. AUM / spread thresholds
   - current evidence에서는 우선순위가 더 낮다
   - practical candidate는 이미 default를 통과했고,
     aggressive near-miss는 threshold 완화로도 안 풀렸다.

## 6. 결론

- ETF operability calibration의 다음 질문은
  **"AUM/spread 값을 얼마나 완화할까?"보다
  "partial profile data coverage를 실전 gate에서 어느 정도로 해석할까?"**
  쪽이 더 중요하다.
- 따라서 ETF family next step도 blanket loosening이 아니라
  **coverage interpretation review first**
  방향이 맞다.
