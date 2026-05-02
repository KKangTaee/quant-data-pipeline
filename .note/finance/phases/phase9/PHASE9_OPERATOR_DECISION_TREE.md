# Phase 9 Operator Decision Tree

## 목적

- diagnostics 결과를 실제 운영 액션으로 연결하는 기준을 고정한다.
- operator가 “다시 수집할지, rebuild할지, 제외로 볼지”를
  같은 순서로 판단하도록 만든다.

## 기본 원칙

1. 숫자 경고만 보고 무조건 재수집하지 않는다
2. coarse gap과 fine diagnosis를 구분한다
3. recoverable case와 structural case를 분리한다
4. structural case는 operator retry보다 policy bucket으로 본다

## step 1. 가격 이슈 먼저 분리

### 사용하는 surface

- `Price Freshness Preflight`
- `Price Stale Diagnosis`

### 기본 판단

- `local_ingestion_gap`
  - targeted price recollection candidate
- `provider_source_gap`
  - provider/source 상태 점검 우선
- `likely_delisted_or_symbol_changed`
  - symbol status review 우선

즉 price stale은 statement coverage와 섞어 보지 않는다.

## step 2. statement shadow coverage gap 확인

### 사용하는 surface

- `Statement Shadow Coverage Preview`
- `Coverage Gap Drilldown`

### coarse 판단

- `no_raw_statement_coverage`
  - raw statement 자체가 없음
- `raw_statement_present_but_shadow_missing`
  - raw는 있고 shadow만 없음

여기까지는 coarse gap 확인이다.

중요:

- 세부 원인 분류는 여기서 끝나지 않는다
- 필요한 경우 `Statement Coverage Diagnosis`로 넘긴다

## step 3. fine-grained statement diagnosis 실행

### 사용하는 surface

- `Statement Coverage Diagnosis`

### bucket별 기본 액션

#### `shadow_available`

- 의미:
  - 이미 usable shadow가 있음
- 액션:
  - 추가 작업 없음

#### `raw_present_shadow_missing`

- 의미:
  - raw는 있고 shadow만 없음
- 액션:
  - `Statement Shadow Rebuild Only`

#### `source_present_raw_missing`

- 의미:
  - source에는 supported-form fact가 보이는데 DB raw ledger가 비어 있음
- 액션:
  - targeted `Extended Statement Refresh`

#### `source_empty_or_symbol_issue`

- 의미:
  - source sample도 비어 있음
- 액션:
  - recollection보다 symbol/source validity review
  - strict preset에서는 기본 exclusion 해석

#### `foreign_or_nonstandard_form_structure`

- 의미:
  - source는 있으나 핵심 form contract가 다름
- 액션:
  - foreign/non-standard support 여부 정책 판단
  - current strict preset에서는 기본 exclusion 해석

#### `source_present_but_not_supported_for_current_mode`

- 의미:
  - source는 있으나 current mode contract와 다름
- 액션:
  - current mode support 확대 여부 검토
  - 당장은 review bucket

#### `inconclusive_statement_coverage`

- 의미:
  - 근거가 섞여 있음
- 액션:
  - targeted small refresh + PIT inspection 병행
  - clear해질 때까지 review bucket

## step 4. preset governance 연결

diagnostics는 operator action으로 끝내지 않고
preset governance로도 연결한다.

### governance rule

- `eligible`
  - `shadow_available`
  - `raw_present_shadow_missing`
- `review_needed`
  - `source_present_raw_missing`
  - `source_present_but_not_supported_for_current_mode`
  - `inconclusive_statement_coverage`
- `excluded`
  - `source_empty_or_symbol_issue`
  - `foreign_or_nonstandard_form_structure`

## step 5. practical examples

### `MRSH`

- diagnosis:
  - `source_empty_or_symbol_issue`
- operator action:
  - targeted recollection보다 symbol/source validity review
- governance:
  - `excluded`

### `AU`

- diagnosis:
  - `foreign_or_nonstandard_form_structure`
- operator action:
  - recollection 반복보다 form support vs exclusion 판단
- governance:
  - `excluded`

### `raw_present_shadow_missing` case

- operator action:
  - `Statement Shadow Rebuild Only`
- governance:
  - `eligible`

즉 “지금 당장 안 보인다고 다 excluded”가 아니라,
recoverable case는 recoverable bucket으로 별도 취급한다.

## current recommended sequence

1. `Price Freshness Preflight`
2. 필요 시 `Price Stale Diagnosis`
3. `Statement Shadow Coverage Preview`
4. `Coverage Gap Drilldown`
5. 필요 시 `Statement Coverage Diagnosis`
6. diagnosis 결과를 operator action + preset governance로 같이 해석

## recommendation

현재 strict family operator 흐름은
아래처럼 해석하는 것이 가장 안전하다.

- simple retry-first 운영은 피한다
- recovery 가능성이 높은 bucket만 rebuild/recollection으로 보낸다
- structural bucket은 policy 문제로 해석한다

즉 Phase 9에서는
diagnostics를 “무엇이 깨졌는가”가 아니라
“어떤 bucket이며, 어떤 action과 governance state로 이어지는가”로 읽는 편이 맞다.
