# Phase 3 First Loader Implementation Order

## 목적
이 문서는 Phase 3에서
첫 번째 loader 구현을 어떤 순서로 진행할지 고정하기 위한 문서다.

관련 문서:
- `.note/finance/phase3/PHASE3_INITIAL_LOADER_IMPLEMENTATION_SET.md`
- `.note/finance/phase3/PHASE3_LOADER_MODULE_PATH.md`

---

## 1. 기본 결론

Phase 3 첫 구현 순서는 아래로 고정한다.

1. `load_universe(...)`
2. `load_price_history(...)`
3. `load_price_matrix(...)`
4. runtime adapter helper

즉:
- 먼저 symbol resolution을 안정화하고
- 그 다음 가격 long-form loader
- 그 다음 matrix loader
- 마지막으로 기존 전략 입력 형태와 연결하는 adapter

순서로 진행한다.

---

## 2. 왜 이 순서인가

### 2-1. `load_universe(...)`를 먼저 하는 이유

- 모든 loader의 공통 진입점이기 때문
- `symbols` / `universe_source` 규칙을 여기서 먼저 고정해야
  이후 price loader가 단순해진다

### 2-2. `load_price_history(...)`를 두 번째로 두는 이유

- DB-backed 첫 전략 실행에서 가장 직접적으로 필요하다
- 기존 `finance.data.data.load_ohlcv_many_mysql(...)`를 감싸기 쉽다
- long-form이 가장 범용적이다

### 2-3. `load_price_matrix(...)`를 세 번째로 두는 이유

- history loader 위에 비교적 쉽게 구축 가능하다
- momentum / relative strength / cross-sectional 계산의 기반이 된다

### 2-4. runtime adapter helper를 네 번째로 두는 이유

- 현재 전략 코드는 ticker별 dict + `Date`, `Close` 같은 컬럼명을 기대한다
- loader 출력과 기존 전략 입력 사이의 bridging이 마지막 연결점이 된다

---

## 3. 구현 순서별 산출물

### Step 1. Universe Loader
- `finance/loaders/universe.py`
- `load_universe(...)`

### Step 2. Price History Loader
- `finance/loaders/price.py`
- `load_price_history(...)`

### Step 3. Price Matrix Loader
- `finance/loaders/price.py`
- `load_price_matrix(...)`

### Step 4. Runtime Adapter
- loader output -> existing strategy input 변환 helper

---

## 4. 후속 순서

위 4개가 끝난 뒤 다음 순서:

5. `load_fundamentals(...)`
6. `load_factors(...)`
7. `load_statement_values(...)`
8. `load_statement_snapshot_strict(...)`

---

## 결론

Phase 3의 첫 구현 순서는
"universe -> price history -> price matrix -> runtime adapter"
로 고정한다.

이 순서가 가장 짧고 안전하게
DB-backed 첫 전략 실행 경로를 여는 순서다.
