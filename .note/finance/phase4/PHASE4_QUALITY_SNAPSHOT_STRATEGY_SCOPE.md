# Phase 4 Quality Snapshot Strategy Scope

## 목적
이 문서는 Phase 4에서 첫 factor / fundamental 전략 후보로
`Quality Snapshot Strategy`를 선택한 뒤,
그 구현 범위를 product-facing 기준으로 고정하기 위한 문서다.

## 선택 이유

`Quality Snapshot Strategy`를 첫 전략으로 고른 이유는 다음과 같다.

1. valuation 전략보다 price attachment 의존성이 약하다
2. snapshot-first 구조를 설명하기 쉽다
3. first-pass UI에서 입력을 과하게 늘리지 않아도 된다
4. `nyse_factors`와 `nyse_fundamentals`에 이미 usable field가 있다

즉 첫 factor / fundamental 전략으로는
구조를 보여주기 좋고,
look-ahead / price-matching 설명도 valuation보다 단순하다.

---

## 전략 개념

기본 아이디어:
- 월말마다 quality snapshot을 조회한다
- quality score가 높은 종목을 고른다
- 선택된 종목을 다음 리밸런싱 구간 동안 equal weight로 보유한다

즉 first-pass는 아래 흐름이다.

```text
rebalance date
  -> quality snapshot load
  -> quality ranking
  -> top N selection
  -> next period equal-weight holding
```

---

## first-pass에서 사용할 quality 후보 컬럼

현재 loader / factor schema 기준으로 first-pass 후보는 아래가 현실적이다.

### 핵심 후보
- `roe`
- `roa`
- `gross_margin`
- `operating_margin`

### 보조 후보
- `current_ratio`
- `debt_ratio`
- `interest_coverage`

현재 권장 first-pass 묶음:
- `roe`
- `gross_margin`
- `operating_margin`
- `debt_ratio`

이유:
- profitability / quality / leverage를 동시에 담을 수 있다
- 의미 설명이 비교적 직관적이다
- first-pass score 조합이 과하게 복잡하지 않다

---

## first-pass score 방식

현재 권장 방식:
- 높은 값이 좋은 factor:
  - `roe`
  - `gross_margin`
  - `operating_margin`
- 낮은 값이 좋은 factor:
  - `debt_ratio`

score 방식 first-pass 권장:
1. factor별 cross-sectional rank
2. 방향성 반영
3. 단순 평균 score

이 방식의 장점:
- 구현이 단순하다
- UI 설명이 쉽다
- factor별 missingness를 비교적 정직하게 다룰 수 있다

이번 단계에서는 z-score보다 rank-average가 더 적합하다.

---

## universe와 frequency

현재 first-pass 권장:
- universe: `NYSE Stocks` 또는 사용자가 지정한 manual tickers
- rebalance frequency: `monthly`
- factor freq: `annual`

이유:
- quarterly까지 열면 snapshot turnover와 missingness 설명이 더 복잡해진다
- annual quality snapshot이 첫 전략으로는 더 안정적이다

즉 first-pass는:
- `monthly rebalance`
- `annual factor snapshot`
조합이 가장 적절하다.

---

## loader / runtime 연결 원칙

이 전략은 아래 3단 구조를 따른다.

1. loader
   - `load_factor_snapshot(...)`
2. runtime connection helper
   - rebalance date 생성
   - snapshot 조회
   - investable universe intersection
   - score 생성
3. strategy runner
   - top N 선택
   - 다음 구간 equal-weight holding

현재 단계에서는
새 전략 클래스보다 먼저
runtime wrapper와 connection helper를 명확히 정의하는 것이 맞다.

---

## first-pass에서 일부러 제외하는 것

이번 전략에서 아직 열지 않을 것:
- multi-factor weighting customization
- sector neutrality
- quarterly snapshot mode
- strict statement-driven custom factor
- optimizer 기반 weighting
- long/short mode

즉 first-pass 목표는
`quality snapshot ranking -> top N equal weight`
까지만 여는 것이다.

---

## 결론

Phase 4 첫 factor / fundamental 전략은
`Quality Snapshot Strategy`로 진행한다.

first-pass 기본 형태는:
- annual quality factor snapshot
- monthly rebalance
- top N selection
- equal-weight holding

다음 구현 직전 남은 핵심 결정은:
- product-facing 기본 snapshot 모드를 `broad research`로 둘지
- 아니면 stricter PIT 제약을 먼저 더 얹을지
이다.
