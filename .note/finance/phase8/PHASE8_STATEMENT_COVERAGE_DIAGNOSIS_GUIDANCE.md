# Phase 8 Statement Coverage Diagnosis Guidance

## Summary

`Statement Shadow Coverage Preview`와 `Statement PIT Inspection`은
coverage 문제를 드러내는 데는 유용했지만,

- 지금 바로 `Extended Statement Refresh`를 다시 돌려야 하는지
- `Statement Shadow Rebuild Only`가 더 맞는지
- 재수집을 해도 가망이 낮은 구조적 케이스인지

를 바로 말해주지는 못했다.

이번 보강은 이 빈칸을 메우기 위한 것이다.

새 `Statement Coverage Diagnosis` 카드는

- DB strict raw coverage
- DB shadow coverage
- live EDGAR source sample

을 함께 보고,
운영자가 다음 액션을 더 빨리 고를 수 있도록 돕는다.

## New Operator Surface

위치:

- `Ingestion > Manual Jobs / Inspection > Statement Coverage Diagnosis`

입력:

- `Coverage Diagnosis Symbols`
- `Coverage Diagnosis Frequency`
- `Source Sample Size`

출력:

- diagnosis summary
- per-symbol recovery guidance
- source payload detail
- optional suggested payloads

## Classification Model

### 1. `shadow_available`

의미:

- 이미 statement shadow coverage가 있음

기본 액션:

- 추가 복구 작업 불필요

### 2. `raw_present_shadow_missing`

의미:

- DB에 strict raw statement row는 있음
- shadow만 비어 있음

기본 액션:

- 먼저 `Statement Shadow Rebuild Only`

이 분류는
“raw collection보다 shadow rebuild만 필요한 경우가 많다”는 운영 observation을
직접 반영한 것이다.

### 3. `source_present_raw_missing`

의미:

- source sample에는 usable fact가 보임
- supported form도 보임
- 그러나 DB strict raw row는 없음

기본 액션:

- 먼저 targeted `Extended Statement Refresh`

### 4. `foreign_or_nonstandard_form_structure`

의미:

- source는 비어 있지 않음
- 하지만 주된 form이 `20-F`, `6-K` 등
  current strict path의 핵심 `10-Q` / `10-K` route와 다름

기본 액션:

- 재수집 반복보다
  - foreign-form support를 넣을지
  - strict coverage universe에서 제외할지
  를 먼저 결정

### 5. `source_empty_or_symbol_issue`

의미:

- source sample도 비어 있음
- DB missing도 함께 발생

기본 액션:

- 재수집부터 시작하지 않음
- 먼저 symbol/source validity 점검

## Example Interpretation

### `MRSH`

실제 diagnosis 결과:

- `source_empty_or_symbol_issue`

해석:

- DB raw/shadow도 비어 있고
- live source sample도 비어 있음

따라서:

- normal re-collection candidate로 보지 않는 편이 맞다
- symbol/source validity, issuer mapping, universe symbol 자체를 먼저 본다

### `AU`

실제 diagnosis 결과:

- `foreign_or_nonstandard_form_structure`

해석:

- source fact는 있음
- 하지만 주요 form이 `20-F`, `6-K`, `6-K/A`

따라서:

- 단순 `Extended Statement Refresh` 반복으로 해결될 가능성은 낮다
- foreign issuer form support를 넣을지,
  아니면 strict coverage universe에서 제외할지 판단이 우선이다

## Backtest -> Ingestion Bridge

`Statement Shadow Coverage Preview > Coverage Gap Drilldown`에는
이제 `Statement Coverage Diagnosis`로 바로 넘기는 버튼도 추가되었다.

버튼:

- `Send Missing Symbols To Statement Coverage Diagnosis`

효과:

- backtest에서 missing symbol을 확인한 뒤
- ingestion card에 same symbol set과 frequency를 prefill한 상태로 이동 가능

주의:

- `Coverage Gap Drilldown`의 `Coverage Gap Status`는 coarse 상태만 보여준다.
- 여기서는 우선
  - `no_raw_statement_coverage`
  - `raw_statement_present_but_shadow_missing`
  만 보여준다.
- 더 세부적인 원인 분류
  - `source_empty_or_symbol_issue`
  - `foreign_or_nonstandard_form_structure`
  - `source_present_raw_missing`
  등은 `Statement Coverage Diagnosis` 실행 후에만 나온다.

## Recommended Usage

1. quarterly prototype에서 `Covered < Requested` 확인
2. `Coverage Gap Drilldown` 열기
3. missing symbol을 `Statement Coverage Diagnosis`로 보냄
4. per-symbol diagnosis 확인
5. 분류에 따라 다음 액션 선택

- `source_present_raw_missing`
  - `Extended Statement Refresh`
- `raw_present_shadow_missing`
  - `Statement Shadow Rebuild Only`
- `foreign_or_nonstandard_form_structure`
  - support vs exclusion 결정
- `source_empty_or_symbol_issue`
  - symbol/source validity 먼저 점검

## Recommendation

현재 strict quarterly operator workflow에서는
이 진단 카드가 실질적으로 필요하다.

이유:

- coverage gap이 보여도 모든 symbol이 같은 이유로 빠지는 것이 아님
- 실제로 `MRSH`와 `AU`는 전혀 다른 원인 bucket으로 분리되었다
- 따라서 무조건 `Extended Statement Refresh`를 반복하는 것은 운영 효율이 낮다

즉 이 기능은

- coverage gap을 “숫자 경고”에서
- “다음 조치 가이드”로 바꾸는 역할

을 한다.
