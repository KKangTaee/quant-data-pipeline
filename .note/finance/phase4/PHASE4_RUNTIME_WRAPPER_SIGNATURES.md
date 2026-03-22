# Phase 4 Runtime Wrapper Signatures

## 목적
이 문서는 Phase 4 첫 백테스트 UI가 직접 호출할
public runtime wrapper 시그니처를 고정한다.

현재 범위:
- first public strategy는 `Equal Weight`
- first data mode는 `DB-backed`

---

## 현재 결정

Phase 4 first pass에서는
UI가 `sample.py`나 `BacktestEngine` 체인을 직접 호출하지 않는다.

대신 아래 2단 구조를 사용한다.

1. strategy-specific public wrapper
2. shared result bundle builder

구현 위치:
- `app/web/runtime/backtest.py`

---

## 1. Shared Result Bundle Builder

현재 공개 helper:

```python
build_backtest_result_bundle(
    result_df,
    *,
    strategy_name: str,
    strategy_key: str,
    input_params: dict,
    execution_mode: str = "db",
    data_mode: str = "db_backed",
    summary_freq: str = "M",
    warnings: list[str] | None = None,
)
```

책임:
- `result_df` 최소 validation
- `summary_df` 생성
- `chart_df` 생성
- UI 표시용 `meta` 조립

반환 구조:

```python
{
    "strategy_name": "...",
    "result_df": ...,
    "summary_df": ...,
    "chart_df": ...,
    "meta": {...},
}
```

---

## 2. First Public Strategy Wrapper

현재 공개 wrapper:

```python
run_equal_weight_backtest_from_db(
    *,
    tickers: Sequence[str] | None = None,
    start: str | None = None,
    end: str | None = None,
    timeframe: str = "1d",
    option: str = "month_end",
    rebalance_interval: int = 12,
    universe_mode: str = "manual_tickers",
    preset_name: str | None = None,
)
```

의미:
- `tickers`: 실행 대상 종목 리스트
- `start`, `end`: 백테스트 구간
- `timeframe`: DB OHLCV 조회 주기
- `option`: 현재는 `month_end` 중심
- `rebalance_interval`: 리밸런싱 간격
- `universe_mode`, `preset_name`: UI 메타데이터용

현재 판단:
- first pass에서는 이 wrapper 하나를 기준 경계로 삼는 것이 적절하다
- 이후 GTAA / Risk Parity / Dual Momentum도 같은 패턴으로 확장한다

---

## 왜 sample 함수를 직접 공개하지 않는가

`finance/sample.py`는 여전히:
- example
- smoke test
- reference path

성격을 유지한다.

반면 Phase 4 UI는:
- stable public boundary
- input normalization
- bundle shape consistency

가 더 중요하다.

즉:
- sample은 reference
- runtime wrapper는 UI public boundary

로 역할을 분리한다.

---

## 다음 연결 단계

이 문서에서 시그니처가 고정됐으므로,
다음 구현은 아래 순서로 진행한다.

1. Equal Weight 실행 form
2. wrapper 호출
3. bundle 결과 표시
4. 빈 결과 / 에러 규칙 추가

---

## 결론

Phase 4 first pass의 public runtime boundary는
현재 아래 조합으로 고정됐다.

- `run_equal_weight_backtest_from_db(...)`
- `build_backtest_result_bundle(...)`

즉 백테스트 탭은
이 wrapper 경계 위에서 실행 UI를 구현한다.
