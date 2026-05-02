# Phase 3 UI Result Bundle Draft

## 목적
이 문서는 Phase 4 전략 실행 UI가 DB-backed runtime wrapper로부터
어떤 결과 구조를 받아야 하는지 최소 초안을 고정한다.

핵심 목표:
- 현재 `result_df`와 `portfolio_performance_summary(...)` 흐름을 최대한 재사용한다
- UI가 전략별 내부 실행 차이를 몰라도 되게 만든다
- 이후 single-strategy 화면에서 multi-strategy 비교 화면으로 확장하기 쉬운 구조를 택한다

---

## 설계 원칙

### 1. runtime wrapper는 DataFrame 하나만 반환하지 않는다

UI는 단순 `result_df`만 받아서는 불편하다.

추가로 필요한 것:
- 성과 요약
- 차트용 최소 데이터
- 실행 메타데이터

따라서 wrapper는 “전략 실행 결과”가 아니라
“UI 표시용 bundle”을 반환하는 편이 맞다.

### 2. 기존 성과 요약 함수를 최대한 재사용한다

현재 프로젝트에는 이미:

- `portfolio_performance_summary(...)`

가 있다.

따라서 first-pass bundle은 이 함수를 재사용하는 방향이 좋다.

### 3. single-strategy first, comparison later

Phase 4 first pass는 전략 하나를 실행하고 보여주는 화면이 우선이다.

그래서 반환 구조도 우선은 single-strategy 중심으로 설계하고,
후에 여러 bundle을 묶어 comparison 화면으로 확장하는 방향이 적절하다.

---

## 권장 최소 반환 구조

권장 반환 구조:

```python
{
    "strategy_name": "...",
    "result_df": ...,
    "summary_df": ...,
    "chart_df": ...,
    "meta": {...},
}
```

이 구조를 first-pass 기본형으로 권장한다.

---

## 필드별 의미

### 1. `strategy_name`

의미:
- UI 제목, 카드 라벨, 실행 이력 라벨에 사용할 전략명

예:
- `Equal Weight`
- `GTAA`
- `Risk Parity`
- `Dual Momentum`

### 2. `result_df`

의미:
- 전략 실행의 원본 결과 시계열

현재 기대 컬럼:
- `Date`
- `Total Balance`
- `Total Return`

전략에 따라 추가 컬럼:
- `End Ticker`
- `Next Ticker`
- `Cash`
- `Rebalancing`
- 기타 전략 상태 컬럼

현재 판단:
- UI의 상세 표와 디버깅용 source of truth는 `result_df`다

### 3. `summary_df`

의미:
- 성과 요약용 1-row DataFrame

현재 재사용 함수:

```python
portfolio_performance_summary(...)
```

현재 기대 컬럼:
- `Name`
- `Start Date`
- `End Date`
- `Start Balance`
- `End Balance`
- `CAGR`
- `Standard Deviation`
- `Sharpe Ratio`
- `Maximum Drawdown`

현재 판단:
- first-pass UI의 KPI card나 summary table은 이 DataFrame을 그대로 사용 가능하다

### 4. `chart_df`

의미:
- UI 차트에 바로 넣기 좋은 최소 시계열

권장 컬럼:
- `Date`
- `Total Balance`
- `Total Return`

현재 판단:
- 기술적으로는 `result_df[['Date', 'Total Balance', 'Total Return']]`의 얇은 view여도 충분하다
- UI 계층이 전략별 여분 컬럼을 매번 걸러내지 않게 별도 필드로 주는 편이 좋다

### 5. `meta`

의미:
- 실행 맥락 설명

권장 키:
- `execution_mode`
- `data_mode`
- `strategy_key`
- `tickers`
- `start`
- `end`
- `timeframe`
- `universe_mode`
- `preset_name`
- `warnings`

예시:

```python
{
    "execution_mode": "db",
    "data_mode": "db_backed",
    "strategy_key": "equal_weight",
    "tickers": ["VIG", "SCHD", "DGRO", "GLD"],
    "start": "2016-01-01",
    "end": "2026-03-20",
    "timeframe": "1d",
    "universe_mode": "manual_tickers",
    "preset_name": None,
    "warnings": [],
}
```

---

## first-pass에서 아직 필요 없는 필드

아래는 나중에 추가 가능하지만 first pass에서 꼭 필요하지는 않다.

### 1. `positions_df`

이유:
- 지금은 result_df 안에 전략별 상태 컬럼이 이미 일부 포함된다
- 별도 position table은 비교 UI나 drill-down 단계에서 더 유용하다

### 2. `trade_log_df`

이유:
- 현재 전략 결과 shape에서 반드시 분리된 trade log가 필요한 상태는 아니다
- 후속 phase에서 전략별 체결/리밸런싱 로그를 정교화할 때 고려

### 3. `debug_payload`

이유:
- 개발 중에는 유용하지만 product-facing first pass에는 과하다

---

## bundle builder 권장 책임

권장 helper:

```python
build_backtest_result_bundle(
    result_df,
    *,
    strategy_name,
    strategy_key,
    input_params,
    execution_mode="db",
)
```

책임:
- `summary_df` 생성
- `chart_df` 생성
- `meta` 조립
- 최소 validation 수행

예:
- `result_df`가 비어 있지 않은지
- `Date`, `Total Balance`, `Total Return`가 존재하는지

---

## 권장 single-strategy wrapper 반환 예시

예:

```python
bundle = run_equal_weight_backtest_from_db(
    tickers=["VIG", "SCHD", "DGRO", "GLD"],
    start="2016-01-01",
    end="2026-03-20",
)
```

반환 예시:

```python
{
    "strategy_name": "Equal Weight",
    "result_df": result_df,
    "summary_df": summary_df,
    "chart_df": chart_df,
    "meta": {
        "execution_mode": "db",
        "data_mode": "db_backed",
        "strategy_key": "equal_weight",
        "tickers": ["VIG", "SCHD", "DGRO", "GLD"],
        "start": "2016-01-01",
        "end": "2026-03-20",
        "timeframe": "1d",
        "warnings": [],
    },
}
```

---

## comparison 화면으로의 확장 방향

후속 phase에서 여러 전략을 비교하려면
single-strategy bundle 여러 개를 리스트로 묶는 방향이 좋다.

예:

```python
comparison_payload = {
    "runs": [bundle1, bundle2, bundle3],
}
```

이 방식의 장점:
- first-pass single bundle 구조를 그대로 재사용
- comparison UI는 `summary_df`들만 모아 표를 만들기 쉬움

---

## 현재 권장안

Phase 4 first-pass 결과 반환 구조:

1. `strategy_name`
2. `result_df`
3. `summary_df`
4. `chart_df`
5. `meta`

이 다섯 개면:
- 상세 표
- KPI 카드
- equity curve
- 실행 이력/입력 요약

을 모두 커버할 수 있다.

---

## 결론

현재 프로젝트 기준에서 UI runtime 반환 구조는
복잡한 API schema보다 먼저
**“result_df + summary_df + chart_df + meta”**
형태의 단순 bundle로 시작하는 것이 가장 적절하다.

이 구조는:
- 현재 코드와 잘 맞고
- sample/runtime path와도 자연스럽게 이어지고
- Phase 4 first-pass UI 구현에 필요한 정보를 충분히 제공한다.
