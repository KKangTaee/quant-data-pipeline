# Phase 3 Factor / Fundamental Runtime Connections

## 목적
이 문서는 future factor / fundamental 전략이 현재 loader / runtime 구조에
어떻게 연결되어야 하는지 기준 경계를 고정한다.

---

## 현재 상태

현재 Phase 3에서 runtime이 직접 검증된 경로는 price-only 전략이다.

현재 가능한 것:
- `load_price_history(...)`
- `load_price_matrix(...)`
- `load_price_strategy_dfs(...)`
- `BacktestEngine.load_ohlcv_from_db(...)`
- `*_from_db` sample 함수

즉 현재 runtime은 `{ticker: DataFrame}` 형태의 가격 시계열 dict를
전략 입력으로 넘기는 구조에 맞춰져 있다.

반면 factor / fundamental 전략은 보통 다음 입력이 추가로 필요하다.

- 특정 `as_of_date` 기준 snapshot
- price universe와 accounting universe의 교집합
- 시점 기준 point-in-time 안전한 factor / statement 값
- 필요 시 rebalance date별 panel 재구성

따라서 price-only 전략과 같은 방식으로 단순히 `engine.load_*()` 하나만 추가해서는
충분하지 않다.

---

## 연결 원칙

### 1. loader는 raw read / normalized read까지만 담당

loader 계층의 책임:
- DB 조회
- symbols / dates / freq 정규화
- snapshot / history / matrix 형태 반환

loader 계층이 하지 않을 일:
- 전략별 ranking
- investable filter
- rebalance loop
- portfolio state update

즉 factor / fundamental loader는 전략 규칙을 품지 않는다.

---

### 2. runtime connection layer가 price와 accounting을 결합

price-only 전략과 달리, factor / fundamental 전략에는 중간 연결 계층이 필요하다.

이 계층의 책임:
- rebalance dates 생성
- 각 rebalance date에서 `as_of_date` 기준 snapshot 조회
- price data와 factor / fundamental snapshot 병합
- 전략이 바로 쓸 수 있는 runtime payload 생성

즉 향후 runtime 경로는 아래처럼 분리하는 것이 맞다.

```text
DB
  -> loader
  -> runtime connection layer
  -> strategy
```

현재 price-only 경로는 사실상 connection layer가 거의 비어 있는 특수 케이스다.

---

### 3. factor / fundamental 전략은 snapshot-first로 다룬다

future factor / fundamental 전략에서 기본 단위는
일봉 row가 아니라 `rebalance-date snapshot`이다.

예:
- 월말 리밸런싱 전략
- 분기 리밸런싱 전략
- annual value / quality 전략

이 경우 필요한 것은:
- rebalance date `t`
- `as_of_date <= t` 기준 snapshot
- investable universe
- 선택된 종목들의 이후 구간 수익률 계산용 price path

즉 입력 계약은:

1. `price history`
2. `fundamental / factor snapshot`
3. `rebalance schedule`

세 축으로 나눠 보는 것이 자연스럽다.

---

## 권장 runtime payload

future factor / fundamental 전략용 연결 계층은
최소한 아래 payload를 만들 수 있어야 한다.

### option A. date -> snapshot DataFrame dict

```python
{
    "2024-03-29": snapshot_df,
    "2024-04-30": snapshot_df,
    ...
}
```

장점:
- 전략별 ranking / filtering 구현이 단순
- monthly/quarterly rebalance 전략에 잘 맞음

### option B. normalized long-form runtime table

필수 컬럼 예시:
- `rebalance_date`
- `symbol`
- `price_date`
- `as_of_date`
- factor columns
- fundamental columns
- next-period return helper columns

장점:
- 다양한 factor 전략에 재사용 가능
- 나중에 UI/analysis 쪽으로 넘기기 쉬움

현재 단계에서는 option A가 구현 시작점으로 더 적합하다.

---

## 현재 loader와의 연결 포인트

현재 준비된 loader 기준으로 보면:

### fundamentals
- `load_fundamentals(...)`
- `load_fundamental_snapshot(...)`

연결 방식:
- `load_fundamental_snapshot(symbols=..., as_of_date=..., freq=...)`
- rebalance date별 snapshot dict 생성

### factors
- `load_factors(...)`
- `load_factor_snapshot(...)`
- `load_factor_matrix(...)`

연결 방식:
- factor ranking 전략은 snapshot 기반 조회가 기본
- matrix는 연구/비교/시각화 쪽에 더 적합

### detailed statements
- `load_statement_values(...)`
- `load_statement_snapshot_strict(...)`

연결 방식:
- 직접 전략 입력으로 쓰기보다는
  custom factor builder 또는 factor preprocessing 단계에 더 가깝다

---

## engine 확장 원칙

현재 `BacktestEngine`은 price dict 중심 체이닝 엔진이다.

따라서 factor / fundamental 전략을 위해 바로 해야 할 일은
`engine.py`에 ad hoc 메서드를 계속 추가하는 것이 아니다.

우선순위:
1. runtime connection helper 정의
2. 그 helper가 만드는 payload 형태 확정
3. 필요 시 engine에 최소 orchestration 메서드 추가

즉 `engine.py`는 마지막 단계에서 얇게 연결하는 것이 맞다.

---

## sample 확장 원칙

future sample 함수는 아래 순서를 따르는 것이 좋다.

1. universe 결정
2. price history load
3. factor/fundamental snapshot connection
4. strategy run
5. summary / display

예상 함수 예시:
- `get_value_factor_from_db(...)`
- `get_quality_factor_from_db(...)`
- `get_multi_factor_from_db(...)`

이 함수들은 price-only sample과 달리
중간에 snapshot connection helper를 반드시 거치는 구조가 될 가능성이 높다.

---

## 다음 구현 전제

다음 단계에서 구현 전에 먼저 고정해야 할 것:

1. rebalance schedule 생성 규칙
2. snapshot payload shape
3. universe intersection 정책
4. missing factor / fundamental row 처리 규칙
5. strict PIT와 broad research 모드 중 어떤 쪽을 기본 runtime으로 삼을지

현재 기준 권장:
- product-facing runtime 기본값은 strict PIT 쪽으로 설계
- broad mode는 research helper 성격으로 남김

---

## 결론

future factor / fundamental 전략은
현재 price-only runtime처럼 단순 engine load 체이닝만으로 연결하지 않는다.

핵심 연결 포인트는:
- loader
- snapshot connection helper
- strategy

의 3단 구조다.

즉 다음 구현의 핵심은 새로운 전략 클래스보다 먼저
**rebalance-date snapshot connection layer**를 정의하는 것이다.
