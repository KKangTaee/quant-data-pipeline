# Phase 8 Statement Shadow Coverage Gap Diagnostics

## Goal

`Statement Shadow Coverage Preview`에서

- `Requested`
- `Covered`

사이의 차이가 보일 때, 사용자가 단순히 "coverage가 부족하다"는 사실만 보는 것이 아니라

- 어떤 심볼이 빠졌는지
- raw statement 자체가 없는지
- raw는 있는데 shadow만 비어 있는지
- 어떤 액션이 더 맞는지

를 바로 확인할 수 있게 만드는 것이 목표다.

## Implemented Behavior

Quarterly prototype single-strategy forms의 `Statement Shadow Coverage Preview`는 이제 다음을 같이 보여준다.

1. `Covered` / `Requested` 기본 요약
2. help popover
   - `Covered`의 의미
   - statement shadow vs price freshness 차이
3. coverage gap metrics
   - `Missing`
   - `Need Raw Collection`
   - `Raw Exists / Shadow Missing`
4. `Coverage Gap Drilldown`
   - missing symbol table
   - raw statement coverage 존재 여부
   - recommended action
5. targeted statement refresh payload
   - `no_raw_statement_coverage` 심볼만 대상으로 생성

## Diagnosis Semantics

### `no_raw_statement_coverage`

- 현재 DB의 strict raw statement ledger에도 coverage가 없음
- 즉 추가 statement 수집이 우선이다
- 권장 액션:
  - `Extended Statement Refresh`
  - 또는 `Financial Statement Ingestion`

### `raw_statement_present_but_shadow_missing`

- strict raw statement ledger는 존재
- 하지만 `nyse_fundamentals_statement` shadow coverage는 비어 있음
- 이 경우 추가 source 수집보다
  - shadow rebuild
  - coverage hardening
  를 먼저 점검하는 것이 더 맞다

## Why This Is Useful

기존 preview는 `Covered 100 / Requested 300`처럼 숫자만 보여줬다.

그래서 사용자는 다음을 알기 어려웠다.

- 실제로 어떤 200개 심볼이 빠졌는지
- 추가 수집이 필요한지
- 이미 raw는 있는데 shadow path가 문제인지

이번 보강으로 quarterly prototype operator flow는 다음처럼 바뀐다.

1. `Statement Shadow Coverage Preview`에서 gap 확인
2. `Coverage Gap Drilldown`에서 missing symbols 확인
3. `no_raw_statement_coverage` 심볼만 targeted refresh payload로 재수집
4. raw가 이미 있는데 shadow만 비어 있으면 rebuild / coverage hardening 쪽을 의심

## Example Interpretation

예:

- `Requested = 300`
- `Covered = 100`
- `Missing = 200`
- `Need Raw Collection = 200`
- `Raw Exists / Shadow Missing = 0`

의미:

- 300개 universe를 quarterly prototype에 쓰려 했지만
- 현재 statement shadow coverage가 있는 심볼은 100개뿐이다
- 빠진 200개는 raw statement ledger도 비어 있으므로
- 먼저 targeted statement refresh가 필요하다

반대로:

- `Need Raw Collection = 20`
- `Raw Exists / Shadow Missing = 80`

이면

- 20개는 실제 source 수집이 더 필요하고
- 80개는 이미 raw statement가 있으므로
- 추가 source 수집보다 shadow rebuild / coverage hardening 점검이 더 우선이다

## Current Limits

- 이 기능은 statement shadow coverage gap을 진단하는 것이지, 자동으로 rebuild를 실행하지는 않는다
- quarterly shadow 전용 operator rebuild 버튼은 아직 없다
- 따라서 `raw_statement_present_but_shadow_missing`는
  현재는 원인 분리를 돕는 진단 라벨로 이해하는 것이 맞다

