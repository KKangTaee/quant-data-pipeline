# Phase 4 Strict Annual Large-Universe Calendar Fix First Pass

## 목적
`Quality Snapshot (Strict Annual)`과 `Value Snapshot (Strict Annual)`을
`US Statement Coverage 300` 같은 대형 주식 유니버스에서도
실제 전략처럼 보이게 만드는 첫 수정 기록이다.

이전 상태에서는 statement coverage보다도
price input shaping 방식이 더 큰 문제였다.

---

## 문제 요약

기존 strict annual public path는 snapshot 전략인데도
price input을 만드는 과정에서 여전히:

- `filter_by_period()`
- `align_dates()`

를 사용했다.

이 때문에 large stock universe에서는
모든 심볼의 공통 날짜 교집합만 남게 되었고,
`US Statement Coverage 300`의 경우 실제 공통 monthly date가
`2025-12-31 ~ 2026-02-27`의 `3개` row로 줄어들었다.

즉 strategy result가 sparse하게 보이던 주원인은
annual statement coverage 자체보다
full-date intersection이었다.

---

## 수정 방향

strict annual 계열 snapshot 전략은
ETF/소수 price-only 전략과 다르게,
모든 심볼의 완전한 공통 가격 이력을 요구하지 않는다.

따라서 first-pass fix는 다음처럼 잡았다.

1. snapshot 전략용 price input builder를 별도로 둔다
2. period filter는 유지한다
3. 대신 마지막 정렬은 `date union calendar`로 맞춘다
4. 미상장/미가용 구간은 `NaN`으로 남긴다
5. 리밸런싱 시점에는 `Close`가 있는 심볼만 investable universe로 본다

---

## 코드 변경

### 1. union-calendar helper 추가
- `finance/transform.py`
  - `align_dfs_by_date_union(...)`

역할:
- 모든 df의 날짜 합집합 calendar 생성
- 각 심볼 df를 해당 calendar에 reindex
- `Ticker`, `Dividends`, `Stock Splits` 같은 일부 컬럼만 기본값 보정

### 2. snapshot 전략 price builder 분리
- `finance/sample.py`
  - `_build_snapshot_strategy_price_dfs(...)`

적용 대상:
- `get_quality_snapshot_from_db(...)`
- `get_statement_quality_snapshot_from_db(...)`
- `get_statement_quality_snapshot_shadow_from_db(...)`
- `get_statement_value_snapshot_shadow_from_db(...)`

### 3. snapshot 전략 가용성 처리 보강
- `finance/strategy.py`
  - `quality_snapshot_equal_weight(...)`

보강 내용:
- `Close`가 `NaN`인 심볼은 해당 rebalance에서 ranking 대상 제외
- held position의 current close가 비면
  해당 period return은 `0.0`으로 두어 balance가 `NaN`으로 망가지지 않게 함

---

## 검증 결과

### 수정 전
- `US Statement Coverage 300`
- `2016-01-01 ~ 2026-03-20`
- `month_end`

결과:
- common aligned rows: `3`
- first active date: `2025-12-31`

### 수정 후

#### Quality strict 300
- rows: `124`
- first date: `2016-01-29`
- first active date: `2016-01-29`
- active rows: `124`
- median selected: `10`
- runtime: `9.086s`
- end balance: `73778.4`

#### Quality strict 100
- first active date: `2016-01-29`
- active rows: `124`
- runtime: `3.320s`
- end balance: `79295.2`

#### Value strict 300
- first active date: `2021-08-31`
- active rows: `57`
- runtime: `9.165s`
- end balance: `20931.1`

#### Sample-universe parity regression check
- optimized strict annual path:
  - `0.322s`
  - `End Balance = 93934.6`
- prototype rebuild path:
  - `16.793s`
  - `End Balance = 93934.6`

즉:
- large-universe sparse issue는 실질적으로 해결되었고
- sample-universe parity도 유지되었다.

---

## 해석

이제 `US Statement Coverage 300`이 sparse하게 보이는 핵심 원인은
full intersection에서 union calendar로 교체되면서 제거되었다.

다만 다음 사실은 그대로 남아 있다.

- statement coverage는 완전 균일하지 않다
- `fully usable` quality factor row 수는 시점별로 달라진다
- valuation 계열은 shares fallback 품질에 영향을 받는다

즉 이번 수정은:
- strategy input shape 문제를 해결한 것
이지,
- 모든 factor missingness를 해결한 것은 아니다.

---

## 다음 단계

이후 자연스러운 후속 작업은:

1. strict annual family의 broad vs strict 역할을 UI에서 더 명확히 설명
2. `Quality` / `Value` strict 결과를 실제로 비교 평가
3. 다음 strict multi-factor 후보 (`Quality + Value`) 검토
