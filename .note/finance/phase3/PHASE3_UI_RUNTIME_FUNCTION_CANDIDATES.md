# Phase 3 UI Runtime Function Candidates

## 목적
이 문서는 Phase 4 전략 실행 UI가 직접 호출할 수 있는
최소 runtime function 후보를 정리한다.

핵심 목표:
- UI가 `BacktestEngine` 체인을 직접 구성하지 않게 한다
- price-only 전략 기준 최소 공개 함수 세트를 먼저 고정한다
- 이후 factor / fundamental 전략 확장 시 같은 구조로 넓힐 수 있게 한다

---

## 설계 원칙

### 1. UI는 engine 체이닝 세부사항을 몰라야 한다

UI는 아래와 같은 내부 실행 흐름을 직접 조합하면 안 된다.

- `load_ohlcv_from_db(...)`
- `add_ma(...)`
- `add_interval_returns(...)`
- `align_dates()`
- `slice(...)`
- `run(strategy)`

이 흐름은 runtime function 내부에 캡슐화하는 것이 맞다.

### 2. 첫 공개 경로는 price-only 전략으로 제한한다

현재 runtime에서 가장 안정적으로 검증된 경로는 price-only 전략이다.

따라서 Phase 4 first pass는 아래 전략만 직접 지원하는 것이 적절하다.

- Equal Weight
- GTAA
- Risk Parity Trend
- Dual Momentum

factor / fundamental 전략은 snapshot connection layer가 구현된 뒤 확장한다.

### 3. UI 호출 함수는 결과 bundle을 반환해야 한다

UI는 단순 result DataFrame 하나보다 다음 구조를 선호한다.

- 전략 결과 시계열
- 성과 요약
- 실행 메타데이터

즉 runtime function은 “전략 실행”만이 아니라
“UI에 전달 가능한 결과 bundle 생성”까지 염두에 두는 편이 자연스럽다.

---

## 후보 함수 레벨

### A. low-level generic runtime helper

후보 예시:

```python
run_price_strategy_from_db(
    strategy_name: str,
    tickers: list[str],
    start: str,
    end: str,
    timeframe: str = "1d",
    option: str = "month_end",
    interval: int | None = None,
    strategy_params: dict | None = None,
)
```

장점:
- UI 입장에서 호출점이 하나로 단순하다
- 전략 selector와 잘 맞는다

단점:
- 내부 분기 로직이 비대해지기 쉽다
- 전략별 입력 계약 차이를 숨기기 어렵다

현재 판단:
- 첫 구현부터 generic 하나로 몰아넣는 것은 아직 이르다

### B. strategy-specific runtime wrappers

후보 예시:

```python
run_equal_weight_backtest_from_db(...)
run_gtaa_backtest_from_db(...)
run_risk_parity_trend_backtest_from_db(...)
run_dual_momentum_backtest_from_db(...)
```

장점:
- UI 버튼/전략 선택과 연결이 직관적이다
- 전략별 파라미터를 명확히 드러낼 수 있다
- sample 함수와 runtime 공개 함수의 역할을 분리하기 쉽다

단점:
- 함수 수가 늘어난다

현재 판단:
- Phase 4 first pass의 기본 공개 방식으로 가장 적절하다

### C. shared result bundle builder

후보 예시:

```python
build_backtest_result_bundle(
    result_df: pd.DataFrame,
    *,
    strategy_name: str,
    input_params: dict,
    execution_mode: str = "db",
)
```

반환 후보:

```python
{
    "strategy_name": "...",
    "result_df": ...,
    "summary_df": ...,
    "chart_df": ...,
    "meta": {...},
}
```

장점:
- UI가 전략별 결과 shape 차이를 덜 신경 써도 된다
- 이후 API/UI 공통 반환 구조로 재사용하기 좋다

현재 판단:
- strategy-specific wrapper와 같이 설계하는 것이 좋다

---

## 권장 최소 공개 함수 세트

Phase 4 첫 구현에서는 아래 2단 구조를 권장한다.

### 1. strategy-specific runtime wrapper

예:

```python
run_equal_weight_backtest_from_db(...)
run_gtaa_backtest_from_db(...)
run_risk_parity_trend_backtest_from_db(...)
run_dual_momentum_backtest_from_db(...)
```

책임:
- 입력 파라미터 정리
- 내부 engine/runtime chain 실행
- 전략 result DataFrame 생성

### 2. shared result bundle builder

예:

```python
build_backtest_result_bundle(...)
```

책임:
- 성과 요약 계산
- UI 표시용 결과 구조 정리
- 메타데이터 부착

이 조합이 좋은 이유:
- 전략별 차이를 wrapper에서 드러낼 수 있다
- UI는 공통 bundle 형태를 받는다
- 이후 generic dispatcher로 수렴시키기 쉽다

---

## 비권장 방향

### 1. UI가 `sample.py`를 직접 호출

이유:
- sample은 example/smoke 성격이다
- UI 공개 경계로 쓰기엔 역할이 맞지 않다

### 2. UI가 `BacktestEngine` 체인을 직접 조합

이유:
- 프론트와 실행 로직 결합이 강해진다
- 전략별 전처리 차이가 UI로 새어 나온다

### 3. 첫 단계부터 factor/fundamental 전략까지 하나의 generic 함수에 통합

이유:
- snapshot connection layer가 아직 구현 전이다
- price-only와 factor/fundamental 전략의 입력 계약이 아직 다르다

---

## Phase 4 첫 구현 권장 순서

1. `run_equal_weight_backtest_from_db(...)`
2. `run_gtaa_backtest_from_db(...)`
3. `run_risk_parity_trend_backtest_from_db(...)`
4. `run_dual_momentum_backtest_from_db(...)`
5. `build_backtest_result_bundle(...)`

즉:
- 전략별 wrapper를 먼저 만들고
- UI는 그 wrapper를 호출하고
- 결과는 공통 bundle로 넘기는 구조가 좋다

---

## 다음 단계 전제

이 문서에서 아직 고정하지 않은 것:

- user-facing input set의 최소 범위
- result bundle의 구체적 필드
- 전략 selector 방식

이 항목들은 각각:

- `D-2 user-facing input set 초안 정리`
- `D-3 결과 반환 형태 초안 정리`

에서 이어서 고정한다.

---

## 결론

현재 기준에서 Phase 4 UI가 직접 부를 최소 runtime function 방향은 명확하다.

- sample 함수는 reference로 유지
- UI는 strategy-specific DB runtime wrapper를 사용
- 결과는 공통 bundle builder를 통해 정리

즉 첫 UI 공개 경계는
**“전략별 DB-backed runtime wrapper + 공통 result bundle”**
조합으로 시작하는 것이 가장 현실적이다.
