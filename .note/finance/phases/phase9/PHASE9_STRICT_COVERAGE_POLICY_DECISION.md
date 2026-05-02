# Phase 9 Strict Coverage Policy Decision

## 목적

- strict annual / quarterly family가 어떤 심볼을 canonical preset에 포함하고,
  어떤 심볼을 review/exclusion 대상으로 둘지 정책으로 고정한다.

## 핵심 결정

### 1. current strict preset semantics

current `Coverage 100/300/500/1000` preset은
**historical point-in-time top-N universe가 아니라**
**managed static research universe**로 공식 해석한다.

즉:

- preset membership는 현재 managed universe 기준 리스트를 사용하고
- run 중에는 각 rebalance date마다 usable symbol만 남긴다

이 semantics는 유지한다.

중요:

- 이 계약은 연구용 / 운영용 preset으로는 유효하다
- 하지만 실전 투자용 최종 validation contract는 아니다

### 2. strict coverage eligibility states

Phase 9부터는 strict coverage 정책을 아래 3단 분류로 운영한다.

- `eligible`
- `review_needed`
- `excluded`

## bucket-to-policy mapping

| Diagnosis bucket | Policy state | Default operator action | 의미 |
| --- | --- | --- | --- |
| `shadow_available` | `eligible` | 추가 조치 없음 | 현재 strict coverage에 정상 포함 |
| `raw_present_shadow_missing` | `eligible` | `Statement Shadow Rebuild Only` | 구조 문제보다 operator recovery case |
| `source_present_raw_missing` | `review_needed` | targeted `Extended Statement Refresh` | source는 보이나 strict raw ledger가 비어 있음 |
| `source_empty_or_symbol_issue` | `excluded` | symbol/source validity review | recollection보다 symbol/source 자체 확인 우선 |
| `foreign_or_nonstandard_form_structure` | `excluded` | support vs exclusion policy 판단 | current strict filing contract와 안 맞음 |
| `source_present_but_not_supported_for_current_mode` | `review_needed` | mode contract review | source는 있으나 current mode와 맞지 않음 |
| `inconclusive_statement_coverage` | `review_needed` | targeted inspection + small recovery | 추가 근거 필요 |

## canonical preset maintenance rule

strict preset을 유지할 때는 아래 원칙을 따른다.

### 기본 유지 원칙

1. `eligible`만 canonical preset membership로 본다
2. `review_needed`는 operator review 전까지
   canonical preset의 public-facing 의미로 과대해석하지 않는다
3. `excluded`는 current strict preset coverage count를 평가할 때
   “회복 가능한 단순 gap”으로 취급하지 않는다

### operator tooling 연결 원칙

- `raw_present_shadow_missing`
  - recovery 대상
- `source_present_raw_missing`
  - recollection 검토 대상
- `source_empty_or_symbol_issue`
  - symbol/source validity 검토 대상
- `foreign_or_nonstandard_form_structure`
  - support/exclusion 정책 대상

즉 diagnostics 결과는
단순 UI 안내가 아니라 preset governance의 입력으로 취급한다.

## foreign / non-standard form policy

Phase 9 기본 결정:

- `20-F`, `6-K`, `40-F` 기반 issuer는
  **current strict quarterly canonical preset에서 기본 제외**

이유:

1. 현재 strict path의 핵심 filing contract는 `10-Q` / `10-K`
2. foreign-form 지원은 policy 정리가 아니라 별도 ingestion/normalization 확장 workstream에 가깝다
3. 지금 단계에서 무리하게 support를 넓히면
   preset semantics가 흔들릴 수 있다

즉:

- foreign-form issuer는 “실수로 빠진 gap”이 아니라
  현재 contract 밖의 symbol로 해석한다

## source-empty / symbol issue policy

`source_empty_or_symbol_issue`는
기본 `excluded`로 둔다.

이유:

1. DB missing + source empty가 겹친 상태라
   일반 recollection candidate로 보기 어렵다
2. 이런 케이스는 provider/source validity 또는 canonical symbol 자체 문제일 가능성이 크다
3. strict preset quality를 유지하려면
   기본 포함보다 기본 제외가 더 안전하다

## annual / quarterly 공통 해석

### strict annual family

- current managed static preset 기준 public candidate로 유지 가능
- 단, 실전 투자용 최종 validation contract는 아니라는 점을 분명히 둔다

### strict quarterly family

- 여전히 `research-only`
- current preset policy는 고정하지만,
  public candidate 승격은 별도 gate를 통과해야 한다

## phase-level decision

Phase 9 정책 기준으로는
현재 가장 중요한 일은 다음이다.

1. current preset semantics를 흔들지 않는다
2. diagnostics bucket을 governance rule로 연결한다
3. foreign-form / source-empty를 기본 exclusion bucket으로 고정한다
4. future real-money validation은 별도 `historical dynamic PIT universe` mode에서 처리한다

## 한 줄 결론

current strict preset은
**managed static research universe**로 유지한다.

그리고 current active exception bucket은
대부분 단순 recollection/rebuild 문제가 아니라
`source_empty_or_symbol_issue` 또는
`foreign_or_nonstandard_form_structure`에 가깝다.

따라서 Phase 9의 기본 정책은:

- recoverable bucket은 operator recovery로 유지
- structural bucket은 default exclusion

으로 고정하는 것이 맞다.
