# Phase 9 Strict Coverage Policy And Promotion Plan

## 목적

- strict annual / quarterly family를 어떤 coverage 정책 위에서 공식 지원할지 고정한다.
- `MRSH`, `AU` 같은 예외 심볼을 개별 대응이 아니라 정책으로 처리한다.
- research-only prototype와 public-candidate 전략 사이의 승격 기준을 문서화한다.

## 왜 이 phase가 필요한가

Phase 7과 Phase 8을 거치며,
우리는 다음을 이미 확보했다.

- quarterly coverage hardening
- quarterly strategy family first pass
- stale price diagnosis
- statement shadow coverage gap drilldown
- statement coverage diagnosis

하지만 아직 남아 있는 질문이 있다.

1. strict coverage universe에 foreign-form issuer를 포함할 것인가
2. source-empty / symbol-mapping issue 심볼은 어떤 기준으로 제외할 것인가
3. annual / quarterly family를 언제 public candidate로 승격할 것인가
4. operator tooling이 실제 정책으로 어떻게 연결되어야 하는가

즉 다음 단계는 기능 추가보다
**strict coverage policy와 promotion gate를 고정하는 phase**
가 더 자연스럽다.

## 실전 투자 목표 기준 상위 권고

이번 phase는 단순 operator 정리 phase가 아니라,
현재 backtest contract를 실전 투자 기준에서 어디까지 인정할지 고정하는 phase로 보는 편이 맞다.

핵심 권고:

1. current strict preset은 `managed static research universe`로 공식 고정
2. annual / quarterly family의 승격 조건을 policy로 명시
3. diagnostics bucket을 preset governance와 operator action으로 연결
4. Phase 9 다음 major engineering priority는
   `historical dynamic PIT universe`로 두고,
   portfolio productization은 그 다음으로 미룬다

상세 rationale은 아래 문서를 기준으로 본다.

- `PHASE9_REAL_MONEY_VALIDATION_DIRECTION.md`

## 이번 phase의 핵심 질문

1. strict family의 canonical eligible symbol은 어떻게 정의할 것인가
2. `10-Q` / `10-K` 밖의 foreign or non-standard form은 어떻게 처리할 것인가
3. `source_empty_or_symbol_issue`는 exclusion인지, 추적 backlog인지
4. `raw_present_shadow_missing` / `source_present_raw_missing`의 operator action은 어디까지 자동화할 것인가
5. annual / quarterly strict family의 public candidate 기준은 무엇인가
6. current `Coverage 100/300/500/1000` preset을 historical point-in-time universe가 아니라 managed static preset으로 공식 고정할 것인가

## 현재 기준 추천 기본안

이번 phase는 완전히 열린 탐색으로 시작하기보다,
아래 **기본 권고안**을 임시 기준으로 놓고 검증/조정하는 방식이 더 효율적이다.

### 1. strict coverage universe는 3단 분류로 관리

- `eligible`
  - 현재 strict coverage universe에 공식 포함
- `review_needed`
  - 자동 복구/정책 판단이 아직 끝나지 않아 추적이 필요한 심볼
- `excluded`
  - 현재 strict coverage universe에서는 제외

### 2. 현재 권고 기본 분류

초기 권고는 아래와 같다.

- `raw_present_shadow_missing`
  - 기본 분류: `eligible`
  - 이유:
    - source/DB raw는 이미 살아 있고
    - shadow rebuild로 회복 가능한 operator case이기 때문

- `source_present_raw_missing`
  - 기본 분류: `review_needed`
  - 이유:
    - supported form은 보이지만 strict raw ledger가 비어 있어
    - targeted recollection이 성공하는지 먼저 봐야 함

- `source_empty_or_symbol_issue`
  - 기본 분류: `excluded`
  - 이유:
    - 정상 recollection candidate가 아니라
    - symbol/source validity 문제 가능성이 높음

- `foreign_or_nonstandard_form_structure`
  - 기본 분류: `excluded`
  - 이유:
    - 현재 strict quarterly path의 core filing contract와 맞지 않음
    - support를 새로 넣기 전까지는 canonical strict preset에서 제외하는 쪽이 안전함

- `source_present_but_not_supported_for_current_mode`
  - 기본 분류: `review_needed`
  - 이유:
    - source는 있으나 현재 mode contract와 맞지 않아
    - 지원 확대 또는 제외 결정을 별도로 해야 함

### 3. foreign-form 지원에 대한 기본 권고

현재 기준 추천은:

- **Phase 9에서는 foreign-form (`20-F`, `6-K`, `40-F`) 지원 확대를 바로 구현하지 않는다**
- 먼저 정책상 `excluded`로 두고,
- 정말 product상 필요성이 크면 later phase에서 별도 support workstream으로 연다

이유:

- 지금 목적은 coverage policy를 고정하는 것
- foreign-form support는 policy가 아니라 ingestion/normalization 확장 workstream에 가까움
- AU 같은 예외를 해결하기 위해 지금 바로 form support를 넓히면
  Phase 9의 초점이 policy에서 implementation으로 흔들릴 수 있음

### 4. promotion gate에 대한 기본 권고

- `strict annual family`
  - 현재 public candidate 성격 유지
- `strict quarterly family`
  - **Phase 9 전체 기간 동안 research-only 유지**

즉 Phase 9에서는 quarterly를 public으로 승격하지 않고,
승격 조건만 문서화하는 것이 권고 기본안이다.

이유:

- quarterly family는 first-pass 구현과 operator tooling까지는 정리되었지만
- 아직 batch QA와 policy 고정이 끝나지 않았음
- 따라서 지금은 승격보다 **승격 조건의 명문화**가 우선이다

### 4-1. universe semantics에 대한 기본 권고

현재 strict coverage preset은
**historical monthly top-N universe가 아니라, run-level static managed preset**
으로 해석하는 것이 맞다.

즉:

- preset membership 자체는 현재 managed asset-profile / market-cap 기준 리스트를 사용하고
- 각 월말 리밸런싱 날짜마다
  - 가격이 있는 종목
  - factor snapshot이 usable한 종목
  만 실제 후보로 남는다

이 구조는:

- late listing / delisting / stale symbol을 어느 정도 자연스럽게 처리하지만
- 매월의 historical top-1000을 point-in-time으로 재구성하지는 않는다

권고:

- Phase 9에서 이 semantics를 **공식 문구로 고정**한다
- historical monthly top-N universe가 필요하다면,
  current preset 의미를 바꾸기보다 **별도 future mode**로 두는 쪽이 맞다

### 5. operator action에 대한 기본 권고

`Statement Coverage Diagnosis` 결과를 아래처럼 action으로 연결하는 것을
기본안으로 둔다.

- `raw_present_shadow_missing`
  - `Statement Shadow Rebuild Only`
- `source_present_raw_missing`
  - targeted `Extended Statement Refresh`
- `source_empty_or_symbol_issue`
  - symbol/source validity review
- `foreign_or_nonstandard_form_structure`
  - support vs exclusion policy decision

즉 Phase 9의 목표는
이 현재 operator guidance를 **공식 정책 문장으로 승격**시키는 것이다.

## 범위 안

### A. strict coverage eligibility policy

- eligible / ineligible / review-needed symbol policy
- symbol-source validity rule
- canonical preset maintenance rule

### B. unsupported filing structure policy

- foreign issuer (`20-F`, `6-K`, `40-F`) handling
- support vs exclusion decision rule
- quarterly strict family에서의 기본 정책 고정

### C. promotion gate definition

- annual strict family public role 재확인
- quarterly family research-only 유지 기준
- public candidate 승격 조건 문서화

### D. operator action policy

- stale / missing / unsupported symbol에 대한 대응 순서
- recollection vs rebuild vs exclusion rule
- diagnostics output을 실제 운영 decision tree로 정리

## 범위 밖

- 새로운 factor 세트 대량 추가
- 새로운 overlay engine 추가
- 포트폴리오 product surface 대규모 확장
- intramonth event engine

## 추천 구현 순서

1. strict coverage exception inventory 작성
2. eligible / review-needed / excluded policy 초안
3. foreign-form support 여부 결정
4. promotion gate 초안 작성
5. operator decision tree 고정
6. preset / UI / docs sync

## 더 구체적인 실행 순서

### Chapter 1. Exception Inventory 고정

목표:

- 현재 diagnostics bucket을 실제 운영 예외 목록으로 변환

실행:

1. known exception symbol set 추출
   - `MRSH`, `AU` 같은 anchor case 고정
2. bucket별 representative example 정리
3. `eligible / review_needed / excluded` 1차 매핑 표 작성

산출물:

- exception inventory 문서
- representative symbol table

### Chapter 2. Coverage Policy 초안 고정

목표:

- 어떤 bucket을 preset에서 허용/제외할지 문서로 결정

실행:

1. `source_empty_or_symbol_issue` 처리 rule
2. `foreign_or_nonstandard_form_structure` 처리 rule
3. `raw_present_shadow_missing` / `source_present_raw_missing` 처리 rule
4. canonical strict preset maintenance rule 작성

산출물:

- strict coverage policy 문서
- preset governance 초안

### Chapter 3. Promotion Gate 초안 고정

목표:

- annual / quarterly family의 public role과 승격 기준을 명시

실행:

1. annual strict family 유지 조건 재정리
2. quarterly strict family research-only 유지 조건 정의
3. quarterly public candidate 진입 조건 정의

산출물:

- promotion gate 문서

### Chapter 4. Operator Decision Tree 고정

목표:

- diagnostics 결과를 operator action과 1:1로 연결

실행:

1. diagnosis bucket -> action mapping 표 작성
2. recollection / rebuild / review / exclusion 순서 고정
3. UI wording / checklist wording sync

산출물:

- operator decision tree 문서
- checklist / guidance sync

### Chapter 5. Chapter Closeout

목표:

- policy, preset, operator wording, promotion gate를 한 세트로 닫기

실행:

1. finance comprehensive analysis sync
2. phase checklist 작성
3. completion summary / next-phase prep 작성

산출물:

- `PHASE9_COMPLETION_SUMMARY.md`
- `PHASE9_NEXT_PHASE_PREPARATION.md`
- `PHASE9_TEST_CHECKLIST.md`

## 이번 phase에서 실제로 결정해야 하는 것

이번 phase에서 반드시 문서로 고정해야 하는 결정은 아래 다섯 가지다.

1. foreign-form issuer를 strict canonical preset에서 기본 제외할지
2. source-empty symbol을 strict canonical preset에서 기본 제외할지
3. recoverable operator case를 preset에서 유지할지
4. quarterly family를 언제까지 research-only로 둘지
5. diagnostics 결과를 어떤 operator action으로 연결할지
6. current preset을 `managed static research universe`로 유지할지, `historical dynamic universe`로 재정의할지

즉 Phase 9는
“무엇을 구현할지”보다
**“무엇을 공식 지원으로 간주할지”를 결정하는 phase**
로 보는 것이 맞다.

## 완료 기준

- strict coverage exception 처리가 policy로 문서화됨
- annual / quarterly public candidate 기준이 명시됨
- diagnostics 결과를 어떤 action으로 연결할지 decision tree가 고정됨
- preset / operator / docs가 같은 정책을 가리킴

## 권고

Phase 9는
“coverage tooling을 더 만드는 단계”가 아니라,
**이미 만들어진 tooling을 정책과 공식 운영 규칙으로 정리하는 단계**
로 두는 것이 가장 좋다.

현재 기준 가장 실용적인 시작안은:

1. `MRSH`형 = 기본 제외
2. `AU`형 = 기본 제외
3. `raw_present_shadow_missing` = eligible + rebuild path 유지
4. `source_present_raw_missing` = review-needed + targeted recollection
5. quarterly family = research-only 유지
6. current strict coverage preset = `run-level static managed universe`로 공식 유지

이 다섯 줄을 임시 기본안으로 놓고,
이번 phase에서 문서/체크리스트/운영 flow로 고정하는 것이 가장 자연스럽다.
