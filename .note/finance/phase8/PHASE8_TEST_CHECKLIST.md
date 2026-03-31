# Phase 8 Test Checklist

## 목적

- Phase 8의 핵심 목표였던 quarterly strict prototype family가
  현재 코드 기준에서도 single / compare / history / operator tooling surface에서
  안정적으로 동작하는지 확인한다.
- 이후 Phase 9, 10에서 coverage guidance와 dynamic PIT mode가 추가되었으므로,
  이번 checklist는 **원래의 Phase 8 목표 + later-phase regression 확인**을 같이 본다.

## 1. Single Strategy - Quarterly Quality

- `Backtest > Single Strategy`
- strategy:
  - `Quality Snapshot (Strict Quarterly Prototype)`
- preset:
  - `US Statement Coverage 100`

확인 포인트:
- `Advanced Inputs`에 `Universe Contract`가 보이는지
- default가 `Static Managed Research Universe`로 열리는지
- `Price Freshness Preflight`가 보이는지
- `Statement Shadow Coverage Preview`가 보이는지
- 실행이 성공하는지
- `Selection History`가 열리는지
- `Interpretation` 탭이 보이는지

## 2. Single Strategy - Quarterly Value

- `Backtest > Single Strategy`
- strategy:
  - `Value Snapshot (Strict Quarterly Prototype)`
- preset:
  - `US Statement Coverage 100`

확인 포인트:
- `Price Freshness Preflight`가 보이는지
- `Statement Shadow Coverage Preview`가 보이는지
- `Covered < Requested`일 때 `Coverage Gap Drilldown`이 보이는지
- missing symbol과 coarse `Coverage Gap Status`가 읽히는지
- 세부 원인 분류는 `Statement Coverage Diagnosis`로 넘긴다고 안내되는지
- 실행이 성공하는지
- `Selection History`가 열리는지
- `Interpretation` 탭이 보이는지

## 3. Single Strategy - Quarterly Quality + Value

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

## 4. Single Strategy - Manual Small Universe

- 각 quarterly prototype 3종에 대해
  - `AAPL,MSFT,GOOG`
  - `2016-01-01 -> today`
  - `month_end`

확인 포인트:
- 실행이 성공하는지
- early period가 완전히 빈 결과만으로 보이지는 않는지
- 필요 시 warning이 늦은 active start를 설명하는지

## 5. Compare - Quarterly Family Exposure

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
- quarterly block 안에도 `Universe Contract` selector가 보이는지

## 6. Compare Execution

- quarterly strategy 하나 이상 포함해서 compare 실행

확인 포인트:
- summary compare가 정상인지
- focused strategy drilldown이 정상인지
- quarterly focused strategy에서 `Selection Interpretation`이 정상인지
- dynamic PIT를 고르지 않았을 때도 quarterly compare가 기존처럼 깨지지 않는지

## 7. History / Prefill

- quarterly single strategy 실행 후
  - `History` 탭 이동

확인 포인트:
- record가 저장되는지
- `Load Into Form`이 동작하는지
- `Run Again`이 동작하는지
- quarterly quality / value / multi-factor 설정값이 다시 채워지는지
- `Universe Contract`도 이전 run 값으로 다시 채워지는지

## 8. Meta / Context

- quarterly single 또는 compare 실행 후

확인 포인트:
- meta에 아래가 남는지
  - `factor_freq = quarterly`
  - `snapshot_mode = strict_statement_quarterly`
  - `snapshot_source = shadow_factors`
  - `universe_contract`
- overlay 사용 시
  - `trend_filter_enabled`
  - `trend_filter_window`
  - `market_regime_enabled`
  - `market_regime_window`
  - `market_regime_benchmark`
  가 남는지

## 9. Expected Semantics

확인 포인트:
- quarterly family는 여전히 `research-only`로 읽히는지
- default preset이 `US Statement Coverage 100`인지
- 늦은 active start가 warning/caption으로 설명되는지
- `Historical Dynamic PIT Universe`가 보이더라도
  quarterly family의 research-only 의미가 흐려지지 않는지

## 10. Operator Diagnosis - Stale Price Follow-up

- `Ingestion > Manual Jobs / Inspection > Price Stale Diagnosis`
- symbol 예시:
  - `AAPL`
  - quarterly / annual preflight에서 stale로 보였던 symbol 1개 이상

확인 포인트:
- `AAPL` 같은 정상 심볼은 `up_to_date_in_db`로 읽히는지
- stale 심볼은 `DB Latest`, `Provider Latest`, `Diagnosis`, `Recommended Action`이 같이 보이는지
- `Provider Probe Details`가 `5d / 1mo / 3mo` 기준으로 보이는지
- `local_ingestion_gap`이 있는 경우에만 targeted `Daily Market Update` payload가 제안되는지

## 11. Operator Tooling - Runtime / Rebuild / Inspector

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

## 12. Operator Tooling - Statement Coverage Guidance

- `Ingestion > Manual Jobs / Inspection > Statement Coverage Diagnosis`
- symbol 예시:
  - `MRSH`
  - `AU`

확인 포인트:
- `Coverage Gap Drilldown` 표는 `Coverage Gap Status`라는 coarse 상태만 보여주고, 세부 diagnosis는 별도 카드에서 나오는지
- `MRSH` 같은 source-empty 케이스가 `source_empty_or_symbol_issue`로 읽히는지
- `AU` 같은 foreign-form 케이스가 `foreign_or_nonstandard_form_structure`로 읽히는지
- 결과 표에 `Recommended Action`과 `Stepwise Guidance`가 같이 보이는지
- 컬럼명은 영어고 값은 한국어인지
- supported-form raw-missing 케이스에만 `Extended Statement Refresh` payload가 나오는지
- raw-present/shadow-missing 케이스에만 `Statement Shadow Rebuild Only` payload가 나오는지

## 13. Optional Regression - Quarterly Dynamic PIT Surface

- 아래 quarterly prototype 3종 중 1개 이상에서
  - `Universe Contract = Historical Dynamic PIT Universe`
  로 실행

확인 포인트:
- run 자체가 정상 완료되는지
- `Universe Membership Count`
- `Universe Contract`
- `universe_debug`
가 함께 보이는지

주의:

- 이 항목은 Phase 10 regression 확인용이다
- Phase 8 closeout의 본질은 quarterly family surface가 유지되는지 보는 것이므로,
  dynamic mode가 보인다는 사실 자체보다
  **later-phase 기능이 original quarterly surface를 깨지 않았는지**를 보는 데 목적이 있다

## 추천 확인 순서

1. quarterly quality single
2. quarterly value single
3. quarterly quality+value single
4. quarterly compare
5. history / prefill
6. meta / semantics
7. stale price diagnosis card
8. operator runtime / rebuild / inspector tooling
9. statement coverage diagnosis guidance
10. quarterly dynamic PIT regression
