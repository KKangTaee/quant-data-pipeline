# Phase 3 Runtime Strategy Input Contract

## 목적
이 문서는 Phase 3 기준으로 전략 runtime이 실제로 어떤 입력 형태를 기대하는지 고정한다.

Phase 2의 loader 입력 계약이
“loader 공개 함수가 무엇을 받는가”에 초점이 있었다면,
이 문서는
“전략 실행 직전 runtime payload가 어떤 모양이어야 하는가”에 초점을 둔다.

---

## 1. 계약 레벨 구분

Phase 3에서는 입력 계약을 아래 3단계로 나눠서 본다.

1. loader input contract
   - loader 함수가 받는 인자
   - 예: `symbols`, `start`, `end`, `as_of_date`, `freq`

2. runtime connection contract
   - loader 결과를 전략 입력으로 연결하기 위한 중간 payload
   - 예: rebalance date별 snapshot dict

3. strategy input contract
   - 전략 클래스의 `run(...)`이 실제로 받는 입력 형태

현재 문서는 3번을 고정한다.

---

## 2. 현재 price-only 전략의 기본 입력 계약

현재 구현된 price-only 전략은 모두
`Strategy.run(dfs: dict)` 형태를 따른다.

여기서 `dfs`는 다음 구조다.

```python
{
    "AAPL": price_df,
    "MSFT": price_df,
    ...
}
```

각 `price_df`의 최소 요구 컬럼:
- `Date`
- `Close`

전략별 추가 요구 컬럼은 다르다.

공통 전제:
- `Date`는 datetime-like 이어야 한다
- 각 DataFrame은 오름차순 정렬 상태여야 한다
- `align_dates()`를 거친 뒤에는 티커 간 날짜 교집합이 맞춰져 있어야 한다
- frequency는 전략이 기대하는 리밸런싱 레벨과 맞아야 한다
  - 보통 월말 필터 후 monthly-like row sequence

---

## 3. 현재 전략별 최소 입력 계약

### 3-1. Equal Weight

입력 형태:
- `{ticker: price_df}` dict

최소 컬럼:
- `Date`
- `Close`

선행 처리 권장:
- `filter_by_period()`
- `align_dates()`
- optional `slice(...)`

비고:
- 가장 단순한 price-only 기준 전략

---

### 3-2. GTAA

입력 형태:
- `{ticker: price_df}` dict

최소 컬럼:
- `Date`
- `Close`
- `MA200`
- `1MReturn`
- `3MReturn`
- `6MReturn`
- `12MReturn`
- `AvgScore`

선행 처리 권장:
- `add_ma(200)`
- `filter_by_period()`
- `add_interval_returns([1,3,6,12])`
- `align_dates()`
- `slice(...)`
- `add_avg_score()`
- `interval(2)`

비고:
- warmup history가 부족하면 시작일이 밀릴 수 있다

---

### 3-3. Risk Parity Trend

입력 형태:
- `{ticker: price_df}` dict

최소 컬럼:
- `Date`
- `Close`
- `MA200`

선행 처리 권장:
- `add_ma(200)`
- `filter_by_period()`
- `align_dates()`
- `slice(...)`

비고:
- 전략 내부에서 최근 변동성을 계산하므로
  runtime은 리밸런싱 직전까지 충분한 과거 row를 보장해야 한다

---

### 3-4. Dual Momentum

입력 형태:
- `{ticker: price_df}` dict

최소 컬럼:
- `Date`
- `Close`
- `MA200`
- `12MReturn`

선행 처리 권장:
- `add_ma(200)`
- `filter_by_period()`
- `add_interval_returns([12])`
- `align_dates()`
- `slice(...)`

비고:
- cash proxy ticker가 포함될 수 있다
- warmup history가 부족하면 12M 모멘텀 계산이 깨진다

---

## 4. future factor / fundamental 전략의 기본 입력 계약

price-only 전략과 달리,
future factor / fundamental 전략은 기본 입력을
단순 `{ticker: price_df}` dict 하나로 보지 않는다.

권장 기준 입력 단위:

1. `price_dfs`
   - `{ticker: price_df}` dict
   - 이후 구간 수익률 계산용

2. `snapshot_by_date`
   - `{rebalance_date: snapshot_df}` dict
   - 종목 선택 / ranking / filtering용

3. `rebalance_dates`
   - runtime이 실제로 순회할 날짜 리스트

즉 최소 개념 계약은:

```python
runtime_payload = {
    "price_dfs": {...},
    "snapshot_by_date": {...},
    "rebalance_dates": [...],
}
```

현재 전략 인터페이스는 아직 이 payload를 직접 받지 않으므로,
다음 단계에서는 이 구조를 감싸는 connection helper 또는 새 runtime entrypoint가 필요하다.

---

## 5. snapshot_df 최소 컬럼 계약

future factor / fundamental 전략의 `snapshot_df`는
최소한 아래 메타 컬럼을 갖는 것이 좋다.

필수 메타 컬럼:
- `symbol`
- `rebalance_date`
- `as_of_date`

권장 메타 컬럼:
- `freq`
- `source_table`
- `pit_mode`

이후 전략별 데이터 컬럼:
- factor 전략:
  - `per`, `pbr`, `psr`, `roe`, ...
- fundamental 전략:
  - `total_revenue`, `net_income`, `total_assets`, ...
- custom statement 전략:
  - selected concept columns

---

## 6. runtime payload 생성 책임

### loader 책임
- raw / normalized DB read
- history / snapshot / matrix 반환

### runtime connection helper 책임
- rebalance dates 생성
- snapshot 조회 반복
- universe intersection
- 필요한 컬럼 결합
- strategy-friendly payload 생성

### strategy 책임
- ranking
- filtering
- allocation
- cash handling
- portfolio state update

즉 strategy는 snapshot query를 직접 수행하지 않는다.

---

## 7. Phase 4 UI 관점 최소 계약

Phase 4에서 UI가 eventually 호출하게 될 runtime entrypoint는
현재 기준으로 아래 입력 집합이면 충분하다.

공통 입력:
- `symbols` 또는 `universe_source`
- `start`
- `end`
- `strategy_name`

price-only 추가 입력:
- `timeframe`
- `option`

factor/fundamental 전략 추가 입력:
- `freq`
- `rebalance_freq`
- `pit_mode`

UI는 이 인자를 전달하고,
runtime entrypoint 내부에서:
- loader 호출
- connection helper 호출
- strategy 실행

순으로 이어지는 구조가 권장된다.

---

## 8. strict / broad 기본 규칙

product-facing runtime 기본값:
- strict PIT 선호

research helper / notebook 실험:
- broad 허용 가능

즉 future factor / fundamental 전략 runtime은
기본적으로 `strict`를 기본 모드로 설계하고,
`broad`는 명시적 override가 있을 때만 허용하는 것이 안전하다.

---

## 9. 현재 결론

현재까지 고정된 계약은 아래처럼 요약할 수 있다.

- price-only 전략:
  - `{ticker: price_df}` dict가 전략 직접 입력
- factor / fundamental 전략:
  - `price_dfs + snapshot_by_date + rebalance_dates`가 runtime 기본 payload
- loader는 전략 규칙을 몰라야 하고
- strategy는 DB 쿼리를 몰라야 한다

즉 앞으로의 핵심은
**rebalance-date snapshot payload를 안정적으로 만드는 connection layer 구현**이다.
