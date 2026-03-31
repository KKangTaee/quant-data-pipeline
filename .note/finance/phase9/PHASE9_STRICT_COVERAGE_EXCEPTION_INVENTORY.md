# Phase 9 Strict Coverage Exception Inventory

## 목적

- current strict coverage preset에서 실제로 어떤 예외 bucket이 관찰되는지 정리한다.
- `Statement Coverage Diagnosis` 결과를
  정책 문서와 preset governance의 입력으로 변환한다.

## 기준

이 inventory는 현재 구현 기준의 다음 surface를 사용한다.

- `Statement Shadow Coverage Preview`
- `Coverage Gap Drilldown`
- `Statement Coverage Diagnosis`

즉 이 문서는
“무슨 종류의 coverage exception이 실제로 preset에서 남는가”
를 정리하는 Phase 9의 기준 inventory다.

## 현재 관찰된 preset-level 상태

`quarterly` 기준으로 다시 확인한 값:

### `US Statement Coverage 100`

- Requested: `100`
- Covered: `100`
- Missing: `0`

해석:

- default quarterly anchor preset에서는 active coverage gap이 현재 없음

### `US Statement Coverage 300`

- Requested: `300`
- Covered: `298`
- Missing: `2`
- `no_raw_statement_coverage`: `2`
- `raw_present_shadow_missing`: `0`

missing symbols:

- `MRSH`
- `AU`

### `US Statement Coverage 500`

- Requested: `500`
- Covered: `497`
- Missing: `3`
- `no_raw_statement_coverage`: `3`
- `raw_present_shadow_missing`: `0`

missing symbols:

- `MRSH`
- `AU`
- `GFS`

### `US Statement Coverage 1000`

- Requested: `1000`
- Covered: `988`
- Missing: `12`
- `no_raw_statement_coverage`: `12`
- `raw_present_shadow_missing`: `0`

앞쪽 대표 missing set:

- `MRSH`
- `AU`
- `GFS`
- `GFL`
- `DOX`
- `CADE`
- `PDI`
- `BEPC`
- `BLTE`
- `GPGI`

## observed diagnosis distribution

대표 예시 10개를 `Statement Coverage Diagnosis`로 다시 확인한 결과:

- `source_empty_or_symbol_issue`: `4`
- `foreign_or_nonstandard_form_structure`: `6`

per-symbol 결과:

| Symbol | Diagnosis |
| --- | --- |
| `MRSH` | `source_empty_or_symbol_issue` |
| `AU` | `foreign_or_nonstandard_form_structure` |
| `GFS` | `foreign_or_nonstandard_form_structure` |
| `GFL` | `foreign_or_nonstandard_form_structure` |
| `DOX` | `foreign_or_nonstandard_form_structure` |
| `CADE` | `source_empty_or_symbol_issue` |
| `PDI` | `source_empty_or_symbol_issue` |
| `BEPC` | `foreign_or_nonstandard_form_structure` |
| `BLTE` | `foreign_or_nonstandard_form_structure` |
| `GPGI` | `source_empty_or_symbol_issue` |

## bucket interpretation

### 1. `source_empty_or_symbol_issue`

의미:

- DB raw / shadow coverage가 없음
- live source sample도 비어 있거나 symbol/source validity가 약함

현재 anchor cases:

- `MRSH`
- `CADE`
- `PDI`
- `GPGI`

정책 해석:

- 일반적인 operator recollection bucket이 아니라
  symbol/source validity review bucket에 가깝다

### 2. `foreign_or_nonstandard_form_structure`

의미:

- live source fact는 있으나
- 핵심 form이 `10-Q` / `10-K`가 아니라
  `20-F`, `6-K`, `40-F` 등 foreign / non-standard structure 쪽에 가깝다

현재 anchor cases:

- `AU`
- `GFS`
- `GFL`
- `DOX`
- `BEPC`
- `BLTE`

정책 해석:

- 현재 strict quarterly contract와 맞지 않는 filing structure bucket이다
- recollection보다 support-vs-exclusion policy가 우선이다

### 3. `source_present_raw_missing`

의미:

- supported form 기반 source fact는 보이는데
- DB strict raw ledger만 비어 있는 bucket

현재 observed active preset gaps:

- 이번 inventory 시점의 active preset gaps에서는 대표 anchor를 아직 확보하지 못했다

정책 해석:

- active preset의 지배적 bucket은 아니지만
- 정책상 `review_needed + targeted Extended Statement Refresh`로 남겨둘 필요가 있다

### 4. `raw_present_shadow_missing`

의미:

- DB strict raw row는 있고
- shadow만 비어 있는 recoverable bucket

현재 observed active preset gaps:

- 이번 inventory 시점의 active preset gaps에서는 `0`

배경:

- Phase 8 operator tooling 보강과 shadow rebuild 경로 정리 이후
  현재 active preset gap에서는 사실상 해소된 상태다

정책 해석:

- 현재는 active exclusion bucket이 아니라
  operator-recoverable maintenance bucket으로 보는 것이 맞다

## inventory-level conclusion

현재 active quarterly strict coverage gap은
주로 아래 두 bucket에 집중된다.

1. `source_empty_or_symbol_issue`
2. `foreign_or_nonstandard_form_structure`

즉 현재 strict quarterly preset에서 남는 문제는
“rebuild만 하면 회복되는 operator gap”보다
“심볼/source validity 또는 unsupported form structure” 쪽이 중심이다.

따라서 Phase 9 정책은
이 두 bucket을 기본 `excluded`로 두는 방향이 자연스럽다.

## recommendation

이번 inventory 기준 권고:

- `source_empty_or_symbol_issue`
  - default `excluded`
- `foreign_or_nonstandard_form_structure`
  - default `excluded`
- `source_present_raw_missing`
  - default `review_needed`
- `raw_present_shadow_missing`
  - default `eligible` + rebuild path

즉 Phase 9는
현재 diagnostics 결과를 operator 팁 수준이 아니라
**strict coverage governance rule**로 승격하는 단계로 가는 것이 맞다.
