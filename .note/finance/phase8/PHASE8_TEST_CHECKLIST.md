# Phase 8 Test Checklist

## 1. Single Strategy - Quarterly Value

- `Backtest > Single Strategy`
- strategy:
  - `Value Snapshot (Strict Quarterly Prototype)`
- preset:
  - `US Statement Coverage 100`

확인 포인트:
- `Price Freshness Preflight`가 보이는지
- `Statement Shadow Coverage Preview`가 보이는지
- 실행이 성공하는지
- `Selection History`가 열리는지
- `Interpretation` 탭이 보이는지

## 2. Single Strategy - Quarterly Quality + Value

- `Backtest > Single Strategy`
- strategy:
  - `Quality + Value Snapshot (Strict Quarterly Prototype)`
- preset:
  - `US Statement Coverage 100`

확인 포인트:
- 실행이 성공하는지
- `Selection History`가 열리는지
- quality/value factor 둘 다 meta에 남는지
- `Interpretation` 탭이 보이는지

## 3. Single Strategy - Manual Small Universe

- 각 quarterly prototype 3종에 대해
  - `AAPL,MSFT,GOOG`
  - `2016-01-01 -> today`
  - `month_end`

확인 포인트:
- 실행이 성공하는지
- early period가 완전히 빈 결과로만 보이지는 않는지
- 필요 시 warning이 늦은 active start를 설명하는지

## 4. Compare - Quarterly Family Exposure

- `Backtest > Compare & Portfolio Builder`
- 다음 중 2~4개 선택:
  - `Quality Snapshot (Strict Quarterly Prototype)`
  - `Value Snapshot (Strict Quarterly Prototype)`
  - `Quality + Value Snapshot (Strict Quarterly Prototype)`
  - annual strict family 1개 이상

확인 포인트:
- quarterly strategies가 compare options에 보이는지
- 각 전략의 expander가 열리는지
- preset / top N / factor / trend / regime 입력이 전략별로 따로 보이는지

## 5. Compare Execution

- quarterly strategy 하나 이상 포함해서 compare 실행

확인 포인트:
- summary compare가 정상인지
- focused strategy drilldown이 정상인지
- quarterly focused strategy에서 `Selection Interpretation`이 정상인지

## 6. History / Prefill

- quarterly single strategy 실행 후
  - `History` 탭 이동

확인 포인트:
- record가 저장되는지
- `Load Into Form`이 동작하는지
- `Run Again`이 동작하는지
- quarterly value / quarterly multi-factor 설정값이 다시 채워지는지

## 7. Meta / Context

- quarterly single 또는 compare 실행 후

확인 포인트:
- meta에 아래가 남는지
  - `factor_freq = quarterly`
  - `snapshot_mode = strict_statement_quarterly`
  - `snapshot_source = shadow_factors`
- overlay 사용 시
  - `trend_filter_enabled`
  - `trend_filter_window`
  - `market_regime_enabled`
  - `market_regime_window`
  - `market_regime_benchmark`
  가 남는지

## 8. Expected Semantics

확인 포인트:
- quarterly family는 여전히 `research-only`로 읽히는지
- default preset이 `US Statement Coverage 100`인지
- 늦은 active start가 warning/caption으로 설명되는지

## 추천 확인 순서

1. quarterly value single
2. quarterly quality+value single
3. quarterly quality / value / quality+value compare
4. history / prefill
5. annual vs quarterly compare readout
