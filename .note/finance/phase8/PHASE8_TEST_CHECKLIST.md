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
- `Covered < Requested`일 때 `Coverage Gap Drilldown`이 보이는지
- missing symbol과 `Recommended Action`이 읽히는지
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

## 9. Operator Diagnosis - Stale Price Follow-up

- `Ingestion > Manual Jobs / Inspection > Price Stale Diagnosis`
- symbol 예시:
  - `AAPL`
  - quarterly / annual preflight에서 stale로 보였던 symbol 1개 이상

확인 포인트:
- `AAPL` 같은 정상 심볼은 `up_to_date_in_db`로 읽히는지
- stale 심볼은 `DB Latest`, `Provider Latest`, `Diagnosis`, `Recommended Action`이 같이 보이는지
- `Provider Probe Details`가 `5d / 1mo / 3mo` 기준으로 보이는지
- `local_ingestion_gap`이 있는 경우에만 targeted `Daily Market Update` payload가 제안되는지

## 10. Operator Tooling - Runtime / Rebuild / Inspector

- `Ingestion`

확인 포인트:
- 상단에 `Runtime / Build` block이 보이는지
- `Runtime Marker`, `Loaded At`, `Git SHA`가 보이는지
- `Manual Jobs / Inspection > Statement Shadow Rebuild Only` 카드가 보이는지
- quarterly prototype의 `Coverage Gap Drilldown`에서 아래 둘이 같이 보이는지
  - `Send Raw-Coverage Gaps To Extended Statement Refresh`
  - `Send Shadow-Missing Gaps To Statement Shadow Rebuild`
- 위 버튼 중 하나를 누른 뒤 ingestion 관련 카드에 symbols/freq가 prefill 되는지
- `Persistent Run History > Run Inspector`에서 아래가 보이는지
  - runtime marker
  - pipeline steps
  - run artifacts
  - related logs
- symbol-level issue가 있는 run 이후 `Failure CSV Preview`에서 새 standardized failure CSV가 보이는지

## 추천 확인 순서

1. quarterly value single
2. quarterly quality+value single
3. quarterly quality / value / quality+value compare
4. history / prefill
5. annual vs quarterly compare readout
6. stale price diagnosis card
7. operator runtime / rebuild / inspector tooling
