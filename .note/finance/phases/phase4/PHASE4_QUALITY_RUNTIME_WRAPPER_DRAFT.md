# Phase 4 Quality Runtime Wrapper Draft

## 목적
이 문서는 `Quality Snapshot Strategy`를 UI에 연결하기 위한
first public runtime wrapper의 초안을 정리한다.

## 권장 공개 함수

```python
run_quality_snapshot_backtest_from_db(
    *,
    tickers: list[str] | None = None,
    start: str,
    end: str,
    factor_freq: str = "annual",
    rebalance_freq: str = "monthly",
    quality_factors: list[str] | None = None,
    top_n: int = 10,
    universe_mode: str = "preset",
    preset_name: str | None = None,
    snapshot_mode: str = "broad_research",
)
```

---

## first-pass 입력 설명

### 필수 입력
- `start`
- `end`
- `top_n`

### universe 입력
- `tickers`
- 또는 `universe_mode + preset_name`

### factor 입력
- `quality_factors`

first-pass 기본값 권장:
```python
["roe", "gross_margin", "operating_margin", "debt_ratio"]
```

### mode 입력
- `factor_freq`
  - first-pass 권장 기본값: `annual`
- `rebalance_freq`
  - first-pass 권장 기본값: `monthly`
- `snapshot_mode`
  - 다음 선택이 필요한 항목

---

## 권장 반환 형태

price-only 전략과 동일하게 result bundle로 반환한다.

```python
{
    "strategy_name": "Quality Snapshot",
    "result_df": ...,
    "summary_df": ...,
    "chart_df": ...,
    "meta": ...,
}
```

추가 meta 권장 항목:
- `factor_freq`
- `rebalance_freq`
- `quality_factors`
- `top_n`
- `snapshot_mode`
- `selected_count`

---

## 내부 연결 개요

```text
run_quality_snapshot_backtest_from_db
  -> load_price_history / price runtime prep
  -> build rebalance dates
  -> load_factor_snapshot at each rebalance date
  -> build quality score
  -> select top N
  -> build next-period holdings
  -> result bundle
```

---

## 현재 남은 핵심 결정

이 wrapper를 실제 구현하기 전에
`snapshot_mode` 기본값을 정해야 한다.

선택지는 사실상 두 가지다.

1. `broad_research`
- 현재 `nyse_factors` snapshot을 그대로 사용
- 구현이 빠르다
- first-pass 전략을 가장 빨리 열 수 있다
- strict PIT는 아니다

2. `strict_later` 전제
- product-facing first strategy도 stricter PIT 경계를 먼저 더 확인한 뒤 연다
- 신뢰도는 높아진다
- 하지만 구현 진입 속도는 느려진다

현재 현실적인 기본값은 `broad_research`다.

단, UI와 문서에는 이 전략이
`research-oriented quality snapshot strategy`
임을 명확히 표시해야 한다.
